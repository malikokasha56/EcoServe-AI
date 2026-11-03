"""Checks the report chapters before building: punctuation rules for prose and citation consistency."""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
chapters = sorted(glob.glob(os.path.join(HERE, "chapters", "*.md")))
refs_text = open(os.path.join(HERE, "references.md"), encoding="utf-8").read().split("## Verification notes")[0]
ref_lines = [l for l in refs_text.splitlines() if l.strip() and not l.startswith("#")]

# Tokens that may legitimately contain a hyphen or colon: identifiers, files, paths, URLs, proper names.
ALLOWED = re.compile(r"(\b(?:N?FR|T|UC)-\d+\b|\S+\.(?:py|bat|sh|csv|json|md|exe|tsx|ts|txt)\b|\S*[/\\]\S*|https?://\S+|\S+@\S+|Siami-Namini|menu-items|food-items)")


def prose_lines(path):
    in_code = False
    for n, line in enumerate(open(path, encoding="utf-8"), start=1):
        s = line.rstrip("\n")
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or s.startswith("|") or s.startswith("![") or s.startswith("@") or not s.strip():
            continue
        yield n, s


problems = 0
for path in chapters:
    name = os.path.basename(path)
    for n, s in prose_lines(path):
        clean = ALLOWED.sub("", s)
        for ch, label in (("—", "em dash"), ("–", "en dash"), (";", "semicolon"), (":", "colon"), ("-", "hyphen")):
            if ch in clean:
                i = clean.index(ch)
                print(f"{name}:{n} {label}: ...{clean[max(0, i - 40):i + 30]}...")
                problems += 1

# Citation check: every cited year must sit next to a known first-author surname, and every reference must be cited.
surnames = {}
for l in ref_lines:
    m = re.match(r"([^,(]+?)(?:,| \()", l)
    y = re.search(r"\((\d{4}|n\.d\.)\)", l)
    if m and y:
        key = m.group(1).strip().split()[0]
        surnames.setdefault(key, set()).add(y.group(1))
alias = {"United": "United Nations Environment Programme", "BCS,": "BCS"}
body = "\n".join(s for p in chapters for _, s in prose_lines(p)) + "\n" + "\n".join(
    l for p in chapters for l in open(p, encoding="utf-8") if l.startswith("|"))
cited = set()
for m in re.finditer(r"(19[5-9]\d|20[0-2]\d|n\.d\.)", body):
    window = body[max(0, m.start() - 90):m.start()]
    hits = [k for k in surnames if re.search(r"\b" + re.escape(k.rstrip(",")) + r"\b", window) and m.group(1) in surnames[k]]
    if hits:
        cited.update(hits)
    elif "(" in window[-60:] or re.search(r"[A-Z][a-z]+ (?:et al\. )?\($", window):
        ctx = body[max(0, m.start() - 50):m.end() + 2].replace("\n", " ")
        if re.search(r"[A-Z][a-zé]+,? (?:et al\.,? )?\(?" + re.escape(m.group(1)), ctx):
            print(f"citation without reference: ...{ctx}...")
            problems += 1
for k in surnames:
    if k not in cited:
        print(f"reference never cited: {k} {sorted(surnames[k])}")
        problems += 1

words = sum(len(s.split()) for p in chapters if not os.path.basename(p).startswith(("00", "09")) for _, s in prose_lines(p))
print(f"\n{problems} problem(s). Main text prose: about {words:,} words (chapters 1 to 8, excluding tables and code).")
