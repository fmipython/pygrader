"""Module for handling external resources."""

import json
import logging
import os
from typing import Optional
from urllib.parse import urlparse

import requests

# from cove_sdk._uri import is_cove_uri
from cove_sdk import BaseItem, PythonItem, fetch_uri, is_cove_uri
from cove_sdk.exceptions import CoveAPIError, URIParseError
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


def is_resource_cove(resource_path: str) -> bool:
    """
    Check if a file is a Cove resource.

    :param resource_path: The path to the resource
    :return: True if the resource is a Cove resource, False otherwise
    """
    return is_cove_uri(resource_path)


def download_file_from_url(url: str, filename: Optional[str] = None) -> str:
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
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3.raw",
        }
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


# TODO - This is similar to the download_file_from_url
def download_python_file_from_cove(cove_uri: str, filename: Optional[str] = None) -> str:
    """
    Download a file from a Cove URI and save it in temp_files under the pygrader root directory.

    :param cove_uri: The Cove URI to download the file from
    :return: The path to the saved file
    """
    logger.log(VERBOSE, "Downloading file from Cove URI %s", cove_uri)

    os.makedirs(TEMP_FILES_DIR, exist_ok=True)

    result = fetch_from_cove(cove_uri)

    if not isinstance(result, PythonItem):
        raise ExternalResourceError(f"Cove resource is not a Python item: {cove_uri}")

    if filename is None:
        filename = result.key

    file_path = os.path.join(TEMP_FILES_DIR, f"{filename}.py")

    with open(file_path, "w+", encoding="utf-8") as file:
        file.write(result.python_value)

    return file_path


def fetch_from_cove(cove_uri: str) -> BaseItem:
    """
    Fetch a resource from a cove URI.

    Handle error cases and return the result as a BaseItem.

    :return: The fetched resource as a BaseItem
    """
    if "COVE_API_KEY" not in os.environ:
        raise ExternalResourceError("COVE_API_KEY environment variable is not set, required to fetch Cove resources")

    try:
        result = fetch_uri(cove_uri, api_key=os.environ["COVE_API_KEY"])
    except (CoveAPIError, URIParseError) as exc:
        raise ExternalResourceError(f"Error parsing Cove URI: {cove_uri}") from exc

    if result is None:
        raise ExternalResourceError(f"Cove resource not found: {cove_uri}")

    return result


class ExternalResourceError(Exception):
    """Custom exception for external resource errors."""
