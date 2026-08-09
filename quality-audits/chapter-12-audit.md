# Chapter Quality Audit: Putting an Agent in CI

## Summary

- Chapter: 12 — Putting an Agent in CI (Module 5, Advanced, closes Module 5)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Live-tested-vs-logical-only disclosure

This chapter's actual subject — a second, CI-specific permission policy
plus two code-level scope checks (a scratch-write boundary, a
protected-branch check) that substitute for the human confirmation CI
cannot give — is, like Chapter 11's, pure Python control-flow logic
that needs no live model to verify. Every piece of it was independently,
directly executed this session, in both interactive and CI mode:

- **`project/solution.py`'s full policy layer, interactive mode**
  (`python3 solution.py < /dev/null`) — confirmed `TOOL_POLICY` behaves
  identically to Chapter 11's shipped version: `read_file` ran
  immediately; `write_file` printed a real confirmation prompt, hit
  `EOFError` on closed stdin, and denied cleanly; `send_email` was
  refused before any prompt.
- **`project/solution.py`'s full policy layer, CI mode**
  (`ACAFE_CI_MODE=1 python3 solution.py < /dev/null`) — confirmed, on a
  real, freshly-initialized disposable git repo with a real deliberately
  failing `unittest` test (never touching this course repo's own git
  history — see "safe to run in this repo's CI" below): (1) `run_tests`
  actually ran the test suite and returned a real `AssertionError`
  traceback; (2) `write_file` inside `ci-scratch/` actually wrote the
  file; (3) the SAME tool, called with a path outside `ci-scratch/`, was
  refused with a clean scope-violation error, even though its
  `TOOL_POLICY_CI` tier is `ALLOWED` — proving the tier and the scope
  check are genuinely independent, not just described as such; (4)
  `edit_file` was refused instantly, no prompt, no confirmation attempt
  at all; (5) `run_shell_command` was refused instantly, same way; (6)
  `git_commit` actually committed on a scratch branch
  (`ci/auto-fix`) — a real commit hash was produced; (7) `git_commit`,
  called again after checking out `main`, was refused with a clean
  protected-branch error, using `git rev-parse --abbrev-ref HEAD` read
  from the real repo, not a mocked value; (8) `send_email` was refused
  in CI mode too.
- **Mode independence, verified directly** — ran the full script twice,
  once with no environment variable and once with `ACAFE_CI_MODE=1` set
  for the WHOLE process, and diffed the two outputs: the interactive-mode
  demo section produces byte-for-byte identical output in both
  invocations (aside from a temp-directory path and a commit hash that
  necessarily differ each run), because `demo_interactive_mode()`
  explicitly forces `CI_MODE = False` for its own duration regardless of
  how the whole script was invoked. This exact bug (the interactive demo
  silently inheriting `CI_MODE=True` from the process environment) was
  caught live during this session by running with `ACAFE_CI_MODE=1` set
  and observing `write_file("demo.txt", ...)` get refused by the
  scratch-scope check instead of pausing for confirmation as it should
  have — fixed by having both `demo_interactive_mode()` and
  `demo_ci_mode()` explicitly force their own mode for their duration,
  not by review alone.
- **The `lstrip()` normalization bug, caught live** — an early draft of
  `_in_ci_scratch()` used `path.lstrip("./")` to strip a leading `"./"`.
  Running `python3 -c "print('../../etc/passwd'.lstrip('./'))"` directly
  showed this mangles `"../../etc/passwd"` into `"etc/passwd"`, silently
  destroying the `../` signal that would make a real scope-escape
  attempt visible — caught by actually running the exact line, not by
  reading it. Fixed in both `project/solution.py`/`starter.py` and
  mirrored in `exercises/solution.py`/`starter.py` to strip only a
  literal two-character `"./"` prefix, never a repeated character-class
  strip. A dedicated regression check
  (`in_scratch: a genuine path escape is NOT accidentally normalized
  into scope`) was added to the exercises' own 17-check test harness so
  this specific mistake is caught mechanically if reintroduced. Note
  that even with the buggy `lstrip()` version, `_safe_path()` (Chapter
  7's independent workspace-boundary check, still called after the
  scratch check in `write_file`) would have caught a real `../../etc/passwd`
  escape attempt regardless — this was a real bug in the CI-scratch
  layer specifically, not an exploitable gap in the full defense, but it
  was fixed rather than left resting on the second layer's coverage.
