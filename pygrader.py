"""
Main entry point of the program.
"""

import sys
from desktop.main import run_grader
from grader.grader import GraderError


if __name__ == "__main__":
    try:
        run_grader()
    except GraderError:
        sys.exit(1)
