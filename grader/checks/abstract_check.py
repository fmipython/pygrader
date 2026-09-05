"""
Module containing a class representing an abstract check.

Each check should inherit from this class.
"""

import logging
from abc import ABC, abstractmethod
from typing import Generic, Optional

from grader.exceptions import CheckError
from grader.models.check_result import CheckResult, T
from grader.utils.external_resources import Resource
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
        assets: Optional[list[str]] = None,
    ):
        """
        Initialize the check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param is_venv_required: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        :param assets: Optional list of resource sources (paths, URLs or Cove URIs) for the check.
        """
        self._name = name
        self._project_root = project_root
        self._is_venv_required = is_venv_required
        self._env_vars = env_vars
        self._assets = [Resource(source) for source in (assets or [])]

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

    @property
    def assets(self) -> list[Resource]:
        """
        Get the assets for the check.

        :returns: The assets for the check.
        :rtype: list[Resource]
        """
        return self._assets

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


class ScoredCheck(AbstractCheck[float]):
    """Each scored check has a maximum amount of points."""

    def __init__(
        self,
        name: str,
        max_points: int,
        project_root: str,
        is_venv_requred: bool = False,
        env_vars: Optional[dict[str, str]] = None,
        assets: Optional[list[str]] = None,
    ):
        """
        Initialize the scored check.

        :param name: The name of the check.
        :param max_points: The maximum points this check can award.
        :param project_root: The root directory of the project.
        :param is_venv_requred: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        :param assets: Optional list of resource sources (paths, URLs or Cove URIs) for the check.
        """
        super().__init__(name, project_root, is_venv_requred, env_vars, assets)
        self._max_points = max_points

    @property
    def max_points(self) -> int:
        """Return the maximum amount of points that can be achieved by the check."""
        return self._max_points


class NonScoredCheck(AbstractCheck[bool]):
    """Non-scored checks do not have a maximum amount of points."""

    def __init__(
        self,
        name: str,
        project_root: str,
        is_fatal: bool,
        is_venv_requred: bool = False,
        env_vars: Optional[dict[str, str]] = None,
        assets: Optional[list[str]] = None,
    ):
        """
        Initialize the non-scored check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param is_fatal: Whether the check is fatal.
        :param is_venv_requred: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        :param assets: Optional list of resource sources (paths, URLs or Cove URIs) for the check.
        """
        super().__init__(name, project_root, is_venv_requred, env_vars, assets)
        self._is_fatal = is_fatal

    @property
    def is_fatal(self) -> bool:
        """Return True if the check failing is fatal, False otherwise."""
        return self._is_fatal
