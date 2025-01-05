"""
Module containing a class representing an abstract check.
Each check should inherit from this class.
"""
from abc import ABC, abstractmethod


class AbstractCheck(ABC):
    """
    Each check has a name and a maximum amount of points.
    It also needs the project root path.
    """
    def __init__(self, name: str, max_points: int, project_root: str):
        self._name = name
        self._max_points = max_points
        self._project_root = project_root

        # TODO - Add a check if running inside a virtual environment

    @abstractmethod
    def run(self) -> float:
        """
        Main method that executes the check.

        Returns the score of the check.
        """

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
