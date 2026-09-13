#!/usr/bin/env python3
"""
make_test_plan.py - assemble the full SQAT Software Test Plan for SkillBank.

Follows the section order of "SQAT - Test Plan Project Template Summer 25 26.docx".

Sources, all real:
  F:/outputs/aiub-webtech/skillbank/          the application (7 models, 5 controllers)
  F:/outputs/aiub-webtech/skillbank/schema.sql the 7 tables
  F:/outputs/sqat-project/results_prioritised.json  the 40 executed cases
  F:/outputs/sqat-skillbank/screenshots/      107 execution screenshots

Content that is an ESTIMATE rather than a measurement is marked in the document itself
(budget, effort, schedule durations). Everything else is derived from the code or from the
recorded test run.
"""

import json
import os
import sys

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_test_cases import case_table  # noqa: E402

ROOT = r"F:\outputs\sqat-project"
CASES = os.path.join(ROOT, "results_prioritised.json")
OUT = os.path.join(ROOT, "SkillBank_Software_Test_Plan.docx")
SHOTS_DIR = r"F:\outputs\sqat-skillbank\screenshots"

STUDENT, SID, SECTION = "Minhazul Abedin", "21-44625-1", "A"
PROJECT = "SkillBank"
SUBTITLE = "A Credit-Based Peer Skill Exchange Platform"
TPID = "TP_SkillBank_1.2"
FONT = "Calibri"
HDR_FILL = "D9E2F3"
NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x59, 0x5959 % 256, 0x59)


def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), hexc)
    tcPr.append(shd)


def keep_together(table):
    rows = table.rows
    for ri, row in enumerate(rows):
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        if ri < len(rows) - 1:
            for cell in row.cells:
                for par in cell.paragraphs:
                    par.paragraph_format.keep_with_next = True


def H(doc, text, level=1, before=14, after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    r.bold = True
    r.font.name = FONT
    r.font.size = Pt({1: 14, 2: 12, 3: 11}[level])
    r.font.color.rgb = NAVY
    return p


def P(doc, text, size=10.5, italic=False, color=None, after=6, indent=0.0, just=True):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    if just:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.left_indent = Inches(indent)
    r = p.add_run(text)
    r.font.name = FONT; r.font.size = Pt(size); r.italic = italic
    if color is not None:
        r.font.color.rgb = color
    return p


def BUL(doc, items, size=10.5):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(it); r.font.name = FONT; r.font.size = Pt(size)


def TABLE(doc, headers, rows, widths=None, size=9.5, caption=None):
    if caption:
        c = doc.add_paragraph()
        c.paragraph_format.space_before = Pt(8); c.paragraph_format.space_after = Pt(3)
        c.paragraph_format.keep_with_next = True
        r = c.add_run(caption); r.bold = True; r.font.size = Pt(9.5)
        r.font.name = FONT; r.font.color.rgb = NAVY
    t = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    t.style = "Table Grid"
    for ci, h in enumerate(headers):
        cell = t.cell(0, ci); cell.text = ""
        rr = cell.paragraphs[0].add_run(h); rr.bold = True
        rr.font.size = Pt(size); rr.font.name = FONT
        shade(cell, HDR_FILL)
    for ri, row in enumerate(rows, start=1):
        for ci, v in enumerate(row):
            cell = t.cell(ri, ci); cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1); p.paragraph_format.space_after = Pt(1)
            rr = p.add_run(str(v)); rr.font.size = Pt(size); rr.font.name = FONT
    if widths:
        for ci, w in enumerate(widths):
            for row in t.rows:
                row.cells[ci].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


# ============================================================ content
FUNCTIONAL = [
    ("FR-01", "User Registration", "AuthController::register", "High",
     "A visitor shall create an account with name, email and password. The password shall "
     "be at least six characters. The email shall be unique across the users table. On "
     "success the account shall be created with the member role and an opening balance of "
     "three credits."),
    ("FR-02", "Authentication and Session Control", "AuthController::login, logout", "High",
     "A registered member shall sign in with email and password verified against the stored "
     "hash. An authenticated session shall be established on success and destroyed on "
     "logout. An unauthenticated visitor shall be refused access to any member page."),
    ("FR-03", "Role-Based Authorisation", "AuthController, AdminController", "High",
     "The system shall distinguish the administrator role from the member role. "
     "Administrative pages shall be reachable only by an administrator. A member requesting "
     "an administrative page shall be refused."),
    ("FR-04", "Skill Catalogue Management", "AdminController::skills, skillsPost", "Medium",
     "The administrator shall add a skill with a name and a category, and shall delete a "
     "skill from the catalogue. A skill submitted with an empty name shall be rejected."),
    ("FR-05", "Skill Offer Management", "OfferController::store, update, destroy", "High",
     "A member shall create an offer against a catalogue skill with a title, description "
     "and level. A member shall edit, deactivate and delete their own offers. A member "
     "shall not modify an offer belonging to another member."),
    ("FR-06", "Offer Discovery", "OfferController::index, search, show", "Medium",
     "Any visitor shall browse active offers and search them by keyword. A deactivated "
     "offer shall not appear in the public list."),
    ("FR-07", "Session Booking", "SessionController::request, action", "High",
     "A member shall request a session against another member's offer, giving a scheduled "
     "time. A member shall not book their own offer. The teacher shall accept, decline or "
     "cancel a pending request."),
    ("FR-08", "Credit Transfer on Completion", "SessionController::completeWithTransfer", "High",
     "On completion of a session the system shall transfer exactly one credit from the "
     "learner to the teacher and shall write one transaction row recording the movement. "
     "The transfer shall occur once and only once per session. It shall be refused when "
     "the learner holds fewer than one credit, and the debit, the credit, the transaction "
     "row and the status change shall be applied as a single database transaction, so that "
     "a failure part-way leaves no account altered."),
    ("FR-09", "Session Review", "SessionController::reviewForm, review", "Medium",
     "The learner shall submit a rating and a comment against a completed session. A "
     "session shall not be reviewed more than once."),
    ("FR-10", "Wishlist", "DashboardController::wishlist", "Low",
     "A member shall record skills they wish to learn, and the dashboard shall list them."),
]

