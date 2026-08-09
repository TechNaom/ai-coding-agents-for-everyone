# Chapter Quality Audit: Why Coding Agents Aren't Just Autocomplete

## Summary

- Chapter: 1 — Why Coding Agents Aren't Just Autocomplete (Module 1, Beginner)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Story-first hook (two developers, same ticket); plain-language framing throughout. |
| Production depth | Pass | Concrete before/after example, real code snippet, common-mistake framing woven into exercises/practice rather than a separate section (appropriate for a conceptual, no-SDK chapter). |
| Real-time adoption usefulness | Pass | Explicitly names Claude Code, Cursor, GitHub Copilot agent mode, and IntelliSense as the tool-agnostic examples, per course-architecture.md's tool-version policy. |
| Architecture and diagrams | Pass | ASCII diagram contrasting autocomplete's single-shot flow with the plan/act/observe/repeat loop. |
| Exercises | Pass | 6 tasks, 3 explicitly marked production-gear (ambiguous transcript, overconfident review, ticket triage). |
| Practice bank | Pass | 6 scenario-cards spanning onboarding, debugging, estimation, trust, tool choice, incident review. |
| Interview preparation | Pass | 8 questions, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves. |
| Project implementation | Pass (scoped) | This chapter intentionally does not ship the L1 project — CURRICULUM_MAP.md states the L1 Guided project ships after Chapter 3. project/index.html is a short, honest preview stating this and explaining why, not a placeholder pretending to be a full project. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section on lesson.html: problem, assumption, distinguishing mechanism, why-it-matters, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches template link order; all pages link back correctly. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, badge-coming-soon); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text; all {{PLACEHOLDER}} tokens from templates replaced with original content. |

## Required Checks

- [x] Lesson starts with a problem, not jargon (two-developer/same-ticket hook).
- [x] Lesson includes core concepts (autocomplete ceiling, the loop, autonomy), a worked example (CSV export + code snippet), a diagram, a thought-process journal, and a summary/cheat-sheet (Points To Remember). Deep failure-lab/security/cost content is deliberately deferred to Chapters 5 (failure modes) and Module 5 (security) — this is Module 1's conceptual/daily-practice layer per CURRICULUM_MAP.md, not the internals module.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (6).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves.
- [x] Project includes a meaningful artifact appropriate to this chapter's position in the sequence: an honest, short preview of the L1 project and why it's gated until Chapter 3, per explicit task instructions — not a premature/placeholder full project.
- [x] Chapter includes diagrams/visual-text architecture aids (ASCII loop diagram).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project. Verified every internal link (`../../index.html`, `lesson.html`, `quiz.html`, `exercises/index.html`, `practice/index.html`, `interview-questions.html`, `project/index.html`) resolves to a real file in this chapter folder.
- [x] Content is original — no wording, examples, or structure reused from `mcp-for-everyone` or any other TechNaom repo; that repo was consulted only for HTML/class structure per the task's explicit instruction.
- [x] No code example calls the Claude Agent SDK or any external API in this chapter (conceptual, Module 1, no-SDK chapter per CURRICULUM_MAP.md) — the one code snippet (`export.py`) is illustrative Python shown for reading, not executed, so the "tested before writing" rule for solution.py files doesn't apply here; no starter.py/solution.py files exist for this chapter by design.
- [x] Terminology cross-checked against `docs/course-architecture.md` and `docs/curriculum/CURRICULUM_MAP.md`: "plan/act/observe/repeat" loop naming, "Level 1, Guided" project naming, module/chapter titles all match verbatim.
- [x] `assets/chapters-data.js` updated: chapter-01 entry now has `path: "chapters/chapter-01-why-coding-agents-arent-just-autocomplete/lesson.html"`. `examPath` for Module 1 left `null` (no written exam exists yet).
- [x] `bash scripts/local_check.sh` run after adding these files — see Follow-Up Tasks for result.

## Follow-Up Tasks

- Human review of tone/pacing for a true beginner audience before considering this chapter final.
- When Chapter 2 and 3 are built, cross-link forward from this chapter's "Points to Remember" if useful (currently references Chapters 2/3 by name only, no links, since those pages don't exist yet — adding links now would 404).
- Revisit project/index.html once the real L1 project spec exists (post-Chapter-3) to make sure the preview's description still matches exactly.
