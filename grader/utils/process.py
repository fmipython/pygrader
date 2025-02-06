"""
Module containing a wrapper for launching shell commands
"""

import logging
import subprocess
from typing import Optional

# from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")


def run(command: list[str], current_directory: Optional[str] = None) -> subprocess.CompletedProcess[str]:
    """
    Execute a command in the terminal.
    Wraps the subprocess.run function, with the check=False, capture_output=True and text=True flags.

    If the command passes, log the stdout.
    If the command fails, log the returncode, stdout and stderr.

    :param command: The command to execute
    :return: The output of the command (returncode, stdout, stderr)
    """
    logger.debug("Running command: %s", command)
    output = subprocess.run(command, check=False, capture_output=True, text=True, cwd=current_directory)

    if output.returncode != 0:
        logger.debug("Command failed: %d %s %s", output.returncode, output.stdout, output.stderr)
    else:
        logger.debug("Command succeeded: %s", output.stdout)
    return output
