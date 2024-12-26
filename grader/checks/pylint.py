from .abstract_check import AbstractCheck


class PylintCheck(AbstractCheck):
    def __init__(self, name: str, max_points: int):
        AbstractCheck.__init__(self, name, max_points)

    def run(self) -> float:
        pass
