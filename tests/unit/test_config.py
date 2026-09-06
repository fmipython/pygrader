"""Unit tests for the config module."""

import unittest
from unittest.mock import MagicMock, mock_open, patch

from grader.exceptions import InvalidConfigError, ResourceError
from grader.utils.config import load_config, read_from_file


class TestLoadConfig(unittest.TestCase):
    """Unit tests for load_config."""

    @patch("grader.utils.config.read_from_file")
    @patch("grader.utils.config.Resource")
    def test_01_resolves_resource_to_file_and_reads_it(
        self, mock_resource_cls: MagicMock, mock_read_from_file: MagicMock
    ) -> None:
        """Test that load_config resolves the resource to a local path and reads it."""
        # Arrange
        sample_config_path = "http://example.com/config.json"
        mock_resource_cls.return_value.to_file.return_value = "/tmp/config.json"
        mock_read_from_file.return_value = {"key": "value"}

        # Act
        config = load_config(sample_config_path)

        # Assert
        self.assertEqual(config, {"key": "value"})
        mock_resource_cls.assert_called_once_with(sample_config_path)
        mock_read_from_file.assert_called_once_with("/tmp/config.json")

    @patch("grader.utils.config.Resource")
    def test_02_resource_error_propagates(self, mock_resource_cls: MagicMock) -> None:
        """Test that a ResourceError from resolving the resource is not swallowed."""
        # Arrange
        mock_resource_cls.return_value.to_file.side_effect = ResourceError("Download failed")

        # Act & Assert
        with self.assertRaises(ResourceError):
            load_config("http://example.com/config.json")


class TestReadFromFile(unittest.TestCase):
    """Unit tests for read_from_file."""

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_01_local_file_loaded_successfully(self, mock_file: MagicMock) -> None:
        """Test if a local file is loaded successfully."""
        # Arrange
        sample_config_path = "config.json"

        # Act
        config = read_from_file(sample_config_path)

        # Assert
        self.assertEqual(config, {"key": "value"})
        mock_file.assert_called_once_with(sample_config_path, encoding="utf-8")

    @patch("builtins.open", new_callable=mock_open)
    def test_02_local_file_not_found(self, mock_file: MagicMock) -> None:
        """Test if a FileNotFoundError for a local file is handled properly."""
        # Arrange
        mock_file.side_effect = FileNotFoundError

        # Act & Assert
        with self.assertRaises(InvalidConfigError):
            read_from_file("non_existent_config.json")

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"')
    def test_03_local_file_invalid_json(self, _: MagicMock) -> None:
        """Test if invalid JSON in a local file is handled properly."""
        # The read_data is intentionally malformed JSON

        # Act & Assert
        with self.assertRaises(InvalidConfigError):
            read_from_file("invalid_config.json")
