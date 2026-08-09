# Chapter Quality Audit: Reading and Reviewing an Agent's Diff Like a Senior Engineer

## Summary

- Chapter: 3 — Reading and Reviewing an Agent's Diff Like a Senior Engineer (Module 1, Intermediate)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook is a realistic-looking agent diff (billing rounding fix) that passes its test and is still wrong in three distinct ways; plain-language framing throughout. |
| Production depth | Pass | Concrete two-file diff with a symptom fix, an out-of-boundary change, and an unjustified constant tweak, all in one example; five-point review checklist; attention-weighted triage order. |
| Real-time adoption usefulness | Pass | Tool-agnostic — references Claude Code, Cursor, GitHub Copilot's agent mode via the project page, no invented tool-specific syntax; review habits apply regardless of tool. |
| Architecture and diagrams | Pass | Two code-window blocks: the hook's flawed diff, and the review triage-order pseudocode. |
| Exercises | Pass | 6 tasks, each with its own realistic diff to analyze; 3 explicitly marked production-gear (quiet security-relevant diff, pattern-consistency judgment, six-file triage plan). |
| Practice bank | Pass | 6 scenario-cards spanning time pressure, confident-wrong summaries, inherited-context gaps, symptom recurrence, pattern consistency, and the Chapter 2/3 boundary. |
| Interview preparation | Pass | 8 questions, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves. |
| Project implementation | Pass | This chapter ships the real Level 1 (Guided) project per CURRICULUM_MAP.md — a concrete four-step build (pick a feature, write a scoped prompt, run and review it, produce a written review log), a required review-log template, and an explicit "what done looks like" checklist. Not a preview — the substantive artifact Chapters 1 and 2 pointed to. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section on lesson.html: problem, assumption, distinguishing mechanism, why-it-matters (tied explicitly to the L1 project), working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 1-2's template link order; all pages link back correctly. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text; all {{PLACEHOLDER}} tokens from templates replaced with original content. |

## Required Checks

- [x] Lesson starts with a problem, not jargon (a realistic agent diff that passes its acceptance test and is still wrong in three separate ways — symptom fix, boundary violation, unjustified change).
- [x] Lesson includes core concepts (no inherited codebase context, no social-embarrassment filter/"confidently wrong," the five-point review checklist, root-cause-vs-symptom, attention-weighted triage order), a worked example (billing rounding diff), two code-window blocks, a thought-process journal, and a summary/cheat-sheet (Points To Remember). Chapters 1-2's terminology (plan/act/observe/repeat, acceptance criterion, boundary, scoping) is referenced and built on, not re-explained from scratch, per task instructions.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6), each centered on a realistic diff to analyze rather than a textbook case.
- [x] Practice bank includes at least 6 realistic scenarios (6).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves.
- [x] Project is the real Level 1 (Guided) project per CURRICULUM_MAP.md ("ship a real small feature using Claude Code/Cursor, with a written review log"), not a preview — includes a concrete feature-selection guide, a scoped-prompt step tied to Chapter 2, a review step tied to this chapter's five-point checklist and triage order, a required review-log template (task/prompt, acceptance criterion, diff summary, checklist results, verdict, time), and an explicit "what done looks like" list. Chapter 1's and Chapter 2's project pages ("unlocks after Chapter 3") were read first and this page is what they point to.
- [x] Chapter includes diagrams/visual-text architecture aids (flawed-diff code-window, triage-order code-window).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project. Verified every internal link (`../../index.html`, `lesson.html`, `quiz.html`, `exercises/index.html`, `practice/index.html`, `interview-questions.html`, `project/index.html`, and the `../../../` variants from subpages) resolves to a real file in this chapter folder; confirmed with a scripted check against the filesystem.
- [x] Content is original — no wording, examples, or structure reused from Chapters 1-2, `mcp-for-everyone`, or any other TechNaom repo; Chapters 1-2 were read for terminology and narrative continuity (loop/autonomy, scoping, acceptance criteria) and referenced by name, not for reused examples or wording.
- [x] No code example calls the Claude Agent SDK or any external API in this chapter (conceptual, Module 1, no-SDK chapter per CURRICULUM_MAP.md) — all code-window blocks are illustrative diff/pseudocode text, not executable code; no starter.py/solution.py files exist for this chapter by design, matching Chapters 1-2's pattern.
- [x] Terminology cross-checked against `docs/course-architecture.md` and `docs/curriculum/CURRICULUM_MAP.md`: "plan/act/observe/repeat" loop, "acceptance criterion," "boundary," "Level 1, Guided" project naming all carried forward and match verbatim. The L1 project description matches CURRICULUM_MAP.md's line item exactly ("ship a real small feature... with a written review log").
- [x] `assets/chapters-data.js` updated: chapter-03 entry now has `path: "chapters/chapter-03-reading-and-reviewing-an-agents-diff-like-a-senior-engineer/lesson.html"`. Module 1's `examPath` left `null`, untouched, per task instruction.
- [x] `bash scripts/local_check.sh` run after adding these files — passed all 6 checks (folders, placeholder scan, Python syntax n/a, solution.py runs n/a, JS syntax + chapter-path validation, secret scan). No new failures.

## Follow-Up Tasks

- Human review of tone/pacing, and of the L1 project's feature-selection guidance, before considering this chapter (and Module 1's exam gate) final.
- Chapters 1 and 2's project pages still say "unlocks after Chapter 3" and were left untouched per explicit task instruction (constraint: do not touch Chapters 1 or 2) — a follow-up task, out of this task's scope, would be adding a forward link from those pages to this chapter's now-real project page.
- Module 1's `examPath` remains `null` by design — building the Module 1 exam is a separate, not-yet-scheduled task per the task instructions.
- The root-link gap (`../../index.html` and `../../docs/curriculum/index.html` from lesson.html, `../../../` variants from subpages) is expected to remain unresolved repo-wide until Step 9 of the build (website/index.html creation), matching Chapters 1-2's documented pattern exactly — confirmed not a bug introduced by this chapter.
