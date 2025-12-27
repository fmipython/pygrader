"""
Unit tests for the checks_factory module in the grader package.
"""

import unittest

from unittest.mock import patch, MagicMock
from grader.checks.checks_factory import create_checks, InvalidCheckError
from grader.utils.config import InvalidConfigError


class TestChecksFactory(unittest.TestCase):
    """
    Unit tests for the create_checks function in the checks_factory module.
    """

    def test_01_no_checks_in_config(self) -> None:
        """
        Test that an empty config raises an InvalidConfigError.
        """
        # Arrange
        config: dict[str, str] = {}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_02_invalid_check_configuration(self) -> None:
        """
        Test that an invalid check configuration raises an InvalidConfigError.
        """
        # Arrange
        config: dict[str, list[dict[str, str]]] = {"checks": [{}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_03_max_points_missing(self) -> None:
        """
        Test that a missing max_points field raises an InvalidConfigError.
        """
        # Arrange
        config = {"checks": [{"name": "coverage"}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_04_name_missing(self) -> None:
        """
        Test that a missing name field raises an InvalidConfigError.
        """
        # Arrange
        config = {"checks": [{"max_points": 10}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_05_unknown_check_name(self) -> None:
        """
        Test that an unknown check name raises an InvalidCheckError.
        """
        # Arrange
        config = {"checks": [{"name": "unknown", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidCheckError):
            create_checks(config, project_root)

    def test_06_venv_required(self) -> None:
        """
        Test that checks requiring a virtual environment are separated correctly.
        """
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": True}]}
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 0)
        self.assertEqual(len(venv_checks), 1)

    def test_07_venv_not_required(self) -> None:
        """
        Test that checks not requiring a virtual environment are separated correctly.
        """
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 1)
        self.assertEqual(len(venv_checks), 0)

    def test_08_is_venv_required_not_present(self) -> None:
        """
        Test that when is_venv_required is not present, an InvalidConfigError is raised.
        """
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            _ = create_checks(config, project_root)

    def test_09_environment_variables_global_only(self) -> None:
        """
        Test that global environment variables are passed to checks.
        """
        # Arrange
        config = {
            "environment": {"variables": {"GLOBAL_VAR": "global_value"}},
            "checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}],
        }
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 1)
        check = non_venv_checks[0]
        self.assertIsNotNone(check.env_vars)

        # To keep the linter happy
        if check.env_vars is not None:
            self.assertIn("GLOBAL_VAR", check.env_vars)
            self.assertEqual(check.env_vars["GLOBAL_VAR"], "global_value")

    def test_10_environment_variables_check_specific(self) -> None:
        """
        Test that check-specific environment variables are passed to checks.
        """
        # Arrange
        config = {
            "checks": [
                {
                    "name": "coverage",
                    "max_points": 10,
                    "is_venv_required": False,
                    "environment": {"variables": {"CHECK_VAR": "check_value"}},
                }
            ]
        }
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 1)
        check = non_venv_checks[0]
        self.assertIsNotNone(check.env_vars)

        # To keep the linter happy
        if check.env_vars is not None:
            self.assertIn("CHECK_VAR", check.env_vars)
            self.assertEqual(check.env_vars["CHECK_VAR"], "check_value")

    def test_11_environment_variables_merge_priority(self) -> None:
        """
        Test that check-specific environment variables override global ones.
        """
        # Arrange
        config = {
            "environment": {"variables": {"API_KEY": "global_key", "GLOBAL_VAR": "global_value"}},
            "checks": [
                {
                    "name": "coverage",
                    "max_points": 10,
                    "is_venv_required": False,
                    "environment": {"variables": {"API_KEY": "check_key", "CHECK_VAR": "check_value"}},
                }
            ],
        }
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 1)
        check = non_venv_checks[0]
        self.assertIsNotNone(check.env_vars)

        # To keep the linter happy
        if check.env_vars is not None:
            # Check that check-specific API_KEY overrides global
            self.assertEqual(check.env_vars["API_KEY"], "check_key")
            # Check that global variable is still present
            self.assertEqual(check.env_vars["GLOBAL_VAR"], "global_value")
            # Check that check-specific variable is present
            self.assertEqual(check.env_vars["CHECK_VAR"], "check_value")

    @patch("os.environ")
    def test_12_environment_variables_none_when_not_defined(self, existing_env: MagicMock) -> None:
        """
        Test that env_vars is None when no environment variables are defined.
        """
        # Arrange
        existing_env.return_value = {}
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 1)
        check = non_venv_checks[0]
        self.assertEqual(check.env_vars, {})
