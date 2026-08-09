# Chapter Quality Audit: Connecting Your Agent to MCP Servers

## Summary

- Chapter: 9 — Connecting Your Agent to MCP Servers (Module 3, Advanced, **closes Module 3**)
- Reviewer: AI build agent (self-audit at time of authoring)
- Date: 2026-08-09
- Status: Ready for human review

## Starting state: a partial prior attempt was found and verified, not discarded

Per this session's task briefing, `chapters/chapter-09-connecting-your-agent-to-mcp-servers/`
was checked before writing anything new. Two files already existed
from an earlier session that had hit an infrastructure/API-access
error partway through: `project/mcp_git_server.py` (the standalone MCP
git server) and `project/solution.py` (the worked agent). Both were
read in full and independently re-verified against the actually-
installed `mcp` package this session (see below) rather than assumed
correct. Every technical claim in both files checked out — the same
discipline this course has followed since Chapter 7. One accuracy
improvement was made to `project/solution.py`'s docstring: the
original text attributed the entire MCP integration pattern to
`mcp-for-everyone` Chapters 7-8, which is accurate for the
`Client`/`list_tools()`/`call_tool()` shape but not for the
subprocess/stdio transport wiring (`StdioServerParameters`,
`stdio_client`) — those two `mcp-for-everyone` chapters connect to
their server **in-process** (`Client(mod.mcp)`), not over stdio to a
separate process. The docstring now states this distinction explicitly
and correctly attributes the stdio-transport piece to independent
verification against the installed `mcp` package, not to
`mcp-for-everyone`. `project/starter.py` (the partial scaffold with
`connect_git_tools()` left as a `TODO`), `project/README.md`,
`project/index.html`, and every other file in this chapter (lesson,
quiz, interview questions, exercises, practice) were written fresh
this session.

## What was actually verified live this session

