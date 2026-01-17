"""
Module for functional tests of the grader.
"""

import os
import shutil
import unittest
import zipfile

from pathlib import Path
from typing import Optional

import grader.utils.constants as const
from grader.utils.process import run


class BaseFunctionalTestWithGrader(unittest.TestCase):
    """
    Base class for functional tests with the grader.
    """

    repo_url = "https://github.com/fmipython/pygrader"
    clone_path = "/tmp/pygrader-cloned"

    def setUp(self) -> None:
        if os.path.exists(self.clone_path):
            return

        clone_result = run(["git", "clone", self.repo_url, self.clone_path])
        if clone_result.returncode != 0:
            raise RuntimeError(f"Failed to clone the repository: {clone_result.stderr}")

        current_branch_result = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], current_directory=os.getcwd())
        if current_branch_result.returncode != 0:
            raise RuntimeError(f"Failed to get current branch: {current_branch_result.stderr}")

        current_branch = current_branch_result.stdout.strip()

        checkout_result = run(["git", "checkout", current_branch], current_directory=self.clone_path)
        if checkout_result.returncode != 0:
            raise RuntimeError(f"Failed to checkout branch {current_branch}: {checkout_result.stderr}")

        # Remove the functional tests from the repo, as they cause issues and time loss.
        functional_tests_path = os.path.join(self.clone_path, "tests", "functional", "test_functional.py")
        if os.path.exists(functional_tests_path):
            os.remove(functional_tests_path)

    def tearDown(self) -> None:
        if not os.path.exists(self.clone_path):
            return

        shutil.rmtree(self.clone_path)


@unittest.skipIf(os.name == "nt", "Test skipped on Windows")
class TestFunctionalGoodWeatherWithGrader(BaseFunctionalTestWithGrader):
    """
    Functional tests for the grader in a good weather scenario.
    """

    def test_01_requirements_txt_exists(self) -> None:
        """
        Verify that the grader can check the requirements.txt file.
        """
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="requirements", grader_output=run_stdout))

    def test_02_pylint_check(self) -> None:
        """
        Verify that the grader runs the pylint check and returns the expected score.
        """
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="pylint", grader_output=run_stdout))

    def test_03_type_hints_check(self) -> None:
        """
        Verify that the grader runs the type hints check and returns the expected score.
        """
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="type-hints", grader_output=run_stdout))

    @unittest.skip("Coverage check test is too unstable")
    def test_04_coverage_check(self) -> None:
        """
        Verify that the grader runs the coverage check and returns the expected score.
        """
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=8, target_check="coverage", grader_output=run_stdout))

    def test_05_log_file_created(self) -> None:
        """
        Verify that the log file is created.
        """
        # Arrange
        log_file = "grader.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(os.path.exists(log_file), "Log file was not created")
        os.remove(log_file)

    def test_06_log_file_with_student_id(self) -> None:
        """
        Verify that the log file is created with the student ID in its name.
        """
        # Arrange
        student_id = "student123"
        log_file = f"{student_id}.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path=self.clone_path, student_id=student_id)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(os.path.exists(log_file), f"Log file with student ID '{student_id}' was not created")
        os.remove(log_file)

    def test_07_student_id_in_output(self) -> None:
        """
        Verify that the student ID is included in the output.
        """
        # Arrange
        student_id = "student123"
        expected_output = f"Running checks for student {student_id}"
        command = build_command(project_path=self.clone_path, student_id=student_id)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertIn(
            expected_output, run_result.stdout, f"Expected output '{expected_output}' not found in the tool's output"
        )

    def test_08_default_log_file_name(self) -> None:
        """
        Verify that the default log file name is used when no student ID is provided.
        """
        # Arrange
        log_file = "grader.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(os.path.exists(log_file), "Default log file 'grader.log' was not created")
        os.remove(log_file)

    @unittest.skip("Unstable test")
    def test_09_all_checks_score_one(self) -> None:
        """
        Verify that all checks return a score of 1 when using the full_single_point.json configuration.
        """
        # Arrange
        config_file = "full_single_point.json"
        command = build_command(project_path=self.clone_path, config_file=config_file)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        for check in ["requirements", "pylint", "type-hints", "coverage"]:
            self.assertTrue(
                is_score_correct(expected_score=1, target_check=check, grader_output=run_stdout),
                f"Check '{check}' did not have the expected score of 1",
            )

    def test_10_only_pylint_check(self) -> None:
        """
        Verify that only the pylint check is executed when using the only_pylint.json configuration.
        """
        # Arrange
        config_file = "only_pylint.json"
        command = build_command(project_path=self.clone_path, config_file=config_file)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(
            is_score_correct(expected_score=1, target_check="pylint", grader_output=run_stdout),
            "Pylint check did not have the expected score of 1",
        )
        for check in ["requirements", "type-hints", "coverage"]:
            self.assertNotIn(f"Check: {check}", run_stdout, f"Unexpected check '{check}' was executed")


