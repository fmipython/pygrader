import logging
import os

from grader.checks.abstract_check import AbstractCheck
from grader.utils.constants import REQUIREMENTS_FILENAME

logger = logging.getLogger("grader")


class RequirementsCheck(AbstractCheck):
    def __init__(self, name: str, max_points: int, project_root: str):
        super().__init__(name, max_points, project_root)

        self.__requirements_path = os.path.join(self._project_root, REQUIREMENTS_FILENAME)

    def run(self) -> float:
        logger.verbose(f"Running {self.name}")

        return int(os.path.exists(self.__requirements_path)) * self.max_points
