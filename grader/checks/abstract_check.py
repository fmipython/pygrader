"""
Module containing a class representing an abstract check.

Each check should inherit from this class.
"""

import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional

from grader.exceptions import CheckError
from grader.models.check_result import CheckResult, T
from grader.utils.logger import VERBOSE
from grader.utils.virtual_environment import VirtualEnvironment

logger = logging.getLogger("grader")


class AbstractCheck(ABC, Generic[T]):
    """Each check has a name and a project root path."""

    def __init__(
        self,
        name: str,
        project_root: str,
        is_venv_required: bool = False,
        env_vars: Optional[dict[str, str]] = None,
    ):
        """
        Initialize the check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param is_venv_required: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        """
        self._name = name
        self._project_root = project_root
        self._is_venv_required = is_venv_required
        self._env_vars = env_vars

    @abstractmethod
    def run(self) -> CheckResult[T]:
        """
        Execute the check.

        :returns: The result of the check.
        :rtype: Optional[T]
        """

    @property
    def name(self) -> str:
        """
        Get the name of the check.

        :returns: The name of the check.
        :rtype: str
        """
        return self._name

    @property
    def env_vars(self) -> Optional[dict[str, str]]:
        """
        Get the environment variables for the check.

        :returns: The environment variables for the check.
        :rtype: Optional[dict[str, str]]
        """
        return self._env_vars

    @staticmethod
    def is_running_within_venv() -> bool:
        """
        Determine if the check is running within a virtual environment.

        :returns: True if running within a virtual environment, False otherwise.
        :rtype: bool
        """
        return VirtualEnvironment.is_initialized

    def _pre_run(self) -> None:
        """
        Pre-run checks to ensure the environment is set up correctly.

        :raises CheckError: If the check requires a virtual environment and is not running within one.
        """
        if self._is_venv_required and not self.is_running_within_venv():
            raise CheckError("Virtual environment is required for this check")

        logger.log(VERBOSE, "Running %s", self.name)
