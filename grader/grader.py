"""
Module containing the Grader class.
"""

from logging import Logger
import os
import shutil
import grader.utils.constants as const

from grader.checks.abstract_check import (
    AbstractCheck,
    CheckError,
    NonScoredCheckResult,
    CheckResult,
    ScoredCheckResult,
    ScoredCheck,
    NonScoredCheck,
)

from grader.checks.checks_factory import create_checks
from grader.utils.config import load_config, InvalidConfigError
from grader.utils.files import get_tests_directory_name
from grader.utils.virtual_environment import VirtualEnvironment


class Grader:
    """
    Main grader class that orchestrates the grading process.
    """

    def __init__(
        self,
        student_id: str,
        project_root: str,
        config_path: str,
        logger: Logger,
        is_keeping_venv: bool = False,
        is_skipping_venv_creation: bool = False,
    ):
        self.__logger = logger

        self.__logger.info("Python project grader, %s", const.VERSION)
        self.__is_keeping_venv = is_keeping_venv
        self.__is_skipping_venv_creation = is_skipping_venv_creation
        try:
            self.__config = load_config(config_path)
        except InvalidConfigError as exc:
            self.__logger.error("Error with the configuration file")
            self.__logger.exception(exc)
            raise GraderError("Could not load configuration file") from exc

        if student_id is not None:
            self.__logger.info("Running checks for student %s", student_id)

        self.__logger.debug("Project root: %s", project_root)
        self.__logger.debug("Configuration file: %s", config_path)
        self.__logger.debug("Keeping virtual environment: %s", is_keeping_venv)
        self.__logger.debug("Skipping virtual environment creation: %s", is_skipping_venv_creation)
        self.__logger.debug("PYTHONPATH: %s", os.environ.get("PYTHONPATH", "Not set"))

        self.__project_root = project_root
        if not os.path.exists(self.__project_root):
            self.__logger.error("Project root directory does not exist")
            raise GraderError("Project root directory does not exist")

    def grade(self) -> list[CheckResult]:
        """
        Main grader method that runs all checks and returns their results.

        :return: A list of CheckResult objects containing the results of the checks.
        """
        tests_directory = get_tests_directory_name(self.__project_root)
        if tests_directory is None:
            self.__logger.warning(
                "No tests directory found in the project directory. Either it is missing or named differently."
            )

        non_venv_checks, venv_checks = create_checks(self.__config, self.__project_root)

        scores = [self.__run_check(check) for check in non_venv_checks]

        if self.__is_skipping_venv_creation or len(venv_checks) == 0:
            return scores

        with VirtualEnvironment(self.__project_root, self.__is_keeping_venv):
            scores += [self.__run_check(check) for check in venv_checks]

        self.__cleanup()

        return scores

    def __run_check(self, check: AbstractCheck) -> CheckResult:
        """
        Run a single check and return the result.

        :param check: The check to run, which can be either a scored or non-scored check.
        :raises TypeError: If the check is of an unknown type.
        :return: The result of the check.
        """
        try:
            check_result = check.run()
        except CheckError as error:
            self.__logger.error("Check failed: %s", error)

            match check:
                case ScoredCheck():
                    check_result = ScoredCheckResult(check.name, 0, check.max_points)
                case NonScoredCheck():
                    check_result = NonScoredCheckResult(check.name, False)
                case _:
                    raise TypeError(f"Unknown check type: {type(check)}") from error

        return check_result

    def __cleanup(self) -> None:
        """
        Cleanup temporary files created during the grading process.
        This is called at the end of grading to ensure no temporary files are left behind.
        """
        shutil.rmtree(const.TEMP_FILES_DIR, ignore_errors=True)

        coverage_file_full_path = os.path.join(self.__project_root, const.COVERAGE_FILE)
        if os.path.exists(coverage_file_full_path):
            os.remove(coverage_file_full_path)
        shutil.rmtree(os.path.join(self.__project_root, const.PYTEST_CACHE), ignore_errors=True)


class GraderError(Exception):
    """
    Custom exception for grader errors.
    """
