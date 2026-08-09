"""
Chapter 10 Exercises: Three Mechanical Checks, Testable Offline

This file builds the three mechanical checks the lesson actually
teaches, as real, callable functions instead of things you only do by
hand: does a claimed method actually exist on a real object
(`method_actually_exists`), does an exact call actually run without
raising, captured instead of crashing your script
(`safe_call`), and does a function's own signature carry the classic
mutable-default-argument trap before you even call it
(`has_mutable_default`). All three are testable completely offline --
no pandas, no requests, no network, just Python's own standard
library and `inspect`.

Fill in TODO 1 through TODO 3, then run:

    python3 starter.py

The built-in test harness at the bottom runs 12 checks and prints
PASS/FAIL for each. Compare against `solution.py`
(`python3 solution.py`, should print `12/12 checks passed.`) if you
get stuck.
"""
import inspect


def method_actually_exists(obj, method_name):
    """
    Given an object (a module, a class, or an instance) and a method
    name as a string, return True if that name actually exists on obj
    AND is callable -- the exact `hasattr()`-based check the lesson
    teaches as the cheapest way to catch a hallucinated method name,
    instead of trusting how plausible the name sounds.

    TODO 1: implement this. Use `hasattr` to check existence, and
    `callable()` on the retrieved attribute (via `getattr`) to confirm
    it's actually something you can call, not e.g. a plain data
    attribute that merely happens to share the name.
    """
    raise NotImplementedError("method_actually_exists: TODO 1")


def safe_call(fn, *args, **kwargs):
    """
    Call fn(*args, **kwargs) inside a try/except and return a dict
    describing what actually happened -- the "does it actually run"
    check the lesson teaches, packaged so a caller can inspect the
    result programmatically instead of watching a traceback scroll by.

    Return, on success:
        {"ok": True, "result": <the return value>}
    Return, on any exception:
        {"ok": False, "error_type": type(e).__name__, "error_message": str(e)}

    TODO 2: implement this.
    """
    raise NotImplementedError("safe_call: TODO 2")


def has_mutable_default(fn):
    """
    Given a function object, return True if ANY of its parameters has
    a default value that is a mutable type (list, dict, or set) -- the
    exact Python gotcha the lesson's `headers={}` example walks
    through. This is a real, useful review check: a function whose
    signature carries a mutable default is worth a second look for the
    cross-call state-leak bug, independent of whether you've spotted
    it by reading the body.

    TODO 3: implement this using `inspect.signature(fn).parameters`.
    A parameter has a real default only if
    `param.default is not inspect.Parameter.empty`. Check
    `isinstance(param.default, (list, dict, set))` for each one with a
    real default.
    """
    raise NotImplementedError("has_mutable_default: TODO 3")


# ---------------------------------------------------------------------------
# Fixtures used by the test harness below -- small, self-contained stand-ins,
# not the real pandas/csv/email examples from the lesson (those need
# packages or produce side effects), but the exact same shape of bug.
# ---------------------------------------------------------------------------
class FakeWriter:
    def writerows(self, rows):
        return len(rows)


def divide(a, b):
    return a / b


def good_default(name, tags=None):
    tags = tags if tags is not None else []
    tags.append(name)
    return tags


def bad_default(name, tags=[]):  # noqa: B006 -- deliberately the bug under test
    tags.append(name)
    return tags


def main():
    checks = []

    def check(label, actual, expected):
        ok = actual == expected
        checks.append(ok)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
        if not ok:
            print(f"       expected: {expected!r}")
            print(f"       actual:   {actual!r}")

    # --- method_actually_exists ---
    check(
        "method_actually_exists finds a real method (writerows)",
        method_actually_exists(FakeWriter(), "writerows"),
        True,
    )
    check(
        "method_actually_exists rejects a hallucinated method (write_all)",
        method_actually_exists(FakeWriter(), "write_all"),
        False,
    )
    check(
        "method_actually_exists works on a module, not just an instance",
        method_actually_exists(inspect, "signature"),
        True,
    )
    check(
        "method_actually_exists rejects a hallucinated module function",
        method_actually_exists(inspect, "get_the_docstring_please"),
        False,
    )

    # --- safe_call ---
    r1 = safe_call(divide, 10, 2)
    check("safe_call reports ok=True on a successful call", r1.get("ok"), True)
    check("safe_call returns the real result on success", r1.get("result"), 5.0)

    r2 = safe_call(divide, 10, 0)
    check("safe_call reports ok=False on a raising call", r2.get("ok"), False)
    check(
        "safe_call captures the real exception type",
        r2.get("error_type"),
        "ZeroDivisionError",
    )

    r3 = safe_call(FakeWriter().writerows, tags="not a real kwarg")
    check(
        "safe_call catches a hallucinated-argument TypeError, not just custom errors",
        r3.get("ok"),
        False,
    )

    # --- has_mutable_default ---
    check(
        "has_mutable_default is False for a safe None-sentinel default",
        has_mutable_default(good_default),
        False,
    )
    check(
        "has_mutable_default is True for the classic tags=[] trap",
        has_mutable_default(bad_default),
        True,
    )
    check(
        "has_mutable_default is False for a function with no defaults at all",
        has_mutable_default(divide),
        False,
    )

    n_passed = sum(checks)
    print(f"\n{n_passed}/{len(checks)} checks passed.")


if __name__ == "__main__":
    main()
