import unittest
from unittest.mock import patch, MagicMock

from grader.checks.requirements_check import RequirementsCheck


class TestRequirementsCheck(unittest.TestCase):
    def setUp(self):
        self.coverage_check = RequirementsCheck("requirements", 1, "sample_dir")

        return super().setUp()

    @patch("os.path.exists")
    def test_01_requirements_exist(self, mocked_exists: MagicMock):
        # Arrange
        mocked_exists.return_value = True
        expected_score = 1

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("os.path.exists")
    def test_02_requirements_does_not_exist(self, mocked_exists: MagicMock):
        # Arrange
        mocked_exists.return_value = False
        expected_score = 0

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
