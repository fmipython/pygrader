"""
Unit tests for the file utility functions.
"""

import os
import shutil
import unittest
from typing import TypeAlias
from unittest.mock import patch, MagicMock
import zipfile
from grader.utils.files import unzip_archive

from grader.utils.files import (
    find_all_files_under_directory,
    find_all_python_files,
    find_all_source_files,
    find_all_test_files,
    get_tests_directory_name,
)


class TestFindAllPythonFiles(unittest.TestCase):
    """
    Test cases for the find_all_python_files function.
    """

    def __init__(self, methodName: str = "runTest") -> None:
        """
        Initialize the test case.

        :param methodName: The name of the test method to run.
        :type methodName: str
        """
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("grader.utils.structure_validator.StructureValidator.get_matching_files")
    def test_01_find_all_python_files(self, mocked_function: MagicMock) -> None:
        """
        Verify that find_all_python_files returns the proper files.

        :param mocked_function: Mocked find_all_files_under_directory function.
        :type mocked_function: MagicMock
        """
        # Arrange
        all_files, expected_files = self.__build_sample_files()
        mocked_function.return_value = all_files

        # Act
        actual_files = find_all_python_files(self.__sample_dir)

        # Assert
        self.assertEqual(expected_files, actual_files)
        mocked_function.assert_called_once_with(self.__sample_dir)

    def __build_sample_files(self) -> tuple[list[str], list[str]]:
        """
        Build the sample files for the test.

        :return: The list of all files and the list of expected files.
        :rtype: tuple[list[str], list[str]]
        """
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
    """
    Test cases for the find_all_source_files function.
    """

    def __init__(self, methodName: str = "runTest") -> None:
        """
        Initialize the test case.

        :param methodName: The name of the test method to run.
        :type methodName: str
        """
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("grader.utils.files.find_all_test_files")
    @patch("grader.utils.files.find_all_python_files")
    @patch("grader.utils.files.get_tests_directory_name")
    def test_01_find_all_source_files(
        self,
        mocked_tests_directory_name: MagicMock,
        mocked_all_python_files: MagicMock,
        mocked_find_all_test_files: MagicMock,
    ) -> None:
        """
        Verify that find_all_source_files returns the proper files.

        :param mocked_tests_directory_name: Mocked get_tests_directory_name function.
        :type mocked_tests_directory_name: MagicMock
        :param mocked_all_python_files: Mocked find_all_python_files function.
        :type mocked_all_python_files: MagicMock
        :param mocked_find_all_test_files: Mocked find_all_test_files function.
        :type mocked_find_all_test_files: MagicMock
        """
        # Arrange
        python_file_names = [f"file{i}" for i in range(1, 11)]
        python_file_paths = [
            os.path.join(self.__sample_dir, python_file_name) for python_file_name in python_file_names
        ]

        test_file_names = [f"file{i}" for i in range(1, 11, 3)]
        test_file_paths = [os.path.join(self.__sample_dir, test_file_name) for test_file_name in test_file_names]

        mocked_all_python_files.return_value = python_file_paths
        mocked_find_all_test_files.return_value = test_file_paths
        mocked_tests_directory_name.return_value = self.__sample_dir

        expected_files = list(set(python_file_paths) - set(test_file_paths))

        # Act
        actual_files = find_all_source_files(self.__sample_dir)

        # Assert
        self.assertEqual(sorted(expected_files), sorted(actual_files))
        mocked_all_python_files.assert_called_once_with(self.__sample_dir)
        mocked_find_all_test_files.assert_called_once_with(self.__sample_dir)
        mocked_tests_directory_name.assert_called_once_with(self.__sample_dir)


