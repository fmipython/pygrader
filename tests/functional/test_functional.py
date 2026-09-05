"""Module for functional tests of the grader."""

import os
import shutil
import unittest
import zipfile
from pathlib import Path
from typing import Optional

import grader.utils.constants as const
from grader.utils.process import run


class BaseFunctionalTestWithGrader(unittest.TestCase):
    """Base class for functional tests with the grader."""

    repo_url = "https://github.com/fmipython/pygrader"
    clone_path = "/tmp/pygrader-cloned"

    def setUp(self) -> None:
        """Set up test fixtures by cloning the grader repository if needed."""
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
        """Clean up test fixtures by removing the cloned repository."""
        if not os.path.exists(self.clone_path):
            return

        shutil.rmtree(self.clone_path)


@unittest.skipIf(os.name == "nt", "Test skipped on Windows")
class TestFunctionalGoodWeatherWithGrader(BaseFunctionalTestWithGrader):
    """Functional tests for the grader in a good weather scenario."""

    def test_01_full_config_single_run(self) -> None:
        """
        Verify requirements/pylint/type-hints scores, log file creation and absence of
        student id output, all from a single grader run with the default full.json config.
        """
        # Arrange
        log_file = "grader.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=10, target_check="requirements", grader_output=run_stdout))
        self.assertTrue(is_score_correct(expected_score=10, target_check="pylint", grader_output=run_stdout))
        self.assertTrue(is_score_correct(expected_score=10, target_check="type-hints", grader_output=run_stdout))
        self.assertTrue(os.path.exists(log_file), "Log file was not created")
        os.remove(log_file)
        self.assertNotIn(
            "Running checks for student", run_stdout, "Unexpected student id output found when none was provided"
        )

    @unittest.skip("Coverage check test is too unstable")
    def test_04_coverage_check(self) -> None:
        """Verify that the grader runs the coverage check and returns the expected score."""
        # Arrange
        command = build_command(project_path=self.clone_path)

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(is_score_correct(expected_score=8, target_check="coverage", grader_output=run_stdout))

    def test_06_student_id_single_run(self) -> None:
        """Verify the student-id log file name and the student-id output line from a single grader run."""
        # Arrange
        student_id = "student123"
        log_file = f"{student_id}.log"
        expected_output = f"Running checks for student {student_id}"
        if os.path.exists(log_file):
            os.remove(log_file)
        command = build_command(project_path=self.clone_path, student_id=student_id)

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(os.path.exists(log_file), f"Log file with student ID '{student_id}' was not created")
        os.remove(log_file)
        self.assertIn(
            expected_output, run_result.stdout, f"Expected output '{expected_output}' not found in the tool's output"
        )

    @unittest.skip("Unstable test")
    def test_09_all_checks_score_one(self) -> None:
        """Verify that all checks return a score of 1 when using the full_single_point.json configuration."""
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
        """Verify that only the pylint check is executed when using the only_pylint.json configuration."""
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

    def test_13_checks_flag_selects_subset(self) -> None:
        """Verify that --checks limits execution to the requested checks from the full config."""
        # Arrange
        command = build_command(project_path=self.clone_path, checks=["requirements"])

        # Act
        run_result = run(command)

        run_returncode = run_result.returncode
        run_stdout = run_result.stdout

        # Assert
        self.assertEqual(run_returncode, 0, run_stdout)
        self.assertTrue(
            is_score_correct(expected_score=10, target_check="requirements", grader_output=run_stdout),
            "Requirements check did not have the expected score of 10",
        )
        for check in ["pylint", "type-hints", "coverage"]:
            self.assertNotIn(f"Check: {check}", run_stdout, f"Unexpected check '{check}' was executed")


@unittest.skipIf(os.name == "nt", "Test skipped on Windows")
class TestFunctionalBadWeatherWithGrader(BaseFunctionalTestWithGrader):
    """Functional tests for the grader in a bad weather scenario."""

    def test_11_requirements_txt_does_not_exist(self) -> None:
        """Verify that the grader handles the absence of requirements.txt gracefully."""
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
        """Verify that the grader handles the absence of a configuration file gracefully."""
        # Arrange
        random_config_path = "/tmp/nonexistent_config.json"
        command = build_command(project_path=self.clone_path, config_file=random_config_path)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no config is provided")
        self.assertIn("Configuration file not found", run_result.stdout)

    def test_14_no_project_path_provided(self) -> None:
        """Verify that the grader handles the absence of a project path gracefully."""
        # Arrange
        command = build_command(project_path=None)

        # Act
        run_result = run(command)

        # Assert
        self.assertNotEqual(run_result.returncode, 0, "Expected non-zero return code when no project path is provided")
        self.assertIn("error: the following arguments are required: project_root", run_result.stderr)

    def test_15_invalid_project_path(self) -> None:
        """Verify that the grader handles an invalid project path gracefully."""
        # Arrange
        invalid_path = "/tmp/invalid_project_path"
        if os.path.exists(invalid_path):
            shutil.rmtree(invalid_path)

        command = build_command(project_path=invalid_path)

        # Act
        run_result = run(command)

        # Assert
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
        """Set up test fixtures by cloning the sample project repository if needed."""
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
        """Clean up test fixtures by removing the cloned repository."""
        if not os.path.exists(self.clone_path):
            return

        shutil.rmtree(self.clone_path)


