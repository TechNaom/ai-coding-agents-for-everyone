# Chapter 11 Practice: Is This Tool Call ALLOWED, REQUIRES_CONFIRMATION, or BLOCKED?

`starter.py`/`solution.py` hand you six real tool calls, each evaluated
against this chapter's actual `TOOL_POLICY` and `SHELL_DENYLIST` (the
exact ones in `project/solution.py`, not a hypothetical). Some are a
straightforward tier lookup; a few have a twist that a tier lookup
alone doesn't fully capture — a denylisted command inside a
`REQUIRES_CONFIRMATION` tool, and a brand-new tool nobody explicitly
classified at all.

## How to run

No external packages, no network — just Python 3.

```bash
python3 --version
python3 starter.py
```

## What to do

Before running it, read each of the six scenarios and predict two
things: which of the three tiers applies, and whether anything else
about the specific call matters beyond a plain tier lookup. Write your
six predictions down. Then run the script — it prints each scenario
followed by its own answer key — and compare.

## Checking your work

`solution.py` is functionally identical to `starter.py` — this
practice script has no blanks to fill in, it's meant to be read,
predicted against, and run. Each scenario's answer key is printed
directly by the script, so there's nothing separate to check against.

## Scenario bank

See `index.html` for additional scenario-style judgment questions —
realistic situations involving the permission layer, the sandboxing
limits, and the least-privilege tool-design lens this chapter builds,
each asking you to reason from the actual mechanism rather than just
re-run the script.
