# AI_HANDOFF.md — AI Coding Agents for Everyone

Read this before touching anything in this repo. It's written so any AI
coding assistant can pick this up cold, with zero prior context, and
not redesign decisions that were already made.

## What this repository is

An open-source, free-to-read (and free-to-*run*) technical course
teaching AI coding agents — using them well (Claude Code, Cursor,
Copilot) and building one from scratch against a local, open-source
model via Ollama — part of the **TechNaom "for Everyone"** course
ecosystem. Follows the same detailed master course-building prompt as
`mcp-for-everyone` (ask the maintainer for "the TechNaom master prompt"
if you need the full philosophy — it's not stored in this repo).

## Design philosophy (non-negotiable)

Same as `mcp-for-everyone`: WHY → WHAT → HOW → BUILD → BREAK → DEBUG →
EVALUATE → SECURE → OPTIMIZE → SCALE → ARCHITECT progression; layered
depth for 5 personas; story-first; no shallow tutorials; 13 chapters,
don't pad; all content original.

## Current state (as of 2026-08-09, Modules 1-4 complete, Chapter 11 live)

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
- **Model/SDK dependency: REVERSED 2026-08-09, same day it was first
  resolved.** The original plan (Claude Agent SDK, Haiku-only cost
  mitigation, `ANTHROPIC_API_KEY` CI secret) is **dead — do not build
  toward it.** The user explicitly rejected any Anthropic-API
  dependency at all, not just an expensive one: "we can't go with
  anthropic either open source or low price api's we should choose."
  Final policy, confirmed via follow-up questions: **fully local,
  open-source model via Ollama**, agent loop **built from scratch**
  (no third-party agent-framework SDK) using the **`openai` Python
  package** as the HTTP client, pointed by default at Ollama's local
  OpenAI-compatible endpoint (`base_url="http://localhost:11434/v1"`,
  `api_key="ollama"` placeholder). Zero API key, zero API cost, for
  every learner by default. See `PROJECT_STATE.md`'s Architecture
  Decisions for the full reasoning and the confirmed API shape
  (`chat.completions.create(model=..., tools=[...])`,
  `message.tool_calls`, `role: "tool"` result messages).
  **Added same day**: the course itself stays open-source/low-price,
  but must give learners a documented, explicit option to point the
  identical code at a hosted provider (OpenAI, Anthropic — which added
  an OpenAI-compatible endpoint in March 2026 — or Gemini) by changing
  only `base_url`/`api_key`/`model`, since all four speak the same
  `openai` client shape. Chapter 7 needs this as a clearly-marked "use
  a hosted API instead" section, each provider's exact endpoint
  re-verified against current docs when written, not assumed from this
  note. Not yet re-verified: the exact model recommendation and its
  tool-calling support against Ollama's current model library — do
  this at the start of Chapter 7. `.github/workflows/ci.yml`'s
  `pip install` line currently installs the `ollama` package, not
  `openai` — needs updating to match this refined policy as part of
  Chapter 7's task, not done yet.

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
- Don't assume `ollama`'s Python API surface from memory — verify
  against the installed package before writing Chapter 7's code, the
  same discipline that caught real bugs throughout `mcp-for-everyone`'s
  build. This is non-negotiable, see that repo's `AI_HANDOFF.md` for
  the full list of what testing-before-writing caught there.
- Do NOT reintroduce the Claude Agent SDK or any `ANTHROPIC_API_KEY`
  dependency into a hands-on chapter — this was explicitly rejected by
  the user on 2026-08-09, after already being resolved once in the
  opposite direction earlier the same day. If cost/dependency questions
  come up again, ask before reintroducing any paid API.
- When writing any chapter that calls the model, state the hardware
  requirement (approximate RAM/disk for the model weights) explicitly
  in the lesson text — this is the direct replacement for the old
  "state the dollar cost" requirement.
- Don't hardcode a chapter-specific case into `ci.yml` again — use the
  `# CI: LONG_RUNNING_SERVER` / `# CI: NEEDS_LIVE_SERVER=` markers.
- Don't copy lesson content, examples, or project stories from
  `mcp-for-everyone` or any other TechNaom repo — structure/templates
  only.

## Current task

**Modules 1-4 (Chapters 1-10) are complete; Chapter 11 (Module 5's
first chapter) is also live.** Chapter 11 resolved everything Chapters
7-9 deliberately left open: a real fail-closed permission-scope system
(`TOOL_POLICY`, `ALLOWED`/`REQUIRES_CONFIRMATION`/`BLOCKED`,
unclassified tools default to `BLOCKED`), `confirm_with_human()`
denying on `EOFError` so an unattended run never hangs, `git_commit`
finally shipped with no `confirm` parameter, and honestly-scoped
resource-limit sandboxing (real `RLIMIT_CPU`/`RLIMIT_AS`, NOT claimed
as container-grade isolation). Read `quality-audits/chapter-11-audit.md`.
Next: Chapter 12 ("Putting an Agent in CI," Advanced) — completes
Module 5. Build directly on Chapter 11's `project/solution.py` — its
fail-closed-on-EOFError confirmation behavior is EXACTLY what makes an
agent safe to run unattended in CI (Chapter 11's own closing thought-
process section names this connection explicitly, forward-referencing
Chapter 12). Read Chapter 11 fully first. This chapter should actually
wire a real CI check, consistent with how this course already treats
its own CI as a live, tested artifact rather than a described concept.
After Chapter 12, write `assessments/written-exams/module-5-exam.md`
("production-readiness checklist exam" per CURRICULUM_MAP.md) — closes
Module 5. Then Chapter 13 (capstone, Module 6) is the final chapter of
the whole course.

**Speed note**: parallel background-agent builds have now been
validated twice (Chapter 9 + Module 1/2 exams; Chapter 10 + the CI
extension). Chapters 11 and 12 were correctly built sequentially since
12 depends on 11's exact permission system — keep doing that when
content genuinely depends on order, don't force parallelism just for
speed.

**Local-testing gotcha, learned from Chapter 11**: `scripts/local_check.sh`
must be run with `< /dev/null` (or from a genuinely non-interactive
shell) once a chapter's code calls `input()` for a live confirmation
demo (Chapter 11 onward) — an open stdin in an interactive shell makes
`input()` block for real instead of hitting `EOFError` the way it does
in CI (confirmed against the real GitHub Actions log for Chapter 11's
commit: `input()` hit EOF immediately there, denied, and continued
correctly). A "failure" without `< /dev/null` is a local-shell
artifact, not a real bug — verify against `< /dev/null` before
concluding something is broken.

**Known gaps to close when possible, not blocking**: Chapter 7's
`project/starter.py`/`solution.py` and Chapter 9's full agent-loop
path against a live model haven't been re-observed live yet (disclosed
in their respective quality-audits) — re-run once Ollama is reliably
reachable; it hung across all five build sessions so far that tried
(check `ollama ps` / try a plain completion first, every time, don't
assume resolved).

## Next task after that

Module 6 (Chapter 13: capstone) is the last chapter of the whole
course. Don't mass-generate ahead of validation.

## Important architectural decisions (see PROJECT_STATE.md for full detail)

1. Agent loop built from scratch against **Ollama** (local, open-source
   model, OpenAI-compatible tool-calling API) — no third-party agent
   SDK, no Anthropic API. `mcp[cli]` still used for the tool-connection
   chapter.
2. 13 chapters, focused-topic sizing.
3. Static site, no backend, mirrors `mcp-for-everyone` exactly.
4. Unlike the original plan, this course now has **zero** API-cost
   implication — the trade-off moved to a hardware requirement
   (local model RAM/disk) instead. State that plainly, same as the old
   dollar-cost policy required.
