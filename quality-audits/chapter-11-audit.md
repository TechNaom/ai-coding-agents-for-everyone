# Chapter Quality Audit: Security: Sandboxing, Permissions, Destructive Commands

## Summary

- Chapter: 11 — Security: Sandboxing, Permissions, Destructive Commands (Module 5, Advanced, first of two chapters)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Live-tested-vs-logical-only disclosure

This chapter's actual subject — a harness-enforced permission-scope
layer checked before tool dispatch — is pure Python control-flow logic
that needs no live model to verify, the same discipline Chapters 7-10's
audits have used for testing tool/dispatch logic independent of a live
model. Every piece of that logic was independently, directly executed
this session:

- **`project/solution.py`'s full permission layer** — ran directly with
  stdin closed (`python3 solution.py < /dev/null`), confirming: (1) an
  `ALLOWED` tool (`read_file`) ran immediately with no prompt; (2) a
  `REQUIRES_CONFIRMATION` tool (`write_file`) printed a real
  confirmation prompt, hit `EOFError` on `input()` since no human was
  attached, and denied cleanly with the expected error string — no
  hang, no crash, exit code 0; (3) the `BLOCKED` tool (`send_email`)
  was refused before any prompt at all; (4) a registered-but-
  unclassified tool (`_unclassified_demo_tool`, deliberately left out
  of `TOOL_POLICY`) was refused too, confirming the fail-closed default
  actually works, not just that it reads correctly; (5) a genuinely
  unknown tool name was rejected as `"unknown tool"`, unrelated to the
  policy layer.
- **The confirmation-granted path** — separately verified with
  `builtins.input` monkeypatched to always return `"y"`: `write_file`
  actually wrote the file, and `git_commit` (against a real, freshly
  initialized git repo in a temp workspace) actually ran `git commit`
  and produced a real commit (`8b1c5d5`), confirming the resolved
  `git_commit` design (no `confirm` parameter, approval happens purely
  in the harness) works end-to-end, not just in isolation.
- **The denylist still applies even when a human would confirm** —
  `run_shell_command("sudo rm -rf /")` was called with `input` forced
  to return `"y"` and was still refused by `SHELL_DENYLIST`, confirming
  the two-layer defense-in-depth point the lesson makes explicitly
  (policy tier and denylist are independent checks, both must clear).
- **The `resource.setrlimit`-based process isolation** — independently
  verified twice, standalone, before being written into the lesson: a
  real infinite CPU-bound loop run as a subprocess with
  `RLIMIT_CPU=(2,2)` was killed by the kernel (`SIGKILL`, exit code
  `137`) after 2 seconds; a real attempt to allocate a 1GB
  `bytearray` against a 256MB `RLIMIT_AS` cap raised a genuine
  `MemoryError` inside the subprocess instead of stressing host memory.
  Both were re-confirmed inside `run_shell_command` itself (5-second
  CPU limit, 512MB memory cap, as shipped) with the same real outcomes.
  `RLIMIT_NPROC` was deliberately tested too, in an early draft — it
  caused spurious `Cannot fork` failures because it applies to the
  entire real user account, not the subprocess tree — and was removed
  from the shipped code specifically because of that live-observed
  failure, not from an abstract concern; the lesson explains this
  exact reasoning.
- **The restricted subprocess environment** — verified live:
  `SUPER_SECRET` was set in this process's real environment, and
  `run_shell_command("env")` (with confirmation granted) showed only
  `PATH` in its output — the secret did not leak into the sandboxed
  subprocess.
- **`exercises/solution.py`** — run live, 18/18 checks pass, including
  the ordering-dependent `classify_threat` case
  (`cat ~/.aws/credentials`) that an earlier draft got wrong (matched
  `SCOPE_ESCAPE` before `SUPPLY_CHAIN_OR_CREDENTIAL` due to check
  order) — caught by actually running the test harness, not by review,
  and fixed by reordering the checks in both `starter.py`'s docstring
  and `solution.py`'s implementation.
