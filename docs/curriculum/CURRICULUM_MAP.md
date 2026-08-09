# AI Coding Agents for Everyone — Curriculum Map

LAST_REVIEWED: 2026-08-09

## Course Size

Focused emerging topic: 13 chapters, 4 projects (L1–L4), 1 capstone —
same sizing model as `mcp-for-everyone`.

## Personas

- **Beginner** — has only used autocomplete-style suggestions.
- **Developer** — wants to use Claude Code/Cursor/Copilot effectively
  day to day.
- **Senior engineer** — needs to review AI-generated code critically and
  know when not to trust it.
- **Tech lead** — sets team conventions for AI-assisted development.
- **Architect** — designs where custom coding agents fit in a workflow
  or CI pipeline.

## Prerequisites

- Comfortable with Python and git (`python-for-everyone` level).
- Soft prerequisite: `mcp-for-everyone` Chapters 1–8, if building a
  custom agent's tool layer via MCP — this course links back rather
  than re-teaching MCP fundamentals.

## Learning Outcomes

1. Use a coding agent effectively — prompt it, scope its task, review
   its diff like a senior engineer would.
2. Explain the agentic loop (plan → act → observe → repeat) and
   diagnose why an agent loops, stalls, or goes off the rails.
3. Build a minimal coding agent using the Claude Agent SDK with real
   tools (file read/write, shell, git).
4. Connect an agent to MCP servers instead of hand-rolled tools.
5. Detect hallucinated APIs and logical bugs in AI-generated code.
6. Secure an agent operating on a live codebase (destructive commands,
   secret exposure, dependency supply-chain risk).
7. Architect where agents fit in a real dev workflow (PR review bots,
   CI troubleshooting agents).

## Module Architecture

### Module 1 — Using Coding Agents Well
**Purpose:** the daily-practice layer before any internals.
**Outcomes:** prompt and scope tasks effectively; review a diff like a
senior engineer.
**Chapters:** 1, 2, 3
**Labs:** ship a real small feature with Claude Code/Cursor, with a
written review log
**Assessment:** concept + judgment quiz

### Module 2 — How Coding Agents Actually Work
**Purpose:** open the hood on the agentic loop.
**Prerequisites:** Module 1
**Outcomes:** explain plan/act/observe/repeat; diagnose common failure
modes; reason about context-window limits on codebase understanding.
**Chapters:** 4, 5, 6
**Labs:** trace a real agent transcript and annotate each loop step
**Assessment:** concept quiz + failure-diagnosis exercise

### Module 3 — Building a Coding Agent
**Purpose:** hands-on construction with the Claude Agent SDK.
**Prerequisites:** Module 2
**Outcomes:** a working minimal agent with real tools, tested.
**Chapters:** 7, 8, 9
**Labs:** minimal agent; add file/shell/git tools; swap in MCP-based
tools instead of hand-rolled ones
**Assessment:** working code review checklist

### Module 4 — Reviewing AI-Generated Code Critically
**Purpose:** the human half of "AI proposes, human reviews."
**Prerequisites:** Module 3
**Outcomes:** detect hallucinated APIs and logical bugs; build a habit
of validating before trusting.
**Chapters:** 10
**Labs:** a deliberately-flawed AI-generated PR to review and fix
**Assessment:** code-review exam

### Module 5 — Production & Safety
**Purpose:** what changes when an agent operates on a live codebase and
in CI.
**Prerequisites:** Module 4
**Outcomes:** sandbox and scope an agent's permissions; integrate an
agent into a CI workflow safely.
**Chapters:** 11, 12
**Labs:** add permission scoping to the Module 3 agent; wire a minimal
agent into a CI check
**Assessment:** production-readiness checklist exam

### Module 6 — Capstone
**Purpose:** architect-level synthesis.
**Prerequisites:** Module 5
**Outcomes:** design (and partially implement) an agentic workflow for
a realistic engineering org.
**Chapters:** 13
**Assessment:** capstone rubric (architecture challenge, Level 4)

## Chapter Roadmap

| # | Chapter | Module | Difficulty |
|---|---------|--------|------------|
| 1 | Why Coding Agents Aren't Just Autocomplete | 1 | Beginner |
| 2 | Prompting and Scoping Tasks for an Agent | 1 | Beginner |
| 3 | Reading and Reviewing an Agent's Diff Like a Senior Engineer | 1 | Intermediate |
| 4 | The Agentic Loop: Plan, Act, Observe, Repeat | 2 | Intermediate |
| 5 | Why Agents Loop, Stall, or Go Off the Rails | 2 | Intermediate |
| 6 | Context Windows and Codebase-Scale Understanding | 2 | Intermediate |
| 7 | Build: A Minimal Coding Agent — **reference chapter** | 3 | Intermediate |
| 8 | Giving Your Agent File/Shell/Git Tools | 3 | Advanced |
| 9 | Connecting Your Agent to MCP Servers | 3 | Advanced |
| 10 | Detecting Hallucinated APIs and Logical Bugs | 4 | Advanced |
| 11 | Security: Sandboxing, Permissions, Destructive Commands | 5 | Advanced |
| 12 | Putting an Agent in CI | 5 | Advanced |
| 13 | Capstone: Design an Agent Workflow for a Real Team | 6 | Architect |

## Projects

- **L1 Guided** — Ship a real small feature using Claude Code/Cursor,
  with a written review log (ships after Ch. 3).
- **L2 Assisted** — Extend a provided minimal agent with one new tool,
  partial scaffold (ships after Ch. 8).
- **L3 Independent** — Build a coding agent from scratch with MCP-based
  tools, no scaffold (ships after Ch. 9).
- **L4 Architecture Challenge** — Design an agentic CI workflow (PR
  review bot or CI troubleshooting agent) for a regulated engineering
  org; business problem only (this is the capstone, Ch. 13).

## Cross-Course Links

- Builds on: `mcp-for-everyone` (tool-access layer for a custom agent),
  `python-for-everyone` (baseline)
- Deepens (does not duplicate): `genai-for-everyone` session 4 (general
  agent/tool-calling concepts) — link back for fundamentals
- Feeds: future `AI Engineering for Everyone`, `AI Security for
  Everyone` (agent-specific security deepens Module 5 here)