@unittest.skipIf(os.name == "nt", "Test skipped on Windows")
class TestFunctionalBadWeatherWithGrader(BaseFunctionalTestWithGrader):
    """
    Functional tests for the grader in a bad weather scenario.
    """

    def test_11_requirements_txt_does_not_exist(self) -> None:
        """
        Verify that the grader handles the absence of requirements.txt gracefully.
        """
        # Arrange
        command = build_command(project_path=self.clone_path)

        if os.path.exists(os.path.join(self.clone_path, "requirements.txt")):
            os.remove(os.path.join(self.clone_path, "requirements.txt"))

        if os.path.exists(os.path.join(self.clone_path, "pyproject.toml")):
            os.remove(os.path.join(self.clone_path, "pyproject.toml"))

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=0, target_check="requirements", grader_output=run_stdout))

    def test_12_no_config_provided(self) -> None:
        """
        Verify that the grader handles the absence of a configuration file gracefully.
        """
        # Arrange
        random_config_path = "/tmp/nonexistent_config.json"
        command = build_command(project_path=self.clone_path, config_file=random_config_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no config is provided")
        self.assertIn("Configuration file not found", run_result.stdout)

    def test_13_no_student_id_in_output(self) -> None:
        """
        Verify that the student ID is not included in the output when no student ID is provided.
        """
        # Arrange
        unexpected_output = "Running checks for student"
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertNotIn(
            unexpected_output, run_result.stdout, f"Unexpected output '{unexpected_output}' found in the tool's output"
        )

    def test_14_no_project_path_provided(self) -> None:
        """
        Verify that the grader handles the absence of a project path gracefully.
        """
        # Arrange
        command = build_command(project_path=None)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no project path is provided")
        self.assertIn("error: the following arguments are required: project_root", run_result.stderr)

    def test_15_invalid_project_path(self) -> None:
        """
        Verify that the grader handles an invalid project path gracefully.
        """
        # Arrange
        invalid_path = "/tmp/invalid_project_path"
        if os.path.exists(invalid_path):
            shutil.rmtree(invalid_path)

        command = build_command(project_path=invalid_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code for invalid project path")
        self.assertIn("Project root directory does not exist", run_result.stdout)


class BaseFunctionalTestWithSampleProject(unittest.TestCase):
    """
    Base class for functional tests with a sample project.
    This class clones a sample project from GitHub.
    It provides setup and teardown methods to manage the cloned repository.
    """

    repo_url = "https://github.com/fmipython/pygrader-sample-project"
    clone_path = "/tmp/sample_project"

    def setUp(self) -> None:
        if os.path.exists(self.clone_path):
            return

        clone_result = run(["git", "clone", self.repo_url, self.clone_path])
        if clone_result.returncode != 0:
            raise RuntimeError(f"Failed to clone the repository: {clone_result.stderr}")

        # Remove the functional tests from the repo, as they cause issues and time loss.
        functional_tests_path = os.path.join(self.clone_path, "tests", "test_functional.py")
        if os.path.exists(functional_tests_path):
            os.remove(functional_tests_path)

    def tearDown(self) -> None:
        if not os.path.exists(self.clone_path):
            return

        shutil.rmtree(self.clone_path)


class TestVariousConfigsOnSampleProject(BaseFunctionalTestWithSampleProject):
    """
    Functional tests for various configurations on the sample project.
    """

    def test_01_only_pylint(self) -> None:
        """
        Verify that only the pylint check is executed when using the only_pylint.json configuration.
        """
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="only_pylint.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct(expected_score=1, target_check="pylint", grader_output=run_result.stdout),
            "Pylint check did not have the expected score of 1",
        )

    def test_02_full(self) -> None:
        """
        Verify that all checks are executed and return the expected scores when using the full.json configuration.
        """
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="full.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct(expected_score=10, target_check="requirements", grader_output=run_result.stdout)
        )
        self.assertTrue(is_score_correct(expected_score=7, target_check="pylint", grader_output=run_result.stdout))
        self.assertTrue(is_score_correct(expected_score=8, target_check="type-hints", grader_output=run_result.stdout))
        self.assertTrue(is_score_correct(expected_score=10, target_check="coverage", grader_output=run_result.stdout))

    def test_03_full_single_point(self) -> None:
        """
        Verify that all checks return a score of 1 when using the full_single_point.json configuration.
        """
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="full_single_point.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct(expected_score=1, target_check="requirements", grader_output=run_result.stdout)
        )
        self.assertTrue(is_score_correct(expected_score=1, target_check="pylint", grader_output=run_result.stdout))
        self.assertTrue(is_score_correct(expected_score=1, target_check="type-hints", grader_output=run_result.stdout))
        self.assertTrue(is_score_correct(expected_score=1, target_check="coverage", grader_output=run_result.stdout))

    def test_04_structure(self) -> None:
        """
        Verify that the structure check is executed and returns the expected result
            when using the structure.json configuration.
        """
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="structure.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_non_scored_check_correct(
                expected_result=True, target_check="structure", grader_output=run_result.stdout
            )
        )

    @unittest.skip("The tests for sample_project are not in the repo")
    def test_05_tests(self) -> None:
        """
        Verify that the tests are executed and return the expected score when using the tests.json configuration.
        """
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="tests.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(is_score_correct(expected_score=13, target_check="tests", grader_output=run_result.stdout))

    def test_06_2024(self) -> None:
        """
        Verify that the checks are executed and return the expected scores when using the 2024.json configuration.
        """
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="2024.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)

        self.assertTrue(is_score_correct(expected_score=2, target_check="pylint", grader_output=run_result.stdout))
        self.assertTrue(is_score_correct(expected_score=3, target_check="type-hints", grader_output=run_result.stdout))
        self.assertTrue(is_score_correct(expected_score=5, target_check="coverage", grader_output=run_result.stdout))
        self.assertTrue(
            is_score_correct(expected_score=1, target_check="requirements", grader_output=run_result.stdout)
        )


