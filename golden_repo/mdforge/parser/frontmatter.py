"""YAML frontmatter parsing."""

import re
import yaml


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from Markdown content.

    Returns a dict with:
        - 'data': parsed YAML as a dict (empty dict if no frontmatter)
        - '_body': content without frontmatter

    If frontmatter parsing fails (malformed YAML), treats entire content as body.
    """
    match = re.match(r"^---\n([\s\S]*?)\n---\n?([\s\S]*)$", content)

    if match:
        yaml_str = match.group(1)
        body = match.group(2)
        try:
            data = yaml.safe_load(yaml_str)
            if data is None:
                data = {}
            if not isinstance(data, dict):
                data = {}
            return {"data": data, "_body": body}
        except yaml.YAMLError:
            return {"data": {}, "_body": content}

    return {"data": {}, "_body": content}