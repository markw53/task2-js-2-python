"""Custom error classes for mdforge."""


class MdForgeError(Exception):
    """Custom error carrying an exit code for CLI reporting.

    Attributes:
        exit_code: Process exit code (1 for general errors, 2 for validation failures).
    """

    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code