class TestVariousConfigsOnSampleProject(BaseFunctionalTestWithSampleProject):
    """Functional tests for various configurations on the sample project."""

    def test_01_only_pylint(self) -> None:
        """Verify that only the pylint check is executed when using the only_pylint.json configuration."""
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
        """Verify that all checks are executed and return the expected scores when using the full.json configuration."""
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
        """Verify that all checks return a score of 1 when using the full_single_point.json configuration."""
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
        Verify that the structure check is executed and returns the expected result.

        Uses the structure.json configuration.
        """
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="structure.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_non_scored_check_correct(expected_result=True, target_check="structure", grader_output=run_result.stdout)
        )

    @unittest.skip("The tests for sample_project are not in the repo")
    def test_05_tests(self) -> None:
        """Verify that the tests are executed and return the expected score when using the tests.json configuration."""
        # Arrange
        command = build_command(project_path=self.clone_path, config_file="tests.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(is_score_correct(expected_score=13, target_check="tests", grader_output=run_result.stdout))

    def test_06_2024(self) -> None:
        """Verify that the checks are executed and return the expected scores when using the 2024.json configuration."""
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
    """Functional tests for the remote tests in the sample project."""

    def test_01_remote_tests(self) -> None:
        """
        Verify that the remote tests are executed and return the expected score.

        Uses the tests.json configuration.
        """
        # Arrange
        path_to_tests = os.path.join(self.clone_path, "tests", "test_sample_code.py")

        if os.path.exists(path_to_tests):
            os.remove(path_to_tests)

        command = build_command(project_path=self.clone_path, config_file="tests.json")

        # Act
        run_result = run(command)

        # input("press any key to continue...")

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(is_score_correct(expected_score=13.5, target_check="tests", grader_output=run_result.stdout))


class TestZipFileOnSampleProject(BaseFunctionalTestWithSampleProject):
    """Tests for grading zip file archives."""

    def test_01_zip_archive_passed(self) -> None:
        """Verify that when passing a zip version of the project, it is graded."""
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


class TestMultipleProjectsSupport(BaseFunctionalTestWithSampleProject):
    """
    Functional tests for grading several submissions in one run via a glob project_root.

    Submissions are laid out the way a Moodle bulk download does:
    ``<batch_dir>/<student_id>-<name>_<number>_assignsubmission_file/<archive>.zip``, since
    that's the shape ``desktop.utils.extract_student_id_from_path`` expects.
    """

    def setUp(self) -> None:
        """Set up the sample project checkout plus a scratch directory for batch fixtures."""
        super().setUp()
        self.batch_dir = Path(self.clone_path).parent / "batch_projects"
        if self.batch_dir.exists():
            shutil.rmtree(self.batch_dir)
        self.batch_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        """Clean up the batch scratch directory in addition to the sample project checkout."""
        if self.batch_dir.exists():
            shutil.rmtree(self.batch_dir)
        super().tearDown()

    def test_01_same_filename_archives_are_graded_independently(self) -> None:
        """
        Verify each submission is graded with its own folder-derived student id and its own
        score, even though every submission's archive shares the same filename - the common
        case when grading a Moodle bulk download.
        """
        # Arrange
        clean_source = Path(self.clone_path)
        _zip_directory(clean_source, self.batch_dir / "CLEANID-Student_One_11111_assignsubmission_file" / "project.zip")

        broken_source = self.batch_dir / "_broken_source"
        shutil.copytree(clean_source, broken_source)
        (broken_source / "src" / "bad_lint.py").write_text(
            "import os,sys,re,json,time,random,string,math,collections,itertools\n"
            "x=1\n"
            "y=2\n"
            "z=3\n"
            "def f(a,b):\n"
            " return a+b\n"
            "def g(a,b):\n"
            " return a-b\n"
            "class c:\n"
            " def m(self,a):\n"
            "  return a\n"
            "try:\n"
            " pass\n"
            "except:\n"
            " pass\n"
        )
        _zip_directory(
            broken_source, self.batch_dir / "BROKENID-Student_Two_22222_assignsubmission_file" / "project.zip"
        )

        command = build_command(project_path=str(self.batch_dir / "*" / "project.zip"), config_file="only_pylint.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct_for_run(
                expected_score=1, target_check="pylint", run_id="CLEANID", grader_output=run_result.stdout
            ),
            "Clean submission did not keep its own pylint score",
        )
        self.assertTrue(
            is_score_correct_for_run(
                expected_score=0, target_check="pylint", run_id="BROKENID", grader_output=run_result.stdout
            ),
            "Broken submission did not get its own (lower) pylint score - archives may be overwriting each other",
        )

    def test_02_venv_failure_for_one_project_does_not_stop_the_batch(self) -> None:
        """Verify that a submission whose dependencies fail to install doesn't block the rest of the batch."""
        # Arrange
        good_source = Path(self.clone_path)
        _zip_directory(good_source, self.batch_dir / "GOODID-Student_One_11111_assignsubmission_file" / "project.zip")

        bad_source = self.batch_dir / "_bad_source"
        shutil.copytree(good_source, bad_source)
        with open(bad_source / "requirements.txt", "a", encoding="utf-8") as requirements_file:
            requirements_file.write("\nthis-package-definitely-does-not-exist-pygrader-test==999.999.999\n")
        _zip_directory(bad_source, self.batch_dir / "BADID-Student_Two_22222_assignsubmission_file" / "project.zip")

        command = build_command(project_path=str(self.batch_dir / "*" / "project.zip"), config_file="only_pylint.json")

        # Act
        run_result = run(command)

        # Assert
        self.assertEqual(run_result.returncode, 0, run_result.stdout)
        self.assertTrue(
            is_score_correct_for_run(
                expected_score=1, target_check="pylint", run_id="GOODID", grader_output=run_result.stdout
            ),
            "Good submission was not graded despite the other submission's venv failure",
        )
        self.assertNotIn(
            "Run ID: BADID",
            run_result.stdout,
            "Submission with an unresolvable dependency should not have produced any results",
        )


