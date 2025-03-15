"""

- Score the code for PEP-8 compliance => 100% only
- Score the code based on type-hints usage => 100% only
- Score the code based on tests code coverage => 100% only

- Support configuration files for specifying the checks to be executed

- Support configuration files for specifying the score for each check =>

- Accept a student's project path as an argument

- Accept a student's ID as an argument

- Run certain checks inside a virtual environment

- Detect source and test directories
"""

import os
import shutil
import unittest

import grader.utils.constants as const
from grader.utils.process import run


def clone_repo(repo_url, clone_path):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not os.path.exists(clone_path):
                clone_result = run(["git", "clone", repo_url, clone_path])
                if clone_result.returncode != 0:
                    raise RuntimeError(f"Failed to clone the repository: {clone_result.stderr}")
            test_result = func(*args, **kwargs)

            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
            return test_result

        return wrapper

    return decorator


class TestFunctionalGoodWeather(unittest.TestCase):
    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
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

    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_03_pylint_check(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="pylint", grader_output=run_stdout))

    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_04_type_hints_check(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=8, target_check="type-hints", grader_output=run_stdout))

    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_05_coverage_check(self):
        # Arrange
        command = build_command(project_path="/tmp/PythonProjectGrader")

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=8, target_check="coverage", grader_output=run_stdout))

    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_06_log_file_created(self):
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

    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_07_log_file_with_student_id(self):
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

    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_09_student_id_in_output(self):
        # Arrange
        student_id = "student123"
        expected_output = f"Running check for student {student_id}"
        command = build_command(project_path="/tmp/PythonProjectGrader", student_id=student_id)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertIn(
            expected_output, run_result.stdout, f"Expected output '{expected_output}' not found in the tool's output"
        )


class TestFunctionalBadWeather(unittest.TestCase):
    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_02_requirements_txt_does_not_exist(self):
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

    @clone_repo("https://github.com/fmipython/PythonProjectGrader", "/tmp/PythonProjectGrader")
    def test_08_no_config_provided(self):
        # Arrange
        random_config_path = "/tmp/nonexistent_config.json"
        command = build_command(project_path="/tmp/PythonProjectGrader", config_file=random_config_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no config is provided")
        self.assertIn("Error: No configuration file provided", run_result.stdout)


def build_command(project_path: str, config_file: str = "full.json", student_id: str = None) -> list[str]:
    python_binary = "python3" if os.name == "posix" else "python"
    grader_entrypoint = "main.py"

    full_config_path = os.path.join(const.CONFIG_DIR, config_file)
    base_command = [python_binary, os.path.join(const.ROOT_DIR, grader_entrypoint)]

    command = base_command + ["--config", full_config_path] + [project_path]
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
