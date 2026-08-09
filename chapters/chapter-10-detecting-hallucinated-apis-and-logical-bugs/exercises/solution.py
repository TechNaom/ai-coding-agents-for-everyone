"""
Chapter 10 Exercises: Three Mechanical Checks, Testable Offline (solution)

See starter.py for the full task description. This file is starter.py
with TODO 1-3 filled in.
"""
import inspect


def method_actually_exists(obj, method_name):
    """See starter.py's docstring for the full spec."""
    if not hasattr(obj, method_name):
        return False
    return callable(getattr(obj, method_name))


def safe_call(fn, *args, **kwargs):
    """See starter.py's docstring for the full spec."""
    try:
        result = fn(*args, **kwargs)
        return {"ok": True, "result": result}
    except Exception as e:  # noqa: BLE001 -- deliberately broad: any failure counts
        return {"ok": False, "error_type": type(e).__name__, "error_message": str(e)}


def has_mutable_default(fn):
    """See starter.py's docstring for the full spec."""
    sig = inspect.signature(fn)
    for param in sig.parameters.values():
        if param.default is inspect.Parameter.empty:
            continue
        if isinstance(param.default, (list, dict, set)):
            return True
    return False


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
