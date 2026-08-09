# AI Coding Agents for Everyone

Free, interactive course on using and building AI coding agents:
prompting and reviewing agent-generated code like a senior engineer,
understanding the agentic loop, building a real agent with the Claude
Agent SDK, and connecting it to tools via MCP.

🔗 **Repo:** <https://github.com/TechNaom/ai-coding-agents-for-everyone>
🔗 **Live UI:** <https://technaom.github.io/ai-coding-agents-for-everyone/>
*(GitHub Pages not yet enabled — no root `index.html` yet)*

This course follows the same philosophy as `mcp-for-everyone`:

- Plain-language first, without hiding the real engineering.
- One chapter at a time, validated before scaling.
- No signup required to *read* the course. **Exception**: chapters that
  actually run the Claude Agent SDK need a real `ANTHROPIC_API_KEY` —
  unlike `mcp-for-everyone`, this course cannot be fully hands-on for
  free. This is called out explicitly wherever it applies, per this
  course's no-hype standard.
- Browser-first learning pages.
- Hands-on code and projects, tested against the real SDK before being
  written into a lesson.
- Interview-ready explanations.
- Strong architecture and trade-off thinking.

All examples, stories, exercises, projects, and thought-process journals
in this course are original to coding-agent usage, agent construction,
and AI-assisted development practice.

## What this is

`AI Coding Agents for Everyone` teaches two things most developers
never learn explicitly: how to use a coding agent (Claude Code, Cursor,
Copilot) well — prompting, scoping, reviewing — and what's actually
happening when you build one yourself with the Claude Agent SDK,
including connecting it to real tools via MCP.

## SDK versions

This course teaches against the **Claude Agent SDK**
(`pip install claude-agent-sdk`, current as of build time) for the
build-your-own-agent chapters, and the **MCP Python SDK**
(`pip install "mcp[cli]"`) for the tool-connection chapter. Commercial
tools (Claude Code, Cursor, Copilot) are covered conceptually — their UI
details change too fast to teach as exact steps.

## Who this is for

- **Beginners** who've only used autocomplete-style suggestions.
- **Developers** who want to use coding agents effectively day to day.
- **Senior engineers** who need to review AI-generated code critically.
- **Tech leads** setting team conventions for AI-assisted development.
- **Architects** designing where agents fit in a dev workflow or CI
  pipeline.

## Learning path

See [`docs/curriculum/CURRICULUM_MAP.md`](docs/curriculum/CURRICULUM_MAP.md)
for the full module/chapter roadmap, learning outcomes, and project ladder.

## Repository structure

```text
ai-coding-agents-for-everyone/
  chapters/            per-chapter lessons, quizzes, labs, interview prep
  docs/curriculum/      curriculum map (source of truth) + styled roadmap
  docs/course-architecture.md
  templates/            reusable chapter/quiz/lab/project templates
  assessments/          quizzes, written exams, interview questions, ADR-style
                         architecture challenges
  quality-audits/       per-chapter quality gate checklists
  codebase/              starters, solutions, shared code, datasets
  assets/                shared site styling, sidebar, progress, quiz engine
  PROJECT_STATE.md       current build status (read this first)
  AI_HANDOFF.md          for any AI coding assistant picking this up cold
```

## How to start

This repo is under active construction. See `PROJECT_STATE.md` for
what's built and what's next.

## Projects

Four project levels, from guided to architecture-challenge — see the
curriculum map's Projects section.

## Capstone

Design (and partially implement) an agentic workflow — a PR review bot
or CI troubleshooting agent — for a realistic engineering org, with the
same ADR/architecture rigor as `mcp-for-everyone`'s capstone.

## Contributing

Solo-maintained; not open to external PRs. See `CONTRIBUTING.md` if
you're forking this for your own use.

## License

Code is licensed under [MIT](LICENSE). Educational content (lessons,
diagrams, exercises, interview questions) is licensed under
[CC BY 4.0](LICENSE-CONTENT).
