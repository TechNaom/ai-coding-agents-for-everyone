# Chapter Quality Audit: Giving Your Agent File/Shell/Git Tools

## Summary

- Chapter: 8 — Giving Your Agent File/Shell/Git Tools (Module 3, Advanced)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## What was actually verified against a live Ollama server (this build session)

None of this chapter's agent code was run against a live model this
session. Before writing any code, this session re-checked whether a
local Ollama server was actually generating, not just responding to
`/api/tags`:

- `curl http://localhost:11434/api/tags` — responded normally,
  confirming `llama3.2:latest` is pulled and the server process is up.
- `curl http://localhost:11434/v1/chat/completions` with a plain,
  non-tool chat message — **timed out (exit code 124) after 12
  seconds**, with no response at all.

This matches exactly the sandbox-wide generation hang disclosed in
`quality-audits/chapter-07-audit.md` and flagged again in the task
briefing for this chapter — the server accepts connections and answers
metadata queries, but generation itself never completes. This is not a
bug in this chapter's code; it's the same environment issue Chapter 7's
own build session hit partway through its work. Per the task's explicit
instruction, this session did not burn further time retrying the hang
and instead followed the disclosed fallback: write real, syntactically
valid, logically sound Python using Chapter 7's exact confirmed API
shape, test everything that doesn't require live generation, and
disclose the gap honestly here rather than claiming live verification
that didn't happen.

**Consequence, stated plainly:** `project/starter.py` and
`project/solution.py` (and by extension the code blocks reproduced in
`lesson.html`) were **not** run end-to-end against a real model this
session. The agent loop itself (`run_agent`, `dispatch_tool_call`,
`main`) is copied unchanged from Chapter 7's already-live-verified
code — nothing about the loop or dispatch mechanism is new in this
chapter. What's new is the tool layer, and every new tool function was
independently tested without a live model (see below).

## What was tested without live model access

All of the following was actually executed in this session, not
asserted from memory:

- **`project/solution.py`'s tool functions**, called directly (not
  through the model) against a real temporary `WORKSPACE` directory
  with a real `git init` inside it:
  - `write_file` / `read_file` round-trip.
  - `edit_file`: a well-formed single-occurrence replace (confirmed the
    file's actual on-disk content changed correctly), a "text not
    found" case, and an ambiguous two-occurrence case (`"foo foo"`,
    replacing `"foo"`) — all three returned the exact error/success
    strings the lesson and code comments claim.
  - `list_directory`: the workspace root listing (includes `.git` and
    the written file), a missing-directory case, and a
    called-on-a-file-not-a-directory case — three distinct, correct
    error/success strings.
  - `git_status` and `git_diff`, called against the real git repo —
    `git_status` correctly reported the untracked file
    (`?? notes.txt`), `git_diff` correctly reported no unstaged changes
    for a tracked-then-unmodified case.
  - `run_shell_command`: a real `ls` (succeeded, returned real stdout),
    and two denylist-blocked calls (`rm -rf /`, `sudo rm notes.txt`) —
    both correctly refused with the expected `"error: command blocked
    (...)"` message, confirmed the command never actually ran.
  - `_safe_path`: confirmed it raises `ValueError` on a workspace-escape
    attempt (`"../../etc/passwd"`).
  - `dispatch_tool_call`: tested via a small fake `tool_call`-shaped
    object (matching the real `openai` client's `tc.function.name` /
    `tc.function.arguments` shape) against a well-formed call, malformed
    JSON, a missing required argument, an unknown tool name, and a
    zero-argument tool (`git_status`) — all five produced the correct
    string or result, with no exception escaping.
- **`project/starter.py`** (the partial scaffold, missing
  `list_directory` on purpose) — confirmed it still runs correctly
  without that tool: `write_file` works, `TOOL_FUNCTIONS` has exactly
  the six provided tools (no `list_directory`), and `list_directory` is
  correctly absent from the `TOOLS` schema list, confirming the scaffold
  is genuinely partial rather than accidentally complete.
