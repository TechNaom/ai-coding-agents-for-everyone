"""
Chapter 13 Exercises: The Regulated-Path Policy Layer's Building Blocks -- Starter

Three TODOs, each a small, pure function -- no live model, no real git
repo, no network access needed to verify any of them. Run this file
after each TODO to see your progress:

    python3 starter.py
"""

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"


def classify_path(path, cde_patterns, gl_patterns):
    """TODO 1: return "CDE" if any pattern in `cde_patterns` appears
    ANYWHERE in `path` (substring containment, not just a leading
    prefix -- a pattern nested under a scratch prefix must still
    match). Return "GL" the same way for `gl_patterns`, checked after
    CDE. Return None if neither matches. Normalize `path` first:
    convert backslashes to forward slashes, and strip a literal
    leading "./" if present.
    """
    raise NotImplementedError("TODO 1: implement classify_path")


import re

PAN_PATTERN = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")


def redact_pan(text):
    """TODO 2: return `text` with every substring matching
    `PAN_PATTERN` replaced by the literal string "[REDACTED-PAN]".
    (One line -- use `PAN_PATTERN.sub`.)
    """
    raise NotImplementedError("TODO 2: implement redact_pan")


def resolve_ci_tier_for_regulated_org(name, path, policy_ci, cde_patterns, gl_patterns):
    """TODO 3: look up `name`'s tier in `policy_ci` (default BLOCKED if
    not present, fail-closed per Chapter 11-12's pattern). If `path` is
    not None AND `classify_path(path, cde_patterns, gl_patterns)`
    returns something other than None, the effective tier is forced to
    BLOCKED regardless of what the policy dict says. Otherwise return
    the plain policy tier.
    """
    raise NotImplementedError("TODO 3: implement resolve_ci_tier_for_regulated_org")


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

    cde = ("payments/card_intake/", "payments/tokenization/")
    gl = ("ledger/gl_posting/",)

    check("classify_path: a CDE path is classified CDE", classify_path("payments/card_intake/parse.py", cde, gl), "CDE")
    check("classify_path: a GL path is classified GL", classify_path("ledger/gl_posting/adjust.py", cde, gl), "GL")
    check("classify_path: an ordinary internal-tools path is neither", classify_path("tools/lint.py", cde, gl), None)
    check(
        "classify_path: a regulated pattern NESTED under a scratch prefix still counts",
        classify_path("ci-scratch/payments/card_intake/notes.txt", cde, gl),
        "CDE",
    )
    check(
        "classify_path: a leading ./ is normalized before matching",
        classify_path("./ledger/gl_posting/adjust.py", cde, gl),
        "GL",
    )
    check(
        "classify_path: a path that merely resembles a pattern's words, in a different order, does not match",
        classify_path("payments/tokenization_docs/readme.md", cde, gl),
        None,
    )

    check("redact_pan: a 16-digit card number is masked", redact_pan("card: 4111111111111111 approved"), "card: [REDACTED-PAN] approved")
    check(
        "redact_pan: a spaced/dashed card number is also masked",
        redact_pan("card: 4111-1111-1111-1111 ok"),
        "card: [REDACTED-PAN] ok",
    )
    check("redact_pan: an unrelated short number is left alone", redact_pan("retry count: 5, port 8080"), "retry count: 5, port 8080")
    check(
        "redact_pan: ordinary text with no digits at all is unchanged",
        redact_pan("build failed: missing fixture"),
        "build failed: missing fixture",
    )

    policy_ci = {"read_file": ALLOWED, "write_file": ALLOWED, "edit_file": BLOCKED}

    check(
        "resolve_ci_tier_for_regulated_org: a non-regulated write keeps its policy tier",
        resolve_ci_tier_for_regulated_org("write_file", "ci-scratch/summary.md", policy_ci, cde, gl),
        ALLOWED,
    )
    check(
        "resolve_ci_tier_for_regulated_org: a write to a CDE path is forced BLOCKED even though the tool's tier is ALLOWED",
        resolve_ci_tier_for_regulated_org("write_file", "payments/card_intake/parse.py", policy_ci, cde, gl),
        BLOCKED,
    )
    check(
        "resolve_ci_tier_for_regulated_org: a write to a GL path is forced BLOCKED too",
        resolve_ci_tier_for_regulated_org("write_file", "ledger/gl_posting/adjust.py", policy_ci, cde, gl),
        BLOCKED,
    )
    check(
        "resolve_ci_tier_for_regulated_org: a tool already BLOCKED stays BLOCKED regardless of path",
        resolve_ci_tier_for_regulated_org("edit_file", "tools/lint.py", policy_ci, cde, gl),
        BLOCKED,
    )
    check(
        "resolve_ci_tier_for_regulated_org: with no path given (a tool that takes none), the plain policy tier applies",
        resolve_ci_tier_for_regulated_org("read_file", None, policy_ci, cde, gl),
        ALLOWED,
    )

    n_passed = sum(checks)
    print(f"\n{n_passed}/{len(checks)} checks passed.")


if __name__ == "__main__":
    main()
