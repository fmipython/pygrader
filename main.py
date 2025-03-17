"""
Main entry point of the program.
Calls all the checks, and stores their results
"""

import os
import sys
import grader.utils.constants as const

from grader.checks.abstract_check import CheckError, ScoredCheck
from grader.checks.checks_factory import create_checks
from grader.utils.cli import get_args
from grader.utils.config import load_config
from grader.utils.files import get_tests_directory_name
from grader.utils.logger import setup_logger
from grader.utils.virtual_environment import VirtualEnvironment

if __name__ == "__main__":
    args = get_args()
    student_id = args["student_id"]
    logger = setup_logger(student_id, verbosity=args["verbosity"])

    logger.info("Python project grader, %s", const.VERSION)

    try:
        config = load_config(args["config"])
    except FileNotFoundError as exc:
        logger.error("Configuration file not found")
        logger.debug("Exception: %s", exc)
        sys.exit(1)

    if student_id is not None:
        logger.info("Running checks for student %s", student_id)
    logger.debug("Arguments: %s", args)

    project_root = args["project_root"]

    if not os.path.exists(project_root):
        logger.error("Project root directory does not exist")
        sys.exit(1)

    tests_directory = get_tests_directory_name(project_root)
    if tests_directory is None:
        logger.warning("No tests directory found in the project directory. Either it is missing or named differently.")

    scores = []
    non_venv_checks, venv_checks = create_checks(config, project_root)

    for check in non_venv_checks:
        try:
            check_result = check.run()
        except CheckError as error:
            logger.error("Check failed: %s", error)
        else:
            if isinstance(check, ScoredCheck):
                scores.append((check.name, check_result, check.max_points))

    # TODO - Not the best way to do this
    if not args["skip_venv_creation"]:
        with VirtualEnvironment(project_root) as venv:
            for check in venv_checks:
                try:
                    check_result = check.run()
                except CheckError as error:
                    logger.error("Check failed: %s", error)
                    check_result = 0.0
                else:
                    if isinstance(check, ScoredCheck):
                        scores.append((check.name, check_result, check.max_points))

    for name, score, max_score in scores:
        logger.info("Check: %s, Score: %s/%s", name, score, max_score)
