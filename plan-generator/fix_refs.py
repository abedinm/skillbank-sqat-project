#!/usr/bin/env python3
"""
fix_refs.py - correct the mis-numbered "Section N" cross-references.

The section numbers settled late, and an earlier sweep only covered prose paragraphs.
References buried inside the DELIVERABLES, RISKS and RESPONSIBILITIES data tables were
missed. A multi-agent audit found seven of them, each confirmed independently.

Correct numbering:
   1 Revision History          9 Item Pass/Fail Criteria
   2 Test Plan Identifier     10 Test Deliverables
   3 References               11 Staffing and Training
   4 Introduction             12 Responsibilities
   5 Requirement Spec         13 Testing Schedule
   6 Features Not To Be Tested 14 Risks and Contingencies
   7 Testing Approach         15 Defects Found and Resolved
   8 Test Cases / Test Items  16 Approvals
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FIXES = [
    # (file, exact old fragment, new fragment, why)
    ("make_test_plan.py",
     '"40 cases across 5 modules, Section 6."',
     '"40 cases across 5 modules, Section 8."',
     "test cases are Section 8, not 6"),
    ("make_test_plan.py",
     '"Two harness defects found and resolved, Section 12."',
     '"Two harness defects found and resolved, Section 15."',
     "defect log is Section 15, not 12"),
    ("make_test_plan.py",
     '"Test cases are written from the requirement statements in Section 3 rather than from "',
     '"Test cases are written from the requirement statements in Section 5 rather than from "',
     "requirements are Section 5, not 3"),
    ("make_test_plan.py",
     '"Performance is explicitly listed in Section 4 as not to be tested."',
     '"Performance is explicitly listed in Section 6 as not to be tested."',
     "not-to-be-tested is Section 6, not 4"),
    ("make_test_plan.py",
     '"Writes case specifications from the requirements in Section 3, fixes expected results "',
     '"Writes case specifications from the requirements in Section 5, fixes expected results "',
     "requirements are Section 5, not 3"),
    ("make_test_plan.py",
     'for the quality attribute vocabulary used in Section 3.2.',
     'for the quality attribute vocabulary used in Section 5.2.',
     "quality attributes are 5.2, not 3.2"),
    ("make_test_plan.py",
     '"Producing the schedule in Section 11."',
     '"Producing the schedule in Section 13."',
     "schedule is Section 13, not 11"),
]

SECTIONS = {
    1: "REVISION HISTORY", 2: "TEST PLAN IDENTIFIER", 3: "REFERENCES",
    4: "INTRODUCTION", 5: "REQUIREMENT SPECIFICATION", 6: "FEATURES NOT TO BE TESTED",
    7: "TESTING APPROACH", 8: "TEST CASES", 9: "ITEM PASS/FAIL",
    10: "TEST DELIVERABLES", 11: "STAFFING", 12: "RESPONSIBILITIES",
    13: "TESTING SCHEDULE", 14: "RISKS", 15: "DEFECTS", 16: "APPROVALS",
}

applied, failed = 0, []
for fname, old, new, why in FIXES:
    p = os.path.join(ROOT, fname)
    t = io.open(p, encoding="utf-8").read()
    n = t.count(old)
    if n != 1:
        failed.append(f"{n} matches in {fname}: {old[:60]}")
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(t.replace(old, new, 1))
    applied += 1
    print(f"  fixed  {why}")

if failed:
    print("\nDID NOT MATCH:", file=sys.stderr)
    for f in failed:
        print("  " + f, file=sys.stderr)
    sys.exit(1)

print(f"\n{applied} cross-references corrected")
print("\nAll Section refs now point at:")
for fname in ("make_test_plan.py", "plan_part2.py"):
    t = io.open(os.path.join(ROOT, fname), encoding="utf-8").read()
    for m in sorted(set(re.findall(r"Section (\d+)(?:\.\d+)?", t)), key=int):
        pass
seen = set()
for fname in ("make_test_plan.py", "plan_part2.py"):
    t = io.open(os.path.join(ROOT, fname), encoding="utf-8").read()
    for m in re.findall(r"Section (\d+)(?:\.\d+)?", t):
        seen.add(int(m))
for n in sorted(seen):
    print(f"  Section {n:>2}  ->  {SECTIONS.get(n, '??? OUT OF RANGE')}")
