# Chapter 11 Project: Add Permission Scoping to the Module 3 Agent

This is Module 5's real lab, per `docs/curriculum/CURRICULUM_MAP.md`:
"add permission scoping to the Module 3 agent." It resolves the exact
question Chapter 8 named and deliberately left open — whether an agent
should ever be able to call `git_commit`, and more generally, what
actually stops a model from approving its own destructive tool call.

## What's already built for you

`starter.py` is Chapter 8's reference agent, copied forward unchanged:
`read_file`, `write_file`, `edit_file`, `list_directory`,
`run_shell_command` (denylist-hardened, now also running with a
restricted environment and real CPU/memory limits — see the lesson's
sandboxing section), `git_status`, `git_diff`, the loop, and
`dispatch_tool_call`'s defensive JSON/KeyError/generic-exception
handling. Two things are new on top of that baseline:

- **A `git_commit` tool schema and real function** — the tool Chapter
  8 sketched, pointed out the flaw in (`confirm=True` doesn't stop a
  model from setting it itself), and shipped nowhere. It's here now,
  and notice its function signature has no `confirm` parameter at all
  — approval doesn't live inside the tool's own arguments anymore.
- **A `send_email` stub tool** — never meant to actually run; it
  exists purely so this project has a concrete example of the
  strictest policy tier (see below) wired into a real tool, not just
  described in prose.

## Your task

`TOOL_POLICY`, `check_permission`, `confirm_with_human`, and the
permission check inside `dispatch_tool_call` are all `# TODO`s in
`starter.py`. Fill them in so that:

1. Every tool has an explicit tier: **`ALLOWED`** (read-only tools run
   immediately, no prompt), **`REQUIRES_CONFIRMATION`** (state-changing
   tools pause and ask a real human, on real stdin, before running),
   or **`BLOCKED`** (never runs, no matter what — no prompt, because
   there's nothing to confirm).
2. A tool name that ISN'T explicitly classified in `TOOL_POLICY`
   defaults to `BLOCKED`, not `ALLOWED` — fail closed, not open.
3. The confirmation prompt uses real `input()`, and denies by default
   if `input()` hits `EOFError` (no human actually there to answer) —
   a "confirmation" that defaults to yes when nobody's watching isn't
   a confirmation.
4. `dispatch_tool_call` checks the policy **before** calling the real
   tool function — a blocked or unconfirmed call never reaches
   `read_file`/`write_file`/etc. at all.

Full step-by-step spec is in `starter.py`'s module docstring and each
TODO's own docstring. This is the whole lab — there's no separate
"pick your own tool" step this time, because the point isn't adding
capability, it's constraining it.

## How to verify your work

Run the file directly. `demo_permission_layer()` runs first and needs
no live model at all — it exercises all three tiers with scripted tool
calls:

```bash
python3 starter.py
```

You should see: `read_file` returns instantly with no prompt;
`write_file` prints a confirmation prompt and (since there's no
terminal actually attached when you just run the file non-interactively,
or if you answer anything other than y/yes) is denied; `send_email` is
refused instantly with no prompt at all; the unclassified demo tool is
also refused instantly, proving your fail-closed default works.

To see the confirmation path actually grant something, run it
interactively and type `y` when prompted, or drive it directly:

```bash
python3 -c "
import starter as s
import builtins
builtins.input = lambda prompt='': 'y'   # simulate a human saying yes
import os
os.makedirs(s.WORKSPACE, exist_ok=True)
open(os.path.join(s.WORKSPACE, 'demo.txt'), 'w').write('hi\n')
tc = s._FakeToolCall('write_file', {'path': 'demo.txt', 'content': 'updated\n'})
print(s.dispatch_tool_call(tc))
"
```

Once the permission layer itself is correct, optionally run the whole
agent end to end against a real local model:

```bash
pip install openai
ollama pull llama3.2       # ~2GB download, see Chapter 7's lesson for hardware notes
ollama serve                # if it isn't already running
python3 starter.py
```

If Ollama isn't reachable, this exits 0 with a clear message instead
of hanging or crashing — the request itself uses a short timeout for
exactly that reason. The permission-layer demo doesn't need Ollama at
all; you can fully verify this project's actual subject without ever
starting a model.

## Review your own diff

Before calling it done, check your work against the same discipline
Chapter 8's project asked for, applied to this chapter's specific
risk:

- Does every state-changing tool actually require confirmation, or did
  one slip through as `ALLOWED` by mistake?
- Does an unclassified tool name really default to `BLOCKED`, or did
  you write `TOOL_POLICY.get(name, ALLOWED)` by accident (the single
  most dangerous one-word typo possible in this file)?
- Does `send_email` get refused BEFORE `confirm_with_human` is ever
  called? (It should never prompt at all — there's nothing to confirm
  for a tool that can't run under any circumstances.)
- If you run the file with stdin closed or redirected from `/dev/null`
  (`python3 starter.py < /dev/null`), does the confirmation path deny
  cleanly instead of hanging or crashing?

`solution.py` is the fully filled-in reference. Compare your output
against it, not just your source code — the observable behavior across
all five demo scenarios is what actually proves the permission layer
works.