- **A real nested-git-repo hazard, caught and fixed before it could
  land** — the first draft of `_init_scratch_repo()` ran a real
  `git init` inside `project/workspace/`, this course's own persistent,
  git-tracked directory (the same one Chapter 11 uses for its
  `demo.txt` scaffold). Running it once revealed this would leave a
  real nested git repository inside this course repo's own working
  tree. Fixed by adding `_temp_git_workspace()`, a context manager that
  points the module-level `WORKSPACE` at a real `tempfile.mkdtemp()`
  directory (fully outside this repo) for the duration of any scenario
  that runs `git init`, and deletes it afterward via
  `shutil.rmtree(..., ignore_errors=True)` — confirmed by directly
  inspecting `project/workspace/` after a full run: it contains only
  `demo.txt` (from the interactive demo, matching Chapter 11's exact
  pattern), no `.git` directory, no leftover CI-mode scratch content.
- **`exercises/solution.py`** — run live, 17/17 checks pass, including
  the `lstrip()`-trap regression check described above.
- **`practice/solution.py`** — run live, prints all six scenarios and
  their answer keys cleanly, no errors, matching Chapters 10-11's
  "practice starter and solution are functionally identical, predict-
  then-run" pattern.
- **`starter.py` files (project and exercises)** — both run live,
  end-to-end, with all TODOs unimplemented: `exercises/starter.py`
  raises a clear `NotImplementedError` naming the exact missing
  function; `project/starter.py` runs to completion (exit code 0)
  because `TOOL_POLICY_CI = {}` (empty, per the TODO) makes
  `check_permission()`'s existing fail-closed default correctly refuse
  every CI-mode tool call — a real, live demonstration that Chapter 11's
  fail-closed design protects even an INCOMPLETE CI policy, not just a
  finished one. A follow-up bug this exposed (an unguarded
  `subprocess.run([...], check=True)` staging a nonexistent scratch
  directory, crashing the whole demo with an uncaught
  `CalledProcessError` once `write_file` was correctly refused) was
  caught by actually running `starter.py`, not by inspection, and fixed
  by changing those specific staging calls to `check=False` in both
  `starter.py` and `solution.py` so a partially-implemented (or, in
  `solution.py`'s case, fully correct) run never crashes the
  surrounding demo script.
- **The example CI workflow YAML** — validated with `python3 -c "import
  yaml; yaml.safe_load(open(...))"`, confirmed to parse as valid YAML
  with the expected top-level keys (`name`, `on` — which PyYAML parses
  as the boolean key `True` under YAML 1.1's `on`/`off` boolean
  coercion, a well-known, harmless GitHub Actions YAML quirk present in
  every real workflow file that uses a bare `on:` trigger key, not a
  bug in this file).
- **`bash scripts/local_check.sh < /dev/null`** — run from the repo root
  after all files were added; all 6 checks passed, including step 4,
  which ran `chapters/chapter-12-.../exercises/solution.py`,
  `chapters/chapter-12-.../practice/solution.py`, and
  `chapters/chapter-12-.../project/solution.py` for real, with no
  special-case marker-comment handling needed (none of these three
  trigger `local_check.sh`'s `sys.stdin` branch; `project/solution.py`'s
  `input()` calls happen only deep inside `confirm_with_human`, reached
  only via the interactive-mode demo's `write_file` call, and
  `local_check.sh` runs each solution.py with the shell's own inherited
  stdin, which — with `< /dev/null` on the outer invocation — hit
  `EOFError` immediately and denied cleanly, well under the 20-second
  timeout, exit code 0). `.github/workflows/ci.yml` and
  `scripts/local_check.sh` themselves were not modified, per the
  explicit constraint not to touch CI files.
- **Internal link check** — a Python link-scanner (checking every
  `href`/`src`/Markdown-link target across every `.html`/`.md` file in
  this chapter's directory) found 63 internal links, zero broken.
- **`python3 -m py_compile`** run on all 6 `.py` files in this chapter
  (`exercises/starter.py`, `exercises/solution.py`, `practice/starter.py`,
  `practice/solution.py`, `project/starter.py`, `project/solution.py`) —
  all compile cleanly.

## What was attempted but NOT observed live this session

**The full agent loop's live tool-calling round trip against Ollama**
(`run_agent()` actually calling `client.chat.completions.create(...)`
against a running Ollama server, in CI mode, and getting real tool
calls back) was **not observed live this session**, for the same two
reasons disclosed in every one of Chapters 7-11's own audits: (1) the
`openai` Python package is not installed in this sandbox
(`ModuleNotFoundError`), so `main()`'s live-agent branch hits the
`except ImportError` message and exits 0 before ever reaching Ollama at
all — confirmed directly, this is the actual code path taken, not an
assumption; (2) Ollama itself has hung on generation across every prior
build session's sandbox per PROJECT_STATE.md, and this chapter's own
subject (the CI policy layer) doesn't depend on it at all, consistent
with this task's framing and every prior Module 5 chapter's disclosure.
The CI-mode wall-clock budget's actual firing behavior (a real
`time.monotonic()` deadline interrupting a real multi-step
`run_agent()` loop mid-run) is therefore logically verified (the
comparison logic itself was read and reasoned through directly against
`MAX_STEPS_CI`/`CI_WALL_CLOCK_BUDGET_SECONDS`) but not observed firing
against a real, slow, live model loop this session — the same class of
gap Chapters 7-9's audits already carry forward, not a new one specific
to this chapter's CI-mode-only code.

`example-ci-workflow.yml` itself was validated for YAML syntax only —
it was never run against a real GitHub Actions runner (by explicit
design and instruction: it is illustrative content for the lesson, not
wired into this repo's own `.github/workflows/`, and must not be).

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook shows Chapter 11's exact `confirm_with_human` running unchanged in CI, printing a real denial, before introducing anything new — makes the "safe but useless" problem concrete immediately, then names the WRONG fix explicitly before building the RIGHT one. |
| Production depth | Pass | A fully worked, live-tested two-policy system with two independent code-level scope checks, a new least-privilege `run_tests` tool, a CI-specific step cap plus wall-clock budget, and a real (illustrative) GitHub Actions workflow showing both use cases wired end to end. |
| Real-time adoption usefulness | Pass | `TOOL_POLICY_CI`, the scratch-scope check, the protected-branch check, and the wall-clock budget are all real, tested code in `project/solution.py` — a reader can copy this pattern directly into their own CI setup, and `example-ci-workflow.yml` shows the exact wiring shape. |
| Architecture and diagrams | Pass | Code-window blocks for the fail-closed trace table, the PR review bot, the wrong fix, both policy dicts side by side, both scope checks, the workflow YAML excerpt, the step-cap/wall-clock code, and the "what's safe to land unreviewed" table. |
| Exercises | Pass | 6 tasks in `exercises/index.html`, 3 production-gear (tasks 4-6: designing a tier/scope for a genuinely new tool, tracing a real `ACAFE_CI_MODE=true` vs `"1"` string-comparison footgun, reviewing a PR that updates one policy dict but not the other). Tasks 1-3 map to 17 live-tested checks in `exercises/solution.py`. |
| Practice bank | Pass | 6 scenario cards in `practice/index.html` (meets the 6 minimum) plus a runnable, live-tested six-scenario script comparing the SAME tool call's outcome across both modes, including a scope-refused-despite-ALLOWED-tier case and a fail-closed-per-dict case. |
| Interview preparation | Pass | 8 questions in `interview-questions.html`, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves; exact plain-markdown mirror in `interview-questions.md`. |
| Project implementation | Pass | This is Module 5's second real lab per the curriculum map ("wire a minimal agent into a CI check") — a genuine, fully-implemented CI-specific policy extension of Chapter 11's agent, not a preview page. `starter.py` ships Chapter 11's agent plus a real `run_tests`/CI-scaffold with 4 connected TODOs; `solution.py` is the complete, live-tested reference in both modes; `example-ci-workflow.yml` is a real, validated, clearly-marked-illustrative GitHub Actions file. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section: problem (a correctly-reviewed CI policy silently going stale as the codebase/conventions around it change, not as a code bug), assumption, what actually distinguishes it, why it matters going forward, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 7-11's link order; uses the richer python-for-everyone-derived file pattern (README.md x3, `interview-questions.md`); lesson.html verified to include BOTH the interview-questions callout box and the footer's GitHub link span, the exact two items Chapter 11's first draft was missing per PROJECT_STATE.md's note. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty, chapter-badge); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text (confirmed via `local_check.sh`'s placeholder-text scan). All content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure only, not content), or any other TechNaom repo. Does not claim the Claude Agent SDK or any Anthropic-API-dependent design anywhere, consistent with this course's confirmed, non-negotiable policy. |

