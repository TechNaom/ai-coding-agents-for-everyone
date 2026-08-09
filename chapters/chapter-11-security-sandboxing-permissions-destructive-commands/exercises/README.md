# Chapter 11 Exercises: The Permission Layer's Building Blocks, Testable Offline

These exercises rebuild the three pieces `project/solution.py`'s
permission-scope layer is made of, as small standalone functions: a
fail-closed policy lookup (`policy_for`), the full allow/confirm/block
decision flow with an injectable fake confirmation function instead of
real stdin (`evaluate_call`), and a shell-command threat-category
classifier (`classify_threat`). All three are testable completely
offline — no live model, no Ollama, no network.

## How to run

```bash
python3 --version
python3 starter.py
```

`starter.py` will raise `NotImplementedError` until you fill in the
three functions below — the same "runs and tells you exactly what's
missing" pattern prior chapters' exercises used.

## Exercise 1 — `policy_for`

Find `TODO 1` inside `policy_for`. One line: look a tool name up in a
policy dict, defaulting to `BLOCKED` (not `ALLOWED`) if the name isn't
present at all. This single default is arguably the most
security-relevant line of code in this entire chapter — get it backward
and every unclassified tool silently becomes safe-by-accident instead
of blocked-by-design.

## Exercise 2 — `evaluate_call`

Find `TODO 2` inside `evaluate_call`. This is `dispatch_tool_call`'s
permission-check logic, extracted into a pure function that takes a
fake confirmation function and a fake "run the tool" function as
arguments, so you can test the decision flow itself — does a blocked
tool ever reach the confirmation step? does a denied confirmation ever
reach the run step? — without needing real stdin or real tool side
effects.

## Exercise 3 — `classify_threat`

Find `TODO 3` inside `classify_threat`. Given a shell command string,
classify it into one of this chapter's four threat categories (data
loss, supply-chain/credential exposure, scope escape, irreversible
external effect) using simple keyword checks, in a specific priority
order — order matters here, because a command like
`cat ~/.aws/credentials` would incorrectly classify as scope escape
(it contains `~/`) if you checked scope escape before the more specific
credential-exposure check.

## Checking your work

Run `python3 starter.py` after filling in all three functions. The
built-in test harness runs 18 checks and prints `PASS`/`FAIL` for each,
plus a final `N/18 checks passed.` summary. Compare against
`solution.py` (`python3 solution.py`) if you get stuck — it should
print `18/18 checks passed.` and exit cleanly.

## Exercise bank

Tasks 4-6 (see `index.html`) go beyond the three functions above:
designing a policy for a tool this chapter never covered, tracing what
happens to a confirmation prompt when stdin is unavailable, and
reviewing a hypothetical PR that adds a new tool without updating
`TOOL_POLICY`. Tasks 4-6 are the production-gear tier — harder,
ambiguous, real judgment calls, not clean textbook cases.