- **Graceful degradation**: both `project/starter.py` and
  `project/solution.py`, run under plain `python3` with no `openai`
  package installed, printed `"The openai package isn't installed. Run:
  pip install openai"` and exited 0 — matching Chapter 7's required
  CI-safety behavior exactly.
- **`exercises/solution.py`** — `edit_file_stub` and
  `is_command_blocked` fully implemented and tested against 9 hardcoded
  scenarios (well-formed edit, a follow-up check that the in-memory
  "disk" actually changed, text-not-found, an ambiguous two-occurrence
  case, a missing file, an unblocked ordinary command, and three
  distinct denylist-blocked commands). `python3 solution.py` prints
  `9/9 checks passed.` and exits 0. `starter.py` correctly raises
  `NotImplementedError` on the first call until filled in (verified —
  the traceback shows the exact expected line).
- **`practice/solution.py`** — the denylist-vs-allowlist comparison
  script, run live: all eight commands produced the printed
  ALLOW/BLOCK verdicts documented in the file's own answer-key
  docstring, confirmed by direct comparison against the actual printed
  output.
- **All six `.py` files in this chapter** compile cleanly under
  `python3 -m py_compile` (`project/starter.py`, `project/solution.py`,
  `exercises/starter.py`, `exercises/solution.py`,
  `practice/starter.py`, `practice/solution.py`).
- **`bash scripts/local_check.sh`**, run from the repo root after
  adding all new files — all 6 checks passed: required folders,
  placeholder-text scan, Python syntax, `exercises/solution.py` +
  `project/solution.py` execution, JS syntax + chapter-path validation,
  secret scan.
- **Internal link scan**: a Python script scanning every `href`/`src`
  attribute in this chapter's `.html` files and every Markdown link in
  its `.md` files, resolving each relative to its source file. 68
  internal links checked; the only unresolved ones are the repo-wide
  `../../index.html` / `../../../index.html` and
  `docs/curriculum/index.html` root-link gaps, which don't exist
  anywhere in the repo yet (Step 9, pending) — the same documented,
  expected pattern Chapters 1-7's own audits noted, not a new issue
  introduced here.

## What was NOT verified live, stated honestly

- **The full agent loop, end to end, against a real model**, for either
  `project/starter.py` or `project/solution.py`. Every tool function
  above was independently confirmed correct by calling it directly, and
  the loop/dispatch mechanism around them is Chapter 7's own,
  already-live-verified code, unmodified — but the actual sequence of
  "model reads the system prompt, decides to call `edit_file`, model
  reads the result, decides to call `git_status`" was not observed as a
  real, live transcript this session, the way Chapter 7's hook and
  "Watching It Actually Run" sections could show two genuine unedited
  runs. This is the direct, disclosed consequence of the generation
  hang confirmed at the top of this document, not an oversight.
- **The reliability caveat Chapter 7 named** (a small model occasionally
  producing malformed tool-call arguments) was not re-observed or
  re-tested against this chapter's new tools specifically — no claim in
  `lesson.html` asserts it was. The existing defensive handling
  (`dispatch_tool_call`'s `JSONDecodeError`/`KeyError`/generic-`Exception`
  branches, unchanged from Chapter 7) covers new tools the same way it
  covered the original three, by construction, not because it was
  re-tested against a live malformed call this session.
