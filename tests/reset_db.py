"""Reset the SkillBank database to a known state before a test run.

Drops + recreates the schema, then calls seed.php through the running app so the
demo accounts (admin / Ayesha / Rahim, password123) and demo offers exist again.
Run this first so every execution of selenium_suite.py starts from the same data.
"""
import subprocess
import sys
import urllib.request

MYSQL = r"C:\xampp\mysql\bin\mysql.exe"
SCHEMA = r"F:\outputs\aiub-webtech\skillbank\schema.sql"
SEED_URL = "http://localhost:8003/seed.php"


def main():
    with open(SCHEMA, "rb") as fh:
        proc = subprocess.run([MYSQL, "-u", "root"], stdin=fh,
                              capture_output=True)
    if proc.returncode != 0:
        print("schema load failed:", proc.stderr.decode("utf-8", "replace"))
        return 1
    print("schema reloaded")

    body = urllib.request.urlopen(SEED_URL, timeout=20).read().decode("utf-8", "replace")
    print("seed:", body.strip()[:80])

    rows = subprocess.run([MYSQL, "-u", "root", "-N", "-B", "-e",
                           "SELECT COUNT(*) FROM skillbank.users;"],
                          capture_output=True, text=True).stdout.strip()
    print("users in database:", rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
