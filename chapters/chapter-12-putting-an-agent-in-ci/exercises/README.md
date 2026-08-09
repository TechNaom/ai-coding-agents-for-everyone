# Chapter 12 Exercises: The CI Policy Layer's Building Blocks, Testable Offline

These exercises rebuild the three pieces `project/solution.py`'s
CI-specific policy layer is made of, as small standalone functions: a
scratch-scope check (`in_scratch`), a protected-branch check
(`is_protected_branch`), and the mode-aware, fail-closed policy lookup
(`resolve_tier`) that stands in for `active_policy()` + `check_permission()`
combined. All three are testable completely offline -- no live model, no
Ollama, no network, no real git repo.

## How to run

```bash
python3 --version
python3 starter.py
```

`starter.py` will raise `NotImplementedError` until you fill in the
three functions below -- the same "runs and tells you exactly what's
missing" pattern Chapter 11's exercises used.

## Exercise 1 -- `in_scratch`

Find `TODO 1` inside `in_scratch`. Watch out for the specific trap this
exercise is built around: `str.lstrip()` strips ANY combination of the
given characters repeatedly from the left, not a literal prefix. A naive
`path.lstrip("./")` mangles `"../../etc/passwd"` into `"etc/passwd"` --
silently destroying the exact signal (`../`) that would make a real
scope-escape attempt visible. The test harness includes a check built
specifically to catch this mistake.

## Exercise 2 -- `is_protected_branch`

Find `TODO 2` inside `is_protected_branch`. The interesting case here
isn't the obvious one (`"main"` is protected) -- it's what happens when
the branch can't be determined at all (`None`, mirroring
`_current_branch()` returning `None` when `git rev-parse` fails). "We
don't know what branch this is" has to be treated as protected, not as
"probably fine."

## Exercise 3 -- `resolve_tier`

Find `TODO 3` inside `resolve_tier`. This is `active_policy()` +
`check_permission()` from `project/solution.py`, combined into one pure
function: pick the right policy dict based on `ci_mode`, then do a
fail-closed lookup on it. The test harness checks that the SAME tool
name can resolve to a DIFFERENT tier depending on mode (both more
permissive, for `write_file`, and more restrictive, for `edit_file`) --
and that an unclassified tool defaults to `BLOCKED` in BOTH modes, not
just one.

## Checking your work

Run `python3 starter.py` after filling in all three functions. The
built-in test harness runs 17 checks and prints `PASS`/`FAIL` for each,
plus a final `N/17 checks passed.` summary. Compare against
`solution.py` (`python3 solution.py`) if you get stuck -- it should
print `17/17 checks passed.` and exit cleanly.

## Exercise bank

Tasks 4-6 (see `index.html`) go beyond the three functions above:
designing a tier and scope for a genuinely new CI tool, tracing a real
environment-variable footgun in how `CI_MODE` gets read, and reviewing a
PR that updates one policy dict but forgets the other. Tasks 4-6 are the
production-gear tier -- harder, ambiguous, real judgment calls, not
clean textbook cases.
