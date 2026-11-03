"""Builds the report .docx from report/chapters/*.md, report/references.md and docs/testing.

The previous dissertation file is used only as a style template (fonts, heading styles, page size and margins).
All of its content is removed before the new text is written.
"""
import glob
import os
import re
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), "EcoServe AI Web Application (3)", "final dissertation.docx")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "EcoServe_AI_Report.docx")

doc = Document(TEMPLATE)
body = doc.element.body
for el in list(body):
    if el.tag != qn("w:sectPr"):
        body.remove(el)
for rid, rel in list(doc.part.rels.items()):
    if rel.reltype.endswith("/image"):
        doc.part.drop_rel(rid)
for section in doc.sections:
    for part in (section.header, section.footer):
        for p in part.paragraphs:
            p.text = ""

styles = doc.styles
for name in ("Heading 1", "Heading 2", "Heading 3"):
    ppr = styles[name].element.get_or_add_pPr()
    num = ppr.find(qn("w:numPr"))
    if num is not None:
        ppr.remove(num)

normal = styles["Normal"]
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_after = Pt(8)


def new_style(name, base, size=None, font=None, outline_body=False):
    if name in [s.name for s in styles]:
        return styles[name]
    st = styles.add_style(name, 1)
    st.base_style = styles[base]
    if size:
        st.font.size = Pt(size)
    if font:
        st.font.name = font
    if outline_body:
        ppr = st.element.get_or_add_pPr()
        lvl = OxmlElement("w:outlineLvl")
        lvl.set(qn("w:val"), "9")
        ppr.append(lvl)
    return st


fig_cap = new_style("Figure Caption", "Caption")
tab_cap = new_style("Table Title", "Caption")
for st in (fig_cap, tab_cap):
    st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    st.paragraph_format.line_spacing = 1.0
    st.paragraph_format.space_after = Pt(10)
    st.font.italic = False
    st.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
tab_cap.paragraph_format.keep_with_next = True
front_heading = new_style("Front Heading", "Heading 1", outline_body=True)
code = new_style("Code Block", "Normal", size=8.5, font="Consolas")
code.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
code.paragraph_format.line_spacing = 1.0
code.paragraph_format.space_after = Pt(0)
cell_style = new_style("Table Text", "Normal", size=9)
cell_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
cell_style.paragraph_format.line_spacing = 1.0
cell_style.paragraph_format.space_after = Pt(0)
ref_style = new_style("Reference Entry", "Normal", size=10.5)
ref_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
ref_style.paragraph_format.line_spacing = 1.15
ref_style.paragraph_format.left_indent = Inches(0.4)
ref_style.paragraph_format.first_line_indent = Inches(-0.4)


def add_field(paragraph, instr, placeholder):
    def run_with(el):
        r = paragraph.add_run()
        r._r.append(el)

    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    run_with(begin)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    run_with(it)
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    run_with(sep)
    paragraph.add_run(placeholder)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run_with(end)


def add_runs(p, text, size=None, bold=False):
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not part:
            continue
        r = p.add_run(part)
        r.bold = bold or (i % 2 == 1)
        if size:
            r.font.size = Pt(size)


def shade(cell, color):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcpr.append(shd)


def add_table(rows, size=9):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows if not re.match(r"^\|\s*-", r)]
    ncols = max(len(r) for r in cells)
    t = doc.add_table(rows=len(cells), cols=ncols)
    t.style = styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(cells):
        for j in range(ncols):
            cell = t.cell(i, j)
            p = cell.paragraphs[0]
            p.style = cell_style
            add_runs(p, row[j] if j < len(row) else "", size=size, bold=(i == 0))
            if i == 0:
                shade(cell, "E5E7EB")
    # Column widths from content: long text columns get more room, short code columns stay narrow.
    usable = 6.5
    char_in = 0.075 * size / 9
    # Every column first gets room for its longest word, then the remaining width is shared by typical length.
    mins, weights = [], []
    for j in range(ncols):
        col = [row[j] if j < len(row) else "" for row in cells]
        longest_word = max((len(w) for c in col for w in c.split()), default=1)
        typical = sorted(len(c) for c in col)[int(len(col) * 0.8)]
        mins.append((min(longest_word, 28) + 2) * char_in)
        weights.append(max(min(typical, 70) - longest_word, 0) + 1)
    spare = max(usable - sum(mins), 0)
    widths = [m + spare * w / sum(weights) for m, w in zip(mins, weights)]
    scale = usable / sum(widths)
    t.autofit = False
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    t._tbl.tblPr.append(layout)
    for j in range(ncols):
        for i in range(len(cells)):
            t.cell(i, j).width = Inches(widths[j] * scale)
    hdr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    hdr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_figure(caption, path):
    from PIL import Image

    full = os.path.join(HERE, path)
    im = Image.open(full)
    if os.path.basename(path).startswith("app_"):
        # Tall full page screenshots are cropped to the top part so the interface text stays readable.
        if im.height > im.width * 0.7:
            os.makedirs(os.path.join(HERE, "figures", "_cropped"), exist_ok=True)
            cropped = os.path.join(HERE, "figures", "_cropped", os.path.basename(path))
            im.crop((0, 0, im.width, int(im.width * 0.66))).save(cropped)
            full = cropped
        width = Inches(6.3)
    else:
        width = Inches(min(6.0, im.width / 220 * 0.8))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(full, width=width)
    doc.add_paragraph(caption, style=fig_cap)


