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
from desktop.utils import extract_student_id_from_path
from grader.exceptions import GraderError
from grader.grader import Grader
from grader.utils.files import is_path_zip, unzip_archive
from grader.utils.logger import setup_logger
from grader.utils.results_reporter import (
    CSVResultsReporter,
    JSONResultsReporter,
    PlainTextResultsReporter,
    ResultsReporter,
)


def build_reporter(report_format: str, is_verbose: bool) -> ResultsReporter:
    """
    Build a results reporter based on the specified report format.

    :param report_format: The format of the report (e.g., "json", "csv", "text").
    :return: An instance of a ResultsReporter subclass.
    """
    match report_format:
        case "json":
            return JSONResultsReporter(is_verbose)
        case "csv":
            return CSVResultsReporter(is_verbose)
        case "text":
            return PlainTextResultsReporter(is_verbose)
        case _:
            return PlainTextResultsReporter(is_verbose)


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

    matched_paths = expand_project_root(args["project_root"])
    is_batch = len(matched_paths) > 1

    logger = setup_logger(
        args["student_id"] if not is_batch else None,
        verbosity=args["verbosity"],
        suppress_info=is_suppressing_info,
    )

    grader = Grader(
        logger,
        is_keeping_venv=args["keep_venv"],
        is_skipping_venv_creation=args["skip_venv_creation"],
        config_path=args["config"],
        selected_checks=args["checks"],
    )

    reporter = build_reporter(args["report_format"], is_verbose=args["verbosity"] >= 1)

    for path in matched_paths:
        project_root = resolve_project_root(path)

        run_id: str = extract_student_id_from_path(path) if is_batch else args["student_id"]

        try:
            grade = grader.grade(project_root, run_id)

        except GraderError:
            logger.error("Grading failed for project %s", project_root)
            continue

        reporter.add_result(grade)

    # TODO - Add output to a file
    print(reporter.to_string())

    if os.path.exists(const.WORK_DIR):
        shutil.rmtree(const.WORK_DIR)
