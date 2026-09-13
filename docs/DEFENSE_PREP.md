# SkillBank Test Plan — defense prep

Read this the night before. The questions are grouped by how likely they are and how
badly they hurt if you fumble them.

**The rule for the whole viva: never invent a number.** If you are not sure, say
"I'd have to check the document" and turn to the page. That answer costs you nothing.
A wrong number costs you the examiner's trust for everything after it.

---

## A. You will almost certainly be asked these

### 1. "What is your project?"

SkillBank is a peer skill-exchange platform. Members teach each other and pay in credits
instead of money. Everyone starts with three credits, teaching a session earns one,
learning one spends one.

**The point to land:** the credit is what makes it work. Without it you'd need to find
someone who wants exactly the skill you have and has exactly the skill you want. Credits
let value move in a triangle — teach one person, learn from a different one.

### 2. "Why does this problem matter?"

Learning a skill in Bangladesh usually means paying cash, and the people who most need to
learn are the ones without cash.

**Numbers, Section 4.1:**
- Private tutoring is the **largest single line** in the average household education
  budget — **26%**, ahead of fees (20%) and books (23%)
- **22%** of 15–29 year olds are not in education, employment or training
- Only **5%** of the labour force has had any training; **1%** any vocational training
- The kicker: **the highest unemployment of any education level is tertiary graduates,
  at 27.8%**

If you remember one figure, remember the last one. It says the people with most to teach
are least likely to be earning.

### 3. "How many test cases and what were the results?"

40 cases across 5 modules. All 40 pass.

| Module | Cases |
|---|---|
| Registration | 10 |
| Login | 8 |
| Skill Offer Management | 8 |
| Session Booking | 7 |
| Admin Panel | 7 |

### 4. "How did you prioritise the test cases?"

**By consequence of failure, not by effort.** 15 High, 17 Medium, 8 Low.

- **High** — core paths and every security boundary. Valid registration and login, the
  credit transfer, and every access-control check: guest blocked from the dashboard,
  member blocked from admin, member blocked from editing another member's offer.
- **Medium** — supporting features and required-field validation. Create, edit, delete.
- **Low** — boundary cases. Password exactly 6 characters versus exactly 5, invalid email
  format, submitting a fully empty form.

**If pushed on an example:** "TC_reg-08 tests a password of exactly 6 characters and
TC_reg-09 exactly 5. Those are Low, because if the boundary is off by one the user sees an
error message they didn't expect. TC_ses-04 tests that completing a session moves exactly
one credit — that's High, because if it's wrong the product's entire economy is broken."

### 5. "What did your testing actually find?"

**Two defects, both in the test harness, none in the application.** Say that plainly and
then explain both, because a report with no findings looks lazy until you explain it.

- **D-01, critical.** 16 of 40 cases failed after the first login. Chrome's password
  manager popup stole keyboard focus and ate the keystrokes meant for the form. Fixed by
  disabling the password manager in the driver profile.
- **D-02, major.** One case failed intermittently. A fixed 0.35-second wait was sometimes
  shorter than the page load. Replaced every fixed sleep in the suite with an explicit
  wait on a real condition.

**The line that shows you understand it:** "Neither was an application defect. Both were
environmental, and I recorded them because a test report listing only successes isn't a
test report."

---

## B. The dangerous ones — where an examiner probes

### 6. "40 cases, all passed, no bugs found. Isn't that suspicious?"

**This is the question most likely to catch you out. Answer it honestly.**

"It's a fair challenge. 40 functional cases across five modules is not exhaustive, and
Section 6 lists everything I didn't test — performance, browsers other than Chrome,
responsive layout, and penetration testing. What I claim is that the functionality I
specified in Section 5 behaves as specified. I don't claim the application is defect-free."

Then hand him the next answer before he asks for it:

### 7. "So is there anything you know you missed?"

**Yes — and volunteering this will do you more good than anything else in the viva.**

"One. `SessionController::completeWithTransfer` refuses to complete a session when the
learner has fewer than one credit. None of my 40 cases exercises that branch. I found it
by reading the code against the suite while writing this plan, not from a failing test.
It's reachable in normal use — a member who spends all three starting credits before
earning any will hit it. It's recorded in Section 6 and Section 9 as the first item of
future work, and closing it needs one case: seed a learner at zero credits, assert the
completion is refused, no transaction row is written, and neither balance moves."

**Why this wins marks:** it proves you traced requirements to tests rather than asserting
coverage. Most students claim 100% coverage. You found your own gap and wrote it down.

