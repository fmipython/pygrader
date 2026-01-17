"""
Unit tests for the main module.
"""

import unittest

from unittest.mock import MagicMock, patch

from desktop.main import build_reporter, run_grader
from desktop.results_reporter import JSONResultsReporter, CSVResultsReporter, PlainTextResultsReporter


class TestBuildReporter(unittest.TestCase):
    """
    Tests for the build_reporter function.
    """

    def test_01_build_json_reporter(self) -> None:
        """
        Test if the function returns a JSONResultsReporter when "json" is passed.
        """
        # Arrange
        reporter_format = "json"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, JSONResultsReporter)

    def test_02_build_csv_reporter(self) -> None:
        """
        Test if the function returns a CSVResultsReporter when "csv" is passed.
        """
        # Arrange
        reporter_format = "csv"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, CSVResultsReporter)

    def test_03_build_plaintext_reporter(self) -> None:
        """
        Test if the function returns a PlainTextResultsReporter when "text" is passed.
        """
        # Arrange
        reporter_format = "text"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, PlainTextResultsReporter)

    def test_04_build_default_reporter(self) -> None:
        """
        Test if the function returns a PlainTextResultsReporter when an unknown format is passed.
        """
        # Arrange
        reporter_format = "unknown_format"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, PlainTextResultsReporter)


