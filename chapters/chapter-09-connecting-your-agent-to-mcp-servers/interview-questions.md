# Chapter 9 Interview Questions: Connecting Your Agent to MCP Servers

These mirror `interview-questions.html` exactly. Grouped by level. Each
includes a strong answer, a red flag, and a natural follow-up an
interviewer might ask next.

---

### 1. (Beginner) What actually changes about `git_status` when it moves from a Chapter 8 local function to a Chapter 9 MCP-based tool -- its behavior, or something else?

**Strong answer:** Its behavior doesn't change at all -- same command
(`git status --porcelain`), same output, same result a model calling
it would observe. What changes is location and reuse: it's no longer a
Python function living only inside this course's own agent file, it's
implemented once in a separate, standalone server process
(`mcp_git_server.py`) that any MCP-speaking client could connect to
and call, not just this one agent.

**Red flags:** Says MCP tools are "smarter" or "more powerful" than
local functions, or can't articulate that the actual git command being
run is identical either way.

**Follow-up:** "If you diffed the two git_status implementations
(Chapter 8's local function vs. this chapter's MCP tool), what would
actually be different?"

---

### 2. (Beginner) Why does this chapter link back to `mcp-for-everyone` for MCP fundamentals instead of explaining what a resource, a transport, or a tool schema are from scratch?

**Strong answer:** Because this course's own architecture rule is
"deepens, does not duplicate" -- `mcp-for-everyone` already spends
eight full chapters on MCP itself, and re-explaining protocol basics
here would be redundant content that adds no value over pointing
directly at material that already covers it well. This chapter's job
is narrower and more specific: given that you already understand MCP,
how do you actually wire it into an agent built the way this course
built one.

**Red flags:** Thinks re-explaining a prerequisite from scratch is
always more helpful, without recognizing the redundancy cost across a
whole course ecosystem, or can't name what this chapter assumes the
reader already knows.

**Follow-up:** "What's the risk of a course NOT stating its
prerequisites clearly, the way this chapter does?"

---

### 3. (Intermediate) The `openai` client's tool-calling shape and MCP's own client API are structurally different. Name the two specific mismatches this chapter had to bridge, and how each was solved.

**Strong answer:** First, a schema-shape mismatch: `TOOLS` needs
`{"type": "function", "function": {"name", "description",
"parameters"}}` entries, while MCP's `list_tools()` returns its own
`Tool` objects with `name`/`description`/`input_schema` -- solved by
`connect_git_tools()` converting one into the other at startup, not by
changing either shape to match the other. Second, a sync/async
mismatch: this course's loop (`run_agent`) is plain synchronous code,
unchanged since Chapter 7, while MCP's client API
(`list_tools()`/`call_tool()`) is entirely `async` -- solved by
`MCPBridge`, which keeps one persistent connection alive on a
background thread's own event loop and exposes plain blocking methods,
so `dispatch_tool_call` never needs an `await`.

**Red flags:** Only names one of the two mismatches, or conflates them
as a single problem, or thinks the loop itself had to become `async`
to support MCP tools.

**Follow-up:** "Why keep the loop synchronous at all -- why not just
make `run_agent` `async def` and simplify the bridge away?"

---

### 4. (Intermediate) `connect_git_tools()` strips the `workspace` argument out of the schema shown to the model, and `dispatch_tool_call` injects it back in right before the MCP call. Why not just let the model supply `workspace` itself?

**Strong answer:** The model has no reliable way to know this agent's
own absolute workspace path, and shouldn't need to -- asking it to
supply a value it can only guess at invites exactly the kind of
subtly-wrong tool call Chapter 7 warned about, for no benefit, since
the harness already knows the correct value with certainty. This is
the same what-the-model-controls-vs-what-the-harness-enforces boundary
Chapter 7's `_safe_path()` established for file paths: `workspace`
is a harness-owned fact about this specific agent's environment, not
something the model's own judgment should be involved in at all.

**Red flags:** Suggests just prompting the model harder to always get
`workspace` right, without recognizing this is a harness-vs-model
control question, not a prompting question.

**Follow-up:** "What would happen if a small model occasionally
supplied a wrong or relative `workspace` value instead?"

---

### 5. (Senior) MCPBridge's docstring describes a real bug an earlier version hit: an "Attempted to exit cancel scope in a different task" error from `anyio`. Walk through why that happened and why the fix (one coroutine, a thread-safe queue) actually resolves it.

**Strong answer:** The earlier version scheduled the MCP client's
connect (`__aenter__`) and disconnect (`__aexit__`) as two separately
`run_coroutine_threadsafe`-scheduled calls on the same event loop.
`anyio`'s task groups (which MCP's stdio transport uses internally)
tie a cancel scope to the specific async task that opened it -- and
two separately-scheduled coroutines still count as two distinct tasks
even though they share one event loop, so the scope opened in the
"enter" task couldn't be legally closed from the "exit" task. The fix
keeps the client's entire connected lifetime -- open, serve requests,
close -- inside a single coroutine (`_worker`), so there's only ever
one task involved; the background thread never re-enters the context
manager directly, it only ever pushes requests onto a queue that
`_worker` reads from inside that same coroutine.

