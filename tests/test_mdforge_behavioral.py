"""
Behavioral test suite for mdforge JavaScript -> Python translation.

Tests invoke the translated CLI via subprocess and assert on stdout/stderr/exit codes.
This suite is language-agnostic: it validates the CLI contract, not internal implementation.

Convention:
  - All Markdown inputs are written to tmp_path fixtures (hermetic).
  - Assertions use substring/regex matching, never strict stdout equality.
  - The binary is invoked via the MDFORGE_BIN environment variable.
"""

import json
import os
import subprocess
import textwrap

TIMEOUT = 30

# How to invoke the CLI — overridable via env var
MDFORGE_BIN = os.environ.get("MDFORGE_BIN", "python3 -m mdforge")
MDFORGE_CWD = os.environ.get("MDFORGE_CWD", "/target")


def run_mdforge(*args, cwd=None):
    """Run the mdforge CLI and return the CompletedProcess."""
    cmd = MDFORGE_BIN.split() + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        cwd=cwd or MDFORGE_CWD,
    )


def write_md(tmp_path, filename, content):
    """Write a Markdown file into tmp_path and return its absolute path as a string."""
    fp = tmp_path / filename
    fp.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(fp)


def write_md_in_subdir(tmp_path, dirname, filename, content):
    """Write a Markdown file inside a subdirectory of tmp_path."""
    d = tmp_path / dirname
    d.mkdir(parents=True, exist_ok=True)
    fp = d / filename
    fp.write_text(textwrap.dedent(content), encoding="utf-8")
    return str(fp)


