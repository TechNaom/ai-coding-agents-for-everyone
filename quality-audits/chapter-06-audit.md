# Chapter Quality Audit: Context Windows and Codebase-Scale Understanding

## Summary

- Chapter: 6 — Context Windows and Codebase-Scale Understanding (Module 2, Intermediate)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook opens with a concrete eleven-file migration transcript where a rule stated on turn 3 is technically still present but silently violated on turn 68, immediately making "presence isn't influence" tangible before any abstract explanation. |
| Production depth | Pass | Covers what a context window is mechanically (tokens, re-sent every turn given Chapter 4's statelessness), the crowding/dilution distinction from a hard-limit cutoff, why codebase-scale understanding is structurally limited (search-first pattern, no "whole codebase in view"), and a dedicated mitigations section (padding harms, scoping, compaction risk, fresh-session trade-off) tied back to Chapter 5's failure modes. |
| Real-time adoption usefulness | Pass | Mitigations section gives concrete, tool-agnostic actions (why not to paste whole docs, scoping sessions, spot-checking compaction output, when a fresh session beats a long one) applicable to any real coding agent tool. |
| Architecture and diagrams | Pass | Four code-window blocks: the hook's turn-3/turn-68 contrast, plus a human-memory-vs-agent-context comparison block illustrating codebase-scale limits. |
| Exercises | Pass | 6 tasks, each requiring precise reasoning about what was/wasn't in context and why; 3 explicitly marked production-gear (diagnosing a summarization bug that lost a deprecation notice, a restart-vs-continue judgment call using both Ch5 and Ch6 vocabulary, and designing a minimal per-session restatement for a multi-session migration). |
| Practice bank | Pass | 6 scenario-cards spanning a false "plenty of room left" reassurance, a well-intentioned full-repo-dump prompt, a "should already know" onboarding-convention assumption, a compaction step that dropped a deliberate exception, a four-hour unattended run judgment call, and a missed-search codebase-scale miss. |
| Interview preparation | Pass | 8 questions, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves. |
| Project implementation | Pass | Correctly does not duplicate Chapter 4's real Level 2 lab; short page points to it, explicitly closes out Module 2 (naming the concept-quiz-plus-failure-diagnosis assessment from CURRICULUM_MAP.md as a separate, not-yet-built task), and previews Chapter 7 as Module 3's first hands-on build, following the brevity pattern of Chapters 1/2/5's project pages. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section on lesson.html: problem (binary "ignored me" vs. "context must be full" false dichotomy), assumption (context is all-or-nothing like a deleted file), the actual distinguishing mechanism (graceful, probabilistic crowding/dilution vs. a hard cutoff), why it matters day to day, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 1-5's template link order; all pages link back correctly. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text; all content is original and specific to this chapter's context-window mechanism. One tag-mismatch typo found and fixed during authoring (a `<span class="scenario-tag">` closed with `</h3>` in practice/index.html scenario 2) — corrected before this audit. |

## Required Checks

- [x] Lesson starts with a problem, not jargon (a concrete migration transcript where an early rule gets violated 65 turns later despite never being deleted from the conversation, not an abstract definition of "context window").
- [x] Lesson delivers on Chapter 4's explicit forward-reference ("what actually happens as the conversation grows toward that limit, and why an agent seems to 'forget' earlier turns well before the limit is technically reached — is Chapter 6's subject in full") and Chapter 2's forward-reference ("Chapter 6 covers context-window limits in depth") — both are paid off directly and by name, not re-derived from scratch.
- [x] Lesson includes core concepts (what a context window is, tokens, re-sent-every-turn cost given Chapter 4's statelessness, crowding vs. dilution as distinct from a hard cutoff, why codebase-scale understanding is structurally limited, mitigation patterns), four code-window examples, a thought-process journal, and a summary/cheat-sheet (Points To Remember) that also functions as a light Module 2 capstone tying Chapters 4/5/6 together explicitly.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (6).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves.
- [x] Project page does not duplicate Chapter 4's real Level 2 lab content; instead links directly to it (`../../chapter-04-the-agentic-loop-plan-act-observe-repeat/project/index.html`, verified resolves to a real file), explicitly names the Module 2 assessment (concept quiz + failure-diagnosis exercise per CURRICULUM_MAP.md) as a separate tracked task rather than building it here, and previews Chapter 7 as Module 3's next hands-on build, matching the brevity of Chapters 1/2/5's project-preview pages.
- [x] Chapter includes diagrams/visual-text architecture aids (four code-window blocks, including a human-memory-vs-agent-context comparison).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project. Verified every internal link with a manual filesystem-relative check across all six pages; only the repo-wide `../../index.html` / `../../../index.html` and `../../docs/curriculum/index.html` / `../../../docs/curriculum/index.html` root-link gap remains unresolved, matching Chapters 1-5's documented, expected pattern (root `index.html` and `docs/curriculum/index.html` don't exist yet repo-wide, pending Step 9). No other missing links found, including the cross-chapter link into Chapter 4's project page.
- [x] Content is original — no wording, examples, or structure reused from Chapters 1-5, `mcp-for-everyone`, or any other TechNaom repo; Chapters 1-5 were read in full for terminology and narrative continuity (loop mechanism, tool calls/results, stop conditions, the four named failure modes) and referenced by name, not for reused examples or wording.
- [x] No code example calls the Claude Agent SDK or any external API in this chapter (conceptual, Module 2, no-SDK chapter per CURRICULUM_MAP.md — SDK work starts Module 3) — all code-window blocks are illustrative transcript/pseudocode/JSON text, not executable code; no starter.py/solution.py files exist for this chapter by design, matching Chapters 1-5's pattern.
- [x] Terminology cross-checked against `docs/course-architecture.md` and `docs/curriculum/CURRICULUM_MAP.md`: "plan/act/observe/repeat," "tool call"/"tool result," "clean stop"/"hard stop"/"boundary stop"/"failure stop," "stateless between turns," and the four Chapter 5 failure-mode names (looping/thrashing, stalling, going off the rails, premature "done") all carried forward and match verbatim.
- [x] `assets/chapters-data.js` updated: chapter-06 entry now has `path: "chapters/chapter-06-context-windows-and-codebase-scale-understanding/lesson.html"`. Module 2's `examPath` left `null`, untouched, per task instruction — confirmed unchanged.
- [x] `bash scripts/local_check.sh` run after adding these files — all six checks passed (required folders, placeholder-text scan, Python syntax [skipped, no Python files], exercises/solution.py execution [none present, skipped cleanly], JS syntax + chapter-path validation, secret scan). No new failures.

## Follow-Up Tasks

- Module 2's `examPath` remains `null` by design — building the Module 2 written exam / assessment (concept quiz + failure-diagnosis exercise per CURRICULUM_MAP.md) under `assessments/` is a separate, not-yet-scheduled task, now unblocked since all three Module 2 chapters exist.
- Human review of tone/pacing, and of whether the migration-transcript hook is the strongest possible opener (an alternative considered and set aside: opening directly with the token/context-window definition — set aside because a concrete "still there but ignored" moment lands harder before the mechanical explanation, matching Chapters 4 and 5's own pattern of narrative-before-mechanism).
- Module 2 is now fully built (Chapters 4-6). Per `PROJECT_STATE.md`'s "Next Recommended Task," the next work is configuring the `ANTHROPIC_API_KEY` CI secret and building Chapter 7 (the reference chapter) — verifying the Claude Agent SDK's actual API surface against the installed package before writing any code sample, and writing the Module 2 assessment (noted above) before or alongside that work.