class TestRemoteTests(BaseFunctionalTestWithSampleProject):
    """
    Functional tests for the remote tests in the sample project.
    """

    def test_01_remote_tests(self) -> None:
        """
        Verify that the remote tests are executed and return the expected score
            when using the tests.json configuration.
        """
        # Arrange
        path_to_tests = os.path.join(self.clone_path, "tests", "test_sample_code.py")
        os.remove(path_to_tests)

        command = build_command(project_path=self.clone_path, config_file="tests.json")

        # Act
        run_result = run(command)

        # input("press any key to continue...")

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(is_score_correct(expected_score=13.5, target_check="tests", grader_output=run_result.stdout))


class TestZipFileOnSampleProject(BaseFunctionalTestWithSampleProject):
    def test_01_zip_archive_passed(self) -> None:
        """
        Verify that when passing a zip version of the project, it is graded.
        """
        # Arrange
        folder_path = Path(self.clone_path)
        zip_path = folder_path / "project.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for entry in folder_path.rglob("*"):
                if entry.is_file():
                    zip_file.write(entry, entry.relative_to(folder_path))

        command = build_command(project_path=str(zip_path), config_file="only_pylint.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct(expected_score=1, target_check="pylint", grader_output=run_result.stdout),
            "Pylint check did not have the expected score of 1",
        )


def build_command(
    project_path: Optional[str], config_file: str = "full.json", student_id: Optional[str] = None
) -> list[str]:
    """
    Build the command to run the grader with the specified configuration and project path.

    :param project_path: The path to the project to be graded.
    :param config_file: The configuration file to use, defaults to "full.json".
    :param student_id: The ID of the student being graded, defaults to None.
    :return: A list of command-line arguments to run the grader.
    """
    python_binary = "python3" if os.name == "posix" else "python"
    grader_entrypoint = "pygrader.py"

    full_config_path = os.path.join(const.CONFIG_DIR, config_file)
    base_command = [python_binary, os.path.join(const.ROOT_DIR, grader_entrypoint)]

    command = base_command + ["--config", full_config_path]
    if project_path is not None:
        command += [project_path]
    if student_id is not None:
        command += ["--student-id", student_id]
    return command


def is_score_correct(expected_score: float, target_check: str, grader_output: str) -> bool:
    """
    Check if the score for a specific check in the grader output matches the expected score.

    :param expected_score: The expected score for the check.
    :param target_check: The name of the check to verify.
    :param grader_output: The output from the grader.
    :return: True if the score matches, False otherwise.
    """
    lines = grader_output.split("\n")

    score_lines = [line for line in lines if line.startswith("Check")]
    score_line = next(line for line in score_lines if target_check in line)

    # Example: "Check: coverage, Score: 8/10"
    actual_score = float(score_line.split(",")[1].split(":")[1].split("/")[0].strip())

    return actual_score == expected_score


def is_non_scored_check_correct(expected_result: bool, target_check: str, grader_output: str) -> bool:
    """
    Check if the result of a non-scored check in the grader output matches the expected result.

    :param expected_result: The expected result for the check.
    :param target_check: The name of the check to verify.
    :param grader_output: The output from the grader.
    :return: True if the result matches, False otherwise.
    """
    lines = grader_output.split("\n")

    score_lines = [line for line in lines if line.startswith("Check")]
    score_line = next(line for line in score_lines if target_check in line)

    # Example: "Check: structure, Result: False"
    actual_result = score_line.split(",")[1].split(":")[1].strip()

    return actual_result == str(expected_result)
