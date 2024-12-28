from typing import Callable

from grader.checks.abstract_check import AbstractCheck
from grader.utils.files import find_all_python_files


class TypeHintsCheck(AbstractCheck):
    def __init__(self, name: str, max_points: int, project_root: str, scores_mapping: Callable[[float], float]):
        super().__init__(name, max_points, project_root, scores_mapping)

        self.__mypy_binary = "mypy"
        self.__mypy_config_file = ""

    def run(self) -> float:
        # Gather all files
        files = find_all_python_files(self._project_root)

        # Run mypy on all files

        # Read mypy linecount report

        # Calculate score
        pass
