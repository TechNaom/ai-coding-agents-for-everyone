"""
Chapter 7 Practice: Watching All Four-Plus-One Stop Conditions Fire

Chapter 4 named five ways an agent loop ends: a clean stop (no tool call),
a hard stop (step cap), a boundary stop (a rule blocks a call), a failure
stop (an unrecoverable tool error), and a context-limit stop (Chapter 6,
not simulated here). This script simulates a tiny agent loop against four
pre-scripted, fake "model turns" -- no real model, no network -- so you can
see exactly which stop condition fires and why, for each scenario.

Before running this, read each scenario below and write down which stop
condition you think will fire. Then run it and check yourself:

    python3 starter.py
"""

MAX_STEPS = 5
BLOCKED_TOOLS = {"delete_file"}  # a boundary rule: this tool is never allowed


class ScriptedModel:
    """Stands in for a real model -- returns pre-written turns in order."""

    def __init__(self, turns):
        self._turns = turns
        self._i = 0

    def next_turn(self):
        turn = self._turns[self._i]
        self._i += 1
        return turn


def run_tool(name, args):
    """A fake tool executor. 'run_broken_command' always fails."""
    if name == "run_broken_command":
        raise RuntimeError("permission denied: cannot execute this command")
    return f"ok: ran {name} with {args}"


def run_loop(model, label):
    print(f"\n--- Scenario: {label} ---")
    for step in range(1, MAX_STEPS + 1):
        turn = model.next_turn()

        if turn["type"] == "text_only":
            print(f"  step {step}: model produced text only, no tool call.")
            print("  STOPPED: clean_stop")
            return "clean_stop"

        name = turn["tool_name"]
        args = turn.get("args", {})

        if name in BLOCKED_TOOLS:
            print(f"  step {step}: model tried to call blocked tool {name!r}.")
            print("  STOPPED: boundary_stop")
            return "boundary_stop"

        try:
            result = run_tool(name, args)
            print(f"  step {step}: {name}({args}) -> {result}")
        except RuntimeError as e:
            print(f"  step {step}: {name}({args}) -> unrecoverable error: {e}")
            print("  STOPPED: failure_stop")
            return "failure_stop"

    print(f"  reached {MAX_STEPS} steps without a clean stop.")
    print("  STOPPED: step_cap")
    return "step_cap"


def main():
    # Scenario A: the model calls two tools, then produces a text-only turn.
    scenario_a = ScriptedModel([
        {"type": "tool_call", "tool_name": "read_file", "args": {"path": "a.py"}},
        {"type": "tool_call", "tool_name": "read_file", "args": {"path": "b.py"}},
        {"type": "text_only"},
    ])

    # Scenario B: the model keeps calling tools past the step cap.
    scenario_b = ScriptedModel([
        {"type": "tool_call", "tool_name": "read_file", "args": {"path": "a.py"}}
        for _ in range(10)
    ])

    # Scenario C: the model tries to call a tool this harness never allows.
    scenario_c = ScriptedModel([
        {"type": "tool_call", "tool_name": "read_file", "args": {"path": "a.py"}},
        {"type": "tool_call", "tool_name": "delete_file", "args": {"path": "prod.db"}},
    ])

    # Scenario D: a tool call fails in a way the model can't route around.
    scenario_d = ScriptedModel([
        {"type": "tool_call", "tool_name": "read_file", "args": {"path": "a.py"}},
        {"type": "tool_call", "tool_name": "run_broken_command", "args": {"cmd": "rm -rf /nope"}},
    ])

    outcomes = {
        "A: two reads then a summary": run_loop(scenario_a, "two reads then a summary"),
        "B: never stops making tool calls": run_loop(scenario_b, "never stops making tool calls"),
        "C: tries a boundary-blocked tool": run_loop(scenario_c, "tries a boundary-blocked tool"),
        "D: hits an unrecoverable tool error": run_loop(scenario_d, "hits an unrecoverable tool error"),
    }

    print("\n--- Summary ---")
    for label, outcome in outcomes.items():
        print(f"  {label}: {outcome}")


if __name__ == "__main__":
    main()
