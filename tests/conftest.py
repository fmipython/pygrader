"""Shared pytest fixtures."""

from collections.abc import Callable

import pytest


@pytest.fixture(name="log_output")
def fixture_log_output(caplog: pytest.LogCaptureFixture) -> Callable[[], list[str]]:
    """
    Capture everything logged below the 'grader' logger.

    Returns a callable producing the captured records formatted as 'LEVEL:logger:message'.
    """
    caplog.set_level(1, logger="grader")
    return lambda: [f"{record.levelname}:{record.name}:{record.getMessage()}" for record in caplog.records]
