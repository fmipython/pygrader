import os
import shutil
import unittest
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock

import grader.utils.constants as const
from grader.checks.type_hints_check import TypeHintsCheck


class TestTypeHintsCheck(unittest.TestCase):
    def setUp(self):
        self.type_hints_check = TypeHintsCheck("type_hints", 2, "sample_dir")
        # This way, we have 3 ranges: 0-33, 34-66, 67-100
        return super().setUp()

    @patch("grader.utils.process.run")
    @patch("grader.utils.files.find_all_source_files")
    def test_01_mypy_called(self, mocked_find_python_files: MagicMock, mocked_run: MagicMock):
        """
        Test if mypy is called with the correct arguments
        """
        # Arrange
        mocked_find_python_files.return_value = ["file1.py", "file2.py"]
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)

        # Copy mypy_sample_linecount.txt to the reports directory
        os.makedirs(const.REPORTS_TEMP_DIR, exist_ok=True)
        shutil.copy(os.path.join("tests", "mypy_sample_linecount.txt"), const.MYPY_LINE_COUNT_REPORT)

        # Act
        self.type_hints_check.run()
        called_with = mocked_run.call_args

        # Assert
        mocked_find_python_files.assert_called_once()
        mocked_run.assert_called_once()
        # called_with[0] is *args. First arg is the list of "args" of lint.Run
        self.assertIn("file1.py", called_with[0][0])
        self.assertIn("file2.py", called_with[0][0])

    @patch("grader.utils.process.run")
    def test_03_mypy_report_missing(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)

        if os.path.exists(const.MYPY_LINE_COUNT_REPORT):
            os.remove(const.MYPY_LINE_COUNT_REPORT)

        # Act
        with self.assertLogs(level="ERROR") as cm:
            result = self.type_hints_check.run()
            is_error_logged = any("Mypy linecount report not found" in log for log in cm.output)

        # Assert
        self.assertEqual(result, 0.0)
        self.assertTrue(is_error_logged)

    @patch("grader.utils.process.run")
    def test_04_translate_score_zero(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 0 100 0")

        expected_score = 0

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_05_translate_score_inside_first_range(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 20 100 0")

        expected_score = 0

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_06_translate_score_right_bound_first_range(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 1 3 0")

        expected_score = 1

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_07_translate_score_left_bound_second_range(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 11 30 0")

        expected_score = 1

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_08_translate_score_inside_bound_second_range(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 15 30 0")

        expected_score = 1

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_09_translate_score_right_bound_second_range(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 22 33 0")

        expected_score = 2

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_10_translate_score_inside_bound_third_range(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 35 40 0")

        expected_score = 2

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_11_translate_score_max(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("1290 1805 107 107 total")

        expected_score = 2

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_12_translate_score_all_zeros(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["mypy"], returncode=0)
        with open(const.MYPY_LINE_COUNT_REPORT, "w", encoding="utf-8") as report_file:
            report_file.write("0 0 0 0 0")

        expected_score = 0

        # Act
        actual_score = self.type_hints_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
