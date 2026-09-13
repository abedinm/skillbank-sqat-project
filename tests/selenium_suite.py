"""SkillBank - Selenium automated test suite (SQAT assignment).

40 automated test cases across five modules: Registration, Login, Skill Offer
management, Session booking + credit transfer, and the Admin panel.

Every step of every test case is screenshotted into ./screenshots and the full
result set is written to results.json, which build_report.py turns into the
Word report.

Run order:
    python reset_db.py
    python selenium_suite.py
"""
import base64
import json
import os
import re
import subprocess

from selenium import webdriver
from selenium.common.exceptions import (NoAlertPresentException,
                                        NoSuchElementException, TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE = "http://localhost:8003"
OUT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(OUT, "screenshots")
MYSQL = r"C:\xampp\mysql\bin\mysql.exe"

DESIGNER = "Minhazul Abedin"
DESIGN_DATE = "02/08/2026"
EXEC_DATE = "02/08/2026"

driver = None
CASES = []


# --------------------------------------------------------------------------
# Test-case registration
# --------------------------------------------------------------------------
def case(cid, module, title, description, precondition, dependencies, expected,
         priority="High"):
    def deco(fn):
        CASES.append({
            "id": cid, "module": module, "title": title,
            "description": description, "precondition": precondition,
            "dependencies": dependencies, "expected": expected,
            "priority": priority, "fn": fn,
        })
        return fn
    return deco


class Ctx:
    """Collects everything the report needs about one test case."""

    def __init__(self, cid):
        self.id = cid
        self.steps = []
        self.data = []
        self.shots = []
        self.actual = ""
        self._n = 0

    def step(self, text):
        self.steps.append("%d. %s" % (len(self.steps) + 1, text))

    def datum(self, label, value):
        self.data.append("%s: %s" % (label, value))

    def shot(self, caption):
        self._n += 1
        name = "%s_%d.png" % (self.id, self._n)
        full_shot(os.path.join(SHOTS, name))
        self.shots.append({"file": name, "caption": caption})


# --------------------------------------------------------------------------
# Browser helpers
# --------------------------------------------------------------------------
def start_browser():
    global driver
    opts = Options()
    # SB_HEADED=1 shows the browser window while the suite drives it; the default
    # headless run produces exactly the same results and screenshots.
    if os.environ.get("SB_HEADED") != "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--force-device-scale-factor=1")
    opts.add_argument("--hide-scrollbars")
    # Chrome's "save password"/leak-detection bubble steals keystrokes from the
    # second login onwards, which would fail the login tests for the wrong reason.
    opts.add_argument("--disable-features=PasswordLeakDetection,AutofillServerCommunication")
    opts.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)


def full_shot(path):
    try:
        metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
        size = metrics.get("cssContentSize") or metrics["contentSize"]
        w = max(int(size["width"]), 1280)
        h = min(int(size["height"]), 2600)
        shot = driver.execute_cdp_cmd("Page.captureScreenshot", {
            "captureBeyondViewport": True,
            "clip": {"x": 0, "y": 0, "width": w, "height": h, "scale": 1},
        })
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(shot["data"]))
    except Exception:
        driver.save_screenshot(path)


WAIT = 15


def wait_ready():
    WebDriverWait(driver, WAIT).until(
        lambda d: d.execute_script("return document.readyState") == "complete")


def wait_navigation(old_html):
    """Block until the click that was just made has produced a new document."""
    try:
        WebDriverWait(driver, WAIT).until(EC.staleness_of(old_html))
    except TimeoutException:
        pass
    wait_ready()


def goto(path=""):
    driver.get(BASE + "/" + path.lstrip("/"))
    wait_ready()


def find(css):
    return WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css)))


def find_link(text):
    return WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.LINK_TEXT, text)))


def find_xpath(xpath):
    return WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, xpath)))


def maybe(css):
    els = driver.find_elements(By.CSS_SELECTOR, css)
    return els[0] if els else None


def type_in(css, value):
    el = find(css)
    el.clear()
    if value:
        el.send_keys(value)
        if el.get_attribute("value") != value:
            el.clear()
            el.send_keys(value)


def submit_form(css="button[type=submit]"):
    old_html = driver.find_element(By.TAG_NAME, "html")
    find(css).click()
    wait_navigation(old_html)


def texts(css):
    return [e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, css)]


def flash():
    el = maybe("div.flash")
    return el.text.strip() if el else ""


def errors():
    return texts("div.error")


def body_text():
    return driver.find_element(By.TAG_NAME, "body").text


def nav_text():
    return driver.find_element(By.CSS_SELECTOR, "nav.nav").text


def accept_alert():
    try:
        WebDriverWait(driver, WAIT).until(EC.alert_is_present()).accept()
        wait_ready()
        return True
    except (NoAlertPresentException, TimeoutException):
        return False


def click_button(label):
    xpath = "//button[normalize-space(text())=%s]" % xquote(label)
    old_html = driver.find_element(By.TAG_NAME, "html")
    find_xpath(xpath).click()
    wait_navigation(old_html)


def xquote(value):
    return "'%s'" % value if "'" not in value else 'concat("%s")' % value


def login(email, password):
    goto("logout")
    goto("login")
    type_in("input[name=email]", email)
    type_in("input[name=password]", password)
    submit_form()


def register(name, email, password):
    goto("register")
    type_in("input[name=name]", name)
    type_in("input[name=email]", email)
    type_in("input[name=password]", password)
    submit_form()


def offer_id(title):
    """Look up an offer id from the public browse page."""
    goto("")
    html = driver.page_source
    m = re.search(r'offer\?id=(\d+)"[^>]*>\s*' + re.escape(title), html)
    return int(m.group(1)) if m else None


def db(sql):
    proc = subprocess.run([MYSQL, "-u", "root", "-N", "-B", "-e", sql],
                          capture_output=True, text=True)
    return proc.stdout.strip()


def credits_of(email):
    value = db("SELECT credits FROM skillbank.users WHERE email='%s';" % email)
    return int(value) if value else None


# ==========================================================================
# MODULE 1 - REGISTRATION
# ==========================================================================
@case("TC_reg-01", "Registration",
      "Verify registration with valid information",
      "Verify that a new visitor can create a SkillBank account using a valid "
      "name, email and password.",
      "The registration page is reachable and the email is not already in the users table.",
      "Registration module, MySQL database, Chrome browser, PHP local server",
      "Account is created, the user is logged in automatically and the dashboard "
      "shows the welcome message with a starting balance of 3 credits.")
