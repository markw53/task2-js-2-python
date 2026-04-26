cat > ~/fix_and_test.py << 'ENDSCRIPT'
"""Fix links.py and html.py regex corruption, then verify."""
import importlib.util
import os
import re
import sys

def build_link_pattern_str():
    """Build the regex pattern string using chr() - impossible to corrupt."""
    # We want: $$([^$$]*)\]\(([^)]+)\)
    BS = chr(92)   # backslash
    OB = chr(91)   # [
    CB = chr(93)   # ]
    OP = chr(40)   # (
    CP = chr(41)   # )
    return BS+OB + "([^" + BS+CB + "]*)" + BS+CB + BS+OP + "([^" + CP + "]+)" + BS+CP

def write_links_py(filepath):
    """Write a correct links.py file."""
    pattern_str = build_link_pattern_str()
    
    code = f'''"""Link extraction and classification."""

import re

LINK_PATTERN = re.compile({repr(pattern_str)})


def extract_links(body: str) -> list[dict]:
    """Extract all links from Markdown body content."""
    links = []
    lines = body.split("\\n")
    in_code_block = False

    for i, line in enumerate(lines):
        trimmed = line.lstrip()

        if trimmed.startswith("```") or trimmed.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        for match in LINK_PATTERN.finditer(line):
            text = match.group(1)
            url = match.group(2).strip()
            link_type = classify_link(url)

            links.append({{
                "text": text,
                "url": url,
                "type": link_type,
                "line": i + 1,
            }})

    return links


def classify_link(url: str) -> str:
    """Classify a URL into a link type."""
    if url.startswith("#"):
        return "anchor"
    if url.startswith("http://") or url.startswith("https://"):
        return "external"
    if url.startswith("mailto:") or url.startswith("ftp://"):
        return "other"
    return "internal"
'''
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Wrote {filepath}")
    
    # Verify
    compiled = re.compile(pattern_str)
    test = "[Example](https://example.com)"
    m = compiled.search(test)
    assert m is not None, f"Pattern {repr(pattern_str)} failed to match {repr(test)}"
    print(f"  Pattern verified: {repr(compiled.pattern)}")
    print(f"  Test match: text={m.group(1)}, url={m.group(2)}")


def fix_html_py(filepath):
    """Fix the link regex in html.py."""
    pattern_str = build_link_pattern_str()
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add _LINK_RE if not present
    link_re_def = f"\n_LINK_RE = re.compile({repr(pattern_str)})\n"
    
    if "_LINK_RE" not in content:
        content = content.replace("import re\n", "import re\n" + link_re_def)
        print(f"  Added _LINK_RE definition")
    
    # Find and replace the re.sub call for links in _inline_markdown
    # Look for any line that has re.sub with link_replace
    new_content_lines = []
    replaced = False
    for line in content.split("\n"):
        if "link_replace" in line and "re.sub" in line:
            # Replace with _LINK_RE.sub
            indent = line[:len(line) - len(line.lstrip())]
            new_content_lines.append(f"{indent}result = _LINK_RE.sub(_link_replace, result)")
            replaced = True
            print(f"  Replaced re.sub link line")
        else:
            new_content_lines.append(line)
    
    if not replaced:
        # Check if it already uses _LINK_RE
        if "_LINK_RE.sub" in content:
            print(f"  Already using _LINK_RE.sub")
        else:
            print(f"  WARNING: Could not find link re.sub to replace")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_content_lines))
    
    print(f"Updated {filepath}")


def verify_module(filepath, module_name):
    """Import and test a module."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_and_test.py <golden_repo_path>")
        print("Example: python fix_and_test.py /tmp/mdforge-golden")
        sys.exit(1)
    
    repo = sys.argv[1]
    
    links_path = os.path.join(repo, "mdforge", "parser", "links.py")
    html_path = os.path.join(repo, "mdforge", "transform", "html.py")
    
    print("=" * 50)
    print("Fixing links.py")
    print("=" * 50)
    write_links_py(links_path)
    
    print()
    print("=" * 50)
    print("Fixing html.py")
    print("=" * 50)
    fix_html_py(html_path)
    
    print()
    print("=" * 50)
    print("Verifying links module")
    print("=" * 50)
    mod = verify_module(links_path, "links")
    
    test_body = "# Test\n\n[external](https://example.com)\n[internal](./other.md)\n[anchor](#section)\n"
    result = mod.extract_links(test_body)
    print(f"Found {len(result)} links:")
    for r in result:
        print(f"  {r['type']}: {r['url']}")
    
    assert len(result) == 3, f"Expected 3 links, got {len(result)}"
    types = [r["type"] for r in result]
    assert "external" in types
    assert "internal" in types
    assert "anchor" in types
    
    print()
    print("ALL VERIFICATIONS PASSED")
ENDSCRIPT

echo "Script saved to ~/fix_and_test.py"