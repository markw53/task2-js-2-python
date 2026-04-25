"""Simple logging utility with colored output.

All log output goes to stderr. CLI output (JSON, HTML, TOC) goes to stdout.
"""

import sys

BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
GRAY = "\033[90m"
RESET = "\033[0m"


def info(msg: str) -> None:
    """Log an informational message."""
    print(f"{BLUE}[INFO]{RESET} {msg}", file=sys.stderr)


def success(msg: str) -> None:
    """Log a success message."""
    print(f"{GREEN}[OK]{RESET} {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    """Log a warning message."""
    print(f"{YELLOW}[WARN]{RESET} {msg}", file=sys.stderr)


def error(msg: str) -> None:
    """Log an error message."""
    print(f"{RED}[ERROR]{RESET} {msg}", file=sys.stderr)


def debug(msg: str) -> None:
    """Log a debug message (only if MDFORGE_DEBUG is set)."""
    import os
    if os.environ.get("MDFORGE_DEBUG"):
        print(f"{GRAY}[DEBUG]{RESET} {msg}", file=sys.stderr)