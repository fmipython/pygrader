import logging

from typing import Optional

VERBOSE = 15
logging.addLevelName(VERBOSE, "VERBOSE")


# Add a custom logging method to the logger class
def verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kwargs)


def setup_logger(student_id: Optional[str] = None, verbosity: int = 0) -> logging.Logger:
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
