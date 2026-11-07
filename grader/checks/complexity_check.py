"""
Module containing the complexity check.

It uses the complexipy python library directly to measure the cognitive complexity of each function.
"""

import logging

import complexipy

from grader.checks.abstract_check import NonScoredCheck
from grader.exceptions import CheckError, InvalidConfigError
from grader.models.check_result import NonScoredCheckResult
from grader.utils import files

logger = logging.getLogger("grader")

DEFAULT_MAX_COMPLEXITY = 15


class ComplexityCheck(NonScoredCheck):
    """The Complexity check class."""

    def __init__(
        self,
        name: str,
        project_root: str,
        max_complexity: int = DEFAULT_MAX_COMPLEXITY,
        is_fatal: bool = False,
        is_venv_required: bool = False,
        env_vars: dict[str, str] | None = None,
        assets: list[str] | None = None,
    ):
        """
        Initialize the complexity check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param max_complexity: The highest cognitive complexity a single function may have.
        :param is_fatal: Whether the check is fatal.
        :param is_venv_required: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        :param assets: Optional list of resource sources (paths, URLs or Cove URIs) for the check.
        """
        if isinstance(max_complexity, bool) or not isinstance(max_complexity, int) or max_complexity < 1:
            raise InvalidConfigError(f"max_complexity must be a positive integer, got {max_complexity!r}")

        super().__init__(name, project_root, is_fatal, is_venv_required, env_vars, assets)
        self.__max_complexity = max_complexity

    def run(self) -> NonScoredCheckResult:
        """
        Run complexipy on all source files of the project.

        The check passes when no function is more complex than the configured maximum.

        Files that cannot be parsed fail the check but do not stop the analysis of the other files.

        :raises CheckError: If the source files cannot be found.
        :returns: The result of the check, listing the offending functions in the info field.
        :rtype: NonScoredCheckResult
        """
        self._pre_run()

        try:
            source_files = files.find_all_source_files(self._project_root)
        except OSError as error:
            logger.error("Error while finding python files: %s", error)
            raise CheckError("Error while finding python files") from error

        offenders: list[str] = []
        unparsable: list[str] = []
        for source_file in source_files:
            try:
                file_complexity = complexipy.file_complexity(source_file)
            except ValueError as error:  # complexipy raises ValueError for unreadable or invalid files
                logger.warning("Could not analyse %s: %s", source_file, error)
                unparsable.append(source_file)
                continue

            offenders.extend(
                f"{source_file}:{function.line_start} {function.name} ({function.complexity})"
                for function in file_complexity.functions
                if function.complexity > self.__max_complexity
            )

        if offenders or unparsable:
            info = []
            if offenders:
                info.append(f"Functions above complexity {self.__max_complexity}: " + ", ".join(offenders))
            if unparsable:
                info.append("Could not analyse: " + ", ".join(unparsable))
            return NonScoredCheckResult(self.name, False, ". ".join(info), "")

        return NonScoredCheckResult(self.name, True, f"All functions are within complexity {self.__max_complexity}", "")
