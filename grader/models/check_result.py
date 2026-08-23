from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class CheckResult(Generic[T]):
    """Class representing the result of a check."""

    name: str
    result: T
    info: str
    error: str


@dataclass
class ScoredCheckResult(CheckResult[float]):
    """Class representing the result of a scored check."""

    max_score: int


@dataclass
class NonScoredCheckResult(CheckResult[bool]):
    """Class representing the result of a non-scored check."""
