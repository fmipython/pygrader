"""
Module for handling external resources
"""

import json
import logging
import os
from typing import Optional
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

from grader.utils.constants import TEMP_FILES_DIR
from grader.utils.logger import VERBOSE


logger = logging.getLogger("grader")
load_dotenv()


def is_resource_remote(resource_path: str) -> bool:
    """
    Check if a file is a remote resource.

    :param resource_path: The path to the resource
    :return: True if the resource is a remote resource, False otherwise
    """
    parsed_url = urlparse(resource_path)
    return parsed_url.scheme in ["http", "https", "ftp"]


def download_file_from_url(url: str, filename: Optional[str] = None, is_json: bool = False) -> str:
    """
    Download a file from a URL and save it in temp_files under the pygrader root directory.

    :param url: The URL to download the file from
    :param filename: Optional filename to save as. If not provided, uses the last part of the URL path.
    :return: The path to the saved file
    """
    logger.log(VERBOSE, "Downloading file from %s", url)

    os.makedirs(TEMP_FILES_DIR, exist_ok=True)

    if filename is None:
        filename = os.path.basename(urlparse(url).path) or "downloaded_file"
    file_path = os.path.join(TEMP_FILES_DIR, filename)

    token = os.getenv("github_token")

    if token is not None:
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3.raw"}
    else:
        headers = {}

    try:
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ExternalResourceError(f"Error downloading file from {url}") from exc

    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    # If a token is not passed, content is returned in a different way
    # Github stuff

    with open(file_path, "r") as file:
        try:
            parsed = json.load(file)
        except json.JSONDecodeError:
            pass
        else:
            if "download_url" in parsed:
                return download_file_from_url(parsed["download_url"], filename)

    return file_path


class ExternalResourceError(Exception):
    """
    Custom exception for external resource errors.
    """
