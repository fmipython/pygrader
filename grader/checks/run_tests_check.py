"""
Module containing the check for running tests against the submitted code.
"""

from collections import defaultdict
import logging
import os
from typing import Optional

from grader.checks.abstract_check import CheckError, ScoredCheck, ScoredCheckResult
from grader.utils.constants import PYTEST_ARGS, PYTEST_PATH, PYTEST_ROOT_DIR_ARG

# from grader.utils.process import run, extend_env_variable
from grader.utils import process

logger = logging.getLogger("grader")


class RunTestsCheck(ScoredCheck):
    """
    The tests check class.
    This class is responsible for running tests on the submitted code and scoring the results.
    """

    def __init__(
        self,
        name: str,
        project_root: str,
        max_points: int,
        is_venv_required: bool,
        tests_path: list[str],
        default_test_score: float = 0.0,
        test_score_mapping: Optional[dict[str, float]] = None,
    ):
        """
        Initialize the TestsCheck class.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param max_points: The maximum points for the check.
        :param is_venv_required: Whether a virtual environment is required.
        :param tests_path: A list of paths to the test files.
        :param default_test_score: The default score for tests not explicitly mapped.
        :param test_score_mapping: A mapping of test names to their respective scores.
        """
        super().__init__(name, max_points, project_root, is_venv_required)
        self.__pytest_full_path = os.path.join(project_root, PYTEST_PATH)
        self.__test_score_mapping = defaultdict(lambda: default_test_score)

        if test_score_mapping is not None:
            for test_name, score in test_score_mapping.items():
                self.__test_score_mapping[test_name] = score

        self.__tests_path = tests_path

    def run(self) -> ScoredCheckResult:
        """
        Run the tests check on the project.

        This method executes the tests using pytest, parses the results, and calculates the score.

        :returns: The score from the tests check.
        :rtype: float
        :raises CheckError: If the total score exceeds the maximum points.
        """
        super().run()

        pytest_stdout = self.__pytest_run()

        passed, failed = self.__parse_pytest_output(pytest_stdout)
        total_amount = len(passed) + len(failed)

        passed_tests_score = sum(self.__test_score_mapping[test] for test in passed)
        failed_tests_score = sum(self.__test_score_mapping[test] for test in failed)
        total_score = passed_tests_score + failed_tests_score

        if total_score > self.max_points:
            raise CheckError("Total score exceeds maximum points")

        logger.info("Passed tests: %d/%d", len(passed), total_amount)
        logger.info("Failed tests: %d/%d", len(failed), total_amount)

        return ScoredCheckResult(self.name, passed_tests_score, self.max_points)

    def __pytest_run(self):
        """
        Run pytest on the specified test files.

        :returns: The stdout output from the pytest run.
        :rtype: str
        :raises CheckError: If pytest fails to execute or encounters an error.
        """
        command = (
            [self.__pytest_full_path]
            + PYTEST_ARGS
            + [PYTEST_ROOT_DIR_ARG.format(self._project_root)]
            + self.__tests_path
        )

        try:
            output = process.run(
                command,
                current_directory=self._project_root,
                env_vars=process.extend_env_variable("PYTHONPATH", self._project_root),
            )
        except (OSError, ValueError) as e:
            logger.error("Tests run failed: %s", e)
            raise CheckError("Tests run failed") from e

        if output.returncode >= 2:  # 0: OK, 1: Tests failed
            logger.error("Tests run failed")
            raise CheckError("Tests run failed")

        return output.stdout

    def __parse_pytest_output(self, output: str) -> tuple[list[str], list[str]]:
        """
        Parse the output from pytest to determine passed and failed tests.

        :param output: The output from the pytest run.
        :returns: A tuple containing two lists - passed tests and failed tests.
        :rtype: tuple[list[str], list[str]]
        """
        passed_tests = []
        failed_tests = []

        for line in output.splitlines():
            if line.startswith("PASSED"):
                test_name = line.split("::")[-1]
                passed_tests.append(test_name)
            elif line.startswith("FAILED"):
                test_name = line.split("::")[-1]
                failed_tests.append(test_name)

        return passed_tests, failed_tests
