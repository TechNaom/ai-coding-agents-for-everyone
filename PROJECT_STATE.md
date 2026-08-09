# PROJECT_STATE.md — AI Coding Agents for Everyone

Last updated: 2026-08-09 (Modules 1-2 complete; SDK/model policy reversed)

## Course Objective

Teach learners (beginner → architect) to use AI coding agents
effectively and to build one themselves, from scratch against a local
open-source model (via Ollama) and MCP, following the TechNaom master
course-building philosophy (layered depth, story-first,
production-grade, interview-ready, original content only).

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
- **SDK/model policy: REVERSED 2026-08-09, then refined same day.**
  The prior "Claude Agent SDK + Haiku-only cost mitigation" policy
  below is **superseded** — the user explicitly rejected any
  Anthropic-API-dependent design, not just an expensive one. New
  policy: build the agent loop **from scratch** using the **`openai`
  Python package** (`pip install openai`) as the HTTP client, pointed
  by default at **Ollama**'s local OpenAI-compatible endpoint
  (`base_url="http://localhost:11434/v1"`, `api_key="ollama"` —
  required but unchecked placeholder) rather than at
  `api.openai.com`. Confirmed via research 2026-08-09: Ollama serves a
  genuine `/v1/chat/completions` route with tool-calling support for
  tool-calling-capable models (`chat.completions.create(model=...,
  messages=..., tools=[...])`, tool calls on `message.tool_calls`,
  results sent back as `role: "tool"` messages). No third-party
  agent-framework SDK is used — the loop is written directly against
  Chapter 4's plan/act/observe/repeat mechanism and the provider's raw
  tool-calling API, deliberately, so the mechanism stays visible.
  Recommended model: a tool-calling-capable open-weight model
  (candidates: Qwen2.5-coder, Llama 3.1) — **re-verify** the current
  recommendation and exact tool-calling support against Ollama's model
  library before writing Chapter 7's code; not yet re-confirmed at the
  code level, only at the API-shape level. Zero API cost, zero API key,
  for every learner by default — but a real hardware cost (RAM/disk for
  local model weights) that must be stated explicitly in the lesson
  text, replacing the old "state the dollar cost" requirement with
  "state the hardware requirement." MCP Python SDK (`mcp[cli]`) is
  unaffected by this reversal, still used for the tool-connection
  chapter (Chapter 9).
- **Learner provider-swap option (added 2026-08-09, same day as the
  reversal):** the course's own build stays open-source/low-price by
  default (Ollama), but Chapter 7 must give learners an explicit,
  documented option to point the exact same agent code at a hosted
  provider instead, if they prefer. Confirmed via research 2026-08-09:
  Anthropic (since March 2026) and Google Gemini both expose their own
  OpenAI-compatible `/v1/chat/completions`-style endpoints (Anthropic's
  is documented as a testing/evaluation layer, not their recommended
  production path — `platform.claude.com/docs/api/openai-sdk`). Because
  Ollama, OpenAI, Anthropic, and Gemini all speak the same `openai`
  client shape, swapping providers is exactly one `base_url`/`api_key`/
  `model` change — no rewrite. Chapter 7 needs a clearly-marked "use a
  hosted API instead" section showing this swap for all three
  alternatives, each verified against that provider's *current*
  documentation before being written into the lesson — do not assume
  the March 2026 Anthropic compatibility layer's exact shape (or
  Gemini's) is still accurate by the time Chapter 7 is actually
  written; re-check.
- **Superseded cost policy (for history only — do not follow):** the
  original 2026-08-09 resolution kept the Claude Agent SDK and pinned
  `ClaudeAgentOptions(model="claude-haiku-4-5", max_turns=<low>)` to
  keep Anthropic API cost to fractions-of-a-cent per run, with an
  `ANTHROPIC_API_KEY` CI secret planned for Chapter 7. The user
  rejected this entirely later the same day — no Anthropic API
  dependency of any kind, cheap or not. Nothing under this bullet
  should be implemented; it's kept only so a future reader understands
  why references to Haiku/ClaudeAgentOptions may still appear in old
  commit messages.
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
- [x] CI bootstrap fix: git doesn't track empty directories, so the
      first real CI run 404'd on `chapters/` and other empty scaffold
      dirs — fixed with `.gitkeep` files. Also fixed a `structure-check`
      job bug (unexpanded `chapters/chapter-*/` glob under `bash -e`
      failed when zero chapters existed) with `shopt -s nullglob`.
      GitHub Pages enabled via `gh api .../pages -X POST`. Both CI
      Checks and Deploy GitHub Pages are green on real GitHub Actions
      runners as of this update.
