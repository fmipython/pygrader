"""
Main entry point of the program.
Calls all the checks, and stores their results
"""

from logging import Logger
import os
import sys
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
from grader.utils.cli import get_args
from grader.utils.config import load_config
from grader.utils.files import get_tests_directory_name
from grader.utils.logger import setup_logger
from grader.utils.results_reporter import (
    JSONResultsReporter,
    CSVResultsReporter,
    PlainTextResultsReporter,
    ResultsReporter,
)
from grader.utils.virtual_environment import VirtualEnvironment


class Grader:
    def __init__(
        self,
        student_id: str,
        project_root: str,
        config_path: str,
        logger: Logger,
        is_keeping_venv: bool = False,
        is_skipping_venv_creation: bool = False,
    ):
        self.__student_id = student_id
        self.__logger = logger

        self.__logger.info("Python project grader, %s", const.VERSION)
        self.__is_keeping_venv = is_keeping_venv
        self.__is_skipping_venv_creation = is_skipping_venv_creation
        try:
            self.__config = load_config(config_path)
        except FileNotFoundError as exc:
            self.__logger.error("Configuration file not found")
            self.__logger.debug("Exception: %s", exc)
            sys.exit(1)

        if student_id is not None:
            self.__logger.info("Running checks for student %s", student_id)

        self.__logger.debug("Project root: %s", project_root)
        self.__logger.debug("Configuration file: %s", config_path)
        self.__logger.debug("Keeping virtual environment: %s", is_keeping_venv)
        self.__logger.debug("Skipping virtual environment creation: %s", is_skipping_venv_creation)

        self.__project_root = project_root
        if not os.path.exists(self.__project_root):
            self.__logger.error("Project root directory does not exist")
            sys.exit(1)

    def grade(self) -> list[CheckResult]:
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

        return scores

    def __run_check(self, check: AbstractCheck) -> CheckResult:
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


def build_reporter(report_format) -> ResultsReporter:
    """
    Build a results reporter based on the specified report format.

    :param report_format: The format of the report (e.g., "json", "csv", "text").
    :return: An instance of a ResultsReporter subclass.
    """
    match report_format:
        case "json":
            return JSONResultsReporter()
        case "csv":
            return CSVResultsReporter()
        case "text":
            return PlainTextResultsReporter()
        case _:
            return PlainTextResultsReporter()


if __name__ == "__main__":
    args = get_args()
    is_suppressing_info = args["report_format"] == "json" or args["report_format"] == "csv" or args["suppress_info"]
    logger = setup_logger(args["student_id"], verbosity=args["verbosity"], suppress_info=is_suppressing_info)

    grader = Grader(
        args["student_id"], args["project_root"], args["config"], logger, args["keep_venv"], args["skip_venv_creation"]
    )

    checks_results = grader.grade()

    reporter = build_reporter(args["report_format"])

    # TODO - Add output to a file
    reporter.display(checks_results)
