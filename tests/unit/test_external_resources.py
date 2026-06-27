"""Unit tests for the external resources functions."""

import os
import unittest
from unittest.mock import MagicMock, call, patch

import requests
from cove_sdk import BaseItem, PythonItem
from cove_sdk.exceptions import CoveAPIError, URIParseError

from grader.utils.constants import TEMP_FILES_DIR
from grader.utils.external_resources import (
    ExternalResourceError,
    download_file_from_url,
    download_python_file_from_cove,
    fetch_from_cove,
    is_resource_remote,
)


class TestIsResourceRemote(unittest.TestCase):
    """Unit tests for the is_resource_remote function."""

    @patch("urllib.parse.urlparse")
    def test_01_scheme_http(self, mock_urlparse: MagicMock) -> None:
        """Test if the function correctly identifies a remote resource with HTTP scheme."""
        # Arrange
        mock_urlparse.return_value.scheme = "http"

        # Act
        result = is_resource_remote("http://example.com/resource")

        # Assert
        self.assertTrue(result)

    @patch("urllib.parse.urlparse")
    def test_02_scheme_https(self, mock_urlparse: MagicMock) -> None:
        """Test if the function correctly identifies a remote resource with HTTPS scheme."""
        # Arrange
        mock_urlparse.return_value.scheme = "https"

        # Act
        result = is_resource_remote("https://example.com/resource")

        # Assert
        self.assertTrue(result)

    @patch("urllib.parse.urlparse")
    def test_03_scheme_ftp(self, mock_urlparse: MagicMock) -> None:
        """Test if the function correctly identifies a remote resource with FTP scheme."""
        # Arrange
        mock_urlparse.return_value.scheme = "ftp"

        # Act
        result = is_resource_remote("ftp://example.com/resource")

        # Assert
        self.assertTrue(result)

    @patch("urllib.parse.urlparse")
    def test_04_scheme_file(self, mock_urlparse: MagicMock) -> None:
        """Test if the function correctly identifies a local resource with file scheme."""
        # Arrange
        mock_urlparse.return_value.scheme = "file"

        # Act
        result = is_resource_remote("file:///path/to/resource")

        # Assert
        self.assertFalse(result)

    @patch("urllib.parse.urlparse")
    def test_05_no_scheme(self, mock_urlparse: MagicMock) -> None:
        """Test if the function correctly identifies a local resource without a scheme."""
        # Arrange
        mock_urlparse.return_value.scheme = ""

        # Act
        result = is_resource_remote("/path/to/resource")

        # Assert
        self.assertFalse(result)


class TestDownloadFileFromUrl(unittest.TestCase):
    """Unit tests for the download_file_from_url function."""

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    def test_01_directory_created(self, _: MagicMock, mock_makedirs: MagicMock, mock_get: MagicMock) -> None:
        """Test if the function creates the TEMP_FILES_DIR directory."""
        # Arrange
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])  # noqa: ARG005

        # Act
        with patch("json.load"):
            download_file_from_url("http://example.com/resource")

        # Assert
        mock_makedirs.assert_called_once_with(TEMP_FILES_DIR, exist_ok=True)

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("urllib.parse.urlparse")
    def test_02_parse_filename_if_not_passed(
        self, mock_urlparse: MagicMock, mock_open: MagicMock, _: MagicMock, mock_get: MagicMock
    ) -> None:
        """Test if the function creates the TEMP_FILES_DIR directory."""
        # Arrange
        sample_filename = "resource"
        sample_filepath = f"/folderA/{sample_filename}"
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])  # noqa: ARG005
        mock_urlparse.return_value.path = sample_filepath

        # Act
        with patch("json.load"):
            download_file_from_url(f"http://example.com{sample_filepath}")

        # Assert
        mock_open.assert_has_calls([call(f"{TEMP_FILES_DIR}/{sample_filename}", "wb")])

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("urllib.parse.urlparse")
    def test_03_default_filename(
        self, mock_urlparse: MagicMock, mock_open: MagicMock, _: MagicMock, mock_get: MagicMock
    ) -> None:
        """Test if the function creates the TEMP_FILES_DIR directory."""
        # Arrange
        sample_filename = ""
        sample_filepath = f"/folderA/{sample_filename}"
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])  # noqa: ARG005
        mock_urlparse.return_value.path = sample_filepath
        expected_filename = "downloaded_file"

        # Act
        with patch("json.load"):
            download_file_from_url(f"http://example.com{sample_filepath}")

        # Assert
        mock_open.assert_has_calls([call(f"{TEMP_FILES_DIR}/{expected_filename}", "wb")])

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("urllib.parse.urlparse")
    def test_04_passed_filename(
        self, mock_urlparse: MagicMock, mock_open: MagicMock, _: MagicMock, mock_get: MagicMock
    ) -> None:
        """Test if the function creates the TEMP_FILES_DIR directory."""
        # Arrange
        sample_filename = "resource"
        sample_filepath = f"/folderA/{sample_filename}"
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])  # noqa: ARG005
        mock_urlparse.return_value.path = sample_filepath
        expected_filename = "passed_filename.txt"

        # Act
        with patch("json.load"):
            download_file_from_url(f"http://example.com{sample_filepath}", expected_filename)

        # Assert
        mock_open.assert_has_calls([call(f"{TEMP_FILES_DIR}/{expected_filename}", "wb")])

    @patch("requests.get")
    def test_05_download_raises_exception_on_failure(self, mock_get: MagicMock) -> None:
        """Test if the function raises an exception when the download fails."""
        # Arrange
        mock_get.side_effect = requests.RequestException("Download failed")

        # Act / Assert
        with self.assertRaises(Exception):
            download_file_from_url("http://example.com/resource")


