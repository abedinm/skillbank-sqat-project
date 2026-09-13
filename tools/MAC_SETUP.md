# Running the SkillBank Selenium suite on macOS

This file has two parts:

1. **[The prompt](#part-1--the-prompt)** — paste it into Claude Code (or any AI coding
   assistant) on the Mac and it will build the whole environment and run the suite.
2. **[The manual steps](#part-2--manual-setup)** — the same thing done by hand, in case
   you would rather do it yourself or something in the prompt run goes wrong.

The suite drives a real Chrome browser against the SkillBank web app running locally,
executes 40 test cases, screenshots every step, and writes a Word report.

**What you need on the Mac:** macOS 12 or newer, an internet connection, and about
15 minutes. Everything installed below is free.

---

## Part 1 — the prompt

Open Terminal, `cd` to where you want the project, start Claude Code, and paste this:

```
I want to set up and run a Selenium automated test suite on this Mac. Do all of it,
do not stop to ask me to run commands yourself.

CONTEXT
Two GitHub repositories (both private, account: abedinm):
  - skillbank                  -> the PHP/MySQL web app under test
  - skillbank-selenium-tests   -> the Python Selenium suite + report generator

The suite was written on Windows. Everything is cross-platform except three hardcoded
paths that you must fix for macOS.

WHAT TO DO

1. Install the toolchain with Homebrew. If Homebrew is missing, install it first.
   - php (8.1+), mysql, python (3.10+), and Google Chrome (brew install --cask
     google-chrome) if Chrome is not already in /Applications.
   - Start MySQL: brew services start mysql

2. Clone both repositories with the gh CLI (gh auth login first if needed):
     gh repo clone abedinm/skillbank
     gh repo clone abedinm/skillbank-selenium-tests

3. Create the database:
     mysql -u root < skillbank/schema.sql
   If your MySQL root user has a password, add -p and remember it for step 5.

4. Create a Python virtual environment inside skillbank-selenium-tests and install
   the dependencies:
     python3 -m venv .venv && source .venv/bin/activate
     pip install selenium pillow python-docx
   Do NOT download ChromeDriver by hand. Selenium 4 ships with Selenium Manager and
   fetches the matching driver automatically.

5. Fix the three Windows-only things in the test suite. These are the ONLY changes
   needed to run on macOS:
   a) selenium_suite.py  -> MYSQL = r"C:\xampp\mysql\bin\mysql.exe"
      becomes            -> MYSQL = "/opt/homebrew/bin/mysql"
      (use `which mysql` to get the real path; on Intel Macs it is /usr/local/bin/mysql)
   b) reset_db.py        -> MYSQL and SCHEMA paths, same idea; SCHEMA must point at
      the schema.sql inside the cloned skillbank repo
   c) reset_db.py        -> the mysql call may need a password flag if your root user
      has one
   If the MySQL root user has a password, also export it so PHP can connect:
     export SB_DB_USER=root
     export SB_DB_PASS=yourpassword

6. Start the web app on port 8003 with PHP's built-in server, from inside the
   skillbank folder, and leave it running in the background:
     php -S 127.0.0.1:8003 index.php
   Confirm it answers: curl -s http://localhost:8003 | head -20
   It should return HTML containing "Browse skills".

7. Seed the demo data by requesting http://localhost:8003/seed.php once. This creates:
     admin@skillbank.test  / password123  (admin)
     ayesha@skillbank.test / password123  (member)
     rahim@skillbank.test  / password123  (member)

8. Run the suite from the skillbank-selenium-tests folder:
     python reset_db.py
     python selenium_suite.py
   Expected output: 40 lines, one per test case, ending with "40/40 passed".
   Screenshots land in ./screenshots (about 107 PNG files).
   To watch the browser instead of running headless: SB_HEADED=1 python selenium_suite.py

9. Build the Word report:
     python build_report.py
   This writes SQAT_Selenium_Report_SkillBank.docx (about 68 pages).

10. Report back with: the exact pass count, the number of screenshots produced, the
    page count of the report, and any test case that failed with the reason.

RULES
- Fix root causes. If a test fails, work out whether it is the app, the environment or
  the test, and say which. Do not delete or skip a failing test to make the run green.
- Do not change any test's expected result to match whatever the app happens to do.
- Report the real numbers. "40/40 passed", not "all tests passed".
```

---

## Part 2 — manual setup

### 1. Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the note it prints at the end about adding brew to your PATH.

### 2. The toolchain

```bash
brew install php mysql python git gh
brew install --cask google-chrome
brew services start mysql
```

Check each one:

```bash
php --version        # expect 8.1 or newer
mysql --version
python3 --version    # expect 3.10 or newer
```

### 3. Get the code

```bash
gh auth login        # choose GitHub.com, HTTPS, authenticate in the browser
gh repo clone abedinm/skillbank
gh repo clone abedinm/skillbank-selenium-tests
```

### 4. Database

```bash
mysql -u root < skillbank/schema.sql
mysql -u root -e "SHOW TABLES FROM skillbank;"
```

You should see seven tables: offers, reviews, sessions, skills, transactions, users,
wishes.

If `mysql -u root` asks for a password, add `-p` to both commands and export the
credentials so PHP can connect too:

```bash
export SB_DB_USER=root
export SB_DB_PASS=yourpassword
```

### 5. Python environment

```bash
cd skillbank-selenium-tests
python3 -m venv .venv
source .venv/bin/activate
pip install selenium pillow python-docx
pip show selenium          # confirm 4.x
```

ChromeDriver is **not** a separate download. Selenium Manager, built into Selenium 4,
downloads the driver that matches your installed Chrome the first time a browser starts.

### 6. Fix the Windows paths

Two files hold Windows paths. Find the right mysql path first:

```bash
which mysql              # /opt/homebrew/bin/mysql on Apple Silicon
```

In **selenium_suite.py**:

```python
MYSQL = r"C:\xampp\mysql\bin\mysql.exe"          # before
MYSQL = "/opt/homebrew/bin/mysql"                # after
```

In **reset_db.py**:

```python
MYSQL  = r"C:\xampp\mysql\bin\mysql.exe"                      # before
SCHEMA = r"F:\outputs\aiub-webtech\skillbank\schema.sql"      # before

MYSQL  = "/opt/homebrew/bin/mysql"                            # after
SCHEMA = "../skillbank/schema.sql"                            # after (adjust to where you cloned)
```

Nothing else is platform specific. The Chrome options, the CDP screenshot calls and
every selector work identically on macOS.

### 7. Start the app

In a second terminal tab, from inside the `skillbank` folder:

```bash
php -S 127.0.0.1:8003 index.php
```

Leave it running. Check it in a browser at <http://localhost:8003> — you should see
"Browse skills" with two demo offers.

Then load <http://localhost:8003/seed.php> once to create the demo accounts:

| Email | Password | Role |
|---|---|---|
| admin@skillbank.test | password123 | admin |
| ayesha@skillbank.test | password123 | member |
| rahim@skillbank.test | password123 | member |

### 8. Run the suite

Back in the first tab, inside `skillbank-selenium-tests` with the venv active:

```bash
python reset_db.py
python selenium_suite.py
```

Expected tail:

```
40 TC_adm-07   Pass Verify a member cannot open the Manage skills page

40/40 passed
```

To watch it work in a visible browser instead of headless:

```bash
SB_HEADED=1 python selenium_suite.py
```

### 9. Build the report

```bash
python build_report.py
```

Writes `SQAT_Selenium_Report_SkillBank.docx` — roughly 68 pages, with every step
screenshot embedded and captioned.

---

## Troubleshooting

**`selenium.common.exceptions.SessionNotCreatedException`**
Chrome is missing or too old. `brew install --cask google-chrome`, or update Chrome and
run again — Selenium Manager will fetch the matching driver.

**`Database connection failed`**
MySQL is not running (`brew services start mysql`) or the root user needs a password.
Export `SB_DB_USER` and `SB_DB_PASS` before starting the PHP server, because the app
reads its credentials from those environment variables.

**Every test fails with connection refused**
The PHP server is not running on 8003, or another process owns that port:
`lsof -i :8003`.

**The login tests fail but everything else passes**
Chrome's password manager is eating the keystrokes. The suite already disables it in
`start_browser()`; make sure those `add_experimental_option("prefs", ...)` lines are
intact.

**A test fails intermittently**
It should not — the suite uses explicit `WebDriverWait` calls, not fixed sleeps. If you
see one, capture the screenshot the runner saves on failure (`<test id>_<n>.png`) and
check whether the page had actually finished loading.

**`reset_db.py` says schema load failed**
The `SCHEMA` path is wrong, or the mysql client needs `-p`. Run the same command by
hand to see the real error:
`mysql -u root < ../skillbank/schema.sql`

---

## What the suite covers

| Module | Cases | What it exercises |
|---|---|---|
| Registration | 10 | Valid signup, blank fields, duplicate email, invalid email format, password boundary at 5 and 6 characters, starting credit balance |
| Login and session | 8 | Member and admin login, wrong password, unknown email, blank fields, logout, guest hitting a protected URL |
| Skill offer CRUD | 8 | Create, validation errors, edit, deactivate, delete with confirm dialog, editing someone else's offer |
| Session booking and credits | 7 | Request, self-booking guard, accept, complete with the 1-credit transfer, review, double-review guard, cancel |
| Admin panel | 7 | Admin dashboard, member and guest blocked, user list, add skill, empty skill name, delete skill |

Twenty of the cases also verify the result directly in MySQL, so a test cannot pass on
a screen message alone.
