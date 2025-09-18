import unittest
from unittest.mock import patch, mock_open, MagicMock

from grader.utils.json_with_templates import load_with_values


class TestJsonWithTemplates(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "${{value}}"}')
    def test_01_successful_substitution(self, _: MagicMock) -> None:
        """
        Test successful substitution of a single placeholder.
        """
        # Arrange
        # (mock_file already set up)

        # Act
        result = load_with_values("dummy.json", value="test")

        # Assert
        self.assertEqual(result, {"key": "test"})

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "${{missing}}"}')
    def test_02_missing_placeholder_value(self, _: MagicMock) -> None:
        """
        Test error raised when a placeholder value is missing.
        """
        # Arrange
        # (mock_file already set up)

        # Act / Assert
        with self.assertRaises(ValueError) as ctx:
            load_with_values("dummy.json", not_missing="test")
        self.assertIn("Missing value for placeholder: missing", str(ctx.exception))

    @patch("builtins.open", new_callable=mock_open, read_data='{"a": "${{x}}", "b": "${{y}}"}')
    def test_04_multiple_placeholders(self, _: MagicMock) -> None:
        """
        Test substitution of multiple placeholders.
        """
        # Arrange
        # (mock_file already set up)

        # Act
        result = load_with_values("dummy.json", x="foo", y="bar")

        # Assert
        self.assertEqual(result, {"a": "foo", "b": "bar"})

    @patch("builtins.open", new_callable=mock_open, read_data='{"num": "${{n}}"}')
    def test_05_non_string_value(self, _: MagicMock) -> None:
        """
        Test substitution with a non-string value.
        """
        # Act
        result = load_with_values("dummy.json", n=123)  # type: ignore

        # Assert
        self.assertEqual(result, {"num": "123"})
