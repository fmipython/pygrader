"""Factory for creating the checks objects."""

from typing import Optional

from grader.checks.abstract_check import AbstractCheck
from grader.checks.coverage_check import CoverageCheck
from grader.checks.pylint_check import PylintCheck
from grader.checks.requirements_check import RequirementsCheck
from grader.checks.run_tests_check import RunTestsCheck
from grader.checks.structure_check import StructureCheck
from grader.checks.type_hints_check import TypeHintsCheck
from grader.exceptions import InvalidCheckError, InvalidConfigError
from grader.utils.environment import merge_environment_variables

NAME_TO_CHECK: dict[str, type[AbstractCheck]] = {
    "coverage": CoverageCheck,
    "pylint": PylintCheck,
    "requirements": RequirementsCheck,
    "type-hints": TypeHintsCheck,
    "structure": StructureCheck,
    "tests": RunTestsCheck,
}


def create_checks(
    config: dict, project_root: str, selected_checks: Optional[list[str]] = None
) -> tuple[list[AbstractCheck], list[AbstractCheck]]:
    """
    Build two lists, containing the non-venv checks and the venv checks.

    :param config: The configuration dictionary.
    :type config: dict
    :param project_root: The root of the project.
    :type project_root: str
    :param selected_checks: If provided, only checks whose "name" is in this list are built.
    :type selected_checks: Optional[list[str]]
    :raises InvalidConfigError: If no checks are found in the configuration file.
    :raises InvalidCheckError: If the check name is unknown, or a requested check is not in the config.
    :return: A tuple containing the non-venv checks and the venv checks.
    :rtype: tuple[list[AbstractCheck], list[AbstractCheck]]
    """
    if "checks" not in config:
        raise InvalidConfigError("No checks found in the configuration file")

    checks: list[dict] = config["checks"]

    if selected_checks is not None:
        checks = __filter_checks(checks, selected_checks)

    global_env = config.get("environment", {}).get("variables", {})

    non_venv_checks = []
    venv_checks = []

    expected_keys = {"name", "is_venv_required"}
    for check in checks:
        created_check = __create_check(project_root, expected_keys, check, global_env)

        is_venv = check.get("is_venv_required", False)
        if is_venv:
            venv_checks.append(created_check)
        else:
            non_venv_checks.append(created_check)

    return non_venv_checks, venv_checks


def __filter_checks(checks: list[dict], selected_checks: list[str]) -> list[dict]:
    """
    Filter the checks to only those whose "name" is in selected_checks.

    :param checks: The full list of check configurations.
    :param selected_checks: The names of the checks that should be kept.
    :raises InvalidCheckError: If a requested check name is not present in the configuration.
    :return: The filtered list of check configurations, in their original order.
    """
    available_names = {check["name"] for check in checks if "name" in check}
    unknown = set(selected_checks) - available_names

    if len(unknown) > 0:
        raise InvalidCheckError(
            f"Unknown check(s) requested: {', '.join(sorted(unknown))}. "
            f"Available in config: {', '.join(sorted(available_names))}"
        )

    return [check for check in checks if check.get("name") in selected_checks]


def __create_check(project_root: str, expected_keys: set[str], check: dict, global_env: dict) -> AbstractCheck:
    if any(key not in check for key in expected_keys):
        raise InvalidConfigError("Invalid check configuration")

    name = check["name"]

    if name not in NAME_TO_CHECK:
        raise InvalidCheckError(f"Unknown check name: {name}")

    check_env = check.get("environment", {}).get("variables", {})

    merged_env = merge_environment_variables(global_env, check_env)

    other_args = {**check}
    del other_args["name"]

    if "environment" in other_args:
        del other_args["environment"]

    other_args["env_vars"] = merged_env

    check_class = NAME_TO_CHECK[name]
    created_check = check_class(name, project_root, **other_args)

    return created_check
