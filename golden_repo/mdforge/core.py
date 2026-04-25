"""Top-level API functions for mdforge."""

import json
from pathlib import Path

from mdforge.parser import parse
from mdforge.transform.toc import generate_toc as _generate_toc
from mdforge.transform.html import to_html
from mdforge.transform.stats import compute_stats as _compute_stats
from mdforge.transform.stats import aggregate_stats
from mdforge.validator import validate_corpus
from mdforge.utils.fileio import read_file, read_directory, write_file


def parse_file(file_path: str) -> dict:
    """Parse a single Markdown file and return its full metadata."""
    content = read_file(file_path)
    return parse(content, file_path)


def generate_toc_for_file(file_path: str) -> str:
    """Generate a table of contents for a single file."""
    content = read_file(file_path)
    parsed = parse(content, file_path)
    return _generate_toc(parsed["headings"])


def convert_to_html(file_path: str) -> str:
    """Convert a Markdown file to simplified HTML."""
    content = read_file(file_path)
    return to_html(content)


def compute_stats_for_path(target_path: str) -> dict:
    """Compute statistics for a file or directory."""
    files = _resolve_files(target_path)
    all_stats = []

    for fp in files:
        content = read_file(fp)
        parsed = parse(content, fp)
        all_stats.append(_compute_stats(parsed, fp))

    return aggregate_stats(all_stats)


def validate_links(dir_path: str) -> dict:
    """Validate internal links across a directory of Markdown files."""
    files = read_directory(dir_path)
    corpus = {}

    for fp in files:
        content = read_file(fp)
        corpus[fp] = parse(content, fp)

    return validate_corpus(corpus)


def batch_process(input_dir: str, output_dir: str) -> dict:
    """Batch process a directory: parse all files and write JSON metadata."""
    files = read_directory(input_dir)
    results = {"processed": 0, "failed": 0, "errors": []}

    for fp in files:
        try:
            content = read_file(fp)
            parsed = parse(content, fp)
            file_stats = _compute_stats(parsed, fp)
            file_toc = _generate_toc(parsed["headings"])

            output = {
                "file": fp,
                "metadata": parsed["frontmatter"],
                "headings": parsed["headings"],
                "links": parsed["links"],
                "codeBlocks": parsed["code_blocks"],
                "stats": file_stats,
                "toc": file_toc,
            }

            out_name = Path(fp).stem + ".json"
            out_path = str(Path(output_dir) / out_name)
            write_file(out_path, json.dumps(output, indent=2))
            results["processed"] += 1
        except Exception as err:
            results["failed"] += 1
            results["errors"].append({"file": fp, "error": str(err)})

    return results


def _resolve_files(target_path: str) -> list[str]:
    """Resolve a path to a list of Markdown files."""
    p = Path(target_path)
    if p.is_dir():
        return read_directory(target_path)
    return [target_path]