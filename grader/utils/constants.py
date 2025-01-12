"""
Module containing the constants
"""

import os

VERSION = "1.0.0"

# Directories
ROOT_DIR = os.path.dirname(os.path.realpath(__name__))
REPORTS_TEMP_DIR = os.path.join(ROOT_DIR, "reports")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")

# Python
PYTHON_BIN_WINDOWS = "python"
PYTHON_BIN_UNIX = "python3"

PYTHON_BIN = PYTHON_BIN_WINDOWS if os.name == "nt" else PYTHON_BIN_UNIX

# Pylint constants
PYLINTRC = os.path.join(CONFIG_DIR, "2024.pylintrc")

# Type hints constants
MYPY_TYPE_HINT_CONFIG = os.path.join(ROOT_DIR, "config", "mypy_type_hints_2024.ini")
MYPY_LINE_COUNT_REPORT = os.path.join(REPORTS_TEMP_DIR, "linecount.txt")

# Virtual environment constants
REQUIREMENTS_FILENAME = "requirements.txt"
VENV_NAME = ".venv"
POSSIBLE_VENV_DIRS = ["venv", ".venv"]
PIP_PATH_WINDOWS = os.path.join("Scripts", "pip.exe")
PIP_PATH_UNIX = os.path.join("bin", "pip")

PIP_PATH = PIP_PATH_WINDOWS if os.name == "nt" else PIP_PATH_UNIX

GRADER_REQUIREMENTS = os.path.join(CONFIG_DIR, "grader_requirements.txt")

# Coverage constants
COVERAGE_BIN = "coverage"
COVERAGE_PATH = os.path.join(VENV_NAME, "bin", COVERAGE_BIN)
COVERAGE_RUN_ARGS = ["run", "-m"]
COVERAGE_RUN_PYTEST_ARGS = ["pytest"]
COVERAGE_REPORT_ARGS = ["report", "--format=total"]

# Tests constants
POSSIBLE_TEST_DIRS = ["tests", "test", "tst"]
