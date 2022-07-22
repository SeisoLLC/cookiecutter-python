#!/usr/bin/env python3
"""
Task execution tool & library
"""

import os
{%- if cookiecutter.versioning == 'CalVer' %}
import re
{%- endif %}
import shutil
import subprocess
import sys
{%- if cookiecutter.versioning == 'CalVer' %}
from datetime import datetime
{%- endif %}
from logging import basicConfig, getLogger, WARNING
from pathlib import Path
from typing import Union

import docker
import git
from bumpversion.cli import main as bumpversion
from invoke import task
from {{ cookiecutter.project_slug }} import __version__, constants

basicConfig(level="INFO", format=constants.LOG_FORMAT)
LOG = getLogger("{{ cookiecutter.project_slug }}.invoke")
getLogger("urllib3").setLevel(WARNING)

CWD = Path(".").absolute()
try:
    REPO: Union[git.repo.base.Repo, None] = git.Repo(CWD)
except git.InvalidGitRepositoryError:
    REPO = None
CLIENT = docker.from_env()
IMAGE = "seiso/{{ cookiecutter.project_slug }}"


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


def log_build_log(*, build_err: docker.errors.BuildError) -> None:
    """Log the docker build log"""
    iterator = iter(build_err.build_log)
    finished = False
    while not finished:
        try:
            item = next(iterator)
            if "stream" in item:
                if item["stream"] != "\n":
                    LOG.error("%s", item["stream"].strip())
            elif "errorDetail" in item:
                LOG.error("%s", item["errorDetail"])
            else:
                LOG.error("%s", item)
        except StopIteration:
            finished = True


# Tasks
@task
def lint(_c, debug=False):
    """Lint {{ cookiecutter.project_name }}"""
    if debug:
        getLogger().setLevel("DEBUG")

    environment = {}

    if REPO.is_dirty(untracked_files=True):
        LOG.error("Linting requires a clean git directory to function properly")
        sys.exit(1)

    # Pass in all of the host environment variables starting with INPUT_
    for element in dict(os.environ):
        if element.startswith("INPUT_"):
            environment[element] = os.environ.get(element)

    image = "seiso/goat:latest"
    environment["RUN_LOCAL"] = True
    working_dir = "/goat/"
    volumes = {CWD: {"bind": working_dir, "mode": "rw"}}

    LOG.info("Pulling %s...", image)
    CLIENT.images.pull(image)
    LOG.info("Running %s...", image)
    container = CLIENT.containers.run(
        auto_remove=False,
        detach=True,
        environment=environment,
        image=image,
        volumes=volumes,
        working_dir=working_dir,
    )
    process_container(container=container)

    LOG.info("Linting completed successfully")


@task
def build(_c, debug=False):
    """Build {{ cookiecutter.project_name }}"""
    if debug:
        getLogger().setLevel("DEBUG")

    version_string = f"v{__version__}"
    commit_hash = REPO.head.commit.hexsha
    commit_hash_short = REPO.git.rev_parse(commit_hash, short=True)

    if (
        version_string in REPO.tags
        and REPO.tags[version_string].commit.hexsha == commit_hash
    ):
        buildargs = {"VERSION": __version__, "COMMIT_HASH": commit_hash}
    else:
        buildargs = {
            "VERSION": f"{__version__}-{commit_hash_short}",
            "COMMIT_HASH": commit_hash,
        }

    # Build and Tag
    for tag in ["latest", buildargs["VERSION"]]:
        tag = f"{IMAGE}:{tag}"
        LOG.info("Building %s...", tag)
        try:
            CLIENT.images.build(
                path=str(CWD), target="final", rm=True, tag=tag, buildargs=buildargs
            )
        except docker.errors.BuildError as build_err:
            LOG.exception("Failed to build, retrieving and logging the more detailed build error...")
            log_build_log(build_err=build_err)
            sys.exit(1)


@task
def test(_c, debug=False):
    """Test {{ cookiecutter.project_name }}"""
    if debug:
        getLogger().setLevel("DEBUG")

    try:
        subprocess.run(
            [
                "pipenv",
                "run",
                "pytest",
                "--cov={{ cookiecutter.project_slug }}",
                "tests",
            ],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        LOG.error(
            f"Testing failed with stdout of {error.stdout.decode('utf-8')} and stderr of {error.stderr.decode('utf-8')}"
        )
        sys.exit(1)


@task
def reformat(_c, debug=False):
    """Reformat {{ cookiecutter.project_name }}"""
    if debug:
        getLogger().setLevel("DEBUG")

    entrypoint_and_command = [
        ("isort", ". --settings-file /action/lib/.automation/.isort.cfg"),
        ("black", "."),
    ]
    image = "seiso/goat:latest"
    working_dir = "/goat/"
    volumes = {CWD: {"bind": working_dir, "mode": "rw"}}

    LOG.info("Pulling %s...", image)
    CLIENT.images.pull(image)
    LOG.info("Reformatting the project...")
    for entrypoint, command in entrypoint_and_command:
        container = CLIENT.containers.run(
            auto_remove=False,
            command=command,
            detach=True,
            entrypoint=entrypoint,
            image=image,
            volumes=volumes,
            working_dir=working_dir,
        )
        process_container(container=container)


@task
def update(_c, debug=False):
    """Update the core components of {{ cookiecutter.project_name }}"""
    if debug:
        getLogger().setLevel("DEBUG")

    # Update the CI dependencies
    image = "python:{{ cookiecutter.python_versions[0] }}"
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
{%- if cookiecutter.versioning == 'SemVer-ish' %}
def release(_c, release_type, debug=False):
{%- elif cookiecutter.versioning == 'CalVer' %}
def release(_c, debug=False):
{%- endif %}
    """Make a new release of {{ cookiecutter.project_name }}"""
    if debug:
        getLogger().setLevel("DEBUG")

    if REPO.head.is_detached:
        LOG.error("In detached HEAD state, refusing to release")
        sys.exit(1)
{%- if cookiecutter.versioning == 'SemVer-ish' %}

    if release_type not in ["major", "minor", "patch"]:
        LOG.error("Please provide a release type of major, minor, or patch")
        sys.exit(1)

    bumpversion([release_type])
{%- elif cookiecutter.versioning == 'CalVer' %}

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

    if latest_release and date_info == latest_release[1:8]:
        increment = str(int(latest_release[9:]) + 1).zfill(2)
    else:
        increment = "01"

    new_version = f"{date_info}.{increment}"

    bumpversion(["--new-version", new_version, "unusedpart"])
{%- endif %}


@task
def publish(_c, tag, debug=False):
    """Publish {{ cookiecutter.project_name }}"""
    if debug:
        getLogger().setLevel("DEBUG")

    if tag not in ["latest", "release"]:
        LOG.error("Please provide a tag of either latest or release")
        sys.exit(1)
    elif tag == "release":
        tag = f"v{__version__}"

{%- if cookiecutter.dockerhub == 'yes' %}
    repository = f"{IMAGE}:{tag}"
    LOG.info("Pushing %s to docker hub...", repository)
    CLIENT.images.push(repository=repository)
    LOG.info("Done publishing the %s image", repository)
{%- else %}
    raise NotImplementedError()
{%- endif %}


@task
def clean(_c, debug=False):
    """Clean up {{ cookiecutter.project_name }}"""
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