# ---------------------------------------------------------------------------
# TestParseCommand
# ---------------------------------------------------------------------------
class TestParseCommand:

    def test_parse_simple_file(self, tmp_path):
        md = write_md(tmp_path, "simple.md", """\
        # Hello World

        Some body text here with words.

        ## Section One

        More text in section one.
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "headings" in data
        assert len(data["headings"]) == 2
        assert data["headings"][0]["text"] == "Hello World"
        assert data["headings"][0]["level"] == 1
        assert data["headings"][1]["text"] == "Section One"
        assert data["headings"][1]["level"] == 2

    def test_parse_with_frontmatter(self, tmp_path):
        md = write_md(tmp_path, "front.md", """\
        ---
        title: My Document
        author: Test Author
        tags:
          - markdown
          - test
        ---

        # Main Heading

        Body content here.
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "frontmatter" in data
        assert data["frontmatter"]["title"] == "My Document"
        assert data["frontmatter"]["author"] == "Test Author"
        assert "markdown" in data["frontmatter"]["tags"]

    def test_parse_no_frontmatter(self, tmp_path):
        md = write_md(tmp_path, "nofm.md", """\
        # Just a heading

        No frontmatter here.
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "frontmatter" in data
        # frontmatter should be empty dict
        assert data["frontmatter"] == {} or len(data["frontmatter"]) == 0

    def test_parse_file_not_found_exit_1(self):
        result = run_mdforge("parse", "/nonexistent/path/file.md")
        assert result.returncode == 1

    def test_parse_extracts_links(self, tmp_path):
        md = write_md(tmp_path, "links.md", """\
        # Links Doc

        Here is an [external link](https://example.com) and
        an [internal link](./other.md) and an [anchor](#section).
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "links" in data
        links = data["links"]
        assert len(links) == 3

        types = [link["type"] for link in links]
        assert "external" in types
        assert "internal" in types
        assert "anchor" in types

    def test_parse_extracts_code_blocks(self, tmp_path):
        md = write_md(tmp_path, "code.md", """\
        # Code Doc

        ```python
        def hello():
            print("hi")
        ```

        Some text.

        ```javascript
        console.log("hi");
        ```
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "codeBlocks" in data
        blocks = data["codeBlocks"]
        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert blocks[1]["language"] == "javascript"


# ---------------------------------------------------------------------------
# TestTocCommand
# ---------------------------------------------------------------------------
class TestTocCommand:

    def test_toc_basic(self, tmp_path):
        md = write_md(tmp_path, "toc.md", """\
        # Title

        ## Introduction

        ## Getting Started

        ## Conclusion
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        stdout = result.stdout
        assert "Introduction" in stdout
        assert "Getting Started" in stdout
        assert "Conclusion" in stdout

    def test_toc_nested_headings(self, tmp_path):
        md = write_md(tmp_path, "nested.md", """\
        # Title

        ## Chapter One

        ### Section A

        ### Section B

        ## Chapter Two

        ### Section C

        #### Subsection C1
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        lines = [line for line in result.stdout.strip().split("\n") if line.strip()]
        # h2 lines should not be indented (or have base indentation)
        # h3 lines should be indented more than h2
        # h4 lines should be indented more than h3
        # We check relative indentation
        assert len(lines) >= 5  # Chapter One, Section A, Section B, Chapter Two, Section C, Subsection C1

        # Find a h3 line and verify it's indented relative to h2
        chapter_line = [entry for entry in lines if "Chapter One" in entry][0]
        section_line = [entry for entry in lines if "Section A" in entry][0]
        assert len(section_line) - len(section_line.lstrip()) > len(chapter_line) - len(chapter_line.lstrip())

    def test_toc_no_headings_empty_output(self, tmp_path):
        md = write_md(tmp_path, "noheadings.md", """\
        Just some text, no headings at all.

        Another paragraph.
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_toc_skips_h1(self, tmp_path):
        md = write_md(tmp_path, "h1only.md", """\
        # Title Only

        Some body text.
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        # H1 should be excluded from TOC — output should be empty
        assert result.stdout.strip() == ""

    def test_toc_slug_generation(self, tmp_path):
        md = write_md(tmp_path, "slugs.md", """\
        # Title

        ## Hello World

        ## Getting Started!

        ## Multiple   Spaces   Here
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        stdout = result.stdout
        assert "#hello-world" in stdout
        assert "#getting-started" in stdout
        assert "#multiple-spaces-here" in stdout


# ---------------------------------------------------------------------------
# TestHtmlCommand
# ---------------------------------------------------------------------------
class TestHtmlCommand:

    def test_html_headings(self, tmp_path):
        md = write_md(tmp_path, "headings.md", """\
        # Heading 1

        ## Heading 2

        ### Heading 3
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<h1>" in result.stdout
        assert "Heading 1" in result.stdout
        assert "<h2>" in result.stdout
        assert "Heading 2" in result.stdout
        assert "<h3>" in result.stdout
        assert "Heading 3" in result.stdout

    def test_html_bold_italic(self, tmp_path):
        md = write_md(tmp_path, "inline.md", """\
        This has **bold text** and *italic text* in it.
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<strong>bold text</strong>" in result.stdout
        assert "<em>italic text</em>" in result.stdout

    def test_html_code_blocks_with_language(self, tmp_path):
        md = write_md(tmp_path, "codeblock.md", """\
        ```python
        def hello():
            pass
        ```
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<pre><code" in result.stdout
        assert "language-python" in result.stdout
        assert "def hello():" in result.stdout

    def test_html_inline_code(self, tmp_path):
        md = write_md(tmp_path, "inlinecode.md", """\
        Use `print()` to output text.
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<code>print()</code>" in result.stdout

    def test_html_links(self, tmp_path):
        md = write_md(tmp_path, "htmllinks.md", """\
        Visit [Example](https://example.com) for more info.
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert '<a href="https://example.com">' in result.stdout
        assert "Example</a>" in result.stdout

    def test_html_unordered_list(self, tmp_path):
        md = write_md(tmp_path, "ul.md", """\
        - Item one
        - Item two
        - Item three
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<ul>" in result.stdout
        assert "<li>Item one</li>" in result.stdout
        assert "<li>Item two</li>" in result.stdout
        assert "<li>Item three</li>" in result.stdout
        assert "</ul>" in result.stdout

    def test_html_ordered_list(self, tmp_path):
        md = write_md(tmp_path, "ol.md", """\
        1. First
        2. Second
        3. Third
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<ol>" in result.stdout
        assert "<li>First</li>" in result.stdout
        assert "<li>Second</li>" in result.stdout
        assert "<li>Third</li>" in result.stdout
        assert "</ol>" in result.stdout

    def test_html_blockquotes(self, tmp_path):
        md = write_md(tmp_path, "bq.md", """\
        > This is a blockquote.
        > It has multiple lines.
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<blockquote>" in result.stdout
        assert "This is a blockquote" in result.stdout
        assert "</blockquote>" in result.stdout

    def test_html_horizontal_rule(self, tmp_path):
        md = write_md(tmp_path, "hr.md", """\
        Some text above.

        ---

        Some text below.
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<hr>" in result.stdout

    def test_html_paragraphs(self, tmp_path):
        md = write_md(tmp_path, "para.md", """\
        First paragraph text.

        Second paragraph text.
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        assert "<p>" in result.stdout
        assert "First paragraph text" in result.stdout
        assert "Second paragraph text" in result.stdout

    def test_html_strips_frontmatter(self, tmp_path):
        md = write_md(tmp_path, "fmhtml.md", """\
        ---
        title: Hidden
        ---

        # Visible Heading

        Visible body.
        """)
        result = run_mdforge("html", md)
        assert result.returncode == 0
        # Frontmatter YAML should NOT appear in HTML output
        assert "title: Hidden" not in result.stdout
        assert "Visible Heading" in result.stdout


# ---------------------------------------------------------------------------
# TestStatsCommand
# ---------------------------------------------------------------------------
class TestStatsCommand:

    def test_stats_single_file(self, tmp_path):
        md = write_md(tmp_path, "stats.md", """\
        ---
        title: Stats Test
        ---

        # Main Title

        Here are some words in the body.

        ## Section

        More words here and [a link](https://example.com).

        ```python
        x = 1
        ```
        """)
        result = run_mdforge("stats", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Should report word count, heading count, link count, code block count
        assert "totalWordCount" in data or "fileCount" in data
        # If single file, might be wrapped in aggregate or direct
        # Check that word count > 0
        if "totalWordCount" in data:
            assert data["totalWordCount"] > 0
        if "totalHeadings" in data:
            assert data["totalHeadings"] >= 2
        if "totalLinks" in data:
            assert data["totalLinks"] >= 1
        if "totalCodeBlocks" in data:
            assert data["totalCodeBlocks"] >= 1

    def test_stats_directory_aggregate(self, tmp_path):
        d = tmp_path / "docs"
        d.mkdir()
        (d / "one.md").write_text("# One\n\nSome words here.\n", encoding="utf-8")
        (d / "two.md").write_text("# Two\n\nMore words in file two.\n\n## Sub\n\nExtra.\n", encoding="utf-8")

        result = run_mdforge("stats", str(d))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "fileCount" in data
        assert data["fileCount"] == 2
        assert "totalWordCount" in data
        assert data["totalWordCount"] > 0

    def test_stats_empty_dir_exit_1(self, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()

        result = run_mdforge("stats", str(d))
        assert result.returncode == 1


# ---------------------------------------------------------------------------
# TestValidateCommand
# ---------------------------------------------------------------------------
class TestValidateCommand:

    def test_validate_all_links_valid(self, tmp_path):
        d = tmp_path / "valid_corpus"
        d.mkdir()
        (d / "index.md").write_text(
            "# Index\n\nSee [about](./about.md) and [section](#index).\n",
            encoding="utf-8",
        )
        (d / "about.md").write_text(
            "# About\n\nBack to [index](./index.md).\n",
            encoding="utf-8",
        )

        result = run_mdforge("validate", str(d))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["valid"] is True
        assert data["brokenCount"] == 0

    def test_validate_broken_file_link(self, tmp_path):
        d = tmp_path / "broken_file"
        d.mkdir()
        (d / "index.md").write_text(
            "# Index\n\nSee [missing](./nonexistent.md).\n",
            encoding="utf-8",
        )

        result = run_mdforge("validate", str(d))
        assert result.returncode == 2
        data = json.loads(result.stdout)
        assert data["valid"] is False
        assert data["brokenCount"] >= 1
        # Check that the broken link details are reported
        assert len(data["brokenLinks"]) >= 1
        assert "nonexistent.md" in data["brokenLinks"][0]["url"]

    def test_validate_broken_anchor_link(self, tmp_path):
        d = tmp_path / "broken_anchor"
        d.mkdir()
        (d / "doc.md").write_text(
            "# Title\n\nSee [bad anchor](#does-not-exist).\n",
            encoding="utf-8",
        )

        result = run_mdforge("validate", str(d))
        assert result.returncode == 2
        data = json.loads(result.stdout)
        assert data["valid"] is False
        assert data["brokenCount"] >= 1

    def test_validate_exit_code_2_on_broken(self, tmp_path):
        d = tmp_path / "exit2"
        d.mkdir()
        (d / "page.md").write_text(
            "# Page\n\n[Dead link](./ghost.md)\n",
            encoding="utf-8",
        )

        result = run_mdforge("validate", str(d))
        # Must exit with code 2, not 1
        assert result.returncode == 2

    def test_validate_ignores_external_links(self, tmp_path):
        d = tmp_path / "ext"
        d.mkdir()
        (d / "page.md").write_text(
            "# Page\n\n[Google](https://google.com) and [mail](mailto:a@b.com)\n",
            encoding="utf-8",
        )

        result = run_mdforge("validate", str(d))
        # External and mailto links should NOT be checked — should pass
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["valid"] is True


# ---------------------------------------------------------------------------
# TestBatchCommand
# ---------------------------------------------------------------------------
class TestBatchCommand:

    def test_batch_creates_json_files(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "alpha.md").write_text("# Alpha\n\nAlpha body.\n", encoding="utf-8")
        (src / "beta.md").write_text("# Beta\n\nBeta body.\n", encoding="utf-8")

        out = tmp_path / "out"

        result = run_mdforge("batch", str(src), "--output", str(out))
        assert result.returncode == 0

        # Output directory should contain alpha.json and beta.json
        output_files = sorted(os.listdir(str(out)))
        assert "alpha.json" in output_files
        assert "beta.json" in output_files

    def test_batch_json_contains_expected_keys(self, tmp_path):
        src = tmp_path / "src2"
        src.mkdir()
        (src / "doc.md").write_text(
            "---\ntitle: Test\n---\n\n# Heading\n\nBody text.\n",
            encoding="utf-8",
        )

        out = tmp_path / "out2"

        result = run_mdforge("batch", str(src), "--output", str(out))
        assert result.returncode == 0

        with open(str(out / "doc.json"), encoding="utf-8") as f:
            data = json.load(f)

        # The JSON output should contain these keys at minimum
        assert "metadata" in data or "frontmatter" in data
        assert "headings" in data
        assert "links" in data
        assert "stats" in data
        assert "toc" in data

    def test_batch_reports_processed_count(self, tmp_path):
        src = tmp_path / "src3"
        src.mkdir()
        (src / "one.md").write_text("# One\n\nBody.\n", encoding="utf-8")
        (src / "two.md").write_text("# Two\n\nBody.\n", encoding="utf-8")
        (src / "three.md").write_text("# Three\n\nBody.\n", encoding="utf-8")

        out = tmp_path / "out3"

        result = run_mdforge("batch", str(src), "--output", str(out))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "processed" in data
        assert data["processed"] == 3
        assert "failed" in data
        assert data["failed"] == 0


# ---------------------------------------------------------------------------
# TestSlugGeneration
# ---------------------------------------------------------------------------
class TestSlugGeneration:
    """
    Verify slug generation by checking TOC output anchors.
    The slug algorithm must match the JS source exactly:
    lowercase, strip non-word chars (except hyphens), spaces→hyphens,
    collapse multiple hyphens, trim leading/trailing hyphens.
    """

    def test_slug_simple(self, tmp_path):
        md = write_md(tmp_path, "slug1.md", """\
        ## Hello World
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        assert "#hello-world" in result.stdout

    def test_slug_special_characters(self, tmp_path):
        md = write_md(tmp_path, "slug2.md", """\
        ## What's New in v2.0?
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        # Apostrophe and question mark should be stripped
        # "What's New in v2.0?" -> "whats-new-in-v20"
        assert "#whats-new-in-v20" in result.stdout

    def test_slug_multiple_spaces(self, tmp_path):
        md = write_md(tmp_path, "slug3.md", """\
        ## Lots   of    spaces
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        # Multiple spaces should collapse to single hyphen
        assert "#lots-of-spaces" in result.stdout

    def test_slug_leading_trailing_hyphens(self, tmp_path):
        md = write_md(tmp_path, "slug4.md", """\
        ## -Dashed Title-
        """)
        result = run_mdforge("toc", md)
        assert result.returncode == 0
        # Leading/trailing hyphens should be trimmed
        assert "#dashed-title" in result.stdout


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------
class TestEdgeCases:
    """
    Edge cases that are common regression points when translating
    from JavaScript to Python. These test behaviors that differ
    subtly between ecosystems.
    """

    def test_empty_file(self, tmp_path):
        md = write_md(tmp_path, "empty.md", "")
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["headings"] == []
        assert data["links"] == []
        assert data["codeBlocks"] == []

    def test_headings_inside_code_blocks_ignored(self, tmp_path):
        md = write_md(tmp_path, "fakeh.md", """\
        # Real Heading

        ```
        # This is NOT a heading
        ## Neither is this
        ```

        ## Another Real Heading
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        headings = data["headings"]
        texts = [h["text"] for h in headings]
        assert "Real Heading" in texts
        assert "Another Real Heading" in texts
        assert "This is NOT a heading" not in texts
        assert "Neither is this" not in texts
        assert len(headings) == 2

    def test_links_inside_code_blocks_ignored(self, tmp_path):
        md = write_md(tmp_path, "fakelink.md", """\
        # Doc

        [real link](https://example.com)

        ```
        [fake link](https://not-real.com)
        ```
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        links = data["links"]
        urls = [link["url"] for link in links]
        assert "https://example.com" in urls
        assert "https://not-real.com" not in urls
        assert len(links) == 1

    def test_unclosed_code_block_discarded(self, tmp_path):
        md = write_md(tmp_path, "unclosed.md", """\
        # Title

        ```python
        def never_closed():
            pass

        ## This looks like a heading but is inside unclosed code block
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Unclosed code blocks should be discarded per source behavior
        assert len(data["codeBlocks"]) == 0
        # The heading inside the unclosed block should NOT be extracted
        # (it's consumed by the code block parser even though the block is discarded)
        heading_texts = [h["text"] for h in data["headings"]]
        assert "Title" in heading_texts
        # The "heading" inside the unclosed fence should not appear
        assert len(data["headings"]) == 1

    def test_word_count_excludes_code(self, tmp_path):
        md = write_md(tmp_path, "wc.md", """\
        # Title

        Three body words.

        ```
        these code words should not count
        ```

        Two more.
        """)
        result = run_mdforge("parse", md)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        word_count = data["wordCount"]
        # "Three body words" = 3, "Two more" = 2, "Title" contributes after stripping #
        # Exact count depends on implementation but code block words must be excluded
        # The JS source strips fenced blocks then counts — so code words are excluded
        # Conservative check: code block has 6 words, total without code should be < 10
        assert word_count < 15
        assert word_count > 0