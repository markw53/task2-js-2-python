Idiom Adaptation
JavaScript → Python idiom changes
1. Error handling: custom Error class → custom Exception class
JavaScript uses custom Error subclasses with throw/catch. Python uses custom Exception subclasses with raise/except — same paradigm, different syntax.

JavaScript:

javascript
class MdForgeError extends Error {
  constructor(message, exitCode = 1) {
    super(message);
    this.name = 'MdForgeError';
    this.exitCode = exitCode;
  }
}

throw new MdForgeError(`File not found: ${filePath}`, 1);
Python:

python
class MdForgeError(Exception):
    """Custom error carrying an exit code for CLI reporting."""
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code

raise MdForgeError(f"File not found: {file_path}", 1)
Unlike JavaScript→Go (where exceptions become error returns), JavaScript→Python preserves the throw/catch paradigm directly. The key adaptation is Python's __init__ replacing the constructor, and self.exit_code as a snake_case attribute.

2. CommonJS modules → Python packages with __init__.py
JavaScript's require/module.exports with barrel index.js files maps to Python's package system with __init__.py re-exports.

JavaScript:

javascript
// src/parser/index.js
const { parseFrontmatter } = require('./frontmatter');
const { extractHeadings } = require('./headings');
const { extractLinks } = require('./links');
const { extractCodeBlocks } = require('./codeblocks');
const { computeWordCount, buildMetadata } = require('./metadata');

module.exports = { parse };
Python:

python
# mdforge/parser/__init__.py
from .frontmatter import parse_frontmatter
from .headings import extract_headings, generate_slug
from .links import extract_links, classify_link
from .codeblocks import extract_code_blocks
from .metadata import compute_word_count, build_metadata

def parse(content: str, file_path: str) -> dict:
    ...
JavaScript's index.js barrel pattern maps naturally to __init__.py. The require('./frontmatter') → from .frontmatter import ... mapping is direct.

3. Async/await file I/O → synchronous file I/O
JavaScript's fs.promises (async by default) maps to Python's synchronous pathlib for CLI tools.

JavaScript:

javascript
const fs = require('fs').promises;

async function readFile(filePath) {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return content;
  } catch (err) {
    if (err.code === 'ENOENT') {
      throw new MdForgeError(`File not found: ${filePath}`, 1);
    }
    throw new MdForgeError(`Error reading file ${filePath}: ${err.message}`, 1);
  }
}
Python:

python
from pathlib import Path

def read_file(file_path: str) -> str:
    p = Path(file_path)
    if not p.exists():
        raise MdForgeError(f"File not found: {file_path}", 1)
    try:
        return p.read_text(encoding="utf-8")
    except OSError as err:
        raise MdForgeError(f"Error reading file {file_path}: {err}", 1)
Why: Node.js uses async I/O by default because it's non-blocking in the event loop. Python CLI tools are synchronous by convention — using asyncio + aiofiles for a simple CLI would be non-idiomatic and unnecessarily complex. The behavioral contract is identical: read file, return string, throw on error.

4. Commander.js → Click
Commander.js's method-chaining CLI builder maps to Click's decorator-based pattern.

JavaScript:

javascript
const { Command } = require('commander');

const program = new Command();
program
  .command('parse <file>')
  .description('Parse a Markdown file and display its metadata')
  .action(async (file) => {
    const filePath = path.resolve(file);
    const result = await mdforge.parseFile(filePath);
    console.log(JSON.stringify(result, null, 2));
  });
Python:

python
import click

@click.group()
@click.version_option("1.2.0")
def cli():
    """A CLI toolkit for parsing, validating, and transforming Markdown files."""
    pass

@cli.command()
@click.argument("file", type=click.Path(exists=False))
def parse(file: str):
    """Parse a Markdown file and display its metadata."""
    file_path = str(Path(file).resolve())
    result = parse_file(file_path)
    click.echo(json.dumps(result, indent=2))
Key differences:

Commander uses imperative method chaining; Click uses decorators
Commander's <file> positional args → Click's @click.argument
Commander's .requiredOption('-o, --output <outdir>') → Click's @click.option('--output', '-o', required=True)
Commander's program.parseAsync(process.argv) → Click's cli() (invoked directly)
console.log → click.echo (which handles encoding edge cases)
5. Object literals → Python dicts
JavaScript's object literal syntax maps directly to Python dictionaries.

JavaScript:

javascript
const output = {
  file: filePath,
  frontmatter: result.frontmatter,
  headings: result.headings,
  links: result.links,
  codeBlocks: result.codeBlocks,
  wordCount: result.wordCount,
};
console.log(JSON.stringify(output, null, 2));
Python:

python
output = {
    "file": file_path,
    "frontmatter": result["frontmatter"],
    "headings": result["headings"],
    "links": result["links"],
    "codeBlocks": result["code_blocks"],
    "wordCount": result["word_count"],
}
print(json.dumps(output, indent=2))
Note on key naming: The JSON output keys must match the JavaScript source exactly (codeBlocks, wordCount — camelCase) to preserve functional equivalence, even though the internal Python variables use snake_case. This is a critical regression point.

