"""
Unit tests for the CoverageCheck class in the coverage_check module.
"""

import unittest
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock

from grader.checks.abstract_check import CheckError
from grader.checks.coverage_check import CoverageCheck


class TestStrucutreCheck(unittest.TestCase):
    """
    Test cases for the CoverageCheck class.
    """
