"""
Chapter 13 Exercises: The Regulated-Path Policy Layer's Building Blocks -- Worked Solution

`starter.py` with all three TODOs filled in. These rebuild, as small
testable functions, the exact mechanisms `project/solution.py` uses:
a regulated-path classifier, a PAN redaction scrub, and a mode-aware
tier resolver where a regulated-path hit overrides an otherwise-ALLOWED
tier. None of this needs a live model, a real git repo, or network
access to verify.

Run:

    python3 solution.py
"""

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"


def classify_path(path, cde_patterns, gl_patterns):
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if any(p in normalized for p in cde_patterns):
        return "CDE"
    if any(p in normalized for p in gl_patterns):
        return "GL"
    return None


import re

PAN_PATTERN = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")


def redact_pan(text):
    return PAN_PATTERN.sub("[REDACTED-PAN]", text)


def resolve_ci_tier_for_regulated_org(name, path, policy_ci, cde_patterns, gl_patterns):
    """Combines Chapter 12's mode-aware tier lookup with this chapter's
    regulated-path override: a tool's tier from `policy_ci` is only the
    STARTING point -- if `path` classifies as regulated, the effective
    tier is forced to BLOCKED regardless of what the policy dict says,
    because a regulated write has no scope narrow enough to pre-approve
    in an unattended run, the same reasoning Chapter 12 applied to
    `edit_file`/`run_shell_command` generalized one level further."""
    tier = policy_ci.get(name, BLOCKED)
    if path is not None and classify_path(path, cde_patterns, gl_patterns) is not None:
        return BLOCKED
    return tier


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
