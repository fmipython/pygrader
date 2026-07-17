"""Module for functional tests related to the wheel package"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from grader.utils.process import run


class TestWheel(unittest.TestCase):
    """Class for testing wheel package functionality"""

    temp_dir: TemporaryDirectory

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_01_wheel_build(self):
        """Test the wheel building process"""

        try:
            wheel_path = build_wheel(self.temp_dir.name)
        except RuntimeError as e:
            self.fail(f"Wheel build failed with error: {e}")

        self.assertTrue(wheel_path.exists(), "Wheel file was not created")


def build_wheel(build_dir: str) -> Path:
    """Function to build a wheel package for testing purposes"""
    # Implementation of wheel building logic goes here
    build_command = ["uv", "build", "--wheel", "--out-dir", build_dir]

    build_result = run(build_command)

    build_path = Path(build_dir)

    if build_result.returncode != 0:
        raise RuntimeError(f"Wheel build failed: {build_result.stderr}")

    wheel_path = next(path for path in build_path.glob("*.whl"))

    return wheel_path
