"""Unit tests for the reporter classes in the results_reporter module."""

import json
import unittest

from grader.models.check_result import CheckResult, NonScoredCheckResult, ScoredCheckResult
from grader.models.grading_result import GradingResult
from grader.utils.results_reporter import CSVResultsReporter, JSONResultsReporter, PlainTextResultsReporter


class TestJSONResultsReporter(unittest.TestCase):
    """Test cases for the JSONResultsReporter class."""

    def setUp(self) -> None:
        """Set up the JSONResultsReporter instance for testing."""
        self.reporter = JSONResultsReporter()
        return super().setUp()

    def test_01_no_results_returns_empty_list(self) -> None:
        """Test that to_string returns an empty JSON array when no results were added."""
        # Act
        actual = json.loads(self.reporter.to_string())

        # Assert
        self.assertEqual(actual, [])

    def test_02_single_run_non_verbose(self) -> None:
        """Test that a non-verbose run serializes scored and non-scored checks without info/error."""
        # Arrange
        scored = ScoredCheckResult("pylint", 1.5, "Info about pylint", "Some error", 2)
        non_scored = NonScoredCheckResult("structure", True, "Info about structure", "")
        self.reporter.add_result(GradingResult("student_1", 1.5, 2, [scored, non_scored]))

        expected = [
            {
                "run_id": "student_1",
                "total_score": 1.5,
                "max_score": 2,
                "results": [
                    {"name": "pylint", "score": 1.5, "max_score": 2},
                    {"name": "structure", "result": True},
                ],
            }
        ]

        # Act
        actual = json.loads(self.reporter.to_string())

        # Assert
        self.assertEqual(actual, expected)

    def test_03_verbose_includes_info_and_error(self) -> None:
        """Test that a verbose run includes the info and error fields for each check."""
        # Arrange
        self.reporter = JSONResultsReporter(is_verbose=True)
        scored = ScoredCheckResult("pylint", 1.5, "Info about pylint", "Some error", 2)
        self.reporter.add_result(GradingResult("student_1", 1.5, 2, [scored]))

        expected = [
            {
                "run_id": "student_1",
                "total_score": 1.5,
                "max_score": 2,
                "results": [
                    {
                        "name": "pylint",
                        "info": "Info about pylint",
                        "error": "Some error",
                        "score": 1.5,
                        "max_score": 2,
                    }
                ],
            }
        ]

        # Act
        actual = json.loads(self.reporter.to_string())

        # Assert
        self.assertEqual(actual, expected)

    def test_04_multiple_runs_are_all_included(self) -> None:
        """Test that adding multiple GradingResults includes one entry per run in the output."""
        # Arrange
        self.reporter.add_result(GradingResult("student_1", 2, 2, [ScoredCheckResult("pylint", 2, "", "", 2)]))
        self.reporter.add_result(GradingResult("student_2", 0, 2, [ScoredCheckResult("pylint", 0, "", "", 2)]))

        # Act
        actual = json.loads(self.reporter.to_string())

        # Assert
        self.assertEqual([run["run_id"] for run in actual], ["student_1", "student_2"])

    def test_05_unknown_check_result_type_raises_value_error(self) -> None:
        """Test that a CheckResult that is neither scored nor non-scored raises a ValueError."""
        # Arrange
        unknown_result = CheckResult("mystery", 1, "", "")
        self.reporter.add_result(GradingResult("student_1", 0, 0, [unknown_result]))

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.reporter.to_string()
        self.assertIn("mystery", str(context.exception))


class TestCSVResultsReporter(unittest.TestCase):
    """Test cases for the CSVResultsReporter class."""

    def setUp(self) -> None:
        """Set up the CSVResultsReporter instance for testing."""
        self.reporter = CSVResultsReporter()
        return super().setUp()

    def test_01_no_results_returns_only_header(self) -> None:
        """Test that to_string returns only the header row when no results were added."""
        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, "Run ID,Check,Score,Max Score\n")

    def test_02_single_run_non_verbose(self) -> None:
        """Test that a non-verbose run emits one row per check without info/error columns."""
        # Arrange
        scored = ScoredCheckResult("pylint", 1.5, "Info about pylint", "Some error", 2)
        non_scored = NonScoredCheckResult("structure", True, "Info about structure", "")
        self.reporter.add_result(GradingResult("student_1", 1.5, 2, [scored, non_scored]))

        expected = "Run ID,Check,Score,Max Score\nstudent_1,pylint,1.5,2\nstudent_1,structure,True,NaN\n"

        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, expected)

    def test_03_verbose_includes_info_and_error_columns(self) -> None:
        """Test that a verbose run includes the info and error columns for each check."""
        # Arrange
        self.reporter = CSVResultsReporter(is_verbose=True)
        scored = ScoredCheckResult("pylint", 1.5, "Info about pylint", "Some error", 2)
        non_scored = NonScoredCheckResult("structure", True, "Info about structure", "Some error")
        self.reporter.add_result(GradingResult("student_1", 1.5, 2, [scored, non_scored]))

        expected = (
            "Run ID,Check,Score,Max Score,Info,Error\n"
            "student_1,pylint,1.5,2,Info about pylint,Some error\n"
            "student_1,structure,True,NaN,Info about structure,Some error\n"
        )

        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, expected)

    def test_04_multiple_runs_include_run_id_per_row(self) -> None:
        """Test that rows from different runs are each tagged with their own run id."""
        # Arrange
        self.reporter.add_result(GradingResult("student_1", 2, 2, [ScoredCheckResult("pylint", 2, "", "", 2)]))
        self.reporter.add_result(GradingResult("student_2", 0, 2, [ScoredCheckResult("pylint", 0, "", "", 2)]))

        expected = "Run ID,Check,Score,Max Score\nstudent_1,pylint,2,2\nstudent_2,pylint,0,2\n"

        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, expected)

    def test_05_unknown_check_result_type_raises_value_error(self) -> None:
        """Test that a CheckResult that is neither scored nor non-scored raises a ValueError."""
        # Arrange
        unknown_result = CheckResult("mystery", 1, "", "")
        self.reporter.add_result(GradingResult("student_1", 0, 0, [unknown_result]))

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.reporter.to_string()
        self.assertIn("mystery", str(context.exception))