class TestRunGrader(unittest.TestCase):
    """
    Tests for the run_grader function.
    """

    @patch("desktop.main.get_args")
    def test_01_get_args_called(self, mock_get_args: MagicMock) -> None:
        """
        Test if get_args is called when run_grader is executed.
        """
        # Arrange
        mock_get_args.return_value = {
            "student_id": "test_student",
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": "text",
            "verbosity": 1,
            "suppress_info": False,
            "keep_venv": False,
            "skip_venv_creation": False,
        }
        # Act
        with patch("desktop.main.Grader"), patch("desktop.main.setup_logger"):
            run_grader()

        # Assert
        mock_get_args.assert_called_once()

    @patch("desktop.main.get_args")
    @patch("desktop.main.setup_logger")
    def test_02_is_suppressing_info_json(self, mock_setup_logger: MagicMock, mock_get_args: MagicMock) -> None:
        """
        Test if is_suppressing_info is set to a proper value when report info is JSON
        """
        # Arrange
        mock_get_args.return_value = {
            "student_id": "test_student",
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": "json",
            "verbosity": 1,
            "suppress_info": False,
            "keep_venv": False,
            "skip_venv_creation": False,
        }

        expected_suppress_info = True
        # Act
        with patch("desktop.main.Grader"):
            run_grader()

        actual_suppress_info = mock_setup_logger.call_args_list[0].kwargs["suppress_info"]

        # Assert
        self.assertEqual(actual_suppress_info, expected_suppress_info)

    @patch("desktop.main.get_args")
    @patch("desktop.main.setup_logger")
    def test_03_is_suppressing_info_csv(self, mock_setup_logger: MagicMock, mock_get_args: MagicMock) -> None:
        """
        Test if is_suppressing_info is set to a proper value when report info is JSON
        """
        # Arrange
        mock_get_args.return_value = {
            "student_id": "test_student",
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": "csv",
            "verbosity": 1,
            "suppress_info": False,
            "keep_venv": False,
            "skip_venv_creation": False,
        }

        expected_suppress_info = True
        # Act
        with patch("desktop.main.Grader"):
            run_grader()

        actual_suppress_info = mock_setup_logger.call_args_list[0].kwargs["suppress_info"]

        # Assert
        self.assertEqual(actual_suppress_info, expected_suppress_info)

    @patch("desktop.main.get_args")
    @patch("desktop.main.setup_logger")
    def test_04_is_suppressing_info_passed_true(self, mock_setup_logger: MagicMock, mock_get_args: MagicMock) -> None:
        """
        Test if is_suppressing_info is set to a proper value when report info is JSON
        """
        # Arrange
        mock_get_args.return_value = {
            "student_id": "test_student",
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": "text",
            "verbosity": 1,
            "suppress_info": True,
            "keep_venv": False,
            "skip_venv_creation": False,
        }

        expected_suppress_info = True
        # Act
        with patch("desktop.main.Grader"):
            run_grader()

        actual_suppress_info = mock_setup_logger.call_args_list[0].kwargs["suppress_info"]

        # Assert
        self.assertEqual(actual_suppress_info, expected_suppress_info)

    @patch("desktop.main.get_args")
    @patch("desktop.main.setup_logger")
    def test_04_is_suppressing_info_not_passed(self, mock_setup_logger: MagicMock, mock_get_args: MagicMock) -> None:
        """
        Test if is_suppressing_info is set to a proper value when report info is JSON
        """
        # Arrange
        mock_get_args.return_value = {
            "student_id": "test_student",
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": "text",
            "verbosity": 1,
            "suppress_info": False,
            "keep_venv": False,
            "skip_venv_creation": False,
        }

        expected_suppress_info = False
        # Act
        with patch("desktop.main.Grader"):
            run_grader()

        actual_suppress_info = mock_setup_logger.call_args_list[0].kwargs["suppress_info"]

        # Assert
        self.assertEqual(actual_suppress_info, expected_suppress_info)

    @patch("desktop.main.get_args")
    @patch("desktop.main.setup_logger")
    def test_05_setup_logger_called(self, mock_setup_logger: MagicMock, mock_get_args: MagicMock) -> None:
        """
        Test if is_suppressing_info is set to a proper value when report info is JSON
        """
        # Arrange
        expected_student_id = "test_student"
        expected_verbosity = 2
        expected_suppress_info = True

        mock_get_args.return_value = {
            "student_id": expected_student_id,
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": "text",
            "verbosity": expected_verbosity,
            "suppress_info": expected_suppress_info,
            "keep_venv": False,
            "skip_venv_creation": False,
        }

        # Act
        with patch("desktop.main.Grader"):
            run_grader()

        # Assert
        mock_setup_logger.assert_called_once_with(
            expected_student_id, verbosity=expected_verbosity, suppress_info=expected_suppress_info
        )

    @patch("desktop.main.get_args")
    @patch("desktop.main.Grader")
    @patch("desktop.main.setup_logger")
    def test_06_grader_instantiated(
        self, mock_logger: MagicMock, mock_grader: MagicMock, mock_get_args: MagicMock
    ) -> None:
        """
        Test if is_suppressing_info is set to a proper value when report info is JSON
        """
        # Arrange
        expected_student_id = "test_student"
        expected_project_root = "/path/to/project"
        expected_config_path = "/path/to/config"
        expected_keep_venv = False
        expected_skip_venv_creation = False

        mock_get_args.return_value = {
            "student_id": expected_student_id,
            "project_root": expected_project_root,
            "config": expected_config_path,
            "report_format": "text",
            "verbosity": 1,
            "suppress_info": False,
            "keep_venv": expected_keep_venv,
            "skip_venv_creation": expected_skip_venv_creation,
        }

        # Act
        run_grader()

        # Assert
        mock_grader.assert_called_once_with(
            expected_student_id,
            expected_project_root,
            expected_config_path,
            mock_logger.return_value,
            expected_keep_venv,
            expected_skip_venv_creation,
        )

    @patch("desktop.main.get_args")
    @patch("desktop.main.build_reporter")
    def test_07_build_reporter_called(self, mock_build_reporter: MagicMock, mock_get_args: MagicMock) -> None:
        """
        Test if get_args is called when run_grader is executed.
        """
        # Arrange
        expected_report_format = "text"
        mock_get_args.return_value = {
            "student_id": "test_student",
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": expected_report_format,
            "verbosity": 1,
            "suppress_info": False,
            "keep_venv": False,
            "skip_venv_creation": False,
        }
        # Act
        with patch("desktop.main.Grader"), patch("desktop.main.setup_logger"):
            run_grader()

        # Assert
        mock_build_reporter.assert_called_once_with(expected_report_format)

    @patch("desktop.main.get_args")
    @patch("desktop.main.build_reporter")
    @patch("desktop.main.Grader")
    @patch("desktop.main.ResultsReporter")
    def test_08_results_reporter_called(
        self,
        mock_results_reporter: MagicMock,
        mock_grader: MagicMock,
        mock_build_reporter: MagicMock,
        mock_get_args: MagicMock,
    ) -> None:
        """
        Test if get_args is called when run_grader is executed.
        """
        # Arrange
        expected_report_format = "text"
        mock_get_args.return_value = {
            "student_id": "test_student",
            "project_root": "/path/to/project",
            "config": "/path/to/config",
            "report_format": expected_report_format,
            "verbosity": 1,
            "suppress_info": False,
            "keep_venv": False,
            "skip_venv_creation": False,
        }
        mock_build_reporter.return_value = mock_results_reporter

        mocked_results = MagicMock()
        mock_grader.grade.return_value = mocked_results

        # Act
        with patch("desktop.main.setup_logger"):
            run_grader()

        # Assert
        mock_results_reporter.display.assert_called_once()
