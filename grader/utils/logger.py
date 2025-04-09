"""
Module containing the logger setup function and the custom VERBOSE level.
"""

import logging
from logging.handlers import RotatingFileHandler
import sys
from typing import Optional

VERBOSE = 15
MAX_LOG_FILES = 20
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

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

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

    # Console handler setup
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter(console_format))

    # Rotating file handler setup
    file_handler = RotatingFileHandler(
        filename=f"{student_id}.log",
        maxBytes=0,  # No size limit
        backupCount=MAX_LOG_FILES - 1,  # -1 because the main file counts as one
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(file_format))
    # Force a rollover on startup to create a new log file each time
    file_handler.doRollover()

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
