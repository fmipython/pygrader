"""Module containing the Grader class."""

import os
import shutil
from logging import Logger
from typing import Optional

import grader.utils.constants as const
from grader.checks.abstract_check import (
    AbstractCheck,
    CheckResult,
    NonScoredCheck,
    NonScoredCheckResult,
    ScoredCheck,
    ScoredCheckResult,
)
from grader.checks.checks_factory import create_checks
from grader.exceptions import (
    CheckError,
    InvalidCheckError,
    InvalidConfigError,
    InvalidProjectRootError,
    VirtualEnvironmentError,
)
from grader.utils.config import load_config
from grader.utils.logger import setup_logger
from grader.utils.virtual_environment import VirtualEnvironment


class Grader:
    """Main grader class that orchestrates the grading process."""

    def __init__(
        self,
        logger: Optional[Logger] = None,
        config_path: Optional[str] = None,
        is_keeping_venv: bool = False,
        is_skipping_venv_creation: bool = False,
    ):
        """
        Initialize the Grader.

        :param logger: The logger instance for output.
        :param config_path: Optional path to configuration file.
        :param is_keeping_venv: Whether to keep the virtual environment after grading.
        :param is_skipping_venv_creation: Whether to skip virtual environment creation.
        """
        self.__logger = logger or setup_logger()

        self.__logger.info("Python project grader, %s", const.VERSION)
        self.__is_keeping_venv = is_keeping_venv
        self.__is_skipping_venv_creation = is_skipping_venv_creation
        try:
            if config_path is None:
                raise InvalidConfigError("No configuration source provided")

            self.__logger.info("Loading configuration from file: %s", config_path)
            self.__config = load_config(config_path)

            self.__logger.debug(f"Config contents: {self.__config}")
        except InvalidConfigError as exc:
            self.__logger.error("Error with the configuration file")
            self.__logger.exception(exc)
            raise

        self.__logger.debug("Configuration file: %s", config_path)
        self.__logger.debug("Keeping virtual environment: %s", is_keeping_venv)
        self.__logger.debug("Skipping virtual environment creation: %s", is_skipping_venv_creation)
        self.__logger.debug("PYTHONPATH: %s", os.environ.get("PYTHONPATH", "Not set"))

    def grade(self, project_root: str, run_id: Optional[str] = None) -> list[CheckResult]:
        """
        Run all checks against a project and return their results.

        :param project_root: The root directory of the project to grade.
        :param run_id: Optional ID of the current run, used for logging.
        :return: A list of CheckResult objects containing the results of the checks.
        """
        if run_id is not None:
            self.__logger.info("Running checks for student %s", run_id)
        self.__logger.debug("Project root: %s", project_root)

        if not os.path.exists(project_root):
            self.__logger.error("Project root directory does not exist")
            raise InvalidProjectRootError("Project root directory does not exist")

        try:
            scores = self.__run_checks(project_root)
        except (InvalidCheckError, VirtualEnvironmentError) as error:
            self.__logger.error("Grading failed for project %s", project_root)
            self.__logger.exception(error)
            self.__cleanup(project_root)
            raise

        self.__cleanup(project_root)
        return scores

    def __run_checks(self, project_root: str) -> list[CheckResult]:
        """
        Run all checks against a project and return their results.

        :param project_root: The root directory of the project to grade.
        :return: A list of CheckResult objects containing the results of the checks.
        """
        non_venv_checks, venv_checks = create_checks(self.__config, project_root)

        scores = [self.__run_check(check) for check in non_venv_checks]

        if self.__is_skipping_venv_creation or len(venv_checks) == 0:
            return scores

        venv_config = self.__config.get("venv", {})

        with VirtualEnvironment(
            project_root,
            is_keeping_venv_after_run=self.__is_keeping_venv,
            **venv_config,
        ):
            scores += [self.__run_check(check) for check in venv_checks]

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

            # TODO - Pass the information from the exception
            match check:
                case ScoredCheck():
                    check_result = ScoredCheckResult(check.name, 0, "", str(error), check.max_points)
                case NonScoredCheck():
                    check_result = NonScoredCheckResult(check.name, False, "", str(error))
                case _:
                    raise TypeError(f"Unknown check type: {type(check)}") from error

        self.__logger.debug("Check result: %s", check_result)
        return check_result

    def __cleanup(self, project_root: str) -> None:
        """
        Cleanup temporary files created during the grading process.

        This is called at the end of grading to ensure no temporary files are left behind.

        :param project_root: The root directory of the project that was graded.
        """
        shutil.rmtree(const.TEMP_FILES_DIR, ignore_errors=True)

        coverage_file_full_path = os.path.join(project_root, const.COVERAGE_FILE)
        if os.path.exists(coverage_file_full_path):
            os.remove(coverage_file_full_path)
        shutil.rmtree(os.path.join(project_root, const.PYTEST_CACHE), ignore_errors=True)
