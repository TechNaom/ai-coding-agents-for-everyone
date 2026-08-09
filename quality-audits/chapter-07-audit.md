# Chapter Quality Audit: Build: A Minimal Coding Agent

## Summary

- Chapter: 7 — Build: A Minimal Coding Agent (Module 3, Intermediate, **reference chapter**)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## What was actually verified against a live Ollama server (this build session)

The task briefing stated the orchestrating session had already confirmed
the base `openai`-client-against-Ollama pattern (installed `openai`
2.53.0, `llama3.2` pulled, server at `localhost:11434`) and that this
build session likely would **not** have live Ollama access. That
assumption turned out to be wrong for part of this session: a real
Ollama server with `llama3.2:latest` pulled (confirmed via
`curl http://localhost:11434/api/tags`) was reachable early in this
session, and the following was genuinely executed, live, not from
memory or copied from the briefing:

- Installed `openai` 2.53.0 in a fresh venv (matching the orchestrating
  session's confirmed version) and ran the exact confirmed
  weather/tool-call pattern from the task briefing end to end — got a
  real `tool_calls` response, parsed real JSON arguments, sent a real
  `role: "tool"` result back, and got a real final natural-language
  answer with `tool_calls: None`. This matches the briefing's confirmed
  shape exactly.
- Wrote and ran, live, a complete standalone three-tool agent
  (`read_file`, `write_file`, `run_shell_command`) with the same
  system-prompt/loop/dispatch shape now in `lesson.html` and
  `project/starter.py`. Two genuine runs are quoted verbatim in
  `lesson.html`'s hook and "Watching It Actually Run" sections:
  - Task "write hello.txt then read it back" produced two real tool
    calls (`write_file` then `read_file`) and a clean stop with an
    accurate summary.
  - Task "run ls and tell me what files are there" produced a real
    `run_shell_command("ls")` call, a real subprocess result, and a
    clean stop.
  Both runs' printed output was copied into the lesson verbatim, not
  paraphrased or invented.
- Partway through this session, the local Ollama server stopped
  responding to generation requests (`/api/tags` kept responding, but
  `/api/generate` and `chat.completions.create` calls hung indefinitely
  — confirmed via direct `curl` timeouts and `ollama ps` showing no
  loaded model process). This appears to be a transient sandbox/resource
  issue, not a bug in this chapter's code. As a direct consequence:
  **`project/starter.py` and `project/solution.py` were NOT independently
  re-executed live against a real model in this session** — two attempts
  (one foregrounded, one backgrounded) both hung and were killed rather
  than completing. They are logically sound and use the identical,
  already-live-verified client construction, tool schema shape, and
  dispatch pattern as the standalone script that *did* run live earlier
  in the same session (same `_safe_path`, same three tools, same
  `dispatch_tool_call` structure, same loop shape) — but that specific
  file was not itself observed producing a live transcript. This is
  flagged explicitly rather than glossed over, per the task's explicit
  honesty requirement.
- The reliability caveat in `lesson.html` (Section 6) reports the
  briefing's stated finding (a small local model occasionally producing
  an incomplete/wrong tool-call arguments object) as **the orchestrating
  session's finding**, not independently reproduced by this session — no
  malformed-arguments case was actually observed in this session's own
  live runs (all live tool calls this session made were well-formed).
  The defensive code (`dispatch_tool_call`'s `json.JSONDecodeError`/
  `KeyError` handling) is real and tested (see below), just not tested
  against a live reproduction of that specific failure mode.

## What was tested without live model access (mocked/stubbed, per the task's explicit fallback instruction)

- `exercises/starter.py` / `solution.py` — `dispatch_tool_call` and
  `run_loop_stub` fully implemented and tested against 8 hardcoded
  scenarios (well-formed calls, missing required argument, malformed
  JSON, unknown tool, clean stop, step cap, step cap with excess
  scripted turns). `python3 solution.py` prints `8/8 checks passed.`
  and exits 0; `starter.py` correctly raises `NotImplementedError` until
  filled in (verified both ways).
- `practice/starter.py` / `solution.py` — a scripted four-scenario
  runner (clean stop, step cap, boundary stop, failure stop) with no
  network dependency. Run live; all four scenarios produced the
  predicted stop condition (`clean_stop`, `step_cap`, `boundary_stop`,
  `failure_stop` respectively).
- `project/starter.py` / `solution.py` graceful-degradation path — run
  live under plain `python3` (no `openai` installed in that
  interpreter): both print `The openai package isn't installed. Run:
  pip install openai` and exit 0, confirming the CI-safety behavior
  CONTRIBUTING.md requires works correctly even though the live-model
  path itself wasn't re-observed this session (see above).
- All six `.py` files in this chapter compile cleanly under
  `python3 -m py_compile`.

## Hosted-provider docs checked (2026-08-09, this session)

