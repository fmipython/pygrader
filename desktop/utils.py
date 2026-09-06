"""Desktop pygrader utilities."""

import re
import uuid


def extract_student_id_from_path(path: str) -> str:
    """
    Extract the student ID from the project root path.

    Example: <extracted_dir>/<homework_name>/<student_id>-<student_name>_<number>_assignsubmission_file/<file>.zip
    :param path: The path to a project directory or a zip archive containing one.
    :return: The student ID extracted from the path.
    """
    pattern = re.compile(r"(.*\/)?([0-9A-Z]*)-.*\/.*")

    match pattern.match(path):
        case None:
            return str(uuid.uuid4())
        case matched:
            return matched.group(2) or str(uuid.uuid4())
