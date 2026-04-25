# mdforge

A command-line toolkit for parsing, validating, and transforming Markdown files.

## Features

- Extract frontmatter (YAML) metadata
- Generate table of contents from headings
- Validate internal links across a Markdown corpus
- Convert Markdown to simplified HTML
- Compute corpus statistics (word counts, heading counts, link counts)
- Batch process entire directories

## Usage

```bash
mdforge parse <file>          # Parse and display metadata
mdforge toc <file>            # Generate table of contents
mdforge html <file>           # Convert to simplified HTML
mdforge stats <file|dir>      # Display statistics
mdforge validate <dir>        # Validate internal links
mdforge batch <dir> --output <outdir>  # Batch process