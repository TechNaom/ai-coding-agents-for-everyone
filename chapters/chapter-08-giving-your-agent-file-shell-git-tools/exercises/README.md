# Chapter 8 Exercises: A Safer Edit Tool and a Shell Command Denylist

These exercises build and test the two pieces of this chapter's tool
layer that carry the most real design risk: `edit_file`'s
ambiguous-match refusal (the logic that keeps a targeted edit from
silently guessing which occurrence you meant) and
`run_shell_command`'s denylist check (the logic that refuses a
recognized dangerous command before it ever runs). Both are testable
completely offline — no `openai` package, no Ollama, no network.

## How to run

```bash
python3 --version
python3 starter.py
```

`starter.py` will raise `NotImplementedError` until you fill in the two
functions below. That's expected — the same "runs and tells you
exactly what's missing" pattern Chapter 7's exercises used.

## Exercise 1 — `edit_file_stub`

Find `TODO 1` through `TODO 4` inside `edit_file_stub`. You're
implementing the same logic as the lesson's real `edit_file`, just
against an in-memory `FAKE_DISK` dict instead of the real filesystem:
reject a missing file, reject a find string that doesn't appear at all,
reject a find string that appears more than once (the core safety
property — never guess which occurrence was meant), and otherwise
perform the replacement.

## Exercise 2 — `is_command_blocked`

Find `TODO 1` through `TODO 3` inside `is_command_blocked`. This is the
same check the lesson's hardened `run_shell_command` runs before
executing anything: walk a list of `(pattern, reason)` pairs, return
the first matching reason, or `None` if the command doesn't match
anything in the list.

## Checking your work

Run `python3 starter.py` after filling in both functions. The built-in
test harness at the bottom of the file runs 9 checks and prints
`PASS`/`FAIL` for each, plus a final `N/9 checks passed.` summary.
Compare against `solution.py` (`python3 solution.py`) if you get stuck
— it should print `9/9 checks passed.` and exit cleanly.

## Exercise bank

Tasks 3-6 (see `index.html`) go beyond the two functions above: a
by-hand trace of a specific ambiguous-match case, extending the
denylist for a real incident without breaking a legitimate command,
constructing a one-character-difference ambiguity case, and a written
review of a hypothetical `git_commit` design's actual safety
properties. Tasks 4-6 are the production-gear tier — harder, more
ambiguous judgment calls, not clean textbook cases.
