"""Unit tests for the AbstractCheck class in the abstract_check module."""

from unittest.mock import MagicMock, call, patch

import pytest

from grader.checks.abstract_check import AbstractCheck
from grader.exceptions import CheckError
from grader.models.check_result import CheckResult


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
