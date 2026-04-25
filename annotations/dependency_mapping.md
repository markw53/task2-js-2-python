Dependency Mapping
Direct dependency substitutions
JavaScript dependency	Python equivalent	Notes
commander (npm)	click (PyPI)	Commander.js provides CLI argument parsing with subcommands, options, and help generation. Click is the idiomatic Python equivalent — decorator-based rather than method-chaining, but same capabilities.
chalk (npm)	colorama + ANSI codes, or no dependency	Chalk provides colored terminal output. Python can use colorama or raw ANSI escape codes. Since logging goes to stderr only, a lightweight approach with ANSI codes and no third-party dependency is acceptable.
gray-matter (npm)	python-frontmatter (PyPI)	Both parse YAML frontmatter from Markdown files. python-frontmatter returns a Post object with .metadata and .content — slightly different API than gray-matter's { data, content } but functionally equivalent.
glob (npm)	glob / pathlib (stdlib)	npm's glob package provides recursive file pattern matching. Python's pathlib.Path.glob() and glob.glob() are stdlib equivalents — no third-party dependency needed.
fs.promises (Node.js stdlib)	pathlib + open() (stdlib)	Node.js async file I/O via fs.promises.readFile, fs.promises.writeFile, fs.promises.stat, fs.promises.mkdir. Python equivalents are synchronous pathlib.Path.read_text(), .write_text(), .stat(), .mkdir(). Async is non-idiomatic for a CLI tool in Python — synchronous I/O is preferred.
path (Node.js stdlib)	pathlib / os.path (stdlib)	path.resolve → pathlib.Path.resolve(). path.join → pathlib.Path / "child" or os.path.join. path.basename → pathlib.Path.stem or .name. path.dirname → pathlib.Path.parent.
process (Node.js global)	sys (stdlib)	process.argv → sys.argv. process.exit(code) → sys.exit(code). process.env → os.environ.
JSON (built-in)	json (stdlib)	JSON.stringify(obj, null, 2) → json.dumps(obj, indent=2). JSON.parse(str) → json.loads(str). Direct equivalents.
RegExp (built-in)	re (stdlib)	JavaScript regex literals (/pattern/g) → Python re.compile() or re.findall(). Key difference: JavaScript's exec() with lastIndex state → Python's re.finditer() which is stateless.
console.error	print(..., file=sys.stderr) or logging	stderr output for log messages. Python's print with file=sys.stderr is the direct equivalent.
console.log	print()	stdout output for CLI results.
Dependencies NOT carried over
eslint / .eslintrc.json: Linting config replaced by Python equivalents (flake8, ruff, etc.) if desired — not required for functional equivalence.
package-lock.json: Lock file replaced by pip freeze or pyproject.toml constraints — not a translated artifact.
node_modules/: Replaced by Python virtual environment / site-packages — managed by pip.
