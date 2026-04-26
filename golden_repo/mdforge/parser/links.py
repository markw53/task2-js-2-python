"""Link extraction and classification."""

import re

LINK_PATTERN = re.compile('\\[([^\\]]*)\\]\\(([^)]+)\\)')


def extract_links(body: str) -> list[dict]:
    """Extract all links from Markdown body content."""
    links = []
    lines = body.split("\n")
    in_code_block = False

    for i, line in enumerate(lines):
        trimmed = line.lstrip()

        if trimmed.startswith("```") or trimmed.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        for match in LINK_PATTERN.finditer(line):
            text = match.group(1)
            url = match.group(2).strip()
            link_type = classify_link(url)

            links.append({
                "text": text,
                "url": url,
                "type": link_type,
                "line": i + 1,
            })

    return links


def classify_link(url: str) -> str:
    """Classify a URL into a link type."""
    if url.startswith("#"):
        return "anchor"
    if url.startswith("http://") or url.startswith("https://"):
        return "external"
    if url.startswith("mailto:") or url.startswith("ftp://"):
        return "other"
    return "internal"
