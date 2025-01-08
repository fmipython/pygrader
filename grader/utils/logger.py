"""
Module containing the logger setup function and the custom VERBOSE level.
"""
import logging

from typing import Optional

VERBOSE = 15
logging.addLevelName(VERBOSE, "VERBOSE")


def setup_logger(student_id: Optional[str] = None, verbosity: int = 0) -> logging.Logger:
    """
    Setup the logger with the given verbosity level and student id

    Args:
        student_id: The id of the student. Defaults to None.
        verbosity: . Defaults to 0.

    Returns:
        logging.Logger: The configured logger object.
    """
    student_id = student_id or "grader"
    logger = logging.getLogger("grader")

    match verbosity:
        case 0:
            level = logging.INFO
        case 1:
            level = VERBOSE
        case 2:
            level = logging.DEBUG
        case _:
            level = logging.DEBUG

    if verbosity > 0:
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
    else:
        log_format = "%(message)s"

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(student_id + ".log"),
        ],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    return logger
