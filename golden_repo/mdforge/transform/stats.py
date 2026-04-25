"""Statistics computation and aggregation."""


def compute_stats(parsed: dict, file_path: str) -> dict:
    """Compute statistics for a single parsed Markdown document."""
    language_dist: dict[str, int] = {}
    for block in parsed["code_blocks"]:
        lang = block["language"] or "unknown"
        language_dist[lang] = language_dist.get(lang, 0) + 1

    return {
        "file": file_path,
        "wordCount": parsed["word_count"],
        "lineCount": parsed["line_count"],
        "headingCount": parsed["heading_count"],
        "linkCount": parsed["link_count"],
        "codeBlockCount": parsed["code_block_count"],
        "internalLinkCount": len(parsed["internal_links"]),
        "externalLinkCount": len(parsed["external_links"]),
        "anchorLinkCount": len(parsed["anchor_links"]),
        "hasTitle": parsed["title"] is not None,
        "hasFrontmatter": parsed["has_frontmatter"],
        "codeLanguages": language_dist,
    }


def aggregate_stats(stats_array: list[dict]) -> dict:
    """Aggregate statistics across multiple files."""
    if len(stats_array) == 0:
        return {
            "fileCount": 0,
            "totalWordCount": 0,
            "totalLineCount": 0,
            "totalHeadings": 0,
            "totalLinks": 0,
            "totalCodeBlocks": 0,
            "averageWordCount": 0,
            "files": [],
            "codeLanguages": {},
        }

    total_words = 0
    total_lines = 0
    total_headings = 0
    total_links = 0
    total_code_blocks = 0
    code_languages: dict[str, int] = {}

    for s in stats_array:
        total_words += s["wordCount"]
        total_lines += s["lineCount"]
        total_headings += s["headingCount"]
        total_links += s["linkCount"]
        total_code_blocks += s["codeBlockCount"]

        for lang, count in (s.get("codeLanguages") or {}).items():
            code_languages[lang] = code_languages.get(lang, 0) + count

    return {
        "fileCount": len(stats_array),
        "totalWordCount": total_words,
        "totalLineCount": total_lines,
        "totalHeadings": total_headings,
        "totalLinks": total_links,
        "totalCodeBlocks": total_code_blocks,
        "averageWordCount": round(total_words / len(stats_array)),
        "files": [s["file"] for s in stats_array],
        "codeLanguages": code_languages,
    }