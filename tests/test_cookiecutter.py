#!/usr/bin/env python3
"""
Test cookiecutter-python
"""

import copy
import itertools
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Union

import git
import pytest
import yaml
from jinja2 import Template


def get_config() -> dict:
    """Generate all the config keys"""
    config_file = Path("./cookiecutter.json")
    with open(config_file, "r") as file_object:
        config = json.load(file_object)
    return config


def render_config(*, config: dict) -> dict:
    """Render the provided config"""
    rendered_config: dict[str, Union[str, list]] = {}
    for key, value in config.items():
        if isinstance(value, str):
            # Sanitize by removing the "cookiecutter." prefix
            sanitized_template = value.replace("cookiecutter.", "")
            template = Template(sanitized_template)
            rendered_config[key] = str(template.render(config))
        elif isinstance(value, list):
            rendered_config[key] = value
        else:
            sys.exit(1)
    return rendered_config


def get_supported_combinations() -> list:
    """Generate all supported combinations of options"""
    config = get_config()
    base_config = render_config(config=config)
    combinations = copy.deepcopy(base_config)

    # Make every str a list[str]
    for key, value in base_config.items():
        if isinstance(value, str):
            combinations[key] = [value]

    # Return all combinations of the config
    supported_combinations = [
        dict(zip(combinations, v)) for v in itertools.product(*combinations.values())
    ]
    return supported_combinations


@pytest.fixture
def context():
    """pytest fixture for context"""
    # Use the rendered defaults
    return get_supported_combinations()[0]


def _fixture_id(ctx):
    """Helper to get a user friendly test name from the parametrized context."""
    return ",".join(f"{key}:{value}" for key, value in ctx.items())


def build_files_list(root_dir):
    """
    Build a list containing absolute paths to the generated files, ignoring
    files under .git/
    """
    root_path = Path(root_dir)
    files = [str(file.absolute()) for file in root_path.glob("**/*") if file.is_file()]
    return list(filter(lambda f: ".git/" not in f, files))


def check_files(files):
    """Method to check all files have correct substitutions."""
    # Assert that no match is found in any of the files
    pattern = r"{{(\s?cookiecutter)[.](.*?)}}"
    re_obj = re.compile(pattern)
    for file in files:
        for line in open(file, "r"):
            match = re_obj.search(line)
            assert match is None, f"cookiecutter variable not replaced in {file}"


@pytest.mark.parametrize(
    "context_override",
    get_supported_combinations(),
    ids=_fixture_id,
)
def test_supported_options(cookies, context_override):
    """
    Test all supported cookiecutter-python answer combinations
    """
    result = cookies.bake(extra_context=context_override)

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == context_override["project_slug"]
    assert result.project.isdir()

    files = build_files_list(str(result.project))
    assert files
    check_files(files)


def test_default_project(cookies):
    """
    Test a default cookiecutter-python project thoroughly
    """
    # Allow the post generation hooks to run, which include git init activities
    if os.environ.get("GITHUB_ACTIONS") == "true":
        os.environ["RUN_POST_HOOK"] = "true"

    result = cookies.bake()
    project = Path(result.project)

    repo = git.Repo(project)
    if repo.is_dirty(untracked_files=True):
        pytest.fail("Something went wrong with the project's post-generation hook")

    try:
        subprocess.run(
            ["pipenv", "run", "invoke", "test"],
            capture_output=True,
            check=True,
            cwd=project,
        )
    except subprocess.CalledProcessError as error:
        pytest.fail(error.stderr.decode("utf-8"))

    # Validate CI
    for filename in ["ci.yml"]:
        with open(f"{result.project}/.github/workflows/{filename}", "r") as file:
            try:
                github_config = yaml.safe_load(file)
                compliant = False
                for action_step in github_config["jobs"]["test"]["steps"]:
                    if action_step.get("uses") == "seisollc/goat@main":
                        compliant = True
                assert compliant
            except yaml.YAMLError as exception:
                pytest.fail(exception)
