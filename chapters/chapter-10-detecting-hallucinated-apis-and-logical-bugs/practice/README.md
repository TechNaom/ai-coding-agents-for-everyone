# Chapter 10 Practice: Find the Flaw in Six Short Snippets

Module 4's own assessment leans on exactly this skill — this practice
bank makes it concrete before you hit the full multi-file project.
`starter.py`/`solution.py` hand you six small, plausible-looking
snippets, each with exactly one deliberate flaw, spanning the
categories the lesson names: a hallucinated argument, two hallucinated
method names (one a near-miss on a real method, one a fully invented
name), an inverted boolean condition, an off-by-one slicing mistake,
and an operator-precedence trap that happens to be correct today by
accident.

## How to run

No external packages, no network — just Python 3.

```bash
python3 --version
python3 starter.py
```

## What to do

Before running it, read each of the six snippets and, for each one,
predict two things: is the flaw a hallucinated API or a logical bug,
and what's the one thing actually wrong? Write your six predictions
down. Then run the script — it prints each snippet followed by its own
answer key — and compare.

## Checking your work

`solution.py` is functionally identical to `starter.py` — this
practice script has no blanks to fill in, it's meant to be read,
predicted against, and run. Each snippet's answer key is printed
directly by the script, so there's nothing separate to check against.

## Scenario bank

See `index.html` for additional scenario-style judgment questions —
realistic situations you might hit reviewing a real agent's diff for
hallucinated APIs or logical bugs, each asking you to reason from this
chapter's mechanism and Chapter 3's review discipline rather than just
re-run the script.
