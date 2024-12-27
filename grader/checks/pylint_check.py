from io import StringIO

from pylint import lint
from pylint.reporters.text import TextReporter

from grader.checks.abstract_check import AbstractCheck
from grader.utils.files import find_all_python_files


class PylintCheck(AbstractCheck):
    def __init__(self, name: str, max_points: int, project_root: str):
        AbstractCheck.__init__(self, name, max_points, project_root, self.__translate_score)
        self.__pylint_max_score = 10

    def run(self) -> float:
        # TODO - Check if running outside of the virtual environment of the project is okay
        results = lint.Run(find_all_python_files(self._project_root), reporter=PylintCustomReporter(), exit=False)
        pylint_score = results.linter.stats.global_note

        return self._scores_mapping(pylint_score)

    def __translate_score(self, pylint_score: float) -> float:
        """
        Split the pylint score into regions and assign a score based on the region.
        The amount of regions depends on the max points for the criteria.

        :param pylint_score: The score from pylint to be translated
        :return: The translated score
        """
        step = self.__pylint_max_score / self._max_points
        steps = [i * step for i in range(self._max_points + 1)]

        regions = list(zip(steps, steps[1:]))

        for score, (start, end) in enumerate(regions, start=1):
            if start <= pylint_score < end:
                return score


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
