"""Module for handling external resources."""

import json
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

# from cove_sdk._uri import is_cove_uri
from cove_sdk import BaseItem, JSONItem, PythonItem, fetch_uri, is_cove_uri
from cove_sdk.exceptions import CoveAPIError, URIParseError
from dotenv import load_dotenv

from grader.exceptions import ResourceError
from grader.utils.constants import TEMP_FILES_DIR
from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")
load_dotenv()


class ResourceType(Enum):
    LOCAL = 0
    REMOTE = 1
    COVE = 2


class Resource:
    def __init__(self, source: str):
        self._source = source
        self._content: Optional[str] = None
        self._type = Resource._sniff_resource_type(self._source)
        self._filename = ""

    def read(self) -> str:
        if self._content is None:
            self._content, self._filename = self._download(self._source, self._type)

        return self._content

    def to_file(self) -> str:
        if self._type == ResourceType.LOCAL:
            return self._source

        file_path = os.path.join(TEMP_FILES_DIR, self._filename)

        with open(file_path, "w+", encoding="utf-8") as file:
            file.write(self.read())

        return file_path

    @staticmethod
    def _sniff_resource_type(source: str) -> ResourceType:
        if Resource._is_resource_cove(source):
            return ResourceType.COVE
        elif Resource._is_resource_remote(source):
            return ResourceType.REMOTE
        else:
            return ResourceType.LOCAL

    @staticmethod
    def _download(source: str, resource_type: ResourceType) -> tuple[str, str]:
        match resource_type:
            case ResourceType.COVE:
                return Resource._fetch_from_cove(source)
            case ResourceType.REMOTE:
                return Resource._download_file_from_url(source)
            case ResourceType.LOCAL:
                return Resource._read_local_file(source)

    @staticmethod
    def _is_resource_remote(resource_path: str) -> bool:
        """
        Check if a file is a remote resource.

        :param resource_path: The path to the resource
        :return: True if the resource is a remote resource, False otherwise
        """
        parsed_url = urlparse(resource_path)
        return parsed_url.scheme in ["http", "https", "ftp"]

    @staticmethod
    def _is_resource_cove(resource_path: str) -> bool:
        """
        Check if a file is a Cove resource.

        :param resource_path: The path to the resource
        :return: True if the resource is a Cove resource, False otherwise
        """
        return is_cove_uri(resource_path)

    @staticmethod
    def _download_file_from_url(url: str) -> tuple[str, str]:
        """
        Download a file from a URL and save it in temp_files under the pygrader root directory.

        :param url: The URL to download the file from
        :param filename: Optional filename to save as. If not provided, uses the last part of the URL path.
        :return: The path to the saved file
        """
        logger.log(VERBOSE, "Downloading file from %s", url)

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ResourceError(f"Error downloading file from {url}") from exc

        filename = os.path.basename(urlparse(url).path) or "downloaded_file"
        # URLs that require tokens (Github private repos) are out of scope for now
        return response.text, filename

    @staticmethod
    def _read_local_file(path: str) -> tuple[str, str]:
        try:
            file = Path(path)
            return file.read_text(), file.name
        except FileNotFoundError as exc:
            raise ResourceError(f"Local file not found: {path}") from exc
        except OSError as exc:
            raise ResourceError(f"Error reading local file: {path}") from exc

    @staticmethod
    def _fetch_from_cove(cove_uri: str) -> tuple[str, str]:
        """
        Fetch a resource from a cove URI.

        Handle error cases and return the result as a BaseItem.

        :return: The fetched resource as a string
        """
        if "COVE_API_KEY" not in os.environ:
            raise ResourceError("COVE_API_KEY environment variable is not set, required to fetch Cove resources")

        try:
            result = fetch_uri(cove_uri, api_key=os.environ["COVE_API_KEY"])
        except (CoveAPIError, URIParseError) as exc:
            raise ResourceError(f"Error parsing Cove URI: {cove_uri}") from exc

        if result is None:
            raise ResourceError(f"Cove resource not found: {cove_uri}")

        match result:
            case JSONItem():
                return json.dumps(result.json_value), f"{result.key}.json"
            case PythonItem():
                return result.python_value, f"{result.key}.py"
            case _:
                raise ResourceError("Cove result is unknown")


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
        raise ResourceError(f"Error downloading file from {url}") from exc

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
        raise ResourceError(f"Cove resource is not a Python item: {cove_uri}")

    if filename is None:
        filename = result.key

    file_path = os.path.join(TEMP_FILES_DIR, f"{filename}.py")

    with open(file_path, "w+", encoding="utf-8") as file:
        file.write(result.python_value)

    return file_path


def fetch_json_from_cove(cove_uri: str) -> dict:
    """
    Fetch a JSON resource from a Cove URI.

    :param cove_uri: The Cove URI to fetch the JSON from
    :raises ExternalResourceError: If the resource cannot be fetched or is not a JSON item
    :return: The contents of the JSON item
    """
    logger.log(VERBOSE, "Fetching JSON from Cove URI %s", cove_uri)

    result = fetch_from_cove(cove_uri)

    if not isinstance(result, JSONItem):
        raise ResourceError(f"Cove resource is not a JSON item: {cove_uri}")

    return result.json_value


def fetch_from_cove(cove_uri: str) -> BaseItem:
    """
    Fetch a resource from a cove URI.

    Handle error cases and return the result as a BaseItem.

    :return: The fetched resource as a BaseItem
    """
    if "COVE_API_KEY" not in os.environ:
        raise ResourceError("COVE_API_KEY environment variable is not set, required to fetch Cove resources")

    try:
        result = fetch_uri(cove_uri, api_key=os.environ["COVE_API_KEY"])
    except (CoveAPIError, URIParseError) as exc:
        raise ResourceError(f"Error parsing Cove URI: {cove_uri}") from exc

    if result is None:
        raise ResourceError(f"Cove resource not found: {cove_uri}")

    return result
