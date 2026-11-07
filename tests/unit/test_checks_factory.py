"""Unit tests for the checks_factory module in the grader package."""

from unittest.mock import MagicMock, patch

import pytest

from grader.checks.checks_factory import create_checks
from grader.checks.complexity_check import ComplexityCheck
from grader.exceptions import InvalidCheckError, InvalidConfigError


class TestChecksFactory:
    """Unit tests for the create_checks function in the checks_factory module."""

    def test_01_no_checks_in_config(self) -> None:
        """Test that an empty config raises an InvalidConfigError."""
        # Arrange
        config: dict[str, str] = {}
        project_root = "test_project"

        # Act
        with pytest.raises(InvalidConfigError):
            create_checks(config, project_root)

    def test_02_invalid_check_configuration(self) -> None:
        """Test that an invalid check configuration raises an InvalidConfigError."""
        # Arrange
        config: dict[str, list[dict[str, str]]] = {"checks": [{}]}
        project_root = "test_project"

        # Act
        with pytest.raises(InvalidConfigError):
            create_checks(config, project_root)

    def test_03_max_points_missing(self) -> None:
        """Test that a missing max_points field raises an InvalidConfigError."""
        # Arrange
        config = {"checks": [{"name": "coverage"}]}
        project_root = "test_project"

        # Act
        with pytest.raises(InvalidConfigError):
            create_checks(config, project_root)

    def test_04_name_missing(self) -> None:
        """Test that a missing name field raises an InvalidConfigError."""
        # Arrange
        config = {"checks": [{"max_points": 10}]}
        project_root = "test_project"

        # Act
        with pytest.raises(InvalidConfigError):
            create_checks(config, project_root)

    def test_05_unknown_check_name(self) -> None:
        """Test that an unknown check name raises an InvalidCheckError."""
        # Arrange
        config = {"checks": [{"name": "unknown", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        with pytest.raises(InvalidCheckError):
            create_checks(config, project_root)

    def test_05b_complexity_check_is_created_with_its_options(self) -> None:
        """Test that the complexity check is built from its config, without max_points."""
        config = {"checks": [{"name": "complexity", "is_venv_required": False, "max_complexity": 7}]}

        non_venv_checks, venv_checks = create_checks(config, "test_project")

        assert not venv_checks
        assert isinstance(non_venv_checks[0], ComplexityCheck)

    def test_06_venv_required(self) -> None:
        """Test that checks requiring a virtual environment are separated correctly."""
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": True}]}
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 0
        assert len(venv_checks) == 1

    def test_07_venv_not_required(self) -> None:
        """Test that checks not requiring a virtual environment are separated correctly."""
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 1
        assert len(venv_checks) == 0

    def test_08_is_venv_required_not_present(self) -> None:
        """Test that when is_venv_required is not present, an InvalidConfigError is raised."""
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10}]}
        project_root = "test_project"

        # Act
        with pytest.raises(InvalidConfigError):
            _ = create_checks(config, project_root)

    def test_09_environment_variables_global_only(self) -> None:
        """Test that global environment variables are passed to checks."""
        # Arrange
        config = {
            "environment": {"variables": {"GLOBAL_VAR": "global_value"}},
            "checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}],
        }
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 1
        check = non_venv_checks[0]
        assert check.env_vars is not None

        # To keep the linter happy
        if check.env_vars is not None:
            assert "GLOBAL_VAR" in check.env_vars
            assert check.env_vars["GLOBAL_VAR"] == "global_value"

    def test_10_environment_variables_check_specific(self) -> None:
        """Test that check-specific environment variables are passed to checks."""
        # Arrange
        config = {
            "checks": [
                {
                    "name": "coverage",
                    "max_points": 10,
                    "is_venv_required": False,
                    "environment": {"variables": {"CHECK_VAR": "check_value"}},
                }
            ]
        }
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 1
        check = non_venv_checks[0]
        assert check.env_vars is not None

        # To keep the linter happy
        if check.env_vars is not None:
            assert "CHECK_VAR" in check.env_vars
            assert check.env_vars["CHECK_VAR"] == "check_value"

    def test_11_environment_variables_merge_priority(self) -> None:
        """Test that check-specific environment variables override global ones."""
        # Arrange
        config = {
            "environment": {"variables": {"API_KEY": "global_key", "GLOBAL_VAR": "global_value"}},
            "checks": [
                {
                    "name": "coverage",
                    "max_points": 10,
                    "is_venv_required": False,
                    "environment": {"variables": {"API_KEY": "check_key", "CHECK_VAR": "check_value"}},
                }
            ],
        }
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 1
        check = non_venv_checks[0]
        assert check.env_vars is not None

        # To keep the linter happy
        if check.env_vars is not None:
            # Check that check-specific API_KEY overrides global
            assert check.env_vars["API_KEY"] == "check_key"
            # Check that global variable is still present
            assert check.env_vars["GLOBAL_VAR"] == "global_value"
            # Check that check-specific variable is present
            assert check.env_vars["CHECK_VAR"] == "check_value"

    @patch("os.environ")
    def test_12_environment_variables_none_when_not_defined(self, existing_env: MagicMock) -> None:
        """Test that env_vars is None when no environment variables are defined."""
        # Arrange
        existing_env.return_value = {}
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 1
        check = non_venv_checks[0]
        assert check.env_vars == {}

    def test_13_selected_checks_filters_subset(self) -> None:
        """Test that selected_checks limits the built checks to the matching subset."""
        # Arrange
        config = {
            "checks": [
                {"name": "requirements", "max_points": 10, "is_venv_required": False},
                {"name": "pylint", "max_points": 10, "is_venv_required": True},
                {"name": "coverage", "max_points": 10, "is_venv_required": True},
            ]
        }
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root, selected_checks=["requirements", "pylint"])

        # Assert
        assert [check.name for check in non_venv_checks] == ["requirements"]
        assert [check.name for check in venv_checks] == ["pylint"]

    def test_14_selected_checks_none_runs_everything(self) -> None:
        """Test that selected_checks=None keeps the current full-run behavior."""
        # Arrange
        config = {
            "checks": [
                {"name": "requirements", "max_points": 10, "is_venv_required": False},
                {"name": "pylint", "max_points": 10, "is_venv_required": True},
            ]
        }
        project_root = "test_project"

        # Act
        non_venv_checks, venv_checks = create_checks(config, project_root, selected_checks=None)

        # Assert
        assert len(non_venv_checks) == 1
        assert len(venv_checks) == 1

    def test_15_selected_checks_unknown_name_raises(self) -> None:
        """Test that requesting an unknown check name raises InvalidCheckError."""
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act & Assert
        with pytest.raises(InvalidCheckError):
            create_checks(config, project_root, selected_checks=["pylintt"])

    @patch("grader.checks.abstract_check.Resource")
    def test_16_assets_are_loaded_as_resources(self, mocked_resource: MagicMock) -> None:
        """Test that a check's "assets" config entries are converted to Resource objects."""
        # Arrange
        config = {
            "checks": [
                {
                    "name": "coverage",
                    "max_points": 10,
                    "is_venv_required": False,
                    "assets": ["local_asset.txt", "cove://fmi-python/asset"],
                }
            ]
        }
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 1
        check = non_venv_checks[0]
        assert check.assets == [mocked_resource.return_value, mocked_resource.return_value]

    def test_17_assets_default_to_empty_list(self) -> None:
        """Test that a check built without an "assets" key exposes an empty assets list."""
        # Arrange
        config = {"checks": [{"name": "coverage", "max_points": 10, "is_venv_required": False}]}
        project_root = "test_project"

        # Act
        non_venv_checks, _ = create_checks(config, project_root)

        # Assert
        assert len(non_venv_checks) == 1
        assert non_venv_checks[0].assets == []
