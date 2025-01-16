"""
Factory for creating the checks objects.
"""

from grader.checks.abstract_check import AbstractCheck

from grader.checks.coverage_check import CoverageCheck
from grader.checks.pylint_check import PylintCheck
from grader.checks.requirements_check import RequirementsCheck
from grader.checks.type_hints_check import TypeHintsCheck


NAME_TO_CHECK: dict[str, type[AbstractCheck]] = {
    "coverage": CoverageCheck,
    "pylint": PylintCheck,
    "requirements": RequirementsCheck,
    "type-hints": TypeHintsCheck,
}


def create_checks(config: dict, project_root: str) -> tuple[list[AbstractCheck], list[AbstractCheck]]:
    checks = config["checks"]

    non_venv_checks = []
    venv_checks = []
    for check in checks:
        name = check["name"]
        max_points = check["max_points"]

        if name not in NAME_TO_CHECK:
            raise ValueError(f"Unknown check name: {name}")  # TODO - Replace with custom exception

        is_venv = check.get("venv", False)

        check_class = NAME_TO_CHECK[name]
        created_check = check_class(name, max_points, project_root)

        if is_venv:
            venv_checks.append(created_check)
        else:
            non_venv_checks.append(created_check)

    return non_venv_checks, venv_checks
