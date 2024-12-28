from abc import ABC, abstractmethod
from typing import Callable


class AbstractCheck(ABC):
    def __init__(self, name: str, max_points: int, project_root: str, scores_mapping: Callable[[float], float]):
        self._name = name
        self._max_points = max_points
        self._project_root = project_root
        self._scores_mapping = scores_mapping

        # TODO - Add a check if running inside a virtual environment

    @abstractmethod
    def run(self) -> float:
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def max_points(self) -> int:
        return self._max_points
