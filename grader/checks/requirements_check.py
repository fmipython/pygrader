"""
Module containing the requirements.txt check.

It checks if requirements.txt exists in the project root.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from grader.checks.abstract_check import ScoredCheck, ScoredCheckResult
from grader.utils.constants import PYPROJECT_FILENAME, REQUIREMENTS_FILENAME
from grader.utils.virtual_environment import VirtualEnvironment, VirtualEnvironmentError

logger = logging.getLogger("grader")


class RequirementsCheck(ScoredCheck):
    """The requirements.txt check class."""

    def __init__(
        self,
        name: str,
        project_root: str,
        max_points: int,
        is_venv_required: bool,
        is_checking_install: bool = False,
        env_vars: Optional[dict[str, str]] = None,
    ):
        """
        Initialize the requirements check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param max_points: The maximum points this check can award.
        :param is_venv_required: Whether a virtual environment is required.
        :param is_checking_install: Whether to check if dependencies can be installed.
        :param env_vars: Optional environment variables for the check.
        """
        super().__init__(name, max_points, project_root, is_venv_required, env_vars)

        self.__requirements_path = os.path.join(self._project_root, REQUIREMENTS_FILENAME)
        self.__pyproject_path = os.path.join(self._project_root, PYPROJECT_FILENAME)
        self.__is_checking_install = is_checking_install

    def run(self) -> ScoredCheckResult:
        """
        Run the requirements check on the project.

        Check if requirements.txt exists in the project root - the score is either 0 or full points.
        :return: The score from the requirements.txt check
        :rtype: float.
        """
        self._pre_run()

        requirements = Path(self.__requirements_path)
        pyproject = Path(self.__pyproject_path)

        files_to_search = [requirements, pyproject]

        is_one_of_files_present = any(file_path.exists() for file_path in files_to_search)

        score = int(is_one_of_files_present) * self.max_points

        info = ""
        if not is_one_of_files_present:
            info = "requirements.txt or pyproject.toml not found"

        if self.__is_checking_install and is_one_of_files_present:
            try:
                with VirtualEnvironment(self._project_root, is_keeping_existing_venv=True):
                    # Context manager automatically handles setup() and teardown()
                    pass
            except VirtualEnvironmentError as e:
                return ScoredCheckResult(self.name, 0, "", str(e), self.max_points)

        return ScoredCheckResult(self.name, score, info, "", self.max_points)
