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
        pass

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
        content = {
            "scored_checks": [result_to_json(result) for result in results if isinstance(result, ScoredCheckResult)],
            "non_scored_checks": [
                result_to_json(result) for result in results if isinstance(result, NonScoredCheckResult)
            ],
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
        case ScoredCheckResult(name, score, max_score):
            return {
                "name": name,
                "score": score,
                "max_score": max_score,
            }
        case NonScoredCheckResult(name, result):
            return {
                "name": name,
                "result": result,
            }
        case _:
            raise ValueError("Unknown CheckResult type")


class CSVResultsReporter(ResultsReporter):
    """Concrete class for CSV output.

    This class implements the `display` method to format and print the results in CSV format.
    """

    def display(self, results: list[CheckResult], file_descriptor: TextIO = sys.stdout) -> None:
        output = ["Check,Score,Max Score"]
        output += [result_to_csv(check_result) for check_result in results]

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
        case ScoredCheckResult(name, score, max_score):
            return f"{name},{score},{max_score}"
        case NonScoredCheckResult(name, result):
            return f"{name},{result},NaN"
        case _:
            raise ValueError("Unknown CheckResult type")


class PlainTextResultsReporter(ResultsReporter):
    """Concrete class for plain text output.

    This class implements the `display` method to format and print the results in plain text format.
    """

    def display(self, results: list[CheckResult], file_descriptor: TextIO = sys.stdout) -> None:
        output = [result_to_plain_text(check_result) for check_result in results]
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
        case ScoredCheckResult(name, score, max_score):
            return f"Check: {name}, Score: {score}/{max_score}"
        case NonScoredCheckResult(name, result):
            return f"Check: {name}, Result: {result}"
        case _:
            raise ValueError(f"Unknown CheckResult type ({type(check_result)}) for check {check_result.name}")