Before writing or trusting any MCP-related code, this session installed
the actual `mcp` package (`pip install "mcp[cli]" openai` in a fresh
venv, since this sandbox's system Python is externally-managed) and
checked every API claim the existing files made, directly:

- `pip show mcp` reports version **2.0.0**.
- `import mcp; dir(mcp)` confirms `Client`, `StdioServerParameters`,
  `stdio_client`, and `Tool` are all real, top-level exports of the
  installed package.
- `import mcp.server.fastmcp` — **raises `ModuleNotFoundError`**,
  confirming the prior session's claim that this import path does not
  exist in this installed version.
- `import mcp.server.mcpserver` — succeeds, and
  `mcp.server.mcpserver.MCPServer` exists with a `tool()` decorator
  method and a `run(transport=...)` method matching the exact calls
  `mcp_git_server.py` makes, confirmed via `inspect.signature()` on
  both.
- `Tool.model_fields` confirms `input_schema` (not `inputSchema` or
  any other name) is the real field name — matching what
  `connect_git_tools()` reads.
- `Client.__init__`'s real signature, and `Client.list_tools()`/
  `Client.call_tool()`'s real signatures, were inspected directly and
  match what `MCPBridge` calls.

With the package genuinely installed, this session then ran the **full
MCP client-server round trip**, live, bypassing the model entirely
(the model layer is exactly what the sandbox's Ollama generation hang
makes impossible to test — see below):

- `solution.py`'s `connect_git_tools()`, called directly: started
  `mcp_git_server.py` as a real subprocess over the real stdio
  transport, called its real `list_tools()`, and got back exactly 2
  tools (`git_diff`, `git_status`) — printed and confirmed.
- `TOOLS` after connecting: confirmed all 6 expected entries present
  (`read_file`, `write_file`, `edit_file`, `run_shell_command`,
  `git_status`, `git_diff`), with the MCP-sourced two built from the
  server's own schema, not hand-typed.
- `dispatch_tool_call`, called with a fake `tool_call`-shaped object
  (matching the real `openai` client's `tc.function.name`/
  `tc.function.arguments` shape) for `git_status` against a real git
  repository (a real `git init`, a real untracked file) — got back the
  real `git status --porcelain` output (`'?? notes.txt\n'`), sourced
  from a genuinely separate process, over MCP, with zero model
  involvement.
- The same for `git_diff` (correctly reported `(no changes)` for an
  untracked-only repo state), `read_file` (a local tool, confirming
  local and MCP tools both dispatch correctly through the same
  function), and an unknown tool name (correctly returned
  `"error: unknown tool: ..."`).
- `MCPBridge.close()` — confirmed it shuts down cleanly with no
  exception and no orphaned subprocess.
- `project/starter.py`'s `connect_git_tools()` — confirmed it raises
  `NotImplementedError` with a clear message (both under plain
  `python3` with no `mcp`/`openai` installed, and under the venv with
  both installed), and that `main()` catches it and exits 0 with a
  clear instruction, rather than an ugly traceback.
- **Graceful degradation**, both `project/starter.py` and
  `project/solution.py`, run under plain `python3` (no `openai`
  installed in that interpreter): both printed `"The openai package
  isn't installed. Run: pip install openai"` and exited 0 — matching
  Chapters 7-8's required CI-safety behavior exactly.

## `mcp-for-everyone` citation, independently re-verified

The task instructed this chapter to reuse `mcp-for-everyone`'s
verified Python MCP client pattern rather than re-deriving it, citing
which chapter it came from. This session grepped `mcp-for-everyone`'s
`chapters/` directory for its Python MCP client code and confirmed:

- `chapters/chapter-07-building-an-mcp-client-host/project/solution.py`
  and `chapters/chapter-08-connecting-multiple-servers/project/solution.py`
  both use `from mcp import Client`, `async with Client(...) as client`,
  `await client.list_tools()` (reading `result.tools`), and
  `await client.call_tool(name, args)` (reading `result.is_error`,
  `result.content[0].text`, `result.structured_content`) — the exact
  shape `MCPBridge` reuses.
- Both of those reference solutions connect **in-process**
  (`Client(mod.mcp)`), not over a subprocess/stdio transport. This
  chapter's server is a genuinely separate process, so
  `StdioServerParameters`/`stdio_client` were required in addition —
  verified independently against the installed package (above), not
  sourced from `mcp-for-everyone`. `project/solution.py`'s docstring
  states this distinction explicitly, corrected during this session
  (see above).

## What was tested without live model access

All of the following was actually executed this session, not asserted:

- **`exercises/solution.py`** — `strip_injected_args`,
  `classify_tool_call`, and `mcp_result_to_text` fully implemented and
  tested against 11 hardcoded checks (schema stripping with and
  without a `required` key present, non-mutation of the input schema,
  local/MCP/unknown tool-name classification, and all three
  `mcp_result_to_text` branches — success, error-with-content, and the
  empty-content/`structured_content`-fallback case). `python3
  solution.py` prints `11/11 checks passed.` and exits 0.
  `exercises/starter.py` correctly raises `NotImplementedError` on the
  first call until filled in (verified — the traceback shows the exact
  expected line and message).
- **`practice/starter.py`/`solution.py`** — the four-diff
  find-the-flaw script, run live: produces all four diffs and their
  answer keys correctly, confirmed by reading the full printed output.
- **All 7 `.py` files in this chapter** compile cleanly under `python3
  -m py_compile` (`project/starter.py`, `project/solution.py`,
  `project/mcp_git_server.py`, `exercises/starter.py`,
  `exercises/solution.py`, `practice/starter.py`, `practice/solution.py`).
- **`bash scripts/local_check.sh`**, run from the repo root after
  adding all new files — all 6 checks passed: required folders,
  placeholder-text scan, Python syntax, `exercises/solution.py` +
  `project/solution.py` execution, JS syntax + chapter-path validation,
  secret scan.
- **Internal link scan**: a Python script scanning every `href`/`src`
  attribute in this chapter's `.html` files and every Markdown link in
  its `.md` files, resolving each relative to its source file. 67
  internal links checked, zero broken.
- **`assets/chapters-data.js`**: re-read first to confirm the Module
  1/2 `examPath` edits from a separately-run parallel task were already
  present, then only `chapter-09`'s `path` field was added. Verified
  with `grep -n "examPath"` afterward that both prior `examPath`
  entries (`module-1-exam.md`, `module-2-exam.md`) and Module 3's own
  `examPath: null` are all still exactly as they were before this
  session's edit — nothing else in the file was touched.

## What was NOT verified live, stated honestly

- **The full agent loop, end to end, against a real model**, calling
  MCP-sourced `git_status`/`git_diff` tools as part of a genuine
  model-driven run. Before writing any code, this session re-confirmed
  the same sandbox-wide issue disclosed in Chapters 7 and 8's own
  audits: `curl http://localhost:11434/api/tags` responds normally
  (confirming `llama3.2:latest` is pulled and the server is up), but
  `curl http://localhost:11434/v1/chat/completions` with a real
  request **timed out (exit code 124) after 12 seconds** — generation
  itself is not completing, the same hang both prior chapters hit.
  This is not a bug in this chapter's code; every piece of the MCP
  integration that doesn't require live generation was independently,
  genuinely verified live (see above) — the loop/dispatch code around
  it is Chapter 8's own, already-live-verified code, unmodified except
  for the one new MCP-routing branch, which was tested directly
  against the real MCP round trip.
- Whether a real model, given only the MCP-sourced (not hand-typed)
  `git_status`/`git_diff` schemas, reliably chooses to call them at the
  right moment — this is exactly the kind of thing the lesson's
  "what changes and what doesn't" section is careful not to overclaim;
  no transcript of a live model choosing an MCP tool is shown, because
  none was observed this session.
- The exact hardware/model recommendation (`llama3.2`) was not
  re-benchmarked — carried forward unchanged from Chapter 7's own
  confirmed recommendation, since this chapter doesn't change the model.

## Scores

| Dimension | Score | Notes |
|---|---:|---|
| Conversational clarity | Pass | Hook opens with the exact same tool call shown dispatched two different ways (local function vs. MCP round trip), making the chapter's central claim concrete before any abstraction. |
| Production depth | Pass | Real, tested `MCPBridge` (with a documented, genuinely-hit `anyio` cancel-scope bug and its fix), real schema-translation logic, real dispatch-routing extension — all independently verified against the installed `mcp` package and a real subprocess round trip, not just described. |
| Real-time adoption usefulness | Pass | Every code block in the lesson matches the actual, tested code in `project/solution.py`; the MCP round trip (server discovery, tool call, result unpacking) was independently confirmed callable and correct without needing a live model. |
| Architecture and diagrams | Pass | Code-window blocks for the schema mismatch, the sync/async bridge, the schema-translation function, and the one-line dispatch extension, each isolated and explained. |
| Exercises | Pass | 6 tasks in `exercises/index.html`, 3 production-gear (tasks 4-6: tracing a schema missing expected keys, reasoning through a tool-name collision, and reviewing a flawed `connect_git_tools()` diff against Chapter 3's checklist). Tasks 1-3 map to real, live-tested TODOs (11/11 passing). |
| Practice bank | Pass | 7 scenario cards in `practice/index.html` (exceeds the 6 minimum) plus a runnable, live-tested four-diff find-the-flaw script directly built around Module 3's actual assessment (a working code review checklist per the curriculum map), not a generic scenario bank. |
| Interview preparation | Pass | 8 questions in `interview-questions.html`, 2 each at beginner/intermediate/senior/architect, each with strong answer/red flag/follow-up/what this proves; exact plain-markdown mirror in `interview-questions.md`. |
| Project implementation | Pass (with the live-loop disclosure above) | This is the real Module 3 L3 (Independent) project per the curriculum map, not a preview page. `project/starter.py` leaves the entire MCP integration (`connect_git_tools()`) unimplemented — no partial-blank scaffold, matching "no scaffold" for the specific skill being tested — while still providing Chapter 8's already-tested tool layer as given infrastructure. `project/solution.py` is a fully worked, independently live-verified example. `project/README.md` gives concrete, live-model-independent verification steps as well as full end-to-end instructions. |
| GenAI thought-process layer | Pass | "GenAI Builder Thought Process" section: problem (treating MCP as inherently safer/better rather than a location/reuse mechanism), assumption, what actually distinguishes it (the same worst-case-bad-call question from Chapter 8, now applied to a tool's origin), why it matters closing Module 3, working definition. |
| Navigation/template consistency | Pass | lesson -> quiz -> exercises -> practice -> interview-questions -> project chain matches Chapters 1-8's link order; uses the same richer python-for-everyone-derived file pattern (README.md x3, `interview-questions.md`). No `ai-paired.html` — matching Chapter 8's own choice not to duplicate that page a second time in the same module, since Chapter 7 already ships it and this chapter's own project already delivers a distinct "produce something, then critique it" arc via the exercises' diff-review tasks. |
| Accessibility/readability | Pass | Uses existing style.css classes only (hook, what-is, code-window, thinking-box, points-to-remember, lesson-card, task-card, scenario-card, page-toc, badge-difficulty, chapter-badge); no invented CSS. |
| Public artifact readiness | Pass | No placeholder text (confirmed via `local_check.sh`'s placeholder-text scan, plus a manual read-through). All content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure only, not content), or any other TechNaom repo; only verified technical patterns (API calls, package names) were reused, explicitly cited as such per the task's constraint. |

## Required Checks

- [x] Lesson starts with a problem, not jargon — opens with the exact same tool call dispatched two different ways, making "same behavior, different mechanism" concrete before any protocol explanation.
- [x] Lesson includes core concepts (what MCP actually is, briefly, with an explicit link to `mcp-for-everyone` rather than re-teaching), internal mechanics (the schema-shape mismatch and sync/async mismatch, both solved explicitly), a worked example (the assembled `connect_git_tools()`/`dispatch_tool_call` extension), a production scenario (the three-question test for when MCP is worth it, covered in interview Q7), trade-offs (a full honest-cost `what-is` box, not overselling MCP), a security-adjacent preview (the `workspace` injection boundary, tied back to Chapter 7's `_safe_path`), an honest common-mistake/failure section (the `MCPBridge` cancel-scope bug and its real fix), a thinking journal, and a summary/cheat-sheet.
- [x] Exercises include at least 6 tasks (6), with at least 3 production-gear tasks (3: tasks 4, 5, 6).
- [x] Practice bank includes at least 6 realistic scenarios (7, plus the runnable four-diff script).
- [x] Interview bank includes at least 8 questions (8) spanning beginner/intermediate/senior/architect (2 each), each with strong answer, red flag, follow-up, and what this proves — plus an exact `.md` mirror.
- [x] Project includes a meaningful implementation artifact, verified runnable and correct where a live model was not required (the entire MCP round trip independently live-tested end to end, bypassing only the model layer that the sandbox's generation hang makes impossible to test), with the full agent-loop-against-a-live-model gap **explicitly disclosed above**, not silently assumed passing. This is the real, graded Level 3 (Independent) project per `docs/curriculum/CURRICULUM_MAP.md`, not a preview page.
- [x] Chapter includes diagrams/visual-text architecture aids (multiple code-window blocks, including the abbreviated `MCPBridge` shape and the schema-translation function).
- [x] Chapter includes a thinking journal (GenAI Builder Thought Process section, visible reasoning not hidden chain-of-thought).
- [x] Navigation follows lesson -> quiz -> exercises -> practice -> interview -> project, plus the required files (README.md x3, `interview-questions.md`) present and internally linked correctly.
- [x] Content is original — no wording, examples, or structure reused from `mcp-for-everyone`, `python-for-everyone` (structure reference only), or any other TechNaom repo. Chapters 7 and 8 were read in full before writing, per the task's explicit instruction, and this chapter's code deliberately extends Chapter 8's exact loop/dispatch pattern rather than redesigning it. `mcp-for-everyone`'s Chapters 7-8 Python MCP client pattern was reused as explicitly-cited verified technical knowledge (API calls, package shape), not lesson content, story, or examples — matching the task's constraint exactly.
- [x] Every new piece of the MCP integration was executed directly against real inputs this session — a real subprocess, a real stdio MCP connection, a real git repository, and a real dispatch call — the one explicitly disclosed gap is the full agent loop against a live model, blocked by the same sandbox-wide Ollama generation hang Chapters 7 and 8 already disclosed, re-confirmed (not assumed) at the start of this session.
- [x] `assets/chapters-data.js` updated: `chapter-09` entry now has `path: "chapters/chapter-09-connecting-your-agent-to-mcp-servers/lesson.html"`. Re-read first to confirm the Module 1/2 `examPath` edits from a parallel task were present; only the `chapter-09` `path` field was added, everything else (including Module 3's own `examPath: null`) left untouched, confirmed via `grep` after the edit.
- [x] Every internal link within this chapter's own pages verified programmatically (a Python link-scanner over every `.html`/`.md` file's `href`/`src`/Markdown-link targets). 67 links checked, zero broken.
- [x] `bash scripts/local_check.sh` run from the repo root after adding all new files — all 6 checks passed. No new failures.
- [x] `python3 -m py_compile` run on all 7 `.py` files in this chapter — all compile cleanly. `exercises/solution.py` and `practice/starter.py`/`solution.py` were additionally run to completion (exit 0, correct output). `project/starter.py` and `project/solution.py` were run under plain `python3` (no `openai` installed) to confirm the graceful-degradation message and exit-0 behavior, and the entire MCP round trip inside `project/solution.py` was independently executed and confirmed correct against a real subprocess and a real git repository (see above).

## Environment note: the generation hang, re-confirmed

Before writing any code, this session ran:

```
curl -s http://localhost:11434/api/tags                        # responded normally
curl -s http://localhost:11434/v1/chat/completions -d '{...}'  # timed out, exit 124, 12s
```

This matches Chapters 7 and 8's own build sessions exactly (`/api/tags`
healthy, actual generation hanging indefinitely) and the task
briefing's explicit warning that this is a persistent, sandbox-wide
issue. Per the task's instructions, this session did not retry the
hang repeatedly, and instead focused live-testing effort on the one
thing that genuinely was testable without a model: the complete MCP
client-server integration, which this session tested more thoroughly
live than either Chapter 7 or 8's own tool layers were able to be
tested (a full round trip through a real separate process over a real
protocol, not just direct Python function calls).

## Follow-Up Tasks

- Re-run `project/starter.py` (after a learner implements
  `connect_git_tools()`) and `project/solution.py` against a live
  Ollama server once one is reliably reachable, to observe a real
  end-to-end transcript of the model choosing to call MCP-sourced
  `git_status`/`git_diff` tools — closing the one explicitly-flagged
  gap in this audit and Chapters 7-8's own carried-forward gap.
- Chapter 7's own audit flagged that `scripts/local_check.sh`/`ci.yml`
  don't run `practice/solution.py` files — still true, still not fixed
  here per the standing instruction not to modify CI/`local_check.sh`
  without being asked. This chapter's `practice/starter.py`/
  `solution.py` were manually verified separately, same as Chapters 7
  and 8's were.
- Modules 1 and 2's written exams (`assessments/written-exams/`) were
  completed by a separate parallel task per this session's briefing —
  not built or touched by this session. Module 3's own `examPath` is
  deliberately left `null`: per the curriculum map, Module 3's
  assessment is the working code review checklist this chapter's
  practice bank builds toward, not a written exam file.
