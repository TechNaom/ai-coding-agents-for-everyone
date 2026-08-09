# Chapter 9 Exercises: The MCP Integration Logic, Testable Offline

These exercises build and test the three pieces of `project/solution.py`'s
MCP integration that carry the most real design risk: the schema
translation that must correctly hide the harness-injected `workspace`
argument from the model (`strip_injected_args`), the dispatch-routing
decision that must correctly tell a local tool apart from an MCP tool
(`classify_tool_call`), and the result-unpacking logic that must
correctly handle an MCP tool's error vs. success shape
(`mcp_result_to_text`). All three are testable completely offline —
no `openai` package, no `mcp` package, no Ollama, no network, no real
subprocess.

## How to run

```bash
python3 --version
python3 starter.py
```

`starter.py` will raise `NotImplementedError` until you fill in the
three functions below. That's expected — the same "runs and tells you
exactly what's missing" pattern Chapters 7 and 8's exercises used.

## Exercise 1 — `strip_injected_args`

Find `TODO 1` inside `strip_injected_args`. This is the same logic
`connect_git_tools()` runs on every discovered MCP tool's schema before
appending it to `TOOLS`: strip a set of harness-injected argument names
(like `workspace`) out of both `properties` and `required`, without
mutating the input, so the model never sees an argument it has no
reliable way to supply correctly.

## Exercise 2 — `classify_tool_call`

Find `TODO 2` inside `classify_tool_call`. This is the same three-way
branch `dispatch_tool_call` runs on every tool call: is this name a
local Python function, a known MCP tool, or neither?

## Exercise 3 — `mcp_result_to_text`

Find `TODO 3` inside `mcp_result_to_text`. This is the same
result-unpacking logic `MCPBridge._worker` runs on every MCP
`call_tool()` response: format an error clearly with the tool's name
if `is_error` is true, otherwise return the first content block's
text, falling back to `structured_content` if there's no content at
all.

## Checking your work

Run `python3 starter.py` after filling in all three functions. The
built-in test harness at the bottom of the file runs 11 checks and
prints `PASS`/`FAIL` for each, plus a final `N/11 checks passed.`
summary. Compare against `solution.py` (`python3 solution.py`) if you
get stuck — it should print `11/11 checks passed.` and exit cleanly.

## Exercise bank

Tasks 4-6 (see `index.html`) go beyond the three functions above: a
by-hand trace of what a specific malformed MCP schema produces,
reasoning through what happens if a tool name collides between
`TOOL_FUNCTIONS` and `MCP_TOOL_NAMES`, and a written review of a
hypothetical MCP-integration diff with a real, deliberately-planted
flaw — using Chapter 3's five-question review checklist, the same
skill Module 3's own assessment is built around. Tasks 4-6 are the
production-gear tier — harder, more ambiguous judgment calls, not
clean textbook cases.
