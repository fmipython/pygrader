"""
Unit tests for the StructureCheck class in the structure_check module.
"""

import unittest
from unittest.mock import patch, MagicMock

from yaml import YAMLError

from grader.checks.abstract_check import CheckError
from grader.checks.structure_check import StructureCheck


class TestStructureCheck(unittest.TestCase):
    """
    Test cases for the StructureCheck class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.structure_check = StructureCheck("structure", "sample_dir", "structure.yaml", is_venv_required=False)
        return super().setUp()

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_01_valid_structure(self, mock_load_structure_file):
        """
        Verify that the run method returns True when all structure elements are valid.
        """
        # Arrange
        mock_element = MagicMock()
        mock_element.is_structure_valid.return_value = True
        mock_element.required = True
        mock_load_structure_file.return_value = [mock_element]

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_02_invalid_required_structure(self, mock_load_structure_file):
        """
        Verify that the run method returns False when a required structure element is invalid.
        """
        # Arrange
        mock_element = MagicMock()
        mock_element.is_structure_valid.return_value = False
        mock_element.required = True
        mock_load_structure_file.return_value = [mock_element]

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertFalse(result)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_03_invalid_non_required_structure(self, mock_load_structure_file):
        """
        Verify that the run method returns True when a non-required structure element is invalid.
        """
        # Arrange
        mock_element = MagicMock()
        mock_element.is_structure_valid.return_value = False
        mock_element.required = False
        mock_load_structure_file.return_value = [mock_element]

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_04_empty_structure_file(self, mock_load_structure_file):
        """
        Verify that the run method returns True when the structure file is empty.
        """
        # Arrange
        mock_load_structure_file.return_value = []

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_05_logs_structure_validity(self, mock_load_structure_file):
        """
        Verify that the run method logs the validity of each structure element.
        """
        # Arrange
        mock_element = MagicMock()
        mock_element.is_structure_valid.return_value = True
        mock_element.required = True
        mock_element.name = "test_element"
        mock_load_structure_file.return_value = [mock_element]

        with self.assertLogs("grader", level="DEBUG") as log:
            # Act
            self.structure_check.run()

        # Assert
        self.assertIn("Is test_element structure valid ?", log.output[0])

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_06_raises_check_error_on_invalid_structure_file(self, mock_load_structure_file):
        """
        Verify that the run method raises a CheckError when the structure file is invalid.
        """
        # Arrange
        mock_load_structure_file.side_effect = CheckError("Invalid structure file")

        # Act & Assert
        with self.assertRaises(CheckError):
            self.structure_check.run()

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_07_multiple_valid_elements(self, mock_load_structure_file):
        """
        Verify that the run method returns True when all structure elements are valid.
        """
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.is_structure_valid.return_value = True
        mock_element1.required = True

        mock_element2 = MagicMock()
        mock_element2.is_structure_valid.return_value = True
        mock_element2.required = False

        mock_load_structure_file.return_value = [mock_element1, mock_element2]

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_08_multiple_elements_with_invalid_required(self, mock_load_structure_file):
        """
        Verify that the run method returns False when one required structure element is invalid.
        """
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.is_structure_valid.return_value = True
        mock_element1.required = True

        mock_element2 = MagicMock()
        mock_element2.is_structure_valid.return_value = False
        mock_element2.required = True

        mock_load_structure_file.return_value = [mock_element1, mock_element2]

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertFalse(result)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_09_multiple_elements_with_invalid_non_required(self, mock_load_structure_file):
        """
        Verify that the run method returns True when only non-required structure elements are invalid.
        """
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.is_structure_valid.return_value = True
        mock_element1.required = True

        mock_element2 = MagicMock()
        mock_element2.is_structure_valid.return_value = False
        mock_element2.required = False

        mock_load_structure_file.return_value = [mock_element1, mock_element2]

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.StructureCheck._StructureCheck__load_structure_file")
    def test_10_all_invalid_elements(self, mock_load_structure_file):
        """
        Verify that the run method returns False when all structure elements are invalid and at least one is required.
        """
        # Arrange
        mock_element1 = MagicMock()
        mock_element1.is_structure_valid.return_value = False
        mock_element1.required = True

        mock_element2 = MagicMock()
        mock_element2.is_structure_valid.return_value = False
        mock_element2.required = False

        mock_load_structure_file.return_value = [mock_element1, mock_element2]

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertFalse(result)

    @patch("grader.utils.structure_validator.StructureValidator.is_structure_valid")
    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.yaml.safe_load")
    def test_11_load_structure_file_valid(self, mock_safe_load, mock_open, mock_structure_valid):
        """
        Verify that run correctly processes a valid structure file.
        """
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

    @patch("grader.checks.structure_check.yaml.safe_load")
    @patch("grader.checks.structure_check.open", create=True)
    def test_12_load_structure_file_invalid(self, mock_open, mock_safe_load):
        """
        Verify that run raises CheckError for an invalid structure file.
        """
        # Arrange
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_safe_load.return_value = {"first": {"second": -1}}

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Invalid structure file", str(context.exception))

    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.yaml.safe_load")
    def test_13_load_structure_file_empty(self, mock_safe_load, mock_open):
        """
        Verify that run returns True for an empty structure file.
        """
        # Arrange
        mock_safe_load.return_value = {}
        mock_open.return_value.__enter__.return_value = MagicMock()

        # Act
        result = self.structure_check.run()

        # Assert
        self.assertTrue(result)

    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.yaml.safe_load")
    def test_14_load_structure_file_yaml_error(self, mock_safe_load, mock_open):
        """
        Verify that run raises CheckError for a YAMLError.
        """
        # Arrange

        mock_safe_load.side_effect = YAMLError("YAML parsing error")
        mock_open.return_value.__enter__.return_value = MagicMock()

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Invalid structure file", str(context.exception))

    @patch("grader.checks.structure_check.open", create=True)
    @patch("grader.checks.structure_check.yaml.safe_load")
    def test_15_load_structure_file_not_found(self, mock_safe_load, mock_open):
        """
        Verify that run raises CheckError for a FileNotFoundError.
        """
        # Arrange
        mock_open.side_effect = FileNotFoundError("File not found")
        mock_safe_load.return_value = {}

        # Act & Assert
        with self.assertRaises(CheckError) as context:
            self.structure_check.run()
        self.assertIn("Cannot read structure file", str(context.exception))