- **Anthropic**: fetched `https://platform.claude.com/docs/en/api/openai-sdk`
  directly. Confirmed current shape: `base_url="https://api.anthropic.com/v1/"`,
  a real Claude API key as `api_key`, `tools`/`tool_calls` fully
  supported through the compatibility layer, system/developer messages
  hoisted into a single leading system message. Confirmed the docs
  explicitly describe this layer as intended for **testing/evaluation,
  not a recommended production path** — stated as such in the lesson.
  Model name used in the lesson's diff (`claude-sonnet-4-6`) is taken
  directly from Anthropic's own current docs example, not invented.
  Pricing cited (~$3/$15 per million input/output tokens) from a web
  search of current 2026 Anthropic API pricing sources, flagged in the
  lesson as "check current pricing," not asserted as permanently fixed.
- **Google Gemini**: fetched `https://ai.google.dev/gemini-api/docs/openai`
  directly. Confirmed current shape: `base_url="https://generativelanguage.googleapis.com/v1beta/openai/"`,
  a Gemini API key as `api_key`, function/tool calling documented as
  fully supported via the standard OpenAI tool schema. Model name used
  (`gemini-3.1-flash-lite`) and pricing (~$0.25/$1.50 per million
  input/output tokens) came from web search of current 2026 Gemini
  pricing sources, flagged the same way.
- **OpenAI**: no compatibility-layer verification needed since the
  `openai` client's default `base_url` already targets OpenAI's own API
  — verified via web search that `gpt-4o-mini` remains a current,
  low-cost model (~$0.15/$0.60 per million input/output tokens as of
  this writing).
- All three swap code blocks in `lesson.html`'s "Using a Hosted API
  Instead" section were written directly from the fetched docs above,
  not from memory or the March-2026 snapshot referenced in
  PROJECT_STATE.md — the task's explicit instruction to re-verify rather
  than assume was followed.

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook opens with a genuine, unedited live transcript (two real tool calls, a clean stop) rather than an invented example, immediately proving the chapter's promise that this is real, runnable code. |
| Production depth | Pass | Full agent built section by section (setup/hardware, tool schemas + real functions + `_safe_path` boundary, the loop mapped explicitly onto Chapter 4's plan/act/observe/repeat vocabulary, a dedicated reliability-caveat section, a fully-verified three-provider hosted-swap section). |
| Real-time adoption usefulness | Pass | Every code block is copy-pasteable and matches the actual files in `project/starter.py`; hardware requirement (~2GB disk, ~4GB RAM) stated explicitly per the task's replacement for the old dollar-cost disclosure. |
| Architecture and diagrams | Pass | Code-window blocks for tool schemas, tool functions, the full loop, isolated dispatch snippets, two real run transcripts, and three hosted-provider diffs — text/code architecture aids throughout, matching this chapter's code-heavy nature. |
| Exercises | Pass | 6 tasks in `exercises/index.html`, 3 explicitly production-gear (tasks 4-6: extending the dispatch table without touching core logic, constructing an exact step-cap boundary case, and a Chapter-3-style review of a hypothetical safety gap). Tasks 1-2 map directly to real, runnable TODOs in `starter.py`/`solution.py`, live-tested (8/8 passing). |
| Practice bank | Pass | 6 scenario-cards in `practice/index.html` plus a runnable, live-tested four-scenario stop-condition script (`starter.py`/`solution.py`) covering clean/hard/boundary/failure stops with a predict-then-run structure and an answer key. |
| Interview preparation | Pass | 8 questions in `interview-questions.html`, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves; exact plain-markdown mirror in `interview-questions.md` per the required file structure. |
| Project implementation | Pass (with the live-execution caveat above) | `project/starter.py` is the complete, real reference agent (matches lesson code); `project/solution.py` adds a `list_files` tool with three deliberate, realistic flaws (boundary escape, ambiguous tool description, inconsistent error handling) used as the critique artifact in `ai-paired.html`. `project/index.html` is a short L2-preview page (L2 doesn't ship until after Chapter 8, per CURRICULUM_MAP.md), matching the brevity of Chapters 1/2's L1-preview pages. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section in `lesson.html`: problem (assuming the loop needs a framework), assumption, what actually distinguishes it (the loop is ~30 lines; real effort is in the tool layer and defensive handling), why it matters before Chapter 8, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 1-6's link order; additionally follows python-for-everyone's richer per-chapter file pattern (README.md in exercises/practice/project, `interview-questions.md`, `ai-paired.html`) as instructed for Chapter 7 onward. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty, badge-coming-soon, qa-item/qa-body/qa-section-label, playbook-template/playbook-field, download-links); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text (confirmed via the same placeholder-text scan `local_check.sh` runs). All content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure only, not content), or any other TechNaom repo. |

## Required Checks

