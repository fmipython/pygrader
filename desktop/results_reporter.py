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
    def display(self, results: list[CheckResult], verbose: bool, file_descriptor: TextIO = sys.stdout) -> None:
        """
        Display the results in a specific format.
        :param results: A list of CheckResult objects to display.
        :param verbose: Whether to include info and error fields in the output.
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

    def display(self, results: list[CheckResult], verbose: bool, file_descriptor: TextIO = sys.stdout) -> None:
        scored_results = [result for result in results if isinstance(result, ScoredCheckResult)]
        total_score = sum(scored_result.result for scored_result in scored_results)
        total_max_score = sum(result.max_score for result in scored_results)

        content = {
            "scored_checks": [result_to_json(result, verbose) for result in scored_results],
            "non_scored_checks": [
                result_to_json(result, verbose) for result in results if isinstance(result, NonScoredCheckResult)
            ],
            "total_score": total_score,
            "total_max_score": total_max_score,
        }

        output = json.dumps(content, indent=4)

        self._to_file_descriptor(output, file_descriptor)


def result_to_json(check_result: CheckResult, verbose: bool) -> dict:
    """
    Convert a CheckResult to a JSON-compatible dictionary.

    :param result: The CheckResult to convert.
    :type result: CheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :raises ValueError: If the result is not of type ScoredCheckResult or NonScoredCheckResult.
    :return: A dictionary representation of the CheckResult.
    :rtype: dict
    """
    match check_result:
        case ScoredCheckResult():
            return scored_result_to_dict(check_result, verbose)
        case NonScoredCheckResult():
            return non_scored_result_to_dict(check_result, verbose)
        case _:
            raise ValueError("Unknown CheckResult type")


def non_scored_result_to_dict(non_scored_result: NonScoredCheckResult, verbose: bool) -> dict:
    """
    Convert a NonScoredCheckResult to a dictionary.

    :param non_scored_result: The NonScoredCheckResult to convert.
    :type non_scored_result: NonScoredCheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :return: A dictionary representation of the NonScoredCheckResult.
    :rtype: dict
    """

    result_dict = {"name": non_scored_result.name, "result": non_scored_result.result}
    if verbose:
        if non_scored_result.info:
            result_dict["info"] = non_scored_result.info
        if non_scored_result.error:
            result_dict["error"] = non_scored_result.error
    return result_dict


def scored_result_to_dict(scored_result: ScoredCheckResult, verbose: bool) -> dict:
    """
    Convert a ScoredCheckResult to a dictionary.

    :param scored_result: The ScoredCheckResult to convert.
    :type scored_result: ScoredCheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :return: A dictionary representation of the ScoredCheckResult.
    :rtype: dict
    """
    result_dict = {
        "name": scored_result.name,
        "score": scored_result.result,
        "max_score": scored_result.max_score,
    }
    if verbose:
        if scored_result.info:
            result_dict["info"] = scored_result.info
        if scored_result.error:
            result_dict["error"] = scored_result.error
    return result_dict


class CSVResultsReporter(ResultsReporter):
    """Concrete class for CSV output.

    This class implements the `display` method to format and print the results in CSV format.
    """

    def display(self, results: list[CheckResult], verbose: bool, file_descriptor: TextIO = sys.stdout) -> None:
        scored_results = [result for result in results if isinstance(result, ScoredCheckResult)]
        total_score = sum(scored_result.result for scored_result in scored_results)
        total_max_score = sum(result.max_score for result in scored_results)

        if verbose:
            output = ["Check,Score,Max Score,Info,Error"]
        else:
            output = ["Check,Score,Max Score"]
        output += [result_to_csv(check_result, verbose) for check_result in results]
        output.append(f"Total,{total_score},{total_max_score}")

        self._to_file_descriptor("\n".join(output) + "\n", file_descriptor)


def result_to_csv(check_result: CheckResult, verbose: bool) -> str:
    """
    Convert a CheckResult to a CSV-compatible string.

    :param result: The CheckResult to convert.
    :type result: CheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :raises ValueError: If the result is not of type ScoredCheckResult or NonScoredCheckResult.
    :return: A CSV-compatible string representation of the CheckResult.
    :rtype: str
    """
    match check_result:
        case ScoredCheckResult(name, score, info, error, max_score):
            if verbose:
                return f"{name},{score},{max_score},{info},{error}"
            return f"{name},{score},{max_score}"
        case NonScoredCheckResult(name, result, info, error):
            if verbose:
                return f"{name},{result},NaN,{info},{error}"
            return f"{name},{result},NaN"
        case _:
            raise ValueError("Unknown CheckResult type")


class PlainTextResultsReporter(ResultsReporter):
    """Concrete class for plain text output.

    This class implements the `display` method to format and print the results in plain text format.
    """

    def display(self, results: list[CheckResult], verbose: bool, file_descriptor: TextIO = sys.stdout) -> None:
        scored_results = [result for result in results if isinstance(result, ScoredCheckResult)]
        total_score = sum(scored_result.result for scored_result in scored_results)
        total_max_score = sum(result.max_score for result in scored_results)

        output = [result_to_plain_text(check_result, verbose) for check_result in results]
        output.append(f"Total Score: {total_score}/{total_max_score}")
        self._to_file_descriptor("\n".join(output) + "\n", file_descriptor)


def result_to_plain_text(check_result: CheckResult, verbose: bool) -> str:
    """
    Convert a CheckResult to a plain text string.

    :param result: The CheckResult to convert.
    :type result: CheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :raises ValueError: If the result is not of type ScoredCheckResult or NonScoredCheckResult.
    :return: A plain text string representation of the CheckResult.
    :rtype: str
    """
    match check_result:
        case ScoredCheckResult():
            return scored_result_to_text(check_result, verbose)
        case NonScoredCheckResult():
            return non_scored_result_to_text(check_result, verbose)
        case _:
            raise ValueError(f"Unknown CheckResult type ({type(check_result)}) for check {check_result.name}")


def scored_result_to_text(scored_result: ScoredCheckResult, verbose: bool) -> str:
    """
    Convert a ScoredCheckResult to a plain text string.
    :param scored_result: The ScoredCheckResult to convert.
    :type scored_result: ScoredCheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :return: A plain text string representation of the ScoredCheckResult.
    :rtype: str
    """
    parts = [f"Check: {scored_result.name}, Score: {scored_result.result}/{scored_result.max_score}"]
    if verbose:
        if scored_result.info:
            parts.append(f"Info: {scored_result.info}")
        if scored_result.error:
            parts.append(f"Error: {scored_result.error}")
    return ". ".join(parts)


def non_scored_result_to_text(non_scored_result: NonScoredCheckResult, verbose: bool) -> str:
    """
    Convert a NonScoredCheckResult to a plain text string.
    :param non_scored_result: The NonScoredCheckResult to convert.
    :type non_scored_result: NonScoredCheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :return: A plain text string representation of the NonScoredCheckResult.
    :rtype: str
    """
    parts = [f"Check: {non_scored_result.name}, Result: {non_scored_result.result}"]
    if verbose:
        if non_scored_result.info:
            parts.append(f"Info: {non_scored_result.info}")
        if non_scored_result.error:
            parts.append(f"Error: {non_scored_result.error}")
    return ". ".join(parts)
