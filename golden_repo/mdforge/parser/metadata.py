"""Word count computation and metadata building."""

import re


def compute_word_count(body: str) -> int:
    """Compute the word count of Markdown body content.

    Strips fenced code blocks and inline code, then counts
    whitespace-delimited tokens.
    """
    # Remove fenced code blocks
    stripped = re.sub(r"(`{3,}|~{3,})[\s\S]*?\1", "", body)

    # Remove inline code
    no_inline_code = re.sub(r"`[^`]+`", "", stripped)

    # Remove Markdown syntax characters but keep words
    cleaned = re.sub(r"[#*_$$$$()>|~`-]", " ", no_inline_code)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if len(cleaned) == 0:
        return 0

    return len(cleaned.split())


def build_metadata(
    file_path: str,
    frontmatter: dict,
    headings: list[dict],
    links: list[dict],
    code_blocks: list[dict],
    word_count: int,
    raw_content: str,
    body_content: str,
) -> dict:
    """Build a structured metadata object from parsed components."""
    title = _infer_title(frontmatter, headings)

    internal_links = [link for link in links if link["type"] == "internal"]
    external_links = [link for link in links if link["type"] == "external"]
    anchor_links = [link for link in links if link["type"] == "anchor"]

    return {
        "file_path": file_path,
        "title": title,
        "frontmatter": frontmatter,
        "headings": headings,
        "links": links,
        "code_blocks": code_blocks,
        "word_count": word_count,
        "line_count": len(raw_content.split("\n")),
        "has_frontmatter": len(frontmatter) > 0,
        "heading_count": len(headings),
        "link_count": len(links),
        "code_block_count": len(code_blocks),
        "internal_links": internal_links,
        "external_links": external_links,
        "anchor_links": anchor_links,
    }


def _infer_title(frontmatter: dict, headings: list[dict]) -> str | None:
    """Infer the document title from frontmatter or the first h1 heading."""
    if "title" in frontmatter:
        return str(frontmatter["title"])

    h1 = next((h for h in headings if h["level"] == 1), None)
    if h1:
        return h1["text"]

    return None