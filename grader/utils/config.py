"""
Module for loading the configuration file.
"""

import json
import os
from pathlib import Path

from cove_sdk import JSONItem, KeyValueItem, PythonItem, fetch_uri
from cove_sdk.exceptions import CoveAPIError, URIParseError

from grader.utils.external_resources import (
    ExternalResourceError,
    download_file_from_url,
    is_resource_cove,
    is_resource_remote,
)
from grader.utils.json_with_templates import load_with_values


def load_config(config_path: str) -> dict:
    """
    Load the configuration file.
    :param config_path: Path, URL or Cove URI to the configuration file.
    :return: The configuration as a dictionary.
    """

    if is_resource_cove(config_path):
        return load_from_cove(config_path)

    if is_resource_remote(config_path):
        try:
            config_path = download_file_from_url(config_path, is_json=True)
        except ExternalResourceError as exc:
            raise InvalidConfigError(
                f"Could not load configuration from {config_path}"
            ) from exc

    config = read_from_file(config_path)

    return config


def read_from_file(config_path: str) -> dict:
    """
    Read the configuration from a file

    :param config_path: File path to the configuration file
    :return: The configuration as a dictionary
    """
    config_dir = str(Path(config_path).parent.absolute())
    try:
        config = load_with_values(config_path, config_dir=config_dir)
    except FileNotFoundError as exc:
        raise InvalidConfigError(
            f"Configuration file not found: {config_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise InvalidConfigError(
            f"Error parsing JSON configuration file: {config_path}"
        ) from exc

    return config


def load_from_cove(cove_uri: str) -> dict:
    """
    Load the configuration from a Cove URI.

    :param cove_uri: The Cove URI to load the configuration from
    :return: The configuration as a dictionary
    """
    if "COVE_API_KEY" not in os.environ:
        raise InvalidConfigError(
            "COVE_API_KEY environment variable is not set, required to fetch Cove resources"
        )

    try:
        result = fetch_uri(cove_uri, api_key=os.environ["COVE_API_KEY"])
    except (CoveAPIError, URIParseError) as exc:
        raise InvalidConfigError(f"Error parsing Cove URI: {cove_uri}") from exc

    if result is None:
        raise InvalidConfigError(f"Cove resource not found: {cove_uri}")

    if not isinstance(result, JSONItem):
        raise InvalidConfigError(f"Cove resource is not a JSON item: {cove_uri}")

    print(result.json_value)
    return result.json_value


class InvalidConfigError(Exception):
    """
    Custom exception for invalid configuration files.
    """
