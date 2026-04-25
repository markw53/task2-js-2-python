"""Internal link validation across a corpus of Markdown files."""

from pathlib import Path


def validate_corpus(corpus: dict) -> dict:
    """Validate all internal links across a corpus of parsed Markdown files.

    Internal links are expected to point to:
        - Other files in the corpus (e.g., ./other.md)
        - Anchors within files (e.g., ./other.md#section or #section)

    Args:
        corpus: Map of filePath → parsed metadata.

    Returns:
        Validation result dict.
    """
    file_paths = list(corpus.keys())
    broken_links: list[dict] = []
    valid_links: list[dict] = []
    checked_count = {"internal": 0, "anchor": 0}

    # Build a set of known files (normalized)
    known_files: set[str] = set()
    for fp in file_paths:
        known_files.add(str(Path(fp).resolve()))

    # Build a map of file → known anchors (heading slugs)
    anchor_map: dict[str, set[str]] = {}
    for fp, parsed in corpus.items():
        resolved = str(Path(fp).resolve())
        anchor_map[resolved] = set(h["slug"] for h in parsed["headings"])

    for fp, parsed in corpus.items():
        file_dir = str(Path(fp).resolve().parent)

        for link in parsed["links"]:
            if link["type"] == "internal":
                checked_count["internal"] += 1
                result = _validate_internal_link(
                    link, fp, file_dir, known_files, anchor_map
                )
                if result["valid"]:
                    valid_links.append(result)
                else:
                    broken_links.append(result)

            elif link["type"] == "anchor":
                checked_count["anchor"] += 1
                result = _validate_anchor_link(link, fp, anchor_map)
                if result["valid"]:
                    valid_links.append(result)
                else:
                    broken_links.append(result)

            # External and "other" links are not validated

    return {
        "valid": len(broken_links) == 0,
        "totalChecked": checked_count["internal"] + checked_count["anchor"],
        "validCount": len(valid_links),
        "brokenCount": len(broken_links),
        "brokenLinks": broken_links,
        "checkedCount": checked_count,
    }


def _validate_internal_link(
    link: dict,
    source_file: str,
    file_dir: str,
    known_files: set[str],
    anchor_map: dict[str, set[str]],
) -> dict:
    """Validate an internal link (relative path to another file, optionally with anchor)."""
    url_parts = link["url"].split("#")
    file_part = url_parts[0]
    anchor_part = url_parts[1] if len(url_parts) > 1 else None

    target_path = str(Path(file_dir, file_part).resolve())

    result = {
        "source": source_file,
        "line": link["line"],
        "text": link["text"],
        "url": link["url"],
        "type": "internal",
        "valid": True,
        "reason": None,
    }

    if target_path not in known_files:
        result["valid"] = False
        result["reason"] = f"File not found: {file_part}"
        return result

    if anchor_part is not None:
        target_anchors = anchor_map.get(target_path)
        if target_anchors is None or anchor_part not in target_anchors:
            result["valid"] = False
            result["reason"] = f"Anchor not found: #{anchor_part} in {file_part}"
            return result

    return result


def _validate_anchor_link(
    link: dict,
    source_file: str,
    anchor_map: dict[str, set[str]],
) -> dict:
    """Validate an anchor link (same-page reference like #section)."""
    anchor = link["url"][1:]  # Remove leading #
    resolved_source = str(Path(source_file).resolve())

    result = {
        "source": source_file,
        "line": link["line"],
        "text": link["text"],
        "url": link["url"],
        "type": "anchor",
        "valid": True,
        "reason": None,
    }

    source_anchors = anchor_map.get(resolved_source)
    if source_anchors is None or anchor not in source_anchors:
        result["valid"] = False
        result["reason"] = f"Anchor not found: {link['url']} in current document"
        return result

    return result