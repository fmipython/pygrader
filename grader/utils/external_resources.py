"""
Module for handling external resources
"""

import logging
import os
from typing import Optional
from urllib.parse import urlparse

import requests

from grader.utils.constants import TEMP_FILES_DIR


logger = logging.getLogger("grader")


def is_resource_remote(resource_path: str) -> bool:
    """
    Check if a file is a remote resource.

    :param resource_path: The path to the resource
    :return: True if the resource is a remote resource, False otherwise
    """
    parsed_url = urlparse(resource_path)
    return parsed_url.scheme in ["http", "https", "ftp"]


def download_file_from_url(url: str, filename: Optional[str] = None) -> str:
    """
    Download a file from a URL and save it in temp_files under the pygrader root directory.

    :param url: The URL to download the file from
    :param filename: Optional filename to save as. If not provided, uses the last part of the URL path.
    :return: The path to the saved file
    """
    logger.info("Downloading file from %s", url)

    os.makedirs(TEMP_FILES_DIR, exist_ok=True)

    if filename is None:
        filename = os.path.basename(urlparse(url).path) or "downloaded_file"
    file_path = os.path.join(TEMP_FILES_DIR, filename)

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ExternalResourceError(f"Error downloading file from {url}") from e

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return file_path


class ExternalResourceError(Exception):
    """
    Custom exception for external resource errors.
    """
