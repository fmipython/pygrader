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
    def test_01_required_argument(self):
        """
        Test 01: Test that the required argument is parsed correctly.
        """
        expected = ("project_root", "path/to/project")
        self.assertIn(expected, get_args().items())

    @patch("sys.argv", ["cli.py", "path/to/project", "-c", "path/to/config"])
    def test_02_optional_config_argument(self):
        """
        Test 02: Test that the optional config argument is parsed correctly.
        """
        expected = ("config", "path/to/config")
        self.assertIn(expected, get_args().items())

    @patch("sys.argv", ["cli.py", "path/to/project", "--student-id", "12345"])
    def test_03_optional_student_id_argument(self):
        """
        Test 03: Test that the optional student ID argument is parsed correctly.
        """
        expected = ("student_id", "12345")
        self.assertIn(expected, get_args().items())

    @patch("sys.argv", ["cli.py", "path/to/project", "-v"])
    def test_04_verbosity_argument(self):
        """
        Test 04: Test that the verbosity argument is parsed correctly.
        """
        expected = ("verbosity", 1)
        self.assertIn(expected, get_args().items())

    @patch("sys.argv", ["cli.py", "path/to/project", "-vv"])
    def test_05_multiple_verbosity_argument(self):
        """
        Test 05: Test that multiple verbosity arguments are parsed correctly.
        """
        expected = ("verbosity", 2)
        self.assertIn(expected, get_args().items())


if __name__ == "__main__":
    unittest.main()
