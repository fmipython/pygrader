"""
Module containing the requirements.txt check.
It checks if requirements.txt exists in the project root.
"""

import logging
import os

from pathlib import Path

from grader.checks.abstract_check import ScoredCheck, ScoredCheckResult
from grader.utils.constants import REQUIREMENTS_FILENAME, PYPROJECT_FILENAME
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
        self.__pyproject_path = os.path.join(self._project_root, PYPROJECT_FILENAME)

    def run(self) -> ScoredCheckResult:
        """
        Run the requirements check on the project.
        Check if requirements.txt exists in the project root - the score is either 0 or full points.
        :return: The score from the requirements.txt check
        :rtype: float
        """
        self._pre_run()

        requirements = Path(self.__requirements_path)
        pyproject = Path(self.__pyproject_path)

        files_to_search = [requirements, pyproject]

        is_one_of_files_present = any(file_path.exists() for file_path in files_to_search)

        score = int(is_one_of_files_present) * self.max_points

        if pyproject.exists():
            pass

        return ScoredCheckResult(self.name, score, "", "", self.max_points)
