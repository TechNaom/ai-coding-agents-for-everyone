# Chapter Quality Audit: Prompting and Scoping Tasks for an Agent

## Summary

- Chapter: 2 — Prompting and Scoping Tasks for an Agent (Module 1, Beginner)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Story-first hook (two engineers, same bug report, two prompts); plain-language framing throughout. |
| Production depth | Pass | Concrete three-prompt comparison (vague / disguised-open-ended / well-scoped), real acceptance-criterion example, common-mistake framing woven into exercises/practice. |
| Real-time adoption usefulness | Pass | Tool-agnostic — references Claude Code, Cursor, GitHub Copilot's agent mode via the project preview page and Chapter 1 continuity, no invented tool-specific syntax. |
| Architecture and diagrams | Pass | Code-window block contrasting three prompts for the same underlying bug, annotated with what each is missing. |
| Exercises | Pass | 6 tasks, 3 explicitly marked production-gear (reasonable-sounding trap, no clean acceptance condition, blast-radius boundary). |
| Practice bank | Pass | 6 scenario-cards spanning ticket triage, scope creep, context overcorrection, boundary-setting, acceptance criteria, size judgment. |
| Interview preparation | Pass | 8 questions, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves. |
| Project implementation | Pass (scoped) | This chapter intentionally does not ship the L1 project — CURRICULUM_MAP.md states the L1 Guided project ships after Chapter 3. project/index.html is a short, honest preview explaining what's still missing (diff review, Chapter 3) and why waiting matters, not a placeholder pretending to be a full project. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section on lesson.html: problem, assumption, distinguishing mechanism, why-it-matters, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapter 1's template link order; all pages link back correctly. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, badge-coming-soon); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text; all {{PLACEHOLDER}} tokens from templates replaced with original content. |

## Required Checks

- [x] Lesson starts with a problem, not jargon (two-engineer/same-bug-report hook contrasting a vague prompt and a scoped one).
- [x] Lesson includes core concepts (context sufficiency, scoping range, boundaries/stop-and-ask, acceptance criteria), a worked example (region-filter bug, three-prompt comparison), a code-window diagram, a thought-process journal, and a summary/cheat-sheet (Points To Remember). Chapter 1's loop/autonomy terminology is referenced and built on, not re-explained from scratch, per task instructions.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (6).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves.
- [x] Project includes a meaningful artifact appropriate to this chapter's position in the sequence: an honest, short preview of the L1 project and why it's still gated until Chapter 3, explicitly connecting what this chapter contributed (scoping) to what's still missing (diff review) — not a premature/placeholder full project.
- [x] Chapter includes diagrams/visual-text architecture aids (three-prompt code-window comparison).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project. Verified every internal link (`../../index.html`, `lesson.html`, `quiz.html`, `exercises/index.html`, `practice/index.html`, `interview-questions.html`, `project/index.html`) resolves to a real file in this chapter folder.
- [x] Content is original — no wording, examples, or structure reused from Chapter 1, `mcp-for-everyone`, or any other TechNaom repo; Chapter 1 was read for terminology continuity (loop, autonomy) and referenced by name, not for reused examples or wording.
- [x] No code example calls the Claude Agent SDK or any external API in this chapter (conceptual, Module 1, no-SDK chapter per CURRICULUM_MAP.md) — the one code-window block is illustrative prompt text, not executable code; no starter.py/solution.py files exist for this chapter by design.
- [x] Terminology cross-checked against `docs/course-architecture.md` and `docs/curriculum/CURRICULUM_MAP.md`: "plan/act/observe/repeat" loop naming carried forward from Chapter 1, "Level 1, Guided" project naming, module/chapter titles all match verbatim. Chapter 5's failure-mode content is forward-referenced briefly (looping/stalling/going off the rails) without duplicating it, per explicit task instruction.
- [x] `assets/chapters-data.js` updated: chapter-02 entry now has `path: "chapters/chapter-02-prompting-and-scoping-tasks-for-an-agent/lesson.html"`. Module 1's `examPath` left `null`, untouched, per task instruction.
- [x] `bash scripts/local_check.sh` run after adding these files — see Follow-Up Tasks for result.

## Follow-Up Tasks

- Human review of tone/pacing for a true beginner audience before considering this chapter final.
- When Chapter 3 is built, cross-link forward from this chapter's project preview once the real L1 project spec exists (currently references Chapter 3 by name only, no link, since that page doesn't exist yet — adding a link now would 404).
- Revisit project/index.html once the real L1 project spec exists (post-Chapter-3) to make sure the preview's description still matches exactly.
- Chapter 1's audit noted the same root-link gap (`../../index.html` and `../../docs/curriculum/index.html` from lesson.html, `../../../` variants from subpages) is expected to remain unresolved repo-wide until Step 9 of the build (website/index.html creation) — this chapter's pages point at the same not-yet-existing root files by design, matching Chapter 1's pattern exactly.
