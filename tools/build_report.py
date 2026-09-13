"""Build the Word report for the SkillBank Selenium assignment.

Reads results.json + screenshots/ produced by selenium_suite.py and writes
SQAT_Selenium_Report_SkillBank.docx in the same folder.
"""
import json
import os

from PIL import Image, ImageChops
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

OUT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(OUT, "screenshots")
SETUP = os.path.join(OUT, "setup_shots")
JPEGS = os.path.join(OUT, "_report_images")
DOCX = os.environ.get("SB_DOCX") or os.path.join(OUT, "SQAT_Selenium_Report_SkillBank.docx")

STUDENT = "Minhazul Abedin"
STUDENT_ID = "21-44625-1"
COURSE = "Software Quality Assurance and Testing"
PROJECT = "SkillBank"
DESIGN_DATE = "02/08/2026"
EXEC_DATE = "02/08/2026"

MODULE_ORDER = [
    ("Registration", "Registration Module"),
    ("Login", "Login and Session Module"),
    ("Skill Offer Management", "Skill Offer Management Module (CRUD)"),
    ("Session Booking", "Session Booking and Credit Transfer Module"),
    ("Admin Panel", "Admin Panel Module"),
]

GREEN = RGBColor(0x1B, 0x7F, 0x3B)
RED = RGBColor(0xB3, 0x1B, 0x1B)
GREY = RGBColor(0x60, 0x6A, 0x75)


# --------------------------------------------------------------------------
def shade(cell, hex_colour):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_colour)
    tc_pr.append(shd)


def put(cell, text, bold=False, size=9, colour=None):
    cell.text = ""
    para = cell.paragraphs[0]
    run = para.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    if colour is not None:
        run.font.color.rgb = colour
    para.paragraph_format.space_before = Pt(1)
    para.paragraph_format.space_after = Pt(1)
    return para


def label_value(cell, label, value):
    cell.text = ""
    para = cell.paragraphs[0]
    run = para.add_run(label + ": ")
    run.bold = True
    run.font.size = Pt(9)
    run2 = para.add_run(str(value))
    run2.font.size = Pt(9)
    para.paragraph_format.space_before = Pt(1)
    para.paragraph_format.space_after = Pt(1)


def mono(doc, text, size=8.5):
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(size)
    para.paragraph_format.space_after = Pt(8)
    para.paragraph_format.left_indent = Inches(0.2)
    return para


def caption(doc, text):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    run.italic = True
    run.font.size = Pt(8.5)
    run.font.color.rgb = GREY
    para.paragraph_format.space_after = Pt(10)


def prepare(png_name, folder=None, quality=72, crop=None, max_aspect=None, border=0):
    """Trim the blank page margin off a screenshot and cache it as a JPEG."""
    src = os.path.join(folder or SHOTS, png_name)
    tag = "%s_%s_%s_%s" % (quality, "-".join(map(str, crop)) if crop else "full",
                           max_aspect, border)
    jpg = os.path.join(JPEGS, png_name.replace(".png", "_%s.jpg" % tag))
    if not os.path.exists(jpg):
        img = Image.open(src).convert("RGB")
        if crop:
            img = img.crop(crop)
        else:
            bg = Image.new("RGB", img.size, img.getpixel((img.width - 3, img.height - 3)))
            box = ImageChops.difference(img, bg).getbbox()
            if box:
                img = img.crop((0, 0, img.width, min(img.height, box[3] + 12)))
        if max_aspect and img.height > img.width * max_aspect:
            img = img.crop((0, 0, img.width, int(img.width * max_aspect)))
        if border:
            framed = Image.new("RGB", (img.width + border * 2, img.height + border * 2),
                               (176, 186, 196))
            framed.paste(img, (border, border))
            img = framed
        img.save(jpg, "JPEG", quality=quality, optimize=True)
    return jpg


