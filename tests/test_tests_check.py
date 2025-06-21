"""
Unit tests for the TestsCheck class.
"""

import unittest
from unittest.mock import patch

from grader.checks.run_tests_check import RunTestsCheck
from grader.checks.abstract_check import CheckError, ScoredCheckResult


class TestTestsCheck(unittest.TestCase):
    """
    Test cases for the TestsCheck class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.name = "Test Check"
        self.project_root = "/path/to/project"
        self.max_points = 100
        self.is_venv_required = False
        self.tests_path = ["test_file.py"]
        self.default_test_score = 10.0
        self.test_score_mapping = {"test_1": 20.0, "test_2": 30.0}

        self.tests_check = RunTestsCheck(
            self.name,
            self.project_root,
            self.max_points,
            self.is_venv_required,
            self.tests_path,
            self.default_test_score,
            self.test_score_mapping,
        )

    @patch("grader.checks.run_tests_check.RunTestsCheck._RunTestsCheck__pytest_run")
    def test_01_all_tests_pass(self, mock_pytest_run):
        """
        Verify run calculates the correct score when all tests pass.
        """
        # Arrange
        mock_pytest_run.return_value = "PASSED test_1::test_1\nPASSED test_2::test_2"
        expected_score = ScoredCheckResult(self.name, 50.0, self.max_points)

        # Act
        score = self.tests_check.run()

        # Assert
        self.assertEqual(score, expected_score)

    @patch("grader.checks.run_tests_check.RunTestsCheck._RunTestsCheck__pytest_run")
    def test_02_some_tests_fail(self, mock_pytest_run):
        """
        Verify run calculates the correct score when some tests fail.
        """
        # Arrange
        mock_pytest_run.return_value = "PASSED test_1::test_1\nFAILED test_2::test_2"
        expected_score = ScoredCheckResult(self.name, 20.0, self.max_points)

        # Act
        score = self.tests_check.run()

        # Assert
        self.assertEqual(score, expected_score)

    @patch("grader.checks.run_tests_check.RunTestsCheck._RunTestsCheck__pytest_run")
    def test_03_score_exceeds_max_points(self, mock_pytest_run):
        """
        Verify run raises CheckError when total score exceeds max_points.
        """
        # Arrange
        test_score_mapping = {"test_1": 20.0, "test_2": 30.0, "test_3": 60.0}

        max_score_exceeded_check = RunTestsCheck(
            self.name,
            self.project_root,
            self.max_points,
            self.is_venv_required,
            self.tests_path,
            self.default_test_score,
            test_score_mapping,
        )

        mock_pytest_run.return_value = "PASSED test_1::test_1\nPASSED test_2::test_2\nPASSED test_3::test_3"

        # Act & Assert
        with self.assertRaises(CheckError):
            max_score_exceeded_check.run()

    @patch("grader.checks.run_tests_check.RunTestsCheck._RunTestsCheck__pytest_run")
    def test_04_logs_correct_passed_and_failed_counts(self, mock_pytest_run):
        """
        Verify run logs the correct number of passed and failed tests.
        """
        # Arrange
        mock_pytest_run.return_value = "PASSED test_1::test_1\nFAILED test_2::test_2"

        # Act
        with self.assertLogs("grader", level="INFO") as log:
            self.tests_check.run()

        # Assert
        self.assertIn("INFO:grader:Passed tests: 1/2", log.output)
        self.assertIn("INFO:grader:Failed tests: 1/2", log.output)

    @patch("grader.checks.run_tests_check.RunTestsCheck._RunTestsCheck__pytest_run")
    def test_05_empty_test_results(self, mock_pytest_run):
        """
        Verify run handles empty test results gracefully.
        """
        # Arrange
        mock_pytest_run.return_value = ""
        expected_score = ScoredCheckResult(self.name, 0.0, self.max_points)

        # Act
        score = self.tests_check.run()

        # Assert
        self.assertEqual(score, expected_score)

    @patch("grader.checks.run_tests_check.RunTestsCheck._RunTestsCheck__pytest_run")
    def test_06_invalid_pytest_output(self, mock_pytest_run):
        """
        Verify run handles invalid pytest output gracefully.
        """
        # Arrange
        mock_pytest_run.return_value = "INVALID OUTPUT"
        expected_score = ScoredCheckResult(self.name, 0.0, self.max_points)

        # Act
        score = self.tests_check.run()

        # Assert
        self.assertEqual(score, expected_score)

    @patch("grader.utils.process.run")
    def test_07_pytest_raises_os_error(self, mock_run):
        """
        Verify run raises CheckError when pytest raises OSError.
        """
        # Arrange
        mock_run.side_effect = OSError("Test error")

        # Act & Assert
        with self.assertRaises(CheckError):
            self.tests_check.run()

    @patch("grader.utils.process.run")
    def test_08_pytest_raises_value_error(self, mock_run):
        """
        Verify run raises CheckError when pytest raises ValueError.
        """
        # Arrange
        mock_run.side_effect = ValueError("Test error")

        # Act & Assert
        with self.assertRaises(CheckError):
            self.tests_check.run()

    @patch("grader.utils.process.run")
    def test_09_pytest_returncode_greater_than_2(self, mock_run):
        """
        Verify run raises CheckError when pytest returncode is greater than 2.
        """
        # Arrange
        mock_run.return_value.returncode = 3

        # Act & Assert
        with self.assertRaises(CheckError):
            self.tests_check.run()
