"""
Unit tests for the CLI module in the cli.py module.
"""

import unittest
from unittest.mock import patch
from grader.utils.cli import get_args

# FILE: grader/utils/test_cli.py


class TestGetArgs(unittest.TestCase):
    """
    Unit tests for the get_args function.
    """

    @patch("sys.argv", ["cli.py", "path/to/project"])
    def test_required_argument(self):
        """
        Test that the required argument is parsed correctly.
        """
        expected = {
            "project_root": "path/to/project",
            "config": None,
            "student_id": None,
            "keep_venv": False,
            "verbosity": 0,
            "skip_venv_creation": False,
            "output": None,
        }
        self.assertTrue(get_args().items() <= expected.items())

    @patch("sys.argv", ["cli.py", "path/to/project", "-c", "path/to/config"])
    def test_optional_config_argument(self):
        """
        Test that the optional config argument is parsed correctly.
        """
        expected = {
            "project_root": "path/to/project",
            "config": "path/to/config",
            "student_id": None,
            "keep_venv": False,
            "verbosity": 0,
            "skip_venv_creation": False,
            "output": None,
        }
        self.assertTrue(get_args().items() <= expected.items())

    @patch("sys.argv", ["cli.py", "path/to/project", "--student-id", "12345"])
    def test_optional_student_id_argument(self):
        """
        Test that the optional student ID argument is parsed correctly.
        """
        expected = {
            "project_root": "path/to/project",
            "config": None,
            "keep_venv": False,
            "student_id": "12345",
            "verbosity": 0,
            "skip_venv_creation": False,
            "output": None,
        }
        self.assertTrue(get_args().items() <= expected.items())

    @patch("sys.argv", ["cli.py", "path/to/project", "-v"])
    def test_verbosity_argument(self):
        """
        Test that the verbosity argument is parsed correctly.
        """
        expected = {
            "project_root": "path/to/project",
            "config": None,
            "student_id": None,
            "keep_venv": False,
            "verbosity": 1,
            "skip_venv_creation": False,
            "output": None,
        }
        self.assertTrue(get_args().items() <= expected.items())

    @patch("sys.argv", ["cli.py", "path/to/project", "-vv"])
    def test_multiple_verbosity_argument(self):
        """
        Test that multiple verbosity arguments are parsed correctly.
        """
        expected = {
            "project_root": "path/to/project",
            "config": None,
            "student_id": None,
            "keep_venv": False,
            "verbosity": 2,
            "skip_venv_creation": False,
            "output": None,
        }
        self.assertTrue(get_args().items() <= expected.items())


if __name__ == "__main__":
    unittest.main()
