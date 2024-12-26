from abc import ABC, abstractmethod


class AbstractCheck(ABC):
    def __init__(self, name: str, max_points: int, project_root: str):
        self._name = name
        self._max_points = max_points
        self._project_root = project_root

    @abstractmethod
    def run(self) -> float:
        pass