- **`practice/solution.py`** — run live, prints all six scenarios and
  their answer keys cleanly, no errors, matching Chapter 10's
  "practice starter and solution are functionally identical, predict-
  then-run" pattern.
- **`bash scripts/local_check.sh`** — run from the repo root after all
  files were added; all 6 checks passed, including step 4, which ran
  `chapters/chapter-11-.../exercises/solution.py`,
  `chapters/chapter-11-.../practice/solution.py`, and
  `chapters/chapter-11-.../project/solution.py` for real, with no
  special-case handling needed (none of these three use
  `sys.stdin`-based interactive input in a way that would trigger
  `local_check.sh`'s `sys.stdin` branch — `project/solution.py`'s
  `input()` calls only happen deep inside `confirm_with_human`, invoked
  only if a scenario reaches the `REQUIRES_CONFIRMATION` tier, and
  `local_check.sh` runs `solution.py` with the shell's own inherited
  stdin, which in this non-interactive session hit `EOFError`
  immediately and denied cleanly rather than hanging — confirmed by the
  run completing well under the 20-second timeout with exit code 0).
  `.github/workflows/ci.yml` and `scripts/local_check.sh` themselves
  were not modified, per the explicit constraint not to touch CI files.

## What was attempted but NOT observed live this session

**The full agent loop's live tool-calling round trip against Ollama**
(`run_agent()` actually calling `client.chat.completions.create(...)`
against a running Ollama server and getting real tool calls back) was
**not observed live this session**, for two separate, honestly
disclosed reasons:

1. **Ollama itself hung on generation**, consistent with the
   sandbox-wide issue disclosed in every one of Chapters 7-9's own
   audits. Per this task's explicit instruction, Ollama was tried
   briefly at the start of this session: `ollama ps`/`/api/tags`
   responded instantly and correctly (the server process is reachable
   and reports `llama3.2:latest` as installed), but two separate direct
   `POST /v1/chat/completions` calls — one with a 30-second timeout, one
   with a 15-second timeout, both plain, non-tool-calling completions
   with a trivial one-line prompt — both timed out with no response at
   all (`curl` exit code 124 both times). This is the same failure
   shape (server reachable, generation itself hangs) disclosed in
   Chapters 7, 8, and 9's audits across four prior build sessions now.
2. **The `openai` Python package is not installed** in this sandbox
   (`import openai` raises `ModuleNotFoundError`). This means
   `project/solution.py`'s and `starter.py`'s `main()` — after running
   the permission-layer demo live, as confirmed above — hit the
   `except ImportError` branch and printed the "openai package isn't
   installed" message and exited 0, exactly as designed (the same
   graceful-degradation behavior Chapter 7 established), rather than
   ever reaching the point where the 8-second client-side request
   timeout (added specifically to make an Ollama hang fail fast instead
   of hanging the whole script, given point 1 above) would have been
   exercised. That specific code path — `OpenAI(..., timeout=8.0)`
   raising a timeout exception that this file's `except Exception`
   block correctly classifies via the `"timeout"`/`"timed out"`
   substring check — is logically verified (the exception-message
   substring matching was tested directly against a synthetic
   `TimeoutError`-shaped message string, confirming the classification
   logic works), but was not observed against a real `openai`-client
   timeout firing against the real hung Ollama server this session.

