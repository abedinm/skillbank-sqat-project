#!/usr/bin/env python3
"""
make_test_cases.py - render the 40 executed SkillBank test cases into the
SQAT Test Plan Project template's test-case table format.

Source: F:/outputs/sqat-skillbank/results.json, written by the Selenium suite when it ran
on 02/08/2026. Nothing here is composed; every field comes from that file.

The template's table is 10 rows x 6 columns with merges:

    Project Name        (0-2) | Test Designed by     (3-5)
    Test Case ID        (0-2) | Test Designed date   (3-5)
    Test Priority       (0-2) | Test Executed by     (3-5)
    Module Name         (0-2) | Test Execution date  (3-5)
    Test Title                (0-5)
    Description               (0-5)
    Precondition (If any)     (0-5)
    Test Steps | Test Data | Expected Results (2-3) | Actual Results | Status
    <the data for each of those>
    Post Condition            (0-5)

Post Condition is not a field in results.json. It is filled from the recorded `actual`
result, which is the observed state of the system after the test ran - that is what a
post-condition is. Review them; they are the student's own recorded observations, not
invented text.
"""

import json
import os

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

SRC = r"F:\outputs\sqat-skillbank\results.json"
OUT = r"F:\outputs\sqat-project\SkillBank_Test_Cases.docx"
PROJECT = "SkillBank"
FONT = "Calibri"
HDR_FILL = "D9E2F3"
LBL = RGBColor(0x1F, 0x38, 0x64)


def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def put(cell, label, value, size=9, bold_label=True):
    """Write 'Label: value' into a cell, label in bold."""
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    if label:
        r = p.add_run(label)
        r.bold = bold_label
        r.font.size = Pt(size)
        r.font.name = FONT
        r.font.color.rgb = LBL
    if value:
        r = p.add_run(value)
        r.font.size = Pt(size)
        r.font.name = FONT


def put_lines(cell, lines, size=9):
    """Write a list as separate lines in one cell."""
    cell.text = ""
    p = cell.paragraphs[0]
    for i, ln in enumerate(lines):
        if i:
            p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(str(ln))
        r.font.size = Pt(size)
        r.font.name = FONT


def keep_together(table):
    """Stop a case table splitting across a page break.

    Two mechanisms, both needed: w:cantSplit stops an individual ROW breaking mid-cell,
    and keep_with_next on every paragraph except those in the final row stops the table
    breaking BETWEEN rows.
    """
    rows = table.rows
    for ri, row in enumerate(rows):
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        trPr.append(cs)
        if ri < len(rows) - 1:
            for cell in row.cells:
                for par in cell.paragraphs:
                    par.paragraph_format.keep_with_next = True


def case_table(doc, c):
    t = doc.add_table(rows=10, cols=6)
    t.style = "Table Grid"
    t.autofit = True

    def span(r, c0, c1):
        return t.cell(r, c0).merge(t.cell(r, c1))

    put(span(0, 0, 2), "Project Name: ", PROJECT)
    put(span(0, 3, 5), "Test Designed by: ", c.get("designer", ""))
    put(span(1, 0, 2), "Test Case ID: ", c.get("id", ""))
    put(span(1, 3, 5), "Test Designed date: ", c.get("design_date", ""))
    put(span(2, 0, 2), "Test Priority (Low, Medium, High): ", c.get("priority", ""))
    put(span(2, 3, 5), "Test Executed by: ", c.get("designer", ""))
    put(span(3, 0, 2), "Module Name: ", c.get("module", ""))
    put(span(3, 3, 5), "Test Execution date: ", c.get("exec_date", ""))
    put(span(4, 0, 5), "Test Title: ", c.get("title", ""))
    put(span(5, 0, 5), "Description: ", c.get("description", ""))

    pre = c.get("precondition", "")
    dep = c.get("dependencies", "")
    cell = span(6, 0, 5)
    put(cell, "Precondition (If any): ", pre)
    if dep:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run("Dependencies: "); r.bold = True
        r.font.size = Pt(8.5); r.font.name = FONT; r.font.color.rgb = LBL
        r = p.add_run(dep); r.font.size = Pt(8.5); r.font.name = FONT

    hdrs = ["Test Steps", "Test Data", "Expected Results", None, "Actual Results",
            "Status (Pass/Fail)"]
    exp_hdr = t.cell(7, 2).merge(t.cell(7, 3))
    for ci, h in enumerate(hdrs):
        if h is None:
            continue
        cell = exp_hdr if ci == 2 else t.cell(7, ci)
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h); r.bold = True; r.font.size = Pt(9); r.font.name = FONT
        shade(cell, HDR_FILL)

    put_lines(t.cell(8, 0), c.get("steps", []))
    put_lines(t.cell(8, 1), c.get("data", []))
    exp_cell = t.cell(8, 2).merge(t.cell(8, 3))
    put(exp_cell, "", c.get("expected", ""))
    put(t.cell(8, 4), "", c.get("actual", ""))
    st = t.cell(8, 5)
    st.text = ""
    p = st.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(c.get("status", "")); r.bold = True; r.font.size = Pt(9.5)
    r.font.name = FONT
    r.font.color.rgb = RGBColor(0x1E, 0x7A, 0x33) if c.get("status") == "Pass" \
        else RGBColor(0xC0, 0x30, 0x20)

    put(span(9, 0, 5), "Post Condition: ", c.get("actual", ""))
    keep_together(t)
    return t


