import argparse

from typing import Any


def get_args() -> dict[str, Any]:
    """
    Create the CLI parser and return the parsed arguments

    :returns: Dictionary, containing the parsed arguments
    """
    parser = argparse.ArgumentParser("Python project grader")

    parser.add_argument("project_root", type=str, help="The path to the project directory")
    parser.add_argument("-c", "--config", type=str, help="The path to the config file to use")
    parser.add_argument("--student-id", type=str, help="The student's id")

    return parser.parse_args().__dict__
