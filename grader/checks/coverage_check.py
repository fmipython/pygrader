"""
Module containing the unit test code coverage check.
"""
import logging

from grader.checks.abstract_check import AbstractCheck
from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")


class CoverageCheck(AbstractCheck):
    """
    The Coverage check class.
    """
    def __init__(self, name: str, max_points: int, project_root: str):
        super().__init__(name, max_points, project_root)

    def run(self) -> float:
        """
        Run the coverage check on the project.

        Returns the score from the coverage check.
        """
        logger.log(VERBOSE, "Running %s", self.name)

        # TODO - Implement the coverage check

        return 0.0