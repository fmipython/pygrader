import unittest
from grader.checks.checks_factory import create_checks, InvalidCheckError
from grader.utils.config import InvalidConfigError


class TestChecksFactory(unittest.TestCase):
    def test_01_no_checks_in_config(self):
        # Arrange
        config = {}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_02_invalid_check_configuration(self):
        # Arrange
        config = {"checks": [{}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_03_max_points_missing(self):
        # Arrange
        config = {"checks": [{"name": "coverage"}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_04_name_missing(self):
        # Arrange
        config = {"checks": [{"max_points": 10}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidConfigError):
            create_checks(config, project_root)

    def test_05_unknown_check_name(self):
        # Arrange
        config = {"checks": [{"name": "unknown", "max_points": 10}]}
        project_root = "test_project"

        # Act
        with self.assertRaises(InvalidCheckError):
            create_checks(config, project_root)

    def test_06_is_venv_present(self):
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10, "requires_venv": True}]}
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 0)
        self.assertEqual(len(venv_checks), 1)

    def test_07_is_venv_not_present(self):
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10}]}
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root)

        # Assert
        self.assertEqual(len(non_venv_checks), 1)
        self.assertEqual(len(venv_checks), 0)
