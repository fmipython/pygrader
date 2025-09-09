"""
Module for loading the configuration file.
"""

import json
from grader.utils.external_resources import is_resource_remote, download_file_from_url, ExternalResourceError


def load_config(config_path: str) -> dict:
    """
    Load the configuration file.
    :param config_path: Path or URL to the configuration file.
    :return: The configuration as a dictionary.
    """

    if is_resource_remote(config_path):
        try:
            config_path = download_file_from_url(config_path)
        except ExternalResourceError as e:
            raise InvalidConfigError(f"Could not load configuration from {config_path}") from e

    try:
        with open(config_path, encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError as e:
        raise InvalidConfigError(f"Configuration file not found: {config_path}") from e
    except json.JSONDecodeError as e:
        raise InvalidConfigError(f"Error parsing JSON configuration file: {config_path}") from e


class InvalidConfigError(Exception):
    """
    Custom exception for invalid configuration files.
    """