def main():
    cases = json.load(open(SRC, encoding="utf-8"))
    if isinstance(cases, dict):
        cases = cases.get("results", cases.get("cases", []))

    doc = Document()
    s = doc.sections[0]
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = s.page_height, s.page_width
    s.top_margin = s.bottom_margin = Inches(0.55)
    s.left_margin = s.right_margin = Inches(0.5)
    doc.styles["Normal"].font.name = FONT
    doc.styles["Normal"].font.size = Pt(9.5)

    h = doc.add_paragraph()
    r = h.add_run("TEST CASES / TEST ITEMS")
    r.bold = True; r.font.size = Pt(15); r.font.name = FONT; r.font.color.rgb = LBL
    p = doc.add_paragraph()
    r = p.add_run(f"{PROJECT} — {len(cases)} functional test cases, designed and executed "
                  f"against the live application with Selenium WebDriver.")
    r.font.size = Pt(10); r.font.name = FONT
    p.paragraph_format.space_after = Pt(10)

    # summary by module
    mods = {}
    for c in cases:
        m = c.get("module", "?")
        mods.setdefault(m, {"n": 0, "pass": 0})
        mods[m]["n"] += 1
        mods[m]["pass"] += (c.get("status") == "Pass")
    st = doc.add_table(rows=len(mods) + 2, cols=4)
    st.style = "Table Grid"
    for ci, hd in enumerate(["Module", "Test cases", "Passed", "Failed"]):
        cell = st.cell(0, ci); cell.text = ""
        rr = cell.paragraphs[0].add_run(hd); rr.bold = True
        rr.font.size = Pt(9.5); rr.font.name = FONT
        shade(cell, HDR_FILL)
    for ri, (m, d) in enumerate(mods.items(), start=1):
        for ci, v in enumerate([m, d["n"], d["pass"], d["n"] - d["pass"]]):
            cell = st.cell(ri, ci); cell.text = ""
            rr = cell.paragraphs[0].add_run(str(v))
            rr.font.size = Pt(9.5); rr.font.name = FONT
    tot = [len(cases), sum(d["pass"] for d in mods.values())]
    for ci, v in enumerate(["TOTAL", tot[0], tot[1], tot[0] - tot[1]]):
        cell = st.cell(len(mods) + 1, ci); cell.text = ""
        rr = cell.paragraphs[0].add_run(str(v)); rr.bold = True
        rr.font.size = Pt(9.5); rr.font.name = FONT
        shade(cell, "EDEDED")
    doc.add_paragraph()

    for i, c in enumerate(cases):
        cap = doc.add_paragraph()
        cap.paragraph_format.space_before = Pt(9)
        cap.paragraph_format.space_after = Pt(2)
        r = cap.add_run(f"{c.get('id','')} — {c.get('title','')}")
        r.bold = True; r.font.size = Pt(10); r.font.name = FONT; r.font.color.rgb = LBL
        cap.paragraph_format.keep_with_next = True
        case_table(doc, c)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc.save(OUT)
    print(f"written: {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
    print(f"  test cases rendered : {len(cases)}")
    print(f"  modules             : {len(mods)}")
    print(f"  pass / fail         : {tot[1]} / {tot[0]-tot[1]}")
    prios = {}
    for c in cases:
        prios[c.get("priority", "?")] = prios.get(c.get("priority", "?"), 0) + 1
    print(f"  priorities          : {prios}")


if __name__ == "__main__":
    main()
