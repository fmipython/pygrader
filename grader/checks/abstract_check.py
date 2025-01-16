"""
Module containing a class representing an abstract check.
Each check should inherit from this class.
"""

from abc import ABC, abstractmethod

# Bad design, but I can't figure out a better way to check if running within a virtual environment
from grader.utils.virtual_environment import VirtualEnvironment


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

    @abstractmethod
    def run(self) -> float:
        """
        Main method that executes the check.

        Returns the score of the check.
        """
        if self._is_venv_required and not self.is_running_within_venv():
            raise RuntimeError("Virtual environment is required for this check")

        raise NotImplementedError("Method run() must be implemented")

    @property
    def name(self) -> str:
        """
        Get the name of the check.

        Returns the name of the check
        """
        return self._name

    @property
    def max_points(self) -> int:
        """
        Returns the maximum amount of points that can be achieved by the check.
        """
        return self._max_points

    @abstractmethod
    def is_running_within_venv(self) -> bool:
        """
        Determine if the check is running within a virtual environment.

        Returns True if running within a virtual environment, False otherwise.
        """

        return VirtualEnvironment.is_initialized
