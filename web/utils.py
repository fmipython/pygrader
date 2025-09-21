import datetime
from multiprocessing import Queue

import pandas as pd

from grader.utils.logger import setup_logger
from grader.grader import Grader
from grader.checks.abstract_check import ScoredCheckResult, NonScoredCheckResult, CheckResult


def run_grader(conn: Queue, run_id: str) -> None:
    """
    Run the grading process and send results back through the connection.
    :param conn: The multiprocessing queue to send results through.
    :param run_id: A unique identifier for the grading run.
    """
    log = setup_logger(run_id)

    project_root = "project"
    config_path = "config/full_single_point.json"

    grader = Grader(run_id, project_root, config_path, log)

    results = grader.grade()

    conn.put(results)


def convert_results(check_results: list[CheckResult]) -> pd.DataFrame:
    """
    Convert a list of CheckResult objects into a pandas DataFrame.

    :param check_results: The list of CheckResult objects to convert.
    :return: A pandas DataFrame representing the check results.
    """
    return pd.DataFrame([__convert_result(result) for result in check_results])


def __convert_result(check_result: CheckResult) -> dict:
    match check_result:
        case ScoredCheckResult(name, score, max_score):
            return {
                "name": name,
                "score": score,
                "max_score": max_score,
            }
        case NonScoredCheckResult(name, result):
            return {
                "name": name,
                "result": result,
            }
        case _:
            raise ValueError("Unknown CheckResult type")


def generate_run_id() -> str:
    """
    Generate a unique run ID based on the current date and time.
    :return: A string representing the run ID.
    """
    now = datetime.datetime.now()
    return "run" + now.strftime("%y%m%d%H%M")
