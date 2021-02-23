#!/usr/bin/env python3
"""
Task execution tool & library
"""

import json
{%- if cookiecutter.versioning == 'CalVer' %}
import re
{%- endif %}
import sys
from logging import basicConfig, getLogger
from pathlib import Path
{%- if cookiecutter.versioning == 'CalVer' %}
from datetime import datetime
{%- endif %}

import docker
import git
from invoke import task
from semantic_release.cli import bump_version
{%- if cookiecutter.versioning == 'SemVer-ish' %}
from semantic_release.history import get_current_version, get_new_version
{%- endif %}
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
def release(c, type="minor"):  # pylint: disable=unused-argument
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
    if type not in ["major", "minor", "patch"]:
        LOG.error("Please provide a release type of major, minor, or patch")
        sys.exit(1)

    new_version = get_new_version(get_current_version(), type)
    bump_version(new_version, type)
{%- elif cookiecutter.versioning == 'CalVer' %}
    # Get the current date info
    date_info = datetime.now().strftime("%Y.%m")

    # Our CalVer pattern which works until year 2200, up to 100 releases a
    # month (purposefully excludes builds)
    pattern = re.compile("v2[0-1][0-9]{2}\.(0[0-9]|1[0-2])_[0-9]{2}")

    # Identify and set the increment
    for tag in reversed(REPO.tags):
        if pattern.fullmatch(tag.name):
            latest_release = tag.name
            break
    else:
        latest_release = None

    if latest_release and date_info == latest_release.split("_")[0]:
        increment = str(int(latest_release.split("_")[-1]) + 1).zfill(2)
    else:
        increment = "01"

    new_version = date_info + "_" + increment
    level_bump = None

    bump_version(new_version, level_bump)
{%- endif %}
    REPO.remotes.origin.push("v" + new_version)


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
