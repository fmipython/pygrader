"""
Unit tests for the PylintCheck class.
"""

from subprocess import CompletedProcess
import unittest
from unittest.mock import patch, MagicMock

import grader.utils.constants as const
from grader.checks.pylint_check import PylintCheck


class TestPylintCheck(unittest.TestCase):
    """
    Test cases for the PylintCheck class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.pylint_check = PylintCheck("pylint", 2, "sample_dir")
        # This way, we have 3 ranges: 0-33, 34-66, 67-100
        return super().setUp()

    @patch("grader.utils.process.run")
    @patch("grader.utils.files.find_all_files_under_directory")
    def test_01_pylint_called(self, mocked_find_python_files: MagicMock, mocked_pylint: MagicMock):
        """
        Test if pylint is called with the correct arguments.

        :param mocked_find_python_files: Mocked find_all_files_under_directory function.
        :type mocked_find_python_files: MagicMock
        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_find_python_files.return_value = ["file1.py", "file2.py"]
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(10))

        # Act
        self.pylint_check.run()
        called_with = mocked_pylint.call_args

        # Assert
        mocked_pylint.assert_called_once()
        mocked_find_python_files.assert_called_once()
        # called_with[0] is *args. First arg is the list of "args" of lint.Run
        self.assertIn("file1.py", called_with[0][0])
        self.assertIn("file2.py", called_with[0][0])

    @patch("grader.utils.process.run")
    @patch("os.path.exists")
    def test_02_pylintrc_file_exists(self, mocked_os_path_exists: MagicMock, mocked_pylint: MagicMock):
        """
        Test if pylint is called with the --rcfile argument when the pylintrc file exists.

        :param mocked_os_path_exists: Mocked os.path.exists function.
        :type mocked_os_path_exists: MagicMock
        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_os_path_exists.return_value = True
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(10))

        # Act
        self.pylint_check.run()
        called_with = mocked_pylint.call_args

        # Assert
        mocked_pylint.assert_called_once()

        # called_with[0] is *args. First arg is the list of "args" of lint.Run
        self.assertIn("--rcfile", called_with[0][0])
        self.assertIn(const.PYLINTRC, called_with[0][0])

    @patch("grader.utils.process.run")
    @patch("os.path.exists")
    def test_03_pylintrc_file_does_not_exist(self, mocked_os_path_exists: MagicMock, mocked_pylint: MagicMock):
        """
        Test if pylint is called without the --rcfile argument when the pylintrc file does not exist.

        :param mocked_os_path_exists: Mocked os.path.exists function.
        :type mocked_os_path_exists: MagicMock
        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_os_path_exists.return_value = False
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(10))

        # Act
        self.pylint_check.run()
        called_with = mocked_pylint.call_args

        # Assert
        mocked_pylint.assert_called_once()

        # called_with[0] is *args. First arg is the list of "args" of lint.Run
        self.assertNotIn("--rcfile", called_with[0][0])
        self.assertNotIn(const.PYLINTRC, called_with[0][0])

    @patch("grader.utils.process.run")
    def test_04_translate_score_zero(self, mocked_pylint: MagicMock):
        """
        Test if a score of 0 is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(0))
        expected_score = 0

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_05_translate_score_inside_first_range(self, mocked_pylint: MagicMock):
        """
        Test if a score inside the first range is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(2.2))
        expected_score = 0

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_06_translate_score_right_bound_first_range(self, mocked_pylint: MagicMock):
        """
        Test if a score at the right bound of the first range is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(10 / 3))
        expected_score = 1

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_07_translate_score_left_bound_second_range(self, mocked_pylint: MagicMock):
        """
        Test if a score at the left bound of the second range is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(10 / 3 + 0.1))
        expected_score = 1

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_08_translate_score_inside_bound_second_range(self, mocked_pylint: MagicMock):
        """
        Test if a score inside the second range is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(5))
        expected_score = 1

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_09_translate_score_right_bound_second_range(self, mocked_pylint: MagicMock):
        """
        Test if a score at the right bound of the second range is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(10 / 3 * 2))
        expected_score = 2

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_10_translate_score_inside_bound_third_range(self, mocked_pylint: MagicMock):
        """
        Test if a score inside the third range is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(7.5))
        expected_score = 2

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.utils.process.run")
    def test_11_translate_score_max(self, mocked_pylint: MagicMock):
        """
        Test if a maximum score is translated correctly.

        :param mocked_pylint: Mocked grader.utils.process.run function.
        :type mocked_pylint: MagicMock
        """
        # Arrange
        mocked_pylint.return_value = CompletedProcess("pylint", 0, self.__create_sample_pylint_output(10))
        expected_score = 2

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @staticmethod
    def __create_sample_pylint_output(score: float) -> str:
        """
        Create a sample pylint output with the given score.

        :param score: The score to be included in the output.
        :type score: float
        :return: The sample pylint output.
        :rtype: str
        """
        content = [
            "************* Module main",
            "/tmp/temp_project/main.py:1:0: C0114: Missing module docstring (missing-module-docstring)",
            "/tmp/temp_project/main.py:2:0: E0401: Unable to import 'numpy' (import-error)",
            '/tmp/temp_project/main.py:2:0: C0413: Import "import numpy as np" should be placed at the top of the module (wrong-import-position)',
            "",
            "------------------------------------------------------------------",
            "Your code has been rated at {score:.2f}/10 (previous run: 1.25/10, +0.00)]",
        ]
        return "\n".join(content).format(score=score)
