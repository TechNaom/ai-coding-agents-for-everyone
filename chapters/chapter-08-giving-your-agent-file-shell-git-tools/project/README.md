# Chapter 8 Project: Extend the Agent With One New Tool of Your Own

This is Module 3's real **Level 2 (Assisted)** project, per
`docs/curriculum/CURRICULUM_MAP.md`: extend a provided minimal agent
with one new tool, from a partial scaffold. It's the graded version
Chapter 7's `project/index.html` pointed forward to.

## What's already built for you

`starter.py` is Chapter 7's reference agent (`read_file`, `write_file`,
`run_shell_command`, the loop, `dispatch_tool_call`'s defensive
handling — none of that changed) plus everything Chapter 8's lesson
built:

- **`edit_file`** — a safer, targeted alternative to `write_file` that
  replaces one exact, unambiguous occurrence of text and fails cleanly
  if the text is missing or ambiguous.
- **`git_status`** and **`git_diff`** — read-only git integration, so
  the agent can check its own work.
- A **hardened `run_shell_command`** — refuses commands matching a
  named denylist of destructive patterns (`rm -rf /`, `sudo`,
  force-pushes, and a few others) before running anything.

All five of those already have full schema entries, real functions
routed through `_safe_path()`, and entries in `TOOL_FUNCTIONS`. You
don't need to touch any of it.

## Your task

Add **one new tool** of your own choosing, following the exact pattern
every existing tool uses. `starter.py`'s module docstring has five
concrete ideas (`list_directory`, `append_to_file`, `git_log`,
`file_exists`, `count_lines`) if you want a starting point, but picking
something else entirely is fine and arguably better practice.

Two `# TODO` markers in `starter.py` show you where to add code:

1. One inside the `TOOLS` list, for your new tool's schema entry.
2. One just above `TOOL_FUNCTIONS`, for your new tool's real function
   (plus registering it in `TOOL_FUNCTIONS` itself, which is a third,
   small edit right there).

Follow the four-step pattern the docstring spells out: a precise schema
description, a function that routes any path argument through
`_safe_path()`, clean `"error: ..."` strings for expected failure
cases instead of letting exceptions fall through to
`dispatch_tool_call`'s generic handler, and a `TOOL_FUNCTIONS` entry.

## How to verify your work

You don't need a live Ollama server to check that your new tool
function itself is correct — that's the same lesson Chapters 7 and 8's
exercises/practice both make: test the tool layer independent of the
model. From this directory:

```bash
python3 -c "
import starter as s
import os

os.makedirs(s.WORKSPACE, exist_ok=True)
# call your new function directly, the same way dispatch_tool_call would
print(s.your_new_function('some/path'))
# and confirm it rejects an escape attempt the same way the others do:
try:
    s._safe_path('../../etc/passwd')
    print('FAIL: should have raised')
except ValueError as e:
    print('OK:', e)
"
```

Once you're confident the function itself is correct, run the whole
agent end to end against a real local model:

```bash
pip install openai
ollama pull llama3.2       # ~2GB download, see Chapter 7's lesson for hardware notes
ollama serve                # if it isn't already running
python3 starter.py
```

Give it a task in `main()` that specifically exercises your new tool
(the way `solution.py`'s own task string asks for `list_directory`),
and watch the printed step-by-step trace to confirm the model actually
called your tool and got back what you expected. If Ollama isn't
reachable, both `starter.py` and `solution.py` detect that, print a
clear message, and exit 0 instead of crashing — the same
graceful-degradation behavior Chapter 7 established.

## Review your own diff

Before calling it done, review your own change against Chapter 3's
five-question checklist — specifically:

- **Question 2** — did it touch anything outside the stated boundary?
  (Did you actually route every path through `_safe_path()`, or did
  you skip it "just this once" the way the AI-produced `list_files` in
  Chapter 7's `project/solution.py` did?)
- **Question 4** — is it consistent with the rest of the file's
  patterns? (Does your tool's description clearly distinguish it from
  every other tool's, the way Chapter 8's lesson discusses? Does a
  missing-file/missing-directory case return a clean `"error: ..."`
  string instead of an uncaught exception?)

`solution.py` shows one fully worked example (`list_directory`) if you
want to compare your approach against a reference — but the goal is a
correct tool of your own choosing, not a match against
`solution.py`'s specific pick.
