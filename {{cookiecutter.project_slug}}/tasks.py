#!/usr/bin/env python3
"""
Task execution tool & library
"""

from {{ cookiecutter.project_slug }} import __version__
import json
import sys
from logging import basicConfig, getLogger
from pathlib import Path
{%- if cookiecutter.versioning == 'CalVer' %}
from datetime import datetime
{%- endif %}

import docker
import git
from invoke import task
from semantic_release.cli import bump_version, changelog
from semantic_release.history import get_new_version, get_current_version

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
COMMIT_HASH = REPO.head.object.hexsha
CLIENT = docker.from_env()
IMAGE = "seiso/{{ cookiecutter.project_slug }}"
TAGS = ["latest", __version__]
IMAGES = []
for tag in TAGS:
    IMAGES.append(IMAGE + ":" + tag)


# Tasks
@task
def build(c, version):  # pylint: disable=unused-argument
    """Build {{ cookiecutter.project_name }}"""
    # TODO: Allow build of any version?  Check git tags, if not there, and not latest, fail.
    buildargs = {"VERSION": __version__, "COMMIT_HASH": COMMIT_HASH}

    # pylint: disable=redefined-outer-name
    for image in IMAGES:
        LOG.info("Building %s...", image)
        CLIENT.images.build(
            path=str(CWD), target="final", rm=True, tag=image, buildargs=buildargs
        )


@task(pre=[build])
def test(c):  # pylint: disable=unused-argument
    """Test {{ cookiecutter.project_name }}"""
    print("TODO: Implement tests")


# TODO: This is WIP.  Need to find a way to automatically differentaite major
# minor patch for semver; commits? How to enforce?
# TODO: Also, consider that we do not want to push v tags to docker hub or use
# them when building (already true)
@task(pre=[test])
{%- if cookiecutter.versioning == 'SemVer' %}
def release(c, type):  # pylint: disable=unused-argument
{%- elif cookiecutter.versioning == 'CalVer' %}
def release(c):  # pylint: disable=unused-argument
{%- endif %}
    """Make a new release of {{ cookiecutter.project_name }}"""
{%- if cookiecutter.versioning == 'SemVer' %}
    if type not in ["major", "minor", "patch"]:
        LOG.error("Please provide a release type of major, minor, or patch")
        sys.exit(1)

    new_version = get_new_version(get_current_version(), type)
    bump_version(new_version, type)
{% elif cookiecutter.versioning == 'CalVer' %}
    # Get the current date info
    date_info = datetime.now().strftime("%Y.%m")

    # Our CalVer pattern which works until year 2200, up to 100 releases a
    # month
    pattern = re.compile('2[0-1][0-9]{2}\.(0[0-9]|1[0-2])-[0-9]{2}')

    # Identify and set the increment
    for tag in reversed(REPO.tags):
        if pattern.fullmatch(tag):
            latest_release = tag
            break
    else:
        latest_release = None

    if latest_release and date_info == latest_release.split('-')[0]:
        increment = str(int(latest_release.split('-')[-1]) + 1).zfill(2)
    else:
        increment = '01'

    new_version = date_info + "-" + increment
    level_bump = None

    bump_version(new_version, level_bump)
{% endif %}
    print('TODO: We\'ve bumped the version, but now what to do a release?')
{%- if cookiecutter.dockerhub == 'y' %}


@task(pre=[build])
def publish(c, tag):  # pylint: disable=unused-argument
    """Publish {{ cookiecutter.project_name }}"""
    if tag not in ["latest", "version"]:
        LOG.error("Please provide a tag of either latest or version")
        sys.exit(1)
    elif tag == "version":
{%- if cookiecutter.versioning == 'SemVer' %}
        tag = "v" + __version__
{% elif cookiecutter.versioning == 'CalVer' %}
        tag = __version__
{% endif %}
    repository = IMAGE + ":" + tag
    LOG.info("Pushing %s to docker hub...", repository)
    CLIENT.images.push(repository=repository)
    LOG.info("Done publishing the %s Docker image", repository)
{%- endif -%}