def include_md_table(path, size):
    lines = [l for l in open(path, encoding="utf-8") if l.startswith("|")]
    add_table(lines, size=size)


def render(md_path, first_heading_break=True):
    lines = open(md_path, encoding="utf-8").read().splitlines()
    i, first = 0, True
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith("@") and not line.startswith("@include"):
            i += 1
            continue
        if line.startswith("@include"):
            what = line.split()[1]
            if what == "traceability":
                include_md_table(os.path.join(ROOT, "docs", "testing", "traceability.md"), 8.5)
            elif what == "evidence":
                include_md_table(os.path.join(ROOT, "docs", "testing", "test_evidence.md"), 7)
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                p = doc.add_paragraph(lines[i] or " ", style=code)
                ppr = p._p.get_or_add_pPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:fill"), "F3F4F6")
                ppr.append(shd)
                i += 1
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            i += 1
            continue
        m = re.match(r"^(#{1,3}) (.+)$", line)
        if m:
            level, text = len(m.group(1)), m.group(2)
            front = os.path.basename(md_path).startswith("00")
            p = doc.add_paragraph(text, style=front_heading if front else f"Heading {level}")
            if level == 1 and (first_heading_break or not first):
                p.paragraph_format.page_break_before = True
            first = False
            i += 1
            continue
        m = re.match(r"^!\[(.+?)\]\((.+?)\)$", line)
        if m:
            add_figure(m.group(1), m.group(2))
            i += 1
            continue
        nxt = next((l for l in lines[i + 1:] if l.strip()), "")
        if re.match(r"^Table [A-Z0-9]+\.\d+ ", line) and nxt.startswith("|"):
            doc.add_paragraph(line, style=tab_cap)
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            add_table(rows)
            continue
        p = doc.add_paragraph()
        add_runs(p, line)
        i += 1


# ---------------------------------------------------------------- title page
meta = {}
for line in open(os.path.join(HERE, "chapters", "00_front.md"), encoding="utf-8"):
    m = re.match(r"^@(\w+) (.+)$", line.strip())
    if m:
        meta[m.group(1)] = m.group(2)


def centred(text, size, bold=False, space=12, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    if color:
        r.font.color.rgb = color
    return p


for _ in range(3):
    doc.add_paragraph()
centred("University of Huddersfield", 14, space=4)
centred(meta["school"].split(",")[0], 12, space=40)
centred(meta["title"], 22, bold=True, space=14, color=RGBColor(0x1F, 0x4D, 0x78))
centred(meta["subtitle"], 14, space=60)
centred(meta["author"], 13, space=4)
centred(meta["studentid"], 12, space=30)
centred("A dissertation submitted in partial fulfilment of the requirements for the degree of", 11, space=4)
centred(meta["programme"], 12, bold=True, space=30)
centred(f"Module: {meta['module']}", 11, space=4)
centred(f"Supervisor: {meta['supervisor']}", 11, space=40)
centred(meta["date"], 11)

render(os.path.join(HERE, "chapters", "00_front.md"))

for title, instr in (("Table of Contents", 'TOC \\o "1-3" \\h \\z \\u'),
                     ("List of Figures", 'TOC \\h \\z \\t "Figure Caption,1"'),
                     ("List of Tables", 'TOC \\h \\z \\t "Table Title,1"')):
    p = doc.add_paragraph(title, style=front_heading)
    p.paragraph_format.page_break_before = True
    add_field(doc.add_paragraph(), instr, "Right click here and choose Update Field to build this list.")

# ---------------------------------------------------------------- main text in its own section (page 1 onwards)
main = doc.add_section(WD_SECTION.NEW_PAGE)
chapter_files = sorted(f for f in glob.glob(os.path.join(HERE, "chapters", "*.md"))
                       if not os.path.basename(f).startswith(("00", "09")))
for n, f in enumerate(chapter_files):
    render(f, first_heading_break=n > 0)

p = doc.add_paragraph("References", style="Heading 1")
p.paragraph_format.page_break_before = True
refs = open(os.path.join(HERE, "references.md"), encoding="utf-8").read().split("## Verification notes")[0]
for line in refs.splitlines():
    if line.strip() and not line.startswith("#"):
        doc.add_paragraph(line.strip(), style=ref_style)

render(os.path.join(HERE, "chapters", "09_appendices.md"))


# ---------------------------------------------------------------- page numbering
def page_numbers(section, fmt, start=None):
    sp = section._sectPr
    pg = sp.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType")
        sp.append(pg)
    pg.set(qn("w:fmt"), fmt)
    if start:
        pg.set(qn("w:start"), str(start))
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.text = ""
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(fp, "PAGE", "1")


front_section, main_section = doc.sections[0], doc.sections[-1]
page_numbers(front_section, "lowerRoman", 1)
front_section.different_first_page_header_footer = True
page_numbers(main_section, "decimal", 1)
main_section.different_first_page_header_footer = False

settings = doc.settings.element
upd = OxmlElement("w:updateFields")
upd.set(qn("w:val"), "true")
settings.append(upd)

doc.core_properties.title = meta["title"]
doc.core_properties.author = meta["author"]
doc.core_properties.comments = ""
doc.save(OUT)
print("saved", OUT, f"{os.path.getsize(OUT) / 1e6:.1f} MB")
