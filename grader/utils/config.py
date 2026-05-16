"""
Module for loading the configuration file.
"""

import json
from pathlib import Path

from cove_sdk import CoveClient

from grader.utils.cove_config import CoveConfig
from grader.utils.external_resources import (
    ExternalResourceError,
    download_file_from_url,
    is_resource_remote,
)
from grader.utils.json_with_templates import load_with_values


def load_config_from_path(config_path: str) -> dict:
    """
    Load the configuration file.
    :param config_path: Path or URL to the configuration file.
    :return: The configuration as a dictionary.
    """

    if is_resource_remote(config_path):
        try:
            config_path = download_file_from_url(config_path, is_json=True)
        except ExternalResourceError as exc:
            raise InvalidConfigError(
                f"Could not load configuration from {config_path}"
            ) from exc

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


def load_config_from_cove(cove_config: CoveConfig) -> dict:
    with CoveClient(
        base_url=cove_config.base_url, api_key=cove_config.api_key
    ) as client:
        projects = client.projects.list()

        project = next(
            (p for p in projects if p.name == cove_config.project_name), None
        )

        if project is None:
            raise InvalidConfigError(
                f"Project '{cove_config.project_name}' not found in Cove at {cove_config.base_url}"
            )

        config = client.json_items.get(project_id=project.id, key="config")

        if config is None:
            raise InvalidConfigError(
                f"JSON item 'config' not found in project '{cove_config.project_name}' in Cove at {cove_config.base_url}"
            )

        return config.json_value


class InvalidConfigError(Exception):
    """
    Custom exception for invalid configuration files.
    """