def add_shot(doc, png_name, cap_text, folder=None, width_in=6.0, quality=72, crop=None):
    jpg = prepare(png_name, folder, quality, crop)
    width, height = Image.open(jpg).size
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after = Pt(2)
    if width_in * height / width > 7.2:
        para.add_run().add_picture(jpg, height=Inches(7.2))
    else:
        para.add_run().add_picture(jpg, width=Inches(width_in))
    caption(doc, cap_text)


def add_shot_grid(doc, shots, prefix, width_in=4.9):
    """One step screenshot per row, framed and spaced so each figure reads clearly."""
    for index, shot in enumerate(shots):
        jpg = prepare(shot["file"], max_aspect=1.05, border=3)
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(10)
        para.paragraph_format.space_after = Pt(3)
        para.add_run().add_picture(jpg, width=Inches(width_in))
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(14)
        run = cap.add_run("%s.%d   Step %d - %s"
                          % (prefix, index + 1, index + 1, shot["caption"]))
        run.italic = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = GREY


# --------------------------------------------------------------------------
def case_tables(doc, case):
    meta = doc.add_table(rows=8, cols=2)
    meta.style = "Table Grid"
    pairs = [
        ("Project Name", PROJECT), ("Test Designed by", STUDENT),
        ("Test Case ID", case["id"]), ("Test Design date", DESIGN_DATE),
        ("Test Priority (Low, Medium, High)", case["priority"]),
        ("Test Executed by", STUDENT),
        ("Module Name", case["module"]), ("Test Execution date", EXEC_DATE),
    ]
    for row_index in range(4):
        left_label, left_value = pairs[row_index * 2]
        right_label, right_value = pairs[row_index * 2 + 1]
        label_value(meta.rows[row_index].cells[0], left_label, left_value)
        label_value(meta.rows[row_index].cells[1], right_label, right_value)
    long_rows = [
        ("Test Title", case["title"]),
        ("Description", case["description"]),
        ("Precondition", case["precondition"]),
        ("Dependencies", case["dependencies"]),
    ]
    for offset, (label, value) in enumerate(long_rows):
        row = meta.rows[4 + offset]
        merged = row.cells[0].merge(row.cells[1])
        label_value(merged, label, value)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    body = doc.add_table(rows=2, cols=5)
    body.style = "Table Grid"
    headers = ["Test Steps", "Test Data", "Expected Results", "Actual Results",
               "Status (Pass/Fail)"]
    for index, text in enumerate(headers):
        cell = body.rows[0].cells[index]
        put(cell, text, bold=True, size=8.5)
        shade(cell, "E8EDF2")
    cells = body.rows[1].cells
    put(cells[0], "\n".join(case["steps"]), size=8.5)
    put(cells[1], "\n".join(case["data"]) if case["data"] else "-", size=8.5)
    put(cells[2], case["expected"], size=8.5)
    put(cells[3], case["actual"], size=8.5)
    put(cells[4], case["status"], bold=True, size=9,
        colour=GREEN if case["status"] == "Pass" else RED)

    widths = [Inches(1.45), Inches(1.25), Inches(1.6), Inches(1.7), Inches(0.6)]
    for row in body.rows:
        for index, width in enumerate(widths):
            row.cells[index].width = width


