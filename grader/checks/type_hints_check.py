"""
Module containing the type hints check.
It calls mypy as a subprocess to generate a report and then read from the report.
"""

import logging
import subprocess

from grader.checks.abstract_check import AbstractCheck
from grader.utils.constants import MYPY_TYPE_HINT_CONFIG, REPORTS_TEMP_DIR, MYPY_LINE_COUNT_REPORT
from grader.utils.files import find_all_python_files

logger = logging.getLogger("grader")


class TypeHintsCheck(AbstractCheck):
    """
    The TypeHints check class.
    """

    def __init__(self, name: str, max_points: int, project_root: str):
        super().__init__(name, max_points, project_root)

        self.__mypy_binary = "mypy"
        self.__mypy_arguments = ["--config-file", MYPY_TYPE_HINT_CONFIG, "--linecount-report", REPORTS_TEMP_DIR]

    def run(self) -> float:
        """
        Run the mypy check on the project.

        First, find all python files in the project, then run mypy on all files with the special config.
        Mypy then generates a report with the amount of lines with type hints and the total amount of lines.

        The first line in the report contains the values for all files.
        The line contains a lot of stuff, we just need the type-hinted lines and the total amount of lines.
        Returns the score from the mypy check.
        """
        super().run()

        # Gather all files
        files = find_all_python_files(self._project_root)  # TODO - Should it only be ran on production code?

        # Run mypy on all files
        command = [self.__mypy_binary] + self.__mypy_arguments + files
        subprocess.run(command, check=False, capture_output=True)

        # Read mypy linecount report
        with open(MYPY_LINE_COUNT_REPORT, "r", encoding="utf-8") as report_file:
            report = report_file.readline().strip().split()

        # Fancy way to get the needed values - I need the 3rd and 4th values, out of 5 total
        *_, lines_with_type_annotations, lines_total, _ = report

        # Calculate score
        return self.__translate_score(int(lines_with_type_annotations) / int(lines_total))

    def __translate_score(self, mypy_score: float) -> float:
        """
        The mypy score is a percentage of the amount of lines with type hints in the project.
        The number is between 0 and 1.

        My initial idea is to put in bins in range 0.5 - 0, 0.5, 1, 1.5, etc.

        :param pylint_score: The score from mypy to be translated
        :return: The translated score
        """
        step = 0.5
        amount_of_steps = int(self._max_points / step) + 1
        steps = [i * step for i in range(amount_of_steps)]
        regions = list(zip(steps, steps[1:]))

        for score, (start, end) in enumerate(regions, start=1):
            if start <= mypy_score * mypy_score < end:
                return score

        return 0