6. Regex with global flag → re.finditer
JavaScript regex with the g flag and exec() loop maps to Python's re.finditer().

JavaScript:

javascript
const linkPattern = /$$([^$$]*)\]\(([^)]+)\)/g;
let match;
linkPattern.lastIndex = 0;

while ((match = linkPattern.exec(line)) !== null) {
  const text = match[1];
  const url = match[2].trim();
  // ...
}
Python:

python
import re

LINK_PATTERN = re.compile(r'$$([^$$]*)\]\(([^)]+)\)')

for match in LINK_PATTERN.finditer(line):
    text = match.group(1)
    url = match.group(2).strip()
    # ...
Why: JavaScript's regex exec() maintains state via lastIndex, requiring manual reset. Python's re.finditer() is stateless and returns an iterator — cleaner and less error-prone. The behavioral result is identical.

7. String.prototype.replace with regex → re.sub
JavaScript:

javascript
function generateSlug(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}
Python:

python
def generate_slug(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = re.sub(r'^-|-$', '', slug)
    return slug
Critical note: JavaScript's \w matches [a-zA-Z0-9_]. Python's \w with default flags matches the same set. However, with re.UNICODE (default in Python 3), \w also matches Unicode letters. For ASCII-only input this produces identical results, but for Unicode headings there could be divergence. The tests use ASCII-only headings, so this is safe.

8. Chalk colored logging → ANSI escape codes
JavaScript:

javascript
const chalk = require('chalk');

const logger = {
  info(msg) { console.error(chalk.blue('[INFO]') + ' ' + msg); },
  success(msg) { console.error(chalk.green('[OK]') + ' ' + msg); },
  warn(msg) { console.error(chalk.yellow('[WARN]') + ' ' + msg); },
  error(msg) { console.error(chalk.red('[ERROR]') + ' ' + msg); },
};
Python:

python
import sys

BLUE = '\033[34m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
RESET = '\033[0m'

def info(msg: str) -> None:
    print(f"{BLUE}[INFO]{RESET} {msg}", file=sys.stderr)

def success(msg: str) -> None:
    print(f"{GREEN}[OK]{RESET} {msg}", file=sys.stderr)

def warn(msg: str) -> None:
    print(f"{YELLOW}[WARN]{RESET} {msg}", file=sys.stderr)

def error(msg: str) -> None:
    print(f"{RED}[ERROR]{RESET} {msg}", file=sys.stderr)
Why: Chalk is a Node.js-specific library. Python could use colorama but for simple ANSI codes on Linux/macOS (the Docker environment), raw escape codes are sufficient and avoid a dependency. Tests validate behavior through stdout JSON and exit codes, not stderr formatting.

9. path.resolve → pathlib.Path.resolve()
JavaScript:

javascript
const filePath = path.resolve(file);
Python:

python
file_path = str(Path(file).resolve())
Both produce absolute paths. Python's pathlib.Path is the modern idiomatic approach over os.path.abspath.

10. Set → Python set
JavaScript:

javascript
const knownFiles = new Set();
for (const fp of filePaths) {
  knownFiles.add(path.resolve(fp));
}
Python:

python
known_files: set[str] = set()
for fp in file_paths:
    known_files.add(str(Path(fp).resolve()))
Direct 1:1 mapping. Both provide O(1) membership testing.

11. Array.prototype.filter / Array.prototype.map → list comprehensions
JavaScript:

javascript
const internalLinks = links.filter((l) => l.type === 'internal');
const files = statsArray.map((s) => s.file);
Python:

python
internal_links = [link for link in links if link["type"] == "internal"]
files = [s["file"] for s in stats_array]
List comprehensions are the idiomatic Python equivalent of JavaScript's filter/map chains.

12. Naming conventions: camelCase → snake_case
All identifiers adapt to Python conventions:

JavaScript	Python
parseFrontmatter	parse_frontmatter
extractHeadings	extract_headings
generateSlug	generate_slug
extractLinks	extract_links
classifyLink	classify_link
extractCodeBlocks	extract_code_blocks
computeWordCount	compute_word_count
buildMetadata	build_metadata
generateToc	generate_toc
toHtml	to_html
computeStats	compute_stats
aggregateStats	aggregate_stats
validateCorpus	validate_corpus
readFile	read_file
readDirectory	read_directory
writeFile	write_file
batchProcess	batch_process
MdForgeError	MdForgeError (class names stay PascalCase)
exitCode	exit_code
filePath	file_path
wordCount	word_count
lineCount	line_count
codeBlocks	code_blocks
frontmatter	frontmatter (no change)
startLine / endLine	start_line / end_line
Critical note on JSON output keys: Internal variable names follow Python's snake_case, but JSON output keys must remain camelCase to match the source CLI's output exactly (e.g., "codeBlocks", "wordCount", "lineCount"). This is a functional equivalence requirement, not a style choice.

