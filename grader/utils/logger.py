import logging

from typing import Optional


def setup_logger(student_id: Optional[str] = None):
    student_id = student_id or "grader"
    logger = logging.getLogger("grader")
    logging.basicConfig(filename=student_id + ".log", level=logging.DEBUG)
