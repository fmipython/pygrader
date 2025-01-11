"""
Module containing the unit test code coverage check.
"""
import logging
import os
import subprocess

from grader.checks.abstract_check import AbstractCheck
from grader.utils.constants import COVERAGE_PATH, COVERAGE_RUN_ARGS, COVERAGE_RUN_PYTEST_ARGS, COVERAGE_REPORT_ARGS
from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")


class CoverageCheck(AbstractCheck):
    """
    The Coverage check class.
    """
    def __init__(self, name: str, max_points: int, project_root: str):
        super().__init__(name, max_points, project_root)

        self.__coverage_full_path = os.path.join(project_root, COVERAGE_PATH)

    def run(self) -> float:
        """
        Run the coverage check on the project.

        Returns the score from the coverage check.
        """
        logger.log(VERBOSE, "Running %s", self.name)

        is_coverage_run_okay = self.__coverage_run()

        if not is_coverage_run_okay:
            return 0.0

        coverage_report_result = self.__coverage_report()

        if coverage_report_result is None:
            return 0.0

        return self.__translate_score(coverage_report_result)

    def __translate_score(self, coverage_score: float) -> float:
        """
        The coverage score is a percentage of the amount of lines covered in the project.
        The number is between 0 and max_points.
        """
        return coverage_score

    def __coverage_run(self):
        """
        Run the coverage tool on the project.
        """
        command = [self.__coverage_full_path] + COVERAGE_RUN_ARGS + COVERAGE_RUN_PYTEST_ARGS
        output = subprocess.run(command, check=False, capture_output=True)

        if output.returncode != 0:
            logger.error("Coverage run failed: %s", output.stderr)
            return False

        return True

    def __coverage_report(self):
        """
        Generate a report from the coverage tool.
        """
        command = [self.__coverage_full_path] + COVERAGE_REPORT_ARGS
        output = subprocess.run(command, check=False, capture_output=True)

        if output.returncode != 0:
            logger.error("Coverage report failed: %s", output.stderr)
            return None

        return int(output.stdout)
