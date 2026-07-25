"""All custom exceptions raised across the grader package."""


class GraderError(Exception):
    """Base class for all custom exceptions raised by pygrader."""


class InvalidConfigError(GraderError):
    """Custom exception for invalid configuration files."""


class InvalidProjectRootError(GraderError):
    """Raised when the given project root directory does not exist."""


class InvalidCheckError(GraderError):
    """Custom exception for invalid check names."""


class CheckError(GraderError):
    """Custom exception for check errors."""


class VirtualEnvironmentError(GraderError):
    """Exception raised when an error occurs during the virtual environment setup."""


class ExternalResourceError(GraderError):
    """Custom exception for external resource errors."""
