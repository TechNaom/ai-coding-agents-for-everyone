# AI_HANDOFF.md — AI Coding Agents for Everyone

Read this before touching anything in this repo. It's written so any AI
coding assistant can pick this up cold, with zero prior context, and
not redesign decisions that were already made.

## What this repository is

An open-source, free-to-read technical course teaching AI coding agents
— using them well (Claude Code, Cursor, Copilot) and building one with
the Claude Agent SDK — part of the **TechNaom "for Everyone"** course
ecosystem. Follows the same detailed master course-building prompt as
`mcp-for-everyone` (ask the maintainer for "the TechNaom master prompt"
if you need the full philosophy — it's not stored in this repo).

## Design philosophy (non-negotiable)

Same as `mcp-for-everyone`: WHY → WHAT → HOW → BUILD → BREAK → DEBUG →
EVALUATE → SECURE → OPTIMIZE → SCALE → ARCHITECT progression; layered
depth for 5 personas; story-first; no shallow tutorials; 13 chapters,
don't pad; all content original.

## Current state (as of 2026-08-09)

**Read `PROJECT_STATE.md` for the authoritative, up-to-date status.**
Freshly scaffolded from `mcp-for-everyone`'s proven structure:

- Directory skeleton, `docs/curriculum/CURRICULUM_MAP.md`,
  `docs/course-architecture.md`, `README.md`, this file,
  `PROJECT_STATE.md`, `LICENSE`/`LICENSE-CONTENT`.
- `templates/` and shared `assets/` copied from `mcp-for-everyone` and
  rebranded (structure only, no content reused).
- **CI (`.github/workflows/ci.yml`) and `scripts/local_check.sh`**
  copied from `mcp-for-everyone` and *generalized*: the chapter-6-
  specific hardcoded long-running-server handling was replaced with a
  marker-comment convention — `# CI: LONG_RUNNING_SERVER` and
  `# CI: NEEDS_LIVE_SERVER=<path>` inside a `solution.py` file — so
  future chapters needing this don't require editing the workflow
  itself. Use these markers, don't hardcode chapter paths in CI again.
- **Critical difference from `mcp-for-everyone`**: this course's SDK
  (`claude-agent-sdk`) requires a real `ANTHROPIC_API_KEY` and costs
  real money to run — MCP's course was entirely free/local. This is an
  **unresolved open decision** (see PROJECT_STATE.md) — do not write
  Chapter 7 or any chapter that calls the SDK until it's resolved with
  the user. Chapters 1–3 (Module 1, conceptual/no-SDK) can proceed
  without this blocker.

No chapter content exists yet. No website (`index.html`) yet.

## Naming conventions

- Chapter folders: `chapters/chapter-NN-kebab-slug/`, matching
  `mcp-for-everyone`.
- Repo name: `ai-coding-agents-for-everyone`, GitHub org assumed
  `technaom` (not yet confirmed/created).

## What NOT to change

- Don't restructure the repo layout without checking
  `docs/course-architecture.md` — mirrors `mcp-for-everyone`
  deliberately.
- Don't assume `claude-agent-sdk`'s API surface from memory — verify
  against the installed package before writing Chapter 7's code, the
  same discipline that caught real bugs throughout `mcp-for-everyone`'s
  build. This is non-negotiable, see that repo's `AI_HANDOFF.md` for
  the full list of what testing-before-writing caught there.
- Don't write any chapter that calls the Claude Agent SDK until the
  `ANTHROPIC_API_KEY` open decision is resolved with the user.
- Don't hardcode a chapter-specific case into `ci.yml` again — use the
  `# CI: LONG_RUNNING_SERVER` / `# CI: NEEDS_LIVE_SERVER=` markers.
- Don't copy lesson content, examples, or project stories from
  `mcp-for-everyone` or any other TechNaom repo — structure/templates
  only.

## Current task

Resolve the `ANTHROPIC_API_KEY` open decision with the user (real
cost/scope question, not a technical detail to guess at). Then build
Chapters 1–3 (Module 1: "Using Coding Agents Well" — conceptual, no SDK
calls needed) while that decision is pending.

## Next task after that

Chapter 7 ("Build: A Minimal Coding Agent") as the reference chapter,
once the API-key question is resolved — verify the SDK's actual API
before writing any code sample. Then continue module by module per
`docs/curriculum/CURRICULUM_MAP.md`, validating each with a
`quality-audits/chapter-0N-audit.md` before moving on. Don't
mass-generate ahead of validation.

## Important architectural decisions (see PROJECT_STATE.md for full detail)

1. SDK: `claude-agent-sdk` for building agents, `mcp[cli]` for the
   tool-connection chapter.
2. 13 chapters, focused-topic sizing.
3. Static site, no backend, mirrors `mcp-for-everyone` exactly.
4. Unlike every other TechNaom course, this one has a real,
   unresolved cost implication (API calls) — don't paper over it.
