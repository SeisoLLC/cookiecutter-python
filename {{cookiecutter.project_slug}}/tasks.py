#!/usr/bin/env python3
"""
Task execution tool & library
"""

import json
{%- if cookiecutter.versioning == 'CalVer' %}
import re
{%- endif %}
import sys
{%- if cookiecutter.versioning == 'CalVer' %}
from datetime import datetime
{%- endif %}
from logging import basicConfig, getLogger
from pathlib import Path

import docker
import git
from invoke import task
from bumpversion.cli import main as bumpversion
from {{ cookiecutter.project_slug }} import __version__

LOG_FORMAT = json.dumps(
    {
        "timestamp": "%(asctime)s",
        "namespace": "%(name)s",
        "loglevel": "%(levelname)s",
        "message": "%(message)s",
    }
)
basicConfig(level="INFO", format=LOG_FORMAT)
LOG = getLogger("{{ cookiecutter.project_slug }}")

CWD = Path(".").absolute()
REPO = git.Repo(CWD)
CLIENT = docker.from_env()
IMAGE = "seiso/{{ cookiecutter.project_slug }}"


# Tasks
@task
def build(c):  # pylint: disable=unused-argument
    """Build {{ cookiecutter.project_name }}"""
    version_string = "v" + __version__
    commit_hash = REPO.head.commit.hexsha
    commit_hash_short = commit_hash[:7]

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


@task(pre=[build])
def test(c):  # pylint: disable=unused-argument
    """Test {{ cookiecutter.project_name }}"""
    LOG.warning("TODO: Implement project tests")


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
    elif REPO.active_branch.name != "main":
        LOG.error("Not on the main branch, refusing to release")
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
    pattern = re.compile(r"v2[0-1][0-9]{2}.(0[0-9]|1[0-2])_[0-9]{2}")

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

{%- if cookiecutter.dockerhub == 'y' %}
    repository = IMAGE + ":" + tag
    LOG.info("Pushing %s to docker hub...", repository)
    CLIENT.images.push(repository=repository)
    LOG.info("Done publishing the %s Docker image", repository)
{%- else %}
    LOG.warning("TODO: Where should I publish to?")
{%- endif %}