- [x] **Module 1 built and live** — Chapters 1–3 (Why Coding Agents
      Aren't Just Autocomplete; Prompting and Scoping Tasks for an
      Agent; Reading and Reviewing an Agent's Diff Like a Senior
      Engineer), each with lesson, quiz (6-8 fill-in-blank), 8 interview
      questions across all 4 levels, 6 exercises (3+ production-gear),
      6 practice scenarios, and a quality-audits/chapter-0N-audit.md.
      Chapter 3 also ships the real L1 project ("ship a real small
      feature with a written review log") that Ch1/Ch2 pointed to.
      All conceptual, no SDK calls — built without needing the
      ANTHROPIC_API_KEY decision below to be operationalized yet.
- [x] **Module 2 built and live** — Chapters 4–6 (The Agentic Loop:
      Plan, Act, Observe, Repeat; Why Agents Loop, Stall, or Go Off the
      Rails; Context Windows and Codebase-Scale Understanding). Same
      per-chapter quality bar as Module 1. Chapter 4 opens the hood on
      the loop mechanism (tool calls as structured model output,
      stateless per-turn prediction, four-plus-one stop conditions) and
      hosts Module 2's real lab ("trace and annotate a transcript").
      Chapter 5 names four failure modes (looping/thrashing, stalling,
      going off the rails, premature "done") mechanically in terms of
      Chapter 4's model. Chapter 6 closes the module: context windows,
      why "forgetting" is graceful degradation (crowding/dilution) not
      a hard cutoff, why codebase-scale understanding is inherently
      limited, and ties back to both Ch4 and Ch5. All conceptual, no
      SDK calls. One authoring bug found and fixed by the build agent
      (mismatched HTML tag in Ch6 practice page) before commit — worth
      spot-checking future chapters' practice pages for the same class
      of error. Module 1 and 2 written exams are NOT built yet
      (`examPath` still null for both).
- [x] **Chapter 7 built and live — reference chapter, starts Module 3**:
      "Build: A Minimal Coding Agent." First chapter with real, running
      code: agent built from scratch against the `openai` package
      pointed at Ollama's local endpoint (`llama3.2`, tool calling
      confirmed live), 3 tools with a harness-enforced `_safe_path`
      boundary, a ~30-line loop mapped explicitly onto Chapter 4's
      vocabulary, two genuine live-run transcripts, a directly-observed
      reliability caveat (small models sometimes send malformed tool
      arguments) with the defensive code it demands, and a verified
      "use a hosted API instead" section (OpenAI/Anthropic/Gemini via
      their OpenAI-compatible endpoints, each re-checked against
      current docs). First chapter using the richer
      python-for-everyone-derived file pattern (README.md in
      exercises/practice/project, `interview-questions.md`,
      `ai-paired.html`). **Known gap, disclosed not hidden**:
      `project/starter.py`/`solution.py` weren't re-observed live in
      the build session or in this session's own re-check — the local
      Ollama server hung on every generation call (even a plain
      non-tool completion) both times, a sandbox-wide issue, not a
      code bug. Re-run live once Ollama is reliably reachable, to close
      this one flagged gap. Also flagged, not yet done: extend
      `scripts/local_check.sh`/`ci.yml` to also run
      `practice/solution.py` files (currently only exercises/project
      solutions run in CI).
- [x] **Chapter 8 built and live**: "Giving Your Agent File/Shell/Git
      Tools." Deepens Chapter 7's tool layer without touching its loop:
      `edit_file` (targeted find-and-replace, refuses ambiguous
      multi-match edits), `list_directory` (a corrected rebuild of
      Chapter 7's flawed AI-paired `list_files` tool — deliberate
      before/after teaching moment), `git_status`/`git_diff` (read-only,
      list-args `subprocess.run`, no `shell=True`), and a
      denylist-hardened `run_shell_command`. Deliberately does NOT ship
      a `git_commit` tool — discussed honestly as unresolved, previewing
      Chapter 11. Ships Module 3's real L2 project (partial scaffold,
      one TODO tool for the learner). Every new tool function
      live-tested directly against a real temp workspace/git repo; full
      agent-loop generation against Ollama not re-verified this session
      (same sandbox-wide hang as Chapter 7, disclosed not hidden).

