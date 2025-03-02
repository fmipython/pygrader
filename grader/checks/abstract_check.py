"""
Module containing a class representing an abstract check.
Each check should inherit from this class.
"""

import logging
from abc import ABC

from grader.utils.logger import VERBOSE
from grader.utils.virtual_environment import VirtualEnvironment

logger = logging.getLogger("grader")


# TODO - Currently, all checks have to have a score.
# This is not always the case. Some checks are just for validation (or true/false).
# Idea is to have separate interface for scored checks and non-scored checks.


# TODO - StructureCheck needs additional arguments to be passed to the constructor.
# This should be handled in all checks.


class AbstractCheck(ABC):
    """
    Each check has a name and a maximum amount of points.
    It also needs the project root path.
    """

    def __init__(self, name: str, max_points: int, project_root: str, is_venv_requred: bool = False):
        self._name = name
        self._max_points = max_points
        self._project_root = project_root
        self._is_venv_required = is_venv_requred

    def run(self) -> float:
        """
        Main method that executes the check.

        :returns: The score of the check.
        :rtype: float
        """
        if self._is_venv_required and not self.is_running_within_venv():
            raise CheckError("Virtual environment is required for this check")

        logger.log(VERBOSE, "Running %s", self.name)

        return 0.0

    @property
    def name(self) -> str:
        """
        Get the name of the check.

        :returns: The name of the check.
        :rtype: str
        """
        return self._name

    @property
    def max_points(self) -> int:
        """
        :returns: The maximum amount of points that can be achieved by the check.
        :rtype: int
        """
        return self._max_points

    @staticmethod
    def is_running_within_venv() -> bool:
        """
        Determine if the check is running within a virtual environment.

        :returns: True if running within a virtual environment, False otherwise.
        :rtype: bool
        """
        return VirtualEnvironment.is_initialized


class CheckError(Exception):
    """Custom exception for check errors."""
