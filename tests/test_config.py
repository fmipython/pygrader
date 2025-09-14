"""
Unit tests for the config module
"""

import unittest
import unittest.mock
from unittest.mock import patch, MagicMock
from grader.utils.config import load_config, InvalidConfigError
from grader.utils.external_resources import ExternalResourceError


class TestConfig(unittest.TestCase):
    """
    Unit tests for the config module.
    """

    @patch("grader.utils.config.is_resource_remote")
    @patch("grader.utils.config.download_file_from_url")
    def test_01_remote_resource_downloaded(self, mock_download: MagicMock, mock_is_remote: MagicMock) -> None:
        """
        Test if a remote resource is downloaded successfully.
        """
        # Arrange
        mock_is_remote.return_value = True
        mock_download.return_value = "file_content"

        sample_config_path = "http://example.com/config.json"

        # Act
        try:
            load_config(sample_config_path)
        except InvalidConfigError:
            pass

        # Assert
        mock_download.assert_called_once_with(sample_config_path)

    @patch("grader.utils.config.is_resource_remote")
    @patch("grader.utils.config.download_file_from_url")
    def test_02_remote_resource_download_raises_exception(
        self, mock_download: MagicMock, mock_is_remote: MagicMock
    ) -> None:
        """
        Test if an exception during remote resource download is handled properly.
        """
        # Arrange
        mock_is_remote.return_value = True
        mock_download.side_effect = ExternalResourceError("Download failed")

        sample_config_path = "http://example.com/config.json"

        # Act & Assert
        with self.assertRaises(InvalidConfigError):
            load_config(sample_config_path)

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data='{"key": "value"}')
    @patch("grader.utils.config.is_resource_remote")
    def test_03_local_file_loaded_successfully(self, mock_is_remote: MagicMock, mock_open: MagicMock) -> None:
        """
        Test if a local file is loaded successfully.
        """
        # Arrange
        mock_is_remote.return_value = False

        sample_config_path = "config.json"

        # Act
        config = load_config(sample_config_path)

        # Assert
        self.assertEqual(config, {"key": "value"})
        mock_open.assert_called_once_with(sample_config_path, encoding="utf-8")

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("grader.utils.config.is_resource_remote")
    def test_04_local_file_not_found(self, mock_is_remote: MagicMock, mock_open: MagicMock) -> None:
        """
        Test if a FileNotFoundError for a local file is handled properly.
        """
        # Arrange
        mock_is_remote.return_value = False
        mock_open.side_effect = FileNotFoundError

        sample_config_path = "non_existent_config.json"

        # Act & Assert
        with self.assertRaises(InvalidConfigError):
            load_config(sample_config_path)

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data='{"key": "value"')
    @patch("grader.utils.config.is_resource_remote")
    def test_05_local_file_invalid_json(self, mock_is_remote: MagicMock, _: MagicMock) -> None:
        """
        Test if invalid JSON in a local file is handled properly.
        """
        # Arrange
        mock_is_remote.return_value = False
        # The read_data is intentionally malformed JSON

        sample_config_path = "invalid_config.json"

        # Act & Assert
        with self.assertRaises(InvalidConfigError):
            load_config(sample_config_path)
