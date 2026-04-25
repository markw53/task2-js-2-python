"""File I/O utilities using pathlib."""

from pathlib import Path

from mdforge.utils.errors import MdForgeError


def read_file(file_path: str) -> str:
    """Read a file and return its content as a UTF-8 string.

    Raises:
        MdForgeError: If the file is not found or cannot be read.
    """
    p = Path(file_path)
    if not p.exists():
        raise MdForgeError(f"File not found: {file_path}", 1)
    try:
        return p.read_text(encoding="utf-8")
    except OSError as err:
        raise MdForgeError(f"Error reading file {file_path}: {err}", 1)


def read_directory(dir_path: str) -> list[str]:
    """Read all Markdown files from a directory (recursive).

    Returns a sorted list of absolute file paths.

    Raises:
        MdForgeError: If the path is not a directory or contains no Markdown files.
    """
    p = Path(dir_path)

    try:
        if not p.is_dir():
            raise MdForgeError(f"Not a directory: {dir_path}", 1)
    except OSError:
        raise MdForgeError(f"Cannot access directory: {dir_path}", 1)

    files = sorted(str(f) for f in p.rglob("*.md") if f.is_file())

    if len(files) == 0:
        raise MdForgeError(f"No Markdown files found in: {dir_path}", 1)

    return files


def write_file(file_path: str, content: str) -> None:
    """Write content to a file, creating parent directories as needed.

    Raises:
        MdForgeError: If the file cannot be written.
    """
    try:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    except OSError as err:
        raise MdForgeError(f"Error writing file {file_path}: {err}", 1)