"""
Chapter 10 Project -- Review Harness for flawed_pr/ (solution)

See starter.py for the full task description. This file is starter.py
with TODO 1-4 filled in.
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
    """See starter.py's docstring for the full spec."""
    if not hasattr(obj, method_name):
        return False
    return callable(getattr(obj, method_name))


def try_run(label, fn, *args, **kwargs):
    """See starter.py's docstring for the full spec."""
    try:
        fn(*args, **kwargs)
        print(f"[RUNS OK] {label}")
        return True
    except Exception as e:  # noqa: BLE001 -- deliberately broad, this is a checker
        print(f"[CRASHES] {label} -- {type(e).__name__}: {e}")
        return False


def trace_week_boundary():
    """See starter.py's docstring for the full spec."""
    records = [{"date": date(2026, 8, d), "amount": 10.0 * d} for d in range(1, 11)]
    as_of = date(2026, 8, 10)
    result = aggregate.filter_week(records, as_of)
    days_included = sorted(r["date"].day for r in result)
    as_of_included = as_of in [r["date"] for r in result]
    print(f"  days included: {days_included}")
    print(f"  as_of (day 10) included: {as_of_included}")
    # Docstring promise: 7 days, NOT including as_of.
    return len(result) == 7 and not as_of_included


def trace_mutable_default_leak():
    """See starter.py's docstring for the full spec."""
    sig = inspect.signature(notify.build_message)
    param = sig.parameters["headers"]
    has_default = param.default is not inspect.Parameter.empty
    return has_default and isinstance(param.default, (list, dict, set))


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

    print("\n=== Summary ===")
    print("Real flaws this harness surfaces: 4")
    print("  1. export_csv.write_report crashes  -- DictWriter.write_all() doesn't exist")
    print("  2. notify.build_message crashes     -- set_content() doesn't return self")
    print("  3. aggregate.average_order_value crashes -- statistics.average() doesn't exist")
    print("  4. aggregate.filter_week boundary   -- includes 8 days and as_of itself,")
    print("     contradicting its own docstring's '7 days, not including as_of' promise")
    print("Plus 1 latent bug this harness doesn't crash on but review should still catch:")
    print("  5. notify.build_message's headers={} mutable default leaks state across calls")
    print("     (see project/review_answer_key.md for a two-call trace proving the leak)")
    print("Deliberately NOT a flaw: aggregate.total_revenue's round() -- justified by its")
    print("own comment; a display-only rounding step, not a hidden symptom fix.")


if __name__ == "__main__":
    main()
