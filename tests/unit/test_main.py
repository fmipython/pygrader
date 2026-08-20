"""Unit tests for the main module."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

from desktop.main import build_reporter, expand_project_root, resolve_project_root, run_grader
from grader.utils.results_reporter import CSVResultsReporter, JSONResultsReporter, PlainTextResultsReporter


class TestBuildReporter(unittest.TestCase):
    """Tests for the build_reporter function."""

    def test_01_build_json_reporter(self) -> None:
        """Test if the function returns a JSONResultsReporter when "json" is passed."""
        # Arrange
        reporter_format = "json"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, JSONResultsReporter)

    def test_02_build_csv_reporter(self) -> None:
        """Test if the function returns a CSVResultsReporter when "csv" is passed."""
        # Arrange
        reporter_format = "csv"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, CSVResultsReporter)

    def test_03_build_plaintext_reporter(self) -> None:
        """Test if the function returns a PlainTextResultsReporter when "text" is passed."""
        # Arrange
        reporter_format = "text"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, PlainTextResultsReporter)

    def test_04_build_default_reporter(self) -> None:
        """Test if the function returns a PlainTextResultsReporter when an unknown format is passed."""
        # Arrange
        reporter_format = "unknown_format"

        # Act
        reporter = build_reporter(reporter_format)

        # Assert
        self.assertIsInstance(reporter, PlainTextResultsReporter)


class TestRunGrader(unittest.TestCase):
    """Tests for the run_grader function."""

    @patch("desktop.main.get_args")
    def test_01_get_args_called(self, mock_get_args: MagicMock) -> None:
        """Test if get_args is called when run_grader is executed."""
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
        """Test if is_suppressing_info is set to a proper value when report info is JSON."""
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
        """Test if is_suppressing_info is set to a proper value when report info is JSON."""
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
        """Test if is_suppressing_info is set to a proper value when report info is JSON."""
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
        """Test if is_suppressing_info is set to a proper value when report info is JSON."""
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
        """Test if is_suppressing_info is set to a proper value when report info is JSON."""
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
        """Test if is_suppressing_info is set to a proper value when report info is JSON."""
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
            mock_logger.return_value,
            is_keeping_venv=expected_keep_venv,
            is_skipping_venv_creation=expected_skip_venv_creation,
            config_path=expected_config_path,
        )
        mock_grader.return_value.grade.assert_called_once_with(expected_project_root, expected_student_id)

    @patch("desktop.main.get_args")
    @patch("desktop.main.build_reporter")
    def test_07_build_reporter_called(self, mock_build_reporter: MagicMock, mock_get_args: MagicMock) -> None:
        """Test if get_args is called when run_grader is executed."""
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
        """Test if get_args is called when run_grader is executed."""
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

    @patch("desktop.main.get_args")
    @patch("desktop.main.Grader")
    @patch("desktop.main.setup_logger")
    def test_09_glob_project_root_grades_each_match(
        self, _mock_logger: MagicMock, mock_grader: MagicMock, mock_get_args: MagicMock
    ) -> None:
        """Test that a glob project_root grades every matched directory, using its name as the run id."""
        # Arrange
        with tempfile.TemporaryDirectory() as batch_dir:
            student_a = os.path.join(batch_dir, "student_a")
            student_b = os.path.join(batch_dir, "student_b")
            os.makedirs(student_a)
            os.makedirs(student_b)

            mock_get_args.return_value = {
                "student_id": "test_student",
                "project_root": os.path.join(batch_dir, "*"),
                "config": "/path/to/config",
                "report_format": "text",
                "verbosity": 1,
                "suppress_info": False,
                "keep_venv": False,
                "skip_venv_creation": False,
            }

            # Act
            run_grader()

            # Assert
            self.assertEqual(
                mock_grader.return_value.grade.call_args_list,
                [call(student_a, "student_a"), call(student_b, "student_b")],
            )


class TestExpandProjectRoot(unittest.TestCase):
    """Tests for the expand_project_root function."""

    def test_01_literal_path_returned_unchanged(self) -> None:
        """Verify a plain path with no glob metacharacters is never passed to glob.glob."""
        self.assertEqual(expand_project_root("some/literal/path"), ["some/literal/path"])

    def test_02_glob_returns_sorted_matches(self) -> None:
        """Verify a wildcard pattern expands to every match, sorted."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            student_a = os.path.join(tmp_dir, "student_a")
            student_b = os.path.join(tmp_dir, "student_b")
            os.makedirs(student_b)
            os.makedirs(student_a)

            result = expand_project_root(os.path.join(tmp_dir, "*"))

            self.assertEqual(result, [student_a, student_b])

    def test_03_glob_with_no_matches_falls_back_to_pattern(self) -> None:
        """Verify a wildcard pattern that matches nothing falls back to the raw pattern."""
        pattern = "/nonexistent/pygrader_test_dir/*"

        self.assertEqual(expand_project_root(pattern), [pattern])

    def test_04_literal_path_with_brackets_not_treated_as_character_class(self) -> None:
        """Verify a literal path containing '[' is returned as-is instead of matched as a glob."""
        pattern = "projects/[final]"

        self.assertEqual(expand_project_root(pattern), [pattern])


class TestResolveProjectRoot(unittest.TestCase):
    """Tests for the resolve_project_root function."""

    def test_01_non_zip_path_returned_unchanged(self) -> None:
        """Verify a plain directory path is returned unchanged, without touching the filesystem."""
        self.assertEqual(resolve_project_root("some/project/dir"), "some/project/dir")

    @patch("desktop.main.unzip_archive")
    @patch("desktop.main.is_path_zip", return_value=True)
    def test_02_zip_with_single_subfolder_is_flattened(self, _mock_is_zip: MagicMock, mock_unzip: MagicMock) -> None:
        """Verify that a single top-level subfolder in the extracted archive becomes the project root."""
        with tempfile.TemporaryDirectory() as extracted_dir:
            project_dir = os.path.join(extracted_dir, "project")
            os.makedirs(project_dir)
            mock_unzip.return_value = extracted_dir

            result = resolve_project_root("archive.zip")

            self.assertEqual(result, project_dir)

    @patch("desktop.main.unzip_archive")
    @patch("desktop.main.is_path_zip", return_value=True)
    def test_03_zip_with_multiple_subfolders_is_not_flattened(
        self, _mock_is_zip: MagicMock, mock_unzip: MagicMock
    ) -> None:
        """Verify that multiple top-level subfolders leave the extraction root untouched."""
        with tempfile.TemporaryDirectory() as extracted_dir:
            os.makedirs(os.path.join(extracted_dir, "src"))
            os.makedirs(os.path.join(extracted_dir, "tests"))
            mock_unzip.return_value = extracted_dir

            result = resolve_project_root("archive.zip")

            self.assertEqual(result, extracted_dir)
