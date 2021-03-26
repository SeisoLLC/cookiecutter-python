#!/usr/bin/env python3
"""
Test {{cookiecutter.project_slug }}/config.py
"""

import pytest


def test_get_args_config():
    """Test get_args_config()"""
    pytest.warns("g_a_c")
    assert True


def test_setup_logging():
    """Test setup_logging()"""
    pytest.warns("s_l")
    assert True


def test_create_arg_parser():
    """Test create_arg_parser()"""
    pytest.warns("c_a_p")
    assert True
