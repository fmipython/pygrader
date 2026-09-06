"""Unit tests for the desktop.utils module."""

import unittest
import uuid
from unittest.mock import patch

from desktop.utils import extract_student_id_from_path


class TestExtractStudentIdFromPath(unittest.TestCase):
    """Unit tests for the extract_student_id_from_path function."""

    def test_01_extracts_id_from_valid_submission_path(self) -> None:
        """Verify the student id is extracted from a Moodle-style submission path."""
        path = "root/hw1/12345-John_Doe_1_assignsubmission_file/submission.zip"

        self.assertEqual(extract_student_id_from_path(path), "12345")

    def test_02_extracts_id_with_uppercase_letters(self) -> None:
        """Verify an id made of digits and uppercase letters is extracted in full."""
        path = "root/hw1/AB12C-Jane_Doe_2_assignsubmission_file/submission.zip"

        self.assertEqual(extract_student_id_from_path(path), "AB12C")

    @patch("desktop.utils.uuid.uuid4")
    def test_03_no_dash_subfolder_falls_back_to_uuid(self, mock_uuid4: unittest.mock.MagicMock) -> None:
        """Verify a path without the '<id>-name/file' shape falls back to a random uuid."""
        mock_uuid4.return_value = uuid.UUID("11111111-1111-1111-1111-111111111111")

        result = extract_student_id_from_path("some/plain/path")

        self.assertEqual(result, "11111111-1111-1111-1111-111111111111")

    @patch("desktop.utils.uuid.uuid4")
    def test_04_empty_id_group_falls_back_to_uuid(self, mock_uuid4: unittest.mock.MagicMock) -> None:
        """Verify a path matching the shape but with no id characters before the dash falls back to a uuid."""
        mock_uuid4.return_value = uuid.UUID("22222222-2222-2222-2222-222222222222")

        result = extract_student_id_from_path("root/hw1/-Name_1_assignsubmission_file/submission.zip")

        self.assertEqual(result, "22222222-2222-2222-2222-222222222222")


if __name__ == "__main__":
    unittest.main()
