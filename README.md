# SkillBank — SQAT Project

**Minhazul Abedin · 21-44625-1 · AIUB · Software Quality Assurance and Testing, Summer 2025-2026**

A credit-based peer skill exchange, and the software test plan written against it.

Members teach each other and pay in credits rather than money. Everyone starts with three
credits. Teaching a session earns one, learning spends one, so value moves in a triangle:
teach one person, learn from a different one. Nobody has to find a partner who happens to
want exactly the skill they hold.

**→ [docs/SkillBank Software Test Plan.pdf](docs/SkillBank%20Software%20Test%20Plan.pdf)** — the submitted deliverable, 41 pages.

---

## What is in here

| Folder | Contents |
|---|---|
| `application/` | The SkillBank web app. PHP 8 + MySQL, 5 controllers, 7 models, 7 tables, ~1,300 lines |
| `tests/` | The Selenium suite, the database reset utility, and the recorded results |
| `screenshots/` | 107 screenshots captured during the test run, one per step |
| `docs/` | Test plan (PDF + Word), test case document, Selenium report, viva prep |
| `plan-generator/` | The scripts that build the test plan document from the recorded results |
| `figures/` | Screen flow, architecture, and the Gantt chart |
| `tools/` | Report builder, screenshot capture helper, macOS setup guide |

---

## Part 1 — Running the application

### What you need

- **PHP 8.0+** and **MySQL 5.7+** — XAMPP gives you both in one installer
- A browser

### Steps

**1. Start Apache and MySQL.** In the XAMPP control panel, start both.

On Windows, note that they are *not* Windows services — if you start `mysqld` from a
terminal it dies when the terminal closes unless you redirect its output.

**2. Create the database.**

```bash
mysql -u root -p -e "CREATE DATABASE skillbank CHARACTER SET utf8mb4;"
mysql -u root -p skillbank < application/schema.sql
```

That creates the seven tables: `users`, `skills`, `offers`, `sessions`, `transactions`,
`reviews`, `wishes`.

**3. Load the seed data.** Visit `seed.php` once in the browser, or:

```bash
php application/seed.php
```

This creates the skill catalogue, a set of demo members and some offers, and the
administrator account. **The suite depends on this seed state** — see Part 2.

**4. Point a web server at `application/`.**

XAMPP: copy `application/` into `C:\xampp\htdocs\skillbank`, then open
`http://localhost/skillbank`.

Or use PHP's built-in server, which is what the test runs were done against:

```bash
php -S 127.0.0.1:8003 -t application application/index.php
```

Then open **http://127.0.0.1:8003**

### Database connection

`application/app/Core/Database.php` reads environment variables and falls back to XAMPP
defaults. No credentials are stored in this repository.

| Variable | Default |
|---|---|
| `SB_DB_HOST` | `localhost` |
| `SB_DB_PORT` | `3306` |
| `SB_DB_USER` | `root` |
| `SB_DB_PASS` | empty |
| `SB_DB_NAME` | `skillbank` |

Set them only if your MySQL differs from the XAMPP default:

```bash
SB_DB_USER=myuser SB_DB_PASS=mypass php -S 127.0.0.1:8003 -t application application/index.php
```

### Trying it by hand

1. Register a new account — you land on the dashboard with **3 credits**
2. Browse offers, open one belonging to another member, request a session
3. Log in as that member, accept the request, then mark it complete
4. **Exactly one credit** moves from learner to teacher, and one row is written to
   `transactions`
5. The learner can then review the session, once

That last step is the whole product. Everything else exists to support it.

---

## Part 2 — Running the tests

### What you need

```bash
pip install selenium mysql-connector-python
```

Plus **Google Chrome** and a matching **ChromeDriver** on your `PATH`. Selenium 4.6+
downloads the driver automatically, so usually you need nothing extra.

### Before every run: reset the database

The suite is only repeatable from a known state. A case that runs after another has spent
a credit or created an offer will fail for reasons unrelated to what it is testing.

```bash
python tests/reset_db.py
```

This drops and rebuilds the data to the seed state. **Run it every time**, not just the
first time.

### Run the whole suite

With the application serving on `127.0.0.1:8003`:

```bash
python tests/selenium_suite.py
```

Chrome opens and drives itself through 40 cases across 5 modules. Expect a few minutes.

Output:

- `run_log.txt` — one line per case with its result and timing
- `results.json` — the full record: steps, data, expected, actual, status, screenshots
- `screenshots/` — a PNG per step

### What the 40 cases cover

| Module | Cases | High | Medium | Low |
|---|---:|---:|---:|---:|
| Registration | 10 | 3 | 2 | 5 |
| Login | 8 | 5 | 3 | 0 |
| Skill Offer Management | 8 | 2 | 5 | 1 |
| Session Booking | 7 | 3 | 3 | 1 |
| Admin Panel | 7 | 2 | 4 | 1 |
| **Total** | **40** | **15** | **17** | **8** |

Priority is the **consequence of failure**, not the effort of running the case. High means
a core path or a security boundary — registration, login, the credit transfer, and every
access-control check. Low means a boundary case, like a password of exactly five
characters versus exactly six.

### Expected result

**40 of 40 pass** from a reset database. Two consecutive runs give the same result.

If cases fail, the usual causes in order of likelihood:

