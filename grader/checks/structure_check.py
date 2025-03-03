"""
Module containing the structure check.
It checks if the project structure is correct.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

from grader.checks.abstract_check import AbstractCheck, CheckError
from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")


# TODO - This whole thing can be re-used to extract tests, source code, etc.
# Still need to think about how though.

# TODO - It also needs to work with multiple structures, depending on the project type.


@dataclass
class StructureInformation:
    """
    Dataclass representing the structure information.
    """

    name: str
    required: bool
    patterns: list[str]


class StructureCheck(AbstractCheck):
    """
    The Structure check class.
    """

    def __init__(self, name, max_points, project_root, structure_file: str):
        super().__init__(name, max_points, project_root)
        self.__structure_file = structure_file

    def run(self) -> float:
        """
        Run the structure check on the project.

        Load the structure file, then check if the structure is valid.

        :raises CheckError: If the structure is invalid
        :return: The score from the structure check
        :rtype: float
        """
        structure_elements = StructureCheck.__load_structure_file(self.__structure_file)

        for element in structure_elements:
            is_element_valid = self.__is_structure_valid(element)

            logger.log(VERBOSE, "Is %s structure valid ? %s", element.name, is_element_valid)

            if element.required and not is_element_valid:
                raise CheckError(f"Structure check failed: {element.name}")  # TODO - Not sure about this

        return 0.0

    @staticmethod
    def __load_structure_file(filepath: str) -> list[StructureInformation]:
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
            elements = [build_structure_information(value) for value in raw_structure.values()]
        except KeyError as error:
            raise CheckError(f"Invalid structure file: {error}") from error
        return elements

    def __is_structure_valid(self, structure_element: StructureInformation) -> bool:
        """
        A structure is valid if all patterns match at least one file in the project.

        :param structure_element: The structure element to check
        :type structure_element: StructureInformation
        :return: Whether the structure is valid
        :rtype: bool
        """
        path = Path(self._project_root)
        for pattern in structure_element.patterns:
            if not any(path.glob(pattern)):
                return False
        return True


def build_structure_information(raw_object: dict) -> StructureInformation:
    """
    Parse the YAML contents into a StructureInformation object.

    :param raw_object: The read YAML object
    :type raw_object: dict
    :return: The parsed structure information
    :rtype: StructureInformation
    """
    name = raw_object["name"]
    required = raw_object["required"]
    patterns = raw_object["patterns"]

    return StructureInformation(name, required, patterns)
