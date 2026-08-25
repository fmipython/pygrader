"""Dataclasses representing the result of a grading operation."""

from dataclasses import dataclass

from grader.models.check_result import CheckResult


@dataclass
class GradingResult:
    """Class representing the overall grading result."""

    run_id: str
    total_score: float
    max_score: float
    results: list[CheckResult]