def build_command(
    project_path: Optional[str],
    config_file: str = "full.json",
    student_id: Optional[str] = None,
    checks: Optional[list[str]] = None,
) -> list[str]:
    """
    Build the command to run the grader with the specified configuration and project path.

    :param project_path: The path to the project to be graded.
    :param config_file: The configuration file to use, defaults to "full.json".
    :param student_id: The ID of the student being graded, defaults to None.
    :param checks: The names of the checks to run, defaults to None (runs all checks).
    :return: A list of command-line arguments to run the grader.
    """
    grader_entrypoint = "pygrader.py"

    full_config_path = os.path.join(const.CONFIG_DIR, config_file)
    base_command = ["uv", "run", os.path.join(const.ROOT_DIR, grader_entrypoint)]

    command = base_command + ["--config", full_config_path]
    if project_path is not None:
        command += [project_path]
    if student_id is not None:
        command += ["--student-id", student_id]
    if checks is not None:
        command += ["--checks", ",".join(checks)]
    return command


def _zip_directory(source_dir: Path, zip_path: Path) -> None:
    """
    Zip the contents of a directory, creating the archive's parent directory if needed.

    :param source_dir: The directory whose contents should be zipped.
    :param zip_path: The destination path for the zip archive.
    """
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for entry in source_dir.rglob("*"):
            if entry.is_file():
                zip_file.write(entry, entry.relative_to(source_dir))


def is_score_correct_for_run(expected_score: float, target_check: str, run_id: str, grader_output: str) -> bool:
    """
    Check if the score for a specific check, within a specific run, matches the expected score.

    Unlike :func:`is_score_correct`, this scopes the lookup to a single run id, which is
    required when the output contains results for several projects (batch/glob grading).

    :param expected_score: The expected score for the check.
    :param target_check: The name of the check to verify.
    :param run_id: The run id (e.g. student id) whose result should be checked.
    :param grader_output: The output from the grader.
    :return: True if the score matches, False otherwise.
    """
    lines = grader_output.split("\n")

    prefix = f"Run ID: {run_id}, Check: {target_check},"
    score_line = next(line for line in lines if line.startswith(prefix))

    # Example: "Run ID: CLEANID, Check: pylint, Score: 1/1"
    actual_score = float(score_line.split(",")[2].split(":")[1].split("/")[0].strip())

    return actual_score == expected_score


def is_score_correct(expected_score: float, target_check: str, grader_output: str) -> bool:
    """
    Check if the score for a specific check in the grader output matches the expected score.

    :param expected_score: The expected score for the check.
    :param target_check: The name of the check to verify.
    :param grader_output: The output from the grader.
    :return: True if the score matches, False otherwise.
    """
    lines = grader_output.split("\n")

    score_lines = [line for line in lines if "Check:" in line and "Score:" in line]

    print(score_lines)
    score_line = next(line for line in score_lines if target_check in line)

    # Example: "Run ID: None, Check: coverage, Score: 8/10"
    actual_score = float(score_line.split(",")[2].split(":")[1].split("/")[0].strip())

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

    score_lines = [line for line in lines if "Check" in line]
    score_line = next(line for line in score_lines if target_check in line)

    # Example: "Run ID: None, Check: structure, Result: True"
    actual_result = score_line.split(",")[2].split(":")[1].strip()

    return actual_result == str(expected_result)