class TestFindAllTestFiles(unittest.TestCase):
    """
    Test cases for the find_all_test_files function.
    """

    def __init__(self, methodName: str = "runTest") -> None:
        """
        Initialize the test case.

        :param methodName: The name of the test method to run.
        :type methodName: str
        """
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("grader.utils.files.find_all_files_under_directory")
    def test_01_no_directory_provided(self, mocked_find_all_files_under_directory: MagicMock) -> None:
        """
        Verify that find_all_test_files returns an empty list when no directory is provided.

        :param mocked_find_all_files_under_directory: Mocked find_all_files_under_directory function.
        :type mocked_find_all_files_under_directory: MagicMock
        """
        # Arrange
        expected_value: list[str] = []

        # Act
        actual_value = find_all_test_files(tests_directory=None)

        # Assert
        self.assertEqual(expected_value, actual_value)
        mocked_find_all_files_under_directory.assert_not_called()

    @patch("grader.utils.structure_validator.StructureValidator.get_matching_files")
    def test_02_directory_provided(self, mocked_find_all_files_under_directory: MagicMock) -> None:
        """
        Verify that find_all_test_files returns the proper files when a directory is provided.

        :param mocked_find_all_files_under_directory: Mocked find_all_files_under_directory function.
        :type mocked_find_all_files_under_directory: MagicMock
        """
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
        mocked_find_all_files_under_directory.assert_called_once_with(self.__sample_dir)


class TestGetTestsDirectoryName(unittest.TestCase):
    """
    Test cases for the get_tests_directory_name function.
    """

    def __init__(self, methodName: str = "runTest") -> None:
        """
        Initialize the test case.

        :param methodName: The name of the test method to run.
        :type methodName: str
        """
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    def tearDown(self) -> None:
        """
        Tear down the test environment.
        """
        if os.path.exists(self.__sample_dir):
            shutil.rmtree(self.__sample_dir)
        return super().tearDown()

    def test_01_tests_directory(self) -> None:
        """
        Verify that get_tests_directory_name returns the proper directory name.
        """
        # Arrange
        test_dir_name = "tests"
        expected_test_dir = os.path.join(self.__sample_dir, test_dir_name)
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertEqual(expected_test_dir, actual_test_dir)

    def test_02_test_directory(self) -> None:
        """
        Verify that get_tests_directory_name returns the proper directory name.
        """
        # Arrange
        test_dir_name = "test"
        expected_test_dir = os.path.join(self.__sample_dir, test_dir_name)
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertEqual(expected_test_dir, actual_test_dir)

    def test_03_tst_directory(self) -> None:
        """
        Verify that get_tests_directory_name returns the proper directory name.
        """
        # Arrange
        test_dir_name = "tst"
        expected_test_dir = os.path.join(self.__sample_dir, test_dir_name)
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertEqual(expected_test_dir, actual_test_dir)

    def test_04_no_directory(self) -> None:
        """
        Verify that get_tests_directory_name returns None when there is no tests directory.
        """
        # Arrange
        test_dir_name = "some_other_name"
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        self.assertIsNone(actual_test_dir)

    @staticmethod
    def __create_structure(root_dir: str, tests_dir: str) -> None:
        """
        Create the directory structure for the test.

        :param root_dir: The root directory.
        :type root_dir: str
        :param tests_dir: The tests directory.
        :type tests_dir: str
        """
        full_path = os.path.join(root_dir, tests_dir)
        os.makedirs(full_path)


