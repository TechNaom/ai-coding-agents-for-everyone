# Chapter 9 Project: Swap git_status/git_diff for MCP-Based Versions

This is Module 3's Level 3 project: take Chapter 8's exact agent and
replace two of its hand-rolled tools (`git_status`, `git_diff`) with
versions served over MCP instead, from a separate, standalone server
process. It's the direct payoff of everything Module 3 built —
Chapter 7's loop, Chapter 8's tool-layer depth — proven by making the
loop keep working, unchanged, while where a tool call actually
executes moves outside this file entirely.

## What's in this directory

- **`mcp_git_server.py`** — a small, standalone MCP server exposing
  `git_status` and `git_diff` as MCP tools, built with the `mcp`
  Python SDK's `MCPServer` decorator API. This is NOT part of the
  agent — it's a separate process the agent connects to.
- **`starter.py`** — Chapter 8's agent with `git_status`/`git_diff`
  removed as local functions, and `connect_git_tools()` left as a
  `TODO`-marked stub for you to implement. Read its module docstring
  first — it's the full task.
- **`solution.py`** — `starter.py` with `connect_git_tools()` filled
  in, fully working.

## Your task

Implement `connect_git_tools()` in `starter.py`: connect to
`mcp_git_server.py` over MCP, discover its tools via `list_tools()`,
convert each one into this course's existing `TOOLS` schema shape, and
register its name in `MCP_TOOL_NAMES` so `dispatch_tool_call` (already
provided, unchanged) knows to route calls for it to the MCP server
instead of a local function. Full step-by-step guidance is in
`starter.py`'s module docstring and inside `connect_git_tools()`
itself.

## How to verify your work — no live model required

The MCP wiring itself doesn't need Ollama at all. You can call it
directly and inspect what it discovers:

```bash
pip install "mcp[cli]"
python3 -c "
import starter as s

ok = s.connect_git_tools()
print('connected:', ok)
print('tools in TOOLS now:', [t['function']['name'] for t in s.TOOLS])
print('MCP_TOOL_NAMES:', s.MCP_TOOL_NAMES)
"
```

You should see `connected: True`, `git_status` and `git_diff` present
in `TOOLS` (with their schemas NOT including a `workspace` field — see
below for why), and both names in `MCP_TOOL_NAMES`.

Then call a tool through `dispatch_tool_call` directly, bypassing the
model entirely, the same way Chapters 7-8's exercises tested dispatch
logic independent of a live model:

```bash
python3 -c "
import json
import starter as s

s.connect_git_tools()

class FakeFn:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class FakeTC:
    def __init__(self, name, arguments):
        self.function = FakeFn(name, arguments)
        self.id = 'call_1'

import os
os.makedirs(s.WORKSPACE, exist_ok=True)
print(s.dispatch_tool_call(FakeTC('git_status', json.dumps({}))))
s.MCP_BRIDGE.close()
"
```

If you run this inside a real git repository's `workspace/` directory
(`git init` it first), you should get back real `git status
--porcelain` output — from a completely separate process, over MCP,
with no model involved at all.

## The one thing you cannot verify without a live model

Whether the model itself correctly *chooses* to call `git_status` at
the right moment, given only the MCP-sourced schema (not one you
hand-typed), still needs a real run:

```bash
pip install openai "mcp[cli]"
ollama pull llama3.2       # ~2GB download, see Chapter 7's lesson for hardware notes
ollama serve                # if it isn't already running
python3 starter.py
```

If Ollama isn't reachable, both files detect that and exit 0 with a
clear message instead of crashing — the same graceful-degradation
behavior Chapters 7-8 established. If `mcp_git_server.py` can't be
reached, `connect_git_tools()` should print a clear message and let
the agent continue with its four remaining local tools rather than
crashing the whole run — that's a deliberate design choice, not a gap;
see the lesson's discussion of why a lost MCP connection shouldn't be
treated as fatal.

## Review your own diff

Before calling it done, review your own `connect_git_tools()` against
Chapter 3's five-question checklist — specifically:

- **Question 2** — did it touch anything outside the stated boundary?
  Specifically: did you strip `workspace` out of every discovered
  tool's schema before appending it to `TOOLS`, or did you leave it in
  and let the model try to guess an absolute path it has no way of
  knowing? (This is the exact MCP-flavored version of the
  `_safe_path()` discipline Chapter 8 taught for local tools.)
- **Question 4** — is it consistent with the rest of the file's
  patterns? Does a connection failure return `False` and a clear
  printed message, matching the graceful-degradation pattern every
  other failure path in this file already uses, or does it let an
  exception escape and crash the whole agent?

`solution.py` shows one fully worked, tested version if you want a
reference — but the goal is a correct, working `connect_git_tools()`,
not a byte-for-byte match.
