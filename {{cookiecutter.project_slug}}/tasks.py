#!/usr/bin/env python3
"""
Task execution tool & library
"""

import os
{%- if cookiecutter.versioning == 'CalVer' %}
import re
{%- endif %}
import subprocess
import sys
{%- if cookiecutter.versioning == 'CalVer' %}
from datetime import datetime
{%- endif %}
from logging import basicConfig, getLogger
from pathlib import Path

import docker
import git
from bumpversion.cli import main as bumpversion
from invoke import task
from {{ cookiecutter.project_slug }} import __version__, constants

basicConfig(level="INFO", format=constants.LOG_FORMAT)
LOG = getLogger("{{ cookiecutter.project_slug }}.invoke")

CWD = Path(".").absolute()
try:
    REPO = git.Repo(CWD)
except git.exc.InvalidGitRepositoryError:
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


# Tasks
@task
def lint(c):  # pylint: disable=unused-argument
    """Lint {{ cookiecutter.project_name }}"""
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
def build(c):  # pylint: disable=unused-argument
    """Build {{ cookiecutter.project_name }}"""
    version_string = "v" + __version__
    commit_hash = REPO.head.commit.hexsha
    commit_hash_short = REPO.git.rev_parse(commit_hash, short=True)

    if (
        version_string in REPO.tags
        and REPO.tags[version_string].commit.hexsha == commit_hash
    ):
        buildargs = {"VERSION": __version__, "COMMIT_HASH": commit_hash}
    else:
        buildargs = {
            "VERSION": __version__ + "-" + commit_hash_short,
            "COMMIT_HASH": commit_hash,
        }

    # Build and Tag
    for tag in ["latest", buildargs["VERSION"]]:
        tag = IMAGE + ":" + tag
        LOG.info("Building %s...", tag)
        CLIENT.images.build(
            path=str(CWD), target="final", rm=True, tag=tag, buildargs=buildargs
        )


@task(pre=[lint, build])
def test(c):  # pylint: disable=unused-argument
    """Test {{ cookiecutter.project_name }}"""
    try:
        subprocess.run(["pipenv", "run", "pytest", "--cov={{ cookiecutter.project_slug }}", "tests"], check=True)
    except subprocess.CalledProcessError:
        LOG.error("Testing failed")
        sys.exit(1)


@task
def reformat(c):  # pylint: disable=unused-argument
    """Reformat {{ cookiecutter.project_name }}"""
    entrypoint_and_command = [("isort", "."), ("black", ".")]
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


@task(pre=[test])
{%- if cookiecutter.versioning == 'SemVer-ish' %}
def release(c, release_type):  # pylint: disable=unused-argument
{%- elif cookiecutter.versioning == 'CalVer' %}
def release(c):  # pylint: disable=unused-argument
{%- endif %}
    """Make a new release of {{ cookiecutter.project_name }}"""
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

    if latest_release and date_info == latest_release[:7]:
        increment = str(int(latest_release[8:]) + 1).zfill(2)
    else:
        increment = "01"

    new_version = date_info + "." + increment

    bumpversion(["--new-version", new_version, "unusedpart"])
{%- endif %}


@task
def publish(c, tag):  # pylint: disable=unused-argument
    """Publish {{ cookiecutter.project_name }}"""
    if tag not in ["latest", "release"]:
        LOG.error("Please provide a tag of either latest or release")
        sys.exit(1)
    elif tag == "release":
        tag = "v" + __version__

{%- if cookiecutter.dockerhub == 'yes' %}
    repository = IMAGE + ":" + tag
    LOG.info("Pushing %s to docker hub...", repository)
    CLIENT.images.push(repository=repository)
    LOG.info("Done publishing the %s Docker image", repository)
{%- else %}
    raise NotImplementedError()
{%- endif %}
