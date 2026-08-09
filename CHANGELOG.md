# Changelog

## 2026-08-09 — Repository scaffolded

- Discovery completed: course vision, personas, prerequisites, outcomes,
  13-chapter/7-module curriculum, project ladder, capstone.
- Curriculum map, course architecture doc, repo structure scaffolded
  from `mcp-for-everyone`'s proven pattern (structure only, no content
  reused).
- Confirmed via research: `claude-agent-sdk`
  (`pip install claude-agent-sdk`, Python 3.10+) is the current Claude
  Agent SDK package, released as recently as 2026-08-08.
- CI (`.github/workflows/ci.yml`) and `scripts/local_check.sh` adapted
  from `mcp-for-everyone` and generalized: chapter-specific
  long-running-server handling replaced with a
  `# CI: LONG_RUNNING_SERVER` / `# CI: NEEDS_LIVE_SERVER=<path>`
  marker-comment convention instead of hardcoded chapter paths.
- Identified and documented an open decision unique to this course:
  unlike `mcp-for-everyone`, hands-on chapters here require a real
  `ANTHROPIC_API_KEY` and cost real money to run — not yet resolved,
  blocks Chapter 7 (the reference chapter) until decided.
- `LICENSE` (MIT), `LICENSE-CONTENT` (CC BY 4.0), `CONTRIBUTING.md`.

No chapter content built yet.
