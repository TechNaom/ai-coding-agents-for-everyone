# PROJECT_STATE.md — AI Coding Agents for Everyone

Last updated: 2026-08-09

## Course Objective

Teach learners (beginner → architect) to use AI coding agents
effectively and to build one themselves, using the Claude Agent SDK and
MCP, following the TechNaom master course-building philosophy (layered
depth, story-first, production-grade, interview-ready, original content
only).

## Architecture Decisions

- **Course size: 13 chapters** (focused-topic sizing, matching
  `mcp-for-everyone`'s model).
- **Repo structure mirrors `mcp-for-everyone`** (the more refined
  reference now, not `rag-for-everyone`): static site,
  `chapters/chapter-XX-slug/`, `docs/curriculum/`, `templates/`,
  `assessments/`, `quality-audits/`, `codebase/`. Shared front-end
  assets, templates, `.github/workflows/ci.yml`, and
  `scripts/local_check.sh` were copied from `mcp-for-everyone` and
  rebranded/generalized — see below.
- **SDK: `claude-agent-sdk`** (confirmed via research 2026-08-09,
  `pip install claude-agent-sdk`, Python 3.10+, released as recently as
  2026-08-08 — verify this hasn't changed if picking this course back
  up much later). MCP Python SDK (`mcp[cli]`) also used for the
  tool-connection chapter, reusing `mcp-for-everyone`'s verified
  patterns rather than re-discovering them.
- **Cost policy (RESOLVED 2026-08-09):** chapters that invoke the
  Claude Agent SDK's model calls need a real `ANTHROPIC_API_KEY` and
  cost real money per call — this breaks the "fully free" philosophy
  other TechNaom courses have, and that's stated explicitly rather than
  hidden. Mitigation: every exercise/solution.py that calls the model
  MUST pin `ClaudeAgentOptions(model="claude-haiku-4-5", max_turns=<low>)`
  — Haiku is the cheapest model, confirmed real/documented via research
  — keeping real cost per run to fractions-of-a-cent/low-cents. State
  the approximate cost in the chapter's lesson text, don't bury it. CI
  is wired to use an `ANTHROPIC_API_KEY` repo secret if configured;
  solution.py files that need it should detect its absence and skip
  gracefully (not fail CI). **This secret has not been configured
  yet** — configure it when Chapter 7 (the reference chapter) is
  actually built, with a low budget/rate limit given the Haiku-only
  policy.
- **CI generalization:** `mcp-for-everyone`'s CI hardcoded a
  chapter-6-specific case for a long-running server. Generalized here
  (and should be backported to `mcp-for-everyone` if convenient) into a
  marker-comment convention: `# CI: LONG_RUNNING_SERVER` and
  `# CI: NEEDS_LIVE_SERVER=<path>` in a solution.py file, rather than
  hardcoding chapter paths in the workflow — more maintainable as new
  chapters are added.

## Completed

- [x] Step 1: Discovery (course vision, personas, prerequisites,
      outcomes, modules, chapters, projects, capstone, repo
      architecture, differentiators, risks, build order) — captured in
      conversation, summarized in `docs/curriculum/CURRICULUM_MAP.md`.
- [x] Research: confirmed current AI coding agent landscape (Claude
      Code, Cursor, GitHub Copilot market position) and the
      `claude-agent-sdk` package details via web search, 2026-08-09.
- [x] Step 2: Curriculum map (`docs/curriculum/CURRICULUM_MAP.md`)
- [x] Step 3: Repository architecture scaffolded — directories,
      templates, shared assets, CI (generalized from
      `mcp-for-everyone`'s), README, this file, AI_HANDOFF.md,
      LICENSE/LICENSE-CONTENT.

## Pending / Not Started

- [x] `ANTHROPIC_API_KEY` cost decision: **confirmed 2026-08-09** — keep
      the Claude Agent SDK (the course's actual subject; a generic
      open-source/local-model framework was considered and rejected as
      a scope change from Discovery), but every exercise and code
      sample must pin `ClaudeAgentOptions(model="claude-haiku-4-5", ...)`
      (confirmed real/documented via research) and a low `max_turns`
      cap, keeping real cost per run in the fractions-of-a-cent to
      low-cents range. State this cost explicitly in every chapter that
      calls the SDK — don't bury it. Still need to: configure an
      `ANTHROPIC_API_KEY` repo secret for CI once Chapter 7 exists (low
      budget given the Haiku-only policy).
- [x] `CONTRIBUTING.md`, `CHANGELOG.md` — done, adapted from
      `mcp-for-everyone`.
- [ ] Step 4: Build Chapter 7 ("Build: A Minimal Coding Agent") as the
      reference chapter — verify the Claude Agent SDK's actual API
      surface (imports, agent-loop construction, tool-definition
      pattern) against installed package before writing any code
      sample, same discipline as `mcp-for-everyone`.
- [ ] Step 5: Validate reference chapter, refine template if needed.
- [ ] Step 6: Build remaining 12 chapters module by module, validating
      after each module (Modules 1–2 are conceptual/no-SDK-needed —
      good candidates to build before the API-key decision is settled).
- [ ] Step 7–8: Projects, assessments beyond per-chapter content.
- [ ] Step 9: Website — root `index.html`, styled roadmap, GitHub Pages
      deploy (copy `mcp-for-everyone`'s `pages.yml`, already staged).
- [ ] Step 10: Capstone (Chapter 13).
- [ ] Step 12: Polish.

## Known Issues

- None yet — repo is freshly scaffolded, no chapter content written.

## Open Decisions

- **`ANTHROPIC_API_KEY` cost policy: RESOLVED 2026-08-09** — see
  "Pending / Not Started" above. Haiku-only, low `max_turns`, cost
  stated explicitly per chapter. Still open: exact CI secret budget/
  rate-limit configuration, to be set when Chapter 7 is built.
- **License**: MIT (code) + CC BY 4.0 (content), matching
  `mcp-for-everyone` — confirmed 2026-08-09, same pattern approved for
  that repo.
- **GitHub org/publish target**: confirmed 2026-08-09 —
  `github.com/TechNaom/ai-coding-agents-for-everyone`, public, `main`
  branch, matching `mcp-for-everyone`'s exact convention.

## Design Standards

See `docs/course-architecture.md` for the full standard. Chapter
completion bar matches `mcp-for-everyone`'s (6 exercises/6 practice
scenarios/8 interview questions minimum, tested code before writing).

## Next Recommended Task

Resolve the `ANTHROPIC_API_KEY` open decision with the user first —
it's a real cost/scope question, not a technical detail to guess at.
Then build Chapters 1–3 (Module 1, conceptual, no SDK calls needed)
using `mcp-for-everyone`'s Chapter 1–3 page sets as the structural
template (not content — original content required). Chapter 7 (the
reference chapter) should wait until the API-key decision lands, since
it's the first chapter that actually needs to run the SDK.
