# Chapter 10 Project: Review a Deliberately-Flawed AI-Generated PR

This is Module 4's real assessment lab, per
`docs/curriculum/CURRICULUM_MAP.md`: "a deliberately-flawed AI-generated
PR to review and fix." Module 4 is one chapter carrying the whole
module, and this project is built to match that weight — a real,
multi-file, plausible-looking PR, not a single short snippet.

## The story

An agent was given this task: "Add a weekly sales report: aggregate
raw daily sales records into a weekly total and average order value,
export the result to CSV, and build the email that sends the CSV to a
distribution list. Acceptance: the export runs and produces a CSV; the
email message builds successfully." It came back reporting success,
with three files — exactly what `flawed_pr/` contains:

- **`flawed_pr/aggregate.py`** — turns raw daily records into weekly
  totals and an average order value.
- **`flawed_pr/export_csv.py`** — writes the aggregated rows to CSV.
- **`flawed_pr/notify.py`** — builds the email message with the CSV
  attached.

The agent's own closing message: *"Implemented aggregate.py,
export_csv.py, and notify.py. I ran a quick smoke test — imported all
three modules, called `total_revenue()` and `write_report()` against a
small sample, and both worked. The report is ready to wire into the
weekly job."*

Read that closing message again once you've done your own review.
Notice exactly what it says was tested, and what it doesn't mention
testing at all.

## Your task

Review `flawed_pr/` the way Chapter 3 and this chapter both taught:
don't just read it and see if it "looks right" — for every unfamiliar
or load-bearing call, check whether it's actually real; for every
function with a boundary, a default argument, or a condition, trace a
concrete case by hand. You have two tools for this:

1. **Read the three files directly.** They're short — under 40 lines
   each.
2. **Run `python3 starter.py`** (after filling in its four TODOs — see
   below), which builds the exact mechanical checks this chapter
   teaches into a runnable harness against the real files.

Write down every flaw you find, and for each one, note whether it's a
hallucinated API or a logical bug, and which of Chapter 3's five
review questions would have caught it. Then compare against
`review_answer_key.md`.

## Running the review harness

`starter.py` is a review harness with four functions left as `TODO`s:
`method_exists` (introspection), `try_run` (actually running a call
and capturing whether it crashes), `trace_week_boundary` (tracing
`aggregate.filter_week`'s actual output against its own docstring),
and `trace_mutable_default_leak` (checking `notify.build_message`'s
signature for a mutable default). Fill them in, then:

```bash
python3 --version
cd chapters/chapter-10-detecting-hallucinated-apis-and-logical-bugs/project
python3 starter.py
```

No `pandas`, no `requests`, no network, no extra installs — every flaw
in this PR is reachable with Python's own standard library.
`solution.py` is the same harness fully filled in; run
`python3 solution.py` to see the complete report, including a summary
of every real flaw found and the one line that's deliberately fine.

## What "done" looks like

Your own review (written down, or via the harness) should identify:

- **3 flaws that crash the instant the exact call actually runs** —
  each catchable by the "does it actually run" check alone.
- **1 flaw that runs cleanly but produces the wrong result**, only
  visible by tracing a concrete boundary case against the function's
  own documented contract.
- **1 flaw that doesn't crash on a single call, but leaks state across
  multiple calls** — the kind of bug a one-shot smoke test structurally
  cannot see, no matter how carefully it's run.
- **1 line that looks like it could be a Chapter 3 rounding-bug
  callback, but is actually fine and justified** — don't flag it,
  and be able to say why not.

Full explanation of all six items is in
[`review_answer_key.md`](review_answer_key.md) — read it after you've
done your own pass, not before.
