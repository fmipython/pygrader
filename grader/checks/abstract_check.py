"""
Module containing a class representing an abstract check.
Each check should inherit from this class.
"""

import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from grader.utils.logger import VERBOSE
from grader.utils.virtual_environment import VirtualEnvironment

logger = logging.getLogger("grader")


T = TypeVar("T")


class AbstractCheck(ABC, Generic[T]):
    """
    Each check has a name and a project root path.
    """

    def __init__(self, name: str, project_root: str, is_venv_requred: bool = False):
        self._name = name
        self._project_root = project_root
        self._is_venv_required = is_venv_requred

    @abstractmethod
    def run(self) -> Optional[T]:
        """
        Main method that executes the check.

        :returns: The result of the check.
        :rtype: Optional[T]
        """
        if self._is_venv_required and not self.is_running_within_venv():
            raise CheckError("Virtual environment is required for this check")

        logger.log(VERBOSE, "Running %s", self.name)
        return None

    @property
    def name(self) -> str:
        """
        Get the name of the check.

        :returns: The name of the check.
        :rtype: str
        """
        return self._name

    @staticmethod
    def is_running_within_venv() -> bool:
        """
        Determine if the check is running within a virtual environment.

        :returns: True if running within a virtual environment, False otherwise.
        :rtype: bool
        """
        return VirtualEnvironment.is_initialized


class ScoredCheck(AbstractCheck[float]):
    """
    Each scored check has a maximum amount of points.
    """

    def __init__(self, name: str, max_points: int, project_root: str, is_venv_requred: bool = False):
        super().__init__(name, project_root, is_venv_requred)
        self._max_points = max_points

    @property
    def max_points(self) -> int:
        """
        :returns: The maximum amount of points that can be achieved by the check.
        :rtype: int
        """
        return self._max_points

    def run(self) -> float:
        """
        Main method that executes the check.

        :returns: The score of the check.
        :rtype: float
        """
        super().run()
        # Implement the logic for the scored check here
        return 0.0  # Replace with actual score


class NonScoredCheck(AbstractCheck[bool]):
    """
    Non-scored checks do not have a maximum amount of points.
    """

    def __init__(self, name: str, project_root: str, is_fatal: bool, is_venv_requred: bool = False):
        super().__init__(name, project_root, is_venv_requred)
        self._is_fatal = is_fatal

    @property
    def is_fatal(self) -> bool:
        """
        :returns: True if the check failing is fatal, False otherwise.
        :rtype: bool
        """
        return self._is_fatal

    def run(self) -> bool:
        """
        Main method that executes the check.

        :returns: True if the check passes, False otherwise.
        :rtype: bool
        """
        super().run()
        # Implement the logic for the non-scored check here
        return True  # or False based on the check logic


class CheckError(Exception):
    """Custom exception for check errors."""
