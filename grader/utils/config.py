"""
Module for loading the configuration file.
"""

import json


def load_config(config_file_path: str) -> dict:
    """
    Load the configuration file.
    :param config_file_path: Path to the configuration file.
    :return: The configuration as a dictionary.
    """
    with open(config_file_path, encoding="utf-8") as config_file:
        return json.load(config_file)


class InvalidConfigError(Exception):
    """
    Custom exception for invalid configuration files.
    """
