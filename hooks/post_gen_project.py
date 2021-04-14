#!/usr/bin/env python3
"""
Post-project generation hook
"""

import json
import os
import subprocess
import sys
from logging import basicConfig, getLogger

LOG_FORMAT = json.dumps(
    {
        "timestamp": "%(asctime)s",
        "namespace": "%(name)s",
        "loglevel": "%(levelname)s",
        "message": "%(message)s",
    }
)

basicConfig(level="INFO", format=LOG_FORMAT)
LOG = getLogger("{{ cookiecutter.project_slug }}.post_generation_hook")

if (
    os.environ.get("GITHUB_ACTIONS") == "true"
    and os.environ.get("RUN_POST_HOOK") != "true"
):
    sys.exit(0)


try:
    subprocess.run(
        ["git", "init", "--initial-branch=main"], capture_output=True, check=True
    )
    if os.environ.get("GITHUB_ACTIONS") == "true":
        subprocess.run(
            ["git", "config", "--global", "user.name", "Seiso Automation"],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "--global", "user.email", "automation@seisollc.com"],
            capture_output=True,
            check=True,
        )
    subprocess.run(["pipenv", "install", "--dev"], capture_output=True, check=True)
#     subprocess.run(
#         ["pipenv", "run", "invoke", "reformat"], capture_output=True, check=True
#     )
    subprocess.run(["git", "add", "-A"], capture_output=True, check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Initial project generation",
            "--author='Seiso Automation <automation@seisollc.com>'",
        ],
        capture_output=True,
        check=True,
    )
except subprocess.CalledProcessError as error:
    LOG.error(
        "stdout: %s, stderr: %s",
        error.stdout.decode("utf-8"),
        error.stderr.decode("utf-8"),
    )
    sys.exit(1)
