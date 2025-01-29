import unittest
from unittest.mock import patch, MagicMock

import grader.utils.constants as const
from grader.checks.pylint_check import PylintCheck


class TestPylintCheck(unittest.TestCase):
    def setUp(self):
        self.pylint_check = PylintCheck("pylint", 2, "sample_dir")
        # This way, we have 3 ranges: 0-33, 34-66, 67-100
        return super().setUp()

    @patch("pylint.lint.Run")
    @patch("grader.utils.files.find_all_python_files")
    def test_01_pylint_called(self, mocked_find_python_files: MagicMock, mocked_pylint: MagicMock):
        # Arrange
        mocked_find_python_files.return_value = ["file1.py", "file2.py"]
        mocked_pylint.return_value.linter.stats.global_note = 10

        # Act
        self.pylint_check.run()
        called_with = mocked_pylint.call_args

        # Assert
        mocked_pylint.assert_called_once()
        # called_with[0] is *args. First arg is the list of "args" of lint.Run
        self.assertIn("file1.py", called_with[0][0])
        self.assertIn("file2.py", called_with[0][0])

    @patch("pylint.lint.Run")
    @patch("os.path.exists")
    def test_02_pylintrc_file_exists(self, mocked_os_path_exists: MagicMock, mocked_pylint: MagicMock):
        # Arrange
        mocked_os_path_exists.return_value = True
        mocked_pylint.return_value.linter.stats.global_note = 10

        # Act
        self.pylint_check.run()
        called_with = mocked_pylint.call_args

        # Assert
        mocked_pylint.assert_called_once()

        # called_with[0] is *args. First arg is the list of "args" of lint.Run
        self.assertIn("--rcfile", called_with[0][0])
        self.assertIn(const.PYLINTRC, called_with[0][0])

    @patch("pylint.lint.Run")
    @patch("os.path.exists")
    def test_03_pylintrc_file_does_not_exist(self, mocked_os_path_exists: MagicMock, mocked_pylint: MagicMock):
        # Arrange
        mocked_os_path_exists.return_value = False
        mocked_pylint.return_value.linter.stats.global_note = 10

        # Act
        self.pylint_check.run()
        called_with = mocked_pylint.call_args

        # Assert
        mocked_pylint.assert_called_once()

        # called_with[0] is *args. First arg is the list of "args" of lint.Run
        self.assertNotIn("--rcfile", called_with[0][0])
        self.assertNotIn(const.PYLINTRC, called_with[0][0])

    @patch("pylint.lint.Run")
    def test_04_translate_score_zero(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 0
        expected_score = 0

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pylint.lint.Run")
    def test_05_translate_score_inside_first_range(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 2.2
        expected_score = 0

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pylint.lint.Run")
    def test_06_translate_score_right_bound_first_range(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 10 / 3
        expected_score = 1

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pylint.lint.Run")
    def test_07_translate_score_left_bound_second_range(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 10 / 3 + 0.1
        expected_score = 1

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pylint.lint.Run")
    def test_08_translate_score_inside_bound_second_range(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 5
        expected_score = 1

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pylint.lint.Run")
    def test_09_translate_score_right_bound_second_range(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 10 / 3 * 2
        expected_score = 2

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pylint.lint.Run")
    def test_10_translate_score_inside_bound_third_range(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 7.5
        expected_score = 2

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pylint.lint.Run")
    def test_11_translate_score_max(self, mocked_pylint: MagicMock):
        # Arrange
        mocked_pylint.return_value.linter.stats.global_note = 10
        expected_score = 2

        # Act
        actual_score = self.pylint_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
