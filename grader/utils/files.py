"""
Module containing the file-related functions.
"""

import os
from typing import Optional

import grader.utils.constants as const
from grader.utils.structure_validator import StructureValidator


def find_all_python_files(project_root_dir: str) -> list[str]:
    """
    Find all python files in the project directory.

    :param project_root_dir: The path to the project directory
    :return: A list of all python files in the project directory
    """
    python_structure = StructureValidator(name="Python Files", required=False, patterns=["**/*.py"])
    python_files = python_structure.get_matching_files(project_root_dir)
    return [file for file in python_files if all(venv_path not in file for venv_path in const.POSSIBLE_VENV_DIRS)]


def find_all_source_files(project_root_dir: str) -> list[str]:
    """
    Find all source files in the project directory.

    :param project_root_dir: The path to the project directory
    :return: A list of all source files in the project directory
    """
    all_files = find_all_python_files(project_root_dir)
    tests_directory = get_tests_directory_name(project_root_dir)
    test_files = find_all_test_files(tests_directory)

    return [file for file in all_files if file not in test_files]


def find_all_test_files(tests_directory: Optional[str] = None) -> list[str]:
    """
    Find all test files in the project directory.

    :param tests_directory: The tests directory, defaults to None
    :return: A list of all test files in the project directory. If no tests directory is found, return an empty list
    """
    if tests_directory is None:
        return []

    test_structure = StructureValidator(name="Test Files", required=False, patterns=["**/*.py"])
    return test_structure.get_matching_files(tests_directory)


def get_tests_directory_name(project_root_dir: str) -> Optional[str]:
    """
    Check if the project directory contains a tests directory.

    :param project_root_dir: The path to the project directory
    :returns: The path to the tests directory if found, otherwise None
    """
    for possible_directory in const.POSSIBLE_TEST_DIRS:
        possible_tests_path = os.path.join(project_root_dir, possible_directory)
        if os.path.exists(possible_tests_path):
            return possible_tests_path

    return None


def find_all_files_under_directory(directory: str, extension: str) -> list[str]:
    """
    Find all files under a directory with a specific extension.

    :param directory: The directory to search in
    :param extension: The extension of the files to search for
    :return: A list of all files under the directory with the specified extension
    :rtype: list[str]
    """
    files = [
        os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(extension)
    ]

    return files
