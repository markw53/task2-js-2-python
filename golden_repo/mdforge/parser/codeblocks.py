"""Fenced code block extraction."""

import re


def extract_code_blocks(body: str) -> list[dict]:
    """Extract fenced code blocks from Markdown body content.

    Supports both backtick (```) and tilde (~~~) fencing.

    Each code block includes:
        - language: the language identifier (empty string if none)
        - code: the code content (without fences)
        - startLine: 1-based line number of the opening fence
        - endLine: 1-based line number of the closing fence

    Unclosed code blocks are discarded.
    """
    blocks = []
    lines = body.split("\n")
    current_block = None

    open_pattern = re.compile(r"^(`{3,}|~{3,})(\S*)$")

    for i, line in enumerate(lines):
        trimmed = line.lstrip()

        if current_block is None:
            # Check for opening fence
            open_match = open_pattern.match(trimmed)
            if open_match:
                current_block = {
                    "fence": open_match.group(1)[0],      # '`' or '~'
                    "fence_len": len(open_match.group(1)),
                    "language": open_match.group(2) or "",
                    "code_lines": [],
                    "start_line": i + 1,
                }
        else:
            # Check for closing fence (must match same char and at least same length)
            fence_char = current_block["fence"]
            fence_len = current_block["fence_len"]

            # Build pattern: 3+ backticks or tildes followed by optional whitespace
            if fence_char == "`":
                close_pattern = re.compile(rf"^`{{{fence_len},}}\s*$")
            else:
                close_pattern = re.compile(rf"^~{{{fence_len},}}\s*$")

            if close_pattern.match(trimmed):
                blocks.append({
                    "language": current_block["language"],
                    "code": "\n".join(current_block["code_lines"]),
                    "startLine": current_block["start_line"],
                    "endLine": i + 1,
                })
                current_block = None
            else:
                current_block["code_lines"].append(line)

    # Unclosed code blocks are discarded (match common Markdown parser behavior)
    return blocks