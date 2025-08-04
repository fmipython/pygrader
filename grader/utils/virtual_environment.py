"""
Module containing the virtual environment class.
"""

from __future__ import annotations  # Python 3.14 will fix this
import logging
import os
import shutil
import grader.utils.constants as const

from grader.utils.logger import VERBOSE
from grader.utils.process import run

logger = logging.getLogger("grader")


class VirtualEnvironment:
    """
    Class that handles the creation and deletion of a virtual environment.
    Acts as a context manager. Everything executed within it, can assume that the venv is setup.
    """

    is_initialized = False

    def __init__(self, project_path: str, keep_venv: bool = False):
        self._project_path = project_path
        self._venv_path = os.path.join(project_path, const.VENV_NAME)
        self.__keep_venv = keep_venv

    def __enter__(self) -> VirtualEnvironment:
        self.setup()
        VirtualEnvironment.is_initialized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        self.teardown()
        VirtualEnvironment.is_initialized = False

    def setup(self) -> None:
        """
        Setup the virtual environment.
        Check if there is an existing venv, if so, delete it.
        Check if there is a requirements.txt file.
        Create a new venv and install the requirements.
        Install the grader dependencies as well.
        """
        # Check for existing venv
        possible_venv_paths = [os.path.join(self._project_path, venv_path) for venv_path in const.POSSIBLE_VENV_DIRS]

        for path in possible_venv_paths:
            if os.path.exists(path):
                logger.log(VERBOSE, "Found existing venv at %s", path)
                shutil.rmtree(path)

        # Check for requirements.txt
        requirements_path = os.path.join(self._project_path, const.REQUIREMENTS_FILENAME)

        does_requirements_exist = os.path.exists(requirements_path)
        if not does_requirements_exist:
            logger.error("No requirements.txt file found in the project directory")

        # Create new venv
        logger.log(VERBOSE, "Creating new venv")

        create_venv_result = run([const.PYTHON_BIN, "-m", "venv", self._venv_path])
        if create_venv_result.returncode != 0:
            logger.error("Failed to create virtual environment")
            raise VirtualEnvironmentError("Failed to create virtual environment")

        # Install requirements
        if does_requirements_exist:
            logger.log(VERBOSE, "Installing requirements")
            VirtualEnvironment.__install_requirements(self._venv_path, requirements_path)

        # Install grader dependencies
        logger.log(VERBOSE, "Installing grader dependencies")

        grader_requirements_path = const.GRADER_REQUIREMENTS
        VirtualEnvironment.__install_requirements(self._venv_path, grader_requirements_path)

    def teardown(self) -> None:
        """
        Delete the virtual environment.
        """
        if not self.__keep_venv:
            shutil.rmtree(self._venv_path)

    @staticmethod
    def __install_requirements(venv_path: str, requirements_path: str) -> None:
        """
        Install the requirements specified in the requirements file into the virtual environment.
        :param venv_path: The path to the virtual environment.
        :type venv_path: str
        :param requirements_path: The path to the requirements file.
        :type requirements_path: str
        :raises VirtualEnvironmentError: If the installation of requirements fails.
        :return: None
        :rtype: None
        """

        pip_path = os.path.join(venv_path, const.PIP_PATH)

        output = run([pip_path, "install", "-r", requirements_path])

        if output.returncode != 0:
            logger.error("Failed to install requirements from %s", requirements_path)
            raise VirtualEnvironmentError(f"Failed to install requirements from {requirements_path}")


class VirtualEnvironmentError(Exception):
    """
    Exception raised when an error occurs during the virtual environment setup.
    """
