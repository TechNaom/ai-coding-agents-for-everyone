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
- [x] **Chapter 9 built and live — closes Module 3**: "Connecting Your
      Agent to MCP Servers." Swaps Chapter 8's hand-rolled
      `git_status`/`git_diff` for MCP-based versions without touching
      `run_agent`'s loop. `connect_git_tools()` translates MCP tool
      metadata into this course's `TOOLS` schema (stripping/re-injecting
      a harness-controlled `workspace` arg the model never sees);
      `MCPBridge` runs one persistent MCP client connection on a
      background thread's event loop so the async MCP client API can be
      called synchronously. Found and fixed a real `anyio` cancel-scope
      bug during testing. States honest trade-offs (server/connection/
      latency/failure-mode cost vs. reuse) without overselling MCP.
      Module 3's assessment (a working code review checklist, per
      CURRICULUM_MAP.md) is built into the practice bank: find the
      deliberate flaw in a tool-integration diff. Full live-tested MCP
      client-server round trip (real subprocess, real stdio transport,
      real git repo); full agent-loop generation against a live model
      not re-verified (same sandbox-wide Ollama hang as Ch7-8).
      **Module 3 (Chapters 7-9) is now fully built and live.**
- [x] **Homepage + roadmap page shipped (Step 9)**: root `index.html`
      and `docs/curriculum/index.html`, adapted from `mcp-for-everyone`'s
      proven pattern. The course had 8 live chapters with no landing
      page before this — every URL required knowing the exact chapter
      path by hand. Hero states the zero-cost/zero-API-key default
      plainly; roadmap lists all 13 chapters with live/coming-soon
      status kept in sync with `chapters-data.js` by hand.
- [x] **Module 1 and 2 written exams built**:
      `assessments/written-exams/module-1-exam.md` (11 questions: MC,
      concept, scenario/judgment, full diff-review-checklist
      application) and `module-2-exam.md` (11 questions, including a
      3-scenario failure-diagnosis exercise), matching each module's
      stated assessment type in `docs/curriculum/CURRICULUM_MAP.md`.
      Registered in `chapters-data.js`'s `examPath` fields.
- [x] **Parallelized chapter-build workflow validated**: Chapter 9's
      build and the Module 1/2 exams' build ran as two concurrent
      background agents (previously always run sequentially to avoid
      `chapters-data.js` edit conflicts). Worked cleanly because the
      exams task was instructed to touch `chapters-data.js` last,
      minimally, after re-reading current state. Worth reusing this
      pattern for future independent work (e.g. a chapter build + an
      exam/assessment build, or two chapters in different modules) to
      cut wall-clock time — each chapter build takes 10-50 minutes of
      real work (multi-file authoring, live code testing) regardless of
      parallelization, so speedup only comes from running genuinely
      independent tasks concurrently, not from rushing any single one.
- [x] **CI extended to cover `practice/solution.py`**: previously only
      `exercises/solution.py` and `project/solution.py` ran in CI —
      flagged as a gap in Chapters 7-9's audits. Minimal, surgical diff
      to `.github/workflows/ci.yml` and `scripts/local_check.sh` (one
      glob pattern added, same marker-comment handling reused). Ran as
      a second parallel background agent alongside Chapter 10's build,
      touching only CI files while Chapter 10 touched only chapter
      content — zero coordination overhead needed since the file sets
      were fully disjoint (unlike the Chapter 9 + exams pairing, which
      needed the `chapters-data.js` sequencing workaround).
- [x] **Chapter 10 built and live — closes Module 4 (the module's only
      chapter)**: "Detecting Hallucinated APIs and Logical Bugs."
      Builds on Chapter 3's checklist (questions 1 and 5, made
      mechanically specific) and Chapter 5's going-off-the-rails
      mechanism. Hook uses a real, live-verified pandas `TypeError` for
      a hallucinated `sort_values(ignore_na=True)` argument. Covers
      three causes of API hallucination (thin training data, post-
      training API drift, structural similarity to a more common
      library's chaining pattern) and four logical-bug shapes (off-by-
      one/boundary, inverted boolean logic, mutable-default-argument
      state leaks, operator precedence). Explicitly self-referential:
      cites this course's own build discipline (verify against the
      installed package before writing any example) as the same
      mechanism it teaches. Ships a substantial 3-file flawed-PR lab
      (3 hallucinated APIs, 2 logical bugs, 1 deliberately-correct line
      to test over-flagging, every flaw independently executed and
      confirmed) plus Module 4's real code-review exam
      (`assessments/written-exams/module-4-exam.md`), per
      CURRICULUM_MAP.md's stated assessment type for this module.
      **Module 4 is now fully built and live.**
