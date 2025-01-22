import os
import shutil
import unittest
from typing import TypeAlias
from unittest.mock import patch, MagicMock

from grader.utils.files import (
    find_all_files_under_directory,
    find_all_python_files,
    find_all_source_files,
    find_all_test_files,
    get_tests_directory_name,
)


class TestFindAllFilesUnderDirectory(unittest.TestCase):
    DirectoryStructure: TypeAlias = list[tuple[str, list[str], list[str]]]

    def __init__(self, methodName="runTest"):
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("os.walk")
    def test_01_partial_files_result(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns the proper files
            when there are multiple files with different extensions.
        """
        files = [
            ["file1.txt", "file2.csv"],
            ["file3.txt"],
            ["file4.csv", "file5.txt"],
            ["file6.csv"],
        ]
        mocked_files = self.__build_sample_files(files)

        self.__base_test(mocked_os_walk, mocked_files, extension_to_search_for=".txt")

    @patch("os.walk")
    def test_02_all_files_result(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns the proper files
            when there are multiple files with the same extension.
        """
        files = [
            ["file1.txt", "file2.txt"],
            ["file3.txt"],
            ["file4.txt", "file5.txt"],
            ["file6.txt"],
        ]
        mocked_files = self.__build_sample_files(files)

        self.__base_test(mocked_os_walk, mocked_files, extension_to_search_for=".txt")

    @patch("os.walk")
    def test_03_no_files_result(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns an empty list
            when there are no files with the searched extension.
        """
        # Arrange
        files = [
            ["file1.txt", "file2.csv"],
            ["file3.txt"],
            ["file4.csv", "file5.txt"],
            ["file6.csv"],
        ]
        mocked_files = self.__build_sample_files(files)

        self.__base_test(mocked_os_walk, mocked_files, extension_to_search_for=".py")

    @patch("os.walk")
    def test_03_no_files_overall(self, mocked_os_walk: MagicMock):
        """
        Verify that find_all_files_under_directory returns an empty list
            when there are no files.
        :param mocked_os_walk: _description_
        """
        self.__base_test(mocked_os_walk, mocked_files=[], extension_to_search_for=".py")

    def __base_test(
        self,
        mocked_os_walk: MagicMock,
        mocked_files: DirectoryStructure,
        extension_to_search_for: str,
    ):
        # Arrange
        mocked_os_walk.return_value = mocked_files

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

    @staticmethod
    def __build_sample_files(files: list[list[str]]) -> DirectoryStructure:
        root_dirs = [
            os.path.join(os.sep, "root"),
            os.path.join(os.sep, "root", "folder1"),
            os.path.join(os.sep, "root", "folder1", "subfolder1"),
            os.path.join(os.sep, "root", "folder2"),
        ]
        subdirs = [["folder1", "folder2"], ["subfolder1"], []]

        return [result for result in zip(root_dirs, subdirs, files)]


class TestGetTestsDirectoryName(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    def tearDown(self):
        if os.path.exists(self.__sample_dir):
            shutil.rmtree(self.__sample_dir)
        return super().tearDown()

    def test_01_tests_directory(self):
        # Arrange
        test_dir_name = "tests"
        expected_test_dir = os.path.join(self.__sample_dir, test_dir_name)
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertEqual(expected_test_dir, actual_test_dir)

    @staticmethod
    def __create_structure(root_dir: str, tests_dir: str):
        full_path = os.path.join(root_dir, tests_dir)
        os.makedirs(full_path)