def reg01(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Enter valid name, email and password.")
    c.datum("Name", "Minhazul Abedin")
    c.datum("Email", "minhazul@skillbank.test")
    c.datum("Password", "abcd1234")
    type_in("input[name=name]", "Minhazul Abedin")
    type_in("input[name=email]", "minhazul@skillbank.test")
    type_in("input[name=password]", "abcd1234")
    c.shot("Valid registration data entered")
    c.step("Click Create account.")
    submit_form()
    c.shot("Dashboard reached after successful registration")
    msg = flash()
    assert "Welcome to SkillBank" in msg, "flash was %r" % msg
    assert "/dashboard" in driver.current_url
    c.actual = ("Account created. Redirected to the dashboard with the message "
                "\"%s\" and a credit balance of 3." % msg)


@case("TC_reg-02", "Registration",
      "Verify registration with an empty Name field",
      "Verify that registration is rejected when the Name field is left blank.",
      "The registration page is reachable.",
      "Registration module, Chrome browser",
      "Registration fails and the validation message \"Name is required.\" is displayed.")
def reg02(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Leave Name blank, enter a valid email and password.")
    c.datum("Name", "(blank)")
    c.datum("Email", "noname@skillbank.test")
    c.datum("Password", "abcd1234")
    type_in("input[name=name]", "")
    type_in("input[name=email]", "noname@skillbank.test")
    type_in("input[name=password]", "abcd1234")
    c.shot("Name field left blank")
    c.step("Click Create account.")
    submit_form()
    c.shot("Validation error returned by the server")
    errs = errors()
    assert "Name is required." in errs, "errors were %r" % errs
    c.actual = "Registration blocked. Error message displayed: \"Name is required.\""


@case("TC_reg-03", "Registration",
      "Verify registration with an empty Email field",
      "Verify that registration is rejected when the Email field is left blank.",
      "The registration page is reachable.",
      "Registration module, Chrome browser",
      "Registration fails and the validation message \"Email is required.\" is displayed.")
def reg03(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Enter a name and password but leave Email blank.")
    c.datum("Name", "Sabbir Ahmed")
    c.datum("Email", "(blank)")
    c.datum("Password", "abcd1234")
    type_in("input[name=name]", "Sabbir Ahmed")
    type_in("input[name=email]", "")
    type_in("input[name=password]", "abcd1234")
    c.shot("Email field left blank")
    c.step("Click Create account.")
    submit_form()
    c.shot("Validation error returned by the server")
    errs = errors()
    assert "Email is required." in errs, "errors were %r" % errs
    c.actual = "Registration blocked. Error message displayed: \"Email is required.\""


@case("TC_reg-04", "Registration",
      "Verify registration with a password shorter than 6 characters",
      "Verify that the minimum password length rule is enforced.",
      "The registration page is reachable.",
      "Registration module, Chrome browser",
      "Registration fails and the message \"Password must be at least 6 characters.\" "
      "is displayed.")
def reg04(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Enter a valid name and email with a 3-character password.")
    c.datum("Name", "Tanvir Hasan")
    c.datum("Email", "tanvir@skillbank.test")
    c.datum("Password", "123")
    type_in("input[name=name]", "Tanvir Hasan")
    type_in("input[name=email]", "tanvir@skillbank.test")
    type_in("input[name=password]", "123")
    c.shot("Short password entered")
    c.step("Click Create account.")
    submit_form()
    c.shot("Password length error displayed")
    errs = errors()
    assert "Password must be at least 6 characters." in errs, "errors were %r" % errs
    c.actual = ("Registration blocked. Error message displayed: "
                "\"Password must be at least 6 characters.\"")


@case("TC_reg-05", "Registration",
      "Verify registration with an already registered email",
      "Verify that the system prevents two accounts from sharing one email address.",
      "The email ayesha@skillbank.test already exists in the users table.",
      "Registration module, MySQL database, Chrome browser",
      "Registration fails and the message \"That email is already registered.\" is displayed.")
def reg05(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Enter a new name with an email that is already registered.")
    c.datum("Name", "Ayesha Copy")
    c.datum("Email", "ayesha@skillbank.test")
    c.datum("Password", "abcd1234")
    type_in("input[name=name]", "Ayesha Copy")
    type_in("input[name=email]", "ayesha@skillbank.test")
    type_in("input[name=password]", "abcd1234")
    c.shot("Duplicate email entered")
    c.step("Click Create account.")
    submit_form()
    c.shot("Duplicate email error displayed")
    errs = errors()
    assert "That email is already registered." in errs, "errors were %r" % errs
    c.actual = ("Registration blocked. Error message displayed: "
                "\"That email is already registered.\"")


@case("TC_reg-06", "Registration",
      "Verify registration with all fields left empty",
      "Verify that submitting a completely empty registration form returns every "
      "validation message at once.",
      "The registration page is reachable.",
      "Registration module, Chrome browser",
      "Registration fails and all three validation messages (name, email, password) "
      "are displayed together.")
def reg06(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Leave every field blank.")
    c.datum("Name", "(blank)")
    c.datum("Email", "(blank)")
    c.datum("Password", "(blank)")
    c.shot("Empty registration form")
    c.step("Click Create account.")
    submit_form()
    c.shot("All validation errors displayed")
    errs = errors()
    assert len(errs) == 3, "expected 3 errors, got %r" % errs
    c.actual = "Registration blocked. Three errors displayed: %s" % " ".join(errs)


@case("TC_reg-07", "Registration",
      "Verify registration with an invalid email format",
      "Verify that the browser blocks submission when the email address has no @ symbol.",
      "The registration page is reachable and the email input is type=\"email\".",
      "Registration module, Chrome browser (HTML5 validation)",
      "The form is not submitted and the browser reports an invalid-email validation "
      "message; the page stays on /register.")
def reg07(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Enter an email address without the @ symbol.")
    c.datum("Name", "Rifat Karim")
    c.datum("Email", "rifatgmail.com")
    c.datum("Password", "abcd1234")
    type_in("input[name=name]", "Rifat Karim")
    type_in("input[name=email]", "rifatgmail.com")
    type_in("input[name=password]", "abcd1234")
    c.shot("Malformed email entered")
    c.step("Click Create account.")
    submit_form()
    c.shot("Form not submitted - page is still the registration page")
    message = driver.execute_script(
        "return document.querySelector('input[name=email]').validationMessage;")
    assert "/register" in driver.current_url, "url was %s" % driver.current_url
    assert message, "browser reported no validation message"
    c.actual = ("Form was not submitted. Chrome reported the validation message: "
                "\"%s\" and the page stayed on /register." % message)


@case("TC_reg-08", "Registration",
      "Verify registration with a password of exactly 6 characters",
      "Boundary value test: 6 characters is the smallest accepted password.",
      "The registration page is reachable and the email is unused.",
      "Registration module, MySQL database, Chrome browser",
      "Registration succeeds and the user is taken to the dashboard.")
def reg08(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Enter valid details with a 6-character password.")
    c.datum("Name", "Mila Rahman")
    c.datum("Email", "mila@skillbank.test")
    c.datum("Password", "abc123 (6 characters)")
    type_in("input[name=name]", "Mila Rahman")
    type_in("input[name=email]", "mila@skillbank.test")
    type_in("input[name=password]", "abc123")
    c.shot("Boundary password entered")
    c.step("Click Create account.")
    submit_form()
    c.shot("Dashboard reached - boundary value accepted")
    assert "/dashboard" in driver.current_url, "url was %s" % driver.current_url
    c.actual = "Registration successful with a 6-character password; dashboard displayed."


@case("TC_reg-09", "Registration",
      "Verify registration with a password of exactly 5 characters",
      "Boundary value test: 5 characters is one below the minimum and must be rejected.",
      "The registration page is reachable.",
      "Registration module, Chrome browser",
      "Registration fails with the message \"Password must be at least 6 characters.\"")
def reg09(c):
    c.step("Open the Registration page.")
    goto("register")
    c.shot("Registration page opened")
    c.step("Enter valid details with a 5-character password.")
    c.datum("Name", "Nova Islam")
    c.datum("Email", "nova@skillbank.test")
    c.datum("Password", "abc12 (5 characters)")
    type_in("input[name=name]", "Nova Islam")
    type_in("input[name=email]", "nova@skillbank.test")
    type_in("input[name=password]", "abc12")
    c.shot("Below-boundary password entered")
    c.step("Click Create account.")
    submit_form()
    c.shot("Password length error displayed")
    errs = errors()
    assert "Password must be at least 6 characters." in errs, "errors were %r" % errs
    c.actual = ("Registration blocked at the boundary. Error message displayed: "
                "\"Password must be at least 6 characters.\"")


@case("TC_reg-10", "Registration",
      "Verify a new member receives the 3 starting credits",
      "Verify that the time-credit rule gives every new account a balance of 3 credits.",
      "The registration page is reachable and the email is unused.",
      "Registration module, MySQL database, Chrome browser",
      "The navigation bar and the dashboard both show a credit balance of 3, and the "
      "users table stores credits = 3.")
def reg10(c):
    c.step("Open the Registration page and register a new member.")
    goto("register")
    c.datum("Name", "Kamrun Nahar")
    c.datum("Email", "kamrun@skillbank.test")
    c.datum("Password", "abcd1234")
    type_in("input[name=name]", "Kamrun Nahar")
    type_in("input[name=email]", "kamrun@skillbank.test")
    type_in("input[name=password]", "abcd1234")
    c.shot("Registration data entered")
    c.step("Click Create account.")
    submit_form()
    c.shot("Dashboard showing the starting credit balance")
    c.step("Read the credit balance from the page and from the database.")
    nav = nav_text()
    stored = credits_of("kamrun@skillbank.test")
    assert "Credits: 3" in nav, "nav was %r" % nav
    assert "Credit balance:\n3" in body_text() or "Credit balance: 3" in body_text()
    assert stored == 3, "database credits = %r" % stored
    c.actual = ("Navigation shows \"Credits: 3\", the dashboard shows "
                "\"Credit balance: 3\" and the users table stores credits = 3.")


# ==========================================================================
# MODULE 2 - LOGIN
# ==========================================================================
@case("TC_log-01", "Login",
      "Verify member login with valid credentials",
      "Verify that a registered member can sign in with the correct email and password.",
      "The account ayesha@skillbank.test / password123 exists.",
      "Login module, MySQL database, Chrome browser",
      "The member is logged in and redirected to the dashboard with the message \"Logged in.\"")
def log01(c):
    c.step("Open the Login page.")
    goto("logout")
    goto("login")
    c.shot("Login page opened")
    c.step("Enter valid member credentials.")
    c.datum("Email", "ayesha@skillbank.test")
    c.datum("Password", "password123")
    type_in("input[name=email]", "ayesha@skillbank.test")
    type_in("input[name=password]", "password123")
    c.shot("Valid credentials entered")
    c.step("Click Login.")
    submit_form()
    c.shot("Dashboard reached after login")
    assert "/dashboard" in driver.current_url, "url was %s" % driver.current_url
    assert "Hi, Ayesha" in nav_text()
    c.actual = ("Login successful. Redirected to the dashboard, navigation shows "
                "\"Hi, Ayesha\" and the flash message \"Logged in.\"")


@case("TC_log-02", "Login",
      "Verify admin login and admin-only navigation link",
      "Verify that an administrator can sign in and that the Admin link appears only "
      "for the admin role.",
      "The account admin@skillbank.test / password123 exists with role = admin.",
      "Login module, role-based access control, MySQL database, Chrome browser",
      "The admin reaches the dashboard and the navigation bar contains an Admin link.")
def log02(c):
    c.step("Open the Login page.")
    goto("logout")
    goto("login")
    c.shot("Login page opened")
    c.step("Enter the administrator credentials.")
    c.datum("Email", "admin@skillbank.test")
    c.datum("Password", "password123")
    type_in("input[name=email]", "admin@skillbank.test")
    type_in("input[name=password]", "password123")
    c.shot("Administrator credentials entered")
    c.step("Click Login.")
    submit_form()
    c.shot("Dashboard with the Admin link visible in the navigation bar")
    nav = nav_text()
    assert "/dashboard" in driver.current_url
    assert "Admin" in nav, "nav was %r" % nav
    c.actual = "Admin logged in successfully and the Admin link is shown in the navigation bar."


@case("TC_log-03", "Login",
      "Verify login with a valid email and wrong password",
      "Verify that the system rejects a correct email combined with an incorrect password.",
      "The account ayesha@skillbank.test exists.",
      "Login module, MySQL database, Chrome browser",
      "Login is denied and the message \"Wrong email or password.\" is displayed.")
def log03(c):
    c.step("Open the Login page.")
    goto("logout")
    goto("login")
    c.shot("Login page opened")
    c.step("Enter a valid email with an incorrect password.")
    c.datum("Email", "ayesha@skillbank.test")
    c.datum("Password", "wrongpass")
    type_in("input[name=email]", "ayesha@skillbank.test")
    type_in("input[name=password]", "wrongpass")
    c.shot("Wrong password entered")
    c.step("Click Login.")
    submit_form()
    c.shot("Login denied with an error message")
    errs = errors()
    assert "Wrong email or password." in errs, "errors were %r" % errs
    c.actual = "Login denied. Error message displayed: \"Wrong email or password.\""


@case("TC_log-04", "Login",
      "Verify login with an unregistered email",
      "Verify that the system rejects an email address that does not exist in the database.",
      "The email nosuch@skillbank.test is not registered.",
      "Login module, MySQL database, Chrome browser",
      "Login is denied and the message \"Wrong email or password.\" is displayed.")
def log04(c):
    c.step("Open the Login page.")
    goto("logout")
    goto("login")
    c.shot("Login page opened")
    c.step("Enter an unregistered email with a valid-looking password.")
    c.datum("Email", "nosuch@skillbank.test")
    c.datum("Password", "password123")
    type_in("input[name=email]", "nosuch@skillbank.test")
    type_in("input[name=password]", "password123")
    c.shot("Unregistered email entered")
    c.step("Click Login.")
    submit_form()
    c.shot("Login denied with an error message")
    errs = errors()
    assert "Wrong email or password." in errs, "errors were %r" % errs
    c.actual = "Login denied. Error message displayed: \"Wrong email or password.\""


@case("TC_log-05", "Login",
      "Verify login with an empty Email field",
      "Verify that the login form cannot be used with a blank email address.",
      "The login page is reachable.",
      "Login module, Chrome browser",
      "Login is denied and the message \"Wrong email or password.\" is displayed.")
def log05(c):
    c.step("Open the Login page.")
    goto("logout")
    goto("login")
    c.shot("Login page opened")
    c.step("Leave Email blank and enter a password.")
    c.datum("Email", "(blank)")
    c.datum("Password", "password123")
    type_in("input[name=email]", "")
    type_in("input[name=password]", "password123")
    c.shot("Email field left blank")
    c.step("Click Login.")
    submit_form()
    c.shot("Login denied with an error message")
    errs = errors()
    assert "Wrong email or password." in errs, "errors were %r" % errs
    c.actual = ("Login denied. The server returned \"Wrong email or password.\" "
                "Note: the email input has no HTML5 required attribute, so the browser "
                "allows the empty submission and the check happens on the server.")


@case("TC_log-06", "Login",
      "Verify login with an empty Password field",
      "Verify that the login form cannot be used with a blank password.",
      "The account ayesha@skillbank.test exists.",
      "Login module, Chrome browser",
      "Login is denied and the message \"Wrong email or password.\" is displayed.")
def log06(c):
    c.step("Open the Login page.")
    goto("logout")
    goto("login")
    c.shot("Login page opened")
    c.step("Enter a valid email and leave Password blank.")
    c.datum("Email", "ayesha@skillbank.test")
    c.datum("Password", "(blank)")
    type_in("input[name=email]", "ayesha@skillbank.test")
    type_in("input[name=password]", "")
    c.shot("Password field left blank")
    c.step("Click Login.")
    submit_form()
    c.shot("Login denied with an error message")
    errs = errors()
    assert "Wrong email or password." in errs, "errors were %r" % errs
    c.actual = "Login denied. Error message displayed: \"Wrong email or password.\""


@case("TC_log-07", "Login",
      "Verify logout ends the session",
      "Verify that after logging out the session is destroyed and the member links "
      "disappear from the navigation bar.",
      "A member is logged in.",
      "Login module, PHP session handling, Chrome browser",
      "The navigation bar shows Login and Register again and the dashboard is no "
      "longer reachable.")
def log07(c):
    c.step("Log in as a member.")
    login("ayesha@skillbank.test", "password123")
    c.datum("Email", "ayesha@skillbank.test")
    c.datum("Password", "password123")
    c.shot("Logged in - navigation shows Dashboard and Logout")
    c.step("Click Logout.")
    goto("logout")
    c.shot("Logged out - navigation shows Login and Register")
    c.step("Try to open the dashboard again.")
    goto("dashboard")
    c.shot("Dashboard blocked after logout")
    nav = nav_text()
    assert "Logout" not in nav, "nav was %r" % nav
    assert "/login" in driver.current_url, "url was %s" % driver.current_url
    c.actual = ("Session destroyed. The navigation bar shows Login and Register, and "
                "opening /dashboard redirects to the login page.")


@case("TC_log-08", "Login",
      "Verify a guest cannot open the dashboard directly",
      "Verify that the require_login guard protects the dashboard URL against a user "
      "who is not signed in.",
      "No user is logged in.",
      "Login module, access-control guard, Chrome browser",
      "The user is redirected to the login page with the message \"Please log in first.\"")
def log08(c):
    c.step("Make sure no user is logged in.")
    goto("logout")
    c.shot("Logged out state")
    c.step("Type the protected dashboard URL directly in the address bar.")
    c.datum("URL", BASE + "/dashboard")
    goto("dashboard")
    c.shot("Redirected to the login page with a warning message")
    assert "/login" in driver.current_url, "url was %s" % driver.current_url
    assert "Please log in first." in flash(), "flash was %r" % flash()
    c.actual = ("Access blocked. The browser was redirected to /login and the message "
                "\"Please log in first.\" was displayed.")


# ==========================================================================
# MODULE 3 - SKILL OFFER MANAGEMENT (CRUD)
# ==========================================================================
@case("TC_off-01", "Skill Offer Management",
      "Verify creating a skill offer with valid information",
      "Verify that a logged-in member can publish a new skill offer.",
      "The member ayesha@skillbank.test is logged in and the skill catalogue is not empty.",
      "Offer module, MySQL database, Chrome browser, PHP local server",
      "The offer is created, the message \"Offer created.\" is shown and the offer "
      "appears in the member's dashboard table.")
def off01(c):
    c.step("Log in as a member and open the Offer a skill page.")
    login("ayesha@skillbank.test", "password123")
    goto("offers/create")
    c.shot("Offer a skill form opened")
    c.step("Choose a skill and fill in the offer details.")
    c.datum("Skill", "Web Development (Programming)")
    c.datum("Title", "Build your first website")
    c.datum("Description", "HTML, CSS and a live page in one sitting.")
    c.datum("Level", "Intermediate")
    Select(find("select[name=skill_id]")).select_by_visible_text("Web Development (Programming)")
    type_in("input[name=title]", "Build your first website")
    type_in("textarea[name=description]", "HTML, CSS and a live page in one sitting.")
    Select(find("select[name=level]")).select_by_visible_text("Intermediate")
    c.shot("Valid offer data entered")
    c.step("Click Create offer.")
    submit_form()
    c.shot("Dashboard showing the newly created offer")
    assert "Offer created." in flash(), "flash was %r" % flash()
    assert "Build your first website" in body_text()
    c.actual = ("Offer created successfully. The message \"Offer created.\" was shown and "
                "the offer is listed in My skill offers with status active.")


@case("TC_off-02", "Skill Offer Management",
      "Verify creating an offer with an empty Title",
      "Verify that an offer cannot be published without a title.",
      "The member ayesha@skillbank.test is logged in.",
      "Offer module, Chrome browser",
      "The offer is not created and the message \"Title is required.\" is displayed.")
def off02(c):
    c.step("Log in as a member and open the Offer a skill page.")
    login("ayesha@skillbank.test", "password123")
    goto("offers/create")
    c.shot("Offer a skill form opened")
    c.step("Choose a skill but leave the Title empty.")
    c.datum("Skill", "Guitar (Music)")
    c.datum("Title", "(blank)")
    c.datum("Level", "Beginner")
    Select(find("select[name=skill_id]")).select_by_visible_text("Guitar (Music)")
    type_in("input[name=title]", "")
    c.shot("Title left blank")
    c.step("Click Create offer.")
    submit_form()
    c.shot("Validation error displayed")
    errs = errors()
    assert "Title is required." in errs, "errors were %r" % errs
    c.actual = "Offer not created. Error message displayed: \"Title is required.\""


@case("TC_off-03", "Skill Offer Management",
      "Verify creating an offer without choosing a skill",
      "Verify that the skill dropdown must be used before an offer can be published.",
      "The member ayesha@skillbank.test is logged in.",
      "Offer module, Chrome browser",
      "The offer is not created and the message \"Choose a skill.\" is displayed.")
def off03(c):
    c.step("Log in as a member and open the Offer a skill page.")
    login("ayesha@skillbank.test", "password123")
    goto("offers/create")
    c.shot("Offer a skill form opened")
    c.step("Leave the skill dropdown on \"-- choose --\" and enter a title.")
    c.datum("Skill", "-- choose -- (nothing selected)")
    c.datum("Title", "Cooking for students")
    Select(find("select[name=skill_id]")).select_by_visible_text("-- choose --")
    type_in("input[name=title]", "Cooking for students")
    c.shot("No skill selected")
    c.step("Click Create offer.")
    submit_form()
    c.shot("Validation error displayed")
    errs = errors()
    assert "Choose a skill." in errs, "errors were %r" % errs
    c.actual = "Offer not created. Error message displayed: \"Choose a skill.\""


@case("TC_off-04", "Skill Offer Management",
      "Verify creating an offer with an empty form",
      "Verify that both offer validation rules fire together on an empty form.",
      "The member ayesha@skillbank.test is logged in.",
      "Offer module, Chrome browser",
      "The offer is not created and both \"Choose a skill.\" and \"Title is required.\" "
      "are displayed.")
def off04(c):
    c.step("Log in as a member and open the Offer a skill page.")
    login("ayesha@skillbank.test", "password123")
    goto("offers/create")
    c.shot("Empty Offer a skill form")
    c.step("Click Create offer without entering anything.")
    submit_form()
    c.shot("Both validation errors displayed")
    errs = errors()
    assert "Choose a skill." in errs and "Title is required." in errs, "errors were %r" % errs
    c.actual = ("Offer not created. Both error messages displayed: \"Choose a skill.\" "
                "and \"Title is required.\"")


@case("TC_off-05", "Skill Offer Management",
      "Verify editing an existing offer",
      "Verify that the owner of an offer can change its title.",
      "The offer \"Build your first website\" created in TC_off-01 exists and belongs "
      "to ayesha@skillbank.test.",
      "Offer module, MySQL database, Chrome browser",
      "The offer is updated, the message \"Offer updated.\" is shown and the new title "
      "appears in the dashboard.")
def off05(c):
    c.step("Log in as the owner and open the dashboard.")
    login("ayesha@skillbank.test", "password123")
    c.shot("Dashboard listing My skill offers")
    c.step("Click Edit on the offer created in TC_off-01.")
    oid = db("SELECT id FROM skillbank.offers WHERE title='Build your first website' LIMIT 1;")
    goto("offers/edit?id=" + oid)
    c.shot("Edit offer form opened")
    c.step("Change the title and save.")
    c.datum("Old title", "Build your first website")
    c.datum("New title", "Build your first website in one day")
    type_in("input[name=title]", "Build your first website in one day")
    c.shot("New title entered")
    submit_form()
    c.shot("Dashboard showing the updated offer")
    assert "Offer updated." in flash(), "flash was %r" % flash()
    assert "Build your first website in one day" in body_text()
    c.actual = ("Offer updated successfully. The message \"Offer updated.\" was shown and "
                "the dashboard lists the new title.")


@case("TC_off-06", "Skill Offer Management",
      "Verify deactivating an offer removes it from the public list",
      "Verify that setting an offer's status to inactive hides it from the Browse page "
      "while keeping it on the owner's dashboard.",
      "The offer edited in TC_off-05 exists and is active.",
      "Offer module, MySQL database, Chrome browser",
      "The dashboard shows status inactive and the offer no longer appears on the "
      "public Browse page.")
def off06(c):
    c.step("Log in as the owner and open the edit form for the offer.")
    login("ayesha@skillbank.test", "password123")
    oid = db("SELECT id FROM skillbank.offers WHERE title='Build your first website in one day' LIMIT 1;")
    goto("offers/edit?id=" + oid)
    c.shot("Edit offer form opened")
    c.step("Change Status from active to inactive and save.")
    c.datum("Status", "inactive")
    Select(find("select[name=status]")).select_by_visible_text("inactive")
    c.shot("Status set to inactive")
    submit_form()
    c.shot("Dashboard showing the offer as inactive")
    c.step("Open the public Browse page and check the offer is hidden.")
    goto("")
    c.shot("Browse page no longer lists the inactive offer")
    assert "Build your first website in one day" not in body_text(), "offer still public"
    status = db("SELECT status FROM skillbank.offers WHERE id=%s;" % oid)
    assert status == "inactive", "database status = %r" % status
    c.actual = ("Offer status changed to inactive in the database and the offer is no "
                "longer listed on the public Browse page.")


@case("TC_off-07", "Skill Offer Management",
      "Verify deleting an offer",
      "Verify that the owner can permanently delete an offer through the confirmation "
      "dialog.",
      "The offer created in TC_off-01 still exists.",
      "Offer module, MySQL database, Chrome browser (JavaScript confirm dialog)",
      "The confirmation dialog appears, the message \"Offer deleted.\" is shown and the "
      "offer disappears from the dashboard and the database.")
def off07(c):
    c.step("Log in as the owner and open the dashboard.")
    login("ayesha@skillbank.test", "password123")
    c.shot("Dashboard before deletion")
    c.step("Click Delete on the offer and accept the confirmation dialog.")
    old_html = driver.find_element(By.TAG_NAME, "html")
    find_xpath("//tr[td[contains(text(),'Build your first website in one day')]]"
               "//button[text()='Delete']").click()
    accepted = accept_alert()
    wait_navigation(old_html)
    c.shot("Dashboard after deletion")
    left = db("SELECT COUNT(*) FROM skillbank.offers WHERE title='Build your first website in one day';")
    assert accepted, "no confirmation dialog appeared"
    assert "Offer deleted." in flash(), "flash was %r" % flash()
    assert left == "0", "rows left = %r" % left
    c.actual = ("Confirmation dialog appeared and was accepted. The message \"Offer "
                "deleted.\" was shown and the row was removed from the offers table.")


@case("TC_off-08", "Skill Offer Management",
      "Verify a member cannot edit another member's offer",
      "Verify that the ownership guard blocks a member who types another member's "
      "offer id into the edit URL.",
      "Rahim owns the offer \"Acoustic guitar for starters\" and Ayesha is logged in.",
      "Offer module, ownership guard, Chrome browser",
      "The edit form is not shown; the user is redirected to the dashboard with the "
      "message \"Offer not found or not yours.\"")
def off08(c):
    c.step("Find the offer id that belongs to the other member.")
    oid = db("SELECT id FROM skillbank.offers WHERE title='Acoustic guitar for starters' LIMIT 1;")
    c.datum("Offer owner", "Rahim (rahim@skillbank.test)")
    c.datum("URL requested", BASE + "/offers/edit?id=" + oid)
    c.step("Log in as a different member.")
    login("ayesha@skillbank.test", "password123")
    c.shot("Logged in as Ayesha")
    c.step("Type the other member's edit URL directly in the address bar.")
    goto("offers/edit?id=" + oid)
    c.shot("Access blocked and redirected to the dashboard")
    assert "/dashboard" in driver.current_url, "url was %s" % driver.current_url
    assert "not yours" in flash(), "flash was %r" % flash()
    c.actual = ("Access blocked. Redirected to the dashboard with the message "
                "\"Offer not found or not yours.\"")


# ==========================================================================
# MODULE 4 - SESSION BOOKING AND CREDIT TRANSFER
# ==========================================================================
@case("TC_ses-01", "Session Booking",
      "Verify a member can request a session on another member's offer",
      "Verify the booking flow: a learner requests a session and it becomes a pending "
      "booking for the teacher.",
      "Ayesha is logged in with at least 1 credit and Rahim's guitar offer is active.",
      "Session module, MySQL database, Chrome browser, PHP local server",
      "The message \"Request sent! The teacher will accept it.\" is shown and the "
      "session is stored with status pending.")
def ses01(c):
    c.step("Log in as the learner and open the teacher's offer page.")
    login("ayesha@skillbank.test", "password123")
    oid = offer_id("Acoustic guitar for starters")
    goto("offer?id=%d" % oid)
    c.shot("Offer page with the request form")
    c.step("Pick a preferred time and submit the request.")
    c.datum("Offer", "Acoustic guitar for starters (teacher: Rahim)")
    c.datum("Preferred time", "2026-08-10 15:00")
    driver.execute_script(
        "document.querySelector('input[name=scheduled_at]').value='2026-08-10T15:00';")
    c.shot("Preferred time selected")
    submit_form()
    c.shot("Request confirmation message")
    status = db("SELECT status FROM skillbank.sessions ORDER BY id DESC LIMIT 1;")
    assert "Request sent!" in flash(), "flash was %r" % flash()
    assert status == "pending", "database status = %r" % status
    c.actual = ("Request sent. The message \"Request sent! The teacher will accept it.\" "
                "was shown and the sessions table stores the booking with status pending.")


@case("TC_ses-02", "Session Booking",
      "Verify a member cannot book their own offer",
      "Verify that the booking form is hidden on an offer that belongs to the logged-in "
      "member, so nobody can spend credits on themselves.",
      "Ayesha owns the offer \"Learn Python basics\" and is logged in.",
      "Session module, ownership guard, Chrome browser",
      "No request form is rendered on the member's own offer page.")
def ses02(c):
    c.step("Log in as the owner of the offer.")
    login("ayesha@skillbank.test", "password123")
    c.step("Open the member's own offer page.")
    oid = offer_id("Learn Python basics")
    c.datum("Offer", "Learn Python basics (owner: Ayesha)")
    goto("offer?id=%d" % oid)
    c.shot("Own offer page - no request form is shown")
    buttons = [b.text for b in driver.find_elements(By.CSS_SELECTOR, "form.form button")]
    assert not any("Request session" in b for b in buttons), "buttons were %r" % buttons
    c.actual = ("The \"Request session\" form is not rendered on the member's own offer "
                "page, so a self-booking cannot be submitted from the interface.")


@case("TC_ses-03", "Session Booking",
      "Verify the teacher can accept a pending request",
      "Verify that the teacher sees the pending booking and can move it to accepted.",
      "The pending session created in TC_ses-01 exists and Rahim is the teacher.",
      "Session module, MySQL database, Chrome browser",
      "The message \"Session accepted.\" is shown and the session status becomes accepted.")
def ses03(c):
    c.step("Log in as the teacher and open the dashboard.")
    login("rahim@skillbank.test", "password123")
    c.shot("Teacher dashboard showing the pending request")
    c.step("Click Accept on the pending booking.")
    c.datum("Learner", "Ayesha")
    c.datum("Action", "Accept")
    click_button("Accept")
    c.shot("Dashboard after accepting the request")
    status = db("SELECT status FROM skillbank.sessions ORDER BY id DESC LIMIT 1;")
    assert "Session accepted." in flash(), "flash was %r" % flash()
    assert status == "accepted", "database status = %r" % status
    c.actual = ("Request accepted. The message \"Session accepted.\" was shown and the "
                "session status changed to accepted.")


@case("TC_ses-04", "Session Booking",
      "Verify completing a session transfers exactly one credit",
      "Verify the core time-banking rule: completing a session moves 1 credit from the "
      "learner to the teacher.",
      "The accepted session from TC_ses-03 exists; Ayesha has 3 credits and Rahim has 3.",
      "Session module, credit transfer transaction, MySQL database, Chrome browser",
      "The learner's balance drops by 1, the teacher's balance rises by 1 and a row is "
      "written to the transactions table.")
def ses04(c):
    c.step("Read both credit balances before completing the session.")
    before_learner = credits_of("ayesha@skillbank.test")
    before_teacher = credits_of("rahim@skillbank.test")
    c.datum("Learner balance before", before_learner)
    c.datum("Teacher balance before", before_teacher)
    c.step("Log in as the teacher and open the dashboard.")
    login("rahim@skillbank.test", "password123")
    c.shot("Teacher dashboard before completing (balance %d)" % before_teacher)
    c.step("Click \"Mark completed (+1)\".")
    click_button("Mark completed (+1)")
    c.shot("Dashboard after completion - teacher balance increased")
    after_learner = credits_of("ayesha@skillbank.test")
    after_teacher = credits_of("rahim@skillbank.test")
    tx = db("SELECT COUNT(*) FROM skillbank.transactions;")
    assert "1 credit transferred" in flash(), "flash was %r" % flash()
    assert after_learner == before_learner - 1, "learner %s -> %s" % (before_learner, after_learner)
    assert after_teacher == before_teacher + 1, "teacher %s -> %s" % (before_teacher, after_teacher)
    assert tx != "0", "no transaction row written"
    c.actual = ("Session completed. Learner balance %d -> %d, teacher balance %d -> %d, "
                "and %s row(s) recorded in the transactions table."
                % (before_learner, after_learner, before_teacher, after_teacher, tx))


@case("TC_ses-05", "Session Booking",
      "Verify the learner can review a completed session",
      "Verify that after completion the learner can leave a 1-5 star review that appears "
      "on the offer page.",
      "The session completed in TC_ses-04 exists and has not been reviewed.",
      "Review module, MySQL database, Chrome browser",
      "The message \"Thanks for your review!\" is shown and the offer page displays the "
      "new rating.")
def ses05(c):
    c.step("Log in as the learner and open the dashboard.")
    login("ayesha@skillbank.test", "password123")
    c.shot("Dashboard showing the completed booking with a Leave review link")
    c.step("Click Leave review.")
    old_html = driver.find_element(By.TAG_NAME, "html")
    find_link("Leave review").click()
    wait_navigation(old_html)
    c.shot("Review form opened")
    c.step("Choose a rating, write a comment and submit.")
    c.datum("Rating", "5 - Excellent")
    c.datum("Comment", "Very clear lesson, learned three chords.")
    Select(find("select[name=rating]")).select_by_visible_text("5 - Excellent")
    type_in("textarea[name=comment]", "Very clear lesson, learned three chords.")
    c.shot("Review filled in")
    submit_form()
    c.shot("Dashboard after submitting the review")
    c.step("Open the offer page and confirm the rating is published.")
    oid = offer_id("Acoustic guitar for starters")
    goto("offer?id=%d" % oid)
    c.shot("Offer page showing the published rating")
    assert "Rating:" in body_text() and "5.0" in body_text(), "offer page has no rating"
    c.actual = ("Review saved. The message \"Thanks for your review!\" was shown and the "
                "offer page now displays \"Rating: 5.0 / 5 (1 review)\".")


@case("TC_ses-06", "Session Booking",
      "Verify the same session cannot be reviewed twice",
      "Verify that the review guard blocks a second review even when the review URL is "
      "typed manually.",
      "The session reviewed in TC_ses-05 already has one review.",
      "Review module, access guard, Chrome browser",
      "The review form is not shown; the user is redirected to the dashboard with the "
      "message \"You cannot review that session.\"")
def ses06(c):
    c.step("Log in as the learner.")
    login("ayesha@skillbank.test", "password123")
    c.step("Find the id of the already-reviewed session and open its review URL.")
    sid = db("SELECT session_id FROM skillbank.reviews ORDER BY id DESC LIMIT 1;")
    c.datum("URL requested", BASE + "/sessions/review?id=" + sid)
    goto("sessions/review?id=" + sid)
    c.shot("Second review blocked and redirected to the dashboard")
    assert "/dashboard" in driver.current_url, "url was %s" % driver.current_url
    assert "cannot review" in flash(), "flash was %r" % flash()
    c.actual = ("Second review blocked. Redirected to the dashboard with the message "
                "\"You cannot review that session.\"")


@case("TC_ses-07", "Session Booking",
      "Verify a pending booking can be cancelled",
      "Verify that a learner can cancel a booking that the teacher has not accepted yet.",
      "Ayesha is logged in and has at least 1 credit.",
      "Session module, MySQL database, Chrome browser",
      "The message \"Session cancelled.\" is shown and the session status becomes cancelled.")
def ses07(c):
    c.step("Log in as the learner and request a new session.")
    login("ayesha@skillbank.test", "password123")
    oid = offer_id("Acoustic guitar for starters")
    goto("offer?id=%d" % oid)
    submit_form()
    c.datum("Offer", "Acoustic guitar for starters (teacher: Rahim)")
    c.shot("New pending request created")
    c.step("Open the dashboard and click Cancel on the pending booking.")
    goto("dashboard")
    c.shot("Dashboard showing the pending booking")
    click_button("Cancel")
    c.shot("Dashboard after cancelling")
    status = db("SELECT status FROM skillbank.sessions ORDER BY id DESC LIMIT 1;")
    assert "Session cancelled." in flash(), "flash was %r" % flash()
    assert status == "cancelled", "database status = %r" % status
    c.actual = ("Booking cancelled. The message \"Session cancelled.\" was shown and the "
                "session status changed to cancelled.")


# ==========================================================================
# MODULE 5 - ADMIN PANEL
# ==========================================================================
@case("TC_adm-01", "Admin Panel",
      "Verify the administrator can open the admin dashboard",
      "Verify that a user with role = admin can reach /admin and see the platform "
      "statistics.",
      "The admin account exists and is logged in.",
      "Admin module, role-based access control, MySQL database, Chrome browser",
      "The admin dashboard opens and shows the Users, Offers and Completed sessions "
      "counters plus the full user table.")
def adm01(c):
    c.step("Log in as the administrator.")
    login("admin@skillbank.test", "password123")
    c.shot("Logged in as administrator")
    c.step("Click the Admin link in the navigation bar.")
    old_html = driver.find_element(By.TAG_NAME, "html")
    find_link("Admin").click()
    wait_navigation(old_html)
    c.shot("Admin dashboard with statistics and the user table")
    text = body_text()
    assert "Admin dashboard" in text, "page text was %r" % text[:120]
    assert "Users" in text and "All users" in text
    c.actual = ("Admin dashboard opened successfully showing the Users / Offers / "
                "Completed sessions counters and the All users table.")


@case("TC_adm-02", "Admin Panel",
      "Verify a normal member cannot open the admin dashboard",
      "Verify that the require_admin guard blocks a member who types the /admin URL.",
      "A member (not an admin) is logged in.",
      "Admin module, role-based access control, Chrome browser",
      "The member is redirected to the Browse page with the message \"Admins only.\"")
def adm02(c):
    c.step("Log in as a normal member.")
    login("ayesha@skillbank.test", "password123")
    c.shot("Logged in as a normal member - no Admin link in the navigation bar")
    c.step("Type the admin URL directly in the address bar.")
    c.datum("URL requested", BASE + "/admin")
    goto("admin")
    c.shot("Access blocked and redirected to the Browse page")
    assert "Admins only." in flash(), "flash was %r" % flash()
    assert "/admin" not in driver.current_url
    c.actual = ("Access blocked. Redirected to the Browse page with the message "
                "\"Admins only.\"")


@case("TC_adm-03", "Admin Panel",
      "Verify a newly registered member appears in the admin user list",
      "Verify that the account created in TC_reg-01 is visible to the administrator "
      "with the correct role and credit balance.",
      "TC_reg-01 has been executed and the admin is logged in.",
      "Admin module, MySQL database, Chrome browser",
      "The All users table contains minhazul@skillbank.test with role member and 3 credits.")
def adm03(c):
    c.step("Log in as the administrator and open the admin dashboard.")
    login("admin@skillbank.test", "password123")
    goto("admin")
    c.shot("Admin dashboard user table")
    c.step("Look up the account registered in TC_reg-01.")
    c.datum("Email searched", "minhazul@skillbank.test")
    row = driver.find_element(
        By.XPATH, "//tr[td[contains(text(),'minhazul@skillbank.test')]]").text
    assert "member" in row, "row was %r" % row
    c.actual = "The user table contains the row: %s" % row.replace("\n", " | ")


@case("TC_adm-04", "Admin Panel",
      "Verify the administrator can add a new skill to the catalogue",
      "Verify skill creation from the Manage skills page.",
      "The admin is logged in and the skill does not already exist.",
      "Admin module, MySQL database, Chrome browser",
      "The message \"Skill added.\" is shown and the new skill appears in the table.")
def adm04(c):
    c.step("Log in as the administrator and open Manage skills.")
    login("admin@skillbank.test", "password123")
    goto("admin/skills")
    c.shot("Manage skills page opened")
    c.step("Enter a new skill name and category.")
    c.datum("Skill name", "Data Analysis")
    c.datum("Category", "Programming")
    type_in("input[name=name]", "Data Analysis")
    type_in("input[name=category]", "Programming")
    c.shot("New skill details entered")
    c.step("Click Add skill.")
    submit_form("button[name=add]")
    c.shot("Skill list containing the new skill")
    assert "Skill added." in flash(), "flash was %r" % flash()
    assert "Data Analysis" in body_text()
    c.actual = ("Skill created. The message \"Skill added.\" was shown and \"Data Analysis "
                "/ Programming\" now appears in the skills table.")


@case("TC_adm-05", "Admin Panel",
      "Verify adding a skill with an empty name is ignored",
      "Verify that submitting the Add skill form with a blank name does not create an "
      "empty catalogue entry.",
      "The admin is logged in on the Manage skills page.",
      "Admin module, MySQL database, Chrome browser",
      "No skill is created and the number of rows in the skills table is unchanged.")
def adm05(c):
    c.step("Log in as the administrator and open Manage skills.")
    login("admin@skillbank.test", "password123")
    goto("admin/skills")
    before = db("SELECT COUNT(*) FROM skillbank.skills;")
    c.datum("Skill name", "(blank)")
    c.datum("Category", "General")
    c.datum("Skills before", before)
    c.shot("Manage skills page with %s skills" % before)
    c.step("Leave the skill name blank, type only a category and click Add skill.")
    type_in("input[name=name]", "")
    type_in("input[name=category]", "General")
    c.shot("Blank skill name entered")
    submit_form("button[name=add]")
    after = db("SELECT COUNT(*) FROM skillbank.skills;")
    c.shot("Skill list unchanged after the empty submission")
    assert after == before, "%s -> %s" % (before, after)
    assert flash() == "", "unexpected flash %r" % flash()
    c.actual = ("No skill was created. The table still holds %s skills and no success "
                "message was displayed." % after)


@case("TC_adm-06", "Admin Panel",
      "Verify the administrator can delete a skill",
      "Verify skill deletion through the confirmation dialog on the Manage skills page.",
      "The skill \"Data Analysis\" created in TC_adm-04 exists.",
      "Admin module, MySQL database, Chrome browser (JavaScript confirm dialog)",
      "The confirmation dialog appears, the message \"Skill deleted.\" is shown and the "
      "row disappears from the table.")
def adm06(c):
    c.step("Log in as the administrator and open Manage skills.")
    login("admin@skillbank.test", "password123")
    goto("admin/skills")
    c.shot("Manage skills page before deletion")
    c.step("Click Delete on the \"Data Analysis\" row and accept the dialog.")
    c.datum("Skill deleted", "Data Analysis")
    old_html = driver.find_element(By.TAG_NAME, "html")
    find_xpath("//tr[td[normalize-space(text())='Data Analysis']]"
               "//button[text()='Delete']").click()
    accepted = accept_alert()
    wait_navigation(old_html)
    c.shot("Skill list after deletion")
    left = db("SELECT COUNT(*) FROM skillbank.skills WHERE name='Data Analysis';")
    assert accepted, "no confirmation dialog appeared"
    assert "Skill deleted." in flash(), "flash was %r" % flash()
    assert left == "0", "rows left = %r" % left
    c.actual = ("Confirmation dialog appeared and was accepted. The message \"Skill "
                "deleted.\" was shown and the row was removed from the skills table.")


@case("TC_adm-07", "Admin Panel",
      "Verify a member cannot open the Manage skills page",
      "Verify that the second admin route is protected by the same role guard.",
      "A member (not an admin) is logged in.",
      "Admin module, role-based access control, Chrome browser",
      "The member is redirected to the Browse page with the message \"Admins only.\"")
def adm07(c):
    c.step("Log in as a normal member.")
    login("ayesha@skillbank.test", "password123")
    c.shot("Logged in as a normal member")
    c.step("Type the Manage skills URL directly in the address bar.")
    c.datum("URL requested", BASE + "/admin/skills")
    goto("admin/skills")
    c.shot("Access blocked and redirected to the Browse page")
    assert "Admins only." in flash(), "flash was %r" % flash()
    assert "admin/skills" not in driver.current_url
    c.actual = ("Access blocked. Redirected to the Browse page with the message "
                "\"Admins only.\"")


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------
def main():
    if os.path.isdir(SHOTS):
        for name in os.listdir(SHOTS):
            os.remove(os.path.join(SHOTS, name))
    else:
        os.makedirs(SHOTS)

    start_browser()
    results = []
    log = ["SkillBank - Selenium test run", "python selenium_suite.py", ""]
    passed = 0
    try:
        for index, meta in enumerate(CASES, start=1):
            ctx = Ctx(meta["id"])
            status, note = "Pass", ""
            try:
                meta["fn"](ctx)
            except AssertionError as ex:
                status, note = "Fail", str(ex)
            except Exception as ex:
                status, note = "Fail", "%s: %s" % (type(ex).__name__, ex)
            if status == "Fail":
                try:
                    ctx.shot("State when the check failed")
                except Exception:
                    pass
                ctx.actual = (ctx.actual or "") + (" FAILED: %s" % note)
            else:
                passed += 1
            results.append({
                "no": index,
                "id": meta["id"],
                "module": meta["module"],
                "title": meta["title"],
                "description": meta["description"],
                "precondition": meta["precondition"],
                "dependencies": meta["dependencies"],
                "priority": meta["priority"],
                "designer": DESIGNER,
                "design_date": DESIGN_DATE,
                "exec_date": EXEC_DATE,
                "steps": ctx.steps,
                "data": ctx.data,
                "expected": meta["expected"],
                "actual": ctx.actual.strip(),
                "status": status,
                "shots": ctx.shots,
            })
            line = "%-2d %-11s %-4s %s" % (index, meta["id"], status, meta["title"])
            log.append(line)
            print(line)
    finally:
        driver.quit()

    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    summary = "%d/%d passed" % (passed, len(results))
    log.append("")
    log.append(summary)
    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    print("\n" + summary)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
