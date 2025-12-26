"""
Module for handling environment variable management and merging.
"""

import os
from typing import Optional


def merge_environment_variables(
    global_env: Optional[dict[str, str]],
    check_env: Optional[dict[str, str]],
) -> dict[str, str]:
    """
    Merge environment variables with the following priority (highest to lowest):
    1. Check-specific environment variables
    2. Global environment variables (from config)
    3. System environment variables

    :param global_env: Global environment variables from the configuration.
    :param check_env: Check-specific environment variables from the configuration.
    :return: Merged environment variables, or None if both inputs are empty/None.
    """
    if global_env is None and check_env is None:
        return {}

    merged = dict(os.environ)

    if global_env is not None:
        merged.update(global_env)

    if check_env is not None:
        merged.update(check_env)

    return merged
