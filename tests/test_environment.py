"""
Unit tests for the environment module in the grader.utils package.
"""

import os
import unittest

from unittest.mock import patch, MagicMock
from grader.utils.environment import merge_environment_variables


class TestEnvironmentMerging(unittest.TestCase):
    """
    Unit tests for the merge_environment_variables function.
    """

    def setUp(self) -> None:
        """Set up test environment."""
        # Save original environment
        self.original_env = dict(os.environ)

    def tearDown(self) -> None:
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_01_both_none_returns_none(self) -> None:
        """
        Test that merging None and None returns an empty dict.
        """
        # Act
        result = merge_environment_variables(None, None)

        # Assert
        self.assertEqual(result, {})

    @patch("os.environ")
    def test_02_both_empty_returns_none(self, existing_env: MagicMock) -> None:
        """
        Test that merging empty dicts returns an empty dict.
        """
        # Arrange
        existing_env.return_value = {}

        # Act
        result = merge_environment_variables({}, {})

        # Assert
        self.assertEqual(result, {})

    def test_03_global_only(self) -> None:
        """
        Test that only global environment variables are merged with system env.
        """
        # Arrange
        os.environ["SYSTEM_VAR"] = "system_value"
        global_env = {"GLOBAL_VAR": "global_value"}

        # Act
        result = merge_environment_variables(global_env, None)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["SYSTEM_VAR"], "system_value")
        self.assertEqual(result["GLOBAL_VAR"], "global_value")

    def test_04_check_only(self) -> None:
        """
        Test that only check-specific environment variables are merged with system env.
        """
        # Arrange
        os.environ["SYSTEM_VAR"] = "system_value"
        check_env = {"CHECK_VAR": "check_value"}

        # Act
        result = merge_environment_variables(None, check_env)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["SYSTEM_VAR"], "system_value")
        self.assertEqual(result["CHECK_VAR"], "check_value")

    def test_05_check_overrides_global(self) -> None:
        """
        Test that check-specific variables override global variables.
        """
        # Arrange
        os.environ["SYSTEM_VAR"] = "system_value"
        global_env = {"API_KEY": "global_key"}
        check_env = {"API_KEY": "check_key"}

        # Act
        result = merge_environment_variables(global_env, check_env)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["API_KEY"], "check_key")

    def test_06_global_overrides_system(self) -> None:
        """
        Test that global variables override system variables.
        """
        # Arrange
        os.environ["API_KEY"] = "system_key"
        global_env = {"API_KEY": "global_key"}

        # Act
        result = merge_environment_variables(global_env, None)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["API_KEY"], "global_key")

    def test_07_check_overrides_system(self) -> None:
        """
        Test that check-specific variables override system variables.
        """
        # Arrange
        os.environ["API_KEY"] = "system_key"
        check_env = {"API_KEY": "check_key"}

        # Act
        result = merge_environment_variables(None, check_env)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["API_KEY"], "check_key")

    def test_08_complete_merge_priority(self) -> None:
        """
        Test complete merging with all three sources (system, global, check).
        Verify priority: check > global > system.
        """
        # Arrange
        os.environ["VAR1"] = "system_1"
        os.environ["VAR2"] = "system_2"
        os.environ["VAR3"] = "system_3"

        global_env = {
            "VAR2": "global_2",
            "VAR3": "global_3",
            "VAR4": "global_4",
        }

        check_env = {
            "VAR3": "check_3",
            "VAR5": "check_5",
        }

        # Act
        result = merge_environment_variables(global_env, check_env)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["VAR1"], "system_1")  # System only
        self.assertEqual(result["VAR2"], "global_2")  # Global overrides system
        self.assertEqual(result["VAR3"], "check_3")  # Check overrides global and system
        self.assertEqual(result["VAR4"], "global_4")  # Global only
        self.assertEqual(result["VAR5"], "check_5")  # Check only


if __name__ == "__main__":
    unittest.main()
