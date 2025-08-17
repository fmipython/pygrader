"""
Unit tests for the StructureValidator class in the structure_validator module.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from grader.utils.structure_validator import StructureValidator


class TestStructureValidator(unittest.TestCase):
    """
    Test cases for the StructureValidator class.
    """

    def setUp(self) -> None:
        """
        Set up the test case environment.
        """
        self.validator = StructureValidator(name="TestStructure", required=True, patterns=["*.py", "tests/*.py"])
        self.project_root = "sample_project"
        return super().setUp()

    @patch("pathlib.Path.glob")
    def test_01_is_structure_valid_all_patterns_match(self, mocked_glob: MagicMock) -> None:
        """
        Test that is_structure_valid returns True when all patterns match files.
        """
        # Arrange
        mocked_glob.side_effect = [[MagicMock()], [MagicMock()]]

        # Act
        result = self.validator.is_structure_valid(self.project_root)

        # Assert
        self.assertTrue(result)
        mocked_glob.assert_any_call("*.py")
        mocked_glob.assert_any_call("tests/*.py")

    @patch("pathlib.Path.glob")
    def test_02_is_structure_valid_some_patterns_do_not_match(self, mocked_glob: MagicMock) -> None:
        """
        Test that is_structure_valid returns False when some patterns do not match files.
        """
        # Arrange
        mocked_glob.side_effect = [[MagicMock()], []]

        # Act
        result = self.validator.is_structure_valid(self.project_root)

        # Assert
        self.assertFalse(result)
        mocked_glob.assert_any_call("*.py")
        mocked_glob.assert_any_call("tests/*.py")

    @unittest.skipIf(os.name == "nt", "Skipping test on Windows due to path normalization.")
    @patch("pathlib.Path.glob")
    def test_03_get_matching_files(self, mocked_glob: MagicMock) -> None:
        """
        Test that get_matching_files returns the correct list of matching files.
        """
        # Arrange
        project_root_abs = os.path.abspath(self.project_root).lower()  # Normalize path for Windows
        matching_files = [
            os.path.join(project_root_abs, "file1.py"),
            os.path.join(project_root_abs, "file2.py"),
            os.path.join(project_root_abs, "tests/test_file.py"),
        ]
        mocked_glob.side_effect = [
            [Path(file) for file in matching_files[:2]],
            [Path(file) for file in matching_files[2:]],
        ]
        expected_result = matching_files

        # Act
        actual_result = self.validator.get_matching_files(self.project_root)

        # Normalize the paths in actual_result for comparison
        actual_result = [filepath.lower() for filepath in actual_result]

        # Assert
        self.assertEqual(actual_result, expected_result)
        mocked_glob.assert_any_call("*.py")
        mocked_glob.assert_any_call("tests/*.py")

    def test_04_from_dict(self) -> None:
        """
        Test that from_dict correctly creates a StructureValidator instance.
        """
        # Arrange
        raw_object = {"name": "SampleStructure", "required": False, "patterns": ["*.md", "docs/*.md"]}

        # Act
        validator = StructureValidator.from_dict(raw_object)

        # Assert
        self.assertEqual(validator.name, "SampleStructure")
        self.assertFalse(validator.required)
        self.assertEqual(validator.patterns, ["*.md", "docs/*.md"])

    def test_05_init(self) -> None:
        """
        Test that the __init__ method correctly initializes attributes.
        """
        # Arrange
        name = "SampleStructure"
        required = True
        patterns = ["*.py", "tests/*.py"]

        # Act
        validator = StructureValidator(name, required, patterns)

        # Assert
        self.assertEqual(validator.name, name)
        self.assertTrue(validator.required)
        self.assertEqual(validator.patterns, patterns)

    @patch("pathlib.Path.glob")
    def test_06_is_structure_valid_empty_patterns(self, mocked_glob: MagicMock) -> None:
        """
        Test that is_structure_valid returns True when patterns list is empty.
        """
        # Arrange
        self.validator.patterns = []

        # Act
        result = self.validator.is_structure_valid(self.project_root)

        # Assert
        self.assertTrue(result)
        mocked_glob.assert_not_called()

    @patch("pathlib.Path.glob")
    def test_07_get_matching_files_empty_patterns(self, mocked_glob: MagicMock) -> None:
        """
        Test that get_matching_files returns an empty list when patterns list is empty.
        """
        # Arrange
        self.validator.patterns = []

        # Act
        result = self.validator.get_matching_files(self.project_root)

        # Assert
        self.assertEqual(result, [])
        mocked_glob.assert_not_called()

    @patch("pathlib.Path.glob")
    def test_08_is_structure_valid_invalid_project_root(self, mocked_glob: MagicMock) -> None:
        """
        Test that is_structure_valid handles invalid project_root gracefully.
        """
        # Arrange
        mocked_glob.side_effect = FileNotFoundError

        # Act
        with self.assertRaises(FileNotFoundError):
            self.validator.is_structure_valid("invalid_path")

    @patch("pathlib.Path.glob")
    def test_09_get_matching_files_invalid_project_root(self, mocked_glob: MagicMock) -> None:
        """
        Test that get_matching_files handles invalid project_root gracefully.
        """
        # Arrange
        mocked_glob.side_effect = FileNotFoundError

        # Act
        with self.assertRaises(FileNotFoundError):
            self.validator.get_matching_files("invalid_path")
