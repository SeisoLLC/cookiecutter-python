#!/usr/bin/env python3
"""
Test cookiecutter-python
"""

import itertools
import json
from logging import basicConfig, getLogger
from pathlib import Path
import random
import string
import sys

import jinja2


LOG_FORMAT = json.dumps(
    {
        "timestamp": "%(asctime)s",
        "namespace": "%(name)s",
        "loglevel": "%(levelname)s",
        "message": "%(message)s",
    }
)
basicConfig(level="INFO", format=LOG_FORMAT)
LOG = getLogger("cookiecutter-python.testing")


def test_bake_project(cookies):
    """
    Test baking the cookiecutter-python project
    """
    result = cookies.bake()

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.isdir()


def test_all_the_options(cookies):
    """
    Test baking a cookiecutter-python with all of the possible options
    """
    all_the_options = []
    config_file = Path('./cookiecutter.json')
    with open(config_file, "r") as file_object:
        config = json.load(file_object)

    # For each item in the config, examine and use it.
    for key, value in config.items():
        options = []
        if isinstance(value, str):
            # Sanitize by removing the "cookiecutter." prefix
            sanitized_template = value.replace("cookiecutter.", "")

            # Add the rendered default to the options list
            template = jinja2.Template(sanitized_template)
            options.append(template.render(config))

            # Add a 32 character pseudorandom string to the options list
            characters = string.ascii_letters + string.digits + "-" + "-"
            options.append(''.join(random.choice(characters) for i in range(32)))
        elif isinstance(value, list):
            # Set the options list to all of the predefined possibilities
            options = value
        else:
            sys.exit(1)

        all_the_options.append(options)

    for options in list(itertools.product(*all_the_options)):
        extra_context = {}

        for key in config:
            extra_context[key] = options

        result = cookies.bake(extra_context=extra_context)
        assert result.exit_code == 0
        assert result.exception is None
        assert result.project.isdir()
