# Chapter 8 Practice: Denylist vs. Allowlist, Concretely

This chapter's lesson names a trade-off in the abstract: a denylist
stays usable but can only block what someone thought to write a
pattern for; an allowlist is safer by default-deny construction but
blocks anything unanticipated. This practice script makes that trade-off
concrete by running the same eight commands through both checkers and
printing the results side by side.

## How to run

No `openai` package, no Ollama, no network -- just Python 3.

```bash
python3 --version
python3 starter.py
```

## What to do

Before running it, read the eight commands defined in `COMMANDS` and,
for each one, predict what each checker (`denylist_check` and
`allowlist_check`) would return: `ALLOW` or `BLOCK`. Write your eight
pairs of predictions down. Then run the script and compare the printed
table against them.

Pay particular attention to the two commands where the two checkers
disagree (`npm run build` and the piped `curl | sh` command) — that
disagreement is not a bug in either checker, it's the trade-off itself,
made visible.

## Checking your work

`solution.py` is functionally identical to `starter.py` — this practice
script has no blanks to fill in, it's meant to be read, predicted
against, and run. `solution.py`'s docstring includes the full answer
key if you want to check yourself without re-deriving it from the code.

## Scenario bank

See `index.html` for seven additional scenario-style judgment
questions — realistic situations you might hit building or reviewing a
real agent's file/shell/git tool layer, each asking you to reason from
this chapter's mechanism rather than just re-run the script.
