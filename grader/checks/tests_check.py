"""
Module containing the check for running tests against the submitted code.
"""

from collections import defaultdict
import logging
import os
from typing import Optional

from grader.checks.abstract_check import CheckError, ScoredCheck
from grader.utils.constants import PYTEST_ARGS, PYTEST_PATH, PYTEST_ROOT_DIR_ARG
from grader.utils.process import run, extend_env_variable

logger = logging.getLogger("grader")


class TestsCheck(ScoredCheck):
    """
    The tests check class.
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
        super().__init__(name, max_points, project_root, is_venv_required)
        self.__pytest_full_path = os.path.join(project_root, PYTEST_PATH)
        self.__test_score_mapping = defaultdict(lambda: default_test_score)

        if test_score_mapping is not None:
            for test_name, score in test_score_mapping.items():
                self.__test_score_mapping[test_name] = score

        self.__tests_path = tests_path

    def run(self) -> float:
        """
        Run the coverage check on the project.

        :returns: The score from the coverage check.
        :rtype: float
        """
        super().run()

        # return self.__translate_score(coverage_report_result)

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

        return passed_tests_score

    def __pytest_run(self):
        command = (
            [self.__pytest_full_path]
            + PYTEST_ARGS
            + [PYTEST_ROOT_DIR_ARG.format(self._project_root)]
            + self.__tests_path
        )

        try:
            output = run(
                command,
                current_directory=self._project_root,
                env_vars=extend_env_variable("PYTHONPATH", self._project_root),
            )
        except (OSError, ValueError) as e:
            logger.error("Tests run failed: %s", e)
            raise CheckError("Tests run failed") from e

        if output.returncode >= 2:  # 0: OK, 1: Tests failed
            logger.error("Tests run failed")
            raise CheckError("Tests run failed")

        return output.stdout

    def __parse_pytest_output(self, output: str) -> tuple[list[str], list[str]]:
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
