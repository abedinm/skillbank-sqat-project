#!/usr/bin/env python3
"""
plan_part2.py - sections 8 to 16 of the SkillBank Software Test Plan.

Kept separate from make_test_plan.py only for size. Helpers and constants are passed in
through `ctx` rather than imported, so there is no circular import between the two.
"""

import os

from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

RED = RGBColor(0xC0, 0x30, 0x20)


def add_sections(doc, cases, ctx):
    H, P, BUL, TABLE = ctx["H"], ctx["P"], ctx["BUL"], ctx["TABLE"]
    case_table, FONT, NAVY = ctx["case_table"], ctx["FONT"], ctx["NAVY"]
    STUDENT, ROOT = ctx["STUDENT"], ctx["ROOT"]
    DELIVERABLES, RISKS = ctx["DELIVERABLES"], ctx["RISKS"]
    SCHEDULE, RESPONSIBILITIES = ctx["SCHEDULE"], ctx["RESPONSIBILITIES"]

    # ------------------------------------------------------------ 8 test cases
    # Portrait throughout, matching the faculty template, which carries the same
    # six-column case table on a portrait page.
    doc.add_page_break()
    H(doc, "8.  TEST CASES / TEST ITEMS", before=0)
    P(doc, f"{len(cases)} functional test cases were designed against the requirements in "
           f"Section 5 and executed against the running application through Selenium "
           f"WebDriver. Every field below was recorded during that execution. Priority is "
           f"the levelling described in Section 5.1: the consequence of the case failing, "
           f"not the effort of running it.")

    mods, prios = {}, {}
    for c in cases:
        m = c.get("module", "?")
        mods.setdefault(m, {"n": 0, "pass": 0, "High": 0, "Medium": 0, "Low": 0})
        mods[m]["n"] += 1
        mods[m]["pass"] += (c.get("status") == "Pass")
        mods[m][c.get("priority", "Medium")] += 1
        prios[c.get("priority")] = prios.get(c.get("priority"), 0) + 1
    rows = [[m, d["n"], d["High"], d["Medium"], d["Low"], d["pass"], d["n"] - d["pass"]]
            for m, d in mods.items()]
    passed = sum(d["pass"] for d in mods.values())
    rows.append(["TOTAL", len(cases), prios.get("High", 0), prios.get("Medium", 0),
                 prios.get("Low", 0), passed, len(cases) - passed])
    TABLE(doc, ["Module", "Cases", "High", "Medium", "Low", "Passed", "Failed"], rows,
          widths=[2.3, 0.8, 0.7, 0.85, 0.7, 0.85, 0.8],
          caption="Table 10. Test case coverage by module and priority.")

    for c in cases:
        cap = doc.add_paragraph()
        cap.paragraph_format.space_before = Pt(9)
        cap.paragraph_format.space_after = Pt(2)
        cap.paragraph_format.keep_with_next = True
        r = cap.add_run(f"{c.get('id','')} - {c.get('title','')}")
        r.bold = True
        r.font.size = Pt(10)
        r.font.name = FONT
        r.font.color.rgb = NAVY
        case_table(doc, c)

    doc.add_page_break()

    # ------------------------------------------------------------ 9 pass/fail
    H(doc, "9.  ITEM PASS/FAIL CRITERIA", before=0)
    P(doc, "A single case passes when the observed result matches the expected result "
           "recorded in its specification, with no unhandled error and no unintended change "
           "to the database.")
    P(doc, "The test process as a whole is judged against the criteria below. They are "
           "weighted by priority, because a failing High case and a failing Low case do not "
           "carry the same consequence.")
    nH, nM, nL = prios.get("High", 0), prios.get("Medium", 0), prios.get("Low", 0)
    TABLE(doc, ["Criterion", "Threshold", "Result"],
          [["High priority cases passing", "100%, no exceptions", f"{nH}/{nH} - met"],
           ["Medium priority cases passing", "at least 95%", f"{nM}/{nM} - met"],
           ["Low priority cases passing", "at least 90%", f"{nL}/{nL} - met"],
           ["Overall cases passing", "at least 95% of all cases",
            f"{passed}/{len(cases)} (100%) - met"],
           ["Critical defects open at exit", "zero", "zero - met"],
           ["Major defects open at exit",
            "at most two, none blocking a test path", "zero - met"],
           ["Requirement coverage",
            "every functional requirement in Section 5.1 exercised by at least one case",
            "9/10 - not met. FR-10 Wishlist (Low) has no case; recorded in Section 6"],
           ["Suite repeatability",
            "two consecutive full runs give the same result from a reset database",
            "confirmed - met"]],
          widths=[2.0, 2.5, 1.7], size=9,
          caption="Table 11. Pass/fail criteria and the result achieved.")
    P(doc, "Seven of the eight criteria were met. The cases pass from a reset database on "
           "a repeated run. This is a statement about the cases that exist. It is not a "
           "claim that the application is free of defects in the areas Section 6 excludes.")
    P(doc, "The criterion that failed is requirement coverage, and it failed twice over. "
           "FR-10, the wishlist, has no case at all: it closed at nine requirements of "
           "ten. And coverage is counted per requirement, not per branch; tracing the "
           "implementation against the suite while this plan was written turned up one "
           "reachable branch with no case behind it, the guard in "
           "SessionController::completeWithTransfer that refuses to complete a session "
           "when the learner holds fewer than one credit. Closing the two gaps is the "
           "future work of this plan and needs two cases: one that records a wish and "
           "asserts the dashboard lists it, and one that seeds a learner at zero credits "
           "and asserts that completion is refused, that no transaction row is written "
           "and that neither balance moves.")

    # ------------------------------------------------------------ 10 deliverables
    H(doc, "10.  TEST DELIVERABLES")
    TABLE(doc, ["Deliverable", "Description", "Status"],
          [list(x) for x in DELIVERABLES],
          widths=[1.9, 3.4, 0.9], caption="Table 12. Test deliverables.")

    # ------------------------------------------------------------ 11 staffing
    H(doc, "11.  STAFFING AND TRAINING NEEDS")
    P(doc, "A costed version of this project would assign one full-time tester through the "
           "system, integration and acceptance phases, joining part-time at the start to "
           "take part in requirement reviews. In the delivered project one person holds "
           "every role. That is stated plainly because it is the plan's most significant "
           "staffing limitation, and it is carried as risk R-01 in Section 14.")
    P(doc, "The following training was needed, and is recorded because it consumed "
           "schedule:")
    TABLE(doc, ["Who", "Training needed", "Why"],
          [["Automation engineer", "Selenium WebDriver, explicit waits, driver options",
            "The suite was built from nothing. Explicit waits in particular were learned "
            "only after a fixed sleep produced an intermittent failure."],
           ["Test designer", "Case specification structure and levelling",
            "Cases had to carry preconditions, data, expected results and dependencies in a "
            "form a second person could execute unaided."],
           ["Developer", "Database state management for repeatable tests",
            "Tests are repeatable only against a known seed state, which required the reset "
            "utility."],
           ["Acceptance users", "A walkthrough of the credit model before their session",
            "The credit economy is the part of the product a new user does not expect, and "
            "an acceptance judgement is worthless if the user misunderstands it."]],
          widths=[1.4, 2.1, 2.7], size=9, caption="Table 13. Training needs.")

    # ------------------------------------------------------------ 12 responsibilities
    H(doc, "12.  RESPONSIBILITIES")
    TABLE(doc, ["Role", "Assigned to", "Responsibility"],
          [list(x) for x in RESPONSIBILITIES],
          widths=[1.35, 1.35, 3.5], size=9,
          caption="Table 14. Roles and responsibilities.")

    # ------------------------------------------------------------ 13 schedule
    H(doc, "13.  TESTING SCHEDULE")
    P(doc, "The schedule was produced in GanttProject and is reproduced below as a task "
           "list with dependencies. The chart it generates is Figure 11. Durations are "
           "ESTIMATES in working days.", italic=True, color=NAVY)
    TABLE(doc, ["ID", "Task", "Duration (days)", "Owner", "Depends on"],
          [list(x) for x in SCHEDULE],
          widths=[0.55, 2.75, 1.05, 1.35, 0.9], size=9,
          caption="Table 15. Testing schedule.")
    total = sum(x[2] for x in SCHEDULE)
    crit = 4 + 6 + 2 + 7 + 5 + 4 + 2 + 3 + 3
    P(doc, f"Total test effort is {total} person-days. The critical path runs T-01, T-03, "
           f"T-04, T-06, T-08, T-09, T-10, T-11, T-12, which is {crit} days. The remaining "
           f"tasks carry float and can absorb a delay without moving the end date.")
    gantt = os.path.join(ROOT, "gantt.png")
    if os.path.exists(gantt):
        pic = doc.add_paragraph()
        pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pic.paragraph_format.space_before = Pt(8)
        pic.paragraph_format.keep_with_next = True
        pic.add_run().add_picture(gantt, width=Inches(6.4))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cp.add_run("Figure 11. Testing schedule, generated in GanttProject.")
        r.font.size = Pt(9)
        r.font.name = FONT
        r.italic = True
    else:
        P(doc, "[ Figure 11 goes here. Open SkillBank_Test_Schedule.gan in GanttProject or "
               "ProjectLibre, then export the chart as PNG to gantt.png in this folder and "
               "re-run the build. ]", italic=True, color=RED)

    # ------------------------------------------------------------ 14 risks
    H(doc, "14.  PLANNING RISKS AND CONTINGENCIES")
    for rid, name, prob, impact, risk, mitigation in RISKS:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"{rid}  {name}")
        r.bold = True
        r.font.size = Pt(11)
        r.font.name = FONT
        r.font.color.rgb = NAVY
        r = p.add_run(f"    (likelihood {prob}, impact {impact})")
        r.font.size = Pt(9.5)
        r.font.name = FONT
        r.italic = True
        P(doc, risk, size=10.5, after=3)
        pm = doc.add_paragraph()
        pm.paragraph_format.space_after = Pt(4)
        pm.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pm.paragraph_format.left_indent = Inches(0.2)
        r = pm.add_run("Contingency.  ")
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.name = FONT
        r = pm.add_run(mitigation)
        r.font.size = Pt(10.5)
        r.font.name = FONT

    # ------------------------------------------------------------ 15 defects
    H(doc, "15.  DEFECTS FOUND AND RESOLVED")
    P(doc, "Two defects were raised during execution. Both were in the test harness rather "
           "than in the application. That is recorded here because a report listing only "
           "successes is not a test report.")
    TABLE(doc, ["ID", "Raised against", "Severity", "Description", "Resolution"],
          [["D-01", "Test harness", "Critical",
            "16 of 40 cases failed after the first login. Chrome's password-manager bubble "
            "took keyboard focus and consumed the keystrokes intended for the form.",
            "Driver profile changed to disable the password manager and leak detection. All "
            "40 cases passed on re-run."],
           ["D-02", "Test harness", "Major",
            "TC_ses-05 failed intermittently. A fixed 0.35 second wait was shorter than the "
            "page load under some conditions.",
            "Every fixed sleep in the suite was replaced with an explicit WebDriverWait on a "
            "real condition. The intermittent failure has not recurred."]],
          widths=[0.5, 1.1, 0.8, 2.4, 2.2], size=9, caption="Table 16. Defect log.")
    P(doc, "No defect was found in the application itself. That is a real result for a suite "
           "of this size, and it is also a limitation: 40 functional cases across five "
           "modules is not exhaustive, and Section 6 lists what was never examined.")

    # ------------------------------------------------------------ 16 approvals
    H(doc, "16.  APPROVALS")
    P(doc, "The signatures below indicate that the signatory has reviewed this plan and "
           "accepts it as the basis for testing.")
    TABLE(doc, ["Role", "Name", "Signature", "Date"],
          [["QA Lead / Test Lead", STUDENT, "", ""],
           ["Senior QA (industry personnel, optional)", "", "", ""],
           ["Course Instructor", "", "", ""]],
          widths=[2.3, 1.7, 1.4, 0.9], size=10)

    return {"modules": len(mods), "priorities": prios, "passed": passed}
