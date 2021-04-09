#!/usr/bin/env python3
"""
Post-project generation hook
"""

import subprocess
import os

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
        ["git", " config", "--global", "user.email", "automation@seisollc.com"],
        capture_output=True,
        check=True,
    )
subprocess.run(["pipenv", "install", "--dev"], capture_output=True, check=True)
subprocess.run(["pipenv", "run", "invoke", "reformat"], capture_output=True, check=True)
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
