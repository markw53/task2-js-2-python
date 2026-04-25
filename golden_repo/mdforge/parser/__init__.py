"""Parser package — extracts structured metadata from Markdown content."""

from mdforge.parser.frontmatter import parse_frontmatter
from mdforge.parser.headings import extract_headings, generate_slug
from mdforge.parser.links import extract_links, classify_link
from mdforge.parser.codeblocks import extract_code_blocks
from mdforge.parser.metadata import compute_word_count, build_metadata


def parse(content: str, file_path: str) -> dict:
    """Parse a Markdown string and extract all structured metadata.

    Args:
        content: Raw Markdown content.
        file_path: Path to the source file (for error reporting).

    Returns:
        Parsed metadata dictionary.
    """
    if not isinstance(content, str):
        raise TypeError(
            f"Expected string content for {file_path}, got {type(content).__name__}"
        )

    fm = parse_frontmatter(content)
    body = fm["_body"]

    headings = extract_headings(body)
    links = extract_links(body)
    code_blocks = extract_code_blocks(body)
    word_count = compute_word_count(body)

    return build_metadata(
        file_path=file_path,
        frontmatter=fm["data"],
        headings=headings,
        links=links,
        code_blocks=code_blocks,
        word_count=word_count,
        raw_content=content,
        body_content=body,
    )


__all__ = [
    "parse",
    "parse_frontmatter",
    "extract_headings",
    "generate_slug",
    "extract_links",
    "classify_link",
    "extract_code_blocks",
    "compute_word_count",
    "build_metadata",
]