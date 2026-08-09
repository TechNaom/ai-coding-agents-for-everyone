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
- **Cost/CI implication (new, didn't apply to `mcp-for-everyone`):**
  chapters that actually invoke the Claude Agent SDK's model calls need
  a real `ANTHROPIC_API_KEY` and cost real money per call. This breaks
  the "fully free and hands-on" philosophy other TechNaom courses have
  — call this out explicitly in every affected chapter, per the
  no-hype standard. CI is wired to use an `ANTHROPIC_API_KEY` repo
  secret if configured; solution.py files that need it should detect
  its absence and skip gracefully (not fail CI) rather than assume it's
  always present. **This secret has not been configured yet** — decide
  and configure before Chapter 7 (the reference chapter) needs to
  actually run.
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

- [ ] Decide and configure the `ANTHROPIC_API_KEY` repo secret question
      (see Open Decisions) before building Chapter 7.
- [ ] Step 3 continued: `CONTRIBUTING.md`, `CHANGELOG.md` (can largely
      copy `mcp-for-everyone`'s and adapt).
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

- **`ANTHROPIC_API_KEY` for CI / hands-on testing**: this course, unlike
  every prior TechNaom course, has chapters that cost real money to run
  hands-on. Needs a decision: (a) who funds a CI secret for automated
  testing, (b) whether learner-facing exercises should default to a
  free/mocked mode with real-API as opt-in, (c) how to phrase the
  README's "no signup required" claim honestly given this exception.
  Not yet resolved — resolve before Chapter 7.
- **License**: MIT (code) + CC BY 4.0 (content), matching
  `mcp-for-everyone` — files created, not yet confirmed with user for
  this specific repo.
- **GitHub org/publish target**: assumed `technaom/ai-coding-agents-for-everyone`
  by convention — not yet created or confirmed.

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
