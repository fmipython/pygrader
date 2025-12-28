"""
Module containing a class representing an abstract check.
Each check should inherit from this class.
"""

from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from grader.utils.logger import VERBOSE
from grader.utils.virtual_environment import VirtualEnvironment

logger = logging.getLogger("grader")


T = TypeVar("T")


@dataclass
class CheckResult(Generic[T]):
    """
    Class representing the result of a check.
    """

    name: str
    result: T
    info: str
    error: str


class AbstractCheck(ABC, Generic[T]):
    """
    Each check has a name and a project root path.
    """

    def __init__(
        self,
        name: str,
        project_root: str,
        is_venv_required: bool = False,
        env_vars: Optional[dict[str, str]] = None,
    ):
        self._name = name
        self._project_root = project_root
        self._is_venv_required = is_venv_required
        self._env_vars = env_vars

    @abstractmethod
    def run(self) -> CheckResult[T]:
        """
        Main method that executes the check.

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


@dataclass
class ScoredCheckResult(CheckResult[T]):
    """
    Class representing the result of a scored check.
    """

    max_score: int


@dataclass
class NonScoredCheckResult(CheckResult[bool]):
    """
    Class representing the result of a non-scored check.
    """


class ScoredCheck(AbstractCheck[float]):
    """
    Each scored check has a maximum amount of points.
    """

    def __init__(
        self,
        name: str,
        max_points: int,
        project_root: str,
        is_venv_requred: bool = False,
        env_vars: Optional[dict[str, str]] = None,
    ):
        super().__init__(name, project_root, is_venv_requred, env_vars)
        self._max_points = max_points

    @property
    def max_points(self) -> int:
        """
        :returns: The maximum amount of points that can be achieved by the check.
        :rtype: int
        """
        return self._max_points


class NonScoredCheck(AbstractCheck[bool]):
    """
    Non-scored checks do not have a maximum amount of points.
    """

    def __init__(
        self,
        name: str,
        project_root: str,
        is_fatal: bool,
        is_venv_requred: bool = False,
        env_vars: Optional[dict[str, str]] = None,
    ):
        super().__init__(name, project_root, is_venv_requred, env_vars)
        self._is_fatal = is_fatal

    @property
    def is_fatal(self) -> bool:
        """
        :returns: True if the check failing is fatal, False otherwise.
        :rtype: bool
        """
        return self._is_fatal


class CheckError(Exception):
    """Custom exception for check errors."""
