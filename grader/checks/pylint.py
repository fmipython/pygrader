import subprocess

from .abstract_check import AbstractCheck
from ..utils.files import find_all_python_files


class PylintCheck(AbstractCheck):
    def __init__(self, name: str, max_points: int, project_root: str):
        AbstractCheck.__init__(self, name, max_points, project_root)

    def run(self) -> float:
        command = "pylint"
        args = [" ".join(find_all_python_files(self._project_root))]

        print(args)
        process = subprocess.run([command, *args], check=False, capture_output=True)
        pass
