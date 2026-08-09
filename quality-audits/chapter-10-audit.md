# Chapter Quality Audit: Detecting Hallucinated APIs and Logical Bugs

## Summary

- Chapter: 10 — Detecting Hallucinated APIs and Logical Bugs (Module 4, Advanced, **is the entire module**)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Live-tested-vs-logical-only disclosure

This chapter is conceptual/review-focused, like Chapters 1-6 — it does
not call a model, does not use the `openai` package, and does not need
Ollama. Every code example in the lesson, every exercise, every
practice snippet, and every planted flaw in the project's `flawed_pr/`
files uses **only Python's standard library** (`csv`, `statistics`,
`datetime`, `inspect`, `email.message`, `tempfile`, `os`, `sys`) —
`requests` appears only as literal example text inside a string in
`practice/starter.py`'s snippet list, never actually imported or
executed by the script itself (confirmed by grep and by the script
actually running clean, see below).

Every single planted bug's actual runtime behavior — not just its
described behavior — was independently executed this session against
a real Python interpreter before being written into the lesson,
exercises, practice bank, project, or exam answer key:

- The hook's `pandas.DataFrame.sort_values(..., ignore_na=True)` claim
  — pandas turned out to be genuinely installed in this sandbox
  (`pip show pandas` reports version 3.0.5), so this was independently
  executed live rather than stated from memory: `inspect.signature(pd.DataFrame.sort_values)`
  confirms `na_position` is real and `ignore_na` is not, and calling
  `df.sort_values(by="signup_date", ascending=False, na_position="last", ignore_na=True)`
  against a real `DataFrame` raises exactly
  `TypeError: DataFrame.sort_values() got an unexpected keyword
  argument 'ignore_na'. Did you mean 'ignore_index'?` — the lesson's
  hook was updated to quote this exact, real error message (including
  pandas's own "did you mean" suggestion) rather than an invented
  approximation. `Series.mean(skipna=True)`'s real signature was
  likewise confirmed via `inspect.signature(pd.Series.mean)`. Every
  *other* code claim in this chapter (all `project/flawed_pr/` files,
  all exercises, all practice snippets, the exam's Part C diff) uses
  only the standard library and was directly executed as well.
- `project/flawed_pr/export_csv.py`'s `DictWriter.write_all()` —
  actually called against a real temp file; confirmed
  `AttributeError: 'DictWriter' object has no attribute 'write_all'`.
- `project/flawed_pr/notify.py`'s `EmailMessage.set_content(...).add_attachment(...)`
  chaining — actually called; confirmed
  `AttributeError: 'NoneType' object has no attribute 'add_attachment'`.
- `project/flawed_pr/aggregate.py`'s `statistics.average(...)` — actually
  called; confirmed `AttributeError: module 'statistics' has no
  attribute 'average'`.
- `project/flawed_pr/aggregate.py`'s `filter_week` boundary bug —
  actually traced with 10 real `date` objects (Aug 1-10, 2026);
  confirmed it returns 8 records (days 3-10) and includes `as_of`
  (day 10) itself, contradicting its own docstring's "7 days, not
  including as_of" promise.
- `project/flawed_pr/notify.py`'s `headers={}` mutable-default leak —
  actually demonstrated with two sequential calls to a working
  (chaining-fixed) copy of `build_message`, confirming both calls
  receive the identical `dict` object (`id(h1) == id(h2)` is `True`)
  and that the second call's message inherits the first call's
  `X-Report-Built-By` header before its own loop even runs.
- `exercises/solution.py`'s three functions
  (`method_actually_exists`/`safe_call`/`has_mutable_default`) — run
  live, 12/12 checks pass.
- `practice/starter.py`'s six snippets — run live, all six print their
  code and answer key correctly with no errors.
- `project/solution.py`'s full review harness — run live against the
  real `flawed_pr/` files, correctly reports all 3 crashing flaws, the
  boundary-trace mismatch, and the mutable-default risk, with 0 false
  positives on the deliberately-fine `round()` line.
- The Module 4 exam's Part C code-review snippet
  (`dedupe_by_email`) — independently executed this session, twice:
  once confirming `dict.values(exclude_none=True)` raises
  `TypeError: dict.values() takes no keyword arguments` (exact message
  captured and corrected into the answer key after the first draft
  used an invented, slightly wrong message text), and once confirming
  the `KeyError` on `last_updated` fires only when a record with a
  missing/duplicate-triggering key is compared against another record
  (not on a single record with no duplicate, due to Python's `or`
  short-circuit evaluation) — this nuance is reflected accurately in
  the exam's own C2 discussion.

No live model, no `openai` package, no MCP, no Ollama dependency
anywhere in this chapter — matching the curriculum map's expectation
that Module 4, like Modules 1 and 2, is conceptual and does not need
live-model access.

## What was NOT independently re-verified live this session

Nothing. Every technical claim made anywhere in this chapter — the
lesson's hook and every code-window example, all three exercise
functions, all six practice snippets, all `project/flawed_pr/` files,
the review harness, and the Module 4 exam's Part C diff — was executed
directly against a real, installed interpreter this session, including
the one example (pandas's `sort_values()`/`ignore_na` claim) that
initially looked like it would need to be stated from documented
knowledge rather than live-tested; pandas turned out to already be
installed in this sandbox, so it was verified live instead and the
lesson's hook was updated to quote the exact real error message pandas
produces (including its own "Did you mean 'ignore_index'?"
suggestion) rather than an approximation. Note that pandas is still
not, and is not planned to become, an actual dependency of this
course's own runnable code (exercises/practice/project) — it appears
only in the lesson's illustrative hook text, which happened to be
independently checkable in this particular sandbox.

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook opens with a single diff containing one real and one hallucinated pandas argument side by side, making the chapter's central claim (plausibility is not evidence) concrete before any explanation. |
| Production depth | Pass | Three fully worked, live-tested hallucination categories (wrong name, wrong argument, wrong return-type/chaining assumption) and four logical-bug categories (off-by-one, inverted boolean, mutable default, operator precedence), each with a real, runnable, independently-executed example. |
| Real-time adoption usefulness | Pass | Every mechanical check taught (`hasattr()`/`dir()`, actually running the exact call, tracing a boundary case) is built into real, runnable code in exercises and the project, not just described in prose. |
| Architecture and diagrams | Pass | Code-window blocks for the hook's diff, the chaining hallucination, the introspection check, and all four logical-bug categories, each isolated and explained. |
| Exercises | Pass | 6 tasks in `exercises/index.html`, 3 production-gear (tasks 4-6: checking a real claim you're unsure about, tracing a slicing boundary by hand, reviewing a pandas diff for a hallucinated argument). Tasks 1-3 map to three live-tested functions (12/12 checks passing). |
| Practice bank | Pass | 6 scenario cards in `practice/index.html` (meets the 6 minimum) plus a runnable, live-tested six-snippet find-the-flaw script covering every category the lesson names, including a distinct hallucinated-argument, two hallucinated-method-name variants, an inverted condition, an off-by-one slice, and an operator-precedence trap. |
| Interview preparation | Pass | 8 questions in `interview-questions.html`, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves; exact plain-markdown mirror in `interview-questions.md`. |
| Project implementation | Pass | This is Module 4's real lab per the curriculum map — a genuine, multi-file (3-file), deliberately-flawed AI-generated PR (`project/flawed_pr/`) with 5 real planted flaws (3 hallucinated APIs, 2 logical bugs) plus 1 deliberately-fine line to test over-flagging, all independently verified live this session, plus a runnable 4-TODO review harness (`starter.py`/`solution.py`) and a full, file-by-file `review_answer_key.md`. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section: problem (trusting a diff because it looks confident and the named test passed), assumption, what actually distinguishes a validated diff, why it matters for the project below, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 7-9's link order; uses the richer python-for-everyone-derived file pattern (README.md x3, `interview-questions.md`). No `ai-paired.html` — this chapter's central "produce something, then critique it" arc is already the project's entire structure (a flawed PR to review), so a separate AI-paired page would be redundant with the chapter's own core exercise, matching Chapter 9's precedent for omitting it when the chapter's own content already delivers that arc. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty, chapter-badge); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text (confirmed via `local_check.sh`'s placeholder-text scan). All content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure only, not content), or any other TechNaom repo. |

## Required Checks

- [x] Lesson starts with a problem, not jargon — opens with a single diff containing a real and a hallucinated pandas argument side by side.
- [x] Lesson includes core concepts (what a hallucinated API is, mechanically, tied to Chapter 4's prediction mechanism), internal mechanics (three clustering situations, each with its own worked example), a worked example (the introspection/run/comment checks), a production scenario (the untested-branch nuance, tied directly into the project's own narrative), trade-offs (why logical bugs are harder to catch than hallucinations, explicitly), a security-adjacent honesty note (mutable-default state leaks are a real production risk, not just a style nit), an honest common-mistake/failure section (all four logical-bug categories with real, run code), a thinking journal, and a summary/cheat-sheet.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (6 scenario cards, plus 6 snippets in the runnable script — 12 total review items).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves — plus an exact `.md` mirror.
- [x] Project includes a meaningful implementation artifact, verified runnable and correct (the entire 3-file flawed PR and the 4-TODO review harness both independently live-tested, see disclosure above). This is Module 4's real, graded lab per `docs/curriculum/CURRICULUM_MAP.md` ("a deliberately-flawed AI-generated PR to review and fix"), not a preview page.
- [x] Chapter includes diagrams/visual-text architecture aids (multiple code-window blocks across the hook and both major sections).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project, plus the required files (README.md x3, `interview-questions.md`) present and internally linked correctly.
- [x] Content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure reference only), or any other TechNaom repo. Chapters 3 and 5 were read in full before writing, per the task's explicit instruction, and this chapter's checklist references (Chapter 3's questions 1 and 5, Chapter 5's going-off-the-rails mechanism) build on them directly without re-deriving or duplicating their content.
- [x] Every piece of runnable code in this chapter (lesson claims about stdlib and pandas behavior, all exercises, all practice snippets, the entire project including the flawed PR and the review harness, and the exam's Part C code) was executed directly against a real Python interpreter this session — including the hook's pandas example, since pandas was found to already be installed in this sandbox.
- [x] `assets/chapters-data.js` updated: Module 4's `examPath` set to `"assessments/written-exams/module-4-exam.md"`, `chapter-10`'s entry now has `path: "chapters/chapter-10-detecting-hallucinated-apis-and-logical-bugs/lesson.html"`. Re-read first to confirm current state before editing; `git diff` confirms only these two fields changed, nothing else in the file touched.
- [x] Every internal link within this chapter's own pages, plus the Module 4 exam file, verified programmatically (a Python link-scanner over every `.html`/`.md` file's `href`/`src`/Markdown-link targets). 71 internal links checked, zero broken.
- [x] `bash scripts/local_check.sh` run from the repo root after adding all new files — all 6 checks passed, including the step that runs every `exercises/solution.py`, `project/solution.py`, and `practice/solution.py` file in the repo (this chapter's three all ran clean). `.github/workflows/ci.yml` and `scripts/local_check.sh` themselves were not modified, read, or touched by this session, per the explicit instruction that a separate parallel session owns extending them.
- [x] `python3 -m py_compile` run on all 9 `.py` files in this chapter (`exercises/starter.py`, `exercises/solution.py`, `practice/starter.py`, `practice/solution.py`, `project/starter.py`, `project/solution.py`, `project/flawed_pr/aggregate.py`, `project/flawed_pr/export_csv.py`, `project/flawed_pr/notify.py`) — all compile cleanly. All were additionally run to completion and their actual output inspected (see the live-tested disclosure above for the specific results of each).

## Follow-Up Tasks

- None outstanding from this chapter's own build — every technical
  claim in it was independently executed live this session (see
  disclosure above).
- Module 4 is now the second module (after Module 3) with a fully
  built chapter and exam in the same session. Module 5 (Chapters
  11-12: security/sandboxing, CI integration) is the recommended next
  module per `PROJECT_STATE.md`'s existing "Next task after that"
  note — those chapters will need a live Ollama connection again
  (unlike Modules 1, 2, and 4), so the standing sandbox-wide Ollama
  generation hang (disclosed in Chapters 7-9's own audits) should be
  re-checked at the start of that work, not assumed resolved.
- `scripts/local_check.sh`/`ci.yml`'s extension to run
  `practice/solution.py` files (flagged as outstanding in Chapters
  7-9's audits) appears to already be present in the current
  `scripts/local_check.sh` (its step 4 glob already includes
  `chapters/*/practice/solution.py`) — this session did not modify
  that file per the explicit instruction not to touch it, and did not
  investigate further whether the parallel session mentioned in this
  chapter's task briefing has completed that work or whether it
  predates this session entirely; worth confirming with whoever owns
  that task.