- [x] **Chapter 11 built and live — starts Module 5**: "Security:
      Sandboxing, Permissions, Destructive Commands." Resolves three
      things Chapters 7-9 deliberately left open. Real three-tier
      permission-scope system (`ALLOWED`/`REQUIRES_CONFIRMATION`/
      `BLOCKED`) checked in the harness before dispatch, defaulting
      unclassified tools to `BLOCKED` (fail closed); `confirm_with_human()`
      reads real stdin and denies on `EOFError` — verified both locally
      (with stdin redirected from `/dev/null`, matching CI) and on the
      real GitHub Actions runner, where `input()` correctly hit EOF
      immediately and the script denied-and-continued rather than
      hanging. `git_commit` finally shipped with no `confirm` parameter
      at all. Honestly-scoped sandboxing: real `RLIMIT_CPU`/`RLIMIT_AS`
      kernel limits and a stripped subprocess environment, independently
      verified (a CPU-bomb actually SIGKILL'd, a 1GB allocation actually
      MemoryError'd) — explicitly NOT claimed as container/VM-grade
      isolation, and `RLIMIT_NPROC` deliberately omitted after testing
      showed it's host-account-scoped, not subprocess-scoped, so it's a
      worse mitigation than none. Four-category threat model (data
      loss, scope escape, supply-chain/credential exposure, irreversible
      external effects) plus a retrospective least-privilege audit of
      every Chapter 7-9 tool. Ships the real Module 5 lab ("add
      permission scoping to the Module 3 agent," per CURRICULUM_MAP.md).
      Fixed two consistency gaps on review: `lesson.html` was missing
      the interview-questions callout and footer GitHub link every
      prior chapter's `lesson.html` includes — worth a final visual
      pass on future chapters' lesson.html against this checklist.
      **Note for local testing**: this chapter's `project/solution.py`
      calls `input()` for a live confirmation demo — running
      `scripts/local_check.sh` from an interactive shell with open
      stdin will make it hang/appear to fail; always run with
      `< /dev/null` or in a genuinely non-interactive shell to match
      CI's actual behavior.

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

**Modules 1-4 (Chapters 1-10) are complete; Module 5's first chapter
(11) is also live.** Next: Chapter 12 ("Putting an Agent in CI,"
Advanced) — completes Module 5. This is where the module's lab ships
("wire a minimal agent into a CI check" per CURRICULUM_MAP.md) — build
on Chapter 11's exact permission-scope system (`TOOL_POLICY`,
`confirm_with_human`'s fail-closed-on-EOFError behavior is PRECISELY
what makes an agent safe to run unattended in CI, and Chapter 11's own
closing thought-process section already named this connection
explicitly). Read Chapter 11 fully first — its `project/solution.py`
is the direct foundation. Consider having Chapter 12 actually wire a
real CI check into a small demo/sample repo structure (this course
already treats its own CI as a live, tested artifact, not just
described — keep that standard). After Chapter 12, write
`assessments/written-exams/module-5-exam.md` ("production-readiness
checklist exam" per the curriculum map) — this closes Module 5.

Then Module 6: Chapter 13, the capstone (architecture challenge,
Level 4) — the final chapter of the entire course.

Continue parallelizing where genuinely independent, but Chapters 11
and 12 were correctly built sequentially since 12 depends on 11's
exact permission system — don't force parallelism where content
genuinely depends on order. The Module 5 exam (after both chapters)
could potentially run alongside early Chapter 13 planning/research if
that becomes independent enough, but check dependencies before
assuming.

Also outstanding, not blocking: re-run Chapter 7's `project/starter.py`/
`solution.py` and Chapter 9's full agent-loop-against-a-live-model path
once Ollama is reliably reachable (both disclosed as not-live-verified
due to a persistent sandbox-wide generation hang across five build
sessions now — check `ollama ps` / try a plain completion before
assuming it's resolved, every time). Also: when running
`scripts/local_check.sh` locally on Chapter 11 or later, always use
`< /dev/null` (or a genuinely non-interactive shell) — a chapter whose
code calls `input()` for a live confirmation demo will hang/appear to
fail if your shell's stdin stays open, which does not reflect real CI
behavior (CI's stdin is already closed, confirmed via the real GitHub
Actions log for Chapter 11's commit).