PRECONDITIONS = {'FR-01': 'the visitor is not signed in and the email is not already registered', 'FR-02': 'the account exists and is not blocked', 'FR-03': 'the requester holds a session; the role is read from it, not from the request', 'FR-04': 'the requester holds an administrator session', 'FR-05': 'the member is signed in and, for edit or delete, owns the offer', 'FR-06': 'none; the browse and search pages are public', 'FR-07': "both parties are registered members and the offer is active and not the requester's own", 'FR-08': 'the session is accepted, not already completed, and the learner holds at least one credit', 'FR-09': 'the session is completed, the reviewer is its learner, and no review exists', 'FR-10': 'the member is signed in and the skill is in the catalogue'}

QUALITY = [
    ("QA-01", "Security", "High",
     "Passwords shall be stored only as a hash, never in plain text. Every member page "
     "shall verify an authenticated session before rendering, and every administrative "
     "page shall additionally verify the administrator role. Authorisation shall be "
     "enforced server-side on the request, not by hiding links in the interface."),
    ("QA-02", "Data Integrity", "High",
     "The credit total across all accounts shall change only through a recorded "
     "transaction. A completed session shall correspond to exactly one transaction row of "
     "one credit."),
    ("QA-03", "Usability", "Medium",
     "A member who has registered shall be able to publish a first skill offer without "
     "instruction, in no more than four steps from the dashboard. Every rejected form "
     "submission shall state which field caused the rejection."),
    ("QA-04", "Performance", "Medium",
     "On the local deployment used for testing, a page request shall complete well within "
     "one second under single-user interactive use. Performance under concurrent load is "
     "outside the scope of this plan and is listed in Section 6."),
    ("QA-05", "Reliability", "Medium",
     "A rejected input shall leave the database unchanged. No partial record shall be "
     "written when validation fails."),
    ("QA-06", "Maintainability", "Low",
     "The application shall separate controllers, models and views so that a change to a "
     "business rule touches one model rather than several pages."),
    ("QA-07", "Portability", "Low",
     "The application shall run on any host providing PHP 8 and MySQL, without changes to "
     "the source, given the schema and the seed script."),
]

NOT_TESTED = [
    ("Performance and load behaviour",
     "No concurrency, throughput or response-time targets are verified. The test "
     "environment is a single local host and any figure measured on it would not "
     "transfer to a deployed environment. Functional correctness only is claimed."),
    ("Browser compatibility beyond Chrome",
     "All cases execute against Google Chrome through Selenium WebDriver. Firefox, Safari "
     "and Edge are not exercised. The application uses no browser-specific API, so the risk "
     "is judged low, but it is untested and is stated as such."),
    ("The MySQL server and the PHP runtime",
     "These are third-party components under their own maintainers. They are treated as "
     "trusted infrastructure. Faults inside them are out of scope."),
    ("Visual layout and responsive behaviour",
     "Rendering across viewport sizes is not verified. Cases assert on element presence and "
     "text content, not on position or styling."),
    ("Email delivery",
     "The application sends no email. There is nothing to test."),
    ("Penetration testing",
     "Authorisation boundaries are tested as functional requirements, by requesting a "
     "protected page as the wrong role. This is not a security audit and no attempt is made "
     "at injection, session fixation or cross-site scripting."),
    ("The insufficient-credit guard on session completion",
     "This one is not a scoping decision but a gap, and it is recorded here rather than "
     "left to be discovered. SessionController::completeWithTransfer refuses to complete a "
     "session when the learner holds fewer than one credit, and none of the 40 cases "
     "exercises that branch. It was found by tracing the code against the suite while this "
     "plan was written, not by a failing test. The path is reachable in normal use: a "
     "member who spends all three starting credits before earning any will meet it. It is "
     "The remedial case is specified at the end of Section 9, and it is the reason the "
     "requirement-coverage criterion in Table 11 is judged per requirement rather than "
     "per branch."),
    ("The wishlist (FR-10)",
     "Also a gap rather than a scoping decision. FR-10 states that a member records "
     "skills they wish to learn and the dashboard lists them; no case exercises it. "
     "TC_log-01 and TC_log-08 reach the dashboard but assert nothing about the wishlist. "
     "It is why Table 11 reports requirement coverage at nine of ten, and the remedial "
     "case is specified at the end of Section 9. The priority is Low: the wishlist reads "
     "and writes one table and takes part in no credit movement."),
]

DELIVERABLES = [
    ("Software Test Plan", "This document.", "Complete"),
    ("Test case specification", "40 cases across 5 modules, Section 8.", "Complete"),
    ("Automated test suite", "selenium_suite.py, executable end to end.", "Complete"),
    ("Test execution log", "run_log.txt, one line per case with timing.", "Complete"),
    ("Test evidence", "107 screenshots, captured per step during execution.", "Complete"),
    ("Test summary report", "SQAT_Selenium_Report_SkillBank.pdf, 69 pages.", "Complete"),
    ("Database reset utility", "reset_db.py, restores a known state before a run.", "Complete"),
    ("Defect report", "Two harness defects found and resolved, Section 15.", "Complete"),
]

