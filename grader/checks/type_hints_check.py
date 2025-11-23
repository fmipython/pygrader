"""
Module containing the type hints check.
It calls mypy as a subprocess to generate a report and then read from the report.
"""

import logging

from grader.checks.abstract_check import ScoredCheck, CheckError, ScoredCheckResult
from grader.utils.constants import MYPY_TYPE_HINT_CONFIG, REPORTS_TEMP_DIR, MYPY_LINE_COUNT_REPORT, MYPY_PATH
from grader.utils import files
from grader.utils import process

logger = logging.getLogger("grader")


class TypeHintsCheck(ScoredCheck):
    """
    The TypeHints check class.
    """

    def __init__(self, name: str, project_root: str, max_points: int, is_venv_required: bool):
        super().__init__(name, max_points, project_root, is_venv_required)

        self.__mypy_binary = MYPY_PATH
        self.__mypy_arguments = ["--config-file", MYPY_TYPE_HINT_CONFIG, "--linecount-report", REPORTS_TEMP_DIR]
        self.__mypy_max_score = 1

    def run(self) -> ScoredCheckResult:
        """
        Run the mypy check on the project.

        First, find all python files in the project, then run mypy on all files with the special config.
        Mypy then generates a report with the amount of lines with type hints and the total amount of lines.

        The first line in the report contains the values for all files.
        The line contains a lot of stuff, we just need the type-hinted lines and the total amount of lines.

        :returns: The score from the mypy check.
        :rtype: float
        """
        self._pre_run()

        # Gather all files
        try:
            all_source_files = files.find_all_source_files(self._project_root)
        except OSError as error:
            logger.error("Error while finding python files: %s", error)
            raise CheckError("Error while finding python files") from error

        # Run mypy on all files
        command = [self.__mypy_binary] + self.__mypy_arguments + all_source_files
        try:
            _ = process.run(command)
        except (OSError, ValueError) as error:
            logger.error("Error while running mypy: %s", error)
            raise CheckError("Error while running mypy") from error

        # Read mypy linecount report
        try:
            with open(MYPY_LINE_COUNT_REPORT, "r", encoding="utf-8") as report_file:
                report = report_file.readline().strip().split()
        except FileNotFoundError as error:
            logger.error("Mypy linecount report not found")
            raise CheckError("Mypy linecount report not found") from error

        # Fancy way to get the needed values - I need the 3rd and 4th values, out of 5 total
        *_, lines_with_type_annotations, lines_total, _ = report

        if int(lines_total) == 0:
            logger.error("Mypy linecount report is empty")
            return ScoredCheckResult(self.name, 0, self.max_points)

        # Calculate score
        score = self.__translate_score(int(lines_with_type_annotations) / int(lines_total))

        return ScoredCheckResult(self.name, score, self.max_points)

    def __translate_score(self, mypy_score: float) -> float:
        """
        Split the mypy score into regions and assign a score based on the region.
        The amount of regions depends on the max points for the criteria.

        :param pylint_score: The score from pylint to be translated
        :return: The translated score
        """
        if self._max_points == -1:
            raise CheckError("Max points for type hints check is set to -1")

        step = self.__mypy_max_score / (self._max_points + 1)
        steps = [i * step for i in range(self._max_points + 2)]

        regions = list(zip(steps, steps[1:]))

        for score, (start, end) in enumerate(regions):
            if round(start, 2) <= round(mypy_score, 2) < round(end, 2):
                return score

        return self._max_points
