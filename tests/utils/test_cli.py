import unittest
from unittest.mock import patch
from grader.utils.cli import get_args

# FILE: grader/utils/test_cli.py


class TestGetArgs(unittest.TestCase):
    @patch("sys.argv", ["cli.py", "path/to/project"])
    def test_required_argument(self):
        expected = {"project_root": "path/to/project", "config": None, "student_id": None, "verbosity": 0}
        self.assertEqual(get_args(), expected)

    @patch("sys.argv", ["cli.py", "path/to/project", "-c", "path/to/config"])
    def test_optional_config_argument(self):
        expected = {"project_root": "path/to/project", "config": "path/to/config", "student_id": None, "verbosity": 0}
        self.assertEqual(get_args(), expected)

    @patch("sys.argv", ["cli.py", "path/to/project", "--student-id", "12345"])
    def test_optional_student_id_argument(self):
        expected = {"project_root": "path/to/project", "config": None, "student_id": "12345", "verbosity": 0}
        self.assertEqual(get_args(), expected)

    @patch("sys.argv", ["cli.py", "path/to/project", "-v"])
    def test_verbosity_argument(self):
        expected = {"project_root": "path/to/project", "config": None, "student_id": None, "verbosity": 1}
        self.assertEqual(get_args(), expected)

    @patch("sys.argv", ["cli.py", "path/to/project", "-vv"])
    def test_multiple_verbosity_argument(self):
        expected = {"project_root": "path/to/project", "config": None, "student_id": None, "verbosity": 2}
        self.assertEqual(get_args(), expected)


if __name__ == "__main__":
    unittest.main()
