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

## Current state (as of 2026-08-09, Modules 1-2 complete)

**Read `PROJECT_STATE.md` for the authoritative, up-to-date status.**

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
- **CI is verified green on real GitHub Actions runners** (not just
  local). Two bootstrap bugs were found and fixed on the first real
  runs: (1) git doesn't track empty directories, so `chapters/` and
  other empty scaffold dirs never made it into the first push —
  fixed with `.gitkeep` placeholders; (2) the `structure-check` job's
  quality-audit-matching loop used an unexpanded `chapters/chapter-*/`
  glob that failed under `bash -e` when zero chapters existed — fixed
  with `shopt -s nullglob`. GitHub Pages is enabled
  (`https://technaom.github.io/ai-coding-agents-for-everyone/`) via
  `gh api repos/TechNaom/ai-coding-agents-for-everyone/pages -X POST -f build_type=workflow`.
- **Module 1 (Chapters 1-3) is built and live**: "Why Coding Agents
  Aren't Just Autocomplete," "Prompting and Scoping Tasks for an
  Agent," "Reading and Reviewing an Agent's Diff Like a Senior
  Engineer." Each has lesson/quiz/interview-questions/exercises/
  practice/project pages and a quality-audits/chapter-0N-audit.md.
  Chapter 3 ships the real L1 project. Each chapter was built by a
  fresh subagent briefed to read the prior chapters first for
  continuity, then reviewed by the orchestrating session before commit
  — that pattern worked well and was reused for Module 2.
- **Module 2 (Chapters 4-6) is built and live**: "The Agentic Loop:
  Plan, Act, Observe, Repeat," "Why Agents Loop, Stall, or Go Off the
  Rails," "Context Windows and Codebase-Scale Understanding." Chapter 4
  opens the hood on the loop mechanism and hosts Module 2's real lab.
  Chapter 5 names four failure modes mechanically, paying off Chapters
  1/2/4's forward-references. Chapter 6 closes the module (context
  windows, graceful degradation, codebase-scale limits) and explicitly
  ties Ch4 and Ch5 together as a recap. All conceptual, no SDK calls.
  Module 1 and 2 written exams are NOT built yet (`examPath` still null
  for both modules).
- **Structural reference changed 2026-08-09**: the user confirmed
  `python-for-everyone` (34 chapters, richer per-chapter files —
  `README.md` in exercises/practice/project, `ai-paired.html`,
  `interview-questions.md` alongside the `.html` version) is the
  preferred structural reference going forward, not the
  `mcp-for-everyone` pattern Chapters 1-6 were built against. Decision:
  forward-only — Chapters 1-6 stay as-is (already shipped, CI-verified);
  apply the richer pattern starting with Chapter 7. Don't retrofit 1-6
  without being asked.
- **Critical difference from `mcp-for-everyone`**: this course's SDK
  (`claude-agent-sdk`) requires a real `ANTHROPIC_API_KEY` and costs
  real money to run — MCP's course was entirely free/local. **RESOLVED
  2026-08-09**: every exercise/solution.py that calls the model MUST
  pin `ClaudeAgentOptions(model="claude-haiku-4-5", max_turns=<low>)`
  to keep real cost to fractions-of-a-cent/low-cents per run, and state
  that approximate cost in the chapter's lesson text. See
  `PROJECT_STATE.md`'s Architecture Decisions for the full reasoning
  (a fully open-source/local-model alternative was considered and
  rejected as a scope change from this course's actual subject). Still
  need to configure the `ANTHROPIC_API_KEY` CI secret when Chapter 7 is
  built — not needed for Module 2 either (still conceptual).

No website root `index.html` yet (Step 9, comes later).

## Naming conventions

- Chapter folders: `chapters/chapter-NN-kebab-slug/`, matching
  `mcp-for-everyone`.
- Repo name: `ai-coding-agents-for-everyone`, GitHub org `TechNaom`
  (confirmed, public, `main` branch — same convention as
  `mcp-for-everyone`).

## What NOT to change

- Don't restructure the repo layout without checking
  `docs/course-architecture.md` — mirrors `mcp-for-everyone`
  deliberately.
- Don't assume `claude-agent-sdk`'s API surface from memory — verify
  against the installed package before writing Chapter 7's code, the
  same discipline that caught real bugs throughout `mcp-for-everyone`'s
  build. This is non-negotiable, see that repo's `AI_HANDOFF.md` for
  the full list of what testing-before-writing caught there.
- When writing any chapter that calls the Claude Agent SDK, always pin
  `model="claude-haiku-4-5"` and a low `max_turns` — this is the
  resolved cost policy, not optional. State the approximate real cost
  in the lesson text.
- Don't hardcode a chapter-specific case into `ci.yml` again — use the
  `# CI: LONG_RUNNING_SERVER` / `# CI: NEEDS_LIVE_SERVER=` markers.
- Don't copy lesson content, examples, or project stories from
  `mcp-for-everyone` or any other TechNaom repo — structure/templates
  only.

## Current task

Configure the `ANTHROPIC_API_KEY` CI secret, then build Chapter 7
("Build: A Minimal Coding Agent") as the reference chapter — the first
chapter that actually runs the SDK, and the first to use
python-for-everyone's richer per-chapter file pattern instead of the
mcp-for-everyone-derived one Chapters 1-6 used. Verify the SDK's actual
API surface against the installed package before writing any code
sample (non-negotiable — same discipline that caught real bugs
throughout `mcp-for-everyone`'s build). Pin `model="claude-haiku-4-5"`
and a low `max_turns`, state the approximate real cost in the lesson
text. Read Chapters 1-6 fully first for continuity/terminology.

## Next task after that

Continue module by module per `docs/curriculum/CURRICULUM_MAP.md`
(Module 3: Chapters 8-9), validating each with a
`quality-audits/chapter-0N-audit.md` before moving on. Also write the
Module 1 and Module 2 written exams (assessments/written-exams/) —
outstanding but not blocking. Don't mass-generate ahead of validation.

## Important architectural decisions (see PROJECT_STATE.md for full detail)

1. SDK: `claude-agent-sdk` for building agents, `mcp[cli]` for the
   tool-connection chapter.
2. 13 chapters, focused-topic sizing.
3. Static site, no backend, mirrors `mcp-for-everyone` exactly.
4. Unlike every other TechNaom course, this one has a real,
   unresolved cost implication (API calls) — don't paper over it.