## Required Checks

- [x] Lesson starts with a problem, not jargon — shows Chapter 11's exact `confirm_with_human` denying every write-capable tool call in CI, before any new material, then names and rejects the wrong fix explicitly before building the right one.
- [x] Lesson includes core concepts (why CI is unattended by construction, not just "unlikely to have a human watching"), internal mechanics (the two-policy design, `active_policy()`, both scope checks, the wall-clock budget), a worked example (the resolved PR review bot and CI troubleshooting agent), a production scenario (the real, illustrative GitHub Actions workflow), trade-offs (why `edit_file`/`run_shell_command` get MORE restrictive in CI, not less, named explicitly as a "what is..." box), a security-adjacent honesty section (the wrong-fix strawman, shown and rejected, not just described), a review-discipline section tying back to Chapter 3, a thinking journal, and a summary/cheat-sheet.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (6 scenario cards, plus 6 tool-call scenarios in the runnable script — 12 total review items).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves — plus an exact `.md` mirror.
- [x] Project includes a meaningful implementation artifact, verified runnable and correct (the full CI-specific policy layer, both scope checks, the wall-clock budget, and the illustrative workflow YAML, all independently live-tested or YAML-validated, see disclosure above). This is Module 5's second real, graded lab per `docs/curriculum/CURRICULUM_MAP.md` ("wire a minimal agent into a CI check"), not a preview page. `project/solution.py` was verified to have no real side effects beyond a `tempfile.mkdtemp()` directory it creates and deletes itself, and does not call any GitHub API or touch this repo's real git history, per the explicit constraint.
- [x] Chapter includes diagrams/visual-text architecture aids (multiple code-window blocks across all five main sections).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project, plus the required files (README.md x3, `interview-questions.md`) present and internally linked correctly.
- [x] Content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure reference only), or any other TechNaom repo. Chapter 11 was read in full (lesson and every subpage) before writing, per the task's explicit instruction, and this chapter builds directly on its exact `TOOL_POLICY`/`check_permission`/`confirm_with_human`/`dispatch_tool_call`/`git_commit` code without re-deriving or duplicating it.
- [x] Every piece of runnable code in this chapter was executed directly this session — the full CI policy layer (all scenarios, both modes), both scope checks (including a caught-and-fixed `lstrip()` normalization bug and a caught-and-fixed nested-git-repo hazard), all 17 exercises checks, all 6 practice scenarios, and both `starter.py` files' fail-closed behavior with TODOs unimplemented. The one path not observed live (the full agent loop's live round trip against Ollama, in CI mode) is honestly disclosed above with the exact two reasons why, consistent with every prior Module 5 chapter's disclosure.
- [x] Does not claim the Claude Agent SDK or any Anthropic-API-dependent design anywhere in this chapter's content, per the explicit constraint.
- [x] `assets/chapters-data.js` updated: `chapter-12`'s entry now has `path: "chapters/chapter-12-putting-an-agent-in-ci/lesson.html"`. Module 5's `examPath` left `null` as instructed (the Module 5 exam is a separate follow-up task). Re-read the file first to confirm current state before editing; the diff adds only this one field.
- [x] Every internal link within this chapter's own pages verified programmatically (a Python link-scanner over every `.html`/`.md` file's `href`/`src`/Markdown-link targets in this chapter's directory). 63 real internal links checked, zero broken.
- [x] `bash scripts/local_check.sh < /dev/null` run from the repo root after adding all new files — all 6 checks passed, including the step that runs every `exercises/solution.py`, `project/solution.py`, and `practice/solution.py` file in the repo (this chapter's three all ran clean, none hung, none needed the `sys.stdin`/`LONG_RUNNING_SERVER`/`NEEDS_LIVE_SERVER` marker conventions). `.github/workflows/ci.yml` and `scripts/local_check.sh` themselves were not modified or touched by this session. The `< /dev/null` requirement (documented in PROJECT_STATE.md's local-testing gotcha) was followed throughout — every manual test run in this session, not just the final `local_check.sh` invocation, used closed stdin to match real CI behavior.
- [x] `python3 -m py_compile` run on all 6 `.py` files in this chapter (`exercises/starter.py`, `exercises/solution.py`, `practice/starter.py`, `practice/solution.py`, `project/starter.py`, `project/solution.py`) — all compile cleanly. All three `solution.py` files were additionally run to completion (in both interactive and CI mode, where applicable) with stdin closed, and their actual output inspected (see the live-tested disclosure above for specifics).

## Follow-Up Tasks

- Re-run `project/solution.py`'s (and `starter.py`'s, once a learner
  fills it in) full live agent-loop path against a real Ollama server,
  in CI mode, once the standing sandbox-wide generation hang (disclosed
  in Chapters 7-11's audits and reconfirmed here) is resolved, and once
  the `openai` package is installed in whatever environment does that
  re-check.
- `assessments/written-exams/module-5-exam.md` ("production-readiness
  checklist exam" per `docs/curriculum/CURRICULUM_MAP.md`) should be
  written now that both Chapter 11 and Chapter 12 are complete — this
  closes Module 5, matching the pattern used for Modules 1, 2, and 4's
  exams (written only after every chapter in the module was complete).
- Chapter 13 (the capstone, Module 6, Level 4 architecture challenge)
  is the final chapter of the whole course, per
  `docs/curriculum/CURRICULUM_MAP.md`. It should be able to draw on this
  chapter's exact two-policy design and the "what's safe to land
  unreviewed vs. what still needs review" framing as one concrete,
  already-built example of the kind of agentic-CI-workflow design
  question the capstone asks learners to work through themselves at
  architect level.
