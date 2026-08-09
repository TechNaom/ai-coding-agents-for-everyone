# Chapter Quality Audit: The Agentic Loop: Plan, Act, Observe, Repeat

## Summary

- Chapter: 4 — The Agentic Loop: Plan, Act, Observe, Repeat (Module 2, Intermediate)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook opens the hood on a concrete rate-limiting task, showing two literal turns (tool_use + tool_result JSON) rather than describing the loop abstractly; plain-language framing throughout. |
| Production depth | Pass | Covers tool-call/tool-result mechanics, stateless-turn re-reading, tool selection via description-matching (no separate router), four+one named stop conditions, and the upfront-plan-vs-reactive-replanning trade-off, all grounded in one running example. |
| Real-time adoption usefulness | Pass | Tool-agnostic mechanism explanation applies to Claude Code, Cursor, and Copilot agent mode alike; project page explicitly has students pull a transcript from whichever tool they use. |
| Architecture and diagrams | Pass | Four code-window blocks: turn 1/turn 2 raw JSON, the tool-description comparison table, and the upfront-vs-reactive planning trace comparison. |
| Exercises | Pass | 6 tasks, each requiring precise turn-by-turn tracing of a scenario; 3 explicitly marked production-gear (unrevised upfront plan causing a missed migration call site, ambiguous tool descriptions causing a silent no-op fix, rebuilding a full turn-by-turn trace from a compressed summary). |
| Practice bank | Pass | 6 scenario-cards spanning folk-psychology mistranslation, trusting a clean-stop message, step-cap vs. genuine completion, a working boundary, an unrevised upfront plan, and raw-transcript literacy for a junior engineer. |
| Interview preparation | Pass | 8 questions, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves. |
| Project implementation | Pass | Ships the real Level 2 lab per CURRICULUM_MAP.md ("trace a real agent transcript and annotate each loop step") — concrete 5-step build (run and capture a real transcript, number turns, annotate three fields per turn, identify the stop condition, write it up), a required annotated-trace.md template, and an explicit "what done looks like" checklist. Not a preview — real, gradable lab content. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section on lesson.html: problem (human-sounding explanations that don't predict behavior), assumption, distinguishing mechanism, why-it-matters (tied explicitly to Chapter 5's diagnosis work), working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 1-3's template link order; all pages link back correctly. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text; all content is original and specific to this chapter's mechanism. |

## Required Checks

- [x] Lesson starts with a problem, not jargon (a concrete rate-limiting task shown as two literal turns of raw tool_use/tool_result data, not an abstract description of "the loop"). Verified complete and well-formed on disk before continuing (no truncation, proper closing tags) — read in full prior to building the remaining pages.
- [x] Lesson includes core concepts (tool call/tool result mechanics, stateless re-reading, tool-selection-by-description-matching, four+one stop conditions, upfront-plan vs. reactive re-planning), a worked example (rate-limiting task carried through all sections), four code-window blocks, a thought-process journal, and a summary/cheat-sheet (Points To Remember). Chapters 1-3's terminology (plan/act/observe/repeat, acceptance criterion, boundary) is referenced and built on, not re-explained from scratch.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6), each centered on tracing a specific scenario against the mechanism rather than a textbook recall question.
- [x] Practice bank includes at least 6 realistic scenarios (6).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves.
- [x] Project is the real Level 2 lab per CURRICULUM_MAP.md ("trace a real agent transcript and annotate each loop step"), not a preview — includes a concrete task-selection guide, a turn-numbering step, a three-field-per-turn annotation step, a stop-condition identification step tied to this chapter's four+one mechanisms, a required annotated-trace.md template, and an explicit "what done looks like" list.
- [x] Chapter includes diagrams/visual-text architecture aids (turn-1/turn-2 raw JSON, tool-description comparison, planning-style comparison code-windows).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project. Verified every internal link (`../../` and `../../../` relative paths, plus same-folder links) resolves to a real file in this chapter's folder with a scripted filesystem check; only the repo-wide `../../index.html` and `../../docs/curriculum/index.html` root-link gap remains unresolved, matching Chapters 1-3's documented, expected pattern (root `index.html` and `docs/curriculum/index.html` don't exist yet repo-wide).
- [x] Content is original — no wording, examples, or structure reused from Chapters 1-3, `mcp-for-everyone`, or any other TechNaom repo; Chapters 1-3 were read for terminology and narrative continuity (loop/autonomy naming, acceptance criteria, review discipline) and referenced by name, not for reused examples or wording.
- [x] No code example calls the Claude Agent SDK or any external API in this chapter (conceptual, Module 2, no-SDK chapter per CURRICULUM_MAP.md — SDK work starts Module 3) — all code-window blocks are illustrative JSON/pseudocode/trace text, not executable code; no starter.py/solution.py files exist for this chapter by design, matching Chapters 1-3's pattern.
- [x] Terminology cross-checked against `docs/course-architecture.md` and `docs/curriculum/CURRICULUM_MAP.md`: "plan/act/observe/repeat" loop, "tool call"/"tool result," "acceptance criterion," "Level 2" lab naming all carried forward and match verbatim. The L2 lab description matches CURRICULUM_MAP.md's line item exactly ("trace a real agent transcript and annotate each loop step").
- [x] `assets/chapters-data.js` updated: chapter-04 entry now has `path: "chapters/chapter-04-the-agentic-loop-plan-act-observe-repeat/lesson.html"`. Checked first and confirmed it was not already set before this session's edit. Module 2's `examPath` left `null`, untouched, per task instruction.
- [x] `bash scripts/local_check.sh` run after adding these files — see result below.

## Follow-Up Tasks

- Human review of tone/pacing, and of the L2 lab's task-sizing guidance (whether 4-8 turns is the right minimum for a useful trace), before considering this chapter final.
- The root-link gap (`../../index.html` and `../../docs/curriculum/index.html` from lesson.html, `../../../` variants from subpages) is expected to remain unresolved repo-wide until the site's top-level `index.html` and `docs/curriculum/index.html` are built, matching Chapters 1-3's documented pattern exactly — confirmed not a bug introduced by this chapter.
- Module 2's `examPath` remains `null` by design — building the Module 2 exam (concept quiz + failure-diagnosis exercise per CURRICULUM_MAP.md) is a separate, not-yet-scheduled task.
- Chapters 5 and 6 (Module 2, not yet built) will need to reference this chapter's L2 lab and mechanism terminology (tool call/tool result, stop conditions, plan-vs-reactive) for continuity, the same way this chapter referenced Chapters 1-3.
