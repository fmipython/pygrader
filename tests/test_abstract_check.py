"""
Unit tests for the AbstractCheck class in the abstract_check module.
"""

import unittest

from grader.checks.abstract_check import AbstractCheck, CheckError


class TestAbstractCheck(unittest.TestCase):
    """
    Test cases for the AbstractCheck class.
    """

    def test_01_run_without_venv_when_required(self):
        """
        Test that running the check without a virtual environment when it is required raises a RuntimeError.
        """

        # Arrange
        class DummyCheck(AbstractCheck):
            """
            Dummy check class for testing
            """

            def run(self) -> float:
                """
                Run the dummy check.
                """
                super().run()
                return 0

        check = DummyCheck("dummy", "dummy", is_venv_requred=True)

        # Act & Assert
        with self.assertRaises(CheckError):
            check.run()
