"""
Module containing the CLI arguments parser.
"""

import argparse

from typing import Any


def get_args() -> dict[str, Any]:
    """
    Create the CLI parser and return the parsed arguments

    My personal preference is to return a dictionary, instead of the normal argparse.Namespace object.
    :returns: Dictionary, containing the parsed arguments
    """
    parser = argparse.ArgumentParser("Python project grader")

    parser.add_argument("project_root", type=str, help="The path to the project directory")
    parser.add_argument("-c", "--config", type=str, help="The path to the config file to use")
    parser.add_argument("--student-id", type=str, help="The student's id")
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="Set verbosity (0: DEBUG, 1: VERBOSE, 2: INFO)"
    )
    parser.add_argument(
        "--skip-venv-creation", action="store_true", help="Skip the virtual environment creation", default=False
    )

    return parser.parse_args().__dict__
