#!/usr/bin/env python3
"""
add_interface.py - answer the template's "Draw the system interface" instruction.

The template says, verbatim, under System Interface:

    "Draw the system interface where the users will interact with the system's
     functionality."

Section 5.3 was a table listing interfaces. A list is not a drawing. This replaces it
with two drawings and eight screenshots captured during test execution, keeping the
coverage table underneath so the traceability is not lost.

Two further gaps found in the same re-read of the template:

  - System Features. The template's worked example gives each requirement a "Priority
    Level:" AND a "Precondition:". Section 5.1 carried priority but no precondition.
  - Project Requirements. The template's example is "Total budget 3,60,000 BDT" and
    "Total Development Time 1 year 3 months" - the WHOLE project, not just the testing
    slice. Section 5.4 costed testing only.
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "make_test_plan.py")
t = io.open(P, encoding="utf-8").read()

SHOTS = r"F:\outputs\sqat-skillbank\screenshots"

# ---------------------------------------------------------------- 5.3 rebuilt
OLD = '''    H(doc, "5.3  System Interface", 2)
    P(doc, "The interfaces exercised by this plan are listed below. Each was captured "
           "during execution; the full set of 107 screenshots accompanies the test summary "
           "report.")'''

NEW = '''    H(doc, "5.3  System Interface", 2)
    P(doc, "Figure 1 draws every screen a user can reach and the two authorisation "
           "boundaries that divide them. Figure 2 draws the request path behind those "
           "screens. Figures 3 to 10 are the interfaces themselves, captured while the "
           "test suite was running against the application; the full set of 107 "
           "screenshots accompanies the test summary report.")
    FIG(doc, "fig_screen_flow.png", 1,
        "Screen flow. Public screens sit left of the dashed line; everything right of it "
        "requires an authenticated session and everything below the dotted line "
        "additionally requires the administrator role.", width=6.5)
    FIG(doc, "fig_architecture.png", 2,
        "Request path. A single front controller dispatches to five controllers, which "
        "reach the seven tables only through their models.", width=6.3)

    SHOT(doc, "TC_reg-01_1.png", 3, "Registration. New members are created here and "
         "receive their three opening credits.")
    SHOT(doc, "TC_log-01_1.png", 4, "Login. Credentials are checked against the stored "
         "hash; failure returns to this screen with the reason.")
    SHOT(doc, "TC_log-01_3.png", 5, "Member dashboard, the hub every authenticated screen "
         "is reached from.")
    SHOT(doc, "TC_off-01_1.png", 6, "Create an offer against a catalogue skill, with a "
         "title, description and level.")
    SHOT(doc, "TC_ses-01_1.png", 7, "Offer detail with the booking form. A member cannot "
         "see this form on their own offer.")
    SHOT(doc, "TC_ses-03_1.png", 8, "Session management. The teacher accepts, declines or "
         "completes a request from here; completion is what moves the credit.")
    SHOT(doc, "TC_adm-01_2.png", 9, "Administrator dashboard, reachable only with the "
         "administrator role.")
    SHOT(doc, "TC_adm-04_1.png", 10, "Manage skills. The catalogue every offer must "
         "reference.")

    P(doc, "The table below traces each interface to the requirement it serves and the "
           "cases that exercise it.")'''

if t.count(OLD) != 1:
    sys.exit(f"ABORT: 5.3 header matched {t.count(OLD)} times")
t = t.replace(OLD, NEW, 1)
print("  5.3 now draws the interface: 2 diagrams + 8 screenshots")

# ---------------------------------------------------------------- FIG / SHOT helpers
HELPERS = '''
def FIG(doc, name, number, caption, width=6.3):
    """A drawn figure, numbered and captioned."""
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        print(f"  MISSING FIGURE: {name}", file=sys.stderr)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Inches(width))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(10)
    r = c.add_run(f"Figure {number}. ")
    r.bold = True; r.font.size = Pt(9); r.font.name = FONT; r.font.color.rgb = NAVY
    r = c.add_run(caption); r.font.size = Pt(9); r.font.name = FONT


def SHOT(doc, name, number, caption, width=4.6):
    """A screenshot captured during test execution."""
    path = os.path.join(SHOTS_DIR, name)
    if not os.path.exists(path):
        print(f"  MISSING SCREENSHOT: {name}", file=sys.stderr)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Inches(width))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(9)
    r = c.add_run(f"Figure {number}. ")
    r.bold = True; r.font.size = Pt(9); r.font.name = FONT; r.font.color.rgb = NAVY
    r = c.add_run(caption); r.font.size = Pt(9); r.font.name = FONT


'''
anchor = "def cover(doc):"
if t.count(anchor) != 1:
    sys.exit("ABORT: cover() not found")
t = t.replace(anchor, HELPERS.lstrip("\n") + anchor, 1)
t = t.replace('SHOTS = r"F:\\outputs\\sqat-skillbank\\screenshots"\n', "", 1)
t = t.replace('OUT = os.path.join(ROOT, "SkillBank_Software_Test_Plan.docx")',
              'OUT = os.path.join(ROOT, "SkillBank_Software_Test_Plan.docx")\n'
              'SHOTS_DIR = r"F:\\outputs\\sqat-skillbank\\screenshots"', 1)
print("  added FIG and SHOT helpers")

# ---------------------------------------------------------------- preconditions
PRE = {
    "FR-01": "the visitor is not signed in and the email is not already registered",
    "FR-02": "the account exists and is not blocked",
    "FR-03": "the requester holds a session; the role is read from it, not from the request",
    "FR-04": "the requester holds an administrator session",
    "FR-05": "the member is signed in and, for edit or delete, owns the offer",
    "FR-06": "none; the browse and search pages are public",
    "FR-07": "both parties are registered members and the offer is active and not the "
             "requester's own",
    "FR-08": "the session is accepted, not already completed, and the learner holds at "
             "least one credit",
    "FR-09": "the session is completed, the reviewer is its learner, and no review exists",
    "FR-10": "the member is signed in and the skill is in the catalogue",
}
old_loop = '''        r = p.add_run(f"{fid}  {name}  [{pri}]  ")
        r.bold = True; r.font.size = Pt(10.5); r.font.name = FONT; r.font.color.rgb = NAVY
        r = p.add_run(text); r.font.size = Pt(10.5); r.font.name = FONT'''
new_loop = '''        r = p.add_run(f"{fid}  {name}  ")
        r.bold = True; r.font.size = Pt(10.5); r.font.name = FONT; r.font.color.rgb = NAVY
        r = p.add_run(text); r.font.size = Pt(10.5); r.font.name = FONT
        pc = doc.add_paragraph()
        pc.paragraph_format.space_after = Pt(7)
        pc.paragraph_format.left_indent = Inches(0.22)
        r = pc.add_run("Priority Level: "); r.bold = True
        r.font.size = Pt(9.5); r.font.name = FONT
        r = pc.add_run(pri); r.font.size = Pt(9.5); r.font.name = FONT
        r = pc.add_run("     Precondition: "); r.bold = True
        r.font.size = Pt(9.5); r.font.name = FONT
        r = pc.add_run(PRECONDITIONS.get(fid, "none"))
        r.font.size = Pt(9.5); r.font.name = FONT'''
if t.count(old_loop) != 1:
    sys.exit(f"ABORT: FR loop matched {t.count(old_loop)} times")
t = t.replace(old_loop, new_loop, 1)
t = t.replace("QUALITY = [",
              "PRECONDITIONS = " + repr(PRE) + "\n\nQUALITY = [", 1)
print("  every functional requirement now carries Priority Level and Precondition")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("\ninterface section rebuilt")
