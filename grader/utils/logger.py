"""
Module containing the logger setup function and the custom VERBOSE level.
"""

import logging
import sys

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
    logger.setLevel(logging.DEBUG)  # Set the logger to the lowest level to capture all messages

    match verbosity:
        case 0:
            console_level = logging.INFO
        case 1:
            console_level = VERBOSE
        case 2:
            console_level = logging.DEBUG
        case _:
            console_level = logging.DEBUG

    if verbosity > 0:
        console_format = "%(asctime)s - %(levelname)s - %(message)s"
    else:
        console_format = "%(message)s"

    file_format = "%(asctime)s - %(levelname)s - %(message)s"

    console_handler = logging.StreamHandler(stream=sys.stdout)  # Change to stdout
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(console_format))

    file_handler = logging.FileHandler(student_id + ".log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(file_format))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
