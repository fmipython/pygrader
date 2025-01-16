"""
Module containing the requirements.txt check.
It checks if requirements.txt exists in the project root.
"""

import logging
import os

from grader.checks.abstract_check import AbstractCheck
from grader.utils.constants import REQUIREMENTS_FILENAME

logger = logging.getLogger("grader")


class RequirementsCheck(AbstractCheck):
    """
    The requirements.txt check class.
    """

    def __init__(self, name: str, max_points: int, project_root: str):
        super().__init__(name, max_points, project_root)

        self.__requirements_path = os.path.join(self._project_root, REQUIREMENTS_FILENAME)

    def run(self) -> float:
        """
        Run the requirements check on the project.
        Check if requirements.txt exists in the project root - the score is either 0 or full points.

        Returns the score from the requirements.txt check
        """
        super().run()

        return int(os.path.exists(self.__requirements_path)) * self.max_points