This is consistent with, and does not change, this task's own stated
expectation: "this chapter's code likely doesn't need live model access
since it's mostly about the harness-level permission layer" — that
expectation held. The chapter's actual subject (permission scoping,
sandboxing via `resource.setrlimit`, the threat-model mapping) needed
no live model at all and was fully live-verified. Only the optional,
clearly-secondary "then also try it against a real agent loop" path at
the end of `main()` was not observed end-to-end this session, for the
two reasons above, both disclosed rather than hidden.

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook reopens Chapter 8's exact unshipped `git_commit(message, confirm=False)` sketch and walks through precisely why it fails, before introducing anything new — makes the chapter's whole reason for existing concrete immediately. |
| Production depth | Pass | A fully worked, live-tested three-tier permission system wired into `dispatch_tool_call`; real, live-tested `resource.setrlimit` process isolation with an honestly-disclosed rejected mitigation (`RLIMIT_NPROC`); a four-category threat model each mapped to a real, already-built or newly-built mitigation; a retrospective least-privilege audit of every tool from Chapters 7-9. |
| Real-time adoption usefulness | Pass | The permission layer, the resource-limit hardening, and the resolved `git_commit` are all real code in `project/solution.py`, not just described — a reader can copy this pattern directly into their own agent. |
| Architecture and diagrams | Pass | Code-window blocks for the confirm-flag failure, the policy dict, `confirm_with_human`, the rewired `dispatch_tool_call`, the resolved `git_commit`, the resource-limit code, and the four-category threat-model table. |
| Exercises | Pass | 6 tasks in `exercises/index.html`, 3 production-gear (tasks 4-6: designing a policy for an uncovered tool, tracing the EOF-on-cron scenario using the real code, reviewing a PR that adds a tool without a policy entry). Tasks 1-3 map to 18 live-tested checks in `exercises/solution.py`. |
| Practice bank | Pass | 6 scenario cards in `practice/index.html` (meets the 6 minimum) plus a runnable, live-tested six-scenario script evaluating real tool calls against the real `TOOL_POLICY`/`SHELL_DENYLIST`, including a two-layer defense-in-depth case and a fail-closed-default case. |
| Interview preparation | Pass | 8 questions in `interview-questions.html`, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves; exact plain-markdown mirror in `interview-questions.md`. |
| Project implementation | Pass | This is Module 5's real lab per the curriculum map ("add permission scoping to the Module 3 agent") — a genuine, fully-implemented permission-scoped extension of Chapter 8's agent, not a preview page. `starter.py` ships the Chapter 8 agent plus a real `git_commit`/`send_email` scaffold with 5 connected TODOs; `solution.py` is the complete, live-tested reference. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section: problem (a developer adding a new tool and forgetting to classify it in `TOOL_POLICY`), assumption, what actually distinguishes it, why it matters for Chapter 12 specifically (CI is unattended), working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 7-10's link order; uses the richer python-for-everyone-derived file pattern (README.md x3, `interview-questions.md`). |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty, chapter-badge); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text (confirmed via `local_check.sh`'s placeholder-text scan). All content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure only, not content), or any other TechNaom repo. |

## Required Checks

