"""Unit tests for the ComplexityCheck class in the complexity_check module."""

from unittest.mock import MagicMock, patch

import pytest

from grader.checks.complexity_check import ComplexityCheck
from grader.exceptions import CheckError, InvalidConfigError
from grader.models.check_result import NonScoredCheckResult


def _file_complexity(*functions: tuple[str, int, int]) -> MagicMock:
    """Build a fake complexipy file result from (name, line_start, complexity) tuples."""
    result = MagicMock()
    result.functions = [MagicMock(line_start=line, complexity=complexity) for _, line, complexity in functions]
    for mock_function, (name, _, _) in zip(result.functions, functions):
        mock_function.name = name
    return result


@pytest.fixture(name="check")
def fixture_check() -> ComplexityCheck:
    """Create a complexity check with a threshold of 10."""
    return ComplexityCheck("complexity", "sample_dir", max_complexity=10)


@patch("complexipy.file_complexity")
@patch("grader.utils.files.find_all_source_files")
def test_01_all_functions_within_threshold(
    mock_find: MagicMock, mock_complexity: MagicMock, check: ComplexityCheck
) -> None:
    """Verify that the check passes when no function exceeds the threshold."""
    mock_find.return_value = ["a.py"]
    mock_complexity.return_value = _file_complexity(("foo", 1, 10), ("bar", 5, 2))

    result = check.run()

    assert result == NonScoredCheckResult("complexity", True, "All functions are within complexity 10", "")


@patch("complexipy.file_complexity")
@patch("grader.utils.files.find_all_source_files")
def test_02_function_above_threshold(mock_find: MagicMock, mock_complexity: MagicMock, check: ComplexityCheck) -> None:
    """Verify that the check fails and names the offending functions."""
    mock_find.return_value = ["a.py", "b.py"]
    mock_complexity.side_effect = [_file_complexity(("foo", 1, 11)), _file_complexity(("bar", 7, 3))]

    result = check.run()

    assert result == NonScoredCheckResult("complexity", False, "Functions above complexity 10: a.py:1 foo (11)", "")


@patch("grader.utils.files.find_all_source_files")
def test_03_no_source_files(mock_find: MagicMock, check: ComplexityCheck) -> None:
    """Verify that a project without source files passes."""
    mock_find.return_value = []

    assert check.run().result is True


@patch("grader.utils.files.find_all_source_files")
def test_04_finding_files_fails(mock_find: MagicMock, check: ComplexityCheck) -> None:
    """Verify that an OSError while finding files is reported as a CheckError."""
    mock_find.side_effect = OSError("boom")

    with pytest.raises(CheckError):
        check.run()


@patch("complexipy.file_complexity")
@patch("grader.utils.files.find_all_source_files")
def test_05_unparsable_file_fails_but_others_are_analysed(
    mock_find: MagicMock, mock_complexity: MagicMock, check: ComplexityCheck
) -> None:
    """Verify that a file complexipy cannot parse fails the check without hiding the other files."""
    mock_find.return_value = ["bad.py", "a.py"]
    mock_complexity.side_effect = [ValueError("bad syntax"), _file_complexity(("foo", 1, 11))]

    result = check.run()

    assert result == NonScoredCheckResult(
        "complexity", False, "Functions above complexity 10: a.py:1 foo (11). Could not analyse: bad.py", ""
    )


@pytest.mark.parametrize("value", [0, -1, "15", True, 1.5])
def test_06_invalid_max_complexity(value: object) -> None:
    """Verify that a non-positive-integer threshold is rejected."""
    with pytest.raises(InvalidConfigError):
        ComplexityCheck("complexity", "sample_dir", max_complexity=value)  # type: ignore[arg-type]
