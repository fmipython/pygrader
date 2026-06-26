"""
Module containing the structure check.

It checks if the project structure is correct.
"""

import json
import logging
from typing import Optional

from grader.checks.abstract_check import CheckError, NonScoredCheck, NonScoredCheckResult
from grader.utils.external_resources import download_file_from_url, is_resource_remote
from grader.utils.logger import VERBOSE
from grader.utils.structure_validator import StructureValidator

logger = logging.getLogger("grader")


class StructureCheck(NonScoredCheck):
    """The Structure check class."""

    def __init__(
        self,
        name: str,
        project_root: str,
        structure_file: str,
        is_fatal: bool = False,
        is_venv_required: bool = False,
        env_vars: Optional[dict[str, str]] = None,
    ):
        """
        Initialize the structure check.

        :param name: The name of the check.
        :param project_root: The root directory of the project.
        :param structure_file: Path to the structure configuration file.
        :param is_fatal: Whether the check is fatal.
        :param is_venv_required: Whether a virtual environment is required.
        :param env_vars: Optional environment variables for the check.
        """
        super().__init__(name, project_root, is_fatal, is_venv_required, env_vars)
        self.__structure_file = structure_file

    def run(self) -> NonScoredCheckResult:
        """
        Run the structure check on the project.

        Load the structure file, then check if the structure is valid.

        :raises CheckError: If the structure is invalid
        :return: The score from the structure check
        :rtype: float
        """
        self._pre_run()
        # TODO - this can be simplified
        self.__structure_file = (
            self.__structure_file
            if not is_resource_remote(self.__structure_file)
            else download_file_from_url(self.__structure_file)
        )
        structure_elements = StructureCheck.__load_structure_file(self.__structure_file)

        for element in structure_elements:
            is_element_valid = element.is_structure_valid(self._project_root)

            logger.log(VERBOSE, "Is %s structure valid ? %s", element.name, is_element_valid)

            if element.required and not is_element_valid:
                return NonScoredCheckResult(self.name, False, f"Structure for '{element.name}' is invalid.", "")

        return NonScoredCheckResult(self.name, True, "Structure is valid", "")

    @staticmethod
    def __load_structure_file(filepath: str) -> list[StructureValidator]:
        """
        Read the structure JSON file and return the structure information.

        :param filepath: The path to the structure file
        :type filepath: str
        :raises CheckError: If the structure file is invalid
        :return: The structure information
        :rtype: list[StructureInformation]
        """
        # TODO - Simplify
        filepath = filepath if not is_resource_remote(filepath) else download_file_from_url(filepath)

        try:
            with open(filepath, "r", encoding="utf-8") as file_pointer:
                raw_structure = json.load(file_pointer)
        except json.JSONDecodeError as error:
            raise CheckError(f"Invalid structure file: {error}") from error
        except OSError as error:
            raise CheckError(f"Cannot read structure file: {error}") from error

        try:
            elements = [StructureValidator.from_dict(value) for value in raw_structure.values()]
        except KeyError as error:
            raise CheckError(f"Invalid structure file: {error}") from error
        return elements
