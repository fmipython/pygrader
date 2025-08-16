"""
Unit tests for the AbstractCheck class in the abstract_check module.
"""

import unittest

from grader.checks.abstract_check import AbstractCheck, CheckError, CheckResult


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

            def run(self) -> CheckResult[int]:
                """
                Run the dummy check.
                """
                super()._pre_run()
                return CheckResult("dummy", 0)

        check = DummyCheck("dummy", "dummy", is_venv_required=True)

        # Act & Assert
        with self.assertRaises(CheckError):
            check.run()