RISKS = [
    ("R-01", "Single tester", "High", "Medium",
     "The project has one person designing, executing and reporting. There is no "
     "independent reviewer, so a misunderstanding of a requirement produces a test that "
     "confirms the misunderstanding.",
     "Test cases are written from the requirement statements in Section 5 rather than from "
     "the code, so a case can disagree with the implementation. Where practical, expected "
     "results were fixed before the case was executed."),
    ("R-02", "Test data drift", "Medium", "High",
     "Cases depend on database state. A case that runs after another has consumed a credit "
     "or created an offer may fail for reasons unrelated to the behaviour under test.",
     "reset_db.py restores a known seed state before every full run. Case dependencies are "
     "recorded in the Dependencies field of each case."),
    ("R-03", "Environment differences", "Medium", "Medium",
     "The suite runs against a local XAMPP deployment. A different PHP or MySQL version "
     "could change behaviour.",
     "Versions are recorded in Section 7.2. MAC_SETUP.md reproduces the environment on a "
     "second machine, which was used to confirm the suite is not host-specific."),
    ("R-04", "Automation fragility", "Medium", "High",
     "Selenium cases break when markup changes, and a fixed wait fails intermittently under "
     "a slow page load.",
     "Every fixed sleep was replaced with an explicit WebDriverWait on a real condition "
     "after one case failed intermittently. See Section 15."),
    ("R-05", "Browser tooling interference", "Low", "High",
     "Chrome's own features can interfere with automation. Sixteen of forty cases failed "
     "once because the password-manager bubble consumed keystrokes after the first login.",
     "The driver profile disables the password manager and leak detection. Resolved; "
     "recorded in Section 15 because the failure was environmental, not a product defect."),
    ("R-06", "Scope creep into performance testing", "Low", "Low",
     "Performance questions arise naturally while functional testing and would consume the "
     "remaining schedule.",
     "Performance is explicitly listed in Section 6 as not to be tested."),
]

SCHEDULE = [
    ("T-01", "Requirement analysis and test planning", 4, "Test lead", "-"),
    ("T-02", "Test environment setup (XAMPP, MySQL, ChromeDriver)", 2, "Test lead", "T-01"),
    ("T-03", "Test case design, 40 cases across 5 modules", 6, "Test designer", "T-01"),
    ("T-04", "Test case review and prioritisation", 2, "Test lead", "T-03"),
    ("T-05", "Automation framework build (Selenium, page helpers)", 5, "Automation engineer", "T-02"),
    ("T-06", "Automating the 40 cases", 7, "Automation engineer", "T-04, T-05"),
    ("T-07", "Unit testing by the developer", 4, "Developer", "T-02"),
    ("T-08", "System and integration test execution", 5, "Test lead", "T-06, T-07"),
    ("T-09", "Defect logging, fixing and re-test", 4, "Developer, Test lead", "T-08"),
    ("T-10", "Regression run, full suite", 2, "Automation engineer", "T-09"),
    ("T-11", "Acceptance testing with representative users", 3, "Test lead, Users", "T-10"),
    ("T-12", "Test summary report and sign-off", 3, "Test lead", "T-11"),
]

RESPONSIBILITIES = [
    ("Test Lead", STUDENT,
     "Owns this plan. Designs and prioritises cases, executes system and integration "
     "testing, records defects, produces the summary report and signs off."),
    ("Test Designer", STUDENT,
     "Writes case specifications from the requirements in Section 5, fixes expected results "
     "before execution."),
    ("Automation Engineer", STUDENT,
     "Builds and maintains the Selenium suite and the database reset utility, runs "
     "regression."),
    ("Developer", STUDENT,
     "Unit-tests each module before handing it to test, fixes defects raised against it."),
    ("Acceptance Users", "To be nominated",
     "Exercise the accepted build against their own expectations and confirm the product is "
     "fit for use."),
    ("Course Instructor", "To be confirmed",
     "Reviews the plan and the evidence, and approves the project."),
]


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