- [x] Lesson starts with a problem, not jargon — opens with a genuine, unedited live transcript from testing this chapter's own code, immediately grounding "this is real, not illustrative."
- [x] Lesson includes core concepts (system prompt, tool schema vs. tool function, the loop mapped explicitly onto Chapter 4's plan/act/observe/repeat), internal mechanics (dispatch, `_safe_path`, message appending), a worked example (two live-run transcripts), a production scenario (the hosted-provider swap with real cost/account implications), trade-offs (framework vs. hand-rolled loop in the thought-process section), security preview (`_safe_path` as harness-enforced vs. prompt-requested, explicitly tied forward to Module 5), an honest common-mistake/failure section (the reliability caveat), a thinking journal, and a summary/cheat-sheet.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (7, plus the runnable script).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves — plus an exact `.md` mirror.
- [x] Project includes a meaningful implementation artifact, verified runnable end-to-end where a live model was reachable (the standalone equivalent script), with the one specific file (`project/starter.py`/`solution.py`) that could not be re-verified live this session due to the Ollama server becoming unresponsive **explicitly disclosed above**, not silently assumed passing.
- [x] Chapter includes diagrams/visual-text architecture aids (multiple code-window blocks, including real transcripts and provider-swap diffs).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project, plus the new required files (README.md x3, interview-questions.md, ai-paired.html) all present and internally linked correctly.
- [x] Content is original — no wording, examples, or structure reused from Chapters 1-6, `mcp-for-everyone`, `python-for-everyone` (structure reference only), or any other TechNaom repo. Chapters 1-6 were read in full for terminology/continuity before writing.
- [x] Every code example was executed against the real, confirmed API shape — either live against a real Ollama server this session, or (for the two files flagged above) using the identical, already-live-verified pattern plus independently-verified mocked/stubbed testing for the parts that don't require a live model, per the task's explicit fallback instructions.
- [x] `assets/chapters-data.js` updated: `chapter-07` entry now has `path: "chapters/chapter-07-build-a-minimal-coding-agent/lesson.html"`. Also corrected the stale Module 3 `summary` and chapter-07 `description` text, which still referenced the dead "Claude Agent SDK" policy — left factually wrong text in a live, publicly-served data file would have directly contradicted this chapter's own content. Module 3's `examPath` left `null`, untouched, per task instruction.
- [x] Every internal link within this chapter's own pages verified programmatically (a small Python link-scanner over every `.html`/`.md` file's `href`/`src` attributes). The only unresolved links are the repo-wide `../../index.html` / `../../../index.html` and `docs/curriculum/index.html` root-link gaps, which don't exist yet anywhere in the repo (Step 9, pending) — the same documented, expected pattern noted in Chapters 1-6's own audits, not a new issue introduced here.
- [x] `bash scripts/local_check.sh` run from the repo root after adding all new files — all 6 checks passed (required folders, placeholder-text scan, Python syntax, `exercises/solution.py`+`project/solution.py` execution, JS syntax + chapter-path validation, secret scan). No new failures.
- [x] `python3 -m py_compile` run on all six `.py` files in this chapter (exercises, practice, project x2 each) — all compile cleanly. `exercises/solution.py` and `practice/solution.py` were additionally run to completion (exit 0, correct output) since they need no live model. `project/starter.py` and `project/solution.py` were run under plain `python3` (no `openai` installed) to confirm the graceful-degradation message and exit-0 behavior CONTRIBUTING.md requires.

## Notes on `scripts/local_check.sh` and `.github/workflows/ci.yml`

Per the task's instruction to flag rather than fix: `local_check.sh`
(and `ci.yml`'s equivalent step) currently only executes
`chapters/*/exercises/solution.py` and `chapters/*/project/solution.py`
— it does not run `practice/solution.py` at all, and it has no notion of
validating the newer file types this chapter introduces
(`README.md` x3, `interview-questions.md`, `ai-paired.html`). This
didn't cause a false pass here because this chapter's `practice/solution.py`
was manually verified separately, and the new Markdown/HTML files were
checked with a manual link-scan rather than anything in the existing
script. If Chapters 8+ keep using the richer python-for-everyone-derived
pattern, it would be worth (in a separate, explicitly-requested task)
extending `local_check.sh` and `ci.yml` to also run
`chapters/*/practice/solution.py`, since it's exactly as real and
runnable as the exercises/project ones and currently gets no CI
coverage at all.

## Follow-Up Tasks

- Re-run `project/starter.py` and `project/solution.py` against a live
  Ollama server once one is reliably reachable again, to close the one
  explicitly-flagged live-verification gap noted above. The code is
  unchanged from the already-live-verified standalone pattern, so this
  is a low-risk gap, but it should still be closed before treating this
  chapter as fully verified rather than "verified with one disclosed
  exception."
- Consider extending `scripts/local_check.sh` / `ci.yml` to run
  `practice/solution.py` files too (see note above) — not done here per
  the task's instruction not to modify CI/`local_check.sh` in this task.
- `qwen2.5-coder` is mentioned in the lesson as a stronger alternative
  model but its tool-calling behavior was explicitly *not*
  independently verified this session (per the task's instruction not
  to claim it was) — worth verifying for real in a future session if the
  course ever wants to recommend it more strongly than "worth trying."
- Module 3's Level 2 project (the real, graded version) remains
  correctly deferred to unlock after Chapter 8, per CURRICULUM_MAP.md —
  not a gap, a deliberate sequencing decision already reflected in
  `project/index.html`.