**Red flags:** Describes the fix mechanically ("use a queue instead")
without explaining why the original approach actually broke -- the
task-identity detail specifically -- or thinks the bug was about
threading in general rather than cancel-scope task identity
specifically.

**Follow-up:** "Would this bug have shown up if the MCP client used a
transport that didn't rely on anyio task groups internally?"

---

### 6. (Senior) A teammate proposes moving `run_shell_command` behind an MCP server too, "for consistency with git_status and git_diff." What's your assessment?

**Strong answer:** Consistency alone isn't a reason -- the actual
criteria this chapter used were generic, reusable, and
low-blast-radius, and `run_shell_command` fails the first two by
design: its entire point is running whatever arbitrary command string
the model composes for a specific task, which has no fixed behavior a
shared server could meaningfully standardize the way a fixed `git
status --porcelain` call can. Moving it behind MCP wouldn't make it
safer, either -- it would add a process boundary and a connection to
manage around the exact same unscoped risk Chapter 8's denylist
already named honestly. If anything, it adds a new failure mode
(server unreachable, connection dropped) without reducing the
original one (a destructive command the denylist didn't anticipate).

**Red flags:** Agrees on "consistency" grounds without evaluating
`run_shell_command`'s specific properties against the actual MCP
trade-off criteria, or claims MCP would make it safer without
explaining a specific mechanism for how.

**Follow-up:** "Is there ANY version of a shell-command tool that
would be a good MCP candidate? What would have to be different about
it?"

---

### 7. (Architect) You're deciding whether a new internal tool your team is building should be a local function or an MCP server. Walk through the actual decision process, using this chapter's criteria.

**Strong answer:** Start with three questions, in this order. First:
is this tool tightly coupled to one specific agent's own state or
boundary (like `_safe_path()`/`WORKSPACE`) -- if yes, hand-rolled,
because an MCP server would either have to duplicate that boundary
logic itself or, worse, not enforce it at all. Second: does the tool
have a fixed, standardizable behavior, or does its whole point involve
arbitrary caller-composed input with no fixed shape to standardize (like
`run_shell_command`) -- arbitrary-input tools are poor MCP candidates
regardless of how "useful" wrapping them sounds. Third, if it passes
both: is it actually going to be reused by more than one agent or
project, and is its blast radius low enough that a connection failure
or a compromised server isn't catastrophic -- if both hold, the
reuse/standardization benefit of MCP is real and worth the added
connection-management and latency cost; if not, you're paying MCP's
real costs (a process to run, a connection to manage, new failure
modes) for a benefit that doesn't actually materialize.

**Red flags:** Treats "MCP vs. hand-rolled" as a stylistic or
architectural-fashion choice rather than working through concrete,
tool-specific trade-offs, or can't name a real tool that should stay
hand-rolled despite MCP being available.

**Follow-up:** "Your team's tool is generic and reusable but gets
called on nearly every single agent loop step. Does that change your
answer?"

---

### 8. (Architect) How would you explain to a non-technical stakeholder what's actually different about this chapter's agent compared to Chapter 8's, given that from a user's perspective both agents do exactly the same things?

**Strong answer:** Nothing about what the agent can accomplish changed
for an end user -- the same tasks, the same tools' behavior, the same
loop. What changed is an internal engineering property: two of this
agent's tools are now implemented in a shared, reusable place instead
of copy-pasted into this one project, which means the next team that
needs the same two git operations in a completely different agent
doesn't have to rewrite them, and a bug fix to the git-tools server
benefits every agent connected to it at once instead of needing to be
separately fixed in every project that hand-rolled its own copy. The
honest trade a stakeholder should also hear: that reuse comes with a
new running process to operate and monitor, and a new way this specific
capability can fail (the server being unreachable) that didn't exist
when the tool was just a function call inside the agent's own code.

**Red flags:** Oversells MCP as a user-facing improvement when nothing
about the agent's actual behavior changed, or omits the operational
cost side of the trade-off entirely.

**Follow-up:** "If your team only ever builds one agent and has no
plans to build a second, is this swap still worth making?"

## Strategy Tips

- If asked to design a new tool live and MCP comes up, walk through
  the same three-question test this chapter used (agent-specific state
  coupling, fixed vs. arbitrary behavior, actual reuse/blast-radius
  profile) rather than defaulting to "MCP is best practice."
- If asked about async/sync bridging in general, this chapter's
  `MCPBridge` -- one persistent coroutine, a thread-safe queue, plain
  blocking methods exposed outward -- is a reusable pattern worth
  naming by name, not just "I'd use asyncio somehow."
