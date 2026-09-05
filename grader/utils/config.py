"""Module for loading the configuration file."""

import json
from pathlib import Path

from grader.exceptions import InvalidConfigError
from grader.utils.external_resources import Resource
from grader.utils.json_with_templates import load_with_values


def load_config(config_path: str) -> dict:
    """
    Load the configuration file.

    :param config_path: Path, URL or Cove URI to the configuration file.
    :return: The configuration as a dictionary.
    """
    config_path_resolved = Resource(config_path).to_file()
    config = read_from_file(config_path_resolved)

    return config


def read_from_file(config_path: str) -> dict:
    """
    Read the configuration from a file.

    :param config_path: File path to the configuration file
    :return: The configuration as a dictionary
    """
    config_dir = str(Path(config_path).parent.absolute())
    try:
        config = load_with_values(config_path, config_dir=config_dir)
    except FileNotFoundError as exc:
        raise InvalidConfigError(f"Configuration file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise InvalidConfigError(f"Error parsing JSON configuration file: {config_path}") from exc

    return config
