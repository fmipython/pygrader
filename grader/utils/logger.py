import logging

from typing import Optional


def setup_logger(student_id: Optional[str] = None, debug_mode: bool = False) -> logging.Logger:
    student_id = student_id or "grader"
    logger = logging.getLogger("grader")
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(student_id + ".log"),
        ],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    return logger
