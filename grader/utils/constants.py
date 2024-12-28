"""
Module containing the constants
"""

import os

ROOT_DIR = os.path.dirname(os.path.realpath(__name__))

REPORTS_TEMP_DIR = os.path.join(ROOT_DIR, "reports")

MYPY_TYPE_HINT_CONFIG = os.path.join(ROOT_DIR, "config", "mypy_type_hints_2024.ini")
MYPY_LINE_COUNT_REPORT = os.path.join(REPORTS_TEMP_DIR, "linecount.txt")


REQUIREMENTS_FILENAME = "requirements.txt"
