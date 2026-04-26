python3 << 'EOF'
import re

# Test what pattern string we need
# We want to match: [Example](https://example.com)
# The regex is: $$([^$$]*)\]\(([^)]+)\)

# Method 1: double-quoted raw string
p1 = re.compile(r"$$([^$$]*)\]\(([^)]+)\)")

# Method 2: build from chr
BS = chr(92)
p2 = re.compile(BS+"[([^"+BS+"]]*)" +BS+ "]"+BS+"(([^)]+)"+BS+")")

text = "Here is a [link](https://example.com) test"

m1 = p1.findall(text)
m2 = p2.findall(text)

print(f"Method 1 pattern: {p1.pattern}")
print(f"Method 1 matches: {m1}")
print(f"Method 2 pattern: {p2.pattern}")
print(f"Method 2 matches: {m2}")

# Now check what's in the actual file
with open("mdforge/parser/links.py", "r") as f:
    content = f.read()

print()
print("=== Current links.py content ===")
print(content[:500])
print()

# Find the LINK_PATTERN line
for i, line in enumerate(content.split("\n"), 1):
    if "LINK_PATTERN" in line or "compile" in line or "chr(" in line:
        print(f"Line {i}: {repr(line)}")
EOF

