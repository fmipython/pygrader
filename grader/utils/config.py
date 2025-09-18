"""
Module for loading the configuration file.
"""

import json

from pathlib import Path

from grader.utils.external_resources import is_resource_remote, download_file_from_url, ExternalResourceError
from grader.utils.json_with_templates import load_with_values


def load_config(config_path: str) -> dict:
    """
    Load the configuration file.
    :param config_path: Path or URL to the configuration file.
    :return: The configuration as a dictionary.
    """

    if is_resource_remote(config_path):
        try:
            config_path = download_file_from_url(config_path)
        except ExternalResourceError as exc:
            raise InvalidConfigError(f"Could not load configuration from {config_path}") from exc

    config_dir = str(Path(config_path).parent.absolute())
    try:
        config = load_with_values(config_path, config_dir=config_dir)
    except FileNotFoundError as exc:
        raise InvalidConfigError(f"Configuration file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise InvalidConfigError(f"Error parsing JSON configuration file: {config_path}") from exc

    return config


class InvalidConfigError(Exception):
    """
    Custom exception for invalid configuration files.
    """
