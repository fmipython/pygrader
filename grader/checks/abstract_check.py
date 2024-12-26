from abc import ABC, abstractmethod


class AbstractCheck(ABC):
    def __init__(self, name: str, max_points: int):
        self._name = name
        self._max_points = max_points

    @abstractmethod
    def run(self) -> float:
        pass
