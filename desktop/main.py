"""
Main entry point of the program.
Calls all the checks, and stores their results
"""

from desktop.cli import get_args
from desktop.results_reporter import (
    JSONResultsReporter,
    CSVResultsReporter,
    PlainTextResultsReporter,
    ResultsReporter,
)
from grader.utils.logger import setup_logger
from grader.grader import Grader


def build_reporter(report_format: str) -> ResultsReporter:
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


def run_grader() -> None:
    args = get_args()
    is_suppressing_info = args["report_format"] == "json" or args["report_format"] == "csv" or args["suppress_info"]
    log = setup_logger(args["student_id"], verbosity=args["verbosity"], suppress_info=is_suppressing_info)

    grader = Grader(
        args["student_id"], args["project_root"], args["config"], log, args["keep_venv"], args["skip_venv_creation"]
    )

    checks_results = grader.grade()

    reporter = build_reporter(args["report_format"])

    # TODO - Add output to a file
    reporter.display(checks_results)
