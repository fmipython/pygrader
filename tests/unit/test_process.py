"""Unit tests for the process module."""

import subprocess
from collections.abc import Callable
from unittest.mock import MagicMock, patch

from grader.utils.process import run


class TestRunProcess:
    """Test cases for the run function in the process module."""

    @patch("subprocess.run")
    def test_01_non_zero_return_code(self, mocked_subprocess: MagicMock, log_output: Callable[[], list[str]]) -> None:
        """
        Test that the run function logs the correct messages and returns the expected result.

        Tests when the subprocess returns a non-zero return code.
        """
        # Arrange
        expected_command = "dummy"
        expected_returncode = 1
        expected_stdout = "stdout"
        expected_stderr = "stderr"

        expected_subprocess_result = subprocess.CompletedProcess(
            expected_command, expected_returncode, expected_stdout, expected_stderr
        )

        expected_line = f"DEBUG:grader:Running command: {expected_command}"
        expected_line += f", from directory: {None}, with environment variables: {None}"

        mocked_subprocess.return_value = expected_subprocess_result

        # Act
        actual_subprocess_result = run([expected_command])

        is_command_name_logged = expected_line in log_output()
        is_additional_information_logged = (
            f"DEBUG:grader:Command failed: {expected_returncode} {expected_stdout} {expected_stderr}" in log_output()
        )

        # Assert
        assert expected_subprocess_result == actual_subprocess_result
        assert is_command_name_logged
        assert is_additional_information_logged
        mocked_subprocess.assert_called_once_with(
            [expected_command], check=False, capture_output=True, text=True, cwd=None, env=None
        )

    @patch("subprocess.run")
    def test_02_zero_return_code(self, mocked_subprocess: MagicMock, log_output: Callable[[], list[str]]) -> None:
        """
        Test that the run function logs the correct messages and returns the expected result.

        Tests when the subprocess returns a zero return code.
        """
        # Arrange
        expected_command = "dummy"
        expected_returncode = 0
        expected_stdout = "stdout"

        expected_subprocess_result = subprocess.CompletedProcess(expected_command, expected_returncode, expected_stdout)

        expected_line = f"DEBUG:grader:Running command: {expected_command}"
        expected_line += f", from directory: {None}, with environment variables: {None}"

        mocked_subprocess.return_value = expected_subprocess_result

        # Act
        actual_subprocess_result = run([expected_command])
        is_command_name_logged = expected_line in log_output()
        is_additional_information_logged = f"DEBUG:grader:Command succeeded: {expected_stdout}" in log_output()

        # Assert
        assert expected_subprocess_result == actual_subprocess_result
        assert is_command_name_logged
        assert is_additional_information_logged
        mocked_subprocess.assert_called_once_with(
            [expected_command], check=False, capture_output=True, text=True, cwd=None, env=None
        )
