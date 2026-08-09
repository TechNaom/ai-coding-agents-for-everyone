"""
Chapter 10 Project -- Review Harness for flawed_pr/

Module 4's project: a "PR" delivered by an agent, claiming to add a
weekly sales report (aggregate raw sales records, export them to CSV,
email the CSV to a distribution list). It lives in flawed_pr/
(aggregate.py, export_csv.py, notify.py) -- read project/README.md
first for the full task story and how the agent said it verified its
own work.

Your job here is NOT to read the three files and guess what's wrong.
It's to build the same two mechanical checks the lesson teaches --
"does the claimed API actually exist" and "does the actual logic
produce the value it claims to, at a real boundary" -- as a small,
runnable review harness, and let it surface every planted flaw for
you, the same way a real reviewer would before ever trusting a diff
that looks this clean.

Fill in TODO 1 through TODO 4 below, then run:

    python3 starter.py

This prints a structured report. Compare against `solution.py`
(`python3 solution.py`) if you get stuck -- it should report all 4
real flaws found and 0 false positives on the 1 deliberately-fine line.
After you're done, read project/review_answer_key.md for the full
explanation of every planted flaw, including the one that's fine.
"""
import inspect
import sys
import tempfile
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "flawed_pr"))

import aggregate  # noqa: E402
import export_csv  # noqa: E402
import notify  # noqa: E402


def method_exists(obj, method_name):
    """
    TODO 1: return True if obj actually has an attribute called
    method_name AND it's callable -- the same hasattr()+callable()
    check exercises/starter.py built. Used below to check
    csv.DictWriter.write_all and EmailMessage.set_content's real
    return-type behavior.
    """
    raise NotImplementedError("method_exists: TODO 1")


def try_run(label, fn, *args, **kwargs):
    """
    TODO 2: call fn(*args, **kwargs) inside try/except. Print
    f"[RUNS OK] {label}" and return True on success, or
    f"[CRASHES] {label} -- {type(e).__name__}: {e}" and return False
    on any exception. This is the "does it actually run" check applied
    to each of flawed_pr's real functions, with real arguments.
    """
    raise NotImplementedError("try_run: TODO 2")


def trace_week_boundary():
    """
    TODO 3: build 10 fake records, one per day from Aug 1 through
    Aug 10 2026 (use `date(2026, 8, d)` for day d, amount=10.0*d), call
    aggregate.filter_week(records, date(2026, 8, 10)), and compare what
    it actually returns against what aggregate.week_range's own
    docstring promises (7 days, NOT including as_of). Print how many
    records came back and whether Aug 10 (as_of itself) is among them.
    Return True if the result matches the docstring's promise (7
    records, Aug 10 excluded), False otherwise.
    """
    raise NotImplementedError("trace_week_boundary: TODO 3")


def trace_mutable_default_leak():
    """
    TODO 4: call notify.build_message.__defaults__ (or
    inspect.signature) to check whether `headers` has a mutable
    default value -- reuse the has_mutable_default idea from
    exercises/solution.py inline here, since this file is meant to be
    self-contained. Return True if a mutable default is present on
    `headers` (the bug), False otherwise.
    """
    raise NotImplementedError("trace_mutable_default_leak: TODO 4")


def make_sample_csv():
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir, "report.csv")
    with open(path, "w") as f:
        f.write("date,amount\n2026-08-01,10.0\n")
    return path


def main():
    print("=== Check 1: does csv.DictWriter actually have write_all()? ===")
    print(
        "  write_all exists:",
        method_exists(export_csv.csv.DictWriter, "write_all"),
        "(should be False -- the real method is writerows)",
    )

    print("\n=== Check 2: run every function in the PR with real arguments ===")
    records = [
        {"date": date(2026, 8, d), "amount": 10.0 * d} for d in range(1, 11)
    ]
    as_of = date(2026, 8, 10)

    try_run("aggregate.filter_week(records, as_of)", aggregate.filter_week, records, as_of)
    try_run("aggregate.total_revenue(records)", aggregate.total_revenue, records)
    try_run("aggregate.average_order_value(records)", aggregate.average_order_value, records)

    csv_path = make_sample_csv()
    export_out = os.path.join(tempfile.mkdtemp(), "out.csv")
    try_run(
        "export_csv.write_report(rows, out_path)",
        export_csv.write_report,
        [{"date": "2026-08-01", "amount": 10.0}],
        export_out,
    )

    try_run(
        "notify.build_message(csv_path, recipients)",
        notify.build_message,
        csv_path,
        ["team@example.com"],
    )

    print("\n=== Check 3: trace the week-boundary logic against its own docstring ===")
    boundary_ok = trace_week_boundary()
    print("  matches docstring's promise:", boundary_ok)

    print("\n=== Check 4: does build_message's signature carry a mutable default? ===")
    leak = trace_mutable_default_leak()
    print("  mutable default on `headers`:", leak, "(True means this is a real bug)")

    print("\n=== Check 5: is total_revenue's round() actually justified? ===")
    print(
        "  Read aggregate.py's comment above total_revenue -- it explains the "
        "rounding is a DISPLAY-only step, with real monetary values computed "
        "and stored separately upstream in Decimal arithmetic. This one is "
        "NOT a flaw -- it's here so you practice not over-flagging a line "
        "that merely resembles Chapter 3's rounding-bug hook."
    )


if __name__ == "__main__":
    main()
