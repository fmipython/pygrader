from dataclasses import dataclass
from typing import Generic, TypeVar

from grader.checks.abstract_check import AbstractCheck

T = TypeVar("T")


@dataclass
class CheckResult(Generic[T]):
    """Class representing the result of a check."""

    name: str
    result: T
    info: str
    error: str


@dataclass
class ScoredCheckResult(CheckResult[T]):
    """Class representing the result of a scored check."""

    max_score: int


@dataclass
class NonScoredCheckResult(CheckResult[bool]):
    """Class representing the result of a non-scored check."""


class ScoredCheck(AbstractCheck[float]):
    """Each scored check has a maximum amount of points."""

    def __init__(
        self,
        name: str,
        max_points: int,
        project_root: str,
        is_venv_requred: bool = False,
        env_vars: Optional[dict[str, str]] = None,
    ):
        """
        Initialize the scored check.

        :param name: The name of the check.
        :param max_points: The maximum points this check can award.
        :param project_root: The root directory of the project.
        :param is_venv_requred: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        """
        super().__init__(name, project_root, is_venv_requred, env_vars)
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
    ):
        """
        Initialize the non-scored check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param is_fatal: Whether the check is fatal.
        :param is_venv_requred: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        """
        super().__init__(name, project_root, is_venv_requred, env_vars)
        self._is_fatal = is_fatal

    @property
    def is_fatal(self) -> bool:
        """Return True if the check failing is fatal, False otherwise."""
        return self._is_fatal
