#!/usr/bin/env python3
"""
Task execution tool & library
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from logging import basicConfig, getLogger
from pathlib import Path

import git
import pytest
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

CWD = Path(".").absolute()
REPO = git.Repo(CWD)


# Tasks
@task
def test(c):  # pylint: disable=unused-argument
    """Test cookiecutter-python"""
    try:
        subprocess.run(["pipenv", "run", "pytest", "tests"])
    except subprocess.CalledProcessError:
        LOG.error("Testing failed")
        sys.exit(1)


@task(pre=[test])
def release(c):  # pylint: disable=unused-argument
    """Make a new release of cookiecutter-python"""
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

    new_version = date_info + "." + increment

    bumpversion(["--new-version", new_version, "unusedpart"])