- The exact hardware/model recommendation (`llama3.2`) was not
  re-benchmarked this session — it's carried forward unchanged from
  Chapter 7's own confirmed recommendation, since this chapter doesn't
  change the model or the loop.

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook opens with a concrete, specific failure scenario (a 400-line config file, `write_file`-only risk) rather than jargon, directly motivating `edit_file` before any code appears. |
| Production depth | Pass | Five new tools built with real design discussion each: `edit_file`'s ambiguous-match refusal, `list_directory`'s type-distinguishing errors (a deliberate correct rebuild of Chapter 7's flawed AI-paired version), `git_status`/`git_diff`'s list-argument safety, and `run_shell_command`'s honestly-limited denylist with an explicit denylist-vs-allowlist trade-off section. |
| Real-time adoption usefulness | Pass | Every code block matches the actual, tested code in `project/starter.py`/`solution.py`; all tool functions independently verified callable and correct without needing a live model. |
| Architecture and diagrams | Pass | Code-window blocks for every new tool, the assembled `TOOL_FUNCTIONS`/`dispatch_tool_call` extension, and a guarded `git_commit` sketch shown explicitly as discussion-only, not shipped code. |
| Exercises | Pass | 6 tasks in `exercises/index.html`, 3 production-gear (tasks 4-6: extending the denylist for a real incident without a false positive, constructing a one-character ambiguity case, and reviewing a hypothetical git_commit design's actual safety properties). Tasks 1-2 map to real, live-tested TODOs (9/9 passing). |
| Practice bank | Pass | 7 scenario cards in `practice/index.html` (exceeds the 6 minimum) plus a runnable, live-tested denylist-vs-allowlist comparison script covering all 8 scripted commands with a predict-then-run structure and a full answer key. |
| Interview preparation | Pass | 8 questions in `interview-questions.html`, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves; exact plain-markdown mirror in `interview-questions.md`. |
| Project implementation | Pass (with the live-loop disclosure above) | This is the real Module 3 L2 project, not a preview page. `project/starter.py` is a genuine partial scaffold (five tools fully implemented and tested, one deliberately left as a `# TODO` for the learner); `project/solution.py` shows one fully worked, tested example (`list_directory`, built correctly where Chapter 7's AI-paired version was flawed). `project/README.md` gives concrete, live-model-independent verification steps as well as full end-to-end instructions. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section: problem (assuming more tools just means more `write_file`-shaped functions), assumption, what actually distinguishes safe tools (read-only by construction vs. needing explicit failure-mode design), why it matters before Chapter 9, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 1-7's link order; uses the same richer python-for-everyone-derived file pattern (README.md x3, `interview-questions.md`) Chapter 7 established. No `ai-paired.html` — Chapter 7 already ships the one AI-pairing page for this stretch of the course, and this chapter's own project (a learner's own tool, reviewed with Chapter 3's checklist against their own diff) already delivers the "produce something, then critique it" arc without duplicating that page. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty, chapter-badge); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text (confirmed via the same placeholder-text scan `local_check.sh` runs, plus a manual read-through). All content is original — no wording, examples, or structure reused from Chapter 7, `mcp-for-everyone`, `python-for-everyone` (structure only, not content), or any other TechNaom repo. |

## Required Checks

- [x] Lesson starts with a problem, not jargon — opens with a specific, concrete failure scenario (a large config file, `write_file`-only risk) that directly motivates the chapter's first new tool.
- [x] Lesson includes core concepts (overwrite vs. targeted edit, discovery-before-action, read-only vs. write-capable git tools, denylist vs. allowlist), internal mechanics (`edit_file`'s ambiguous-match counting, `list_directory`'s type checks, `subprocess.run` list-args vs. shell-string), a worked example (the assembled `TOOL_FUNCTIONS` extension), a production scenario (scoping tool access differently for different agent roles, covered in interview Q7), trade-offs (edit vs. overwrite, denylist vs. allowlist, both stated without overselling either), a security preview (`git_commit` deliberately not shipped, explicitly tied to Module 5), an honest common-mistake/failure section (the denylist's honest limits, stated plainly), a thinking journal, and a summary/cheat-sheet.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (7, plus the runnable script).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves — plus an exact `.md` mirror.
- [x] Project includes a meaningful implementation artifact, verified runnable and correct where a live model was not required (every new tool function independently tested, both starter.py's partial-scaffold state and solution.py's fully-worked state confirmed), with the full agent-loop-against-a-live-model gap **explicitly disclosed above**, not silently assumed passing. This is the real, graded Level 2 project per `docs/curriculum/CURRICULUM_MAP.md`, not a preview page.
- [x] Chapter includes diagrams/visual-text architecture aids (multiple code-window blocks, including the discussion-only `git_commit` sketch clearly marked as not shipped).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project, plus the required files (README.md x3, `interview-questions.md`) present and internally linked correctly. `ai-paired.html` deliberately not duplicated — see navigation note in the Scores table above.
- [x] Content is original — no wording, examples, or structure reused from Chapter 7, `mcp-for-everyone`, `python-for-everyone` (structure reference only), or any other TechNaom repo. Chapter 7 was read in full (lesson, quiz, interview questions, exercises, practice, project including `ai-paired.html`) before writing, per the task's explicit instruction, and this chapter's code deliberately extends Chapter 7's exact loop/dispatch pattern rather than redesigning it.
- [x] Every new tool function was executed directly against real inputs (a real temp workspace with a real git repo, or a real in-memory fake filesystem for the exercises/practice scripts) this session — the one explicitly disclosed gap is the full agent loop against a live model, which Chapter 7's own build already verified for the identical loop/dispatch code, and which this session could not re-verify for the new tool layer specifically due to the generation hang confirmed at the top of this document.
- [x] `assets/chapters-data.js` updated: `chapter-08` entry now has `path: "chapters/chapter-08-giving-your-agent-file-shell-git-tools/lesson.html"`. Module 3's `examPath` left `null`, untouched, per task instruction.
- [x] Every internal link within this chapter's own pages verified programmatically (a Python link-scanner over every `.html`/`.md` file's `href`/`src`/Markdown-link targets). The only unresolved links are the repo-wide root-link gaps documented above, matching the same pattern noted in every prior chapter's audit.
- [x] `bash scripts/local_check.sh` run from the repo root after adding all new files — all 6 checks passed. No new failures.
- [x] `python3 -m py_compile` run on all six `.py` files in this chapter — all compile cleanly. `exercises/solution.py` and `practice/solution.py` were additionally run to completion (exit 0, correct output). `project/starter.py` and `project/solution.py` were run under plain `python3` (no `openai` installed) to confirm the graceful-degradation message and exit-0 behavior, and every individual tool function inside both files was called directly and confirmed correct (see the live-tested section above).

## Environment note: the generation hang, re-confirmed

Before writing any code, this session ran:

```
curl -s http://localhost:11434/api/tags          # responded normally
curl -s http://localhost:11434/v1/chat/completions -d '{...}'   # timed out, exit 124, 12s
```

This matches Chapter 7's own build session's experience exactly (`/api/tags`
healthy, actual generation hanging indefinitely) and the task briefing's
explicit warning that this is a persistent, sandbox-wide issue. Per the
task's instructions, this session did not retry the hang repeatedly —
one confirmation attempt was enough to establish the same known state —
and instead worked from Chapter 7's exact, already-live-verified API
shape and loop code, focusing live testing effort on the new tool layer
specifically, where it was actually possible to verify without a
reachable model.

## Follow-Up Tasks

- Re-run `project/starter.py` (after a learner adds their own tool) and
  `project/solution.py` against a live Ollama server once one is
  reliably reachable again, to observe a real end-to-end transcript
  exercising `edit_file`, `list_directory`, `git_status`, and the
  denylist together — closing the one explicitly-flagged gap in this
  audit. Low risk: the loop/dispatch code is unchanged from Chapter 7's
  already-live-verified version, and every new tool function was
  independently confirmed correct.
- Chapter 7's own audit flagged that `scripts/local_check.sh`/`ci.yml`
  don't run `practice/solution.py` files — still true, still not fixed
  here per the same instruction not to modify CI/`local_check.sh`
  without being asked. This chapter's `practice/solution.py` was
  manually verified separately, same as Chapter 7's was.
- The `git_commit` design question this chapter previews is deliberately
  left open, pointing to Chapter 11 (Security: Sandboxing, Permissions,
  Destructive Commands) for a real resolution — not a gap, a deliberate
  sequencing decision matching how Chapter 7's `_safe_path` section
  previewed Module 5 without fully covering it.
