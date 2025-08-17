"""
Unit tests for the RequirementsCheck class in the requirements_check module.
"""

import unittest
from unittest.mock import patch, MagicMock

from grader.checks.requirements_check import RequirementsCheck
from grader.checks.abstract_check import ScoredCheckResult


class TestRequirementsCheck(unittest.TestCase):
    """
    Unit tests for the RequirementsCheck class.
    """

    def setUp(self) -> None:
        """
        Set up the test case environment.
        """
        self.requirements_check = RequirementsCheck("requirements", "sample_dir", 1, is_venv_required=False)
        return super().setUp()

    @patch("os.path.exists")
    def test_01_requirements_exist(self, mocked_exists: MagicMock) -> None:
        """
        Test that the requirements file exists.
        """
        # Arrange
        mocked_exists.return_value = True
        expected_score = ScoredCheckResult(self.requirements_check.name, 1, self.requirements_check.max_points)

        # Act
        actual_score = self.requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("os.path.exists")
    def test_02_requirements_does_not_exist(self, mocked_exists: MagicMock) -> None:
        """
        Test that the requirements file does not exist.
        """
        # Arrange
        mocked_exists.return_value = False
        expected_score = ScoredCheckResult(self.requirements_check.name, 0, self.requirements_check.max_points)

        # Act
        actual_score = self.requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
