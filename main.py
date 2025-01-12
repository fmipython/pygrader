"""
Main entry point of the program.
Calls all the checks, and stores their results
"""

import grader.utils.constants as const

from grader.checks.coverage_check import CoverageCheck
from grader.checks.pylint_check import PylintCheck
from grader.checks.type_hints_check import TypeHintsCheck
from grader.checks.requirements_check import RequirementsCheck
from grader.utils.cli import get_args
from grader.utils.files import get_tests_directory_name
from grader.utils.logger import setup_logger
from grader.utils.virtual_environment import VirtualEnvironment

if __name__ == "__main__":
    args = get_args()
    logger = setup_logger(args["student_id"], verbosity=args["verbosity"])

    logger.info("Python project grader, %s", const.VERSION)
    logger.info("Running checks for student %s", args["student_id"])
    logger.debug("Arguments: %s", args)

    tests_directory = get_tests_directory_name(args["project_root"])
    if tests_directory is None:
        logger.warning("No tests directory found in the project directory. Either it is missing or named differently.")

    scores = []

    requirements = RequirementsCheck("requirements.txt", 1, args["project_root"])
    scores.append((requirements.name, requirements.run(), requirements.max_points))

    pylint = PylintCheck("pylint", 3, args["project_root"])
    scores.append((pylint.name, pylint.run(), pylint.max_points))

    type_hints = TypeHintsCheck("type_hints", 2, args["project_root"])
    scores.append((type_hints.name, type_hints.run(), type_hints.max_points))

    with VirtualEnvironment(args["project_root"]) as venv:
        coverage = CoverageCheck("coverage", 5, args["project_root"])
        scores.append((coverage.name, coverage.run(), coverage.max_points))

    for check, score, max_score in scores:
        logger.info("Check: %s, Score: %s/%s", check, score, max_score)
