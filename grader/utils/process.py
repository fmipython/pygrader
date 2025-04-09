"""
Module containing a wrapper for launching shell commands
"""

import logging
import subprocess
import os
from typing import Optional

# from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")


def run(
    command: list[str], current_directory: Optional[str] = None, env_vars: Optional[dict[str, str]] = None
) -> subprocess.CompletedProcess[str]:
    """
    Execute a command in the terminal.
    Wraps the subprocess.run function, with the check=False, capture_output=True and text=True flags.

    If the command passes, log the stdout.
    If the command fails, log the returncode, stdout and stderr.

    :param command: The command to execute
    :param current_directory: The directory to execute the command in
    :param env_vars: A dictionary of environment variables to set for the subprocess
    :return: The output of the command (returncode, stdout, stderr)
    """
    logger.debug("Running command: %s", command)

    # Prepare the environment variables
    if env_vars is not None:
        env_vars.update(os.environ.copy())

    output = subprocess.run(command, check=False, capture_output=True, text=True, cwd=current_directory, env=env_vars)

    if output.returncode != 0:
        logger.debug("Command failed: %d %s %s", output.returncode, output.stdout, output.stderr)
    else:
        logger.debug("Command succeeded: %s", output.stdout)
    return output


def extend_env_variable(variable: str, value: str) -> dict[str, str]:
    """
    Extend an environment variable with a new value.

    :param variable: The name of the environment variable to extend
    :param value: The value to append to the environment variable
    :return: A dictionary with the updated environment variable
    """
    env = os.environ.copy()
    env[variable] = f"{env.get(variable, '')}:{value}"
    return env
