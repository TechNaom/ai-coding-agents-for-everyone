# Chapter 9 Practice: Reviewing MCP-Integration Diffs, Concretely

Module 3's assessment (per `docs/curriculum/CURRICULUM_MAP.md`) is a
working code review checklist, not a written exam — this practice
bank's runnable script makes that concrete: four small, plausible-
looking MCP-integration diffs, each with exactly one deliberate,
realistic flaw, using the same five review questions Chapter 3 taught.

## How to run

No `openai` package, no `mcp` package, no Ollama, no network — just
Python 3.

```bash
python3 --version
python3 starter.py
```

## What to do

Before running it, read each of the four diffs printed by the script
and, for each one, predict: what's the one flaw, and which of Chapter
3's five review questions would catch it (does it match its stated
goal, does it stay inside its boundary, is every change justified, is
it consistent with the rest of the file's patterns, is it a root-cause
fix or a symptom fix)? Write your four predictions down. Then run the
script — it prints each diff followed by its own answer key — and
compare.

## Checking your work

`solution.py` is functionally identical to `starter.py` — this
practice script has no blanks to fill in, it's meant to be read,
predicted against, and run. Each diff's answer key is printed directly
by the script, so there's nothing separate to check against.

## Scenario bank

See `index.html` for seven additional scenario-style judgment
questions — realistic situations you might hit building or reviewing a
real agent's MCP integration, each asking you to reason from this
chapter's mechanism and Chapter 3's review discipline rather than just
re-run the script.
