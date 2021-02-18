#!/usr/bin/env python3
"""
Task execution tool & library
"""

from pathlib import Path
import sys
import json
from logging import getLogger, basicConfig
import git
from invoke import task
import docker

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

{% if cookiecutter.versioning == 'SemVer' -%}
VERSION = "0.1.0"
{% elif cookiecutter.versioning == 'CalVer' -%}
VERSION = "{% now 'local', '%Y.%m-01' %}"
{% endif -%}
CWD = Path(".").absolute()
REPO = git.Repo(CWD)
COMMIT_HASH = REPO.head.object.hexsha
CLIENT = docker.from_env()
IMAGE = "seiso/{{ cookiecutter.project_slug }}"
TAGS = [IMAGE + ":latest", IMAGE + ":" + VERSION]


## Tasks
@task
def build(c):  # pylint: disable=unused-argument
    """Build {{ cookiecutter.project_name }}"""
    buildargs = {"VERSION": VERSION, "COMMIT_HASH": COMMIT_HASH}

    # pylint: disable=redefined-outer-name
    for tag in TAGS:
        LOG.info("Building %s...", tag)
        CLIENT.images.build(
            path=str(CWD), target="final", rm=True, tag=tag, buildargs=buildargs
        )


@task(pre=[build])
def test(c):  # pylint: disable=unused-argument
    """Test {{ cookiecutter.project_name }}"""
    print("TODO: Implement tests")


@task
def publish(c, tag):  # pylint: disable=unused-argument
    """Publish {{ cookiecutter.project_name }}"""
    if tag not in ["latest", "version"]:
        LOG.error("Please provide a tag of either latest or version")
        sys.exit(1)
    elif tag == "version":
        tag = VERSION

    repository = IMAGE + ":" + tag
    LOG.info("Pushing %s to docker hub...", repository)
    CLIENT.images.push(repository=repository)
    LOG.info("Done publishing the %s Docker image", repository)
