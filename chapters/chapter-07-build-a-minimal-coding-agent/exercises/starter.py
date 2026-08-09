"""
Chapter 7 Exercises: Minimal Coding Agent -- Tool Dispatch and Loop Control

These exercises don't require a running Ollama server. They test the two
pieces of the agent loop that don't need a live model to verify: the
tool-dispatch logic (turning a model's tool call into a real function call,
safely) and the loop's stop-condition control flow (Chapter 4's four-plus-one
ways a loop ends).

Run this file directly to see PASS/FAIL for each exercise:

    python3 starter.py
"""
import json

# ---------------------------------------------------------------------------
# Two real tools, same shape as the lesson's read_file/write_file.
# A tiny in-memory "filesystem" stands in for the real disk so these
# exercises run instantly and deterministically, with no I/O.
# ---------------------------------------------------------------------------
FAKE_DISK = {"notes.txt": "hello from disk"}


def read_file(path):
    if path not in FAKE_DISK:
        return f"error: no such file: {path}"
    return FAKE_DISK[path]


def write_file(path, content):
    FAKE_DISK[path] = content
    return f"wrote {len(content)} bytes to {path}"


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
}

# read_file needs ["path"]; write_file needs ["path", "content"]
REQUIRED_ARGS = {
    "read_file": ["path"],
    "write_file": ["path", "content"],
}


# ---------------------------------------------------------------------------
# Exercise 1: dispatch_tool_call
# ---------------------------------------------------------------------------
def dispatch_tool_call(name, arguments_json):
    """
    Turn one model-issued tool call into a real function call, and never
    raise -- always return a string, even when something goes wrong.

    TODO 1: Parse `arguments_json` (a JSON string, exactly what
            tc.function.arguments looks like in the real client) into a
            dict with json.loads(). If it isn't valid JSON, catch
            json.JSONDecodeError and return the string:
                f"error: invalid JSON arguments for {name}: {arguments_json!r}"

    TODO 2: If `name` isn't a key in TOOL_FUNCTIONS, return the string:
                f"error: unknown tool: {name}"

    TODO 3: Before calling the tool function, check that every key in
            REQUIRED_ARGS[name] is actually present in the parsed
            arguments dict. This is the reliability discipline the
            lesson calls out: a small local model can produce a tool
            call with a missing expected key, and code that assumes
            the arguments are well-formed will crash with a KeyError.
            If a required key is missing, return the string:
                f"error: missing required argument {missing!r} for {name}"
            (where `missing` is the name of the first missing key).

    TODO 4: Call TOOL_FUNCTIONS[name] with the parsed arguments
            (use **arguments) and return whatever it returns.

    This function must never let an exception escape -- every failure
    path above returns a descriptive string instead.
    """
    # YOUR CODE HERE
    raise NotImplementedError("dispatch_tool_call is not implemented yet")


# ---------------------------------------------------------------------------
# Exercise 2: run_loop_stub
# ---------------------------------------------------------------------------
def run_loop_stub(scripted_turns, max_steps):
    """
    A stand-in for the real agent loop's control flow, driven by a list of
    pre-scripted "model turns" instead of a real client -- this is exactly
    what the chapter's lesson meant by testing the loop without a live
    model: a mocked/stubbed response feeding the same control flow the
    real loop uses.

    `scripted_turns` is a list of dicts, each shaped like:
        {"tool_call": True}   -- this turn "made a tool call"
        {"tool_call": False}  -- this turn was a clean stop (no tool call)

    TODO 1: Walk through scripted_turns one at a time, tracking how many
            steps you've taken (starting at 1).
    TODO 2: If a turn's "tool_call" is False, stop immediately and return
            the string "clean_stop" -- this is Chapter 4's clean stop:
            a turn with no tool call.
    TODO 3: If you reach max_steps and every turn so far still had a tool
            call (never hit a clean stop), return the string "step_cap"
            -- Chapter 4's hard stop: the harness-enforced step limit,
            independent of what the model "wanted" to do next.
    TODO 4: If scripted_turns runs out before max_steps and before a
            clean stop (a malformed test case), return "ran_out_of_turns".

    Return exactly one of: "clean_stop", "step_cap", "ran_out_of_turns".
    """
    # YOUR CODE HERE
    raise NotImplementedError("run_loop_stub is not implemented yet")


# ---------------------------------------------------------------------------
# Test harness -- do not need to edit anything below this line.
# ---------------------------------------------------------------------------
def _check(label, actual, expected):
    status = "PASS" if actual == expected else "FAIL"
    print(f"[{status}] {label} -> got {actual!r} (expected {expected!r})")
    return status == "PASS"


def main():
    results = []

    # --- dispatch_tool_call ---
    results.append(_check(
        "well-formed read_file call",
        dispatch_tool_call("read_file", json.dumps({"path": "notes.txt"})),
        "hello from disk",
    ))
    results.append(_check(
        "well-formed write_file call",
        dispatch_tool_call("write_file", json.dumps({"path": "out.txt", "content": "hi"})),
        "wrote 2 bytes to out.txt",
    ))
    results.append(_check(
        "missing required argument",
        dispatch_tool_call("read_file", json.dumps({})),
        "error: missing required argument 'path' for read_file",
    ))
    results.append(_check(
        "malformed JSON arguments",
        dispatch_tool_call("read_file", "{not valid json"),
        "error: invalid JSON arguments for read_file: '{not valid json'",
    ))
    results.append(_check(
        "unknown tool name",
        dispatch_tool_call("delete_everything", json.dumps({"path": "x"})),
        "error: unknown tool: delete_everything",
    ))

    # --- run_loop_stub ---
    results.append(_check(
        "clean stop on turn 3",
        run_loop_stub(
            [{"tool_call": True}, {"tool_call": True}, {"tool_call": False}],
            max_steps=8,
        ),
        "clean_stop",
    ))
    results.append(_check(
        "hits the step cap",
        run_loop_stub(
            [{"tool_call": True}] * 8,
            max_steps=8,
        ),
        "step_cap",
    ))
    results.append(_check(
        "step cap is respected even with more scripted turns available",
        run_loop_stub(
            [{"tool_call": True}] * 20,
            max_steps=4,
        ),
        "step_cap",
    ))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed.")
    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