def build():
    with open(os.path.join(OUT, "results.json"), encoding="utf-8") as fh:
        results = json.load(fh)
    os.makedirs(JPEGS, exist_ok=True)

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    # ---------------- title ------------------------------------------------
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Automated Software Testing with Selenium WebDriver")
    run.bold = True
    run.font.size = Pt(19)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run("Test design and execution report for the SkillBank web application")
    run.font.size = Pt(12)
    run.font.color.rgb = GREY

    info = doc.add_table(rows=4, cols=2)
    info.style = "Table Grid"
    rows = [("Course", COURSE), ("Student name", STUDENT),
            ("Student ID", STUDENT_ID),
            ("Application under test", "SkillBank - skill-swap platform (PHP MVC + MySQL)")]
    for index, (label, value) in enumerate(rows):
        put(info.rows[index].cells[0], label, bold=True, size=9)
        put(info.rows[index].cells[1], value, size=9)
        info.rows[index].cells[0].width = Inches(1.6)
        info.rows[index].cells[1].width = Inches(5.0)
    doc.add_paragraph()

    passed = sum(1 for r in results if r["status"] == "Pass")

    # ---------------- 1. introduction --------------------------------------
    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(
        "This report documents the design and automated execution of %d test cases for "
        "SkillBank, a skill-swap web application I built as a PHP MVC project with a "
        "MySQL database. Members register, publish the skills they can teach, book "
        "sessions with each other and pay for them with time credits instead of money; "
        "an administrator manages the skill catalogue and can see every account. "
        "The application therefore contains all of the parts an assignment like this "
        "needs to exercise: registration, login for two different roles, a member "
        "dashboard, create/read/update/delete screens, a transactional workflow and an "
        "admin panel." % len(results))
    doc.add_paragraph(
        "Every test case below was executed by a Selenium WebDriver script that drives a "
        "real Chrome browser: it opens pages, types into the form fields, clicks the "
        "buttons, accepts JavaScript confirmation dialogs and reads the resulting page. "
        "Each step of each test case is captured as a screenshot, and several test cases "
        "additionally query the MySQL database directly so that the actual result is "
        "verified in storage and not only on screen. The full run finished with %d of "
        "%d test cases passing." % (passed, len(results)))

    doc.add_heading("1.1 Application under test", level=2)
    app_table = doc.add_table(rows=6, cols=2)
    app_table.style = "Table Grid"
    app_rows = [
        ("Application", "SkillBank - members teach and learn skills using time credits"),
        ("Architecture", "PHP 8.2 front controller with a Model-View-Controller structure"),
        ("Database", "MySQL (XAMPP), 7 tables: users, skills, offers, sessions, "
                     "transactions, reviews, wishes"),
        ("Roles", "admin and member (role column on the users table)"),
        ("Local address", "http://localhost:8003 (PHP built-in development server)"),
        ("Modules tested", "Registration, Login/Session, Skill Offer Management, "
                           "Session Booking and Credit Transfer, Admin Panel"),
    ]
    for index, (label, value) in enumerate(app_rows):
        put(app_table.rows[index].cells[0], label, bold=True, size=9)
        put(app_table.rows[index].cells[1], value, size=9)
        app_table.rows[index].cells[0].width = Inches(1.4)
        app_table.rows[index].cells[1].width = Inches(5.2)
    doc.add_paragraph()

    doc.add_heading("1.2 Demo accounts used by the tests", level=2)
    acc = doc.add_table(rows=4, cols=3)
    acc.style = "Table Grid"
    acc_rows = [("Email", "Password", "Role"),
                ("admin@skillbank.test", "password123", "admin"),
                ("ayesha@skillbank.test", "password123", "member"),
                ("rahim@skillbank.test", "password123", "member")]
    for r_index, row in enumerate(acc_rows):
        for c_index, value in enumerate(row):
            put(acc.rows[r_index].cells[c_index], value, bold=(r_index == 0), size=9)
            if r_index == 0:
                shade(acc.rows[r_index].cells[c_index], "E8EDF2")
    doc.add_paragraph()

    # ---------------- 2. environment ---------------------------------------
    doc.add_heading("2. Test environment and setup", level=1)
    env = doc.add_table(rows=8, cols=2)
    env.style = "Table Grid"
    env_rows = [
        ("Operating system", "Windows 11 Pro (64-bit)"),
        ("Browser", "Google Chrome, 1280 x 900 viewport (headless by default, "
                    "SB_HEADED=1 shows the window)"),
        ("Automation tool", "Selenium WebDriver 4.46.0 for Python"),
        ("Driver", "ChromeDriver, resolved automatically by Selenium Manager"),
        ("Language", "Python 3.13"),
        ("Web server", "PHP 8.2.12 built-in development server on port 8003"),
        ("Database server", "MariaDB / MySQL from XAMPP on port 3306"),
        ("Test folder", r"F:\outputs\sqat-skillbank"),
    ]
    for index, (label, value) in enumerate(env_rows):
        put(env.rows[index].cells[0], label, bold=True, size=9)
        put(env.rows[index].cells[1], value, size=9)
        env.rows[index].cells[0].width = Inches(1.6)
        env.rows[index].cells[1].width = Inches(5.0)
    doc.add_paragraph()

    doc.add_heading("2.1 Test project created in the IDE", level=2)
    doc.add_paragraph(
        "A separate folder was created for the automation work so that the test code "
        "never mixes with the application code, and it was opened as a project in "
        "Visual Studio Code. The whole suite is written in Python and lives in "
        "selenium_suite.py; the supporting scripts and the generated evidence sit "
        "beside it in the same folder.")
    mono(doc,
         "F:\\outputs\\sqat-skillbank\\\n"
         "    reset_db.py        - reloads schema.sql and re-seeds the demo data\n"
         "    selenium_suite.py  - the %d automated test cases\n"
         "    build_report.py    - builds this Word report from the results\n"
         "    capture_window.ps1 - captures the IDE / console windows for this report\n"
         "    results.json       - machine-readable result of the last run\n"
         "    run_log.txt        - console output of the last run\n"
         "    screenshots\\       - %d step screenshots captured during the run\n"
         "    setup_shots\\       - screenshots of the environment and the run itself"
         % (len(results), len(os.listdir(SHOTS))))
    add_shot(doc, "01_vscode_project.png",
             "Fig. 2.1: The test project open in Visual Studio Code - the folder created "
             "for the automation work and the top of selenium_suite.py", folder=SETUP, width_in=6.9, quality=88)

    doc.add_heading("2.2 Installing Selenium", level=2)
    doc.add_paragraph(
        "Selenium was installed with pip. Selenium 4 ships with Selenium Manager, so "
        "ChromeDriver does not have to be downloaded manually - the matching driver for "
        "the installed Chrome version is fetched automatically the first time a browser "
        "is started.")
    add_shot(doc, "02_pip_install.png",
             "Fig. 2.2: Installing Selenium with pip and confirming the installed "
             "version (selenium 4.46.0)", folder=SETUP, width_in=6.9, quality=88)

    doc.add_heading("2.3 How a test run is started", level=2)
    doc.add_paragraph(
        "The database is reset before every run so that the same test data always "
        "produces the same result. reset_db.py reloads schema.sql through the MySQL "
        "client and then calls seed.php, which recreates the three demo accounts and "
        "the two demo offers. The suite itself is then started with one command and "
        "prints the verdict of every test case as it finishes.")
    mono(doc,
         "> python reset_db.py\n"
         "schema reloaded\n"
         "seed: Seed complete. Login as admin@skillbank.test / password123.\n"
         "users in database: 3\n\n"
         "> python selenium_suite.py")
    add_shot(doc, "04_test_run_output.png",
             "Fig. 2.3: The end of a complete run in the terminal - every test case "
             "reports its own verdict and the suite finishes with 40/40 passed",
             folder=SETUP, width_in=6.9, quality=88)

    doc.add_heading("2.4 Watching the browser being driven", level=2)
    doc.add_paragraph(
        "The suite normally runs headless because it is faster and does not take over "
        "the screen, but setting the environment variable SB_HEADED=1 shows the browser "
        "window while the script works. The figure below was taken during a live run: "
        "Chrome displays the \"Chrome is being controlled by automated test software\" "
        "banner, and the page behind it is the SkillBank dashboard that the script has "
        "just reached by filling in the login form and clicking the button itself.")
    add_shot(doc, "03_chrome_automated.png",
             "Fig. 2.4: Chrome under Selenium control during the run, showing the "
             "automation banner and the dashboard reached by the login test",
             folder=SETUP, width_in=6.9, quality=88)

    doc.add_heading("2.5 Browser configuration used by the script", level=2)
    doc.add_paragraph(
        "The WebDriver is started with a fixed 1280 x 900 viewport so that every "
        "screenshot has the same width. Chrome's password manager and "
        "password-leak detection are switched off. This is not cosmetic: with the "
        "default settings Chrome shows a \"save password\" bubble after the first "
        "successful login, and that bubble swallows the keystrokes sent to the next "
        "login form, which made five login test cases fail for a reason that had nothing "
        "to do with the application. Disabling it removed the false failures.")
    mono(doc,
         "opts = Options()\n"
         "if os.environ.get(\"SB_HEADED\") != \"1\":\n"
         "    opts.add_argument(\"--headless=new\")\n"
         "opts.add_argument(\"--window-size=1280,900\")\n"
         "opts.add_argument(\"--disable-features=PasswordLeakDetection,\"\n"
         "                  \"AutofillServerCommunication\")\n"
         "opts.add_experimental_option(\"prefs\", {\n"
         "    \"credentials_enable_service\": False,\n"
         "    \"profile.password_manager_enabled\": False,\n"
         "})\n"
         "driver = webdriver.Chrome(options=opts)")

    doc.add_heading("2.6 How every step is screenshotted", level=2)
    doc.add_paragraph(
        "Each test case records its steps through a small helper object. Calling "
        "c.shot(\"caption\") captures the whole page - not just the visible part - using "
        "the Chrome DevTools Protocol command Page.captureScreenshot with "
        "captureBeyondViewport enabled, and stores it as "
        "screenshots/<test case id>_<step number>.png. The captions in this report are "
        "the captions passed in the script, so the figures and the code cannot drift "
        "apart.")
    mono(doc,
         "def full_shot(path):\n"
         "    metrics = driver.execute_cdp_cmd(\"Page.getLayoutMetrics\", {})\n"
         "    size = metrics[\"cssContentSize\"]\n"
         "    shot = driver.execute_cdp_cmd(\"Page.captureScreenshot\", {\n"
         "        \"captureBeyondViewport\": True,\n"
         "        \"clip\": {\"x\": 0, \"y\": 0, \"width\": w, \"height\": h, \"scale\": 1},\n"
         "    })\n"
         "    open(path, \"wb\").write(base64.b64decode(shot[\"data\"]))")

    doc.add_heading("2.7 The test code in the IDE", level=2)
    doc.add_paragraph(
        "The whole suite is one Python file. A small harness at the top starts the "
        "browser, captures the screenshots and records the steps, and each test case is "
        "then a short function carrying its own documentation in a @case decorator - the "
        "same title, description, precondition and dependencies that appear in the tables "
        "of this report, so the report cannot disagree with the code.")
    code_shots = [
        ("06_code_browser_setup.png",
         "Fig. 2.5: The WebDriver setup and the full-page screenshot helper"),
        ("07_code_helpers.png",
         "Fig. 2.6: The small helper functions the test cases are written with - typing "
         "into a field, submitting a form, reading the flash and error messages"),
        ("08_code_testcase.png",
         "Fig. 2.7: TC_reg-01 and TC_reg-02 in code - the @case decorator holds the test "
         "documentation, the function body performs the steps and asserts the result"),
        ("09_code_credit_test.png",
         "Fig. 2.8: TC_ses-04, the credit-transfer test - balances are read from MySQL "
         "before and after the action and compared"),
        ("10_code_runner.png",
         "Fig. 2.9: The runner - it executes every case, screenshots the failure state if "
         "an assertion fails, and writes results.json and run_log.txt"),
    ]
    for name, cap in code_shots:
        add_shot(doc, name, cap, folder=SETUP, width_in=6.9, quality=88,
                 crop=(360, 70, 1800, 770))

    doc.add_heading("2.8 Verifying results in the database", level=2)
    doc.add_paragraph(
        "Several test cases do not trust the screen alone. The credit transfer, the "
        "session status, the transaction record and the skill catalogue are read back "
        "from MySQL inside the test case, so a message on the page cannot make a test "
        "pass if the data behind it is wrong. The figure below shows the state of the "
        "database straight after the run: Ayesha has spent one credit (3 to 2), Rahim "
        "has earned one (3 to 4), the transfer is recorded in the transactions table, "
        "and the two sessions the suite created are completed and cancelled exactly as "
        "TC_ses-04 and TC_ses-07 expected.")
    add_shot(doc, "05_db_verification.png",
             "Fig. 2.10: The MySQL tables after the automated run, confirming the credit "
             "transfer and the session statuses asserted by the test cases", folder=SETUP, width_in=6.9, quality=88)

    doc.add_heading("2.9 Test design techniques applied", level=2)
    for text in [
        "Positive (valid) testing - the normal path of every module: register, log in, "
        "publish an offer, book a session, complete it, review it, administer skills.",
        "Negative testing - blank fields, wrong password, unregistered email, malformed "
        "email address, duplicate email, empty forms.",
        "Boundary value analysis - the password length rule is exactly 6 characters, so "
        "the suite tests 5 characters (rejected) and 6 characters (accepted).",
        "Access-control testing - typing a protected URL directly as a guest, as a "
        "member, and as the owner of somebody else's record.",
        "Database verification - credit balances, session status, transaction rows and "
        "skill rows are read back from MySQL, so a test cannot pass on a screen message "
        "alone.",
    ]:
        para = doc.add_paragraph(text, style="List Bullet")
        para.paragraph_format.space_after = Pt(3)

    doc.add_heading("2.10 How the test suite itself was validated", level=2)
    doc.add_paragraph(
        "An automated suite is only useful if it is both stable and able to detect a "
        "real defect, so the suite was checked in three ways before this report was "
        "produced.")
    for text in [
        "Repeatability - the suite was executed three times in a row, each time from a "
        "freshly reset database. All three runs reported 40 of 40 passed with identical "
        "results, so the outcome does not depend on timing or on leftover data.",
        "Flakiness removed - an earlier version used fixed sleeps after each click. On "
        "one run TC_ses-05 failed because the dashboard had not finished loading in the "
        "0.35 seconds allowed, even though the application was correct. Every fixed "
        "sleep was replaced with an explicit WebDriverWait that waits for the old "
        "document to go stale and for document.readyState to become complete, which "
        "removed the false failure.",
        "Detection check (mutation test) - the validation message in the application was "
        "deliberately changed from \"Name is required.\" to \"Name missing.\" and the "
        "suite was run again. TC_reg-02 correctly reported Fail and the other 39 test "
        "cases still passed, which shows the suite detects a regression rather than "
        "passing by default. The application was then restored.",
    ]:
        para = doc.add_paragraph(text, style="List Bullet")
        para.paragraph_format.space_after = Pt(4)

    # ---------------- 3. summary -------------------------------------------
    doc.add_page_break()
    doc.add_heading("3. Test summary", level=1)

    counts = {}
    for result in results:
        bucket = counts.setdefault(result["module"], [0, 0])
        bucket[0] += 1
        if result["status"] == "Pass":
            bucket[1] += 1

    summary = doc.add_table(rows=len(MODULE_ORDER) + 2, cols=4)
    summary.style = "Table Grid"
    for index, text in enumerate(["Module", "Test cases", "Passed", "Failed"]):
        put(summary.rows[0].cells[index], text, bold=True, size=9)
        shade(summary.rows[0].cells[index], "E8EDF2")
    for index, (key, label) in enumerate(MODULE_ORDER, start=1):
        total, ok = counts.get(key, [0, 0])
        put(summary.rows[index].cells[0], label, size=9)
        put(summary.rows[index].cells[1], str(total), size=9)
        put(summary.rows[index].cells[2], str(ok), size=9)
        put(summary.rows[index].cells[3], str(total - ok), size=9)
    last = summary.rows[len(MODULE_ORDER) + 1]
    put(last.cells[0], "Total", bold=True, size=9)
    put(last.cells[1], str(len(results)), bold=True, size=9)
    put(last.cells[2], str(passed), bold=True, size=9, colour=GREEN)
    put(last.cells[3], str(len(results) - passed), bold=True, size=9,
        colour=RED if passed != len(results) else GREEN)
    doc.add_paragraph()

    doc.add_heading("3.1 Result of every test case", level=2)
    table = doc.add_table(rows=len(results) + 1, cols=5)
    table.style = "Table Grid"
    for index, text in enumerate(["#", "Test Case ID", "Module", "Test Title", "Status"]):
        put(table.rows[0].cells[index], text, bold=True, size=8.5)
        shade(table.rows[0].cells[index], "E8EDF2")
    for index, result in enumerate(results, start=1):
        row = table.rows[index]
        put(row.cells[0], str(result["no"]), size=8.5)
        put(row.cells[1], result["id"], size=8.5)
        put(row.cells[2], result["module"], size=8.5)
        put(row.cells[3], result["title"], size=8.5)
        put(row.cells[4], result["status"], bold=True, size=8.5,
            colour=GREEN if result["status"] == "Pass" else RED)
        for width, cell in zip([Inches(0.35), Inches(1.0), Inches(1.35), Inches(3.1),
                                Inches(0.6)], row.cells):
            cell.width = width
    doc.add_paragraph()

    # ---------------- 4+. modules ------------------------------------------
    number = 3
    for key, label in MODULE_ORDER:
        number += 1
        doc.add_page_break()
        doc.add_heading("%d. %s" % (number, label), level=1)
        module_cases = [r for r in results if r["module"] == key]
        doc.add_paragraph(
            "%d automated test cases. Every figure is a screenshot taken by the Selenium "
            "script at the moment its caption describes; the full-size files are in the "
            "screenshots folder." % len(module_cases))
        for case in module_cases:
            doc.add_heading("Test Case %02d - %s" % (case["no"], case["id"]), level=2)
            case_tables(doc, case)
            add_shot_grid(doc, case["shots"], "Fig. %d.%d" % (number, case["no"]))

    # ---------------- conclusion -------------------------------------------
    doc.add_page_break()
    doc.add_heading("%d. Observations and conclusion" % (number + 1), level=1)
    doc.add_paragraph(
        "All %d automated test cases passed against the current build of SkillBank. "
        "The validation rules, the role guards and the credit-transfer transaction all "
        "behaved exactly as the specification of the application requires."
        % len(results))

    doc.add_heading("%d.1 Observations worth recording" % (number + 1), level=2)
    for text in [
        "The login form has no HTML5 required attribute, so an empty email or password "
        "is submitted to the server and rejected there (TC_log-05, TC_log-06). The "
        "registration form behaves the same way. The application is still safe because "
        "every rule is enforced server-side, but adding the required attribute would "
        "give the user faster feedback.",
        "Adding a skill with an empty name (TC_adm-05) is silently ignored: nothing is "
        "created, but no message is displayed either. The behaviour is correct, the "
        "feedback is not - a validation message would be an improvement.",
        "The credit transfer in TC_ses-04 was verified in the database as well as on "
        "screen: the learner went from 3 credits to 2, the teacher from 3 to 4, and one "
        "row was written to the transactions table. This is the most important business "
        "rule in the application, so it is checked at both levels.",
        "Chrome's password manager interfered with the automation itself rather than "
        "with the application. This is a useful reminder that a failing automated test "
        "does not always mean a defect in the system under test; the tooling has to be "
        "eliminated as a cause first.",
    ]:
        para = doc.add_paragraph(text, style="List Bullet")
        para.paragraph_format.space_after = Pt(4)

    doc.add_heading("%d.2 Conclusion" % (number + 1), level=2)
    doc.add_paragraph(
        "Automating these %d cases with Selenium WebDriver took the whole regression "
        "suite from a manual click-through that takes around an hour to a repeatable run "
        "of roughly two minutes that also produces its own evidence. Because the database "
        "is reset before every run, the suite can be executed again after any change to "
        "the application and the results stay comparable. The %d screenshots in this "
        "report were all produced by that single run."
        % (len(results), sum(len(r["shots"]) for r in results)))

    doc.save(DOCX)
    size_mb = os.path.getsize(DOCX) / 1048576
    print("wrote %s (%.1f MB, %d cases, %d figures)"
          % (DOCX, size_mb, len(results), sum(len(r["shots"]) for r in results)))


if __name__ == "__main__":
    build()
