"""
Module containing the check for running tests against the submitted code.
"""

from collections import defaultdict
from typing import Optional
import logging
import os

from grader.checks.abstract_check import CheckError, ScoredCheck, ScoredCheckResult
from grader.utils.constants import PYTEST_ARGS, PYTEST_PATH, PYTEST_ROOT_DIR_ARG
from grader.utils.external_resources import is_resource_remote, download_file_from_url

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
        self.__default_test_score = default_test_score
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
        self._pre_run()

        pytest_stdout = self.__pytest_run()

        passed, failed = self.__parse_pytest_output(pytest_stdout)
        total_amount = len(passed) + len(failed)

        passed_tests_score, _, total_score = self.__calculate_score(passed, failed)

        if total_score > self.max_points:
            raise CheckError("Total score exceeds maximum points")

        logger.info("Passed tests: %d/%d", len(passed), total_amount)
        logger.info("Failed tests: %d/%d", len(failed), total_amount)

        return ScoredCheckResult(self.name, passed_tests_score, self.max_points)

    def __pytest_run(self) -> str:
        """
        Run pytest on the specified test files.

        :returns: The stdout output from the pytest run.
        :rtype: str
        :raises CheckError: If pytest fails to execute or encounters an error.
        """
        if os.path.isabs(self._project_root):
            pytest_root_dir = PYTEST_ROOT_DIR_ARG.format(self._project_root)
        else:
            pytest_root_dir = PYTEST_ROOT_DIR_ARG.format(os.path.join(os.getcwd(), self._project_root))
        command = [PYTEST_PATH] + PYTEST_ARGS + [pytest_root_dir] + self.__tests_path

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

    def __parse_pytest_output(self, output: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """
        Parse the output from pytest to determine passed and failed tests.

        :param output: The output from the pytest run.
        :returns: A tuple containing two lists - passed tests and failed tests.
        :rtype: tuple[list[str], list[str]]
        """
        passed_tests = []
        failed_tests = []

        for line in output.splitlines():
            items = line.split("::")

            if line.startswith("PASSED"):
                class_name = items[-2]
                test_name = items[-1]
                passed_tests.append((class_name, test_name))
            elif line.startswith("FAILED"):
                class_name = items[-2]
                test_name = items[-1]
                failed_tests.append((class_name, test_name))

        return passed_tests, failed_tests

    def _pre_run(self) -> None:
        super()._pre_run()

        self.__tests_path = [
            path if not is_resource_remote(path) else download_file_from_url(path) for path in self.__tests_path
        ]

    def __calculate_score(
        self, passed_tests: list[tuple[str, str]], failed_tests: list[tuple[str, str]]
    ) -> tuple[float, float, float]:
        """
        Calculate the total score based on passed and failed tests.

        :param passed_tests: A list of names of passed tests.
        :param failed_tests: A list of names of failed tests.
        :returns: The total score from the tests.
        :rtype: float
        """

        passed_tests_score = sum(
            self.__score_test(passed_test_class, passed_test_name)
            for passed_test_class, passed_test_name in passed_tests
        )

        failed_tests_score = sum(
            self.__score_test(failed_test_class, failed_test_name)
            for failed_test_class, failed_test_name in failed_tests
        )

        total_score = passed_tests_score + failed_tests_score

        return passed_tests_score, failed_tests_score, total_score

    def __score_test(self, test_class: str, test_name: str) -> float:
        """
        Score an individual test based on its class and name.

        If the class is scored, take it's score
        If the test is scored, take it's score
        If neither is scored, take the default score
        However, if both the class and the test itself are scored, test score takes precedences

        :param test_class: The name of the test class.
        :param test_name: The name of the test.
        :return: The score for the test.
        """

        if test_class in self.__test_score_mapping and test_name in self.__test_score_mapping:
            score = self.__test_score_mapping[test_name]
        elif test_class in self.__test_score_mapping and test_name not in self.__test_score_mapping:
            score = self.__test_score_mapping[test_class]
        elif test_class not in self.__test_score_mapping and test_name in self.__test_score_mapping:
            score = self.__test_score_mapping[test_name]
        else:
            score = self.__default_test_score

        logger.debug("Test %s::%s scored %.2f", test_class, test_name, score)
        return score
