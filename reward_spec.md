# Reward Specification

## Terminal reward

- `1.0`: `pip install -e .` succeeds and all 42 target behavioral tests pass.
- `0.0`: install fails or any test fails.

## Interim reward guidance

- **+0.10**: correct `pyproject.toml` (or `setup.py`) with valid dependencies (`click`, `python-frontmatter`) and proper entry point configuration so both `python3 -m mdforge` and `python3 /target/bin/mdforge.py` work
- **+0.10**: idiomatic Python project layout (`mdforge/` package with `__init__.py` files for each subpackage — `parser/`, `transform/`, `validator/`, `utils/`, `config/`) correctly mapping JavaScript's CommonJS barrel `index.js` exports
- **+0.10**: `parse` command produces JSON output with correct keys (`file`, `frontmatter`, `headings` with level/text/slug/line, `links` with text/url/type/line, `codeBlocks` with language/code/startLine/endLine, `wordCount`) — camelCase JSON keys preserved despite snake\_case internal code
- **+0.10**: `html` command converts Markdown to simplified HTML matching source behavior exactly — headings, bold, italic, inline code, fenced code blocks with language class, links, unordered lists, ordered lists, blockquotes, horizontal rules, paragraph wrapping, and frontmatter stripping
- **+0.10**: `toc` command generates Markdown TOC with correct indentation (h1 excluded, h2 at base indent, h3 indented 2 spaces, h4 indented 4 spaces) and correct anchor slug links
- **+0.10**: slug generation algorithm matches source exactly — lowercase, strip non-word chars except hyphens, spaces to hyphens, collapse multiple hyphens, trim leading/trailing hyphens
- **+0.10**: `validate` command checks internal and anchor links across a corpus, returns JSON with `valid`, `totalChecked`, `brokenCount`, `brokenLinks` array, exits 0 when all valid, exits 2 when broken links found, and correctly ignores external/mailto links
- **+0.05**: `MdForgeError` custom exception class preserves `exit_code` attribute, top-level error boundary catches it and calls `sys.exit(err.exit_code)` — exit code 0 for success, 1 for general errors, 2 for validation failures
- **+0.05**: `stats` command produces JSON with aggregate statistics (`fileCount`, `totalWordCount`, `totalLineCount`, `totalHeadings`, `totalLinks`, `totalCodeBlocks`, `averageWordCount`, `files` array, `codeLanguages` distribution) matching source output
- **+0.05**: `batch` command processes directory of Markdown files, writes one JSON file per input to output directory with expected keys (`metadata`/`frontmatter`, `headings`, `links`, `stats`, `toc`), and reports `processed`/`failed` counts in stdout JSON
- **+0.05**: edge cases handled correctly — headings and links inside fenced code blocks are ignored, unclosed fenced code blocks are discarded, word count excludes fenced code blocks and inline code, empty files produce empty arrays for headings/links/codeBlocks
- **+0.05**: async I/O correctly removed — synchronous `pathlib` file operations used throughout, no `asyncio`, no `aiofiles`, Click used instead of Commander.js, `glob` npm package replaced with `pathlib.Path.rglob` — all idiomatic Python adaptations
- **+0.05**: Commander.js CLI correctly translated to Click with all six subcommands (`parse`, `toc`, `html`, `stats`, `validate`, `batch`) registered with correct arguments, options (`--output` for batch), and matching help text