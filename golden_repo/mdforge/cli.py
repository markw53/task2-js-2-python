"""Click-based CLI for mdforge."""

import json
import sys
from pathlib import Path

import click

from mdforge import core
from mdforge.utils.errors import MdForgeError
from mdforge.utils import logger


class MdForgeCLI(click.Group):
    """Custom Click group that handles MdForgeError exceptions."""

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except MdForgeError as err:
            logger.error(str(err))
            sys.exit(err.exit_code)
        except Exception as err:
            logger.error(f"Unexpected error: {err}")
            sys.exit(1)


@click.group(cls=MdForgeCLI)
@click.version_option("1.2.0", prog_name="mdforge")
def cli():
    """A CLI toolkit for parsing, validating, and transforming Markdown files."""
    pass


@cli.command()
@click.argument("file", type=click.Path())
def parse(file):
    """Parse a Markdown file and display its metadata."""
    file_path = str(Path(file).resolve())
    result = core.parse_file(file_path)
    output = {
        "file": file_path,
        "frontmatter": result["frontmatter"],
        "headings": result["headings"],
        "links": result["links"],
        "codeBlocks": result["code_blocks"],
        "wordCount": result["word_count"],
    }
    click.echo(json.dumps(output, indent=2))


@cli.command()
@click.argument("file", type=click.Path())
def toc(file):
    """Generate a table of contents."""
    file_path = str(Path(file).resolve())
    result = core.generate_toc_for_file(file_path)
    click.echo(result)


@cli.command()
@click.argument("file", type=click.Path())
def html(file):
    """Convert Markdown to simplified HTML."""
    file_path = str(Path(file).resolve())
    result = core.convert_to_html(file_path)
    click.echo(result)


@cli.command()
@click.argument("path", type=click.Path())
def stats(path):
    """Compute statistics for a file or directory."""
    resolved = str(Path(path).resolve())
    result = core.compute_stats_for_path(resolved)
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument("dir", type=click.Path())
def validate(dir):
    """Validate internal links across a directory."""
    dir_path = str(Path(dir).resolve())
    result = core.validate_links(dir_path)

    if result["valid"]:
        logger.success("All internal links are valid.")
        click.echo(json.dumps(result, indent=2))
    else:
        logger.warn(f"Found {result['brokenCount']} broken link(s).")
        click.echo(json.dumps(result, indent=2))
        raise MdForgeError(
            f"Validation failed: {result['brokenCount']} broken link(s)",
            2,
        )


@cli.command()
@click.argument("dir", type=click.Path())
@click.option("-o", "--output", required=True, help="Output directory for JSON files")
def batch(dir, output):
    """Batch process a directory of Markdown files."""
    input_dir = str(Path(dir).resolve())
    output_dir = str(Path(output).resolve())

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    result = core.batch_process(input_dir, output_dir)
    click.echo(json.dumps(result, indent=2))

    if result["failed"] > 0:
        logger.warn(f"{result['failed']} file(s) failed processing.")
    logger.success(
        f"Batch complete: {result['processed']} processed, {result['failed']} failed."
    )