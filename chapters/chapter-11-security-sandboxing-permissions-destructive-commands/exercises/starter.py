"""
Chapter 11 Exercises: The Permission Layer's Building Blocks, Testable Offline

This file builds three small, standalone functions that mirror exactly
what `project/solution.py`'s permission-scope layer does -- a
fail-closed policy lookup, the full allow/confirm/block decision flow
(with a fake, injectable confirmation function instead of real stdin,
so it's testable without a human in the loop), and a threat-category
classifier for shell commands. No live model, no Ollama, no network --
just Python.

Fill in TODO 1 through TODO 3, then run:

    python3 starter.py

The built-in test harness at the bottom runs a set of checks and
prints PASS/FAIL for each. Compare against `solution.py`
(`python3 solution.py`) if you get stuck.
"""

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"


def policy_for(name, policy):
    """
    Given a tool name and a policy dict (name -> one of ALLOWED /
    REQUIRES_CONFIRMATION / BLOCKED), return that tool's tier. If
    `name` is NOT a key in `policy` at all, return BLOCKED -- fail
    closed, not open. This is the exact lookup `project/solution.py`'s
    `check_permission()` performs.

    TODO 1: implement this in one line using `policy.get(...)`.
    """
    raise NotImplementedError("policy_for: TODO 1")


def evaluate_call(name, args, policy, confirm_fn, run_fn):
    """
    The full decision flow, in isolation from any real tool functions
    or real stdin -- exactly what `dispatch_tool_call` does, minus the
    JSON parsing and the "unknown tool" case (both already handled
    elsewhere; this function assumes `name` is a real, known tool).

    - Look up name's tier via policy_for(name, policy).
    - If BLOCKED: return ("blocked", f"{name} is blocked by policy")
      WITHOUT calling confirm_fn at all.
    - If REQUIRES_CONFIRMATION: call confirm_fn(name, args). If it
      returns False, return ("denied", f"{name} requires human
      confirmation, which was not granted"). If it returns True, fall
      through to running the tool.
    - If ALLOWED, or REQUIRES_CONFIRMATION that was granted: call
      run_fn(name, args) and return ("ran", <its return value>).

    TODO 2: implement this. `confirm_fn` and `run_fn` are plain
    functions passed in by the caller (the test harness below passes
    fakes) -- this function should call them, not know anything about
    what they actually do internally.
    """
    raise NotImplementedError("evaluate_call: TODO 2")


# A named category per Chapter 11's threat model, roughly in the order
# the lesson introduces them: data loss, scope escape, supply-chain /
# credential exposure, irreversible external effects.
DATA_LOSS = "data_loss"
SCOPE_ESCAPE = "scope_escape"
SUPPLY_CHAIN_OR_CREDENTIAL = "supply_chain_or_credential"
IRREVERSIBLE_EXTERNAL = "irreversible_external"


def classify_threat(command):
    """
    Given a shell command string, return which of the four threat
    categories above it most clearly falls into, or None if it doesn't
    match any of them (an ordinary, harmless command like "ls" or
    "pytest").

    Use simple substring/keyword checks (no need for regex precision
    here -- this exercise is about the categories, not building a
    production-grade denylist, which `project/solution.py`'s
    SHELL_DENYLIST already does for the data-loss patterns
    specifically). Check in this order and return the FIRST category
    that matches:

    1. DATA_LOSS: the command contains "rm -rf", "git reset --hard", or
       "drop table" (case-insensitive).
    2. SUPPLY_CHAIN_OR_CREDENTIAL: the command contains "pip install",
       "npm install", "cat ~/.aws", "cat ~/.ssh", or ".env" (these
       represent installing new code from the outside, or reading
       credential material) -- checked BEFORE the more general
       scope-escape check below, since a credential-reading command
       like "cat ~/.aws/credentials" would otherwise also match "~/".
    3. SCOPE_ESCAPE: the command references a path starting with "../"
       or an absolute path outside a project, like "/etc/" or "~/" --
       for this exercise, just check for the literal substrings "../",
       "/etc/", or "~/".
    4. IRREVERSIBLE_EXTERNAL: the command contains "sendmail",
       "curl -X POST", or "git push" (representing a real external
       side effect that can't be locally undone).

    Return None if nothing matches.

    TODO 3: implement this, checking in the order above and returning
    on the first match.
    """
    raise NotImplementedError("classify_threat: TODO 3")


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

    # --- policy_for ---
    check("policy_for finds an ALLOWED tool", policy_for("read_file", policy), ALLOWED)
    check("policy_for finds a REQUIRES_CONFIRMATION tool", policy_for("write_file", policy), REQUIRES_CONFIRMATION)
    check("policy_for finds a BLOCKED tool", policy_for("send_email", policy), BLOCKED)
    check(
        "policy_for defaults an UNCLASSIFIED tool to BLOCKED, not ALLOWED",
        policy_for("some_new_tool_nobody_classified", policy),
        BLOCKED,
    )

    # --- evaluate_call ---
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

    # --- classify_threat ---
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
