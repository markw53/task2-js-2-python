"""Default configuration values for mdforge."""

DEFAULTS = {
    # Maximum file size to process (in bytes)
    "max_file_size": 10 * 1024 * 1024,  # 10MB

    # Supported file extensions
    "markdown_extensions": [".md", ".markdown", ".mdown", ".mkd"],

    # Default output format for stats
    "stats_format": "json",

    # Timeout for batch operations (seconds)
    "batch_timeout": 30,

    # Maximum recursion depth for directory scanning
    "max_depth": 10,

    # Whether to follow symlinks
    "follow_symlinks": False,

    # Default encoding
    "encoding": "utf-8",

    # HTML conversion options
    "html": {
        "wrap_in_body": False,
        "include_doctype": False,
        "escape_html": True,
    },

    # TOC generation options
    "toc": {
        "min_level": 2,
        "max_level": 4,
        "ordered": False,
    },
}


def merge_config(user_config: dict | None = None) -> dict:
    """Merge user config with defaults (shallow)."""
    if user_config is None:
        user_config = {}
    return {**DEFAULTS, **user_config}