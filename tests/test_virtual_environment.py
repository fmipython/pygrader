import os
import shutil
import subprocess
import unittest
from unittest.mock import MagicMock, patch

import grader.utils.constants as const
from grader.utils.process import run
from grader.utils.virtual_environment import VirtualEnvironment, VirtualEnvironmentError


# TODO - These tests take some time to run, also aren't exactly unit tests. Consider refactoring
class TestsVirtualEnvironment(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        self.__sample_root_dir_path = "sample_root_dir"
        self.__sample_package_name = "pylint"
        self.__sample_package_version = "3.3.3"
        super().__init__(methodName)

    def setUp(self):
        os.makedirs(self.__sample_root_dir_path, exist_ok=True)

        return super().setUp()

    def tearDown(self):
        if os.path.exists(self.__sample_root_dir_path):
            shutil.rmtree(self.__sample_root_dir_path)

        return super().tearDown()

    def test_01_existing_venv(self):
        """
        Verify that the VirtualEnvironment class cleans pre-existing virtual enviroments
        """
        # Arrange
        possible_paths = [
            os.path.join(self.__sample_root_dir_path, venv_path) for venv_path in const.POSSIBLE_VENV_DIRS
        ]

        for path in possible_paths:
            os.makedirs(path, exist_ok=True)

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            do_directories_exist = (os.path.exists(venv_path) for venv_path in possible_paths)

        # Assert
        self.assertTrue(not any(do_directories_exist))

    def test_02_non_existing_requirements(self):
        """
        Verify that the VirtualEnvironment class reports when it can't find a requirements.txt file
        """
        # Arrange
        expected_message = "No requirements.txt file found in the project directory"
        # Act

        with self.assertLogs("grader", level="ERROR") as log:
            with VirtualEnvironment(self.__sample_root_dir_path):
                is_message_in_log = any(expected_message in output for output in log.output)

        # Assert
        self.assertTrue(is_message_in_log)

    def test_03_successful_venv_creation(self):
        """
        Verify that the VirtualEnvironment class can successfully create a virtualenv
        """
        # Arrange
        unix_path_to_python = os.path.join(self.__sample_root_dir_path, const.VENV_NAME, "bin", const.PYTHON_BIN_UNIX)
        windows_path_to_python = os.path.join(
            self.__sample_root_dir_path, const.VENV_NAME, "Scripts", const.PYTHON_BIN_WINDOWS
        )

        path_to_python = windows_path_to_python if os.name == "nt" else unix_path_to_python

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            does_python_exist = os.path.exists(path_to_python)

        # Assert
        self.assertTrue(does_python_exist)

    @patch("subprocess.run")
    def test_04_failed_venv_creation(self, patched_run: MagicMock):
        """
        Verify that the VirtualEnvironment class raises an exception when it can't create a virtualenv
        """

        patched_run.return_value = subprocess.CompletedProcess([], 1)

        # Act & Assert
        with self.assertRaises(VirtualEnvironmentError):
            with VirtualEnvironment(self.__sample_root_dir_path):
                pass

    def test_05_install_requirements(self):
        """
        Verify that the VirtualEnvironment class install the requirements
        """
        # Arrange
        requirements_path = os.path.join(self.__sample_root_dir_path, "requirements.txt")
        self.__create_sample_requirements(requirements_path)

        pip_full_path = os.path.join(self.__sample_root_dir_path, const.VENV_NAME, const.PIP_PATH)

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            pip_run_result = run([pip_full_path, "freeze"])

            is_expected_package_installed = self.__sample_package_name in pip_run_result.stdout
            is_version_correct = self.__sample_package_version in pip_run_result.stdout

        # Assert
        self.assertTrue(is_expected_package_installed)
        self.assertTrue(is_version_correct)

    @patch("subprocess.run")
    def test_06_fail_install_requirements(self, patched_run: MagicMock):
        """
        Verify that the VirtualEnvironment class raises an exception when it fails to install the requirements
        """

        # Arrange
        def custom_run_behavior(command: list[str], *args, **kwargs):
            if "install" in command:
                return subprocess.CompletedProcess("", 1)
            else:
                return subprocess.CompletedProcess("", 0)

        patched_run.side_effect = custom_run_behavior

        # Act & Assert
        with self.assertRaises(VirtualEnvironmentError):
            with VirtualEnvironment(self.__sample_root_dir_path):
                pass

    def test_07_install_grader_requirements(self):
        """
        Verify that the VirtualEnvironment class install the grader requirements
        """
        # Arrange
        pip_full_path = os.path.join(self.__sample_root_dir_path, const.VENV_NAME, const.PIP_PATH)

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            pip_run_result = run([pip_full_path, "freeze"])

            is_expected_package_installed = "coverage" in pip_run_result.stdout
            is_version_correct = "7.6.10" in pip_run_result.stdout

        # Assert
        self.assertTrue(is_expected_package_installed)
        self.assertTrue(is_version_correct)

    @patch("subprocess.run")
    def test_08_fail_install_grader_requirements(self, patched_run: MagicMock):
        """
        Verify that the VirtualEnvironment class raises an exception when it fails to install the requirements
        """

        # Arrange
        def custom_run_behavior(command: list[str], *args, **kwargs):
            if "install" in command:
                return subprocess.CompletedProcess("", 1)
            else:
                return subprocess.CompletedProcess("", 0)

        patched_run.side_effect = custom_run_behavior

        # Act & Assert
        with self.assertRaises(VirtualEnvironmentError):
            with VirtualEnvironment(self.__sample_root_dir_path):
                pass

    def test_09_teardown(self):
        """
        Verify that the VirtualEnvironment class removes the virtual environment when the context manager is exited
        """
        # Arrange
        venv_path = os.path.join(self.__sample_root_dir_path, const.VENV_NAME)

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            does_venv_exist_before = os.path.exists(venv_path)

        does_venv_exist_after = os.path.exists(venv_path)

        # Assert
        self.assertTrue(does_venv_exist_before)
        self.assertFalse(does_venv_exist_after)

    def __create_sample_requirements(self, requirements_path: str):
        content = f"{self.__sample_package_name}=={self.__sample_package_version}"

        with open(requirements_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(content)
