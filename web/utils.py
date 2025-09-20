from multiprocessing import Queue

import pandas as pd

from grader.utils.logger import setup_logger
from grader.grader import Grader
from grader.checks.abstract_check import ScoredCheckResult, NonScoredCheckResult, CheckResult
from desktop.results_reporter import result_to_json  # TODO - This should be moved


def run_grader(conn: Queue) -> None:
    student_id = "student123"
    log = setup_logger(student_id)

    project_root = "staging/project"
    config_path = "config/full_single_point.json"

    grader = Grader(student_id, project_root, config_path, log)

    results = grader.grade()

    conn.put(results)


def convert_result(check_result: CheckResult) -> pd.DataFrame:
    return pd.DataFrame([__convert_result(result) for result in check_result])


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


# def grade() -> str:
#     conn: Queue = Queue()
#     thread = Process(target=run_grader, args=(conn,))

#     thread.start()
#     thread.join()

#     return conn.get()
