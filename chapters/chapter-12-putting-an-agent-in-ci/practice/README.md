# Chapter 12 Practice: What Happens to This Tool Call, Interactively vs. in CI?

`starter.py`/`solution.py` hand you six real tool calls, each evaluated
against `project/solution.py`'s actual `TOOL_POLICY`, `TOOL_POLICY_CI`,
`CI_SCRATCH_PREFIX`, and `PROTECTED_BRANCHES` (the exact ones this
chapter ships, not a hypothetical). Several have a twist a plain tier
lookup in ONE mode doesn't capture -- the point of this bank is
predicting what changes, and what doesn't, between interactive and CI
mode for the SAME call.

## How to run

No external packages, no network -- just Python 3.

```bash
python3 --version
python3 starter.py
```

## What to do

Before running it, read each of the six scenarios and predict TWO
outcomes: what happens interactively, and what happens in CI mode. Some
scenarios are the same for both (a read-only tool); some genuinely
differ (a write that's confirmed-and-denied interactively but
scope-checked-and-allowed in CI); one shows a tier being MORE permissive
in CI while another kind of call to the SAME tool is still refused by a
scope check underneath that tier. Write your twelve predictions down (six
scenarios x two modes). Then run the script -- it prints each scenario
followed by its own answer key -- and compare.

## Checking your work

`solution.py` is functionally identical to `starter.py` -- this
practice script has no blanks to fill in, it's meant to be read,
predicted against, and run. Each scenario's answer key is printed
directly by the script, so there's nothing separate to check against.

## Scenario bank

See `index.html` for additional scenario-style judgment questions --
realistic situations involving the two-policy design, the scratch and
branch scope checks, and the human-review question this chapter closes
on, each asking you to reason from the actual mechanism rather than
just re-run the script.
