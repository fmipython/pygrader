"""Unit tests for the Resource class in external_resources."""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

import requests
from cove_sdk import BaseItem, JSONItem, PythonItem
from cove_sdk.exceptions import CoveAPIError, URIParseError

from grader.exceptions import ResourceError
from grader.utils.constants import TEMP_FILES_DIR
from grader.utils.external_resources import Resource, ResourceType


class TestIsResourceRemote(unittest.TestCase):
    """Unit tests for Resource._is_resource_remote."""

    def test_01_scheme_http(self) -> None:
        """Test if the function correctly identifies a remote resource with HTTP scheme."""
        self.assertTrue(Resource._is_resource_remote("http://example.com/resource"))

    def test_02_scheme_https(self) -> None:
        """Test if the function correctly identifies a remote resource with HTTPS scheme."""
        self.assertTrue(Resource._is_resource_remote("https://example.com/resource"))

    def test_03_scheme_ftp(self) -> None:
        """Test if the function correctly identifies a remote resource with FTP scheme."""
        self.assertTrue(Resource._is_resource_remote("ftp://example.com/resource"))

    def test_04_scheme_file(self) -> None:
        """Test if the function correctly identifies a local resource with file scheme."""
        self.assertFalse(Resource._is_resource_remote("file:///path/to/resource"))

    def test_05_no_scheme(self) -> None:
        """Test if the function correctly identifies a local resource without a scheme."""
        self.assertFalse(Resource._is_resource_remote("/path/to/resource"))


class TestIsResourceCove(unittest.TestCase):
    """Unit tests for Resource._is_resource_cove."""

    @patch("grader.utils.external_resources.is_cove_uri")
    def test_01_delegates_to_is_cove_uri(self, mock_is_cove_uri: MagicMock) -> None:
        """Test that the function delegates to cove_sdk's is_cove_uri."""
        mock_is_cove_uri.return_value = True

        result = Resource._is_resource_cove("cove://example/resource")

        self.assertTrue(result)
        mock_is_cove_uri.assert_called_once_with("cove://example/resource")


class TestSniffResourceType(unittest.TestCase):
    """Unit tests for Resource._sniff_resource_type."""

    @patch.object(Resource, "_is_resource_cove", return_value=True)
    @patch.object(Resource, "_is_resource_remote", return_value=False)
    def test_01_cove_takes_priority(self, _: MagicMock, __: MagicMock) -> None:
        """Test that a Cove URI is sniffed as COVE."""
        self.assertEqual(Resource._sniff_resource_type("cove://example/resource"), ResourceType.COVE)

    @patch.object(Resource, "_is_resource_cove", return_value=False)
    @patch.object(Resource, "_is_resource_remote", return_value=True)
    def test_02_remote(self, _: MagicMock, __: MagicMock) -> None:
        """Test that a remote URL is sniffed as REMOTE."""
        self.assertEqual(Resource._sniff_resource_type("http://example.com/resource"), ResourceType.REMOTE)

    @patch.object(Resource, "_is_resource_cove", return_value=False)
    @patch.object(Resource, "_is_resource_remote", return_value=False)
    def test_03_local(self, _: MagicMock, __: MagicMock) -> None:
        """Test that a local path is sniffed as LOCAL."""
        self.assertEqual(Resource._sniff_resource_type("/path/to/resource"), ResourceType.LOCAL)


class TestReadLocalFile(unittest.TestCase):
    """Unit tests for Resource._read_local_file."""

    @patch("pathlib.Path.read_text")
    def test_01_reads_file_contents_and_name(self, mock_read_text: MagicMock) -> None:
        """Test that the function reads file contents and returns the file name."""
        mock_read_text.return_value = "file contents"

        content, name = Resource._read_local_file("/folderA/resource.txt")

        self.assertEqual(content, "file contents")
        self.assertEqual(name, "resource.txt")

    @patch("pathlib.Path.read_text", side_effect=FileNotFoundError)
    def test_02_missing_file_raises_resource_error(self, _: MagicMock) -> None:
        """Test that a missing file raises ResourceError."""
        with self.assertRaises(ResourceError):
            Resource._read_local_file("/missing/resource.txt")

    @patch("pathlib.Path.read_text", side_effect=OSError)
    def test_03_os_error_raises_resource_error(self, _: MagicMock) -> None:
        """Test that an OSError while reading raises ResourceError."""
        with self.assertRaises(ResourceError):
            Resource._read_local_file("/broken/resource.txt")


class TestDownloadFileFromUrl(unittest.TestCase):
    """Unit tests for Resource._download_file_from_url."""

    @patch("requests.get")
    def test_01_returns_text_and_filename_from_url_path(self, mock_get: MagicMock) -> None:
        """Test that the function returns the response text and filename parsed from the URL."""
        mock_get.return_value = MagicMock(text="file contents")

        content, filename = Resource._download_file_from_url("http://example.com/folderA/resource.txt")

        self.assertEqual(content, "file contents")
        self.assertEqual(filename, "resource.txt")

    @patch("requests.get")
    def test_02_default_filename_when_url_has_no_path(self, mock_get: MagicMock) -> None:
        """Test that a default filename is used when the URL has no path component."""
        mock_get.return_value = MagicMock(text="file contents")

        _, filename = Resource._download_file_from_url("http://example.com")

        self.assertEqual(filename, "downloaded_file")

    @patch("requests.get")
    def test_03_download_raises_resource_error_on_failure(self, mock_get: MagicMock) -> None:
        """Test that a failed request raises ResourceError."""
        mock_get.side_effect = requests.RequestException("Download failed")

        with self.assertRaises(ResourceError):
            Resource._download_file_from_url("http://example.com/resource")


