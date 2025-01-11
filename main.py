"""
Main entry point of the program.
Calls all the checks, and stores their results
"""

from grader.checks.coverage_check import CoverageCheck
from grader.checks.pylint_check import PylintCheck
from grader.checks.type_hints_check import TypeHintsCheck
from grader.checks.requirements_check import RequirementsCheck
from grader.utils.cli import get_args
from grader.utils.logger import setup_logger, VERBOSE
from grader.utils.virtual_environment import VirtualEnvironment

if __name__ == "__main__":
    args = get_args()
    logger = setup_logger(args["student_id"], verbosity=args["verbosity"])

    logger.log(VERBOSE, "Python project grader, v0.1")
    logger.debug("Arguments: %s", args)

    scores = []

    requirements = RequirementsCheck("requirements.txt", 1, args["project_root"])
    scores.append((requirements.name, requirements.run()))

    pylint = PylintCheck("pylint", 3, args["project_root"])
    scores.append((pylint.name, pylint.run()))

    type_hints = TypeHintsCheck("type_hints", 2, args["project_root"])
    scores.append((type_hints.name, type_hints.run()))

    with VirtualEnvironment(args["project_root"]) as venv:
        coverage = CoverageCheck("coverage", 5, args["project_root"])
        scores.append((coverage.name, coverage.run()))

    for check, score in scores:
        logger.info("Check: %s, Score: %s", check, score)
