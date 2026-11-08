"""Unit tests for the VirtualEnvironment class."""

import os
import shutil
import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

import pytest

import grader.utils.constants as const
from grader.exceptions import VirtualEnvironmentError
from grader.utils.process import run
from grader.utils.virtual_environment import VirtualEnvironment


# TODO - These tests take some time to run, also aren't exactly unit tests. Consider refactoring
class TestsVirtualEnvironment:
    """Test cases for the VirtualEnvironment class."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        self.__sample_root_dir_path = "sample_root_dir"
        self.__sample_package_name = "pylint"
        self.__sample_package_version = "4.0.8"
        Path(self.__sample_root_dir_path).mkdir(parents=True, exist_ok=True)

    def teardown_method(self) -> None:
        """Tear down the test environment."""
        if Path(self.__sample_root_dir_path).exists():
            shutil.rmtree(self.__sample_root_dir_path)

    def test_01_existing_venv(self) -> None:
        """Verify that the VirtualEnvironment class cleans pre-existing virtual environments."""
        # Arrange
        possible_paths = [str(Path(self.__sample_root_dir_path, venv_path)) for venv_path in const.POSSIBLE_VENV_DIRS]

        for path in possible_paths:
            Path(path).mkdir(parents=True, exist_ok=True)

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            do_directories_exist = (Path(venv_path).exists() for venv_path in possible_paths)

        # Assert
        assert not any(do_directories_exist)

    def test_03_successful_venv_creation(self) -> None:
        """Verify that the VirtualEnvironment class can successfully create a virtual environment."""
        # Arrange
        unix_path_to_python = str(Path(self.__sample_root_dir_path, const.VENV_NAME, "bin", const.PYTHON_BIN_UNIX))
        windows_path_to_python = str(
            Path(self.__sample_root_dir_path, const.VENV_NAME, "Scripts", const.PYTHON_BIN_WINDOWS)
        )

        path_to_python = windows_path_to_python if os.name == "nt" else unix_path_to_python

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            does_python_exist = Path(path_to_python).exists()

        # Assert
        assert does_python_exist

    @patch("subprocess.run")
    def test_04_failed_venv_creation(self, patched_run: MagicMock) -> None:
        """
        Verify that the VirtualEnvironment class raises an exception when it can't create a virtual environment.

        :param patched_run: Mocked subprocess.run function.
        :type patched_run: MagicMock
        """
        patched_run.return_value = subprocess.CompletedProcess([], 1)

        # Act & Assert
        with pytest.raises(VirtualEnvironmentError), VirtualEnvironment(self.__sample_root_dir_path):
            pass

    def test_05_install_requirements(self) -> None:
        """Verify that the VirtualEnvironment class installs the requirements."""
        # Arrange
        requirements_path = str(Path(self.__sample_root_dir_path, "requirements.txt"))
        self.__create_sample_requirements(requirements_path)

        pip_full_path = str(Path(self.__sample_root_dir_path, const.VENV_NAME, const.PIP_PATH))

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            pip_run_result = run([pip_full_path, "freeze"])

            is_expected_package_installed = self.__sample_package_name in pip_run_result.stdout
            print(self.__sample_package_name)
            print(self.__sample_package_version)
            print(pip_run_result.stdout)
            is_version_correct = self.__sample_package_version in pip_run_result.stdout

        # Assert
        assert is_expected_package_installed
        assert is_version_correct

    @patch("subprocess.run")
    def test_06_fail_install_requirements(self, patched_run: MagicMock) -> None:
        """
        Verify that the VirtualEnvironment class raises an exception when it fails to install the requirements.

        :param patched_run: Mocked subprocess.run function.
        :type patched_run: MagicMock
        """

        # Arrange
        def custom_run_behavior(command: list[str], *args: list, **kwargs: dict) -> CompletedProcess:  # noqa: ARG001
            if "install" in command:
                return CompletedProcess("", 1)
            return CompletedProcess("", 0)

        patched_run.side_effect = custom_run_behavior

        # Act & Assert
        with pytest.raises(VirtualEnvironmentError), VirtualEnvironment(self.__sample_root_dir_path):
            pass

    def test_07_install_grader_requirements(self) -> None:
        """Verify that the VirtualEnvironment class installs the grader requirements."""
        # Arrange
        pip_full_path = str(Path(self.__sample_root_dir_path, const.VENV_NAME, const.PIP_PATH))

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            pip_run_result = run([pip_full_path, "freeze"])

            is_expected_package_installed = "coverage" in pip_run_result.stdout
            is_version_correct = "7.16.0" in pip_run_result.stdout

        # Assert
        assert is_expected_package_installed
        assert is_version_correct

    @patch("subprocess.run")
    def test_08_fail_install_grader_requirements(self, patched_run: MagicMock) -> None:
        """
        Verify that the VirtualEnvironment class raises an exception when it fails to install the grader requirements.

        :param patched_run: Mocked subprocess.run function.
        :type patched_run: MagicMock
        """

        # Arrange
        def custom_run_behavior(command: list[str], *args: list, **kwargs: dict) -> CompletedProcess:  # noqa: ARG001
            if "install" in command:
                return CompletedProcess("", 1)
            return CompletedProcess("", 0)

        patched_run.side_effect = custom_run_behavior

        # Act & Assert
        with pytest.raises(VirtualEnvironmentError), VirtualEnvironment(self.__sample_root_dir_path):
            pass

    def test_09_teardown(self) -> None:
        """Verify that the VirtualEnvironment class removes the virtual environment when the context manager is exited."""
        # Arrange
        venv_path = str(Path(self.__sample_root_dir_path, const.VENV_NAME))

        # Act
        with VirtualEnvironment(self.__sample_root_dir_path):
            does_venv_exist_before = Path(venv_path).exists()

        does_venv_exist_after = Path(venv_path).exists()

        # Assert
        assert does_venv_exist_before
        assert not does_venv_exist_after

    def __create_sample_requirements(self, requirements_path: str) -> None:
        """
        Create a sample requirements.txt file.

        :param requirements_path: The path to the requirements.txt file.
        :type requirements_path: str
        """
        content = f"{self.__sample_package_name}=={self.__sample_package_version}"

        with open(requirements_path, "w+", encoding="utf-8") as file_handler:
            file_handler.write(content)
