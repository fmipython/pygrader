"""Unit tests for the SpecCheck class in the spec_check module."""

import json
import unittest
from typing import Optional
from unittest.mock import MagicMock, patch

import requests

from grader.checks.spec_check import SpecCheck
from grader.exceptions import CheckError, ResourceError
from grader.models.check_result import ScoredCheckResult


def _make_response(status_code: int = 200, json_body: Optional[dict] = None, text: str = "") -> MagicMock:
    """Build a MagicMock standing in for a requests.Response."""
    response = MagicMock()
    response.status_code = status_code
    response.text = text or json.dumps(json_body or {})
    response.json.return_value = json_body
    return response


class TestSpecCheck(unittest.TestCase):
    """Unit tests for the SpecCheck class."""

    def setUp(self) -> None:
        """Set up the test environment."""
        self.spec_check = SpecCheck("spec", "sample_dir", 10, is_venv_required=False)
        self.spec_check._assets = [MagicMock(read=MagicMock(return_value="# Spec\nDo the thing."))]
        return super().setUp()

    def _mock_source(self, mocked_find_all_source_files: MagicMock, files: dict) -> None:
        """Point find_all_source_files at fake files, patching open() to serve their contents."""
        mocked_find_all_source_files.return_value = list(files.keys())

        def fake_open(path: str, *_args: object, **_kwargs: object) -> MagicMock:
            handle = MagicMock()
            handle.__enter__.return_value.read.return_value = files[path]
            return handle

        patcher = patch("builtins.open", side_effect=fake_open)
        self.addCleanup(patcher.stop)
        patcher.start()

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_01_happy_path(self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock) -> None:
        """Verify that the run method returns the score and rationale from the model."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {"sample_dir/main.py": "print('hi')"})
        mocked_post.return_value = _make_response(
            200, {"choices": [{"message": {"content": json.dumps({"score": 7, "rationale": "Solid attempt."})}}]}
        )
        expected = ScoredCheckResult("spec", 7.0, "Solid attempt.", "", 10)

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act
            actual = self.spec_check.run()

        # Assert
        self.assertEqual(expected, actual)

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_02_score_above_max_is_clamped(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that a score above max_points is clamped to max_points."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {})
        mocked_post.return_value = _make_response(
            200, {"choices": [{"message": {"content": json.dumps({"score": 15, "rationale": "Great."})}}]}
        )

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act
            actual = self.spec_check.run()

        # Assert
        self.assertEqual(actual.result, 10.0)

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_03_negative_score_is_clamped_to_zero(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that a negative score is clamped to 0."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {})
        mocked_post.return_value = _make_response(
            200, {"choices": [{"message": {"content": json.dumps({"score": -3, "rationale": "Missing everything."})}}]}
        )

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act
            actual = self.spec_check.run()

        # Assert
        self.assertEqual(actual.result, 0.0)

    def test_04_missing_api_key_raises_check_error(self) -> None:
        """Verify that a missing API key environment variable raises a CheckError."""
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(CheckError):
                self.spec_check.run()

    def test_05_missing_assets_raises_check_error(self) -> None:
        """Verify that running without a configured spec asset raises a CheckError."""
        # Arrange
        self.spec_check._assets = []

        # Act & Assert
        with self.assertRaises(CheckError):
            self.spec_check.run()

    def test_06_unreadable_spec_file_raises_check_error(self) -> None:
        """Verify that a spec file that cannot be read raises a CheckError."""
        # Arrange
        self.spec_check._assets = [MagicMock(read=MagicMock(side_effect=ResourceError("boom")))]

        # Act & Assert
        with self.assertRaises(CheckError):
            self.spec_check.run()

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_07_non_2xx_response_raises_check_error(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that a non-2xx response raises a CheckError carrying the status code."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {})
        mocked_post.return_value = _make_response(500, text="internal error")

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act & Assert
            with self.assertRaises(CheckError) as context:
                self.spec_check.run()

        self.assertIn("500", str(context.exception))

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_08_network_error_raises_check_error(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that a network error raises a CheckError."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {})
        mocked_post.side_effect = requests.ConnectionError("network down")

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act & Assert
            with self.assertRaises(CheckError):
                self.spec_check.run()

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_09_error_in_200_response_raises_check_error(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that an {"error": ...} body in a 200 response raises a CheckError."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {})
        mocked_post.return_value = _make_response(200, {"error": {"message": "no credits"}})

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act & Assert
            with self.assertRaises(CheckError):
                self.spec_check.run()

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_10_non_json_model_output_raises_check_error(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that non-JSON model output raises a CheckError."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {})
        mocked_post.return_value = _make_response(
            200, {"choices": [{"message": {"content": "not json at all"}}]}
        )

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act & Assert
            with self.assertRaises(CheckError):
                self.spec_check.run()

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_11_fenced_json_output_parses_correctly(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that model output wrapped in a markdown code fence still parses."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {})
        fenced_content = '```json\n{"score": 4, "rationale": "Partial."}\n```'
        mocked_post.return_value = _make_response(200, {"choices": [{"message": {"content": fenced_content}}]})
        expected = ScoredCheckResult("spec", 4.0, "Partial.", "", 10)

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act
            actual = self.spec_check.run()

        # Assert
        self.assertEqual(expected, actual)

    @patch("grader.checks.spec_check.requests.post")
    @patch("grader.checks.spec_check.find_all_source_files")
    def test_12_source_sent_to_model_excludes_test_files(
        self, mocked_find_all_source_files: MagicMock, mocked_post: MagicMock
    ) -> None:
        """Verify that only files returned by find_all_source_files are sent (tests excluded upstream)."""
        # Arrange
        self._mock_source(mocked_find_all_source_files, {"sample_dir/main.py": "print('hi')"})
        mocked_post.return_value = _make_response(
            200, {"choices": [{"message": {"content": json.dumps({"score": 5, "rationale": "ok"})}}]}
        )

        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"}):
            # Act
            self.spec_check.run()

        # Assert
        sent_payload = mocked_post.call_args.kwargs["json"]
        user_message = sent_payload["messages"][1]["content"]
        self.assertIn("main.py", user_message)
        self.assertIn("print('hi')", user_message)
        self.assertNotIn("test_main.py", user_message)
