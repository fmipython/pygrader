import unittest

from grader.checks.abstract_check import AbstractCheck


class TestAbstractCheck(unittest.TestCase):
    def test_01_run_without_venv_when_required(self):
        # Arrange
        class DummyCheck(AbstractCheck):
            def run(self) -> float:
                super().run()

                return 0

        check = DummyCheck("dummy", 1, "dummy", is_venv_requred=True)

        # Act & Assert
        with self.assertRaises(RuntimeError):
            check.run()
