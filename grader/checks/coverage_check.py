"""
Module containing the unit test code coverage check.
"""

import logging

from grader.checks.abstract_check import ScoredCheck, CheckError, ScoredCheckResult
from grader.utils.constants import (
    COVERAGE_PATH,
    COVERAGE_RUN_ARGS,
    COVERAGE_RUN_PYTEST_ARGS,
    COVERAGE_REPORT_ARGS,
    COVERAGE_REPORT_ARGS_NO_FORMAT,
)
from grader.utils.files import find_all_source_files
from grader.utils.process import run
from typing import Optional

logger = logging.getLogger("grader")


class CoverageCheck(ScoredCheck):
    """
    The Coverage check class.
    """

    def __init__(
        self,
        name: str,
        project_root: str,
        max_points: int,
        is_venv_required: bool,
        env_vars: Optional[dict[str, str]] = None,
    ):
        super().__init__(name, max_points, project_root, is_venv_required, env_vars)

        self.__coverage_full_path = COVERAGE_PATH

    def run(self) -> ScoredCheckResult:
        """
        Run the coverage check on the project.

        :returns: The score from the coverage check.
        :rtype: float
        """
        self._pre_run()

        self.__coverage_run()

        coverage_report_result = self.__coverage_report()

        if coverage_report_result is None:
            raise CheckError("Coverage report generation failed")

        score = self.__translate_score(coverage_report_result)
        return ScoredCheckResult(self.name, score, "", "", self.max_points)

    def __translate_score(self, coverage_score: float) -> float:
        """
        Split the coverage score into regions and assign a score based on the region.
        The amount of regions depends on the max points for the criteria.

        :param coverage_score: The score from pylint to be translated
        :return: The translated score
        """

        if self._max_points == -1:
            raise CheckError("Max points for coverage check is set to -1")

        step = 100 / (self._max_points + 1)
        steps = [i * step for i in range(self._max_points + 2)]

        regions = list(zip(steps, steps[1:]))

        for score, (start, end) in enumerate(regions):
            if round(start, 2) <= round(coverage_score, 2) < round(end, 2):
                return score

        return self._max_points

    def __coverage_run(self) -> None:
        """
        Run the coverage tool on the project.
        """
        command = [self.__coverage_full_path] + COVERAGE_RUN_ARGS + COVERAGE_RUN_PYTEST_ARGS

        try:
            output = run(command, current_directory=self._project_root, env_vars=self.env_vars)
        except (OSError, ValueError) as e:
            logger.error("Coverage run failed: %s", e)
            raise CheckError("Coverage run failed") from e

        if output.returncode != 0:
            logger.error("Coverage run failed")
            raise CheckError("Coverage run failed")

    def __coverage_report(self) -> int:
        """
        Generate a report from the coverage tool.
        """
        source_files = find_all_source_files(self._project_root)

        try:
            command = [self.__coverage_full_path] + COVERAGE_REPORT_ARGS_NO_FORMAT + source_files
            _ = run(command, current_directory=self._project_root, env_vars=self.env_vars)
        except (OSError, ValueError) as e:
            logger.error("Coverage report (no format) failed: %s", e)
            raise CheckError("Coverage report (no format) failed") from e

        try:
            command = [self.__coverage_full_path] + COVERAGE_REPORT_ARGS + source_files
            output = run(command, current_directory=self._project_root, env_vars=self.env_vars)
        except (OSError, ValueError) as e:
            logger.error("Coverage report (with format) failed: %s", e)
            raise CheckError("Coverage report (with format) failed") from e

        if output.returncode != 0:
            logger.error("Coverage report failed")
            raise CheckError("Coverage report failed")

        return int(output.stdout)
