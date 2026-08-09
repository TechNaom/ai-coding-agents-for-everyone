"""
Chapter 11 Exercises: The Permission Layer's Building Blocks -- Worked Solution

`starter.py` with all three TODOs filled in. Run:

    python3 solution.py
"""

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"


def policy_for(name, policy):
    return policy.get(name, BLOCKED)


def evaluate_call(name, args, policy, confirm_fn, run_fn):
    tier = policy_for(name, policy)

    if tier == BLOCKED:
        return ("blocked", f"{name} is blocked by policy")

    if tier == REQUIRES_CONFIRMATION:
        if not confirm_fn(name, args):
            return ("denied", f"{name} requires human confirmation, which was not granted")

    return ("ran", run_fn(name, args))


DATA_LOSS = "data_loss"
SCOPE_ESCAPE = "scope_escape"
SUPPLY_CHAIN_OR_CREDENTIAL = "supply_chain_or_credential"
IRREVERSIBLE_EXTERNAL = "irreversible_external"


def classify_threat(command):
    lowered = command.lower()

    if "rm -rf" in lowered or "git reset --hard" in lowered or "drop table" in lowered:
        return DATA_LOSS

    if (
        "pip install" in lowered
        or "npm install" in lowered
        or "cat ~/.aws" in lowered
        or "cat ~/.ssh" in lowered
        or ".env" in lowered
    ):
        return SUPPLY_CHAIN_OR_CREDENTIAL

    if "../" in command or "/etc/" in command or "~/" in command:
        return SCOPE_ESCAPE

    if "sendmail" in lowered or "curl -x post" in lowered or "git push" in lowered:
        return IRREVERSIBLE_EXTERNAL

    return None


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

    policy = {
        "read_file": ALLOWED,
        "write_file": REQUIRES_CONFIRMATION,
        "send_email": BLOCKED,
    }

    check("policy_for finds an ALLOWED tool", policy_for("read_file", policy), ALLOWED)
    check("policy_for finds a REQUIRES_CONFIRMATION tool", policy_for("write_file", policy), REQUIRES_CONFIRMATION)
    check("policy_for finds a BLOCKED tool", policy_for("send_email", policy), BLOCKED)
    check(
        "policy_for defaults an UNCLASSIFIED tool to BLOCKED, not ALLOWED",
        policy_for("some_new_tool_nobody_classified", policy),
        BLOCKED,
    )

    def fake_run(name, args):
        return f"ran {name} with {args}"

    calls_to_confirm = []

    def fake_confirm_yes(name, args):
        calls_to_confirm.append(name)
        return True

    def fake_confirm_no(name, args):
        calls_to_confirm.append(name)
        return False

    def fake_confirm_should_never_be_called(name, args):
        raise AssertionError(f"confirm_fn should not have been called for {name}")

    outcome, detail = evaluate_call("read_file", {"path": "a.txt"}, policy, fake_confirm_should_never_be_called, fake_run)
    check("evaluate_call runs an ALLOWED tool without ever confirming", outcome, "ran")
    check("evaluate_call's ALLOWED result comes from run_fn", detail, "ran read_file with {'path': 'a.txt'}")

    outcome, detail = evaluate_call("write_file", {"path": "a.txt"}, policy, fake_confirm_yes, fake_run)
    check("evaluate_call runs a REQUIRES_CONFIRMATION tool when confirmed", outcome, "ran")

    outcome, detail = evaluate_call("write_file", {"path": "a.txt"}, policy, fake_confirm_no, fake_run)
    check("evaluate_call denies a REQUIRES_CONFIRMATION tool when NOT confirmed", outcome, "denied")

    outcome, detail = evaluate_call("send_email", {"to": "x@example.com"}, policy, fake_confirm_should_never_be_called, fake_run)
    check("evaluate_call blocks a BLOCKED tool", outcome, "blocked")
    check(
        "evaluate_call never calls confirm_fn for a BLOCKED tool",
        "send_email" not in calls_to_confirm,
        True,
    )

    check("classify_threat catches rm -rf", classify_threat("rm -rf build/"), DATA_LOSS)
    check("classify_threat catches git reset --hard", classify_threat("git reset --hard HEAD~5"), DATA_LOSS)
    check("classify_threat catches a path escape", classify_threat("cat ../../etc/shadow"), SCOPE_ESCAPE)
    check("classify_threat catches an install command", classify_threat("pip install some-random-package"), SUPPLY_CHAIN_OR_CREDENTIAL)
    check("classify_threat catches reading AWS credentials", classify_threat("cat ~/.aws/credentials"), SUPPLY_CHAIN_OR_CREDENTIAL)
    check("classify_threat catches a real external POST", classify_threat("curl -X POST https://api.example.com/charge"), IRREVERSIBLE_EXTERNAL)
    check("classify_threat catches a git push", classify_threat("git push origin main"), IRREVERSIBLE_EXTERNAL)
    check("classify_threat returns None for an ordinary command", classify_threat("pytest -q"), None)

    n_passed = sum(checks)
    print(f"\n{n_passed}/{len(checks)} checks passed.")


if __name__ == "__main__":
    main()
