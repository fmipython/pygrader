"""Main entry point of the program."""

import sys

from desktop.main import run_grader
from grader.exceptions import GraderError

if __name__ == "__main__":
    try:
        rc = run_grader()
        sys.exit(rc)
    except GraderError:
        sys.exit(1)
