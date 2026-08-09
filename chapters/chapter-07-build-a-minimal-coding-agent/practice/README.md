# Chapter 7 Practice: Watching the Stop Conditions Fire

Chapter 4 named the loop's ways of ending in the abstract. This practice
script makes all four you can meaningfully simulate without a live model
concrete: run a tiny scripted loop through four scenarios and watch, in
the printed output, exactly which stop condition fires and why.

## How to run

No `openai` package, no Ollama, no network -- just Python 3.

```bash
python3 --version
python3 starter.py
```

## What to do

Before running it, read the four scenarios defined in `main()`:

- **A** — the model reads two files, then produces a text-only turn.
- **B** — the model keeps calling `read_file` well past the step cap.
- **C** — the model tries to call `delete_file`, which this harness's
  boundary rule (`BLOCKED_TOOLS`) never allows.
- **D** — the model calls a tool that fails in a way it can't route
  around (a simulated permissions error).

Write down, for each one, which of Chapter 4's stop conditions (clean
stop, hard stop/step cap, boundary stop, failure stop) you expect to
fire — before running the script. Then run it and check the printed
`STOPPED: ...` line for each scenario against your prediction.

## Checking your work

`solution.py` is functionally identical to `starter.py` — this practice
script has no blanks to fill in, it's meant to be read, predicted
against, and run. `solution.py`'s docstring includes the answer key
(`A -> clean_stop, B -> step_cap, C -> boundary_stop, D -> failure_stop`)
if you want to check yourself without re-deriving it from the code.

## Scenario bank

See `index.html` for six additional scenario-style judgment questions —
realistic situations you might hit building or reviewing a real agent
harness, each asking you to reason from this chapter's mechanism rather
than just re-run the script.
