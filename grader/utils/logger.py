import logging

from typing import Optional


def setup_logger(student_id: Optional[str] = None):
    student_id = student_id or "grader"
    logger = logging.getLogger("grader")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(student_id + ".log")],
    )
