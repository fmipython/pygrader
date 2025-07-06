import os
import shutil
import unittest

from typing import Optional

import grader.utils.constants as const
from grader.utils.process import run


class BaseFunctionalTestWithGrader(unittest.TestCase):
    repo_url = "https://github.com/fmipython/pygrader"
    clone_path = "/tmp/pygrader"

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
        functional_tests_path = os.path.join(self.clone_path, "tests", "test_functional.py")
        if os.path.exists(functional_tests_path):
            os.remove(functional_tests_path)

    def tearDown(self) -> None:
        if not os.path.exists(self.clone_path):
            return

        shutil.rmtree(self.clone_path)


@unittest.skipIf(os.name == "nt", "Test skipped on Windows")
class TestFunctionalGoodWeatherWithGrader(BaseFunctionalTestWithGrader):
    @unittest.skip("debug")
    def test_01_requirements_txt_exists(self) -> None:
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="requirements", grader_output=run_stdout))

    @unittest.skip("debug")
    def test_02_pylint_check(self) -> None:
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
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="type-hints", grader_output=run_stdout))

    def test_04_coverage_check(self) -> None:
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=7, target_check="coverage", grader_output=run_stdout))

    @unittest.skip("debug")
    def test_05_log_file_created(self) -> None:
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

    @unittest.skip("debug")
    def test_06_log_file_with_student_id(self) -> None:
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

    @unittest.skip("debug")
    def test_07_student_id_in_output(self) -> None:
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

    @unittest.skip("debug")
    def test_08_default_log_file_name(self) -> None:
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

    @unittest.skip("debug")
    def test_09_all_checks_score_one(self) -> None:
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

    @unittest.skip("debug")
    def test_10_only_pylint_check(self) -> None:
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
@unittest.skip("debug")
class TestFunctionalBadWeatherWithGrader(BaseFunctionalTestWithGrader):
    def test_11_requirements_txt_does_not_exist(self) -> None:
        # Arrange
        command = build_command(project_path=self.clone_path)

        os.remove(os.path.join(self.clone_path, "requirements.txt"))

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=0, target_check="requirements", grader_output=run_stdout))

    def test_12_no_config_provided(self) -> None:
        # Arrange
        random_config_path = "/tmp/nonexistent_config.json"
        command = build_command(project_path=self.clone_path, config_file=random_config_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no config is provided")
        self.assertIn("Configuration file not found", run_result.stdout)

    def test_13_no_student_id_in_output(self) -> None:
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
        # Arrange
        command = build_command(project_path=None)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no project path is provided")
        self.assertIn("error: the following arguments are required: project_root", run_result.stderr)

    def test_15_invalid_project_path(self) -> None:
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
    @unittest.skip("debug")
    def test_01_only_pylint(self) -> None:
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

    @unittest.skip("debug")
    def test_02_full(self) -> None:
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

    @unittest.skip("debug")
    def test_03_full_single_point(self) -> None:
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

    @unittest.skip("debug")
    def test_04_structure(self) -> None:
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
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="tests.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(is_score_correct(expected_score=13, target_check="tests", grader_output=run_result.stdout))

    @unittest.skip("debug")
    def test_06_2024(self) -> None:
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


def build_command(
    project_path: Optional[str], config_file: str = "full.json", student_id: Optional[str] = None
) -> list[str]:
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


def is_score_correct(expected_score: int, target_check: str, grader_output: str) -> bool:
    lines = grader_output.split("\n")

    score_lines = [line for line in lines if line.startswith("Check")]
    score_line = next(line for line in score_lines if target_check in line)

    # Example: "Check: coverage, Score: 8/10"
    actual_score = int(score_line.split(",")[1].split(":")[1].split("/")[0].strip())

    return actual_score == expected_score


def is_non_scored_check_correct(expected_result: bool, target_check: str, grader_output: str) -> bool:
    lines = grader_output.split("\n")

    score_lines = [line for line in lines if line.startswith("Check")]
    score_line = next(line for line in score_lines if target_check in line)

    # Example: "Check: structure, Result: False"
    actual_result = score_line.split(",")[1].split(":")[1].strip()

    return actual_result == str(expected_result)
