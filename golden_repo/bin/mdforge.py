#!/usr/bin/env python3
"""Direct invocation entry point for mdforge CLI."""

import sys
from pathlib import Path


def main():
    # Ensure the package is importable when run directly
    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from mdforge.cli import cli
    from mdforge.utils.errors import MdForgeError
    from mdforge.utils import logger

    try:
        cli(standalone_mode=False)
    except MdForgeError as err:
        logger.error(str(err))
        sys.exit(err.exit_code)
    except SystemExit:
        raise
    except Exception as err:
        logger.error(f"Unexpected error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()