## Pending / Not Started

- [x] Model/SDK dependency decision: **reversed 2026-08-09** — dropped
      Claude Agent SDK / Anthropic API entirely (see "REVERSED
      2026-08-09" above). New policy: Ollama + local open-source model,
      agent loop built from scratch, zero API cost/key for any learner.
- [ ] Confirm the specific Ollama model recommendation (Qwen2.5-coder
      vs. Llama 3.1 vs. a newer option) and its tool-calling support
      against Ollama's current model library — do this at the start of
      Chapter 7, not before; verify against the actually-installed
      package/model, not from memory or this note.
- [ ] Update `.github/workflows/ci.yml` and `scripts/local_check.sh`:
      remove the `ANTHROPIC_API_KEY`/`claude-agent-sdk` install steps,
      add an Ollama install + model pull step for chapters that need
      it. Not yet done as of this note — do this alongside or just
      before Chapter 7's CI needs it.
- [x] `CONTRIBUTING.md`, `CHANGELOG.md` — done, adapted from
      `mcp-for-everyone`.
- [ ] Step 4: Build Chapter 7 ("Build: A Minimal Coding Agent") as the
      reference chapter — verify Ollama's actual tool-calling API
      surface (imports, chat/tool-call shape, tool-definition pattern)
      against the installed `ollama` package before writing any code
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

- None currently open. Chapters 1-6 (Modules 1-2) built, CI-verified
  green on real GitHub Actions runners, and live on GitHub Pages.

## Structural reference note (2026-08-09)

The user confirmed `python-for-everyone` (34 chapters, richer
per-chapter file set — `README.md` in `exercises/`/`practice/`/
`project/`, `ai-paired.html`, `interview-questions.md` alongside the
`.html` version, top-level `capstones/`) is the preferred structural
reference for TechNaom courses going forward, not `rag-for-everyone`
or the `mcp-for-everyone` pattern this repo was originally scaffolded
from. Decision: **forward-only** — Chapters 1-6 stay as already built
(mcp-for-everyone-derived pattern, already shipped and CI-verified);
apply the richer python-for-everyone-derived per-chapter file set
starting with Chapter 7 onward. Don't retrofit 1-6 without being asked.

## Open Decisions

- **Model/SDK dependency: RESOLVED 2026-08-09, then REVERSED same
  day.** Final policy: Ollama + local open-source model, agent loop
  built from scratch — no Anthropic API dependency at all, not even a
  cheap one. See "Architecture Decisions" above for full detail. Still
  open: exact model name/version to standardize on (verify at Chapter
  7 start), and whether CI can practically run a local model at all
  (a GitHub Actions runner pulling and running an LLM may be slow or
  resource-constrained — evaluate when updating `ci.yml`; it may be
  more practical for CI to skip model-dependent checks gracefully,
  similar to how the old policy planned to skip without an API key).
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

Chapter 8 is done. Module 3's last chapter is next: Chapter 9
("Connecting Your Agent to MCP Servers," Advanced) — swap some of
Chapters 7-8's hand-rolled tools for MCP-based ones, reusing
`mcp-for-everyone`'s verified MCP client/server patterns rather than
re-discovering them (that course's `mcp[cli]` usage is already
confirmed working — see that repo's chapters for reference, structure
and verified code only, not content). Chapter 8's own "GenAI Builder
Thought Process" section already previews this: the same worst-case
questions (what does a bad call do, who scopes it) apply whether a
tool is a local Python function or lives behind an MCP server. Read
Chapters 7-8 fully first. Chapter 9 completes Module 3 and should
close its arc similarly to how Chapter 6 closed Module 2.

Before writing any new code, check whether Ollama generation is
actually working (not just `/api/tags` responding) — it hung across
both Chapter 7 and Chapter 8's build sessions; don't assume it's
resolved without checking. Also outstanding, not blocking Chapter 9:
write the Module 1 and Module 2 written exams
(assessments/written-exams/), re-run Chapter 7's `project/starter.py`/
`solution.py` live once Ollama is reliably reachable, and consider
extending `scripts/local_check.sh`/`ci.yml` to run `practice/solution.py`
files too (flagged in both Chapter 7 and 8's audits, not yet done).
