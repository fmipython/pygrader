"""
Unit tests for the external resources functions.
"""

import unittest
from unittest.mock import patch, MagicMock

from grader.utils.external_resources import is_resource_remote, download_file_from_url
from grader.utils.constants import TEMP_FILES_DIR


class TestIsResourceRemote(unittest.TestCase):
    """
    Unit tests for the is_resource_remote function.
    """

    @patch("urllib.parse.urlparse")
    def test_01_scheme_http(self, mock_urlparse: MagicMock) -> None:
        """
        Test if the function correctly identifies a remote resource with HTTP scheme.
        """
        # Arrange
        mock_urlparse.return_value.scheme = "http"

        # Act
        result = is_resource_remote("http://example.com/resource")

        # Assert
        self.assertTrue(result)

    @patch("urllib.parse.urlparse")
    def test_02_scheme_https(self, mock_urlparse: MagicMock) -> None:
        """
        Test if the function correctly identifies a remote resource with HTTPS scheme.
        """
        # Arrange
        mock_urlparse.return_value.scheme = "https"

        # Act
        result = is_resource_remote("https://example.com/resource")

        # Assert
        self.assertTrue(result)

    @patch("urllib.parse.urlparse")
    def test_03_scheme_ftp(self, mock_urlparse: MagicMock) -> None:
        """
        Test if the function correctly identifies a remote resource with FTP scheme.
        """
        # Arrange
        mock_urlparse.return_value.scheme = "ftp"

        # Act
        result = is_resource_remote("ftp://example.com/resource")

        # Assert
        self.assertTrue(result)

    @patch("urllib.parse.urlparse")
    def test_04_scheme_file(self, mock_urlparse: MagicMock) -> None:
        """
        Test if the function correctly identifies a local resource with file scheme.
        """
        # Arrange
        mock_urlparse.return_value.scheme = "file"

        # Act
        result = is_resource_remote("file:///path/to/resource")

        # Assert
        self.assertFalse(result)

    @patch("urllib.parse.urlparse")
    def test_05_no_scheme(self, mock_urlparse: MagicMock) -> None:
        """
        Test if the function correctly identifies a local resource without a scheme.
        """
        # Arrange
        mock_urlparse.return_value.scheme = ""

        # Act
        result = is_resource_remote("/path/to/resource")

        # Assert
        self.assertFalse(result)


class TestDownloadFileFromUrl(unittest.TestCase):
    """
    Unit tests for the download_file_from_url function.
    """

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    def test_01_directory_created(self, mock_open: MagicMock, mock_makedirs: MagicMock, mock_get: MagicMock) -> None:
        """
        Test if the function creates the TEMP_FILES_DIR directory.
        """
        # Arrange
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])

        # Act
        download_file_from_url("http://example.com/resource")

        # Assert
        mock_makedirs.assert_called_once_with(TEMP_FILES_DIR, exist_ok=True)

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("urllib.parse.urlparse")
    def test_02_parse_filename_if_not_passed(
        self, mock_urlparse: MagicMock, mock_open: MagicMock, mock_makedirs: MagicMock, mock_get: MagicMock
    ) -> None:
        """
        Test if the function creates the TEMP_FILES_DIR directory.
        """
        # Arrange
        sample_filename = "resource"
        sample_filepath = f"/folderA/{sample_filename}"
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])
        mock_urlparse.return_value.path = sample_filepath

        # Act
        download_file_from_url(f"http://example.com{sample_filepath}")

        # Assert
        mock_open.assert_called_once_with(f"{TEMP_FILES_DIR}/{sample_filename}", "wb")

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("urllib.parse.urlparse")
    def test_03_default_filename(
        self, mock_urlparse: MagicMock, mock_open: MagicMock, mock_makedirs: MagicMock, mock_get: MagicMock
    ) -> None:
        """
        Test if the function creates the TEMP_FILES_DIR directory.
        """
        # Arrange
        sample_filename = ""
        sample_filepath = f"/folderA/{sample_filename}"
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])
        mock_urlparse.return_value.path = sample_filepath
        expected_filename = "downloaded_file"

        # Act
        download_file_from_url(f"http://example.com{sample_filepath}")

        # Assert
        mock_open.assert_called_once_with(f"{TEMP_FILES_DIR}/{expected_filename}", "wb")

    @patch("requests.get")
    @patch("os.makedirs")
    @patch("builtins.open")
    @patch("urllib.parse.urlparse")
    def test_04_passed_filename(
        self, mock_urlparse: MagicMock, mock_open: MagicMock, mock_makedirs: MagicMock, mock_get: MagicMock
    ) -> None:
        """
        Test if the function creates the TEMP_FILES_DIR directory.
        """
        # Arrange
        sample_filename = "resource"
        sample_filepath = f"/folderA/{sample_filename}"
        mock_get.return_value = MagicMock(status_code=200, iter_content=lambda chunk_size: [b"data"])
        mock_urlparse.return_value.path = sample_filepath
        expected_filename = "passed_filename.txt"

        # Act
        download_file_from_url(f"http://example.com{sample_filepath}", expected_filename)

        # Assert
        mock_open.assert_called_once_with(f"{TEMP_FILES_DIR}/{expected_filename}", "wb")
