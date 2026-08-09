# Chapter Quality Audit: Why Agents Loop, Stall, or Go Off the Rails

## Summary

- Chapter: 5 — Why Agents Loop, Stall, or Go Off the Rails (Module 2, Intermediate)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook opens with a concrete, realistic import-error thrashing transcript (turns 4-9) rather than an abstract description of "failure modes"; plain-language framing throughout. |
| Production depth | Pass | Covers all four forward-referenced failure modes (looping/thrashing, stalling, compounding mistakes/going off the rails, premature "done") each explained mechanically via Chapter 4's stateless-per-turn-prediction-over-a-growing-conversation model, plus a dedicated mitigation-patterns section (scoping/boundaries, acceptance criteria, step caps, human transcript review). |
| Real-time adoption usefulness | Pass | Mitigation section gives concrete, tool-agnostic actions (narrow scoping, checkable acceptance criteria, step caps, reading transcripts for named patterns) applicable to any real coding agent tool. |
| Architecture and diagrams | Pass | Five code-window blocks: the hook's turn-4-9 thrashing trace, a stalling trace, a compounding-mistake trace (misread search result), and a premature-done trace (clean-stop message with no fresh test run). |
| Exercises | Pass | 6 tasks, each requiring precise identification of which failure mode is occurring and why; 3 explicitly marked production-gear (a confident diff shipping the wrong fix on a production incident, designing a log-only stalling detector, and diagnosing a step-cap cutoff on a database migration). |
| Practice bank | Pass | 6 scenario-cards spanning folk-psychology mistranslation ("just being thorough"), a guess hardening into stated fact, trusting a stale test run, an unhelpful "try harder" instruction, a boundary's preventive vs. damage-limiting effect, and reading a stall from step-count alone. |
| Interview preparation | Pass | 8 questions, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves. |
| Project implementation | Pass | Correctly does not duplicate Chapter 4's real Level 2 lab; short page points to it directly (with a working cross-chapter link), explains why revisiting it now (with the four failure-mode shapes in hand) is worthwhile, and previews Chapter 7 as Module 3's first hands-on build, following the brevity pattern of Chapters 1/2's project pages. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section on lesson.html: problem (human-sounding "stuck/confused/lazy" descriptions), assumption (different malfunctions need different diagnoses), the actual distinguishing mechanism (same prediction mechanism, different conversational contents), why it matters day to day, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 1-4's template link order; all pages link back correctly. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text; all content is original and specific to this chapter's failure-mode mechanisms. |

## Required Checks

- [x] Lesson starts with a problem, not jargon (a concrete, realistic thrashing transcript — an import-error fix looping back to its own first failed attempt — not an abstract description of "failure modes"). Verified complete and well-formed on disk before continuing.
- [x] Lesson delivers on Chapters 1, 2, and 4's explicit forward-references: "why agents loop, stall, or go off the rails," "the compounding-mistake failure mode," and "thrashing" are all named and mechanically explained here, each tied directly to Chapter 4's per-turn-prediction-over-a-growing-conversation model rather than described only impressionistically.
- [x] Lesson includes core concepts (looping/thrashing, stalling, going off the rails/compounding mistakes, premature "done", mitigation patterns), five code-window transcript examples, a thought-process journal, and a summary/cheat-sheet (Points To Remember). Chapters 1-4's terminology (plan/act/observe/repeat, tool call/tool result, clean stop, acceptance criterion, boundary, scoping) is referenced and built on, not re-explained from scratch.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6), each centered on identifying a specific failure mode and its mechanism in a transcript excerpt.
- [x] Practice bank includes at least 6 realistic scenarios (6).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves.
- [x] Project page does not duplicate Chapter 4's real Level 2 lab content; instead links directly to it (`../../chapter-04-the-agentic-loop-plan-act-observe-repeat/project/index.html`, verified resolves to a real file) and previews Chapter 7 as Module 3's next hands-on build, matching the brevity of Chapters 1/2's project-preview pages.
- [x] Chapter includes diagrams/visual-text architecture aids (five code-window transcript traces).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project. Verified every internal link with a scripted filesystem check across all six pages; only the repo-wide `../../index.html` / `../../../index.html` and `../../docs/curriculum/index.html` / `../../../docs/curriculum/index.html` root-link gap remains unresolved, matching Chapters 1-4's documented, expected pattern (root `index.html` and `docs/curriculum/index.html` don't exist yet repo-wide). No other missing links found, including the cross-chapter link into Chapter 4's project page.
- [x] Content is original — no wording, examples, or structure reused from Chapters 1-4, `mcp-for-everyone`, or any other TechNaom repo; Chapters 1-4 were read in full for terminology and narrative continuity (loop mechanism, acceptance criteria, review discipline, stop conditions) and referenced by name, not for reused examples or wording.
- [x] No code example calls the Claude Agent SDK or any external API in this chapter (conceptual, Module 2, no-SDK chapter per CURRICULUM_MAP.md — SDK work starts Module 3) — all code-window blocks are illustrative transcript/pseudocode text, not executable code; no starter.py/solution.py files exist for this chapter by design, matching Chapters 1-4's pattern.
- [x] Terminology cross-checked against `docs/course-architecture.md` and `docs/curriculum/CURRICULUM_MAP.md`: "plan/act/observe/repeat" loop, "tool call"/"tool result," "clean stop"/"hard stop"/"boundary stop"/"failure stop," "acceptance criterion" all carried forward and match verbatim.
- [x] `assets/chapters-data.js` updated: chapter-05 entry now has `path: "chapters/chapter-05-why-agents-loop-stall-or-go-off-the-rails/lesson.html"`. Module 2's `examPath` left `null`, untouched, per task instruction — confirmed unchanged.
- [x] `bash scripts/local_check.sh` run after adding these files — all six checks passed (required folders, placeholder-text scan, Python syntax, exercises/solution.py execution [none present, skipped cleanly], JS syntax + chapter-path validation, secret scan). No new failures.

## Follow-Up Tasks

- Human review of tone/pacing, and of whether the hook's import-error thrashing example is the strongest possible opener (an alternative considered and set aside: a compounding-mistake hook instead, since that failure mode is arguably the highest-stakes one — thrashing was kept as the opener because it's the most visually obvious "loop" to a reader seeing this material for the first time, with compounding mistakes given its own full section immediately after).
- Chapter 6 (Module 2, not yet built) will need to reference this chapter's four named failure modes (looping/thrashing, stalling, going off the rails, premature "done") for continuity, the same way this chapter referenced Chapter 4's mechanism vocabulary, and should explain how context-window pressure interacts with or worsens some of these failure modes (particularly stalling and compounding mistakes, where older forcing facts can fall out of effective context).
- Module 2's `examPath` remains `null` by design — building the Module 2 exam (concept quiz + failure-diagnosis exercise per CURRICULUM_MAP.md) is a separate, not-yet-scheduled task, expected once Chapter 6 ships.