class TestFindAllFilesUnderDirectory(unittest.TestCase):
    """
    Test cases for the find_all_files_under_directory function.
    """

    DirectoryStructure: TypeAlias = list[tuple[str, list[str], list[str]]]

    def __init__(self, methodName: str = "runTest") -> None:
        """
        Initialize the test case.

        :param methodName: The name of the test method to run.
        :type methodName: str
        """
        self.__sample_dir = "sample_dir"
        super().__init__(methodName)

    @patch("os.walk")
    def test_01_partial_files_result(self, mocked_os_walk: MagicMock) -> None:
        """
        Verify that find_all_files_under_directory returns the proper files
            when there are multiple files with different extensions.

        :param mocked_os_walk: Mocked os.walk function.
        :type mocked_os_walk: MagicMock
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
    def test_02_all_files_result(self, mocked_os_walk: MagicMock) -> None:
        """
        Verify that find_all_files_under_directory returns the proper files
            when there are multiple files with the same extension.

        :param mocked_os_walk: Mocked os.walk function.
        :type mocked_os_walk: MagicMock
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
    def test_03_no_files_result(self, mocked_os_walk: MagicMock) -> None:
        """
        Verify that find_all_files_under_directory returns an empty list
            when there are no files with the searched extension.

        :param mocked_os_walk: Mocked os.walk function.
        :type mocked_os_walk: MagicMock
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
    def test_03_no_files_overall(self, mocked_os_walk: MagicMock) -> None:
        """
        Verify that find_all_files_under_directory returns an empty list
            when there are no files.

        :param mocked_os_walk: Mocked os.walk function.
        :type mocked_os_walk: MagicMock
        """
        self.__base_test(mocked_os_walk, mocked_files=[], extension_to_search_for=".py")

    def __base_test(
        self,
        mocked_os_walk: MagicMock,
        mocked_files: DirectoryStructure,
        extension_to_search_for: str,
    ) -> None:
        """
        Base test for find_all_files_under_directory.

        :param mocked_os_walk: Mocked os.walk function.
        :type mocked_os_walk: MagicMock
        :param mocked_files: Mocked directory structure.
        :type mocked_files: DirectoryStructure
        :param extension_to_search_for: The file extension to search for.
        :type extension_to_search_for: str
        """
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
        """
        Build the sample files for the test.

        :param files: The list of files in each directory.
        :type files: list[list[str]]
        :return: The directory structure.
        :rtype: DirectoryStructure
        """
        root_dirs = [
            os.path.join(os.sep, self.__sample_dir),
            os.path.join(os.sep, self.__sample_dir, "folder1"),
            os.path.join(os.sep, self.__sample_dir, "folder1", "subfolder1"),
            os.path.join(os.sep, self.__sample_dir, "folder2"),
        ]
        subdirs = [["folder1", "folder2"], ["subfolder1"], []]

        return list(zip(root_dirs, subdirs, files))


class TestUnzipArchive(unittest.TestCase):
    """
    Test cases for the unzip_archive function.
    """

    @patch("zipfile.ZipFile")
    @patch("os.path.exists", return_value=True)
    def test_01_unzip_to_default_directory(self, mock_exists, mock_zipfile):
        """
        Verify that unzip_archive extracts to the default directory and returns the correct path.
        """
        # Setup
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        archive_path = "/fake/path/test_archive.zip"
        # Act
        result_dir = unzip_archive(archive_path)
        # Assert
        mock_zip.extractall.assert_called_once()
        self.assertIn("test_archive", result_dir)
        self.assertTrue(mock_exists.called)

    @patch("zipfile.ZipFile")
    @patch("os.path.exists", return_value=True)
    def test_02_unzip_to_custom_directory(self, mock_exists, mock_zipfile):
        """
        Verify that unzip_archive extracts to a custom target directory.
        """
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        archive_path = "/fake/path/test_archive.zip"
        custom_dir = "/custom/dir"
        # Act
        result_dir = unzip_archive(archive_path, target_directory=custom_dir)
        # Assert
        mock_zip.extractall.assert_called_once_with(custom_dir)
        self.assertEqual(result_dir, custom_dir)
        self.assertTrue(mock_exists.called)

    @patch("zipfile.ZipFile", side_effect=zipfile.BadZipFile)
    @patch("os.path.exists", return_value=True)
    def test_03_invalid_zip_file(self, mock_exists, _):
        """
        Verify that unzip_archive raises an exception for an invalid zip file.
        """
        archive_path = "/fake/path/invalid.zip"
        with self.assertRaises(Exception):
            unzip_archive(archive_path)
        self.assertTrue(mock_exists.called)

    @patch("os.path.exists", return_value=False)
    def test_04_nonexistent_zip_file(self, mock_exists):
        """
        Verify that unzip_archive raises an exception for a nonexistent file.
        """
        archive_path = "/nonexistent/path/to/file.zip"
        with self.assertRaises(FileNotFoundError):
            unzip_archive(archive_path)
        self.assertTrue(mock_exists.called)
