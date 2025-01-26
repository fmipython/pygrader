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


class TestFindAllPythonFiles(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("grader.utils.files.find_all_files_under_directory")
    def test_01_find_all_python_files(self, mocked_function: MagicMock):
        # Arrange
        all_files, expected_files = self.__build_sample_files()
        mocked_function.return_value = all_files

        # Act
        actual_files = find_all_python_files(self.__sample_dir)

        # Assert
        self.assertEqual(expected_files, actual_files)

    def __build_sample_files(self) -> tuple[list[str], list[str]]:
        root_dir = self.__sample_dir
        folder_1 = os.path.join(root_dir, "folder1")
        folder_2 = os.path.join(root_dir, "folder2")
        subfolder_2 = os.path.join(folder_2, "subfolder2")
        subfolder_3 = os.path.join(folder_2, "subfolder3")
        venv_dir_1 = os.path.join(root_dir, "venv")
        venv_dir_2 = os.path.join(root_dir, ".venv")

        all_files = [
            os.path.join(folder_1, "file2.py"),
            os.path.join(folder_1, "file3.py"),
            os.path.join(folder_2, "file5.py"),
            os.path.join(subfolder_2, "file9.py"),
            os.path.join(subfolder_3, "file10.py"),
            os.path.join(venv_dir_1, "file11.py"),
            os.path.join(venv_dir_1, "file12.py"),
            os.path.join(venv_dir_2, "file13.py"),
            os.path.join(venv_dir_2, "file14.py"),
        ]

        expected_files = [
            os.path.join(folder_1, "file2.py"),
            os.path.join(folder_1, "file3.py"),
            os.path.join(folder_2, "file5.py"),
            os.path.join(subfolder_2, "file9.py"),
            os.path.join(subfolder_3, "file10.py"),
        ]

        return all_files, expected_files


class TestFindAllSourceFiles(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("grader.utils.files.find_all_test_files")
    @patch("grader.utils.files.find_all_python_files")
    def test_01_test_name(
        self,
        mocked_all_python_files: MagicMock,
        mocked_find_all_test_files: MagicMock,
    ):
        # Arrange
        python_file_names = [f"file{i}" for i in range(1, 11)]
        python_file_paths = [
            os.path.join(self.__sample_dir, python_file_name) for python_file_name in python_file_names
        ]

        test_file_names = [f"file{i}" for i in range(1, 11, 3)]
        test_file_paths = [os.path.join(self.__sample_dir, test_file_name) for test_file_name in test_file_names]

        mocked_all_python_files.return_value = python_file_paths
        mocked_find_all_test_files.return_value = test_file_paths

        expected_files = list(set(python_file_paths) - set(test_file_paths))

        # Act
        actual_files = find_all_source_files(self.__sample_dir)

        # Assert
        self.assertEqual(sorted(expected_files), sorted(actual_files))


class TestFindAllTestFiles(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("grader.utils.files.find_all_files_under_directory")
    def test_01_no_directory_provided(self, mocked_find_all_files_under_directory: MagicMock):
        # Arrange
        expected_value: list[str] = []

        # Act
        actual_value = find_all_test_files(tests_directory=None)

        # Assert
        self.assertEqual(expected_value, actual_value)
        mocked_find_all_files_under_directory.assert_not_called()

    @patch("grader.utils.files.find_all_files_under_directory")
    def test_02_directory_provided(self, mocked_find_all_files_under_directory: MagicMock):
        # Arrange
        expected_value: list[str] = [
            os.path.join(self.__sample_dir, "file1.py"),
            os.path.join(self.__sample_dir, "file2.py"),
        ]

        mocked_find_all_files_under_directory.return_value = expected_value

        # Act
        actual_value = find_all_test_files(self.__sample_dir)

        # Assert
        self.assertEqual(expected_value, actual_value)
        mocked_find_all_files_under_directory.assert_called_once_with(self.__sample_dir, ".py")


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

    def test_02_test_directory(self):
        # Arrange
        test_dir_name = "test"
        expected_test_dir = os.path.join(self.__sample_dir, test_dir_name)
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertEqual(expected_test_dir, actual_test_dir)

    def test_03_tst_directory(self):
        # Arrange
        test_dir_name = "tst"
        expected_test_dir = os.path.join(self.__sample_dir, test_dir_name)
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertEqual(expected_test_dir, actual_test_dir)

    def test_04_no_directory(self):
        # Arrange
        test_dir_name = "some_other_name"
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertIsNone(actual_test_dir)

    @staticmethod
    def __create_structure(root_dir: str, tests_dir: str):
        full_path = os.path.join(root_dir, tests_dir)
        os.makedirs(full_path)


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

    def __build_sample_files(self, files: list[list[str]]) -> DirectoryStructure:
        root_dirs = [
            os.path.join(os.sep, self.__sample_dir),
            os.path.join(os.sep, self.__sample_dir, "folder1"),
            os.path.join(os.sep, self.__sample_dir, "folder1", "subfolder1"),
            os.path.join(os.sep, self.__sample_dir, "folder2"),
        ]
        subdirs = [["folder1", "folder2"], ["subfolder1"], []]

        return [result for result in zip(root_dirs, subdirs, files)]
