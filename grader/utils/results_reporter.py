"""Module for handling the output of results from checks."""

import json
from abc import ABC, abstractmethod

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
        self._results: list[GradingResult] = []
        self._is_verbose = is_verbose

    @abstractmethod
    def to_string(self) -> str:
        """
        Convert the results to a string in a specific format.

        :return: A string representation of the results in a specific format.
        """

    def add_result(self, result: GradingResult) -> None:
        """
        Add a GradingResult to the reporter.

        :param result: The GradingResult to add.
        """
        self._results.append(result)


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

    def to_string(self) -> str:
        """
        Convert the results to a plain-text string.

        Each check result is emitted as its own line, followed by a per-run Total line.

        :return: A string representation of the results in plain-text format.
        """
        lines = []
        for result in self._results:
            lines += [self.__check_result_to_text(result.run_id, check_result) for check_result in result.results]
            lines.append(f"Run ID: {result.run_id}, Total Score: {result.total_score}/{result.max_score}")

        return "\n".join(lines) + "\n"

    def __check_result_to_text(self, run_id: str, check_result: CheckResult) -> str:
        """
        Convert a CheckResult to a plain text line.

        :param run_id: The run the check result belongs to.
        :param check_result: The CheckResult to convert.
        """
        match check_result:
            case ScoredCheckResult():
                score = f"{check_result.result}/{check_result.max_score}"
                parts = [f"Run ID: {run_id}, Check: {check_result.name}, Score: {score}"]
            case NonScoredCheckResult():
                parts = [f"Run ID: {run_id}, Check: {check_result.name}, Result: {check_result.result}"]
            case _:
                raise ValueError(f"Unknown CheckResult type ({type(check_result)}) for check {check_result.name}")

        if self._is_verbose:
            if check_result.info:
                parts.append(f"Info: {check_result.info}")
            if check_result.error:
                parts.append(f"Error: {check_result.error}")

        return ". ".join(parts)
