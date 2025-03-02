import logging
from dataclasses import dataclass

import yaml

from grader.checks.abstract_check import AbstractCheck, CheckError

logger = logging.getLogger("grader")


class StructureCheck(AbstractCheck):
    def __init__(self, name, max_points, project_root, structure_file: str, *args, **kwargs):
        super().__init__(name, max_points, project_root)
        self.__structure_file = structure_file

    def run(self) -> float:
        StructureCheck.__load_structure_file(self.__structure_file)
        return 0.0

    @staticmethod
    def __load_structure_file(filepath: str):
        with open(filepath, "r") as file_pointer:
            raw_structure = yaml.safe_load(file_pointer)

        print(raw_structure)
        # try:
        #     structure = __build_structure_information(raw_structure)
        # except KeyError as e:
        #     raise CheckError(f"Invalid structure file: {e}")


@dataclass
class StructureInformation:
    name: str
    required: bool
    patterns: list[str]


def __build_structure_information(raw_object: dict) -> StructureInformation:
    name = raw_object["name"]
    required = raw_object["required"]
    patterns = raw_object["patterns"]

    return StructureInformation(name, required, patterns)
