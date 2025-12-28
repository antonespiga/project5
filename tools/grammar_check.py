import sys
from pathlib import Path

try:
    import language_tool_python
except Exception as e:
    print('MISSING_LIB')
    sys.exit(2)

p = Path('README_en.md')
if not p.exists():
    print('FILE_NOT_FOUND')
    sys.exit(3)

text = p.read_text(encoding='utf-8')
tool = language_tool_python.LanguageTool('en-US')
matches = tool.check(text)

# Show up to 40 matches
for i, m in enumerate(matches[:40], 1):
    start = m.offset
    end = start + m.errorLength
    context = text[max(0, start-30):min(len(text), end+30)].replace('\n',' ')
    print(f"{i}. Issue: {m.message}\n   Context: {context}\n   Suggested: {m.replacements}\n")

print('TOTAL_ISSUES:', len(matches))
