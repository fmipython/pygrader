import os
import shutil
import unittest

from typing import Optional

import grader.utils.constants as const
from grader.utils.process import run


class BaseFunctionalTestWithGrader(unittest.TestCase):
    repo_url = "https://github.com/fmipython/PythonProjectGrader"
    clone_path = "/tmp/PythonProjectGrader"

    def setUp(self):
        if os.path.exists(self.clone_path):
            return

        clone_result = run(["git", "clone", self.repo_url, self.clone_path])
        if clone_result.returncode != 0:
            raise RuntimeError(f"Failed to clone the repository: {clone_result.stderr}")

        # Remove the functional tests from the repo, as they cause issues and time loss.
        functional_tests_path = os.path.join(self.clone_path, "tests", "test_functional.py")
        if os.path.exists(functional_tests_path):
            os.remove(functional_tests_path)

    def tearDown(self):
        if not os.path.exists(self.clone_path):
            return

        shutil.rmtree(self.clone_path)


@unittest.skipIf(os.name == "nt", "Test skipped on Windows")
class TestFunctionalGoodWeatherWithGrader(BaseFunctionalTestWithGrader):
    def test_01_requirements_txt_exists(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="requirements", grader_output=run_stdout))

    def test_02_pylint_check(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="pylint", grader_output=run_stdout))

    def test_03_type_hints_check(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=8, target_check="type-hints", grader_output=run_stdout))

    def test_04_coverage_check(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=8, target_check="coverage", grader_output=run_stdout))

    def test_05_log_file_created(self):
        # Arrange
        log_file = "grader.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(os.path.exists(log_file), "Log file was not created")
        os.remove(log_file)

    def test_06_log_file_with_student_id(self):
        # Arrange
        student_id = "student123"
        log_file = f"{student_id}.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path="/tmp/PythonProjectGrader", student_id=student_id)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(os.path.exists(log_file), f"Log file with student ID '{student_id}' was not created")
        os.remove(log_file)

    def test_07_student_id_in_output(self):
        # Arrange
        student_id = "student123"
        expected_output = f"Running checks for student {student_id}"
        command = build_command(project_path="/tmp/PythonProjectGrader", student_id=student_id)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertIn(
            expected_output, run_result.stdout, f"Expected output '{expected_output}' not found in the tool's output"
        )

    def test_08_default_log_file_name(self):
        # Arrange
        log_file = "grader.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(os.path.exists(log_file), "Default log file 'grader.log' was not created")
        os.remove(log_file)

    def test_09_all_checks_score_one(self):
        # Arrange
        config_file = "full_single_point.json"
        command = build_command(project_path="/tmp/PythonProjectGrader", config_file=config_file)

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

    def test_10_only_pylint_check(self):
        # Arrange
        config_file = "only_pylint.json"
        command = build_command(project_path="/tmp/PythonProjectGrader", config_file=config_file)

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
    def test_11_requirements_txt_does_not_exist(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        os.remove(os.path.join("/tmp/PythonProjectGrader", "requirements.txt"))

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=0, target_check="requirements", grader_output=run_stdout))

    def test_12_no_config_provided(self):
        # Arrange
        random_config_path = "/tmp/nonexistent_config.json"
        command = build_command(project_path="/tmp/PythonProjectGrader", config_file=random_config_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no config is provided")
        self.assertIn("Configuration file not found", run_result.stdout)

    def test_13_no_student_id_in_output(self):
        # Arrange
        unexpected_output = "Running checks for student"
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertNotIn(
            unexpected_output, run_result.stdout, f"Unexpected output '{unexpected_output}' found in the tool's output"
        )

    def test_14_no_project_path_provided(self):
        # Arrange
        command = build_command(project_path=None)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no project path is provided")
        self.assertIn("error: the following arguments are required: project_root", run_result.stderr)

    def test_15_invalid_project_path(self):
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


class TestVariousConfigsOnSampleProject(unittest.TestCase):
    def test_01_only_pylint(self):
        # Arrange
        project_path = os.path.join(const.ROOT_DIR, "tests", "sample_project")
        command = build_command(project_path=project_path, config_file="only_pylint.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct(expected_score=1, target_check="pylint", grader_output=run_result.stdout),
            "Pylint check did not have the expected score of 1",
        )

    def test_02_full(self):
        # Arrange
        project_path = os.path.join(const.ROOT_DIR, "tests", "sample_project")
        command = build_command(project_path=project_path, config_file="full.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct(expected_score=10, target_check="requirements", grader_output=run_result.stdout)
        )
        self.assertTrue(is_score_correct(expected_score=10, target_check="pylint", grader_output=run_result.stdout))
        self.assertTrue(
            is_score_correct(expected_score=10, target_check="type-hints", grader_output=run_result.stdout)
        )
        self.assertTrue(is_score_correct(expected_score=10, target_check="coverage", grader_output=run_result.stdout))

    def test_03_full_single_point(self):
        # Arrange
        project_path = os.path.join(const.ROOT_DIR, "tests", "sample_project")
        command = build_command(project_path=project_path, config_file="full_single_point.json")

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

    def test_04_structure(self):
        # Arrange
        project_path = os.path.join(const.ROOT_DIR, "tests", "sample_project")
        command = build_command(project_path=project_path, config_file="structure.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="structure", grader_output=run_result.stdout))

    def test_05_tests(self):
        # Arrange
        project_path = os.path.join(const.ROOT_DIR, "tests", "sample_project")
        command = build_command(project_path=project_path, config_file="tests.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="tests", grader_output=run_result.stdout))

    def test_06_2024(self):
        # Arrange
        project_path = os.path.join(const.ROOT_DIR, "tests", "sample_project")
        command = build_command(project_path=project_path, config_file="2024.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)

        self.assertTrue(is_score_correct(expected_score=3, target_check="pylint", grader_output=run_result.stdout))
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
