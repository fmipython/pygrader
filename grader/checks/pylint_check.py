"""Module containing the pylint check.
It uses the pylint python library directly to run the check.
"""

import logging
import os
import re
from io import StringIO
from typing import Optional

from pylint.reporters.text import TextReporter

import grader.utils.constants as const
from grader.utils import process
from grader.checks.abstract_check import ScoredCheck, CheckError, ScoredCheckResult

# import grader.utils.files as files
from grader.utils import files

logger = logging.getLogger("grader")


class PylintCheck(ScoredCheck):
    """
    The Pylint check class.
    """

    def __init__(
        self,
        name: str,
        project_root: str,
        max_points: int,
        is_venv_required: bool,
        pylintrc_path: Optional[str] = None,
        env_vars: Optional[dict[str, str]] = None,
    ):
        super().__init__(name, max_points, project_root, is_venv_required, env_vars)
        self.__pylint_max_score = 10
        self.__pylintrc_path = pylintrc_path or const.PYLINTRC

    def run(self) -> ScoredCheckResult:
        """
        Run the pylint check on the project.
        First, find all python files in the project, then create a custom reporter (to suppress all output).
        Run the pylint check itself and map the score within the desired bounds.

        :returns: The score from the pylint check.
        :rtype: float
        """
        self._pre_run()

        try:
            pylint_args = files.find_all_python_files(self._project_root)
        except OSError as error:
            logger.error("Error while finding python files: %s", error)
            raise CheckError("Error while finding python files") from error

        logger.debug("Running pylint check on files: %s", pylint_args)
        pylint_args.append("--fail-under=0")

        if os.path.exists(self.__pylintrc_path):
            pylint_args.extend(["--rcfile", self.__pylintrc_path])

        command = [const.PYLINT_PATH] + pylint_args  # Current working directory is set in the process.run method
        try:
            results = process.run(command, current_directory=self._project_root, env_vars=self._env_vars)
        except (OSError, ValueError) as error:
            logger.error("Error while running pylint: %s", error)
            raise CheckError("Error while running pylint") from error

        if results.returncode != 0:
            raise CheckError("Pylint check failed")

        pylint_score = self.__get_pylint_score(results.stdout)

        logger.debug("Pylint score: %s", pylint_score)
        score = self.__translate_score(pylint_score)

        return ScoredCheckResult(self.name, score, self.max_points)

    def __translate_score(self, pylint_score: float) -> float:
        """
        Split the pylint score into regions and assign a score based on the region.
        The amount of regions depends on the max points for the criteria.

        :param pylint_score: The score from pylint to be translated
        :return: The translated score
        """
        if self._max_points == -1:
            raise CheckError("Max points for pylint check is set to -1")

        step = self.__pylint_max_score / (self._max_points + 1)
        steps = [i * step for i in range(self._max_points + 2)]

        regions = list(zip(steps, steps[1:]))

        for score, (start, end) in enumerate(regions):
            if round(start, 2) <= round(pylint_score, 2) < round(end, 2):
                return score

        return self._max_points

    def __get_pylint_score(self, pylint_output: str) -> float:
        """
        Get the score from the pylint output.
        The score is the last value in the output.

        :param pylint_output: The output from the pylint check
        :return: The score from the pylint check
        """
        expression = re.compile(r"[a-zA-Z ]*(\d*.\d*)\/.*")

        for line in pylint_output.strip().split("\n"):
            if "Your code has been rated at" in line:
                match expression.match(line):
                    case re.Match() as match_result:
                        score = match_result.group(1)
                        return float(score)
                    case None:
                        logger.error("Pylint score not found")
                        raise CheckError("Pylint score not found")

        logger.error("Pylint score not found")
        raise CheckError("Pylint score not found")


class PylintCustomReporter(TextReporter):
    """
    Custom reported to suppress all output.
    By default, the pylint library shows everything on the stdout.
    """

    def __init__(self) -> None:
        self.output = StringIO()
        super().__init__(self.output)

    def display_messages(self, layout) -> None:  # type: ignore
        pass

    def display_reports(self, layout) -> None:  # type: ignore
        pass