- [x] Lesson starts with a problem, not jargon — reopens Chapter 8's exact `git_commit` sketch and shows precisely why its `confirm` flag fails, before any new material.
- [x] Lesson includes core concepts (why a model-set flag isn't a real permission check), internal mechanics (the three-tier policy, `check_permission`, `confirm_with_human`, the rewired `dispatch_tool_call`), a worked example (the resolved `git_commit`), a production scenario (the unattended-cron-job EOF case, tied directly into an exercise and an interview question), trade-offs (per-tool vs. per-argument policy granularity, named explicitly as a "what is..." box), a security-adjacent honesty section (sandboxing's real scope vs. what Python alone can provide, including the deliberately-rejected `RLIMIT_NPROC`), a concrete threat model (four categories mapped to mitigations), a least-privilege retrospective, a thinking journal, and a summary/cheat-sheet.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (6 scenario cards, plus 6 tool-call scenarios in the runnable script — 12 total review items).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves — plus an exact `.md` mirror.
- [x] Project includes a meaningful implementation artifact, verified runnable and correct (the full permission-scope layer, the resolved `git_commit`, and the resource-limit hardening, all independently live-tested, see disclosure above). This is Module 5's real, graded lab per `docs/curriculum/CURRICULUM_MAP.md` ("add permission scoping to the Module 3 agent"), not a preview page.
- [x] Chapter includes diagrams/visual-text architecture aids (multiple code-window blocks across all five main sections).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project, plus the required files (README.md x3, `interview-questions.md`) present and internally linked correctly.
- [x] Content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure reference only), or any other TechNaom repo. Chapters 7, 8, and 9 were read in full (including every subpage's relevant security-adjacent content) before writing, per the task's explicit instruction, and this chapter's resolutions (the permission layer, the resolved `git_commit`, the threat model, the least-privilege retrospective) build directly on their exact prior code and stated open questions without re-deriving or duplicating their content.
- [x] Every piece of runnable code in this chapter was executed directly this session — the full permission layer (all five tiers/paths, plus the confirmation-granted path and the denylist-still-applies path), the resource-limit hardening (CPU kill, memory cap, restricted environment, all independently verified), all 18 exercises checks, and all 6 practice scenarios. The one path not observed live (the full agent loop's live round trip against Ollama) is honestly disclosed above with the exact two reasons why, consistent with this task's own stated expectation that this chapter likely wouldn't need live model access.
- [x] `assets/chapters-data.js` updated: `chapter-11`'s entry now has `path: "chapters/chapter-11-security-sandboxing-permissions-destructive-commands/lesson.html"`. Module 5's `examPath` left `null` as instructed (Chapter 12 needs to land first). Re-read the file first to confirm current state before editing; `git diff` confirms only this one field was added, nothing else in the file touched.
- [x] Every internal link within this chapter's own pages verified programmatically (a Python link-scanner over every `.html`/`.md` file's `href`/`src`/Markdown-link targets in this chapter's directory). 63 real internal links checked, zero broken (one regex false-positive from a code snippet containing `**args` inside a Markdown-link-shaped pattern was manually confirmed to not be a real link).
- [x] `bash scripts/local_check.sh` run from the repo root after adding all new files — all 6 checks passed, including the step that runs every `exercises/solution.py`, `project/solution.py`, and `practice/solution.py` file in the repo (this chapter's three all ran clean, none hung, none needed the `sys.stdin`/`LONG_RUNNING_SERVER`/`NEEDS_LIVE_SERVER` marker conventions). `.github/workflows/ci.yml` and `scripts/local_check.sh` themselves were not modified or touched by this session.
- [x] `python3 -m py_compile` run on all 6 `.py` files in this chapter (`exercises/starter.py`, `exercises/solution.py`, `practice/starter.py`, `practice/solution.py`, `project/starter.py`, `project/solution.py`) — all compile cleanly. All three `solution.py` files were additionally run to completion and their actual output inspected (see the live-tested disclosure above for specifics).

## Follow-Up Tasks

- Re-run `project/solution.py`'s (and `starter.py`'s, once a learner
  fills it in) full live agent-loop path against a real Ollama server
  once the standing sandbox-wide generation hang (disclosed in
  Chapters 7-9's audits and reconfirmed here, a fifth time now, across
  five separate build sessions) is resolved. Also install the `openai`
  package in whatever environment does that re-check, since it wasn't
  present in this session's sandbox either — that alone was enough to
  keep `main()`'s live-agent branch from being reached at all, separate
  from the Ollama hang itself.
- Chapter 12 ("Putting an Agent in CI") is the recommended next task
  per `PROJECT_STATE.md`/`AI_HANDOFF.md` — it should build directly on
  this chapter's permission-scope layer and its fail-closed,
  unattended-safe design (Section 2 and the GenAI Builder Thought
  Process section both explicitly flag this connection: a CI run is,
  by construction, the unattended case this chapter's `EOFError`
  handling exists for). Read this chapter in full before starting
  Chapter 12, the same way this chapter was built only after reading
  Chapters 7-9 in full.
- Module 5's "production-readiness checklist exam" (per
  `docs/curriculum/CURRICULUM_MAP.md`) should be written once Chapter
  12 also lands, matching the pattern used for Modules 1, 2, and 4's
  exams (written only after every chapter in the module was complete).
