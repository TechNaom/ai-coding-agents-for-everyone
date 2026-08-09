# AI Coding Agents for Everyone — Course Architecture

## Reference Pattern

Structural reference: `TechNaom/mcp-for-everyone` (not
`rag-for-everyone` this time — `mcp-for-everyone` is the more recent,
more refined pattern, including its CI setup and quality-audit bar).
Reuse:

- Root `index.html` GitHub Pages entry point.
- Shared `assets/` (style.css, sidebar.js, progress.js, quiz-engine.js,
  chapters-data.js) — copied and rebranded, structure only.
- `chapters/chapter-XX-slug/` per-chapter folders with the full page
  set: lesson, quiz, interview-questions, exercises, practice, project.
- `docs/curriculum/CURRICULUM_MAP.md` + `docs/curriculum/index.html`.
- `templates/`, `assessments/`, `quality-audits/`.
- `PROJECT_STATE.md`, `AI_HANDOFF.md` from day one (not retrofitted).
- **CI**: `.github/workflows/ci.yml` and `scripts/local_check.sh` are
  copied from `mcp-for-everyone` and adapted (folder names, any
  course-specific long-running-process special cases) rather than
  rebuilt from scratch — that workflow is already proven.

Do not reuse `mcp-for-everyone`'s lesson content, examples, or project
stories. All coding-agent examples, exercises, and interview answers
must be original to this course.

## Production Depth Standard

Same bar as `mcp-for-everyone`: 6+ exercises (3+ production-gear) per
chapter, 6+ practice scenarios, 8+ interview questions across all 4
levels, a tested project. Every code example must be installed and run
against the real SDK/tool before being written into a lesson — this is
the single most load-bearing practice from `mcp-for-everyone` and
carries over unchanged.

## Tool/SDK Version Policy

This course teaches against the **Claude Agent SDK** (current as of
build time) for the "build your own agent" chapters, and covers
Claude Code / Cursor / GitHub Copilot at a conceptual, tool-agnostic
level for the "use agents well" chapters — specific UI details of
commercial tools change too fast to teach as exact steps; teach the
underlying practice (scoping, reviewing, iterating) that survives tool
churn. Verify current SDK package name, install command, and API
surface against primary sources before writing Chapter 7 (the
reference chapter) — do not assume prior knowledge is current.

## Conversational Clarity Standard

Same as `mcp-for-everyone`: explain like a helpful expert beside the
learner, story-first, senior-level trade-offs unpacked patiently.

## Builder Thought-Process Layer

Every chapter includes a visible reasoning section (problem framing,
options considered, chosen approach, validation, observed failure,
decision) — same pattern as `mcp-for-everyone`, adapted to
coding-agent-building decisions (which tool to give an agent, how to
scope its permissions, how to structure its loop).
