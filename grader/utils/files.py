"""
Module containing the file-related functions.
"""
import os


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