class TestFetchFromCove(unittest.TestCase):
    """Unit tests for the fetch_from_cove function."""

    def test_01_missing_cove_api_key_raises_error(self) -> None:
        """Test that a missing COVE_API_KEY raises ExternalResourceError."""
        # Arrange
        env_without_key = {k: v for k, v in os.environ.items() if k != "COVE_API_KEY"}

        # Act & Assert
        with patch.dict("os.environ", env_without_key, clear=True):
            with self.assertRaises(ExternalResourceError):
                fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_02_fetch_uri_raises_cove_api_error(self, mock_fetch: MagicMock) -> None:
        """Test that a CoveAPIError from fetch_uri is wrapped in ExternalResourceError."""
        # Arrange
        mock_fetch.side_effect = CoveAPIError("API error", detail="some detail")

        # Act & Assert
        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}):
            with self.assertRaises(ExternalResourceError):
                fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_03_fetch_uri_raises_uri_parse_error(self, mock_fetch: MagicMock) -> None:
        """Test that a URIParseError from fetch_uri is wrapped in ExternalResourceError."""
        # Arrange
        mock_fetch.side_effect = URIParseError("Parse error")

        # Act & Assert
        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}):
            with self.assertRaises(ExternalResourceError):
                fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_04_fetch_uri_returns_none_raises_error(self, mock_fetch: MagicMock) -> None:
        """Test that None returned from fetch_uri raises ExternalResourceError."""
        # Arrange
        mock_fetch.return_value = None

        # Act & Assert
        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}):
            with self.assertRaises(ExternalResourceError):
                fetch_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_uri")
    def test_05_fetch_uri_returns_valid_item(self, mock_fetch: MagicMock) -> None:
        """Test that a valid BaseItem returned from fetch_uri is returned as-is."""
        # Arrange
        mock_item = MagicMock(spec=BaseItem)
        mock_fetch.return_value = mock_item

        # Act
        with patch.dict("os.environ", {"COVE_API_KEY": "test_key"}):
            result = fetch_from_cove("cove://example/resource")

        # Assert
        self.assertEqual(result, mock_item)


class TestDownloadPythonFileFromCove(unittest.TestCase):
    """Unit tests for the download_python_file_from_cove function."""

    @patch("grader.utils.external_resources.fetch_from_cove")
    def test_01_fetch_from_cove_raises_error_propagates(self, mock_fetch: MagicMock) -> None:
        """Test that an ExternalResourceError from fetch_from_cove propagates."""
        # Arrange
        mock_fetch.side_effect = ExternalResourceError("fetch failed")

        # Act & Assert
        with self.assertRaises(ExternalResourceError):
            download_python_file_from_cove("cove://example/resource")

    @patch("grader.utils.external_resources.fetch_from_cove")
    def test_02_non_python_item_raises_error(self, mock_fetch: MagicMock) -> None:
        """Test that a non-PythonItem result raises ExternalResourceError."""
        # Arrange
        mock_fetch.return_value = MagicMock(spec=BaseItem)

        # Act & Assert
        with self.assertRaises(ExternalResourceError):
            download_python_file_from_cove("cove://example/resource")

    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("grader.utils.external_resources.fetch_from_cove")
    def test_03_default_filename_uses_result_key(
        self, mock_fetch: MagicMock, mock_open: MagicMock, _: MagicMock
    ) -> None:
        """Test that when no filename is given, result.key is used as the filename."""
        # Arrange
        mock_item = MagicMock(spec=PythonItem)
        mock_item.key = "my_test"
        mock_item.python_value = "print('hello')"
        mock_fetch.return_value = mock_item
        expected_path = os.path.join(TEMP_FILES_DIR, "my_test.py")

        # Act
        result = download_python_file_from_cove("cove://example/resource")

        # Assert
        self.assertEqual(result, expected_path)
        mock_open.assert_called_once_with(expected_path, "w+", encoding="utf-8")

    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("grader.utils.external_resources.fetch_from_cove")
    def test_04_explicit_filename_overrides_key(
        self, mock_fetch: MagicMock, mock_open: MagicMock, _: MagicMock
    ) -> None:
        """Test that a provided filename is used instead of result.key."""
        # Arrange
        mock_item = MagicMock(spec=PythonItem)
        mock_item.key = "original_key"
        mock_item.python_value = "print('hello')"
        mock_fetch.return_value = mock_item
        expected_path = os.path.join(TEMP_FILES_DIR, "custom_name.py")

        # Act
        result = download_python_file_from_cove("cove://example/resource", filename="custom_name")

        # Assert
        self.assertEqual(result, expected_path)
        mock_open.assert_called_once_with(expected_path, "w+", encoding="utf-8")

    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("grader.utils.external_resources.fetch_from_cove")
    def test_05_makedirs_called_for_temp_dir(
        self, mock_fetch: MagicMock, _: MagicMock, mock_makedirs: MagicMock
    ) -> None:
        """Test that os.makedirs is called to ensure the temp directory exists."""
        # Arrange
        mock_item = MagicMock(spec=PythonItem)
        mock_item.key = "my_test"
        mock_item.python_value = "print('hello')"
        mock_fetch.return_value = mock_item

        # Act
        download_python_file_from_cove("cove://example/resource")

        # Assert
        mock_makedirs.assert_called_once_with(TEMP_FILES_DIR, exist_ok=True)