class TestFetchFromCove(unittest.TestCase):
    """Unit tests for Resource._fetch_from_cove."""

    def test_01_missing_cove_api_key_raises_error(self) -> None:
        """Test that a missing COVE_API_KEY raises ResourceError."""
        env_without_key = {k: v for k, v in os.environ.items() if k != "COVE_API_KEY"}

        with patch.dict("os.environ", env_without_key, clear=True), self.assertRaises(ResourceError):
            Resource._fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_02_fetch_uri_raises_cove_api_error(self, mock_fetch: MagicMock) -> None:
        """Test that a CoveAPIError from fetch_uri is wrapped in ResourceError."""
        mock_fetch.side_effect = CoveAPIError("API error", detail="some detail")

        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}), self.assertRaises(ResourceError):
            Resource._fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_03_fetch_uri_raises_uri_parse_error(self, mock_fetch: MagicMock) -> None:
        """Test that a URIParseError from fetch_uri is wrapped in ResourceError."""
        mock_fetch.side_effect = URIParseError("Parse error")

        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}), self.assertRaises(ResourceError):
            Resource._fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_04_fetch_uri_returns_none_raises_error(self, mock_fetch: MagicMock) -> None:
        """Test that None returned from fetch_uri raises ResourceError."""
        mock_fetch.return_value = None

        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}), self.assertRaises(ResourceError):
            Resource._fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_05_json_item_returns_dumped_json_and_filename(self, mock_fetch: MagicMock) -> None:
        """Test that a JSONItem is returned as dumped JSON with a .json filename."""
        expected_json = {"source": {"name": "Source files", "required": True, "patterns": ["src/**/*.py"]}}
        mock_item = MagicMock(spec=JSONItem)
        mock_item.json_value = expected_json
        mock_item.key = "my_config"
        mock_fetch.return_value = mock_item

        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}):
            content, filename = Resource._fetch_from_cove("cove://example/resource")

        self.assertEqual(content, json.dumps(expected_json))
        self.assertEqual(filename, "my_config.json")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_06_python_item_returns_source_and_filename(self, mock_fetch: MagicMock) -> None:
        """Test that a PythonItem is returned as source code with a .py filename."""
        mock_item = MagicMock(spec=PythonItem)
        mock_item.python_value = "print('hello')"
        mock_item.key = "my_test"
        mock_fetch.return_value = mock_item

        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}):
            content, filename = Resource._fetch_from_cove("cove://example/resource")

        self.assertEqual(content, "print('hello')")
        self.assertEqual(filename, "my_test.py")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_07_unknown_item_type_raises_error(self, mock_fetch: MagicMock) -> None:
        """Test that an unrecognized Cove item type raises ResourceError."""
        mock_fetch.return_value = MagicMock(spec=BaseItem)

        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}), self.assertRaises(ResourceError):
            Resource._fetch_from_cove("cove://example/resource")


class TestResourceDownloadDispatch(unittest.TestCase):
    """Unit tests for Resource._download dispatching by resource type."""

    @patch.object(Resource, "_fetch_from_cove", return_value=("content", "file.json"))
    def test_01_cove_dispatches_to_fetch_from_cove(self, mock_fetch: MagicMock) -> None:
        """Test that COVE resources are downloaded via _fetch_from_cove."""
        result = Resource._download("cove://example/resource", ResourceType.COVE)

        self.assertEqual(result, ("content", "file.json"))
        mock_fetch.assert_called_once_with("cove://example/resource")

    @patch.object(Resource, "_download_file_from_url", return_value=("content", "file.txt"))
    def test_02_remote_dispatches_to_download_file_from_url(self, mock_download: MagicMock) -> None:
        """Test that REMOTE resources are downloaded via _download_file_from_url."""
        result = Resource._download("http://example.com/resource", ResourceType.REMOTE)

        self.assertEqual(result, ("content", "file.txt"))
        mock_download.assert_called_once_with("http://example.com/resource")

    @patch.object(Resource, "_read_local_file", return_value=("content", "file.txt"))
    def test_03_local_dispatches_to_read_local_file(self, mock_read: MagicMock) -> None:
        """Test that LOCAL resources are read via _read_local_file."""
        result = Resource._download("/path/to/resource", ResourceType.LOCAL)

        self.assertEqual(result, ("content", "file.txt"))
        mock_read.assert_called_once_with("/path/to/resource")


class TestResourceRead(unittest.TestCase):
    """Unit tests for Resource.read."""

    @patch.object(Resource, "_download", return_value=("content", "file.txt"))
    def test_01_downloads_and_caches_content(self, mock_download: MagicMock) -> None:
        """Test that read downloads once and caches the content for subsequent calls."""
        resource = Resource("/path/file.txt")

        self.assertEqual(resource.read(), "content")
        self.assertEqual(resource.read(), "content")
        mock_download.assert_called_once()


class TestResourceToFile(unittest.TestCase):
    """Unit tests for Resource.to_file."""

    def test_01_local_resource_returns_source_path_unchanged(self) -> None:
        """Test that a local resource returns its source path without writing a file."""
        resource = Resource("/path/to/file.txt")

        self.assertEqual(resource.to_file(), "/path/to/file.txt")

    @patch("builtins.open")
    @patch.object(Resource, "_download", return_value=("content", "downloaded.txt"))
    def test_02_remote_resource_writes_content_to_temp_dir(self, _: MagicMock, mock_open: MagicMock) -> None:
        """Test that a non-local resource is written to TEMP_FILES_DIR and that path is returned."""
        resource = Resource("http://example.com/downloaded.txt")
        expected_path = os.path.join(TEMP_FILES_DIR, "downloaded.txt")

        result = resource.to_file()

        self.assertEqual(result, expected_path)
        mock_open.assert_called_once_with(expected_path, "w+", encoding="utf-8")
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with("content")
