import logging

from typing import Optional

VERBOSE = 15
logging.addLevelName(VERBOSE, "VERBOSE")


# Add a custom logging method to the logger class
def verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kwargs)


def setup_logger(student_id: Optional[str] = None, verbosity: int = 2) -> logging.Logger:
    student_id = student_id or "grader"
    logging.Logger.verbose = verbose
    logger = logging.getLogger("grader")

    match verbosity:
        case 0:
            level = logging.DEBUG
        case 1:
            level = VERBOSE
        case _:
            level = logging.INFO

    if verbosity < 2:
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
