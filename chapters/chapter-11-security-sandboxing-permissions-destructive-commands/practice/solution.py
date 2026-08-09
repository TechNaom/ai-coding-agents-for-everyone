"""
Chapter 11 Practice: Is This Tool Call ALLOWED, REQUIRES_CONFIRMATION,
or BLOCKED? (solution)

Six real tool calls, each evaluated against `project/solution.py`'s
actual TOOL_POLICY and SHELL_DENYLIST -- not a hypothetical policy,
the exact one this chapter ships. For each one, predict: (1) which of
the three tiers applies, and (2) whether anything ELSE about the call
(not just its tier) matters -- some of these have a twist that a
tier lookup alone doesn't capture.

    python3 --version
    python3 starter.py

Read each SCENARIO below and write down your prediction before running
the script -- it prints each scenario followed by its own answer key.
"""

SCENARIOS = [
    {
        "title": "Scenario 1 -- reading a file before making any changes",
        "call": 'read_file(path="src/config.py")',
        "context": (
            "An agent's very first tool call in a task, before touching anything."
        ),
        "verdict": "ALLOWED",
        "explanation": (
            "read_file is read-only -- it cannot change any state, so gating it "
            "behind a human would be pure friction with no safety benefit. It runs "
            "immediately, no prompt, exactly like git_status and git_diff. The "
            "TOOL_POLICY tier for a tool is fixed regardless of WHICH file is being "
            "read -- there's no path-based exception here, because the risk profile "
            "of reading is uniformly low across the whole workspace boundary "
            "_safe_path() already enforces."
        ),
    },
    {
        "title": "Scenario 2 -- editing a file the agent was explicitly asked to fix",
        "call": 'edit_file(path="src/config.py", find="timeout = 30", replace="timeout = 60")',
        "context": (
            "The user's own task description literally asked for this exact change."
        ),
        "verdict": "REQUIRES_CONFIRMATION",
        "explanation": (
            "edit_file changes state, so it's REQUIRES_CONFIRMATION in TOOL_POLICY "
            "-- and that tier does not change based on how clearly the user's "
            "original request maps to this specific call. This is deliberate, not "
            "an oversight: the confirmation step exists precisely because a plan "
            "that LOOKS like it matches the request is not the same guarantee as a "
            "human actually reading the specific diff before it lands, which is "
            "Chapter 3's entire opening point, still true here."
        ),
    },
    {
        "title": "Scenario 3 -- a shell command that's also denylisted",
        "call": 'run_shell_command(command="git push origin main --force")',
        "context": (
            "The agent decides, on its own, that force-pushing will 'clean up' a "
            "messy branch history."
        ),
        "verdict": "REQUIRES_CONFIRMATION tier, but BLOCKED in practice by the denylist -- two independent layers, both have to clear",
        "explanation": (
            "run_shell_command's TOOL_POLICY tier is REQUIRES_CONFIRMATION, so in "
            "principle a human COULD be asked. But run_shell_command's own body "
            "checks SHELL_DENYLIST first, and 'git push ... --force' matches the "
            "'force-push (can destroy remote history)' pattern -- so this specific "
            "command is refused before a human is ever prompted, regardless of "
            "what the permission tier says. This is the defense-in-depth point the "
            "lesson makes explicitly: the per-tool policy tier and the "
            "per-command denylist are two SEPARATE checks defending against "
            "different things (should this TOOL run at all vs. should THIS "
            "specific command run), and a call has to clear both."
        ),
    },
    {
        "title": "Scenario 4 -- the agent tries to notify someone about a failure",
        "call": 'send_email(to="oncall@example.com", subject="Build failed", body="...")',
        "context": (
            "A plausible, even well-intentioned reason -- the agent wants a human "
            "to know something went wrong."
        ),
        "verdict": "BLOCKED",
        "explanation": (
            "send_email is BLOCKED in TOOL_POLICY, full stop -- no prompt, no "
            "chance to confirm, regardless of how reasonable the stated reason "
            "sounds. This is the point of a BLOCKED tier existing at all: some "
            "actions (a real, irreversible external effect reaching a third party) "
            "aren't worth a human's split-second yes/no under time pressure, "
            "because a rushed 'y' to a plausible-sounding prompt is a real, "
            "predictable failure mode of confirmation-based systems generally. "
            "Removing the decision from the runtime path entirely is safer than "
            "trusting every future confirmation to be given carefully."
        ),
    },
    {
        "title": "Scenario 5 -- the commit Chapter 8 wouldn't ship",
        "call": 'git_commit(message="Fix timeout bug")',
        "context": (
            "All prior tool calls in this task succeeded, git_status shows exactly "
            "the one expected file changed, and git_diff looks correct."
        ),
        "verdict": "REQUIRES_CONFIRMATION",
        "explanation": (
            "Even with a clean git_status and a correct-looking git_diff, "
            "git_commit is REQUIRES_CONFIRMATION -- the tier is fixed per-tool, not "
            "conditional on how confident the run looks so far. This is exactly "
            "the resolution to Chapter 8's open question: there is no `confirm` "
            "argument on git_commit's own signature for the model to set, and "
            "nothing about a clean-looking git_diff changes what dispatch_tool_call "
            "does -- it still pauses for a real human, every single time, no matter "
            "how routine the change looks."
        ),
    },
    {
        "title": "Scenario 6 -- a brand-new tool nobody explicitly classified yet",
        "call": 'run_database_migration(sql_file="002_add_column.sql")',
        "context": (
            "A teammate added this tool's schema and function last week, wired it "
            "into TOOL_FUNCTIONS, and forgot to add an entry for it in TOOL_POLICY."
        ),
        "verdict": "BLOCKED (by the fail-closed default, not by an explicit decision anyone made)",
        "explanation": (
            "check_permission()/policy_for() return BLOCKED for any tool name "
            "that isn't a key in TOOL_POLICY at all -- so this call is refused, "
            "not because anyone decided database migrations are too risky, but "
            "because nobody decided anything, and the default for 'nobody decided "
            "anything' is BLOCKED, not ALLOWED. This is the single most important "
            "line in the whole permission layer: a `.get(name, BLOCKED)` instead of "
            "a `.get(name, ALLOWED)` is the difference between an unclassified tool "
            "failing safely and an unclassified tool running completely unguarded "
            "the very first time the model happens to call it."
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
