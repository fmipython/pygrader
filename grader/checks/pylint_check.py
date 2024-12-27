import subprocess
from io import StringIO

from pylint import lint
from pylint.reporters.text import TextReporter

from grader.checks.abstract_check import AbstractCheck
from grader.utils.files import find_all_python_files


class PylintCheck(AbstractCheck):
    def __init__(self, name: str, max_points: int, project_root: str):
        AbstractCheck.__init__(self, name, max_points, project_root)

    def run(self) -> float:
        results = lint.Run(find_all_python_files(self._project_root), reporter=PylintCustomReporter(), exit=False)
        pylint_score = results.linter.stats.global_note

        return pylint_score


class PylintCustomReporter(TextReporter):
    """
    Custom reported to suppress all output
    """

    def __init__(self):
        self.output = StringIO()
        super().__init__(self.output)

    def display_messages(self, layout):
        pass

    def display_reports(self, layout):
        pass

    def display_score(self):
        pass
