"""Tests for JSON template utilities."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from grader.utils.json_with_templates import load_with_values


class TestJsonWithTemplates:
    """Tests for the load_with_values function."""

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "${{value}}"}')
    def test_01_successful_substitution(self, _: MagicMock) -> None:
        """Test successful substitution of a single placeholder."""
        # Arrange
        # (mock_file already set up)

        # Act
        result = load_with_values("dummy.json", value="test")

        # Assert
        assert result == {"key": "test"}

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "${{missing}}"}')
    def test_02_missing_placeholder_value(self, _: MagicMock) -> None:
        """Test error raised when a placeholder value is missing."""
        # Arrange
        # (mock_file already set up)

        # Act / Assert
        with pytest.raises(ValueError) as ctx:
            load_with_values("dummy.json", not_missing="test")
        assert "Missing value for placeholder: missing" in str(ctx.value)

    @patch("builtins.open", new_callable=mock_open, read_data='{"a": "${{x}}", "b": "${{y}}"}')
    def test_04_multiple_placeholders(self, _: MagicMock) -> None:
        """Test substitution of multiple placeholders."""
        # Arrange
        # (mock_file already set up)

        # Act
        result = load_with_values("dummy.json", x="foo", y="bar")

        # Assert
        assert result == {"a": "foo", "b": "bar"}

    @patch("builtins.open", new_callable=mock_open, read_data='{"num": "${{n}}"}')
    def test_05_non_string_value(self, _: MagicMock) -> None:
        """Test substitution with a non-string value."""
        # Act
        result = load_with_values("dummy.json", n=123)  # type: ignore

        # Assert
        assert result == {"num": "123"}
