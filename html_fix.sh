cat > /tmp/fix_html.py << 'FIXEOF'
import sys
import re

target = sys.argv[1] if len(sys.argv) > 1 else "mdforge/transform/html.py"

with open(target, "r", encoding="utf-8") as f:
    content = f.read()

# Build the correct link regex using chr() - impossible to corrupt
correct_link_pattern = (
    'chr(92) + chr(91)          # ' + repr(chr(92)+chr(91)) + '\n'
    '    + "([^"\n'
    '    + chr(92) + chr(93)        # ' + repr(chr(92)+chr(93)) + '\n'
    '    + "]+)"\n'
    '    + chr(92) + chr(93)        # ' + repr(chr(92)+chr(93)) + '\n'
    '    + chr(92) + chr(40)        # ' + repr(chr(92)+chr(40)) + '\n'
    '    + "([^"\n'
    '    + chr(41)                  # ' + repr(chr(41)) + '\n'
    '    + "]+)"\n'
    '    + chr(92) + chr(41)        # ' + repr(chr(92)+chr(41))
)

# Find _inline_markdown and replace link regex
# We'll add a module-level compiled pattern and use it
new_pattern_def = '''
# Link pattern built from char codes to avoid shell/editor corruption
_LINK_RE = re.compile(
    chr(92) + chr(91)
    + "([^"
    + chr(92) + chr(93)
    + "]+)"
    + chr(92) + chr(93)
    + chr(92) + chr(40)
    + "([^"
    + chr(41)
    + "]+)"
    + chr(92) + chr(41)
)
'''

# Check if _LINK_RE already exists
if "_LINK_RE" not in content:
    # Add it after the imports
    content = content.replace(
        'import re\n',
        'import re\n' + new_pattern_def + '\n'
    )

# Replace the link sub in _inline_markdown
# Find any re.sub call for links and replace with _LINK_RE.sub
old_patterns = [
    r'''re.sub(r"$$([^$$]+)\]\(([^)]+)\)", _link_replace, result)''',
    r'''re.sub(r'$$([^$$]+)\]\(([^)]+)\)', _link_replace, result)''',
]

replacement = '_LINK_RE.sub(_link_replace, result)'

for old in old_patterns:
    if old in content:
        content = content.replace(old, replacement)
        print(f"Replaced link regex pattern")
        break
else:
    # Try a broader search
    import re as real_re
    # Find the re.sub line that handles links
    link_sub_pattern = real_re.compile(r"result = re\.sub\(r[\"'].*?$$.*?$$.*?\(.*?\).*?[\"'],\s*_link_replace,\s*result\)")
    match = link_sub_pattern.search(content)
    if match:
        content = content[:match.start()] + "result = " + replacement + content[match.end():]
        print(f"Replaced link regex pattern (broad match)")
    else:
        print("WARNING: Could not find link regex to replace in _inline_markdown")
        print("Searching for any line with 'link_replace'...")
        for i, line in enumerate(content.split('\n'), 1):
            if 'link_replace' in line:
                print(f"  Line {i}: {repr(line)}")

with open(target, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {target}")

# Verify the pattern compiles
exec_globals = {}
exec("import re\n" + new_pattern_def, exec_globals)
test = "Visit [Example](https://example.com) for more."
matches = list(exec_globals['_LINK_RE'].finditer(test))
print(f"HTML link pattern test: {len(matches)} matches")
assert len(matches) == 1
print("SUCCESS")
FIXEOF

cd /tmp/mdforge-golden
python3 /tmp/fix_html.py golden_repo/mdforge/transform/html.py