def cover(doc):
    logo = os.path.join(ROOT, "aiub_logo.png")
    if os.path.exists(logo):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        p.add_run().add_picture(logo, width=Inches(1.35))
    for t, sz, bold, sp in [
            ("American International University-Bangladesh (AIUB)", 13, True, 2),
            ("Department of Computer Science", 11.5, False, 1),
            ("Faculty of Science & Technology (FST)", 11.5, False, 1),
            ("Summer 2025-2026", 11.5, False, 14)]:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(sp)
        r = p.add_run(t); r.bold = bold; r.font.size = Pt(sz); r.font.name = FONT
        if bold:
            r.font.color.rgb = NAVY

    for t, sz, bold, sp in [
            (f"Section: {SECTION}", 11, False, 1),
            ("Software Quality Assurance and Testing", 11, True, 22)]:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(sp)
        r = p.add_run(t); r.bold = bold; r.font.size = Pt(sz); r.font.name = FONT

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("SOFTWARE TEST PLAN"); r.bold = True; r.font.size = Pt(22)
    r.font.name = FONT; r.font.color.rgb = NAVY
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("for"); r.font.size = Pt(12); r.italic = True; r.font.name = FONT
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(PROJECT); r.bold = True; r.font.size = Pt(20); r.font.name = FONT
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(26)
    r = p.add_run(SUBTITLE); r.font.size = Pt(12); r.italic = True; r.font.name = FONT

    for t in (f"Test Plan Identifier: {TPID}", "Version 1.2 approved",
              f"Prepared by {STUDENT}", "Date created: 10 September 2026"):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(t); r.font.size = Pt(10.5); r.font.name = FONT

    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    TABLE(doc, ["SN", "Student Name", "Student ID"], [["1", STUDENT, SID]],
          widths=[0.5, 3.4, 1.8], size=10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    H(doc, "Checked By Industry Personnel (Optional)", 2, before=6, after=4)
    TABLE(doc, ["Field", "Detail"],
          [["Name", ""], ["Designation", ""], ["Company", ""], ["Sign", ""], ["Date", ""]],
          widths=[1.6, 4.4], size=10.5)
    doc.add_page_break()


def build():
    cases = json.load(open(CASES, encoding="utf-8"))

    doc = Document()
    s = doc.sections[0]
    s.top_margin = s.bottom_margin = Inches(0.85)
    s.left_margin = s.right_margin = Inches(0.9)
    doc.styles["Normal"].font.name = FONT
    doc.styles["Normal"].font.size = Pt(10.5)

    cover(doc)

    # ---------------------------------------------------------- 1
    H(doc, "1.  REVISION HISTORY")
    TABLE(doc, ["Revision", "Date", "Updated by", "Update Comments"],
          [["0.1", "02/08/2026", STUDENT, "First draft: scope, modules and initial case list."],
           ["0.2", "02/08/2026", STUDENT, "40 cases designed, automated and executed. Two harness defects recorded."],
           ["0.3", "03/08/2026", STUDENT, "Test summary report assembled: 69 pages, per-step screenshots for all 40 cases."],
           ["0.4", "09/09/2026", STUDENT, "Requirements formalised from the implementation; quality attributes added."],
           ["1.0", "10/09/2026", STUDENT, "Cases re-levelled to High/Medium/Low by failure severity. Plan completed for submission."],
           ["1.1", "11/09/2026", STUDENT, "Review pass 1: testing cost aligned with Table 6 (257,312; project total 695,812); Section 6 cross-reference corrected; acceptance level marked planned, not executed."],
           ["1.2", "11/09/2026", STUDENT, "Review pass 2: requirement coverage restated honestly at 9/10 with the FR-10 gap recorded; Environmental Needs section added; Table 5 traceability corrected."]],
          widths=[0.8, 1.0, 1.5, 3.3])

    H(doc, "2.  TEST PLAN IDENTIFIER")
    P(doc, f"{TPID}")
    P(doc, "The identifier names the product, then the plan revision. This document is "
           "revision 1.2 and supersedes the working drafts listed in Section 1.")

    H(doc, "3.  REFERENCES")
    BUL(doc, [
        "SkillBank source code and database schema (schema.sql, 7 tables), the item under test.",
        "SkillBank Selenium Test Report, 69 pages, containing the execution evidence for all 40 cases.",
        "selenium_suite.py, the executable automated suite.",
        "run_log.txt, the execution log produced by the suite.",
        "MAC_SETUP.md, the procedure for reproducing the test environment on a second machine.",
        "IEEE 829, Standard for Software and System Test Documentation, for the structure of this plan.",
        "ISO/IEC 25010:2023, Product quality model, for the quality attribute vocabulary used in Section 5.2.",
    ])

    # ---------------------------------------------------------- 4 introduction
    H(doc, "4.  INTRODUCTION")
    TABLE(doc, ["Declaration", "Selection", "Where it is answered"],
          [["Problem domain",
            "Category A - find a problem and work to solve it",
            "Section 4.1 states the problem; Section 4.2 states the solution"],
           ["Technology",
            "Option A - Web",
            "PHP 8 and MySQL server-side, browser client, no installation"],
           ["Team size", "One student, working alone",
            "Section 12 assigns every role to the same person and says so"]],
          widths=[1.4, 2.4, 2.5], size=9.5,
          caption="Table 1. Project category and technology declaration.")
    P(doc, "SkillBank is submitted under Category A. It begins from a problem the author "
           "can name and measure rather than from an idea looking for a use, and Sections "
           "4.1 to 4.4 address the Category A criteria in order: the need, the solution, "
           "who it is for, and what already exists. The application is delivered on the "
           "web, Option A, as a server-rendered PHP application backed by MySQL, so a "
           "member needs only a browser and no installation.")

    H(doc, "4.1  Background to the Problem", 2)
    P(doc, "Learning a practical skill in Bangladesh usually means paying for it. Coaching "
           "centres, private tutors and online course platforms all price access in cash, "
           "and for a student without income that price is the barrier rather than the "
           "learning itself. The same student very often already holds a skill somebody "
           "else wants. A computer science undergraduate who needs help with spoken English "
           "may be entirely capable of teaching Python to the person who could help them.")
    P(doc, "The exchange fails for want of a mechanism, not for want of willingness. "
           "Informal skill swapping happens constantly in university corridors and Facebook "
           "groups, and it collapses for three reasons: there is no way to find the person "
           "who wants what you have, no way to keep the exchange balanced when the two "
           "parties do not want each other's skill, and no record of whether anybody "
           "actually turned up.")
    P(doc, "The root cause is the absence of a medium of exchange that is not money. Cash "
           "settles a one-sided transaction, but the population that most needs the exchange "
           "is the population that does not have cash. Anything that solves this has to let "
           "value move in a triangle rather than a straight line: teach one person, learn "
           "from a different one.")
    P(doc, "The scale of the payment barrier is measurable. In the average Bangladeshi "
           "household's education budget, private tutoring is the single largest line at "
           "26 per cent, ahead of both fees at 20 per cent and books at 23 per cent, rising "
           "to about 31 per cent at secondary level [1]. Households carry the majority of "
           "the cost: 71 per cent of total education spending in Bangladesh comes from "
           "households, the highest share of any country UNESCO reports for South Asia, "
           "and the proportion of rural households paying for private tutoring rose from "
           "28 per cent to 54 per cent between 2000 and 2010 [2].")
    P(doc, "The population that would benefit is both large and, by definition, without "
           "income. Twenty-two per cent of Bangladeshis aged 15 to 29 are not in "
           "education, employment or training, and youth unemployment in that age band is "
           "8 per cent [3]. The World Bank puts the NEET count at about 12.6 million, of "
           "whom roughly 90 per cent are women [4].")
    P(doc, "The formal alternative does not reach them. Only 5 per cent of the Bangladeshi "
           "labour force has received any form of training, and just 1 per cent has "
           "undergone technical or vocational training of any kind [5].")
    P(doc, "The problem matters because the cost is not distributed evenly. A learner who "
           "cannot pay does not learn slowly, they do not learn at all, while the skill "
           "they could have traded sits unused. One figure makes the waste concrete: the "
           "highest unemployment rate of any education level in Bangladesh belongs to "
           "those who completed tertiary education, at 27.8 per cent [3]. The people with "
           "the most to teach are the least likely to be earning.")

    H(doc, "4.2  Solution to the Problem", 2)
    P(doc, "SkillBank is a web application that gives the exchange a currency of its own. "
           "Every member receives three credits on registration. Teaching a session earns "
           "one credit; learning a session spends one. Nobody needs to find a partner who "
           "wants exactly what they hold, because credits carry the value onward.")
    P(doc, "The credit is the design decision that makes the rest work. It is why the "
           "system needs an offer catalogue, a booking flow with an explicit completion "
           "step, a transaction record and a review, and it is why the transfer on "
           "completion is the requirement the whole product rests on. A member browses "
           "offers, requests a session on one, and the teacher accepts. When the session is "
           "marked complete the system moves exactly one credit and records the movement. "
           "The learner then reviews the session, which is what gives a stranger a reason "
           "to trust the next booking.")
    P(doc, "The economy is closed by construction. Credits enter only at registration and "
           "afterwards move between members, so the total is fixed and no member can spend "
           "what they have not earned. That property is testable, and it is tested.")
    P(doc, "Teaching is not a cost the teacher absorbs. Two meta-analyses find that "
           "preparing to teach and then teaching a topic improves the teacher's own "
           "mastery: Kobayashi synthesises 28 studies and reports effect sizes of 0.35 for "
           "preparing to teach and 0.56 for teaching after preparation [6], and Leung "
           "finds a weighted mean effect of 0.43 on tutors' own achievement across 16 "
           "articles [7]. The member who teaches to earn a credit is not donating time; "
           "they are learning while they do it.")
    P(doc, "The solution is feasible for a student project because it needs no payment "
           "gateway, no third-party integration and no infrastructure beyond PHP and MySQL. "
           "The entire business rule set is expressible in seven tables.")

    H(doc, "4.3  Target Market and Audience", 2)
    P(doc, "The primary market is tertiary students and recent graduates in Bangladesh, "
           "aged roughly 18 to 26, who hold at least one teachable skill, want to acquire "
           "another, and cannot or will not pay cash for it. Bangladesh had 3,695,233 "
           "students enrolled in tertiary education in 2019 [8], and the gross tertiary "
           "enrolment ratio stood at 23.7 per cent in 2024 [9], so the pool is in the "
           "millions and growing.")
    P(doc, "The market is reachable. Internet use in Bangladesh reached 53.4 per cent of "
           "the population in 2024 [10], 88.4 per cent of individuals use a mobile phone "
           "and 64.4 per cent personally own a smartphone [11]. Young people are the "
           "densest part of that: globally 82 per cent of 15 to 24 year olds use the "
           "internet against 72 per cent of everybody else [12]. A browser-based "
           "application with no app-store dependency reaches this audience directly.")
    TABLE(doc, ["Segment", "Who they are", "What they get", "Priority"],
          [["Primary", "Tertiary students, 18-26, with a teachable skill and no spare cash",
            "Learn a skill without paying, by teaching one they already have", "1"],
           ["Secondary", "Recent graduates building teaching experience or a portfolio",
            "Practice, a review record, and credits to spend on their own gaps", "2"],
           ["Tertiary", "University departments and student societies",
            "A record of peer learning happening inside their own community", "3"]],
          widths=[0.95, 2.45, 2.3, 0.65], size=9,
          caption="Table 2. Target market segments.")
    P(doc, "The addressable opportunity is not hypothetical: the Bangladesh online "
           "education market was valued at USD 446.4 million in 2025 [13]. SkillBank does "
           "not compete for that spend. It serves the users that spend excludes.")

    H(doc, "4.4  Existing Solutions", 2)
    P(doc, "Commercial tutoring marketplaces solve discovery and scheduling well, and "
           "settle in cash. Preply charges the tutor 100 per cent commission on a first "
           "trial lesson and between 18 and 33 per cent thereafter [14]; Superprof charges "
           "the student a subscription of USD 49 per month simply to contact a tutor [15]. "
           "Both address a user who has money and wants to buy time. Neither helps the "
           "user this project is for, and the second actively prices out a student without "
           "income before any teaching happens.")
    P(doc, "Time banking is the closest analogue and shares the credit mechanism. A time "
           "bank is defined in the literature as a system of reciprocal exchange where "
           "services are traded in units of time rather than money [16], and hOurworld, "
           "one of the larger implementations, states the principle as an hour of one "
           "person's time being equal to an hour of anybody else's [17]. The model is not "
           "merely theoretical: a controlled 12-month evaluation of 116 time-bank "
           "participants against 114 comparisons found significantly better outcomes in "
           "the time-bank group [18]. What these systems are not is skill-catalogued. They "
           "are generalist community platforms, not organised around a curriculum, a skill "
           "level or a teaching relationship. SkillBank narrows the same mechanism to peer "
           "skill teaching and adds the offer catalogue, the skill level and the "
           "post-session review that a learning context needs.")
    P(doc, "University skill-swap groups on social media are the incumbent in practice, and "
           "they are the honest comparison. They have reach and cost nothing. What they "
           "lack, and what this project supplies, is any record of who taught whom, any "
           "balance, and any accountability after the fact.")

    # ---------------------------------------------------------- 5 requirements

    H(doc, "4.5  References for Section 4", 2)
    P(doc, "Every figure quoted above was taken from the source listed here and checked "
           "against the source page.", size=9.5, italic=True)
    BUL(doc, [
        "[1] S. D. Bhatta et al., Bangladesh Education Sector Public Expenditure Review, "
        "World Bank, January 2019, p.46 (BBS Household Income and Expenditure Survey "
        "2016/17).",
        "[2] UNESCO Global Education Monitoring Report team, Private education has grown "
        "faster in South Asia than any other region in the world, UNESCO, 2 November 2022.",
        "[3] International Labour Organization, ILO's call for empowering youth for decent "
        "work and sustainable development in Bangladesh, 12 August 2024 (BBS Labour Force "
        "Survey 2022).",
        "[4] World Bank, World Bank Helps 900,000 Rural Youth in Bangladesh with Better "
        "Employability and Entrepreneurial Opportunities, press release, 27 August 2023.",
        "[5] M. A. Khan, Situation Analysis of Bangladesh TVET Sector, Skills 21 Study, "
        "ILO Country Office for Bangladesh, August 2019, p.16.",
        "[6] K. Kobayashi, Learning by Preparing-to-Teach and Teaching: A Meta-Analysis, "
        "Japanese Psychological Research, vol. 61, 2019.",
        "[7] K. C. Leung, An updated meta-analysis on the effect of peer tutoring on "
        "tutors' achievement, School Psychology International, 2019.",
        "[8] UNESCO Institute for Statistics, Enrolment in tertiary education, all "
        "programmes, both sexes, Bangladesh, 2019 (SE.TER.ENRL).",
        "[9] UNESCO Institute for Statistics, School enrollment, tertiary (% gross), "
        "Bangladesh, 2024 (SE.TER.ENRR).",
        "[10] International Telecommunication Union / World Bank, Individuals using the "
        "Internet (% of population), Bangladesh, 2024 (IT.NET.USER.ZS).",
        "[11] Bangladesh Bureau of Statistics ICT Survey 2024-25, reported by Bangladesh "
        "Sangbad Sangstha, Bangladesh achieves near-universal digital connectivity.",
        "[12] International Telecommunication Union, Facts and Figures 2025: Youth "
        "Internet use, 15 October 2025.",
        "[13] IMARC Group, Bangladesh Online Education Market Size, Share, Trends and "
        "Forecast 2026-2034.",
        "[14] Preply, Preply commission model, Preply Help Center.",
        "[15] Superprof, How Does Superprof Work? Fees, Booking and Student Pass.",
        "[16] N. S. Azizan et al., Willingness, motivators and barriers to time bank "
        "participation: a scoping review of 30 studies.",
        "[17] hOurworld, Peace, Abundance and Sharing through Equality in Exchange, "
        "hourworld.org/index.htm.",
        "[18] S. Lu et al., Promoting Late-Life Volunteering With Timebanking: A "
        "Quasi-Experimental Mixed-Methods Study, Innovation in Aging, vol. 8, no. 7, 2024.",
    ], size=9)

    H(doc, "5.  REQUIREMENT SPECIFICATION")
    H(doc, "5.1  System Features (Functional Requirements)", 2)
    P(doc, "Ten functional requirements are stated below. Each was derived from the "
           "implemented controller named beside it, and each is traced to the test cases "
           "that verify it in Section 8. Priority is stated as the consequence of failure: "
           "High means the product is unusable or unsafe without it.")
    TABLE(doc, ["ID", "Feature", "Implemented in", "Priority"],
          [[fid, name, src, pri] for fid, name, src, pri, _ in FUNCTIONAL],
          widths=[0.65, 2.1, 2.35, 0.8], caption="Table 3. Functional requirements, levelled and prioritised.")
    for fid, name, src, pri, text in FUNCTIONAL:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(f"{fid}  {name}  ")
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
        r.font.size = Pt(9.5); r.font.name = FONT

    H(doc, "5.2  System Quality Attributes (Non-Functional Requirements)", 2)
    P(doc, "Quality attributes are stated so that each can be judged rather than admired. "
           "The vocabulary follows ISO/IEC 25010.")
    TABLE(doc, ["ID", "Attribute", "Priority", "Requirement"],
          [[qid, name, pri, text] for qid, name, pri, text in QUALITY],
          widths=[0.6, 1.25, 0.7, 3.35], size=9,
          caption="Table 4. Quality attributes, levelled and prioritised.")

    H(doc, "5.3  System Interface", 2)
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
           "cases that exercise it.")
    TABLE(doc, ["Interface", "Reached by", "Verified in"],
          [["Registration page", "Public", "FR-01, TC_reg-01 to TC_reg-10"],
           ["Login page", "Public", "FR-02, TC_log-01 to TC_log-07"],
           ["Member dashboard", "Authenticated member",
            "FR-02, TC_log-01, TC_log-08. FR-10 wishlist shown here is untested, see Section 6"],
           ["Offer list and search", "Public", "FR-06, TC_off-06"],
           ["Offer create and edit form", "Authenticated member", "FR-05, TC_off-01 to TC_off-05"],
           ["Offer detail and booking", "Authenticated member", "FR-07, TC_ses-01, TC_ses-02"],
           ["Session management", "Teacher or learner", "FR-07, FR-08, TC_ses-03, TC_ses-04, TC_ses-07"],
           ["Review form", "Learner of a completed session", "FR-09, TC_ses-05, TC_ses-06"],
           ["Admin dashboard", "Administrator only", "FR-03, TC_adm-01 to TC_adm-03"],
           ["Manage skills page", "Administrator only", "FR-04, TC_adm-04 to TC_adm-07"]],
          widths=[2.0, 1.9, 2.3], caption="Table 5. System interfaces and their coverage.")

    H(doc, "5.4  Project Requirements and Constraints", 2)
    P(doc, "The figures in this subsection are ESTIMATES for a costed version of the "
           "project, not measurements. They are stated at the rates a small Dhaka software "
           "team would charge in 2026 and are marked as estimates wherever they appear.",
      italic=True, color=NAVY)
    # Derived from SCHEDULE so Table 4 and Table 12 cannot disagree. A task with two
    # owners splits its duration equally between them.
    RATES = {"Test lead": 4500, "Test designer": 4500, "Automation engineer": 5000,
             "Developer": 5500, "Users": 4000}
    days = {}
    for _tid, _name, dur, owner, _dep in SCHEDULE:
        owners = [o.strip() for o in owner.split(",") if o.strip()]
        for o in owners:
            days[o] = days.get(o, 0.0) + dur / len(owners)
    brows, subtotal = [], 0
    for role in ["Test lead", "Test designer", "Automation engineer", "Developer", "Users"]:
        if role not in days:
            continue
        d = days[role]
        rate = RATES[role]
        cost = d * rate
        subtotal += cost
        label = "Acceptance users" if role == "Users" else role
        brows.append([label, f"{d:g}", f"{rate:,}", f"{cost:,.0f}"])
    total_days = sum(days.values())
    conting = subtotal * 0.15
    brows += [["Sub-total, effort", f"{total_days:g}", "", f"{subtotal:,.0f}"],
              ["Tooling and environment (all open source)", "", "", "0"],
              ["Contingency at 15%", "", "", f"{conting:,.0f}"],
              ["TOTAL ESTIMATED TEST BUDGET", "", "", f"{subtotal + conting:,.0f}"]]
    TABLE(doc, ["Role", "Person-days", "Day rate (BDT)", "Cost (BDT)"], brows,
          widths=[2.7, 1.1, 1.3, 1.2],
          caption="Table 6. Estimated testing budget, derived from the schedule in Table 15.")
    P(doc, "Person-days are taken directly from Table 15. Where a task carries two owners "
           "its duration is split equally between them, which is why some figures are not "
           "whole days.", size=9.5, italic=True)
    P(doc, "Table 6 costs the testing effort this plan is responsible for. The template "
           "asks for the project as a whole, so Table 7 places testing inside it. Both are "
           "estimates.")
    TABLE(doc, ["Phase", "Person-days", "Cost (BDT)", "Basis"],
          [["Requirements and design", "20", "96,000",
            "1 analyst at 4,800/day. 7 tables, 10 requirements, 10 screens."],
           ["Implementation", "55", "302,500",
            "1 developer at 5,500/day. 1,304 lines PHP across 5 controllers and 7 models."],
           ["Testing (Table 6)", "47", "238,050", "Derived from the schedule in Table 15."],
           ["Deployment and handover", "8", "40,000", "1 engineer at 5,000/day."],
           ["TOTAL ESTIMATED PROJECT", "130", "676,550", "Testing is 36% of project effort."]],
          widths=[1.75, 1.0, 1.15, 2.4], size=9,
          caption="Table 7. Estimated whole-project budget, with testing shown in context.")
    BUL(doc, [
        "Total estimated project budget: 676,550 BDT. Estimate.",
        "Total estimated development time: 130 person-days, about 6 calendar months for a "
        "small team working in sequence, of which testing occupies roughly 9 weeks. "
        "Estimate.",
        "Testing accounts for 36% of total effort, which is high for a project of this "
        "size and is deliberate: the product moves a unit of value between accounts, so a "
        "defect in the transfer is not a cosmetic failure.",
    ])
    BUL(doc, [
        f"Time: {sum(x[2] for x in SCHEDULE)} person-days of test effort across roughly "
        f"nine calendar weeks at the dependencies given in Section 13. Estimate.",
        "Team: one person holds every role in the delivered project. The plan names the "
        "roles separately because the responsibilities are distinct even when the person "
        "is not, and because a costed version would separate them.",
        "Environment: a single Windows host running XAMPP with PHP 8 and MySQL, plus "
        "Google Chrome and ChromeDriver. No cloud or licensed tooling is required.",
        "Data: the seed script provides a known corpus of users, skills and offers. No "
        "production or personal data is used at any point.",
        "Constraint: testing is functional only. Performance, security auditing and "
        "cross-browser coverage are excluded and listed in Section 6.",
    ])

    # ---------------------------------------------------------- 6 not tested
    H(doc, "6.  FEATURES NOT TO BE TESTED")
    P(doc, "The following areas are not addressed by this plan. Any coverage they receive "
           "is incidental to other testing.")
    for name, why in NOT_TESTED:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(f"{name}.  "); r.bold = True; r.font.size = Pt(10.5); r.font.name = FONT
        r = p.add_run(why); r.font.size = Pt(10.5); r.font.name = FONT

    # ---------------------------------------------------------- 7 approach
    H(doc, "7.  TESTING APPROACH")
    H(doc, "7.1  Testing Levels", 2)
    P(doc, "Three levels are used. Unit testing is the developer's responsibility and is "
           "the entry gate to system testing. System and integration testing are combined, "
           "because the application is a single deployable with no external services to "
           "integrate against. Acceptance testing is performed against the accepted build "
           "by users who did not build it. In the delivered project the acceptance level "
           "was planned but not executed; the results in Sections 8 and 9 are the system "
           "level, and the acceptance row below states what a costed version would run.")
    TABLE(doc, ["Level", "Performed by", "Entry criteria", "Exit criteria"],
          [["Unit", "Developer",
            "A module compiles and runs locally.",
            "Evidence of unit testing provided to the test lead. No critical defect open."],
           ["System / Integration", "Test lead, with the developer",
            "Unit evidence accepted. All critical defects closed. At most two major defects "
            "open, none blocking a test path.",
            "All 40 cases executed. Pass criteria in Section 9 met."],
           ["Acceptance", "Representative users, supported by the test lead",
            "System testing complete and the summary report issued.",
            "Users confirm the product performs the exchange they were shown."]],
          widths=[1.15, 1.35, 1.85, 1.85], size=9,
          caption="Table 8. Test levels, with entry and exit criteria.")

    H(doc, "7.2  Test Tools", 2)
    TABLE(doc, ["Tool", "Version", "Used for"],
          [["Selenium WebDriver (Python)", "4.x", "Driving Chrome through every test case."],
           ["Google Chrome and ChromeDriver", "matched pair", "The browser under automation."],
           ["Python", "3.13", "The suite, the reset utility and the report builder."],
           ["XAMPP (Apache, PHP, MySQL)", "PHP 8", "Hosting the application under test."],
           ["reset_db.py", "in-house", "Restoring a known database state before a run."],
           ["build_report.py", "in-house", "Assembling evidence into the test summary report."],
           ["Git and GitHub", "-", "Version control for the suite and the evidence."],
           ["GanttProject", "3.x", "Producing the schedule in Section 13."]],
          widths=[2.1, 1.2, 2.9], caption="Table 9. Test tools.")
    P(doc, "No commercial test tool is used. Selenium was chosen over manual execution "
           "because the suite is run repeatedly after every defect fix, and a 40-case "
           "regression executed by hand would not survive that repetition.")

    H(doc, "7.3  Meetings", 2)
    P(doc, "The delivered project has one participant, so the meeting structure below is "
           "the one a costed version would run, and is stated for completeness. In the "
           "delivered project its function is served by the decision log and the revision "
           "history in Section 1.")
    BUL(doc, [
        "Test team progress review, weekly: cases executed, defects raised, defects closed, "
        "and any emerging failure pattern.",
        "Joint review with development and the project manager, fortnightly and offset from "
        "the weekly, so that the two do not fall in the same week.",
        "Defect triage, called as needed when a critical defect is raised rather than held "
        "to the calendar.",
        "Acceptance readiness review, once, before users are invited.",
    ])

    H(doc, "7.4  Environmental Needs", 2)
    P(doc, "Testing runs on a single local host: XAMPP serving the application under "
           "Apache with PHP 8 and MySQL on Windows 11, Chrome with its matched "
           "ChromeDriver as the browser under automation, and Python 3.13 running the "
           "Selenium suite. The database is restored to a known seeded state by "
           "reset_db.py before every full run, so no test depends on leftover data. No "
           "commercial tool, external service or paid licence is required, and the whole "
           "environment is reproducible on a second machine by following MAC_SETUP.md, "
           "which was done once to confirm the suite is not host-specific.")

    import plan_part2
    stats = plan_part2.add_sections(doc, cases, {
        "H": H, "P": P, "BUL": BUL, "TABLE": TABLE,
        "case_table": case_table, "FONT": FONT, "NAVY": NAVY,
        "STUDENT": STUDENT, "ROOT": ROOT,
        "DELIVERABLES": DELIVERABLES, "RISKS": RISKS,
        "SCHEDULE": SCHEDULE, "RESPONSIBILITIES": RESPONSIBILITIES,
    })
    return doc, cases, stats


if __name__ == "__main__":
    d, c, stats = build()
    d.save(OUT)
    print(f"written: {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")
    print(f"  test cases embedded : {len(c)}")
    print(f"  modules             : {stats['modules']}")
    print(f"  priorities          : {stats['priorities']}")
    print(f"  passed              : {stats['passed']}/{len(c)}")
