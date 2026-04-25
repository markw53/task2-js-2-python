"""Table of contents generation."""


def generate_toc(headings: list[dict]) -> str:
    """Generate a Markdown-formatted table of contents from extracted headings.

    Output format:
        - {text}         (for h2)
          - {text}       (for h3)
            - {text}     (for h4)

    h1 headings are treated as the document title and excluded from the TOC.
    Indentation is 2 spaces per level below h2.
    Each entry links to its anchor slug.
    """
    if not headings:
        return ""

    toc_lines = []

    for heading in headings:
        # Skip h1 (document title)
        if heading["level"] == 1:
            continue

        indent = "  " * (heading["level"] - 2)
        line = f"{indent}- [{heading['text']}](#{heading['slug']})"
        toc_lines.append(line)

    return "\n".join(toc_lines)