"""Unit tests for the file utility functions."""

import shutil
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from grader.utils.files import (
    find_all_files_under_directory,
    find_all_python_files,
    find_all_source_files,
    find_all_test_files,
    get_tests_directory_name,
    unzip_archive,
)


class TestFindAllPythonFiles:
    """Test cases for the find_all_python_files function."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        self.__sample_dir = "sample_dir"

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
        assert expected_files == actual_files
        mocked_function.assert_called_once_with(self.__sample_dir)

    def __build_sample_files(self) -> tuple[list[str], list[str]]:
        """
        Build the sample files for the test.

        :return: The list of all files and the list of expected files.
        :rtype: tuple[list[str], list[str]]
        """
        root_dir = self.__sample_dir
        folder_1 = str(Path(root_dir, "folder1"))
        folder_2 = str(Path(root_dir, "folder2"))
        subfolder_2 = str(Path(folder_2, "subfolder2"))
        subfolder_3 = str(Path(folder_2, "subfolder3"))
        venv_dir_1 = str(Path(root_dir, "venv"))
        venv_dir_2 = str(Path(root_dir, ".venv"))

        all_files = [
            str(Path(folder_1, "file2.py")),
            str(Path(folder_1, "file3.py")),
            str(Path(folder_2, "file5.py")),
            str(Path(subfolder_2, "file9.py")),
            str(Path(subfolder_3, "file10.py")),
            str(Path(venv_dir_1, "file11.py")),
            str(Path(venv_dir_1, "file12.py")),
            str(Path(venv_dir_2, "file13.py")),
            str(Path(venv_dir_2, "file14.py")),
        ]

        expected_files = [
            str(Path(folder_1, "file2.py")),
            str(Path(folder_1, "file3.py")),
            str(Path(folder_2, "file5.py")),
            str(Path(subfolder_2, "file9.py")),
            str(Path(subfolder_3, "file10.py")),
        ]

        return all_files, expected_files


class TestFindAllSourceFiles:
    """Test cases for the find_all_source_files function."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        self.__sample_dir = "sample_dir"

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
        python_file_paths = [str(Path(self.__sample_dir, python_file_name)) for python_file_name in python_file_names]

        test_file_names = [f"file{i}" for i in range(1, 11, 3)]
        test_file_paths = [str(Path(self.__sample_dir, test_file_name)) for test_file_name in test_file_names]

        mocked_all_python_files.return_value = python_file_paths
        mocked_find_all_test_files.return_value = test_file_paths
        mocked_tests_directory_name.return_value = self.__sample_dir

        expected_files = list(set(python_file_paths) - set(test_file_paths))

        # Act
        actual_files = find_all_source_files(self.__sample_dir)

        # Assert
        assert sorted(expected_files) == sorted(actual_files)
        mocked_all_python_files.assert_called_once_with(self.__sample_dir)
        mocked_find_all_test_files.assert_called_once_with(self.__sample_dir)
        mocked_tests_directory_name.assert_called_once_with(self.__sample_dir)


