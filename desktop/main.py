"""
Main entry point of the program.

Calls all the checks, and stores their results.
"""

import glob
import os
import shutil
from pathlib import Path

import grader.utils.constants as const
from desktop.cli import get_args
from grader.grader import Grader
from grader.utils.files import is_path_zip, unzip_archive
from grader.utils.logger import setup_logger
from grader.utils.results_reporter import (
    CSVResultsReporter,
    JSONResultsReporter,
    PlainTextResultsReporter,
    ResultsReporter,
)


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


def expand_project_root(pattern: str) -> list[str]:
    """
    Expand project_root into the list of paths to grade.

    Only patterns containing glob metacharacters (``*``, ``?``, ``[``) are treated as globs; a
    pattern with none of these characters is returned as-is. A path containing ``[`` (e.g.
    "[test]") is therefore treated as a glob (a character class), not a literal directory name.
    A glob that matches nothing falls back to the raw pattern, so a bad pattern still surfaces
    InvalidProjectRootError from grade() below instead of silently grading zero projects.

    :param pattern: The CLI project_root argument - a literal path or a glob pattern.
    :return: The list of paths to grade.
    """
    if not any(char in pattern for char in "*?["):
        return [pattern]

    return sorted(glob.glob(pattern)) or [pattern]


def resolve_project_root(path: str) -> str:
    """
    Resolve a single project path or archive to the directory that should be graded.

    :param path: The path to a project directory or a zip archive containing one.
    :return: The path to the directory to grade.
    """
    if not is_path_zip(path):
        return path

    project_root = unzip_archive(path)

    # If the unzipped folder contains only one subfolder (except MACOS subdirectories), use that as the project root
    project_root_dir = Path(project_root)
    subdirs = [
        directory
        for directory in project_root_dir.iterdir()
        if directory.is_dir() and directory.name not in const.IGNORE_DIRS
    ]

    if len(subdirs) == 1:
        project_root = str(subdirs[0])

    return project_root


def run_grader() -> None:
    """Run the grader application."""
    args = get_args()
    is_suppressing_info = args["report_format"] == "json" or args["report_format"] == "csv" or args["suppress_info"]
    log = setup_logger(
        args["student_id"],
        verbosity=args["verbosity"],
        suppress_info=is_suppressing_info,
    )

    matched_paths = expand_project_root(args["project_root"])
    is_batch = len(matched_paths) > 1

    grader = Grader(
        log,
        is_keeping_venv=args["keep_venv"],
        is_skipping_venv_creation=args["skip_venv_creation"],
        config_path=args["config"],
    )

    reporter = build_reporter(args["report_format"])
    verbose = args["verbosity"] >= 1

    for path in matched_paths:
        project_root = resolve_project_root(path)

        # TODO - Think of ways to extract the student ID from the project root path
        # <homework_name>/<student_id>-<student_name>_<number>_assignsubmission_file/<file>.zip
        run_id = Path(path).stem if is_batch else args["student_id"]

        # TODO - Exceptions cause pygrader to completely stop and no cleanup of WORK_DIR
        checks_results = grader.grade(project_root, run_id)

        # TODO - Combine the results of all runs into a single report if is_batch is True
        # TODO - Add output to a file
        reporter.display(checks_results, verbose=verbose)

    if os.path.exists(const.WORK_DIR):
        shutil.rmtree(const.WORK_DIR)
