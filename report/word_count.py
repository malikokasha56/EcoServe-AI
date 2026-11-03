"""Word count of the main text (chapters 1 to 8): prose, headings and captions.

Excludes the front matter (title page, abstract, acknowledgements, abbreviations), tables, code listings,
references and appendices.
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
total = 0
for f in sorted(glob.glob(os.path.join(HERE, "chapters", "0[1-8]_*.md"))):
    n, code = 0, False
    for line in open(f, encoding="utf-8"):
        s = line.strip()
        if s.startswith("```"):
            code = not code
            continue
        if code or s.startswith("|") or not s:
            continue
        if s.startswith("!["):
            s = re.match(r"!\[(.*?)\]", s).group(1)
        n += len(s.lstrip("#").split())
    total += n
    print(f"{os.path.basename(f):<28} {n:>6,}")
print(f"{'TOTAL main text':<28} {total:>6,}")
