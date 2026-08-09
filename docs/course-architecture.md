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

**Revised 2026-08-09** (was: Claude Agent SDK + Anthropic API). The
user rejected any Anthropic-API-dependent design, including the
Haiku-only low-cost mitigation — the requirement is genuinely free
(open-source) or genuinely low-price, and the resolved choice is
**fully local, open-source**: no API key, no account, no per-run cost
for any learner, ever.

This course builds the "build your own agent" chapters' agent loop
**from scratch** using the **`openai` Python package** (`pip install
openai`) as the HTTP client, pointed at **Ollama**'s local
OpenAI-compatible endpoint (`base_url="http://localhost:11434/v1"`,
`api_key="ollama"` — a required-but-unchecked placeholder) rather than
at `api.openai.com`. Confirmed via research 2026-08-09: Ollama serves
a genuine `/v1/chat/completions` route with tool-calling support
(`chat.completions.create(model=..., messages=..., tools=[...])`,
tool calls returned on `message.tool_calls`, results sent back as
`role: "tool"` messages) for tool-calling-capable models. There is
deliberately no third-party agent-framework SDK layered on top: the
loop is written directly against Chapter 4's plan/act/observe/repeat
mechanism and the provider's raw tool-calling API, so the mechanism
stays visible rather than hidden behind framework abstraction — this
is also a better teaching fit than adopting a framework like LangGraph
would have been.

**Why the `openai` package specifically, not Ollama's own Python
client**: per the 2026-08-09 clarification, this course stays
open-source/low-price by default, but must give learners an explicit,
documented option to point the same code at a hosted provider if they
prefer speed/quality over local hardware cost. Confirmed via research
2026-08-09: Anthropic (since March 2026) and Google Gemini both expose
their own OpenAI-compatible `/v1/chat/completions`-style endpoints
(Anthropic's documented as a testing/evaluation layer, not their
recommended production path — see `platform.claude.com/docs/api/
openai-sdk`). Because Ollama, OpenAI, Anthropic, and Gemini all speak
the same `openai` client shape, the agent code in Chapter 7 needs
exactly one `base_url`/`api_key`/`model` change to point at any of
them — no rewrite. Chapter 7 must include an explicit, clearly-marked
"use a hosted API instead" section showing that swap for all three
alternatives, verified against each provider's current documentation
before being written into the lesson (don't assume the March 2026
Anthropic compatibility layer's exact shape is still accurate by the
time this is written — re-check).

**Model choice**: recommend a tool-calling-capable open-weight model —
current candidates are Qwen2.5-coder (coding-tuned) or Llama 3.1 —
verify against Ollama's current model library and confirm tool-calling
support before writing Chapter 7's code (do not assume prior knowledge
is current; the reference-chapter research discipline applies here
just as much as it did to the original SDK research). State the
hardware expectation (approximate RAM, disk space for the model
weights) explicitly in the lesson text, the same way the old policy
required stating API cost explicitly — this course's no-hype standard
applies to hardware cost the same way it applied to dollar cost.

Claude Code / Cursor / GitHub Copilot are still covered at a
conceptual, tool-agnostic level for the "use agents well" chapters
(Module 1) — specific UI details of commercial tools change too fast
to teach as exact steps; teach the underlying practice (scoping,
reviewing, iterating) that survives tool churn. This part of the
policy is unchanged — Module 1 never depended on the Anthropic API and
required no rework.

## Conversational Clarity Standard

Same as `mcp-for-everyone`: explain like a helpful expert beside the
learner, story-first, senior-level trade-offs unpacked patiently.

## Builder Thought-Process Layer

Every chapter includes a visible reasoning section (problem framing,
options considered, chosen approach, validation, observed failure,
decision) — same pattern as `mcp-for-everyone`, adapted to
coding-agent-building decisions (which tool to give an agent, how to
scope its permissions, how to structure its loop).
