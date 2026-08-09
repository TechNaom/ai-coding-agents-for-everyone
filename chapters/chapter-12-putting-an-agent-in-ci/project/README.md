# Chapter 12 Project: Wire a Minimal Agent Into a CI Check

This is Module 5's second real lab, per `docs/curriculum/CURRICULUM_MAP.md`:
"wire a minimal agent into a CI check." It resolves the exact tension
Chapter 11's own closing section set up for this chapter: Chapter 11's
agent, dropped into CI unchanged, is safe but useless (every
`REQUIRES_CONFIRMATION` tool denies automatically, since there is no
human on the other end of `input()`). Your job is the fix that makes it
useful again without reopening Chapter 8's self-granted-permission flaw.

## What's already built for you

`starter.py` is Chapter 11's exact permission-scoped agent — `TOOL_POLICY`,
`check_permission`, `confirm_with_human`, `dispatch_tool_call`, the
resolved `git_commit` — all copied forward unchanged, none of it is a
TODO. Two things are new on top of that baseline:

- **`run_tests`** — a new, narrow, bounded tool (no arguments at all)
  that runs this workspace's test suite. It's the least-privilege fix
  Chapter 11's own retrospective named for `run_shell_command`'s
  "structurally over-privileged by nature" problem, applied to exactly
  the one CI use case that needs it.
- **`CI_MODE`** — a flag read once, at import time, from the
  `ACAFE_CI_MODE` environment variable. Nothing downstream (not the
  model, not any tool call, not any part of the agent's own output) can
  change it once the process starts.

## Your task

Four TODOs in `starter.py`, all part of one connected idea: a SECOND
policy for CI runs, decided ahead of time and paired with code-level
scopes that substitute for the human confirmation CI can't give.

1. **TODO 1** (`write_file`): refuse to write outside `ci-scratch/`
   when `CI_MODE` is on.
2. **TODO 2** (`TOOL_POLICY_CI`): the CI-specific policy dict itself.
3. **TODO 3** (`git_commit`): refuse to commit to a protected branch
   (`main`/`master`) when `CI_MODE` is on.
4. **TODO 4** (`run_agent`): a wall-clock budget, so a run that thrashes
   in CI stops on its own instead of burning real, metered CI minutes.

Full spec is in `starter.py`'s module docstring and each TODO's own
comment.

## What "done" looks like

Running `python3 starter.py` (interactive-mode demo) and
`ACAFE_CI_MODE=1 python3 starter.py` (CI-mode demo) should each run a
full scripted demonstration with no live model needed:

- **Interactive mode**: identical to Chapter 11 — `read_file` runs
  instantly, `write_file` pauses for stdin and denies cleanly with no
  human attached, `send_email` is refused outright.
- **CI mode**: `run_tests` runs a real (deliberately failing) test
  suite; `write_file` succeeds inside `ci-scratch/` but is refused
  outside it; `edit_file` and `run_shell_command` are refused outright,
  no prompt; `git_commit` succeeds on a scratch branch (`ci/auto-fix`)
  but is refused on `main`; `send_email` is refused in every mode.

None of this requires Ollama to be running — like Chapter 11's project,
the permission layer is pure harness logic, fully verifiable on its own.

## The two use cases this project covers

1. **A PR review bot** (`demo_pr_review_bot`) — entirely read-only,
   needs zero policy changes at all. It's already demonstrated for you,
   not a TODO, precisely because it's the easy half of "putting an agent
   in CI": every tool it needs (`read_file`, `git_diff`) was already
   `ALLOWED` under Chapter 11's policy.
2. **A CI troubleshooting agent** (`demo_ci_mode`) — needs real write
   capability against a live, disposable repo with a real failing test.
   This is where your TODOs actually earn their keep — it's the harder,
   more interesting design problem this chapter is really about.

## `example-ci-workflow.yml`

A realistic (illustrative-only) GitHub Actions workflow showing how
`solution.py`'s two use cases would actually get wired into a real
project's CI: a read-only PR-review job that posts a comment, and a
troubleshooting job that runs only after a real test job fails, opens a
scratch branch, runs the agent under `ACAFE_CI_MODE=1`, and opens a
**draft** pull request — never merges anything itself. This file is
**not** connected to this course repo's real CI and is not run by it;
it's example content for the lesson, kept in this project folder on
purpose so it's easy to find alongside the code it documents.

## Before you call it done

Run `python3 starter.py < /dev/null` (interactive mode) and
`ACAFE_CI_MODE=1 python3 starter.py < /dev/null` (CI mode) — with stdin
closed, matching real CI. Check specifically:

- Does `write_file` inside `ci-scratch/` succeed in CI mode, but get
  refused outside it — even though `TOOL_POLICY_CI["write_file"]` is
  `ALLOWED`? (If both succeed, or both fail, TODO 1 isn't right yet.)
- Does `git_commit` succeed on the scratch branch but get refused on
  `main`? (Same pattern as above, TODO 3.)
- Does `edit_file` get refused with NO confirmation prompt at all in CI
  mode — not "asked and denied," but never asked in the first place?
- Does the interactive-mode demo still behave exactly like Chapter 11's,
  completely unaffected by anything you changed for CI mode?

`solution.py` is the fully filled-in reference. Compare your output
against it in BOTH modes, not just your source code — the observable
behavior across all the scenarios in each mode is what actually proves
the CI-specific scoping works.
