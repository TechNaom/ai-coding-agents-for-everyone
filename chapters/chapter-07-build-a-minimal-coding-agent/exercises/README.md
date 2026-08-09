# Chapter 7 Exercises: Tool Dispatch and Loop Control

These exercises build the two pieces of a minimal coding agent that you can
verify completely without a running Ollama server: the **tool-dispatch
logic** (turning one of the model's structured tool calls into a real
function call, safely) and the **loop's stop-condition control flow**
(Chapter 4's clean stop vs. hard stop, reproduced here with scripted,
mocked "model turns" instead of a live model).

## How to run

You need Python 3 only -- no `openai` package, no Ollama, no network.

```bash
python3 --version
python3 starter.py
```

`starter.py` will raise `NotImplementedError` until you fill in the two
functions below. That's expected -- it's the same "runs and tells you
exactly what's missing" pattern the rest of this course uses.

## Exercise 1 — `dispatch_tool_call`

Find `TODO 1` through `TODO 4` inside `dispatch_tool_call`. You're
implementing the exact function a real agent loop calls after the model
emits a `tool_use` block: parse the model's JSON arguments, look up the
right Python function for the tool name, check that every argument the
tool actually needs is present, and call it — without ever letting an
exception escape.

This is directly the reliability discipline the lesson calls out: on a
real test run against `llama3.2`, a tool call came back with an
incomplete arguments object (a missing expected key) before a retry with
identical input produced a correct one. `dispatch_tool_call` is where you
defend against that — checking for a missing key and returning a
descriptive error string instead of crashing with a raw `KeyError`, and
catching `json.JSONDecodeError` instead of assuming the model's JSON is
always well-formed.

## Exercise 2 — `run_loop_stub`

Find `TODO 1` through `TODO 4` inside `run_loop_stub`. This function
doesn't call any model at all — it's fed a list of pre-scripted "turns"
(each one just says whether that turn "made a tool call" or not) and has
to reproduce the real loop's control flow: keep going while turns keep
making tool calls, stop cleanly the moment a turn doesn't make one
(Chapter 4's clean stop), and stop at `max_steps` regardless of what the
scripted turns say next (Chapter 4's hard stop / step cap).

Testing loop control flow this way — with mocked, scripted responses
instead of a live model — is a genuinely useful pattern beyond this
exercise: it's how you'd unit-test a real agent harness's stop-condition
logic without needing a model call (and its cost, latency, and
non-determinism) in every test run.

## Checking your work

Run `python3 starter.py` after filling in both functions. The built-in
test harness at the bottom of the file runs 8 checks and prints
`PASS`/`FAIL` for each, plus a final `N/8 checks passed.` summary. Compare
against `solution.py` (`python3 solution.py`) if you get stuck — it
should print `8/8 checks passed.` and exit cleanly.
