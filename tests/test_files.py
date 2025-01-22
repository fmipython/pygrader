import os
import unittest
from unittest.mock import patch, MagicMock

from grader.utils.files import (
    find_all_files_under_directory,
    find_all_python_files,
    find_all_source_files,
    find_all_test_files,
    get_tests_directory_name,
)


class TestFindAllFilesUnderDirectory(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("os.walk")
    def test_01_partial_files_result(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns the proper files
            when there are multiple files with different extensions.
        :param mocked_os_walk: _description_
        """
        # Arrange
        mocked_os_walk.return_value = [
            (os.path.join(os.sep, "root"), ["folder1", "folder2"], ["file1.txt", "file2.csv"]),
            (os.path.join(os.sep, "root", "folder1"), ["subfolder1"], ["file3.txt"]),
            (os.path.join(os.sep, "root", "folder1", "subfolder1"), [], ["file4.csv", "file5.txt"]),
            (os.path.join(os.sep, "root", "folder2"), [], ["file6.csv"]),
        ]

        extension_to_search_for = ".txt"
        expected_files = [
            os.path.join(root, file)
            for root, _, files in mocked_os_walk.return_value
            for file in files
            if file.endswith(extension_to_search_for)
        ]

        # Act
        actual_files = find_all_files_under_directory(self.__sample_dir, extension_to_search_for)

        # Assert
        self.assertEqual(expected_files, actual_files)

    @patch("os.walk")
    def test_02_all_files_result(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns the proper files
            when there are multiple files with the same extension.
        :param mocked_os_walk: _description_
        """
        # Arrange
        mocked_os_walk.return_value = [
            (os.path.join(os.sep, "root"), ["folder1", "folder2"], ["file1.txt", "file2.txt"]),
            (os.path.join(os.sep, "root", "folder1"), ["subfolder1"], ["file3.txt"]),
            (os.path.join(os.sep, "root", "folder1", "subfolder1"), [], ["file4.txt", "file5.txt"]),
            (os.path.join(os.sep, "root", "folder2"), [], ["file6.txt"]),
        ]

        extension_to_search_for = ".txt"
        expected_files = [
            os.path.join(root, file)
            for root, _, files in mocked_os_walk.return_value
            for file in files
            if file.endswith(extension_to_search_for)
        ]

        # Act
        actual_files = find_all_files_under_directory(self.__sample_dir, extension_to_search_for)

        # Assert
        self.assertEqual(expected_files, actual_files)

    @patch("os.walk")
    def test_03_no_files_result(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns an empty list
            when there are no files with the searched extension.
        :param mocked_os_walk: _description_
        """
        # Arrange
        mocked_os_walk.return_value = [
            (os.path.join(os.sep, "root"), ["folder1", "folder2"], ["file1.txt", "file2.txt"]),
            (os.path.join(os.sep, "root", "folder1"), ["subfolder1"], ["file3.txt"]),
            (os.path.join(os.sep, "root", "folder1", "subfolder1"), [], ["file4.txt", "file5.txt"]),
            (os.path.join(os.sep, "root", "folder2"), [], ["file6.txt"]),
        ]

        extension_to_search_for = ".py"
        expected_files = [
            os.path.join(root, file)
            for root, _, files in mocked_os_walk.return_value
            for file in files
            if file.endswith(extension_to_search_for)
        ]

        # Act
        actual_files = find_all_files_under_directory(self.__sample_dir, extension_to_search_for)

        # Assert
        self.assertEqual(expected_files, actual_files)

    @patch("os.walk")
    def test_03_no_files_overall(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns an empty list
            when there are no files.
        :param mocked_os_walk: _description_
        """
        # Arrange
        mocked_os_walk.return_value = []

        extension_to_search_for = ".py"
        expected_files = [
            os.path.join(root, file)
            for root, _, files in mocked_os_walk.return_value
            for file in files
            if file.endswith(extension_to_search_for)
        ]

        # Act
        actual_files = find_all_files_under_directory(self.__sample_dir, extension_to_search_for)

        # Assert
        self.assertEqual(expected_files, actual_files)
