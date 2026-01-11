"""
Unit tests for the CoverageCheck class in the coverage_check module.
"""

import unittest
from typing import Optional
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock

from grader.checks.abstract_check import CheckError, ScoredCheckResult
from grader.checks.coverage_check import CoverageCheck


class TestCoverageCheck(unittest.TestCase):
    """
    Test cases for the CoverageCheck class.
    """

    def setUp(self) -> None:
        """
        Set up the CoverageCheck instance for testing.
        """
        self.coverage_check = CoverageCheck("Coverage", "sample_dir", 2, is_venv_required=False)
        # This way, we have 3 ranges: 0-33, 34-66, 67-100
        return super().setUp()

    @patch("subprocess.run")
    def test_01_coverage_run_fail(self, mocked_run: MagicMock) -> None:
        """
        Test that a failed coverage run logs an error and raises an exception.
        """
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["coverage", "run"], returncode=1)

        # Act
        with self.assertLogs("grader", level="ERROR") as log:
            with self.assertRaises(CheckError):
                self.coverage_check.run()
            is_message_logged = "ERROR:grader:Coverage run failed. stdout:" in log.output[0]

        # Assert
        self.assertTrue(is_message_logged)

    @patch("subprocess.run")
    def test_02_coverage_report_fail(self, mocked_run: MagicMock) -> None:
        """
        Test that a failed coverage report logs an error and returns a score of 0.0.
        """

        # Arrange
        def mocked_run_side_effect(*args: list, **_: dict) -> Optional[CompletedProcess]:
            if "run" in args[0]:
                return CompletedProcess(args=["coverage", "run"], returncode=0)
            if "report" in args[0]:
                return CompletedProcess(args=["coverage", "report"], returncode=1)
            return None

        mocked_run.side_effect = mocked_run_side_effect
        # Act
        with self.assertLogs("grader", level="ERROR") as log:
            with self.assertRaises(CheckError):
                self.coverage_check.run()
            is_message_logged = "ERROR:grader:Coverage report failed" in log.output

        # Assert
        self.assertTrue(is_message_logged)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_03_translate_score_zero(self, mocked_report: MagicMock, mocked_run: MagicMock) -> None:
        """
        Test that a coverage report of 0 translates to a score of 0.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 0
        expected_score = ScoredCheckResult("Coverage", 0, "Tests cover 0.00% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_04_translate_score_inside_first_range(self, mocked_report: MagicMock, mocked_run: MagicMock) -> None:
        """
        Test that a coverage report inside the first range translates to a score of 0.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 22
        expected_score = ScoredCheckResult("Coverage", 0, "Tests cover 22.00% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_05_translate_score_right_bound_first_range(self, mocked_report: MagicMock, mocked_run: MagicMock) -> None:
        """
        Test that a coverage report at the right bound of the first range translates to a score of 1.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100 / 3
        expected_score = ScoredCheckResult("Coverage", 1, "Tests cover 33.33% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_06_translate_score_left_bound_second_range(self, mocked_report: MagicMock, mocked_run: MagicMock) -> None:
        """
        Test that a coverage report at the left bound of the second range translates to a score of 1.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100 / 3 + 1
        expected_score = ScoredCheckResult("Coverage", 1, "Tests cover 34.33% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_07_translate_score_inside_bound_second_range(
        self, mocked_report: MagicMock, mocked_run: MagicMock
    ) -> None:
        """
        Test that a coverage report inside the second range translates to a score of 1.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 50
        expected_score = ScoredCheckResult("Coverage", 1, "Tests cover 50.00% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_08_translate_score_right_bound_second_range(
        self, mocked_report: MagicMock, mocked_run: MagicMock
    ) -> None:
        """
        Test that a coverage report at the right bound of the second range translates to a score of 2.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100 / 3 * 2
        expected_score = ScoredCheckResult("Coverage", 2, "Tests cover 66.67% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_09_translate_score_inside_bound_third_range(
        self, mocked_report: MagicMock, mocked_run: MagicMock
    ) -> None:
        """
        Test that a coverage report inside the third range translates to a score of 2.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 75
        expected_score = ScoredCheckResult("Coverage", 2, "Tests cover 75.00% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_10_translate_score_max(self, mocked_report: MagicMock, mocked_run: MagicMock) -> None:
        """
        Test that a coverage report of 100 translates to a score of 2.
        """
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100
        expected_score = ScoredCheckResult("Coverage", 2, "Tests cover 100.00% of the code", "", 2)

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("subprocess.run")
    def test_11_coverage_report_read_properly(self, mocked_run: MagicMock) -> None:
        """
        Test that the coverage report is read properly and returns the correct score.
        """

        # Arrange
        def mocked_run_side_effect(*args: list, **_: dict) -> Optional[CompletedProcess]:
            if "run" in args[0]:
                return CompletedProcess(args=["coverage", "run"], returncode=0)
            if "report" in args[0]:
                return CompletedProcess(args=["coverage", "report"], returncode=0, stdout="100")
            return None

        mocked_run.side_effect = mocked_run_side_effect
        # Act
        result = self.coverage_check.run()

        # Assert
        self.assertEqual(ScoredCheckResult("Coverage", 2, "Tests cover 100.00% of the code", "", 2), result)
