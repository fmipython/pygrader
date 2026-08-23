"""Module for handling the output of results from checks."""

import json
import sys
from abc import ABC, abstractmethod
from typing import TextIO, Union

from grader.models.check_result import CheckResult, NonScoredCheckResult, ScoredCheckResult
from grader.models.grading_result import GradingResult

CheckResultDict = dict[str, str | int | float | bool]
GradingResultDict = dict[str, str | float | list[CheckResultDict]]


class ResultsReporter(ABC):
    """Abstract base class for output classes.

    This class defines the interface for output classes that handle the display of results.
    Concrete subclasses must implement the `display` method.
    """

    def __init__(self, is_verbose: bool = False) -> None:
        """
        Initialize the ResultsReporter.

        :param verbose: Whether to include info and error fields in the output.
        """
        self._results = []
        self._is_verbose = is_verbose

    @abstractmethod
    def to_string(self) -> str:
        """
        Convert the results to a string in a specific format.

        :return: A string representation of the results in a specific format.
        """


class JSONResultsReporter(ResultsReporter):
    """Concrete class for JSON output.

    This class implements the `display` method to format and print the results in JSON format.
    """

    def to_string(self) -> str:
        """
        Convert the results to a JSON string.

        :return: A string representation of the results in JSON format.
        """
        content = [self.__grading_result_to_dict(result) for result in self._results]
        return json.dumps(content, indent=4)

    def __grading_result_to_dict(self, result: GradingResult) -> GradingResultDict:
        """
        Convert a GradingResult to a dictionary.

        :param result: The GradingResult to convert.
        """
        return {
            "run_id": result.run_id,
            "total_score": result.total_score,
            "max_score": result.max_score,
            "results": [self.__check_result_to_dict(check_result) for check_result in result.results],
        }

    def __check_result_to_dict(self, check_result: CheckResult) -> CheckResultDict:
        """
        Convert a CheckResult to a dictionary.

        :param check_result: The CheckResult to convert.
        """
        result: CheckResultDict = {}

        result["name"] = check_result.name

        if self._is_verbose:
            result["info"] = check_result.info
            result["error"] = check_result.error

        match check_result:
            case ScoredCheckResult():
                result["score"] = check_result.result
                result["max_score"] = check_result.max_score
            case NonScoredCheckResult():
                result["result"] = check_result.result
            case _:
                raise ValueError(f"Unknown CheckResult type ({type(check_result)}) for check {check_result.name}")

        return result


class CSVResultsReporter(ResultsReporter):
    """Concrete class for CSV output.

    This class implements the `display` method to format and print the results in CSV format.
    """

    def to_string(self) -> str:
        """
        Convert the results to a CSV string.

        Each check result is emitted as its own row, followed by a per-run Total row.

        :return: A string representation of the results in CSV format.
        """
        if self._is_verbose:
            rows = ["Run ID,Check,Score,Max Score,Info,Error"]
        else:
            rows = ["Run ID,Check,Score,Max Score"]

        for result in self._results:
            rows += [self.__check_result_to_csv(result.run_id, check_result) for check_result in result.results]

        return "\n".join(rows) + "\n"

    def __check_result_to_csv(self, run_id: str, check_result: CheckResult) -> str:
        """
        Convert a CheckResult to a CSV row.

        :param run_id: The run the check result belongs to.
        :param check_result: The CheckResult to convert.
        """
        match check_result:
            case ScoredCheckResult(name, score, info, error, max_score):
                if self._is_verbose:
                    return f"{run_id},{name},{score},{max_score},{info},{error}"
                return f"{run_id},{name},{score},{max_score}"
            case NonScoredCheckResult(name, result, info, error):
                if self._is_verbose:
                    return f"{run_id},{name},{result},NaN,{info},{error}"
                return f"{run_id},{name},{result},NaN"
            case _:
                raise ValueError(f"Unknown CheckResult type ({type(check_result)}) for check {check_result.name}")


class PlainTextResultsReporter(ResultsReporter):
    """Concrete class for plain text output.

    This class implements the `display` method to format and print the results in plain text format.
    """

    def display(
        self,
        run_id: str,
        results: list[CheckResult],
        verbose: bool,
        file_descriptor: TextIO = sys.stdout,
    ) -> None:
        """
        Display the results in plain text format.

        :param results: A list of CheckResult objects to display.
        :param verbose: Whether to include info and error fields in the output.
        :param file_descriptor: The file descriptor to write the output to.
        """
        output = self.to_string(run_id, results, verbose)
        self._to_file_descriptor(output, file_descriptor)

    def to_string(self, run_id: str, results: list[CheckResult], verbose: bool) -> str:
        """
        Convert the results to a plain-text string.

        :param results: A list of CheckResult objects to convert.
        :param verbose: Whether to include info and error fields in the output.
        :return: A string representation of the results in plain-text format.
        """
        scored_results = [result for result in results if isinstance(result, ScoredCheckResult)]
        total_score = sum(scored_result.result for scored_result in scored_results)
        total_max_score = sum(result.max_score for result in scored_results)

        output = [result_to_plain_text(run_id, check_result, verbose) for check_result in results]
        output.append(f"Total Score: {total_score}/{total_max_score}")
        return "\n".join(output) + "\n"


def result_to_plain_text(run_id: str, check_result: CheckResult, verbose: bool) -> str:
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
            return scored_result_to_text(run_id, check_result, verbose)
        case NonScoredCheckResult():
            return non_scored_result_to_text(run_id, check_result, verbose)
        case _:
            raise ValueError(f"Unknown CheckResult type ({type(check_result)}) for check {check_result.name}")


def scored_result_to_text(run_id: str, scored_result: ScoredCheckResult, verbose: bool) -> str:
    """
    Convert a ScoredCheckResult to a plain text string.

    :param scored_result: The ScoredCheckResult to convert.
    :type scored_result: ScoredCheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :return: A plain text string representation of the ScoredCheckResult.
    :rtype: str.
    """
    parts = [f"Run ID: {run_id}, Check: {scored_result.name}, Score: {scored_result.result}/{scored_result.max_score}"]
    if verbose:
        if scored_result.info:
            parts.append(f"Info: {scored_result.info}")
        if scored_result.error:
            parts.append(f"Error: {scored_result.error}")
    return ". ".join(parts)


def non_scored_result_to_text(run_id: str, non_scored_result: NonScoredCheckResult, verbose: bool) -> str:
    """
    Convert a NonScoredCheckResult to a plain text string.

    :param non_scored_result: The NonScoredCheckResult to convert.
    :type non_scored_result: NonScoredCheckResult
    :param verbose: Whether to include info and error fields.
    :type verbose: bool
    :return: A plain text string representation of the NonScoredCheckResult.
    :rtype: str.
    """
    parts = [f"Run ID: {run_id}, Check: {non_scored_result.name}, Result: {non_scored_result.result}"]
    if verbose:
        if non_scored_result.info:
            parts.append(f"Info: {non_scored_result.info}")
        if non_scored_result.error:
            parts.append(f"Error: {non_scored_result.error}")
    return ". ".join(parts)
