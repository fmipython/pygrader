from grader.utils.cli import get_args
from grader.utils.logger import setup_logger
from grader.utils.virtual_environment import VirtualEnvironment
from grader.checks.pylint_check import PylintCheck

if __name__ == "__main__":
    args = get_args()
    logger = setup_logger(args["student_id"], verbosity=args["verbosity"])

    logger.verbose("Python project grader, v0.1")
    logger.debug("Arguments: %s", args)

    scores = []
    with VirtualEnvironment(args["project_root"]) as venv:
        pylint = PylintCheck("pylint", 3, args["project_root"])
        scores.append((pylint.name, pylint.run()))

    for check, score in scores:
        logger.info("Check: %s, Score: %s", check, score)
