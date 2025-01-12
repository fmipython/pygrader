"""
Module containing the file-related functions.
"""
import os

import grader.utils.constants as const


def find_all_python_files(project_root_dir: str) -> list[str]:
    """
    Find all python files in the project directory

    :param project_root_dir: The path to the project directory
    :return: A list of all python files in the project directory
    """
    python_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(project_root_dir)
        for file in files
        if file.endswith(".py") and ".venv" not in root
    ]

    return python_files

def find_source_files(project_root_dir: str) -> list[str]:
    """
    Find all source files in the project directory

    :param project_root_dir: The path to the project directory
    :return: A list of all source files in the project directory
    """
    source_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(project_root_dir)
        for file in files
        if ".venv" not in root
    ]

    return source_files


def find_all_test_files(project_root_dir: str) -> list[str]:
    pass


def is_tests_directory_present(project_root_dir: str) -> bool:
    """
    Check if the project directory contains a tests directory.

    Args:
        project_root_dir: The path to the project directory

    Returns:
        bool: True if the project directory contains a tests directory, False otherwise
    """
    for possible_directory in const.POSSIBLE_TEST_DIRS:
        if os.path.exists(os.path.join(project_root_dir, possible_directory)):
            return True
    
    return False
