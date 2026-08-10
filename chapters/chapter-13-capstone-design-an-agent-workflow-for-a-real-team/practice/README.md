# Chapter 13 Practice Bank: Scenario Judgment for a Regulated CI Agent

A runnable script (`starter.py` / `solution.py` in this folder) hands
you six real tool calls and asks what Meridian Ledger's regulated-org
CI policy decides for each one, and why. Predict each outcome yourself
before running it, then work through the six scenarios below, which
extend the same judgment to situations the script's six calls don't
cover.

Run:

    python3 solution.py

## Scenarios

**Scenario · The report that never gets written.** The CI
troubleshooting agent investigates a failing test in
`ledger/gl_posting/rounding.py`, correctly diagnoses the bug in its
final message, but every `write_file` call it tries (even inside
`ci-scratch/`, with a summary that only quotes a few lines of the
GL file for context) succeeds — the SUMMARY isn't a regulated path
itself, even though it's ABOUT one. Does this chapter's design
consider that acceptable? What's the actual boundary — is it "never
touch a regulated path" or "never touch a regulated path's actual
CONTENT," and does `classify_path` (which only looks at path strings)
enforce the second one at all?

**Scenario · A dependency bump that touches everything.** A routine
dependency version bump touches 40 files across the repo, including
one file under `ledger/reconciliation/`, because that file imports the
bumped package. The CI troubleshooting agent is asked to auto-fix a
resulting type error in 39 of those 40 files. Using this chapter's
`git_commit` staged-path check, what happens if the agent stages all
40 files in one commit? What would you recommend the agent (or the
harness around it) do instead, so the 39 legitimate fixes aren't
blocked by the one regulated file mixed into the same change?

**Scenario · The actor field that lies.** A workflow sets
`MERIDIAN_TRIGGERED_BY` to a hardcoded string,
`"scheduled-nightly-run"`, for every nightly scheduled CI run, since no
specific human triggered it. Every commit this run produces passes the
"actor is non-empty" check and gets attributed to that string. Does
this satisfy ADR-003's stated goal (SOX individual accountability), or
does it just satisfy the CODE'S check while missing the actual
requirement? What's the difference between "the field is populated"
and "the field identifies an accountable individual"?

**Scenario · A regulated path that used to be safe.** Eighteen months
after this design ships, `analytics/legacy_reports/` — long
classified as neither CDE nor GL — starts receiving a new kind of
export that includes unmasked account numbers, because a well-meaning
engineer added a "raw data" mode to an existing report generator, with
no change to `CDE_PATH_PATTERNS`. Using this chapter's own honest-gaps
framing (and Chapter 12's policy-drift discussion), whose
responsibility is it to catch this, and at what point in the process —
code review of the report-generator change, or a separate periodic
audit of `CDE_PATH_PATTERNS` itself?

**Scenario · Two failing checks, one root cause.** The CI
troubleshooting agent runs `run_tests`, gets a failure in
`ledger/gl_posting/rounding_test.py`, and — correctly barred from
writing to `ledger/gl_posting/` directly — writes a proposed fix to
`ci-scratch/gl_posting_fix_proposal.py` instead, with a clear summary.
A reviewer later merges that proposal by hand, moving the code from
scratch into the real GL path themselves. Does this outcome match
ADR-002's intended design, or does something about "a human copies
code an agent wrote in a scratch file directly into a regulated path"
deserve MORE scrutiny than an ordinary human-authored PR to that same
path would get — and if so, what, specifically?

**Scenario · The audit log itself becomes evidence.** Six months into
production, a PCI-DSS QSA assessment asks Meridian Ledger to produce
every CI-agent-triggered action that touched (or attempted to touch) a
CDE path in the last quarter. Using this chapter's `audit_log()`
design (every call logged BEFORE the tool runs, including refused
ones), can this question actually be answered from the log file alone?
What's missing, if anything — and does a `REFUSED` decision belong in
that answer at all, or only `ALLOWED` ones?