class TestPlainTextResultsReporter(unittest.TestCase):
    """Test cases for the PlainTextResultsReporter class."""

    def setUp(self) -> None:
        """Set up the PlainTextResultsReporter instance for testing."""
        self.reporter = PlainTextResultsReporter()
        return super().setUp()

    def test_01_no_results_returns_empty_string(self) -> None:
        """Test that to_string returns a single newline when no results were added."""
        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, "\n")

    def test_02_single_run_non_verbose(self) -> None:
        """Test that a non-verbose run emits one line per check plus a total line, without info/error."""
        # Arrange
        scored = ScoredCheckResult("pylint", 1.5, "Info about pylint", "Some error", 2)
        non_scored = NonScoredCheckResult("structure", True, "Info about structure", "")
        self.reporter.add_result(GradingResult("student_1", 1.5, 2, [scored, non_scored]))

        expected = (
            "Run ID: student_1, Check: pylint, Score: 1.5/2\n"
            "Run ID: student_1, Check: structure, Result: True\n"
            "Run ID: student_1, Total Score: 1.5/2\n"
        )

        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, expected)

    def test_03_verbose_includes_info_and_error_when_present(self) -> None:
        """Test that a verbose run appends Info/Error segments when they are non-empty."""
        # Arrange
        self.reporter = PlainTextResultsReporter(is_verbose=True)
        scored = ScoredCheckResult("pylint", 1.5, "Info about pylint", "Some error", 2)
        self.reporter.add_result(GradingResult("student_1", 1.5, 2, [scored]))

        expected = (
            "Run ID: student_1, Check: pylint, Score: 1.5/2. Info: Info about pylint. Error: Some error\n"
            "Run ID: student_1, Total Score: 1.5/2\n"
        )

        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, expected)

    def test_04_verbose_omits_info_and_error_when_empty(self) -> None:
        """Test that a verbose run does not append Info/Error segments when they are empty strings."""
        # Arrange
        self.reporter = PlainTextResultsReporter(is_verbose=True)
        non_scored = NonScoredCheckResult("structure", True, "", "")
        self.reporter.add_result(GradingResult("student_1", 0, 0, [non_scored]))

        expected = "Run ID: student_1, Check: structure, Result: True\nRun ID: student_1, Total Score: 0/0\n"

        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, expected)

    def test_05_multiple_runs_each_get_their_own_total_line(self) -> None:
        """Test that each added run produces its own group of check lines and total line."""
        # Arrange
        self.reporter.add_result(GradingResult("student_1", 2, 2, [ScoredCheckResult("pylint", 2, "", "", 2)]))
        self.reporter.add_result(GradingResult("student_2", 0, 2, [ScoredCheckResult("pylint", 0, "", "", 2)]))

        expected = (
            "Run ID: student_1, Check: pylint, Score: 2/2\n"
            "Run ID: student_1, Total Score: 2/2\n"
            "Run ID: student_2, Check: pylint, Score: 0/2\n"
            "Run ID: student_2, Total Score: 0/2\n"
        )

        # Act
        actual = self.reporter.to_string()

        # Assert
        self.assertEqual(actual, expected)

    def test_06_unknown_check_result_type_raises_value_error(self) -> None:
        """Test that a CheckResult that is neither scored nor non-scored raises a ValueError."""
        # Arrange
        unknown_result = CheckResult("mystery", 1, "", "")
        self.reporter.add_result(GradingResult("student_1", 0, 0, [unknown_result]))

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.reporter.to_string()
        self.assertIn("mystery", str(context.exception))


class TestResultsReporterAddResult(unittest.TestCase):
    """Test cases for the shared ResultsReporter.add_result behavior."""

    def setUp(self) -> None:
        """Set up a concrete ResultsReporter instance for testing, since the base class is abstract."""
        self.reporter = PlainTextResultsReporter()
        return super().setUp()

    def test_01_add_result_appends_to_results(self) -> None:
        """Test that add_result appends the given GradingResult to the internal results list."""
        # Arrange
        first_result = GradingResult("student_1", 1, 2, [])
        second_result = GradingResult("student_2", 2, 2, [])

        # Act
        self.reporter.add_result(first_result)
        self.reporter.add_result(second_result)

        # Assert
        self.assertEqual(self.reporter._results, [first_result, second_result])  # pylint: disable=protected-access
