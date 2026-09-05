"""Module for handling external resources."""

import json
import logging
import os
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

import requests

# from cove_sdk._uri import is_cove_uri
from cove_sdk import JSONItem, PythonItem, fetch_uri, is_cove_uri
from cove_sdk.exceptions import CoveAPIError, URIParseError
from dotenv import load_dotenv

from grader.exceptions import ResourceError
from grader.utils.constants import TEMP_FILES_DIR
from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")
load_dotenv()


class ResourceType(Enum):
    """Enum for resource types."""

    LOCAL = 0
    REMOTE = 1
    COVE = 2


class Resource:
    """Class that handles resources in the grader, regardless of their origin."""

    def __init__(self, source: str):
        """
        Create the resource.

        Actual content is not loaded until read() is called, to avoid unnecessary downloads.
        :param source: Local path, URL or Cove URI to the resource
        """
        self._source = source
        self._content: str | None = None
        self._type = Resource._sniff_resource_type(self._source)
        self._filename = ""

    def read(self) -> str:
        """Read the content of the resource."""
        if self._content is None:
            self._content, self._filename = self._download(self._source, self._type)

        return self._content

    def to_file(self) -> str:
        """
        Write the content of the resource to a temporary file and return the path to it.

        If the resource is already a local file, returns the path to it.
        """
        if self._type == ResourceType.LOCAL:
            return self._source

        content = self.read()
        file_path = os.path.join(TEMP_FILES_DIR, self._filename)
        os.makedirs(TEMP_FILES_DIR, exist_ok=True)

        with open(file_path, "w+", encoding="utf-8") as file:
            file.write(content)

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
