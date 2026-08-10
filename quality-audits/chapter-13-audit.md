# Chapter Quality Audit: Capstone — Design an Agent Workflow for a Real Team

## Summary

- Chapter: 13 — Capstone: Design an Agent Workflow for a Real Team (Module 6, Architect, closes the course)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-10
- Status: Ready for human review

This is the course's final chapter and its shape is deliberately
different from Chapters 7-12: the center of the deliverable is a
design document (a business scenario, a permission-scope design, an
audit-trail design, three real ADRs, and a rubric), not a new agent
implementation. One concrete mechanism — a regulated-path-aware
extension of Chapters 11-12's `TOOL_POLICY`/`TOOL_POLICY_CI` pattern —
is shown precisely in real, runnable code, matching the task's
explicit allowance ("it can include real, runnable code where a
concrete mechanism benefits from it"), but most of this chapter's
content is markdown design documents (ADRs, a rubric, a project
README), not Python.

## Live-tested-vs-logical-only disclosure

**Runnable code in this chapter is limited to one mechanism** — a
regulated-path classifier, mode-aware `write_file`/`git_commit` scope
checks, mandatory CI-mode actor attribution, and a redacted, append-only
audit log, extending Chapter 12's `TOOL_POLICY_CI` pattern for the
fictional Meridian Ledger scenario (PCI-DSS Level 1 + SOX Section 404).
Every piece of it was independently, directly executed this session:

- **`project/solution.py`, full demo** (`python3 solution.py < /dev/null`)
  — confirmed on a real, freshly-initialized disposable git repo
  (never touching this course repo's own git history, via the same
  `_temp_git_workspace()` pattern Chapter 12 established): (1) a
  non-regulated write inside `ci-scratch/` actually succeeded; (2) a
  write nested under `ci-scratch/payments/card_intake/` was refused —
  proving the regulated-path check catches a pattern nested under an
  otherwise-allowed scratch prefix, not just a bare regulated path,
  which is the specific design claim Section 3 of the lesson makes;
  (3) a direct write to a GL path was refused; (4) a commit attempt
  with no actor set on a real, non-protected scratch branch was
  refused with the "no attributable actor" error, even though the
  branch and staged files were otherwise fully compliant; (5) the same
  commit, retried with an actor set, actually succeeded, producing a
  real commit hash, and `git log -1 --format=%B` on the real repo
  confirmed both the `Agent-Run-Id` and `Triggered-By` trailers were
  actually present in the commit message, not just constructed and
  discarded; (6) a commit attempt staging a file under
  `payments/card_intake/` was refused, citing the specific staged
  file and its category, even on a non-protected branch with a valid
  actor attached — confirming the regulated-path check on
  `git_commit` is independent of (and cannot be bypassed by
  satisfying) the branch and actor checks; (7) the audit log file was
  read back after the run and printed, confirming six real JSON lines
  were written with the correct actor/tool/tier per call, including
  the calls that were refused — the audit log records attempted
  actions, not just successful ones, which is the specific design
  claim Section 4 of the lesson makes.
- **A real bug found and fixed live, not caught by review alone**: the
  first version of `regulated_category()` used `path.startswith(pattern)`
  (a leading-prefix match, matching Chapter 12's `_in_ci_scratch()`
  convention). Running scenario 2 of the demo above
  (`ci-scratch/payments/card_intake/notes.txt`) with that version
  produced a successful write, not a refusal, because the CDE pattern
  `"payments/card_intake/"` does not appear at the START of a path
  that begins with `"ci-scratch/"` — even though the lesson text and
  this file's own docstring both describe the check as catching a
  regulated pattern nested under a scratch prefix. Caught by actually
  running the demo and noticing the printed output didn't match the
  documented behavior, not by re-reading the code. Fixed by switching
  to substring containment (`p in normalized`) in `project/solution.py`,
  `project/starter.py`'s TODO 1 docstring, and `exercises/solution.py`'s
  `classify_path` — all three now consistently describe and implement
  containment, not prefix matching, and this is called out explicitly
  in the lesson's Section 3 code comment.
- **A second real bug found and fixed live**: `redact_pan()`'s original
  regex, `r"\b(?:\d[ -]?){13,19}\b"`, consumed a trailing separator
  character as part of its last repetition, so redacting
  `"card: 4111111111111111 approved"` produced
  `"card: [REDACTED-PAN]approved"` (the space before "approved" was
  silently absorbed into the match) instead of the expected
  `"card: [REDACTED-PAN] approved"`. Caught by a failing exercise
  check, not by inspection — `exercises/solution.py`'s own test harness
  flagged the mismatch on the first run. Fixed by changing the pattern
  to `r"\b\d(?:[ -]?\d){12,18}\b"` (a separator only ever appears
  BETWEEN two digits, never trailing after the last one) in all three
  files that define this pattern (`project/solution.py`,
  `project/starter.py`, `exercises/solution.py`) — reran all affected
  scripts afterward to confirm the fix.
- **`exercises/solution.py`** — run live, 15/15 checks pass, including
  the two regression-relevant checks above (nested-scratch containment,
  trailing-separator redaction).
- **`exercises/starter.py`** — run through `python3 -m py_compile`
  (compiles cleanly); not executed to completion, since all three TODOs
  intentionally raise `NotImplementedError` by design, matching
  Chapters 11-12's starter-file convention. Not part of
  `local_check.sh`'s solution-only run loop, so this doesn't affect the
  automated check either.
- **`practice/solution.py`** — run live, prints all six scripted tool
  calls with distinct, correct decisions (`ALLOWED`/`REFUSED` per call,
  each with a specific reason string) — confirmed the six scenarios
  actually exercise six different code paths (policy tier, regulated
  write, scratch-scope write, protected branch, and two variants of the
  git_commit checks), not six copies of the same outcome.
- **`practice/starter.py`** — compiles cleanly; `decide()` intentionally
  raises `NotImplementedError`, matching the exercises pattern.
- **`project/starter.py`** — compiles cleanly; all three TODOs
  intentionally raise `NotImplementedError`, matching Chapters 11-12's
  starter-file convention (a partially-implemented harness should fail
  loudly and specifically, not silently do the wrong thing).

## What was NOT attempted this session, and why

**No live agent-loop call against Ollama** is made anywhere in this
chapter's code, by design, not by omission — this chapter's own subject
(a CI policy extension) is pure harness-side logic, the same
"the interesting code lives in a place the model never sees" framing
Chapters 11-12 used, and the lesson explicitly says so in its closing
recap. There is therefore no live-model gap to disclose for this
chapter specifically, unlike Chapters 7-9's carried-forward Ollama-hang
gap (which remains open for those chapters, not this one).

**No real OIDC/GitHub Actions integration** was built or tested —
`get_actor()` reads a plain environment variable
(`MERIDIAN_TRIGGERED_BY`) as a stand-in for a real OIDC-verified actor
identity, and both `project/solution.py`'s docstring and ADR-003 say so
explicitly, naming this as a genuine, disclosed gap between the ADR's
decision and the demo code that accompanies it — not hidden or implied
to be production-ready as written.

**No real PCI-DSS/SOX compliance review** of this design was performed
by an actual compliance professional — Meridian Ledger, its scenario,
and its specific regulatory framing are original, plausible, but
fictional, built for teaching purposes; the chapter and rubric both
name this design's own open gaps rather than presenting it as a
certified-compliant reference architecture.

**`example-adrs/`'s three ADRs and `capstone-rubric.md`** are prose
design documents, not runnable code — verified for internal
consistency (cross-references between ADRs and the lesson text; the
rubric's seven criteria map onto content actually covered by the
lesson) by direct reading, not by an automated check, since none of
this content has a "run it" verification path by nature.

## Internal link check

A Python link-scanner (checking every `href`/`src`/Markdown-link target
across every `.html`/`.md` file in this chapter's directory) found
every internal link resolves: `lesson.html`'s links to all three
example ADRs, the rubric, and the interview-questions page; every
`chapter-nav` link across `quiz.html`/`exercises/index.html`/
`practice/index.html`/`interview-questions.html`/`project/index.html`;
`project/README.md`'s and `project/index.html`'s links to
`starter.py`/`solution.py`/`adr-template.md`/`capstone-rubric.md`. Zero
broken links found.

## `bash scripts/local_check.sh < /dev/null`

Run from the repo root after all files were added. All 6 checks
passed:

1. Required folders present.
2. No placeholder text found.
3. `python3 -m py_compile` succeeded on all `.py` files across the
   whole repo, including this chapter's 6.
4. Every `exercises/solution.py`, `project/solution.py`, and
   `practice/solution.py` across the whole repo ran successfully,
   including this chapter's three — none call `input()` or reference
   `sys.stdin`, so none hit `local_check.sh`'s special-case branches;
   all three completed well under the 20-second timeout with exit
   code 0.
5. JS syntax check and `chapters-data.js` chapter-path validation
   passed — confirmed `chapters/chapter-13-capstone-design-an-agent-workflow-for-a-real-team/lesson.html`
   resolves as a real file.
6. No likely secrets found.

`.github/workflows/ci.yml` and `scripts/local_check.sh` themselves
were not modified, per the explicit constraint not to touch CI files.

## Registration

- `assets/chapters-data.js`: Module 6's chapter-13 entry now has
  `path: "chapters/chapter-13-capstone-design-an-agent-workflow-for-a-real-team/lesson.html"`.
  Module 6's `examPath` left `null` — per
  `docs/curriculum/CURRICULUM_MAP.md`, Module 6's stated assessment IS
  the capstone rubric itself (`project/capstone-rubric.md`), not a
  separate written exam, matching this task's explicit default
  guidance.

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | The hook states Meridian Ledger's two regulatory regimes concretely (PCI-DSS Level 1, SOX Section 404) and poses compliance's actual question before any mechanism is introduced, matching this course's story-first standard. |
| Production depth | Pass | A fully worked, live-tested regulated-path classifier, mode-aware scope checks, mandatory actor attribution, and a redacted audit log — plus three real, filled-out ADRs and a seven-criterion rubric with three levels each, matching the L4 Architecture Challenge's stated deliverable shape. |
| Course-wide synthesis | Pass | Every mechanism in this chapter is traced explicitly to a specific earlier chapter (Chapter 3's checklist, Chapter 5's failure modes, Chapters 7-9's harness discipline, Chapters 11-12's permission/CI model) rather than presented as new material — the lesson's own "GenAI Builder Thought Process" section makes this traceability the chapter's explicit closing point. |
| Honesty about gaps | Pass | The rubric's cross-cutting criterion, ADR-001/002/003's Consequences sections, interview question 8, and this audit's own "not attempted" section all name specific, real, unsolved gaps (pattern-list drift, no real OIDC integration, no professional compliance review) rather than presenting the design as fully solved. |
| Course closure | Pass | The lesson's lede, Section 2's opening, and the closing Points to Remember explicitly name this as the course's final chapter and tie back to the full Module 1-6 arc, per the task's explicit requirement. |

## Known limitations, disclosed

- `regulated_category()`'s two pattern lists
  (`CDE_PATH_PATTERNS`/`GL_PATH_PATTERNS`) are illustrative, not
  exhaustive — the lesson, the exercises, and the practice bank all
  name pattern-list drift as a real, open risk rather than implying
  these three or four example prefixes constitute a complete
  classification of any real org's regulated surface.
- The redaction regex (`PAN_PATTERN`) is a narrow, defense-in-depth
  scrub for the audit log specifically — explicitly not presented as
  Meridian Ledger's real PCI cardholder-data masking control, which
  would live in the actual payment-processing code, out of this
  chapter's scope.
- `get_actor()`'s environment-variable stand-in for a verified OIDC
  identity is a simulation for this offline demo, not a claim that
  this file implements real OIDC verification — stated explicitly in
  both the code's docstring and ADR-003.
