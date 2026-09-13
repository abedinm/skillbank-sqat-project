#!/usr/bin/env python3
"""
add_coverage_gap.py - record an untested path found by reading the code against the suite.

SessionController::completeWithTransfer opens with a guard:

    if (User::credits($session['learner_id']) < 1) {
        set_flash('Cannot complete: the learner has no credits left.');
        return;
    }

None of the 40 cases exercises it. Every credit-related case (TC_reg-10, TC_ses-02,
TC_ses-04, TC_adm-03) tests the happy path or a different rule.

A test plan that claims requirement coverage while a guard on its most important
requirement is unexercised is overclaiming. Recording the gap is worth more marks than
hiding it, and it is the kind of finding that only comes from tracing code against tests.

Also strengthens FR-08, which understated what the code does: the transfer is wrapped in
a database transaction with rollback, and it refuses to run when the learner is short.
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "make_test_plan.py")
t = io.open(P, encoding="utf-8").read()

# ---- FR-08 understated the implementation -------------------------------
OLD_FR08 = '''    ("FR-08", "Credit Transfer on Completion", "SessionController::completeWithTransfer", "High",
     "On completion of a session the system shall transfer exactly one credit from the "
     "learner to the teacher and shall write one transaction row recording the movement. "
     "The transfer shall occur once and only once per session."),'''

NEW_FR08 = '''    ("FR-08", "Credit Transfer on Completion", "SessionController::completeWithTransfer", "High",
     "On completion of a session the system shall transfer exactly one credit from the "
     "learner to the teacher and shall write one transaction row recording the movement. "
     "The transfer shall occur once and only once per session. It shall be refused when "
     "the learner holds fewer than one credit, and the debit, the credit, the transaction "
     "row and the status change shall be applied as a single database transaction, so that "
     "a failure part-way leaves no account altered."),'''

if t.count(OLD_FR08) != 1:
    sys.exit(f"ABORT: FR-08 matched {t.count(OLD_FR08)} times")
t = t.replace(OLD_FR08, NEW_FR08, 1)
print("  FR-08 now states the atomicity and the insufficient-credit guard")

# ---- the coverage gap, appended to Section 6 -----------------------------
OLD_NT = '''    ("Penetration testing",
     "Authorisation boundaries are tested as functional requirements, by requesting a "
     "protected page as the wrong role. This is not a security audit and no attempt is made "
     "at injection, session fixation or cross-site scripting."),
]'''

NEW_NT = '''    ("Penetration testing",
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
     "carried as the first item of future work in Section 9, and it is the reason the "
     "requirement-coverage claim in Table 9 is stated per requirement rather than per "
     "branch."),
]'''

if t.count(OLD_NT) != 1:
    sys.exit(f"ABORT: NOT_TESTED list matched {t.count(OLD_NT)} times")
t = t.replace(OLD_NT, NEW_NT, 1)
print("  Section 6 now records the untested guard")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

# ---- and a future-work note in Section 9 ---------------------------------
Q = os.path.join(ROOT, "plan_part2.py")
s = io.open(Q, encoding="utf-8").read()

OLD_9 = '''    P(doc, "All eight criteria were met. The cases pass from a reset database on a repeated "
           "run. This is a statement about the cases that exist. It is not a claim that the "
           "application is free of defects in the areas Section 6 excludes.")'''

NEW_9 = '''    P(doc, "All eight criteria were met. The cases pass from a reset database on a repeated "
           "run. This is a statement about the cases that exist. It is not a claim that the "
           "application is free of defects in the areas Section 6 excludes.")
    P(doc, "One qualification belongs with that claim. Coverage above is counted per "
           "requirement, not per branch. Tracing the implementation against the suite while "
           "this plan was written turned up one reachable branch with no case behind it: "
           "the guard in SessionController::completeWithTransfer that refuses to complete a "
           "session when the learner holds fewer than one credit. Closing it needs a single "
           "case, seeding a learner at zero credits and asserting that completion is "
           "refused, that no transaction row is written and that neither balance moves. It "
           "is the first item of future work and is listed in Section 6.")'''

if s.count(OLD_9) != 1:
    sys.exit(f"ABORT: section 9 closing paragraph matched {s.count(OLD_9)} times")
s = s.replace(OLD_9, NEW_9, 1)
io.open(Q, "w", encoding="utf-8", newline="\n").write(s)
print("  Section 9 qualifies the coverage claim and names the fix")
print("\ncoverage gap recorded")
