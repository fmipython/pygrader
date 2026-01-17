"""
Unit tests for the RequirementsCheck class in the requirements_check module.
"""

import unittest
from unittest.mock import patch, MagicMock

from grader.checks.requirements_check import RequirementsCheck
from grader.checks.abstract_check import ScoredCheckResult
from grader.utils.virtual_environment import VirtualEnvironmentError


class TestRequirementsCheck(unittest.TestCase):
    """
    Unit tests for the RequirementsCheck class.
    """

    def setUp(self) -> None:
        """
        Set up the test case environment.
        """
        self.requirements_check = RequirementsCheck("requirements", "sample_dir", 1, is_venv_required=False)
        return super().setUp()

    @patch("pathlib.Path.exists")
    def test_01_requirements_exist(self, mocked_exists: MagicMock) -> None:
        """
        Test that the requirements file exists.
        """
        # Arrange
        mocked_exists.return_value = True
        expected_score = ScoredCheckResult(self.requirements_check.name, 1, "", "", self.requirements_check.max_points)

        # Act
        actual_score = self.requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("pathlib.Path.exists")
    def test_02_requirements_does_not_exist(self, mocked_exists: MagicMock) -> None:
        """
        Test that the requirements file does not exist.
        """
        # Arrange
        mocked_exists.return_value = False
        expected_score = ScoredCheckResult(
            self.requirements_check.name,
            0,
            "requirements.txt or pyproject.toml not found",
            "",
            self.requirements_check.max_points,
        )

        # Act
        actual_score = self.requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.requirements_check.VirtualEnvironment")
    @patch("pathlib.Path.exists")
    def test_03_is_checking_install_with_successful_venv_setup(
        self, mocked_exists: MagicMock, mocked_venv_class: MagicMock
    ) -> None:
        """
        Test that when is_checking_install=True and requirements exist,
        a virtual environment is created, set up, and torn down successfully.
        """
        # Arrange
        mocked_exists.return_value = True
        mocked_venv_instance = MagicMock()
        mocked_venv_instance.__enter__ = MagicMock(return_value=mocked_venv_instance)
        mocked_venv_instance.__exit__ = MagicMock(return_value=False)
        mocked_venv_class.return_value = mocked_venv_instance

        requirements_check = RequirementsCheck(
            "requirements", "sample_dir", 1, is_venv_required=False, is_checking_install=True
        )
        expected_score = ScoredCheckResult(requirements_check.name, 1, "", "", requirements_check.max_points)

        # Act
        actual_score = requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
        mocked_venv_class.assert_called_once_with("sample_dir", is_keeping_existing_venv=True)
        mocked_venv_instance.__enter__.assert_called_once()
        mocked_venv_instance.__exit__.assert_called_once()

    @patch("grader.checks.requirements_check.VirtualEnvironment")
    @patch("pathlib.Path.exists")
    def test_04_is_checking_install_with_failed_venv_setup(
        self, mocked_exists: MagicMock, mocked_venv_class: MagicMock
    ) -> None:
        """
        Test that when is_checking_install=True and venv setup fails,
        the check returns 0 score with the error message.
        """
        # Arrange
        mocked_exists.return_value = True
        error_message = "Failed to install dependencies"
        mocked_venv_instance = MagicMock()
        mocked_venv_instance.__enter__ = MagicMock(side_effect=VirtualEnvironmentError(error_message))
        mocked_venv_instance.__exit__ = MagicMock(return_value=False)
        mocked_venv_class.return_value = mocked_venv_instance

        requirements_check = RequirementsCheck(
            "requirements", "sample_dir", 1, is_venv_required=False, is_checking_install=True
        )
        expected_score = ScoredCheckResult(
            requirements_check.name, 0, "", error_message, requirements_check.max_points
        )

        # Act
        actual_score = requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
        mocked_venv_class.assert_called_once_with("sample_dir", is_keeping_existing_venv=True)
        mocked_venv_instance.__enter__.assert_called_once()
        mocked_venv_instance.__exit__.assert_not_called()

    @patch("grader.checks.requirements_check.VirtualEnvironment")
    @patch("pathlib.Path.exists")
    def test_05_is_checking_install_false_does_not_create_venv(
        self, mocked_exists: MagicMock, mocked_venv_class: MagicMock
    ) -> None:
        """
        Test that when is_checking_install=False, no virtual environment is created
        even if requirements file exists.
        """
        # Arrange
        mocked_exists.return_value = True

        requirements_check = RequirementsCheck(
            "requirements", "sample_dir", 1, is_venv_required=False, is_checking_install=False
        )
        expected_score = ScoredCheckResult(requirements_check.name, 1, "", "", requirements_check.max_points)

        # Act
        actual_score = requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
        mocked_venv_class.assert_not_called()

    @patch("grader.checks.requirements_check.VirtualEnvironment")
    @patch("pathlib.Path.exists")
    def test_06_is_checking_install_true_but_no_requirements_file(
        self, mocked_exists: MagicMock, mocked_venv_class: MagicMock
    ) -> None:
        """
        Test that when is_checking_install=True but no requirements file exists,
        no virtual environment is created.
        """
        # Arrange
        mocked_exists.return_value = False

        requirements_check = RequirementsCheck(
            "requirements", "sample_dir", 1, is_venv_required=False, is_checking_install=True
        )
        expected_score = ScoredCheckResult(
            requirements_check.name,
            0,
            "requirements.txt or pyproject.toml not found",
            "",
            requirements_check.max_points,
        )

        # Act
        actual_score = requirements_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)
        mocked_venv_class.assert_not_called()
