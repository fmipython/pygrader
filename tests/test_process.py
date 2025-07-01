"""
Unit tests for the process module.
"""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from grader.utils.process import run


class TestRunProcess(unittest.TestCase):
    """
    Test cases for the run function in the process module.
    """

    @patch("subprocess.run")
    def test_01_non_zero_return_code(self, mocked_subprocess: MagicMock):
        """
        Test that the run function logs the correct messages and returns the expected result
        when the subprocess returns a non-zero return code.
        """
        # Arrange
        expected_command = "dummy"
        expected_returncode = 1
        expected_stdout = "stdout"
        expected_stderr = "stderr"

        expected_subprocess_result = subprocess.CompletedProcess(
            expected_command, expected_returncode, expected_stdout, expected_stderr
        )

        mocked_subprocess.return_value = expected_subprocess_result

        # Act
        with self.assertLogs("grader", level="DEBUG") as log:
            actual_subprocess_result = run([expected_command])

            is_command_name_logged = (
                f"DEBUG:grader:Running command: {[expected_command]}, from directory: {None}" in log.output
            )
            is_additional_information_logged = (
                f"DEBUG:grader:Command failed: {expected_returncode} {expected_stdout} {expected_stderr}" in log.output
            )

        # Assert
        self.assertEqual(expected_subprocess_result, actual_subprocess_result)
        self.assertTrue(is_command_name_logged)
        self.assertTrue(is_additional_information_logged)
        mocked_subprocess.assert_called_once_with(
            [expected_command], check=False, capture_output=True, text=True, cwd=None, env=None
        )

    @patch("subprocess.run")
    def test_02_zero_return_code(self, mocked_subprocess: MagicMock):
        """
        Test that the run function logs the correct messages and returns the expected result
        when the subprocess returns a zero return code.
        """
        # Arrange
        expected_command = "dummy"
        expected_returncode = 0
        expected_stdout = "stdout"

        expected_subprocess_result = subprocess.CompletedProcess(
            expected_command, expected_returncode, expected_stdout
        )

        mocked_subprocess.return_value = expected_subprocess_result

        # Act
        with self.assertLogs("grader", level="DEBUG") as log:
            actual_subprocess_result = run([expected_command])

            is_command_name_logged = (
                f"DEBUG:grader:Running command: {[expected_command]}, from directory: {None}" in log.output
            )
            is_additional_information_logged = f"DEBUG:grader:Command succeeded: {expected_stdout}" in log.output

        # Assert
        self.assertEqual(expected_subprocess_result, actual_subprocess_result)
        self.assertTrue(is_command_name_logged)
        self.assertTrue(is_additional_information_logged)
        mocked_subprocess.assert_called_once_with(
            [expected_command], check=False, capture_output=True, text=True, cwd=None, env=None
        )
