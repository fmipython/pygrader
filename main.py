"""
Main entry point of the program.
Calls all the checks, and stores their results
"""

from logging import Logger
import os
import sys
import grader.utils.constants as const

from grader.checks.abstract_check import AbstractCheck, CheckError, ScoredCheck, NonScoredCheck
from grader.checks.checks_factory import create_checks
from grader.utils.cli import get_args
from grader.utils.config import load_config
from grader.utils.files import get_tests_directory_name
from grader.utils.logger import setup_logger
from grader.utils.virtual_environment import VirtualEnvironment


class Grader:
    def __init__(self, student_id: str, project_root: str, config_path: str, logger: Logger):
        self.__student_id = student_id
        self.__logger = logger

        self.__logger.info("Python project grader, %s", const.VERSION)

        try:
            self.__config = load_config(config_path)
        except FileNotFoundError as exc:
            self.__logger.error("Configuration file not found")
            self.__logger.debug("Exception: %s", exc)
            sys.exit(1)

        if student_id is not None:
            self.__logger.info("Running checks for student %s", student_id)
        self.__logger.debug("Arguments: %s", args)

        self.__project_root = project_root
        if not os.path.exists(self.__project_root):
            self.__logger.error("Project root directory does not exist")
            sys.exit(1)

    def grade(self):
        tests_directory = get_tests_directory_name(self.__project_root)
        if tests_directory is None:
            self.__logger.warning(
                "No tests directory found in the project directory. Either it is missing or named differently."
            )

        scores = []
        non_scored_checks_results = []

        non_venv_checks, venv_checks = create_checks(self.__config, self.__project_root)

        for check in non_venv_checks:
            check_result = self.__run_check(scores, non_scored_checks_results, check)
            match check:
                case ScoredCheck():
                    scores.append((check.name, check_result, check.max_points))
                case NonScoredCheck():
                    non_scored_checks_results.append((check.name, check_result))

        if args["skip_venv_creation"]:
            return scores, []

        with VirtualEnvironment(self.__project_root) as venv:
            for check in venv_checks:
                check_result = self.__run_check(scores, non_scored_checks_results, check)
                match check:
                    case ScoredCheck():
                        scores.append((check.name, check_result, check.max_points))
                    case NonScoredCheck():
                        non_scored_checks_results.append((check.name, check_result))

        return scores, non_scored_checks_results

    def __run_check(self, check: AbstractCheck):
        try:
            check_result = check.run()
        except CheckError as error:
            self.__logger.error("Check failed: %s", error)
            check_result = 0.0

        return check_result


if __name__ == "__main__":
    args = get_args()
    logger = setup_logger(args["student_id"], verbosity=args["verbosity"])

    grader = Grader(args["student_id"], args["project_root"], args["config"], logger)

    scored_checks_result, non_scored_checks_result = grader.grade()

    for name, score, max_score in scored_checks_result:
        logger.info("Check: %s, Score: %s/%s", name, score, max_score)

    for name, result in non_scored_checks_result:
        logger.info("Check: %s, Result: %s", name, result)
