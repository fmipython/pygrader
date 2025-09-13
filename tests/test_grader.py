"""
Unit tests for the Grader class
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from grader.grader import Grader, GraderError
from grader.checks.abstract_check import (
    CheckError,
    ScoredCheck,
    ScoredCheckResult,
    NonScoredCheck,
    NonScoredCheckResult,
)


class TestGrader(unittest.TestCase):
    @patch("grader.utils.config.load_config")
    def test_01_load_config_fails(self, mock_load_config: MagicMock) -> None:
        """
        Test that Grader exits with SystemExit when the configuration file is not found.
        """
        # Arrange
        mock_load_config.side_effect = FileNotFoundError("Config file not found")

        # Act
        with self.assertRaises(GraderError):
            Grader("student_id", "project_root", "config_path", logger=MagicMock())

    @patch("os.path.exists")
    def test_02_project_root_does_not_exist(self, mock_exists: MagicMock) -> None:
        """
        Test that Grader exits with SystemExit when the project root directory does not exist.
        """
        # Arrange
        mock_exists.return_value = False
        config_path = os.path.join("config", "full_single_point.json")

        # Act & Assert
        with self.assertRaises(GraderError):
            Grader("student_id", "nonexistent_project_root", config_path, logger=MagicMock())

    @patch("grader.grader.create_checks")
    def test_03_create_checks_is_called(self, mock_create_checks: MagicMock) -> None:
        """
        Test that create_checks is called when grade() is called.
        """
        # Arrange
        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_create_checks.return_value = ([], [])
        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act
        grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        mock_create_checks.assert_called_once()

    @patch("grader.grader.create_checks")
    def test_04_non_venv_checks_run_called(self, mock_create_checks: MagicMock) -> None:
        """
        Test that the run method of each non_venv_check is called when grade() is executed.
        """
        # Arrange
        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_check1 = MagicMock()
        mock_check2 = MagicMock()
        mock_check1.run.return_value = "result1"
        mock_check2.run.return_value = "result2"
        mock_create_checks.return_value = ([mock_check1, mock_check2], [])

        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act
        grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        mock_check1.run.assert_called_once()
        mock_check2.run.assert_called_once()

    @patch("grader.grader.create_checks")
    def test_05_non_venv_checks_results_are_returned(self, mock_create_checks: MagicMock) -> None:
        """
        Test that the results from non_venv_checks are returned by grade().
        """
        # Arrange
        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_check1 = MagicMock()
        mock_check2 = MagicMock()
        result1 = "result1"
        result2 = "result2"
        mock_check1.run.return_value = result1
        mock_check2.run.return_value = result2
        mock_create_checks.return_value = ([mock_check1, mock_check2], [])

        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act
        results = grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        self.assertEqual(results, [result1, result2])

    @patch("grader.grader.create_checks")
    def test_06_skipping_venv_creation_returns_only_non_venv_checks(self, mock_create_checks: MagicMock) -> None:
        """
        Test that when is_skipping_venv_creation is True and venv_checks is not empty,
        only non_venv_checks results are returned by grade().
        """
        # Arrange
        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_non_venv_check1 = MagicMock()
        mock_non_venv_check2 = MagicMock()
        mock_venv_check1 = MagicMock()
        mock_venv_check2 = MagicMock()
        result1 = "non_venv_result1"
        result2 = "non_venv_result2"
        mock_non_venv_check1.run.return_value = result1
        mock_non_venv_check2.run.return_value = result2
        mock_venv_check1.run.return_value = "venv_result1"
        mock_venv_check2.run.return_value = "venv_result2"
        mock_create_checks.return_value = (
            [mock_non_venv_check1, mock_non_venv_check2],
            [mock_venv_check1, mock_venv_check2],
        )

        grader = Grader(
            "student_id", sample_project_path, sample_config_path, logger=MagicMock(), is_skipping_venv_creation=True
        )

        # Act
        results = grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        self.assertEqual(results, [result1, result2])

    @patch("grader.grader.VirtualEnvironment")
    @patch("grader.grader.create_checks")
    def test_07_venv_checks_run_called_in_context_manager(
        self, mock_create_checks: MagicMock, mock_virtualenv: MagicMock
    ) -> None:
        """
        Test that the run method of each venv_check is called inside the VirtualEnvironment context manager.
        """
        # Arrange
        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_non_venv_check = MagicMock()
        mock_venv_check1 = MagicMock()
        mock_venv_check2 = MagicMock()
        mock_non_venv_check.run.return_value = "non_venv_result"
        mock_venv_check1.run.return_value = "venv_result1"
        mock_venv_check2.run.return_value = "venv_result2"
        mock_create_checks.return_value = ([mock_non_venv_check], [mock_venv_check1, mock_venv_check2])

        mock_context_manager = MagicMock()
        mock_virtualenv.return_value.__enter__.return_value = mock_context_manager
        mock_virtualenv.return_value.__exit__.return_value = None

        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act
        grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        mock_venv_check1.run.assert_called_once()
        mock_venv_check2.run.assert_called_once()
        mock_virtualenv.assert_called_once_with(sample_project_path, False)

    @patch("grader.grader.VirtualEnvironment")
    @patch("grader.grader.create_checks")
    def test_08_venv_checks_results_are_returned(
        self, mock_create_checks: MagicMock, mock_virtualenv: MagicMock
    ) -> None:
        """
        Test that the results from venv_checks are returned by grade().
        """
        # Arrange
        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_non_venv_check = MagicMock()
        mock_venv_check1 = MagicMock()
        mock_venv_check2 = MagicMock()
        non_venv_result = "non_venv_result"
        venv_result1 = "venv_result1"
        venv_result2 = "venv_result2"
        mock_non_venv_check.run.return_value = non_venv_result
        mock_venv_check1.run.return_value = venv_result1
        mock_venv_check2.run.return_value = venv_result2
        mock_create_checks.return_value = ([mock_non_venv_check], [mock_venv_check1, mock_venv_check2])

        mock_context_manager = MagicMock()
        mock_virtualenv.return_value.__enter__.return_value = mock_context_manager
        mock_virtualenv.return_value.__exit__.return_value = None

        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act
        results = grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        self.assertEqual(results, [non_venv_result, venv_result1, venv_result2])

    @patch("grader.grader.create_checks")
    def test_09_scored_checkerror_returns_scored_result(self, mock_create_checks: MagicMock) -> None:
        """
        Test that if a ScoredCheck raises CheckError, grade returns a ScoredCheckResult with score 0.
        """
        # Arrange

        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_scored_check = MagicMock(spec=ScoredCheck)
        mock_scored_check.name = "scored_check"
        mock_scored_check.max_points = 10
        mock_scored_check.run.side_effect = CheckError("fail")
        mock_create_checks.return_value = ([mock_scored_check], [])

        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act
        results = grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], ScoredCheckResult)
        self.assertEqual(results[0].name, "scored_check")
        self.assertEqual(results[0].result, 0)
        self.assertEqual(results[0].max_score, 10)

    @patch("grader.grader.create_checks")
    def test_10_nonscored_checkerror_returns_nonscored_result(self, mock_create_checks: MagicMock) -> None:
        """
        Test that if a NonScoredCheck raises CheckError, grade returns a NonScoredCheckResult with result=False.
        """

        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        mock_nonscored_check = MagicMock(spec=NonScoredCheck)
        mock_nonscored_check.name = "nonscored_check"
        mock_nonscored_check.run.side_effect = CheckError("fail")
        mock_create_checks.return_value = ([mock_nonscored_check], [])

        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act
        results = grader.grade()

        os.rmdir(sample_project_path)

        # Assert
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], NonScoredCheckResult)
        self.assertEqual(results[0].name, "nonscored_check")
        self.assertFalse(results[0].result)

    @patch("grader.grader.create_checks")
    def test_11_unknown_checkerror_raises_typeerror(self, mock_create_checks: MagicMock) -> None:
        """
        Test that if a check is neither ScoredCheck nor NonScoredCheck and raises CheckError, grade raises TypeError.
        """
        from grader.checks.abstract_check import CheckError

        sample_config_path = os.path.join("config", "full_single_point.json")
        sample_project_path = os.path.join("/tmp", "project_root")
        os.makedirs(sample_project_path, exist_ok=True)

        class UnknownCheck:
            def run(self):
                raise CheckError("fail")

        mock_unknown_check = UnknownCheck()
        mock_create_checks.return_value = ([mock_unknown_check], [])

        grader = Grader("student_id", sample_project_path, sample_config_path, logger=MagicMock())

        # Act & Assert
        with self.assertRaises(TypeError):
            grader.grade()

        os.rmdir(sample_project_path)
