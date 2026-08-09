"""
Chapter 12 Practice: What Happens to This Tool Call, Interactively vs. in CI? (solution)

Functionally identical to starter.py -- this practice script has no
blanks to fill in, it's meant to be read, predicted against, and run.

    python3 --version
    python3 solution.py

Read each SCENARIO below and write down your prediction before running
the script -- it prints each scenario followed by its own answer key.
"""

SCENARIOS = [
    {
        "title": "Scenario 1 -- a read-only tool call, in either mode",
        "call": 'git_diff(path="app.py")',
        "context": "The very first thing a PR review bot does when a pull request opens.",
        "verdict": "ALLOWED in BOTH modes, unchanged",
        "explanation": (
            "git_diff is read-only, so it's ALLOWED in both TOOL_POLICY and "
            "TOOL_POLICY_CI -- nothing about it needed to change for CI at "
            "all. This is the lesson's point about the PR review bot use "
            "case: an entirely read-only agent needed zero policy work to "
            "run safely and usefully in CI, because Chapter 11's original "
            "policy already covered it."
        ),
    },
    {
        "title": "Scenario 2 -- write_file, same call, two different modes",
        "call": 'write_file(path="ci-scratch/summary.md", content="...")',
        "context": "A CI troubleshooting agent writing its diagnosis of a failing test.",
        "verdict": "Interactively: REQUIRES_CONFIRMATION, denied on closed stdin. In CI mode: ALLOWED, and it actually writes.",
        "explanation": (
            "Same tool, same call shape, genuinely different outcome by "
            "mode -- and for a REASON, not by accident. Interactively, "
            "write_file is REQUIRES_CONFIRMATION; with no human on stdin, "
            "confirm_with_human denies it. In CI mode, TOOL_POLICY_CI marks "
            "write_file ALLOWED, but the path is inside CI_SCRATCH_PREFIX, "
            "so the function's own internal scope check passes it through. "
            "The confirmation that CI can't give was replaced by a "
            "pre-decided scope, not skipped."
        ),
    },
    {
        "title": "Scenario 3 -- write_file to a tracked source file, in CI mode",
        "call": 'write_file(path="app.py", content="def add(a, b):\\n    return a + b\\n")',
        "context": "The same troubleshooting agent, now trying to apply its fix directly.",
        "verdict": "Refused in CI mode -- ALLOWED tier, but scope-refused",
        "explanation": (
            "TOOL_POLICY_CI still says write_file is ALLOWED -- the TIER "
            "alone would let this through. But write_file()'s own body "
            "checks CI_SCRATCH_PREFIX before writing anything, and "
            "'app.py' isn't inside 'ci-scratch/', so it's refused with a "
            "clean error string, not a crash. This is the scenario that "
            "shows why a policy TIER and a SCOPE check are two separate "
            "things -- the same distinction Chapter 11 drew between "
            "_safe_path() and TOOL_POLICY, now applied a level deeper "
            "inside a single tool's own tier."
        ),
    },
    {
        "title": "Scenario 4 -- run_shell_command, same call, two different modes",
        "call": 'run_shell_command(command="ls -la")',
        "context": "A harmless, read-only-in-effect command -- just listing files.",
        "verdict": "Interactively: REQUIRES_CONFIRMATION, denied on closed stdin. In CI mode: BLOCKED outright, no prompt at all.",
        "explanation": (
            "Even though 'ls -la' itself is harmless, run_shell_command's "
            "policy tier doesn't vary by WHICH command is given -- that's "
            "true in both modes. Interactively it's REQUIRES_CONFIRMATION "
            "(denied without a human). In CI mode it's explicitly BLOCKED "
            "-- not because this specific command is dangerous, but "
            "because no scope exists that would make an ARBITRARY shell "
            "command safe to pre-approve for every possible argument a "
            "model might supply. The harmlessness of one example command "
            "doesn't change the tier for the whole tool."
        ),
    },
    {
        "title": "Scenario 5 -- git_commit, on two different branches, same CI run",
        "call": 'git_commit(message="apply proposed fix")',
        "context": "Called twice: once while checked out on ci/auto-fix-42, once (by mistake) on main.",
        "verdict": "Allowed on ci/auto-fix-42. Refused on main -- even though TOOL_POLICY_CI marks git_commit ALLOWED.",
        "explanation": (
            "Exactly the same shape as write_file's scratch-scope check, "
            "applied to commits instead of writes: git_commit() checks "
            "the CURRENT BRANCH (read from git itself, not from any "
            "argument the model provided) against PROTECTED_BRANCHES "
            "before committing. A scratch branch passes; main is refused "
            "with a clean error, regardless of how reasonable the commit "
            "message sounds or how confirmed-looking the rest of the run "
            "was."
        ),
    },
    {
        "title": "Scenario 6 -- a new tool, added to TOOL_POLICY but not TOOL_POLICY_CI",
        "call": 'run_linter()',
        "context": "A teammate added this read-only tool last week and classified it ALLOWED in TOOL_POLICY, but forgot TOOL_POLICY_CI entirely.",
        "verdict": "ALLOWED interactively. BLOCKED in CI mode -- by the fail-closed default, not by an explicit decision.",
        "explanation": (
            "active_policy() picks TOOL_POLICY_CI when CI_MODE is True, "
            "then check_permission() does a .get(name, BLOCKED) lookup on "
            "WHATEVER dict got picked. Since 'run_linter' isn't a key in "
            "TOOL_POLICY_CI at all, the CI run gets BLOCKED -- not because "
            "anyone decided a linter is dangerous, but because nobody "
            "classified it for CI specifically, and the fail-closed "
            "default for 'nobody decided' is BLOCKED in EVERY policy "
            "dict, not just the interactive one. Two separate dicts means "
            "two separate places this default has to hold -- and it does, "
            "independently, in both."
        ),
    },
]


def main():
    for i, s in enumerate(SCENARIOS, start=1):
        print(f"\n{'=' * 70}")
        print(f"{s['title']}")
        print("=" * 70)
        print(f"Call:    {s['call']}")
        print(f"Context: {s['context']}")
        print("--- ANSWER KEY ---")
        print(f"Verdict: {s['verdict']}")
        print(f"Why:     {s['explanation']}")


if __name__ == "__main__":
    main()
