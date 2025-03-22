"""
Module containing the StructureValidator class.
"""

from pathlib import Path


class StructureValidator:
    """
    Class representing the structure information.
    """

    def __init__(self, name: str, required: bool, patterns: list[str]):
        self.name = name
        self.required = required
        self.patterns = patterns

    def is_structure_valid(self, project_root: str) -> bool:
        """
        A structure is valid if all patterns match at least one file in the project.

        :param project_root: The root directory of the project
        :type project_root: str
        :return: Whether the structure is valid
        :rtype: bool
        """
        path = Path(project_root)
        for pattern in self.patterns:
            if not any(path.glob(pattern)):
                return False
        return True

    def get_matching_files(self, project_root: str) -> list[str]:
        """
        Get the paths of all files that match the patterns.

        :param project_root: The root directory of the project
        :type project_root: str
        :return: A list of paths to files matching the patterns
        :rtype: list[str]
        """
        path = Path(project_root)
        return [str(file.resolve()) for pattern in self.patterns for file in path.glob(pattern)]

    @staticmethod
    def from_dict(raw_object: dict) -> "StructureValidator":
        """
        Parse a dictionary into a StructureInformation object.

        :param raw_object: The dictionary containing structure information
        :type raw_object: dict
        :return: The parsed structure information
        :rtype: StructureInformation
        """
        name = raw_object["name"]
        required = raw_object["required"]
        patterns = raw_object["patterns"]

        return StructureValidator(name, required, patterns)
