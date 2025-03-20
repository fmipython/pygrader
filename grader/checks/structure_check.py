"""
Module containing the structure check.
It checks if the project structure is correct.
"""

import logging

import yaml

from grader.checks.abstract_check import NonScoredCheck, CheckError
from grader.utils.logger import VERBOSE
from grader.utils.structure_validator import StructureValidator

logger = logging.getLogger("grader")


# TODO - It also needs to work with multiple structures, depending on the project type.


class StructureCheck(NonScoredCheck):
    """
    The Structure check class.
    """

    def __init__(self, name: str, project_root: str, structure_file: str, is_venv_required: bool = False):
        super().__init__(name, project_root, is_venv_required)
        self.__structure_file = structure_file

    def run(self) -> bool:
        """
        Run the structure check on the project.

        Load the structure file, then check if the structure is valid.

        :raises CheckError: If the structure is invalid
        :return: The score from the structure check
        :rtype: float
        """
        structure_elements = StructureCheck.__load_structure_file(self.__structure_file)

        for element in structure_elements:
            is_element_valid = element.is_structure_valid(self._project_root)

            logger.log(VERBOSE, "Is %s structure valid ? %s", element.name, is_element_valid)

            if element.required and not is_element_valid:
                return False

        return True

    @staticmethod
    def __load_structure_file(filepath: str) -> list[StructureValidator]:
        """
        Read the structure YAML file and return the structure information.

        :param filepath: The path to the structure file
        :type filepath: str
        :raises CheckError: If the structure file is invalid
        :return: The structure information
        :rtype: list[StructureInformation]
        """
        with open(filepath, "r", encoding="utf-8") as file_pointer:
            raw_structure = yaml.safe_load(file_pointer)

        try:
            elements = [StructureValidator.from_dict(value) for value in raw_structure.values()]
        except KeyError as error:
            raise CheckError(f"Invalid structure file: {error}") from error
        return elements
