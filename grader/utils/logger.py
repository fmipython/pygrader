import logging

from typing import Optional


def setup_logger(student_id: Optional[str] = None, debug_mode: bool = False) -> logging.Logger:
    student_id = student_id or "grader"
    logger = logging.getLogger("grader")

    level = logging.DEBUG if debug_mode else logging.INFO

    if debug_mode:
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
    else:
        log_format = "%(levelname)s - %(message)s"

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
