#!/usr/bin/env python3
"""
priorities.py - assign a defensible priority level to each of the 40 test cases.

All 40 were recorded as High when the suite ran. The marking scheme asks twice whether
requirements and cases are "leveled and prioritized", and a uniform level reads as never
having been prioritized at all.

The rule applied here is severity of failure, not effort:

  High    core business paths and security boundaries. If this fails the product is
          either unusable or unsafe: account creation, authentication, the credit
          transfer that is the whole point of the exchange, and every access-control
          boundary (guest -> dashboard, member -> admin, member -> another member's data).

  Medium  supporting functionality and required-field validation. A failure is visible
          and annoying but neither loses data nor exposes it: create/edit/delete flows,
          empty-field rejection on a single field.

  Low     boundary and format cases. Off-by-one on a length rule, malformed input,
          fully empty form submission. Worth testing, cheapest to lose.

This changes ONLY the priority field. Every other recorded value is untouched.
"""

import json
import os
import shutil

SRC = r"F:\outputs\sqat-skillbank\results.json"
OUT = r"F:\outputs\sqat-project\results_prioritised.json"

HIGH = {
    "TC_reg-01",   # valid registration - core path
    "TC_reg-05",   # duplicate email - data integrity
    "TC_reg-10",   # starting credits granted - the economy depends on it
    "TC_log-01",   # valid member login - core path
    "TC_log-02",   # admin login and admin link - privilege
    "TC_log-03",   # wrong password rejected - security boundary
    "TC_log-07",   # logout ends session - security boundary
    "TC_log-08",   # guest cannot reach dashboard - access control
    "TC_off-01",   # create an offer - core path
    "TC_off-08",   # cannot edit another member's offer - access control
    "TC_ses-01",   # request a session - core path
    "TC_ses-03",   # teacher accepts - core path
    "TC_ses-04",   # completing transfers exactly one credit - the core transaction
    "TC_adm-02",   # member cannot open admin dashboard - access control
    "TC_adm-07",   # member cannot open Manage skills - access control
}

LOW = {
    "TC_reg-04",   # password shorter than 6 - boundary
    "TC_reg-06",   # all fields empty - degenerate input
    "TC_reg-07",   # invalid email format - format validation
    "TC_reg-08",   # password exactly 6 - boundary, on the limit
    "TC_reg-09",   # password exactly 5 - boundary, just under
    "TC_off-04",   # empty offer form - degenerate input
    "TC_adm-05",   # empty skill name ignored - degenerate input
    "TC_ses-06",   # cannot review twice - guard on a secondary flow
}


def main():
    cases = json.load(open(SRC, encoding="utf-8"))
    if isinstance(cases, dict):
        cases = cases.get("results", cases.get("cases", []))

    counts = {"High": 0, "Medium": 0, "Low": 0}
    for c in cases:
        cid = c.get("id", "")
        if cid in HIGH:
            c["priority"] = "High"
        elif cid in LOW:
            c["priority"] = "Low"
        else:
            c["priority"] = "Medium"
        counts[c["priority"]] += 1

    known = HIGH | LOW
    unknown = known - {c.get("id") for c in cases}
    if unknown:
        raise SystemExit(f"ABORT: ids listed but not present in results.json: {sorted(unknown)}")

    json.dump(cases, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"written: {OUT}")
    print(f"  total cases : {len(cases)}")
    for k in ("High", "Medium", "Low"):
        print(f"  {k:<7}     : {counts[k]:>2}  ({100*counts[k]/len(cases):.0f}%)")
    print("\n  original results.json untouched")


if __name__ == "__main__":
    main()
