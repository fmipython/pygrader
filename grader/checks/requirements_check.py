"""
Module containing the requirements.txt check.
It checks if requirements.txt exists in the project root.
"""

import logging
import os

from grader.checks.abstract_check import ScoredCheck, ScoredCheckResult
from grader.utils.constants import REQUIREMENTS_FILENAME
from typing import Optional

logger = logging.getLogger("grader")


class RequirementsCheck(ScoredCheck):
    """
    The requirements.txt check class.
    """

    def __init__(
        self,
        name: str,
        project_root: str,
        max_points: int,
        is_venv_required: bool,
        env_vars: Optional[dict[str, str]] = None,
    ):
        super().__init__(name, max_points, project_root, is_venv_required, env_vars)

        self.__requirements_path = os.path.join(self._project_root, REQUIREMENTS_FILENAME)

    def run(self) -> ScoredCheckResult:
        """
        Run the requirements check on the project.
        Check if requirements.txt exists in the project root - the score is either 0 or full points.
        :return: The score from the requirements.txt check
        :rtype: float
        """
        self._pre_run()

        score = int(os.path.exists(self.__requirements_path)) * self.max_points

        return ScoredCheckResult(self.name, score, self.max_points)
