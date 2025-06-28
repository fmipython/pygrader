import unittest
from unittest.mock import patch
from src.logic import add, subtract, multiply, divide, main_logic


class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(0, 0), 0)

    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract(0, 1), -1)
        self.assertEqual(subtract(-1, -1), 0)

    def test_multiply(self):
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-1, 1), -1)
        self.assertEqual(multiply(0, 5), 0)

    def test_divide(self):
        self.assertEqual(divide(6, 3), 2)
        self.assertEqual(divide(-6, 2), -3)
        with self.assertRaises(ValueError):
            divide(5, 0)


class TestMainFunction(unittest.TestCase):
    @patch("builtins.input", side_effect=["1", "2", "3"])
    @patch("builtins.print")
    def test_main_add(self, mock_print, mock_input):
        main_logic()
        mock_print.assert_any_call("The result is: 5")

    @patch("builtins.input", side_effect=["2", "5", "3"])
    @patch("builtins.print")
    def test_main_subtract(self, mock_print, mock_input):
        main_logic()
        mock_print.assert_any_call("The result is: 2")

    @patch("builtins.input", side_effect=["3", "4", "5"])
    @patch("builtins.print")
    def test_main_multiply(self, mock_print, mock_input):
        main_logic()
        mock_print.assert_any_call("The result is: 20")

    @patch("builtins.input", side_effect=["4", "8", "2"])
    @patch("builtins.print")
    def test_main_divide(self, mock_print, mock_input):
        main_logic()
        mock_print.assert_any_call("The result is: 4.0")

    @patch("builtins.input", side_effect=["4", "5", "0"])
    @patch("builtins.print")
    def test_main_divide_by_zero(self, mock_print, mock_input):
        main_logic()
        self.assertTrue(any("Error: Cannot divide by zero." in str(call) for call in mock_print.call_args_list))

    @patch("builtins.input", side_effect=["5", "1", "2"])
    @patch("builtins.print")
    def test_main_invalid_choice(self, mock_print, mock_input):
        main_logic()
        mock_print.assert_any_call("Invalid input")

    @patch("builtins.input", side_effect=["1", "a", "2"])
    @patch("builtins.print")
    def test_main_invalid_number(self, mock_print, mock_input):
        main_logic()
        self.assertTrue(any("Error:" in str(call) for call in mock_print.call_args_list))


if __name__ == "__main__":
    unittest.main()
