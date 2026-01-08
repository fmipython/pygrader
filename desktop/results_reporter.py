"""
Module for handling the output of results from checks.
"""

import json
import sys
from abc import ABC, abstractmethod
from typing import TextIO

from grader.checks.abstract_check import ScoredCheckResult, NonScoredCheckResult, CheckResult


class ResultsReporter(ABC):
    """Abstract base class for output classes.

    This class defines the interface for output classes that handle the display of results.
    Concrete subclasses must implement the `display` method.
    """

    @abstractmethod
    def display(self, results: list[CheckResult], file_descriptor: TextIO = sys.stdout) -> None:
        """
        Display the results in a specific format.
        :param results: A list of CheckResult objects to display.
        :param file_descriptor: The file descriptor to write the output to, defaults to sys.stdout.
        """

    def _to_file_descriptor(self, content: str, file_descriptor: TextIO) -> None:
        """Write the content to the specified file descriptor.

        Args:
            content (str): The content to write.
            file_descriptor (TextIO): The file descriptor to write to.
        """
        file_descriptor.write(content)
        file_descriptor.flush()


class JSONResultsReporter(ResultsReporter):
    """Concrete class for JSON output.

    This class implements the `display` method to format and print the results in JSON format.
    """

    def display(self, results: list[CheckResult], file_descriptor: TextIO = sys.stdout) -> None:
        scored_results = [result for result in results if isinstance(result, ScoredCheckResult)]
        total_score = sum(scored_result.result for scored_result in scored_results)
        total_max_score = sum(result.max_score for result in scored_results)

        content = {
            "scored_checks": [result_to_json(result) for result in scored_results],
            "non_scored_checks": [
                result_to_json(result) for result in results if isinstance(result, NonScoredCheckResult)
            ],
            "total_score": total_score,
            "total_max_score": total_max_score,
        }

        output = json.dumps(content, indent=4)

        self._to_file_descriptor(output, file_descriptor)


def result_to_json(check_result: CheckResult) -> dict:
    """
    Convert a CheckResult to a JSON-compatible dictionary.

    :param result: The CheckResult to convert.
    :type result: CheckResult
    :raises ValueError: If the result is not of type ScoredCheckResult or NonScoredCheckResult.
    :return: A dictionary representation of the CheckResult.
    :rtype: dict
    """
    match check_result:
        case ScoredCheckResult(name, score, info, error, max_score):
            return {
                "name": name,
                "score": score,
                "info": info,
                "error": error,
                "max_score": max_score,
            }
        case NonScoredCheckResult(name, result, info, error):
            return {"name": name, "result": result, "info": info, "error": error}
        case _:
            raise ValueError("Unknown CheckResult type")


class CSVResultsReporter(ResultsReporter):
    """Concrete class for CSV output.

    This class implements the `display` method to format and print the results in CSV format.
    """

    def display(self, results: list[CheckResult], file_descriptor: TextIO = sys.stdout) -> None:
        scored_results = [result for result in results if isinstance(result, ScoredCheckResult)]
        total_score = sum(scored_result.result for scored_result in scored_results)
        total_max_score = sum(result.max_score for result in scored_results)

        output = ["Check,Score,Max Score"]
        output += [result_to_csv(check_result) for check_result in results]
        output.append(f"Total,{total_score},{total_max_score}")

        self._to_file_descriptor("\n".join(output) + "\n", file_descriptor)


def result_to_csv(check_result: CheckResult) -> str:
    """
    Convert a CheckResult to a CSV-compatible string.

    :param result: The CheckResult to convert.
    :type result: CheckResult
    :raises ValueError: If the result is not of type ScoredCheckResult or NonScoredCheckResult.
    :return: A CSV-compatible string representation of the CheckResult.
    :rtype: str
    """
    match check_result:
        case ScoredCheckResult(name, score, info, error, max_score):
            return f"{name},{score},{info},{error},{max_score}"
        case NonScoredCheckResult(name, result, info, error):
            return f"{name},{result},{info},{error},NaN"
        case _:
            raise ValueError("Unknown CheckResult type")


class PlainTextResultsReporter(ResultsReporter):
    """Concrete class for plain text output.

    This class implements the `display` method to format and print the results in plain text format.
    """

    def display(self, results: list[CheckResult], file_descriptor: TextIO = sys.stdout) -> None:
        scored_results = [result for result in results if isinstance(result, ScoredCheckResult)]
        total_score = sum(scored_result.result for scored_result in scored_results)
        total_max_score = sum(result.max_score for result in scored_results)

        output = [result_to_plain_text(check_result) for check_result in results]
        output.append(f"Total Score: {total_score}/{total_max_score}")
        self._to_file_descriptor("\n".join(output) + "\n", file_descriptor)


def result_to_plain_text(check_result: CheckResult) -> str:
    """
    Convert a CheckResult to a plain text string.

    :param result: The CheckResult to convert.
    :type result: CheckResult
    :raises ValueError: If the result is not of type ScoredCheckResult or NonScoredCheckResult.
    :return: A plain text string representation of the CheckResult.
    :rtype: str
    """
    match check_result:
        case ScoredCheckResult(name, score, info, error, max_score):
            return f"Check: {name}, Score: {score}/{max_score}, Info: {info}"
        case NonScoredCheckResult(name, result, info, error):
            return f"Check: {name}, Result: {result}, Info: {info}"
        case _:
            raise ValueError(f"Unknown CheckResult type ({type(check_result)}) for check {check_result.name}")