1. **You forgot `reset_db.py`.** By far the most common.
2. **The app is not serving on `127.0.0.1:8003`** — check the port.
3. **ChromeDriver does not match your Chrome version.** Update Chrome.
4. **Chrome's password manager is stealing focus.** The suite disables it in the driver
   profile; if you have modified that, see the note below.

### Two defects found during development, both in the harness

Recorded because a test report listing only successes is not a test report.

**D-01 (critical).** Sixteen of forty cases failed after the first login. Chrome's own
password-manager bubble took keyboard focus and consumed the keystrokes meant for the
form. Fixed by disabling the password manager and leak detection in the driver profile.
Not an application defect — the application was fine and the harness was lying about it.

**D-02 (major).** One case failed intermittently. A fixed `time.sleep(0.35)` was sometimes
shorter than the page load. Every fixed sleep in the suite was replaced with an explicit
`WebDriverWait` on a real condition. The flakiness has not recurred.

### Known coverage gaps

Found by tracing the code against the suite while writing the test plan, not by a failing
test. Both are recorded in the plan rather than left to be discovered:

1. **`SessionController::completeWithTransfer`** refuses to complete a session when the
   learner holds fewer than one credit. No case exercises that branch. It is reachable in
   normal use — a member who spends all three starting credits before earning any will hit
   it.
2. **FR-10, the wishlist**, has no test case at all. Requirement coverage closed at 9 of
   10, not 10 of 10.

Closing both needs two cases. Neither is written yet.

---

## Part 3 — Rebuilding the test plan document

The plan is generated from the recorded results, not typed by hand. That means the numbers
in the document cannot drift away from the run that produced them.

```bash
pip install python-docx matplotlib
```

```bash
python plan-generator/priorities.py       # results.json -> results_prioritised.json
python plan-generator/make_diagrams.py    # screen flow + architecture figures
python plan-generator/make_schedule.py    # the GanttProject file
python plan-generator/make_test_cases.py  # the 40 case tables, standalone
python plan-generator/make_test_plan.py   # the full document
```

`make_test_plan.py` imports `plan_part2.py` for sections 8 to 16 — run the former, not the
latter.

### The Gantt chart

The assignment requires the schedule to come from a project management tool, not from Word
or Excel. `make_schedule.py` writes `SkillBank_Test_Schedule.gan`, a real GanttProject
file with twelve tasks, thirteen dependencies and resource allocations.

Open it in [GanttProject](https://www.ganttproject.biz/) (free) and export a PNG, or drive
the exporter directly:

```bash
"C:\Program Files\GanttProject-3.3\runtime\bin\java.exe" ^
  -classpath "eclipsito.jar;lib\slf4j-api-2.0.4.jar;lib\slf4j-jdk14-2.0.4.jar;." ^
  com.bardsoftware.eclipsito.Launch --version-dirs plugins ^
  --app net.sourceforge.ganttproject.GanttProject ^
  -export png -out gantt.png SkillBank_Test_Schedule.gan
```

Run that from `C:\Program Files\GanttProject-3.3\app`. GanttProject 3.3 needs Java 11+;
it ships its own Java 17 in `runtime\`, which is why the command points there rather than
at the system Java.

Save the result as `figures/gantt.png` and re-run `make_test_plan.py` — it picks the image
up automatically as Figure 11.

### PDF export

Windows, via Word:

```powershell
$w = New-Object -ComObject Word.Application
$d = $w.Documents.Open("SkillBank_Software_Test_Plan.docx", $false, $true)
$d.ExportAsFixedFormat("SkillBank Software Test Plan.pdf", 17)
$d.Close($false); $w.Quit()
```

macOS or Linux, via LibreOffice:

```bash
soffice --headless --convert-to pdf SkillBank_Software_Test_Plan.docx
```

---

## Part 4 — The test plan itself

41 pages, sixteen sections, following the course template.

| § | Section | § | Section |
|---|---|---|---|
| 1 | Revision History | 9 | Item Pass/Fail Criteria |
| 2 | Test Plan Identifier | 10 | Test Deliverables |
| 3 | References | 11 | Staffing and Training Needs |
| 4 | Introduction | 12 | Responsibilities |
| 5 | Requirement Specification | 13 | Testing Schedule |
| 6 | Features Not To Be Tested | 14 | Planning Risks and Contingencies |
| 7 | Testing Approach | 15 | Defects Found and Resolved |
| 8 | Test Cases / Test Items | 16 | Approvals |

Ten functional requirements and seven quality attributes, each levelled and prioritised,
each traced to the cases that verify it. Eleven figures, sixteen tables.

Section 4 carries eighteen cited sources on the problem domain — household education
spending, NEET figures, peer-teaching effect sizes. Every figure was fetched from its
source and confirmed there before being used.

---

## Honest notes

- **The budget and schedule are estimates**, not measurements. They are labelled as such in
  the document. 47 person-days of testing inside a 130 person-day project is a
  construction, not a fact.
- **One person holds every role.** The plan names Test Lead, Test Designer, Automation
  Engineer and Developer separately because the responsibilities differ even when the
  person does not. This is carried as risk R-01.
- **No defect was found in the application itself.** That is a real result for a suite of
  this size and also a limitation: 40 functional cases across five modules is not
  exhaustive. Section 6 of the plan lists everything that was never examined — performance,
  browsers other than Chrome, responsive layout, and penetration testing.

## Repository note

`abedinm/skillbank-selenium-tests` holds an earlier, Selenium-only snapshot of this work.
This repository supersedes it and contains the complete project.