class TestFindAllTestFiles:
    """Test cases for the find_all_test_files function."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        self.__sample_dir = "sample_dir"

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
        assert expected_value == actual_value
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
            str(Path(self.__sample_dir, "file1.py")),
            str(Path(self.__sample_dir, "file2.py")),
        ]

        mocked_find_all_files_under_directory.return_value = expected_value

        # Act
        actual_value = find_all_test_files(self.__sample_dir)

        # Assert
        assert expected_value == actual_value
        mocked_find_all_files_under_directory.assert_called_once_with(self.__sample_dir)


class TestGetTestsDirectoryName:
    """Test cases for the get_tests_directory_name function."""

    def setup_method(self) -> None:
        """Set up the test environment."""
        self.__sample_dir = "sample_dir"

    def teardown_method(self) -> None:
        """Tear down the test environment."""
        if Path(self.__sample_dir).exists():
            shutil.rmtree(self.__sample_dir)

    def test_01_tests_directory(self) -> None:
        """Verify that get_tests_directory_name returns the proper directory name."""
        # Arrange
        test_dir_name = "tests"
        expected_test_dir = str(Path(self.__sample_dir, test_dir_name))
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        assert expected_test_dir == actual_test_dir

    def test_02_test_directory(self) -> None:
        """Verify that get_tests_directory_name returns the proper directory name."""
        # Arrange
        test_dir_name = "test"
        expected_test_dir = str(Path(self.__sample_dir, test_dir_name))
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        assert expected_test_dir == actual_test_dir

    def test_03_tst_directory(self) -> None:
        """Verify that get_tests_directory_name returns the proper directory name."""
        # Arrange
        test_dir_name = "tst"
        expected_test_dir = str(Path(self.__sample_dir, test_dir_name))
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        assert expected_test_dir == actual_test_dir

    def test_04_no_directory(self) -> None:
        """Verify that get_tests_directory_name returns None when there is no tests directory."""
        # Arrange
        test_dir_name = "some_other_name"
        self.__create_structure(self.__sample_dir, test_dir_name)

        # Act
        actual_test_dir = get_tests_directory_name(self.__sample_dir)

        # Assert
        assert actual_test_dir is None

    @staticmethod
    def __create_structure(root_dir: str, tests_dir: str) -> None:
        """
        Create the directory structure for the test.

        :param root_dir: The root directory.
        :type root_dir: str
        :param tests_dir: The tests directory.
        :type tests_dir: str
        """
        full_path = str(Path(root_dir, tests_dir))
        Path(full_path).mkdir(parents=True)


class TestFindAllFilesUnderDirectory:
    """Test cases for the find_all_files_under_directory function."""

    @staticmethod
    def __build_tree(root: Path, files: list[str]) -> None:
        for file in files:
            (root / file).parent.mkdir(parents=True, exist_ok=True)
            (root / file).touch()

    def test_01_partial_files_result(self, tmp_path: Path) -> None:
        """Verify that only files with the requested extension are returned, recursively."""
        self.__build_tree(
            tmp_path, ["file1.txt", "file2.csv", "dir/file3.txt", "dir/sub/file4.csv", "dir/sub/file5.txt"]
        )
        expected = sorted(str(tmp_path / name) for name in ["file1.txt", "dir/file3.txt", "dir/sub/file5.txt"])

        assert sorted(find_all_files_under_directory(str(tmp_path), ".txt")) == expected

    def test_02_all_files_result(self, tmp_path: Path) -> None:
        """Verify that all files are returned when they all have the requested extension."""
        names = ["file1.txt", "file2.txt", "dir/file3.txt", "dir/sub/file4.txt"]
        self.__build_tree(tmp_path, names)

        assert sorted(find_all_files_under_directory(str(tmp_path), ".txt")) == sorted(str(tmp_path / n) for n in names)

    def test_03_no_files_result(self, tmp_path: Path) -> None:
        """Verify that an empty list is returned when no file has the requested extension."""
        self.__build_tree(tmp_path, ["file1.csv", "dir/file2.csv"])

        assert not find_all_files_under_directory(str(tmp_path), ".py")

    def test_04_no_files_overall(self, tmp_path: Path) -> None:
        """Verify that an empty list is returned for an empty directory."""
        assert not find_all_files_under_directory(str(tmp_path), ".py")

    def test_05_directory_matching_extension_is_skipped(self, tmp_path: Path) -> None:
        """Verify that a directory whose name ends with the extension is not returned."""
        (tmp_path / "package.py").mkdir()

        assert not find_all_files_under_directory(str(tmp_path), ".py")


class TestUnzipArchive:
    """Test cases for the unzip_archive function."""

    @patch("zipfile.ZipFile")
    def test_01_unzip_to_default_directory(self, mock_zipfile: MagicMock) -> None:
        """Verify that unzip_archive extracts to the default directory and returns the correct path."""
        # Setup
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        archive_path = "/fake/path/test_archive.zip"

        # Act
        result_dir = unzip_archive(archive_path)

        # Assert
        mock_zip.extractall.assert_called_once()
        assert "test_archive" in result_dir

    @patch("zipfile.ZipFile")
    def test_02_unzip_to_custom_directory(self, mock_zipfile: MagicMock) -> None:
        """Verify that unzip_archive extracts to a custom target directory."""
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        archive_path = "/fake/path/test_archive.zip"
        custom_dir = "/custom/dir"
        # Act
        result_dir = unzip_archive(archive_path, target_directory=custom_dir)
        # Assert
        mock_zip.extractall.assert_called_once_with(custom_dir)
        assert result_dir == custom_dir

    @patch("zipfile.ZipFile", side_effect=zipfile.BadZipFile)
    def test_03_invalid_zip_file(self, mock_exists: MagicMock) -> None:
        """Verify that unzip_archive raises an exception for an invalid zip file."""
        archive_path = "/fake/path/invalid.zip"
        with pytest.raises(zipfile.BadZipFile):
            unzip_archive(archive_path)
        assert mock_exists.called

    def test_04_nonexistent_zip_file(self) -> None:
        """Verify that unzip_archive raises an exception for a nonexistent file."""
        archive_path = "/nonexistent/path/to/file.zip"
        with pytest.raises(FileNotFoundError):
            unzip_archive(archive_path)