### 8. "Where did the budget and schedule numbers come from?"

**Say the word "estimate" in your first sentence.** They are labelled as estimates in the
document, so do not let him think you are presenting them as measured.

"Those are estimates for a costed version of the project, not measurements. Testing is 47
person-days, derived from the task durations in the schedule — a task with two owners
splits between them, which is why some figures are half-days. Total project is 130
person-days, 676,550 BDT. Testing is 36% of project effort, which is high, and that's
deliberate: this product moves a unit of value between two accounts, so a defect in the
transfer isn't cosmetic."

### 9. "Why is testing 36% of the effort? Isn't that too much?"

"For a CRUD application it would be. This one has a transaction that moves value between
accounts and an authorisation model with two roles. A bug in either is not a display
problem — it's either lost credits or a member reading another member's data. That's
where the weight went: 15 of the 40 cases are core paths or security boundaries."

### 10. "Why Selenium and not manual testing?"

"Because the suite gets re-run after every defect fix. A 40-case regression by hand
wouldn't survive that repetition — it would get skipped once and then always. Automating
it meant that after fixing D-01 I could re-run all 40 and know within minutes that nothing
else had broken."

### 11. "Your schedule assumes a team. You worked alone."

"Yes, and Section 11 says that in the first paragraph. I named the roles separately
because the responsibilities are genuinely different even when the person isn't, and
because a costed version would separate them. It's carried as risk R-01: one person
designing, executing and reporting means no independent reviewer, so a misunderstood
requirement produces a test that confirms the misunderstanding."

---

## C. Straightforward technical questions

### 12. "What are your testing levels?"

Three. **Unit** — developer's job, and the entry gate to system testing. **System and
integration, combined** — because the application is one deployable with no external
services to integrate against. **Acceptance** — real users, on the accepted build.

Entry and exit criteria for each are in Table 8.

### 13. "What's a test plan identifier and what's yours?"

It names the product and the plan revision so you can tell two versions apart.
Mine is **TP_SkillBank_1.0**.

### 14. "What's in the pass/fail criteria?"

Eight criteria, weighted by priority because a failing High and a failing Low aren't the
same. High cases must be 100%, Medium at least 95%, Low at least 90%, overall at least
95%, zero critical defects open, at most two major and none blocking, every requirement
covered by at least one case, and two consecutive runs from a reset database give the same
result. All eight met.

### 15. "Why Category A and not B?"

"Because it starts from a problem I can name and measure rather than from an idea looking
for a use. The problem is in Section 4.1 with figures; the solution is 4.2."

### 16. "Explain your most important requirement."

**FR-08, the credit transfer.** On completion, exactly one credit moves from learner to
teacher, one transaction row is written, and the session status changes. All four happen
in a single database transaction, so a failure halfway leaves no account altered. It's
refused if the learner holds under one credit.

**If he asks how you know it's atomic:** the code wraps it in
`mysqli_begin_transaction` with a commit on success and a rollback in the catch block.

### 17. "How do you keep tests repeatable?"

`reset_db.py` restores a known seed state before every full run. Without it a case that
runs after another has spent a credit or created an offer fails for reasons unrelated to
what it's testing. That's risk R-02.

---

## D. Numbers to have at your fingertips

| | |
|---|---|
| Test cases | 40, all pass |
| Modules | 5 |
| Priorities | 15 High / 17 Medium / 8 Low |
| Screenshots | 107 |
| Application | 1,304 lines PHP, 5 controllers, 7 models, 7 tables |
| Starting credits | 3 |
| Credits per session | exactly 1 |
| Defects found | 2, both in the harness |
| Testing effort | 47 person-days |
| Project effort | 130 person-days, 676,550 BDT (estimate) |
| Schedule tasks | 12, critical path 36 days |
| Requirements | 10 functional, 7 quality attributes |

---

## E. If you don't know the answer

Say so. Three phrasings that cost you nothing:

- "I'd have to check the document — it's in Section X."
- "I don't know, but here's how I'd find out."
- "That's outside what I tested. Section 6 lists what I excluded and why."

**Do not guess at a number.** One invented figure and he'll start checking everything.

## F. The two soft spots — know them before he finds them

1. **The document is far more polished than a first test plan usually is.** If he asks how
   you produced it, don't oversell. The application, the 40 test cases and their execution
   are genuinely your work from August. The plan document was assembled afterwards from
   that data.

2. **The budget and schedule are constructions, not measurements.** Never defend them as
   facts. Every time one comes up, the word "estimate" goes in your first sentence.
