"""
Chapter 12 Exercises: The CI Policy Layer's Building Blocks -- Worked Solution

`starter.py` with all three TODOs filled in. Run:

    python3 solution.py
"""

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"


def in_scratch(path, prefix):
    normalized = path[2:] if path.startswith("./") else path
    return normalized.startswith(prefix)


def is_protected_branch(branch, protected_branches):
    if branch is None:
        return True
    return branch in protected_branches


def resolve_tier(name, ci_mode, policy, policy_ci):
    active = policy_ci if ci_mode else policy
    return active.get(name, BLOCKED)


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

    check("in_scratch: a file directly inside the prefix", in_scratch("ci-scratch/summary.md", "ci-scratch/"), True)
    check("in_scratch: a nested file inside the prefix", in_scratch("ci-scratch/sub/dir/file.txt", "ci-scratch/"), True)
    check("in_scratch: a leading ./ is normalized away", in_scratch("./ci-scratch/summary.md", "ci-scratch/"), True)
    check("in_scratch: a file outside the prefix", in_scratch("app.py", "ci-scratch/"), False)
    check(
        "in_scratch: a path that merely CONTAINS the prefix name isn't enough",
        in_scratch("not-ci-scratch/summary.md", "ci-scratch/"),
        False,
    )
    check("in_scratch: the bare prefix itself doesn't count as a file inside it", in_scratch("ci-scratch", "ci-scratch/"), False)
    check(
        "in_scratch: a genuine path escape is NOT accidentally normalized into scope (the lstrip() trap)",
        in_scratch("../../etc/passwd", "ci-scratch/"),
        False,
    )

    protected = {"main", "master"}
    check("is_protected_branch: main is protected", is_protected_branch("main", protected), True)
    check("is_protected_branch: master is protected", is_protected_branch("master", protected), True)
    check("is_protected_branch: a scratch branch is not protected", is_protected_branch("ci/auto-fix", protected), False)
    check("is_protected_branch: an undetermined branch (None) is treated as protected", is_protected_branch(None, protected), True)

    policy = {"read_file": ALLOWED, "write_file": REQUIRES_CONFIRMATION, "edit_file": REQUIRES_CONFIRMATION}
    policy_ci = {"read_file": ALLOWED, "write_file": ALLOWED, "edit_file": BLOCKED}

    check("resolve_tier: interactive mode uses the interactive policy", resolve_tier("write_file", False, policy, policy_ci), REQUIRES_CONFIRMATION)
    check("resolve_tier: CI mode uses the CI policy for the SAME tool name", resolve_tier("write_file", True, policy, policy_ci), ALLOWED)
    check("resolve_tier: CI mode can be MORE restrictive for a tool too", resolve_tier("edit_file", True, policy, policy_ci), BLOCKED)
    check("resolve_tier: interactive mode for that same tool is less restrictive", resolve_tier("edit_file", False, policy, policy_ci), REQUIRES_CONFIRMATION)
    check(
        "resolve_tier: a tool unclassified in BOTH policies defaults to BLOCKED in interactive mode",
        resolve_tier("run_database_migration", False, policy, policy_ci),
        BLOCKED,
    )
    check(
        "resolve_tier: the SAME unclassified tool also defaults to BLOCKED in CI mode",
        resolve_tier("run_database_migration", True, policy, policy_ci),
        BLOCKED,
    )

    n_passed = sum(checks)
    print(f"\n{n_passed}/{len(checks)} checks passed.")


if __name__ == "__main__":
    main()
