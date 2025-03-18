import unittest
from grader.checks.checks_factory import create_checks, InvalidCheckError
from grader.utils.config import InvalidConfigError


class TestChecksFactory(unittest.TestCase):
    """
    Unit tests for the create_checks function in the checks_factory module.
    """

    def test_01_no_checks_in_config(self):
        """
        Test that an empty config raises an InvalidConfigError.
        """
        # Arrange
        config = {}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_02_invalid_check_configuration(self):
        """
        Test that an invalid check configuration raises an InvalidConfigError.
        """
        # Arrange
        config = {"checks": [{}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_03_max_points_missing(self):
        """
        Test that a missing max_points field raises an InvalidConfigError.
        """
        # Arrange
        config = {"checks": [{"name": "coverage"}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_04_name_missing(self):
        """
        Test that a missing name field raises an InvalidConfigError.
        """
        # Arrange
        config = {"checks": [{"max_points": 10}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_05_unknown_check_name(self):
        """
        Test that an unknown check name raises an InvalidCheckError.
        """
        # Arrange
        config = {"checks": [{"name": "unknown", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidCheckError):
            create_checks(config, project_root)

    def test_06_venv_required(self):
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

    def test_07_venv_not_required(self):
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

    def test_08_is_venv_required_not_present(self):
        """
        Test that when is_venv_required is not present, an InvalidConfigError is raised.
        """
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            _ = create_checks(config, project_root)
