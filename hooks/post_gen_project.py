#!/usr/bin/env python3
"""
Post-project generation hook
"""

import datetime
import json
import os
import pprint
import subprocess
import sys
# Used indirectly in the below Jinja2 block
from collections import OrderedDict # pylint: disable=unused-import
from logging import basicConfig, getLogger
from pathlib import Path
from typing import Union

import yaml

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
PROJECT_CONTEXT = Path('.github/project.yml')

if (
    os.environ.get("GITHUB_ACTIONS") == "true"
    and os.environ.get("RUN_POST_HOOK") != "true"
):
    sys.exit(0)


def get_context() -> dict:
    """Return the context as a dict"""
    # TODO: This is failing with a module import error
    import git

    cookiecutter = None
    timestamp = datetime.datetime.utcnow().isoformat(timespec='seconds')

    ##############
    # This section leverages cookiecutter's jinja interpolation
    cookiecutter_context: OrderedDict[str, str] = {{ cookiecutter | pprint }} # type: ignore

    project_name = cookiecutter_context["project_slug"] # pylint: disable=unsubscriptable-object
    project_description = cookiecutter_context['project_short_description'] # pylint: disable=unsubscriptable-object
    template = cookiecutter_context['_template'] # pylint: disable=unsubscriptable-object
    ##############

    try:
        # TODO: Is this the right location?
        repo = git.Repo(template)

        # Expect this is a local template
        branch = repo.active_branch
        dirty = repo.is_dirty(untracked_files=True)
        template_commit_hash = git.cmd.Git().ls_remote(template, "HEAD")[:40]
    except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        # Expect this is a remote template
        # I would like this to be able to be more robust instead of assuming 'main'. However, this is pending
        # https://github.com/cookiecutter/cookiecutter/issues/1759
        # TODO: Can I pull this from wherever it clones the template?
        branch = "main"
        dirty = False
        template_commit_hash = git.cmd.Git().ls_remote(template, "main")[:40]

    context: dict[str, Union[str, dict[str, Union[str, bool, dict[str, str]]]]] = {}
    context['name'] = project_name
    context['description'] = project_description
    context['origin'] = {}
    context['origin']['timestamp'] = timestamp
    context['origin']['generated'] = True
    context['origin']['template'] = {}
    context['origin']['template']['branch'] = branch
    context['origin']['template']['commit hash'] = template_commit_hash
    context['origin']['template']['dirty'] = dirty
    context['origin']['template']['location'] = template
    context['origin']['template']['cookiecutter'] = {}
    context['origin']['template']['cookiecutter'] = cookiecutter_context

    # Filter out unwanted cookiecutter context
    del cookiecutter_context['_output_dir'] # pylint: disable=unsubscriptable-object

    return context


def write_context(*, context: dict) -> None:
    """Write the context dict to the config file"""
    with open(PROJECT_CONTEXT, "w", encoding='utf-8') as file:
        yaml.dump(context, file)


def run_post_gen_hook():
    """Run post generation hook"""
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

        # Write the context to the project.yml
        # TODO: Remove
        print(sys.path)
        context = get_context()
        write_context(context=context)

        subprocess.run(
            ["pipenv", "run", "invoke", "reformat"], capture_output=True, check=True
        )
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


if __name__ == '__main__':
    run_post_gen_hook()
