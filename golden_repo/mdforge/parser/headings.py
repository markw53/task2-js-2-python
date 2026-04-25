"""Heading extraction and slug generation."""

import re


def extract_headings(body: str) -> list[dict]:
    """Extract all Markdown headings from the body content.

    Supports ATX-style headings (# through ######).
    Skips headings inside fenced code blocks.

    Each heading includes:
        - level (1-6)
        - text (trimmed heading text)
        - slug (URL-friendly anchor)
        - line (1-based line number)
    """
    headings = []
    lines = body.split("\n")
    in_code_block = False

    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    for i, line in enumerate(lines):
        trimmed = line.lstrip()

        # Track fenced code blocks to avoid false positives
        if trimmed.startswith("```") or trimmed.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            slug = generate_slug(text)

            headings.append({
                "level": level,
                "text": text,
                "slug": slug,
                "line": i + 1,
            })

    return headings


def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from heading text.

    Lowercases, replaces non-word characters (except hyphens) with nothing,
    spaces with hyphens, collapses multiple hyphens, and trims
    leading/trailing hyphens.
    """
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = re.sub(r"^-|-$", "", slug)
    return slug