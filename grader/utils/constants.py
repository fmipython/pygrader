"""
Module containing the constants
"""

import os
from importlib.metadata import version

VERSION = version("pygrader")


# Directories
ROOT_DIR = os.path.dirname(os.path.realpath(__name__))
REPORTS_TEMP_DIR = os.path.join(ROOT_DIR, "reports")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
TEMP_FILES_DIR = os.path.join(ROOT_DIR, "temp_files")  # TODO - Change this to be under WORK_DIR ?

WORK_DIR = os.path.join("/tmp", "pygrader")

# Python
PYTHON_BIN_WINDOWS = "python.exe"
PYTHON_BIN_UNIX = "python3"

PYTHON_BIN = PYTHON_BIN_WINDOWS if os.name == "nt" else PYTHON_BIN_UNIX


# Virtual environment constants
REQUIREMENTS_FILENAME = "requirements.txt"
PYPROJECT_FILENAME = "pyproject.toml"
VENV_NAME = ".venv-pygrader"
POSSIBLE_VENV_DIRS = ["venv", ".venv"]
PIP_PATH_WINDOWS = os.path.join("Scripts", "pip.exe")
PIP_PATH_UNIX = os.path.join("bin", "pip")

PIP_PATH = PIP_PATH_WINDOWS if os.name == "nt" else PIP_PATH_UNIX

GRADER_REQUIREMENTS = os.path.join(CONFIG_DIR, "grader_requirements.txt")

# Type hints constants
MYPY_BIN_WINDOWS = "mypy.exe"
MYPY_BIN_UNIX = "mypy"
MYPY_BIN = MYPY_BIN_WINDOWS if os.name == "nt" else MYPY_BIN_UNIX

MYPY_TYPE_HINT_CONFIG = os.path.join(ROOT_DIR, "config", "mypy_type_hints_2024.ini")
MYPY_LINE_COUNT_REPORT = os.path.join(REPORTS_TEMP_DIR, "linecount.txt")
MYPY_PATH_WINDOWS = os.path.join(VENV_NAME, "Scripts", MYPY_BIN)
MYPY_PATH_UNIX = os.path.join(VENV_NAME, "bin", MYPY_BIN)
MYPY_PATH = MYPY_PATH_WINDOWS if os.name == "nt" else MYPY_PATH_UNIX


# Pylint constants
PYLINT_BIN_WINDOWS = os.path.join("Scripts", "pylint.exe")
PYLINT_BIN_UNIX = os.path.join("bin", "pylint")
PYLINT_BIN = PYLINT_BIN_WINDOWS if os.name == "nt" else PYLINT_BIN_UNIX
PYLINT_PATH = os.path.join(VENV_NAME, PYLINT_BIN)
PYLINTRC = os.path.join(CONFIG_DIR, "2024.pylintrc")

# Pytest constants
PYTEST_BIN_WINDOWS = "pytest.exe"
PYTEST_BIN_UNIX = "pytest"
PYTEST_BIN = PYTEST_BIN_WINDOWS if os.name == "nt" else PYTEST_BIN_UNIX

PYTEST_PATH_WINDOWS = os.path.join(VENV_NAME, "Scripts", PYTEST_BIN)
PYTEST_PATH_UNIX = os.path.join(VENV_NAME, "bin", PYTEST_BIN)
PYTEST_PATH = PYTEST_PATH_WINDOWS if os.name == "nt" else PYTEST_PATH_UNIX
PYTEST_ARGS = ["--no-header", "-r A"]
PYTEST_ROOT_DIR_ARG = "--rootdir={}"

PYTEST_CACHE = ".pytest_cache"

# Coverage constants
COVERAGE_BIN_WINDOWS = "coverage.exe"
COVERAGE_BIN_UNIX = "coverage"
COVERAGE_BIN = COVERAGE_BIN_WINDOWS if os.name == "nt" else COVERAGE_BIN_UNIX

COVERAGE_PATH_WINDOWS = os.path.join(VENV_NAME, "Scripts", COVERAGE_BIN)
COVERAGE_PATH_UNIX = os.path.join(VENV_NAME, "bin", COVERAGE_BIN)
COVERAGE_PATH = COVERAGE_PATH_WINDOWS if os.name == "nt" else COVERAGE_PATH_UNIX
COVERAGE_RUN_ARGS = ["run", "-m"]
COVERAGE_RUN_PYTEST_ARGS = ["pytest"]
COVERAGE_REPORT_ARGS = ["report", "--format=total"]
COVERAGE_REPORT_ARGS_NO_FORMAT = ["report"]

COVERAGE_FILE = ".coverage"

# Tests constants
POSSIBLE_TEST_DIRS = ["tests", "test", "tst"]


# Ignore paths
IGNORE_DIRS = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    "_MACOSX",
    os.path.join("build", "lib"),
    *POSSIBLE_VENV_DIRS,
]
