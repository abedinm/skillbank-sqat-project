#!/usr/bin/env python3
"""
add_declaration.py - declare the project category and technology option.

Two instructions in the guidelines that the document did not answer:

  "Each team is required to come up with a great idea (either Category A or Category B)"
  "You must choose at least one of the options for technology"  (A Web / B Desktop / C Mobile)

This matters beyond box-ticking: the Concept marking scheme branches on the category.

  For Category A: Does the project address a clear need, problem, or opportunity and is
                  the solution clearly explained?
  For Category B: What makes this project new, innovative, interesting...? Does the
                  project duplicate functionality already available in the market?

Without a declaration the marker does not know which set to apply. SkillBank is
Category A: it starts from a stated problem (skill learning priced in cash, in a
population without cash) and builds a solution to it. Technology is Option A, Web.

The paragraph is placed at the head of Section 4 so it is the first thing read, and it
points at the subsections that answer the Category A criteria.
"""

import io
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(ROOT, "make_test_plan.py")
t = io.open(P, encoding="utf-8").read()

ANCHOR = '''    H(doc, "4.  INTRODUCTION")
    H(doc, "4.1  Background to the Problem", 2)'''

REPLACEMENT = '''    H(doc, "4.  INTRODUCTION")
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

    H(doc, "4.1  Background to the Problem", 2)'''

if t.count(ANCHOR) != 1:
    sys.exit(f"ABORT: introduction anchor matched {t.count(ANCHOR)} times")
t = t.replace(ANCHOR, REPLACEMENT, 1)
print("  declared Category A and Technology Option A at the head of Section 4")

# the new table takes Table 1; everything after shifts by one
import re
for n in range(14, 0, -1):
    t = t.replace(f'caption="Table {n}.', f'caption="Table {n + 1}.')
# ...except the one just added, which must stay Table 1
t = t.replace('caption="Table 2. Project category and technology declaration."',
              'caption="Table 1. Project category and technology declaration."', 1)
# and the budget caption's internal reference to the schedule table
t = t.replace("derived from the schedule in Table 13.",
              "derived from the schedule in Table 14.")
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("  renumbered captions in make_test_plan.py")

Q = os.path.join(ROOT, "plan_part2.py")
s = io.open(Q, encoding="utf-8").read()
for n in range(14, 7, -1):
    s = s.replace(f'caption="Table {n}.', f'caption="Table {n + 1}.')
io.open(Q, "w", encoding="utf-8", newline="\n").write(s)
print("  renumbered captions in plan_part2.py")
print("\ndeclaration added")
