#!/usr/bin/env python3
"""
Task execution tool & library
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from logging import WARNING, basicConfig, getLogger
from pathlib import Path

import docker
import git
from bumpversion.cli import main as bumpversion
from invoke import task

LOG_FORMAT = json.dumps(
    {
        "timestamp": "%(asctime)s",
        "namespace": "%(name)s",
        "loglevel": "%(levelname)s",
        "message": "%(message)s",
    }
)
basicConfig(level="INFO", format=LOG_FORMAT)
LOG = getLogger("cookiecutter-python")
getLogger("urllib3").setLevel(WARNING)

CWD = Path(".").absolute()
REPO = git.Repo(CWD)
CLIENT = docker.from_env()


def process_container(*, container: docker.models.containers.Container) -> None:
    """Process a provided container"""
    response = container.wait(condition="not-running")
    decoded_response = container.logs().decode("utf-8")
    response["logs"] = decoded_response.strip().replace("\n", "  ")
    container.remove()
    if not response["StatusCode"] == 0:
        LOG.error(
            "Received a non-zero status code from docker (%s); additional details: %s",
            response["StatusCode"],
            response["logs"],
        )
        sys.exit(response["StatusCode"])
    else:
        LOG.info("%s", response["logs"])


# Tasks
@task
def test(_c, debug=False):
    """Test cookiecutter-python"""
    if debug:
        getLogger().setLevel("DEBUG")

    try:
        subprocess.run(
            ["pipenv", "run", "pytest", "--keep-baked-projects", "tests"],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        LOG.error(
            f"Testing failed with stdout of {error.stdout.decode('utf-8')} and stderr of {error.stderr.decode('utf-8')}"
        )
        sys.exit(1)


@task(pre=[test])
def release(_c, debug=False):
    """Make a new release of cookiecutter-python"""
    if debug:
        getLogger().setLevel("DEBUG")

    if REPO.head.is_detached:
        LOG.error("In detached HEAD state, refusing to release")
        sys.exit(1)

    # Get the current date info
    date_info = datetime.now().strftime("%Y.%m")

    # Our CalVer pattern which works until year 2200, up to 100 releases a
    # month (purposefully excludes builds)
    pattern = re.compile(r"v2[0-1][0-9]{2}.(0[0-9]|1[0-2]).[0-9]{2}")

    # Identify and set the increment
    for tag in reversed(REPO.tags):
        if pattern.fullmatch(tag.name):
            latest_release = tag.name
            break
    else:
        latest_release = None

    if latest_release and date_info == latest_release[:7]:
        increment = str(int(latest_release[8:]) + 1).zfill(2)
    else:
        increment = "01"

    new_version = f"{date_info}.{increment}"

    bumpversion(["--new-version", new_version, "unusedpart"])


@task
def update(_c, debug=False):
    """Update the core components of cookiecutter-python"""
    if debug:
        getLogger().setLevel("DEBUG")

    # Update the CI dependencies
    image = "python:3.10"
    working_dir = "/usr/src/app/"
    volumes = {CWD: {"bind": working_dir, "mode": "rw"}}
    CLIENT.images.pull(repository=image)
    command = '/bin/bash -c "python3 -m pip install --upgrade pipenv &>/dev/null && pipenv update"'
    container = CLIENT.containers.run(
        auto_remove=False,
        command=command,
        detach=True,
        image=image,
        volumes=volumes,
        working_dir=working_dir,
    )
    process_container(container=container)


@task
def clean(_c, debug=False):
    """Clean up cookiecutter-python"""
    if debug:
        getLogger().setLevel("DEBUG")

    cleanup_list = []
    cleanup_list.extend(list(CWD.glob("**/.DS_Store")))
    cleanup_list.extend(list(CWD.glob("**/.Thumbs.db")))
    cleanup_list.extend(list(CWD.glob("**/.mypy_cache")))
    cleanup_list.extend(list(CWD.glob("**/*.pyc")))

    for item in cleanup_list:
        if item.is_dir():
            shutil.rmtree(item)
        elif item.is_file():
            item.unlink()
