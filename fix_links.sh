cat > /tmp/fix_links.py << 'FIXEOF'
import os
import sys

# Build the file content byte by byte - no shell interpretation possible
lines = [
    '"""Link extraction and classification."""',
    '',
    'import re',
    '',
    '',
    '# Build pattern from char codes to avoid editor/shell corruption',
    'LINK_PATTERN = re.compile(',
    '    chr(92) + chr(91)          # \$$',
    '    + "([^"',
    '    + chr(92) + chr(93)        # \$$',
    '    + "]*)"',
    '    + chr(92) + chr(93)        # \\]',
    '    + chr(92) + chr(40)        # \\(',
    '    + "([^"',
    '    + chr(41)                  # )',
    '    + "]+)"',
    '    + chr(92) + chr(41)        # \\)',
    ')',
    '',
    '',
    'def extract_links(body: str) -> list[dict]:',
    '    """Extract all links from Markdown body content."""',
    '    links = []',
    '    lines = body.split("\\n")',
    '    in_code_block = False',
    '',
    '    for i, line in enumerate(lines):',
    '        trimmed = line.lstrip()',
    '',
    '        if trimmed.startswith("```") or trimmed.startswith("~~~"):',
    '            in_code_block = not in_code_block',
    '            continue',
    '',
    '        if in_code_block:',
    '            continue',
    '',
    '        for match in LINK_PATTERN.finditer(line):',
    '            text = match.group(1)',
    '            url = match.group(2).strip()',
    '            link_type = classify_link(url)',
    '',
    '            links.append({',
    '                "text": text,',
    '                "url": url,',
    '                "type": link_type,',
    '                "line": i + 1,',
    '            })',
    '',
    '    return links',
    '',
    '',
    'def classify_link(url: str) -> str:',
    '    """Classify a URL into a link type."""',
    '    if url.startswith("#"):',
    '        return "anchor"',
    '    if url.startswith("http://") or url.startswith("https://"):',
    '        return "external"',
    '    if url.startswith("mailto:") or url.startswith("ftp://"):',
    '        return "other"',
    '    return "internal"',
    '',
]

target = sys.argv[1] if len(sys.argv) > 1 else "mdforge/parser/links.py"
with open(target, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote {target}")

# Verify
import importlib.util
spec = importlib.util.spec_from_file_location("links", target)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

test_text = "Click [here](https://example.com) now"
matches = list(mod.LINK_PATTERN.finditer(test_text))
print(f"Pattern: {mod.LINK_PATTERN.pattern}")
print(f"Test matches: {len(matches)}")
for m in matches:
    print(f"  text={m.group(1)}, url={m.group(2)}")

result = mod.extract_links("# Doc\n\n[link](https://example.com)\n[other](./page.md)\n[anchor](#top)\n")
print(f"extract_links found {len(result)} links:")
for r in result:
    print(f"  {r}")

if len(matches) != 1:
    print("FAIL: regex not working")
    sys.exit(1)
print("SUCCESS: regex works correctly")
FIXEOF

cd /tmp/mdforge-golden
python3 /tmp/fix_links.py mdforge/parser/links.py