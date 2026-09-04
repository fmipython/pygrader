"""Unit tests for the StructureCheck class in the structure_check module."""

import unittest
from json import JSONDecodeError
from unittest.mock import MagicMock, patch

from grader.checks.structure_check import StructureCheck
from grader.exceptions import CheckError, ResourceError
from grader.models.check_result import NonScoredCheckResult


class TestStructureCheck(unittest.TestCase):
    """Test cases for the StructureCheck class."""

    def setUp(self) -> None:
        """Set up the test environment."""
        self.structure_check = StructureCheck("structure", "sample_dir", "structure.json", is_venv_required=False)
        return super().setUp()

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_01_valid_structure(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns True when all structure elements are valid."""
        # Arrange
        mock_element = MagicMock()
        mock_element.is_structure_valid.return_value = True
        mock_element.required = True
        mock_load_structure_file.return_value = [mock_element]
        expected = NonScoredCheckResult(self.structure_check.name, True, "Structure is valid", "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_02_invalid_required_structure(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns False when a required structure element is invalid."""
        # Arrange
        mock_element = MagicMock()
        expected_element_name = "foo"
        mock_element.name = expected_element_name
        mock_element.is_structure_valid.return_value = False
        mock_element.required = True
        mock_load_structure_file.return_value = [mock_element]

        expected_info = f"Structure for '{expected_element_name}' is invalid."
        expected = NonScoredCheckResult(self.structure_check.name, False, expected_info, "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_03_invalid_non_required_structure(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns True when a non-required structure element is invalid."""
        # Arrange
        mock_element = MagicMock()
        mock_element.is_structure_valid.return_value = False
        mock_element.required = False
        mock_load_structure_file.return_value = [mock_element]

        expected = NonScoredCheckResult(self.structure_check.name, True, "Structure is valid", "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_04_empty_structure_file(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns True when the structure file is empty."""
        # Arrange
        mock_load_structure_file.return_value = []
        expected = NonScoredCheckResult(self.structure_check.name, True, "Structure is valid", "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_05_logs_structure_validity(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method logs the validity of each structure element."""
        # Arrange
        mock_element = MagicMock()
        mock_element.is_structure_valid.return_value = True
        mock_element.required = True
        mock_element.name = "test_element"
        mock_load_structure_file.return_value = [mock_element]
        expected_log_output = "Is test_element structure valid ?"

        with self.assertLogs("grader", level="DEBUG") as log:
            # Act
            self.structure_check.run()

        # Assert
        self.assertTrue(any(expected_log_output in message for message in log.output))

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_06_raises_check_error_on_invalid_structure_file(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method raises a CheckError when the structure file is invalid."""
        # Arrange
        mock_load_structure_file.side_effect = CheckError("Invalid structure file")

        # Act & Assert
        with self.assertRaises(CheckError):
            self.structure_check.run()

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_07_multiple_valid_elements(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns True when all structure elements are valid."""
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.is_structure_valid.return_value = True
        mock_element1.required = True

        mock_element2 = MagicMock()
        mock_element2.is_structure_valid.return_value = True
        mock_element2.required = False

        mock_load_structure_file.return_value = [mock_element1, mock_element2]
        expected = NonScoredCheckResult(self.structure_check.name, True, "Structure is valid", "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_08_multiple_elements_with_invalid_required(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns False when one required structure element is invalid."""
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.is_structure_valid.return_value = True
        mock_element1.required = True

        mock_element2 = MagicMock()
        expected_element_name = "bar"
        mock_element2.name = expected_element_name
        expected_info = f"Structure for '{expected_element_name}' is invalid."
        mock_element2.is_structure_valid.return_value = False
        mock_element2.required = True

        mock_load_structure_file.return_value = [mock_element1, mock_element2]
        expected = NonScoredCheckResult(self.structure_check.name, False, expected_info, "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_09_multiple_elements_with_invalid_non_required(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns True when only non-required structure elements are invalid."""
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.is_structure_valid.return_value = True
        mock_element1.required = True

        mock_element2 = MagicMock()
        mock_element2.is_structure_valid.return_value = False
        mock_element2.required = False

        mock_load_structure_file.return_value = [mock_element1, mock_element2]
        expected = NonScoredCheckResult(self.structure_check.name, True, "Structure is valid", "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_10_all_invalid_elements(self, mock_load_structure_file: MagicMock) -> None:
        """Verify that the run method returns False when all structure elements are invalid and at least one is required."""
        # Arrange
        mock_element1 = MagicMock()
        expected_element1_name = "foo"
        mock_element1.name = expected_element1_name
        mock_element1.is_structure_valid.return_value = False
        mock_element1.required = True

        mock_element2 = MagicMock()
        expected_element2_name = "bar"
        mock_element2.name = expected_element2_name
        mock_element2.is_structure_valid.return_value = False
        mock_element2.required = False

        mock_load_structure_file.return_value = [mock_element1, mock_element2]

        expected_info = f"Structure for '{expected_element1_name}' is invalid."
        expected = NonScoredCheckResult(self.structure_check.name, False, expected_info, "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.utils.structure_validator.StructureValidator.is_structure_valid")
    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.json.load")
    def test_11_load_structure_file_valid(
        self, mock_safe_load: MagicMock, mock_open: MagicMock, mock_structure_valid: MagicMock
    ) -> None:
        """Verify that run correctly processes a valid structure file."""
        # Arrange
        mock_safe_load.return_value = {
            "source": {"name": "Source files", "required": True, "patterns": ["src/**/*.py"]},
            "init": {"name": "Init files", "required": True, "patterns": ["src/**/__init__.py"]},
            "tests": {"name": "Test files", "required": False, "patterns": ["tests/**/*.py", "tst/**/*.py"]},
            "requirements": {"name": "Requirements file", "required": False, "patterns": ["requirements.txt"]},
            "main": {"name": "Main file", "required": True, "patterns": ["main.py"]},
            "readme": {"name": "Readme file", "required": False, "patterns": ["README.md"]},
        }
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_structure_valid.return_value = True

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.json.load")
    @patch("grader.checks.structure_check.open", create=True)
    def test_12_load_structure_file_invalid(self, mock_open: MagicMock, mock_safe_load: MagicMock) -> None:
        """Verify that run raises CheckError for an invalid structure file."""
        # Arrange
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_safe_load.return_value = {"first": {"second": -1}}

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Invalid structure file", str(context.exception))

    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.json.load")
    def test_13_load_structure_file_empty(self, mock_safe_load: MagicMock, mock_open: MagicMock) -> None:
        """Verify that run returns True for an empty structure file."""
        # Arrange
        mock_safe_load.return_value = {}
        mock_open.return_value.__enter__.return_value = MagicMock()

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.json.load")
    def test_14_load_structure_file_yaml_error(self, mock_safe_load: MagicMock, mock_open: MagicMock) -> None:
        """Verify that run raises CheckError for a YAMLError."""
        # Arrange

        mock_safe_load.side_effect = JSONDecodeError("Expecting value", "doc", 0)
        mock_open.return_value.__enter__.return_value = MagicMock()

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Invalid structure file", str(context.exception))

    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.json.load")
    def test_15_load_structure_file_not_found(self, mock_safe_load: MagicMock, mock_open: MagicMock) -> None:
        """Verify that run raises CheckError for a FileNotFoundError."""
        # Arrange
        mock_open.side_effect = FileNotFoundError("File not found")
        mock_safe_load.return_value = {}

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Cannot read structure file", str(context.exception))

    @patch("grader.checks.structure_check.download_file_from_url")
    def test_16_load_structure_file_remote_download_fails(self, mock_download: MagicMock) -> None:
        """Verify that run raises CheckError when the remote structure file cannot be downloaded."""
        # Arrange
        mock_download.side_effect = ResourceError("Error downloading file")
        structure_check = StructureCheck(
            "structure", "sample_dir", "https://example.com/structure.json", is_venv_required=False
        )

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            structure_check.run()
        self.assertIn("Cannot read structure file", str(context.exception))


class TestStructureCheckFromCove(unittest.TestCase):
    """Test cases for loading the structure file of the StructureCheck class from Cove."""

    def setUp(self) -> None:
        """Set up the test environment."""
        self.cove_uri = "cove://example/structure"
        self.structure_check = StructureCheck("structure", "sample_dir", self.cove_uri, is_venv_required=False)
        return super().setUp()

    @patch("grader.utils.structure_validator.StructureValidator.is_structure_valid")
    @patch("grader.checks.structure_check.fetch_json_from_cove")
    def test_01_valid_structure_from_cove(self, mock_fetch_json: MagicMock, mock_structure_valid: MagicMock) -> None:
        """Verify that the structure file is fetched from Cove and validated."""
        # Arrange
        mock_fetch_json.return_value = {
            "source": {"name": "Source files", "required": True, "patterns": ["src/**/*.py"]},
            "main": {"name": "Main file", "required": True, "patterns": ["main.py"]},
        }
        mock_structure_valid.return_value = True
        expected = NonScoredCheckResult(self.structure_check.name, True, "Structure is valid", "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)
        mock_fetch_json.assert_called_once_with(self.cove_uri)

    @patch("grader.utils.structure_validator.StructureValidator.is_structure_valid")
    @patch("grader.checks.structure_check.fetch_json_from_cove")
    def test_02_invalid_structure_from_cove(self, mock_fetch_json: MagicMock, mock_structure_valid: MagicMock) -> None:
        """Verify that an invalid required element from a Cove structure file fails the check."""
        # Arrange
        expected_element_name = "Main file"
        mock_fetch_json.return_value = {
            "main": {"name": expected_element_name, "required": True, "patterns": ["main.py"]},
        }
        mock_structure_valid.return_value = False
        expected_info = f"Structure for '{expected_element_name}' is invalid."
        expected = NonScoredCheckResult(self.structure_check.name, False, expected_info, "")

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertEqual(result, expected)

    @patch("grader.checks.structure_check.fetch_json_from_cove")
    def test_03_cove_fetch_error_raises_check_error(self, mock_fetch_json: MagicMock) -> None:
        """Verify that an ExternalResourceError from Cove is wrapped in a CheckError."""
        # Arrange
        mock_fetch_json.side_effect = ResourceError("Cove resource not found")

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Cannot read structure file", str(context.exception))

    @patch("grader.checks.structure_check.fetch_json_from_cove")
    def test_04_invalid_structure_contents_from_cove(self, mock_fetch_json: MagicMock) -> None:
        """Verify that malformed structure contents from Cove raise a CheckError."""
        # Arrange
        mock_fetch_json.return_value = {"first": {"second": -1}}

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Invalid structure file", str(context.exception))

    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.fetch_json_from_cove")
    def test_05_cove_uri_is_not_opened_as_a_file(self, mock_fetch_json: MagicMock, mock_open: MagicMock) -> None:
        """Verify that a Cove URI is never read from the file system."""
        # Arrange
        mock_fetch_json.return_value = {}

        # Act
        self.structure_check.run()

        # Assert
        mock_open.assert_not_called()
