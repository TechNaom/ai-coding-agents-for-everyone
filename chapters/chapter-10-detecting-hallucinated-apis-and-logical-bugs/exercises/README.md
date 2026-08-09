# Chapter 10 Exercises: Three Mechanical Checks, Testable Offline

These exercises turn the lesson's mechanical checks into real, callable
functions: does a claimed method actually exist on a real object
(`method_actually_exists`), does an exact call actually run without
crashing your review, captured instead of raising
(`safe_call`), and does a function's own signature carry the classic
mutable-default-argument trap before you even read its body
(`has_mutable_default`). All three are testable completely offline —
no pandas, no requests, no network, just Python's own standard library.

## How to run

```bash
python3 --version
python3 starter.py
```

`starter.py` will raise `NotImplementedError` until you fill in the
three functions below. That's expected — the same "runs and tells you
exactly what's missing" pattern Chapters 7-9's exercises used.

## Exercise 1 — `method_actually_exists`

Find `TODO 1` inside `method_actually_exists`. This is the lesson's
cheapest check: given an object and a method name, confirm via
`hasattr()`/`callable()` whether that name is actually real — the
exact check that would have caught the hook's `ignore_na` and this
file's `write_all` before either was ever trusted.

## Exercise 2 — `safe_call`

Find `TODO 2` inside `safe_call`. This wraps the lesson's second
check — actually running the exact call with real arguments — so a
caller gets a structured `{"ok": ..., ...}` result back instead of a
crash, the same shape a review harness needs to check many calls in
one pass without one bad call stopping the whole run.

## Exercise 3 — `has_mutable_default`

Find `TODO 3` inside `has_mutable_default`. Given a function object,
inspect its real signature (`inspect.signature`) and flag whether any
parameter's default value is a mutable type (`list`, `dict`, `set`) —
a genuinely useful static check for the exact class of logical bug the
lesson's `headers={}` example walks through, catchable before you even
call the function once.

## Checking your work

Run `python3 starter.py` after filling in all three functions. The
built-in test harness at the bottom of the file runs 12 checks and
prints `PASS`/`FAIL` for each, plus a final `N/12 checks passed.`
summary. Compare against `solution.py` (`python3 solution.py`) if you
get stuck — it should print `12/12 checks passed.` and exit cleanly.

## Exercise bank

Tasks 4-6 (see `index.html`) go beyond the three functions above: using
`method_actually_exists` to actually check a real standard-library
claim you're unsure about, tracing a boundary case by hand for a
function with an off-by-one bug, and reviewing a small hypothetical
diff for a hallucinated API using this chapter's checks combined with
Chapter 3's five-question checklist. Tasks 4-6 are the production-gear
tier — harder, more ambiguous judgment calls, not clean textbook cases.
