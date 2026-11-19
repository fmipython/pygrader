"""Unit tests for the AbstractCheck class in the abstract_check module."""

from unittest.mock import MagicMock, call, patch

import pytest

from grader.checks.abstract_check import AbstractCheck, ScoredCheck
from grader.exceptions import CheckError
from grader.models.check_result import CheckResult, ScoredCheckResult


class DummyCheck(AbstractCheck):
    """Dummy check class for testing."""

    def run(self) -> CheckResult[int]:
        """Run the dummy check."""
        super()._pre_run()
        return CheckResult("dummy", 0, "", "")


class TestAbstractCheck:
    """Test cases for the AbstractCheck class."""

    def test_01_run_without_venv_when_required(self) -> None:
        """Test that running the check without a virtual environment when it is required raises a RuntimeError."""
        # Arrange
        check = DummyCheck("dummy", "dummy", is_venv_required=True)

        # Act & Assert
        with pytest.raises(CheckError):
            check.run()

    def test_02_assets_default_to_empty_list(self) -> None:
        """Test that a check built without assets exposes an empty assets list."""
        # Arrange & Act
        check = DummyCheck("dummy", "dummy")

        # Assert
        assert check.assets == []

    @patch("grader.checks.abstract_check.Resource")
    def test_03_assets_are_wrapped_in_resource(self, mocked_resource: MagicMock) -> None:
        """Test that each asset source is wrapped in a Resource object."""
        # Arrange
        sources = ["local.txt", "cove://fmi-python/asset"]

        # Act
        check = DummyCheck("dummy", "dummy", assets=sources)

        # Assert
        mocked_resource.assert_has_calls([call(source) for source in sources])
        assert check.assets == [mocked_resource.return_value, mocked_resource.return_value]


class DummyScoredCheck(ScoredCheck):
    """Dummy scored check class for testing the score translation."""

    def run(self) -> ScoredCheckResult:
        """Run the dummy scored check."""
        return ScoredCheckResult(self.name, 0, "", "", self.max_points)


class TestScoredCheckTranslateScore:
    """Test cases for ScoredCheck._translate_score."""

    @pytest.mark.parametrize(
        ("max_points", "value", "expected"),
        [
            # Integer max points: 3 regions of ~33.33, awarding 0, 1, 2
            (2, 0, 0),
            (2, 33.33, 1),
            (2, 50, 1),
            (2, 66.67, 2),
            (2, 100, 2),
            # 1.5 -> 3 regions of ~33.33, awarding 0, 0.75, 1.5
            (1.5, 0, 0),
            (1.5, 33.32, 0),
            (1.5, 33.33, 0.75),
            (1.5, 66.67, 1.5),
            (1.5, 100, 1.5),
            # 0.5 -> 2 regions of 50, awarding 0, 0.5
            (0.5, 49.99, 0),
            (0.5, 50, 0.5),
            (0.5, 100, 0.5),
            # 2.5 -> 4 regions of 25, awarding 0, 0.83, 1.67, 2.5
            (2.5, 24.99, 0),
            (2.5, 25, 0.83),
            (2.5, 50, 1.67),
            (2.5, 75, 2.5),
            (2.5, 100, 2.5),
        ],
    )
    def test_01_translate_score(self, max_points: float, value: float, expected: float) -> None:
        """Test that a raw value is translated into the expected score for integer and float max points."""
        check = DummyScoredCheck("dummy", max_points, "dummy")

        assert check._translate_score(value, 100) == expected  # pylint: disable=protected-access

    def test_02_translate_score_integer_max_returns_int(self) -> None:
        """Test that integer max points keep producing integer scores."""
        check = DummyScoredCheck("dummy", 2, "dummy")

        assert isinstance(check._translate_score(50, 100), int)  # pylint: disable=protected-access

    def test_03_translate_score_negative_max(self) -> None:
        """Test that max points of -1 raise a CheckError."""
        check = DummyScoredCheck("dummy", -1, "dummy")

        with pytest.raises(CheckError):
            check._translate_score(50, 100)  # pylint: disable=protected-access
