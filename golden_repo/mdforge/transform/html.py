"""Markdown to simplified HTML conversion."""

import re

# Link pattern built from char codes to avoid shell/editor corruption
_LINK_RE = re.compile(
    chr(92) + chr(91)
    + "([^"
    + chr(92) + chr(93)
    + "]+)"
    + chr(92) + chr(93)
    + chr(92) + chr(40)
    + "([^"
    + chr(41)
    + "]+)"
    + chr(92) + chr(41)
)



def to_html(content: str) -> str:
    """Convert Markdown content to simplified HTML."""
    body = _strip_frontmatter(content)
    lines = body.split("\n")
    html_parts: list[str] = []

    in_code_block = False
    code_block_lang = ""
    code_lines: list[str] = []
    in_list = False
    list_type: str | None = None
    in_blockquote = False
    paragraph_lines: list[str] = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            text = " ".join(paragraph_lines)
            inlined = _inline_markdown(text)
            html_parts.append(f"<p>{inlined}</p>")
            paragraph_lines = []

    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            html_parts.append("</ul>" if list_type == "ul" else "</ol>")
            in_list = False
            list_type = None

    def flush_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            html_parts.append("</blockquote>")
            in_blockquote = False

    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
    hr_pattern = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")
    ul_pattern = re.compile(r"^[-*]\s+(.+)$")
    ol_pattern = re.compile(r"^\d+\.\s+(.+)$")
    fence_pattern = re.compile(r"^(`{3,}|~{3,})")

    for line in lines:
        trimmed = line.strip()

        # Fenced code blocks
        if fence_pattern.match(trimmed):
            if not in_code_block:
                flush_paragraph()
                flush_list()
                flush_blockquote()
                in_code_block = True
                code_block_lang = re.sub(r"^[`~]+", "", trimmed).strip()
                code_lines = []
                continue
            else:
                lang_attr = (
                    f' class="language-{code_block_lang}"' if code_block_lang else ""
                )
                code_content = _escape_html("\n".join(code_lines))
                html_parts.append(f"<pre><code{lang_attr}>{code_content}</code></pre>")
                in_code_block = False
                code_block_lang = ""
                code_lines = []
                continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Horizontal rule
        if hr_pattern.match(trimmed):
            flush_paragraph()
            flush_list()
            flush_blockquote()
            html_parts.append("<hr>")
            continue

        # Headings
        heading_match = heading_pattern.match(trimmed)
        if heading_match:
            flush_paragraph()
            flush_list()
            flush_blockquote()
            level = len(heading_match.group(1))
            text = _inline_markdown(heading_match.group(2).strip())
            html_parts.append(f"<h{level}>{text}</h{level}>")
            continue

        # Blockquote
        if trimmed.startswith(">"):
            flush_paragraph()
            flush_list()
            if not in_blockquote:
                html_parts.append("<blockquote>")
                in_blockquote = True
            quote_text = _inline_markdown(re.sub(r"^>\s?", "", trimmed))
            html_parts.append(f"<p>{quote_text}</p>")
            continue
        elif in_blockquote:
            flush_blockquote()

        # Unordered list
        ul_match = ul_pattern.match(trimmed)
        if ul_match:
            flush_paragraph()
            flush_blockquote()
            if not in_list or list_type != "ul":
                flush_list()
                html_parts.append("<ul>")
                in_list = True
                list_type = "ul"
            html_parts.append(f"<li>{_inline_markdown(ul_match.group(1))}</li>")
            continue

        # Ordered list
        ol_match = ol_pattern.match(trimmed)
        if ol_match:
            flush_paragraph()
            flush_blockquote()
            if not in_list or list_type != "ol":
                flush_list()
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            html_parts.append(f"<li>{_inline_markdown(ol_match.group(1))}</li>")
            continue

        # If we were in a list and hit a non-list line, close it
        if in_list and len(trimmed) > 0:
            flush_list()

        # Empty line: flush paragraph
        if len(trimmed) == 0:
            flush_paragraph()
            continue

        # Paragraph text
        paragraph_lines.append(trimmed)

    # Flush remaining state
    flush_paragraph()
    flush_list()
    flush_blockquote()

    if in_code_block:
        code_content = _escape_html("\n".join(code_lines))
        html_parts.append(f"<pre><code>{code_content}</code></pre>")

    return "\n".join(html_parts)


def _inline_markdown(text: str) -> str:
    """Apply inline Markdown transformations."""
    result = text

    # Inline code (must be done before other transforms)
    def _code_replace(match):
        return f"<code>{_escape_html(match.group(1))}</code>"

    result = re.sub(r"`([^`]+)`", _code_replace, result)

    # Bold (**text** or __text__)
    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result)
    result = re.sub(r"__(.+?)__", r"<strong>\1</strong>", result)

    # Italic (*text* or _text_) — must come after bold
    result = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", result)
    result = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<em>\1</em>", result)

    # Links [text](url) — use function replacement to avoid backreference issues
    def _link_replace(match):
        link_text = match.group(1)
        url = match.group(2)
        return f'<a href="{url}">{link_text}</a>'

    result = _LINK_RE.sub(_link_replace, result)
    
    return result


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _strip_frontmatter(content: str) -> str:
    """Strip YAML frontmatter from content."""
    match = re.match(r"^---\n[\s\S]*?\n---\n?", content)
    if match:
        return content[len(match.group(0)):]
    return content