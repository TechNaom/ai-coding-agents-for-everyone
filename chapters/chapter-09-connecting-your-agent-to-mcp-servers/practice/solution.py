"""
Chapter 9 Practice: Find the Flaw in Four MCP-Integration Diffs

Module 3's assessment (per docs/curriculum/CURRICULUM_MAP.md) is a
working code review checklist, not a written exam -- the actual skill
being tested is whether you can find what's wrong in a real
tool-integration diff using Chapter 3's five review questions. This
script hands you four small, plausible-looking snippets of MCP
integration code, each with exactly one deliberate, realistic flaw.

No `openai` package, no `mcp` package, no Ollama, no network -- just
Python.

    python3 --version
    python3 starter.py

Before running it, read each of the four DIFFS below and, for each
one, predict: what's the one flaw, and which of Chapter 3's five
review questions would catch it (does it match its stated goal, does
it stay inside its boundary, is every change justified, is it
consistent with the rest of the file's patterns, is it a root-cause
fix or a symptom fix)? Write your four predictions down. Then run the
script -- it prints each diff followed by its answer key -- and
compare.
"""

DIFFS = [
    {
        "title": "Diff 1 -- the schema that forgot to strip workspace",
        "snippet": '''\
def connect_git_tools():
    bridge = MCPBridge(sys.executable, [GIT_SERVER_SCRIPT])
    tools = bridge.list_tools()
    for t in tools:
-       schema = _strip_injected_args(t.input_schema, MCP_INJECTED_ARGS)
+       schema = t.input_schema  # simplified -- pass the schema straight through
        TOOLS.append({
            "type": "function",
            "function": {"name": t.name, "description": t.description, "parameters": schema},
        })
        MCP_TOOL_NAMES.add(t.name)
''',
        "flaw": (
            "The model now sees `workspace` as a required argument it's expected to "
            "supply -- but it has no reliable way to know this agent's own absolute "
            "workspace path. Either the model guesses wrong (a real, silent failure "
            "mode -- the call might succeed against the WRONG directory) or the schema "
            "validation rejects a call missing a value the model was never told how to "
            "produce correctly. This is the harness-vs-model-controlled boundary Chapter "
            "7's _safe_path() drew for file paths, broken here for an MCP argument."
        ),
        "checklist_question": (
            "Question 2 (did it touch anything outside the stated boundary?) and "
            "Question 5 (root cause vs. symptom) both apply: 'simplified' silently "
            "removed a real safety boundary, not a cosmetic step, and the failure it "
            "introduces (a wrong or missing workspace) is the kind that fails quietly "
            "instead of loudly."
        ),
    },
    {
        "title": "Diff 2 -- the connection failure that crashes instead of degrading",
        "snippet": '''\
def connect_git_tools():
    global MCP_BRIDGE
-   try:
-       bridge = MCPBridge(sys.executable, [GIT_SERVER_SCRIPT])
-   except Exception as e:
-       print(f"[mcp] could not connect to mcp_git_server.py: {e}")
-       return False
+   bridge = MCPBridge(sys.executable, [GIT_SERVER_SCRIPT])  # let failures surface directly
    tools = bridge.list_tools()
    ...
''',
        "flaw": (
            "Removing the try/except means ANY failure to start or connect to "
            "mcp_git_server.py -- a missing mcp package, a typo in GIT_SERVER_SCRIPT, "
            "the server process crashing on startup -- now propagates as an unhandled "
            "exception out of connect_git_tools(), which (per main()'s actual structure) "
            "crashes the whole agent before it ever gets a chance to run with its four "
            "remaining local tools. Losing git_status/git_diff for one run is a real "
            "capability loss; crashing an entire task that might not have needed git "
            "tools at all is a much bigger regression, and a silent one from the caller's "
            "point of view -- 'the agent crashed' gives no hint the actual cause was an "
            "optional MCP connection."
        ),
        "checklist_question": (
            "Question 4 (is it consistent with the rest of the file's patterns?) -- "
            "every other failure path in this file (missing openai, missing mcp, "
            "unreachable Ollama) degrades gracefully with a clear message and exit(0) "
            "or a False return. This diff makes exactly one failure path behave "
            "completely differently from every other one, with no stated reason."
        ),
    },
    {
        "title": "Diff 3 -- trusting an MCP result without checking is_error",
        "snippet": '''\
elif kind == "call_tool":
    name, call_args = payload
    result = await client.call_tool(name, call_args)
-   if result.is_error:
-       text = result.content[0].text if result.content else "unknown MCP error"
-       result_q.put(("ok", f"error: MCP tool {name!r} failed: {text}"))
-   elif result.content:
-       result_q.put(("ok", result.content[0].text))
-   else:
-       result_q.put(("ok", str(result.structured_content)))
+   result_q.put(("ok", result.content[0].text))  # tools always return content, right?
''',
        "flaw": (
            "This assumes result.content is always a non-empty list -- true for the "
            "happy path, but an MCP tool that fails (is_error=True) may still populate "
            "content with an error message, or in some failure modes return no content "
            "at all, which means result.content[0] can raise IndexError and crash the "
            "whole background worker thread. Even when it doesn't crash, an error "
            "message from a failed git command would get silently returned to the model "
            "as if it were a SUCCESSFUL git_status/git_diff result, with no 'error:' "
            "prefix -- the model has no way to tell a real status output from an error "
            "message describing why the command failed."
        ),
        "checklist_question": (
            "Question 1 (does it actually match the acceptance criterion, not just "
            "pass it?) and Question 5 (root cause vs. symptom): this 'simplification' "
            "passes the happy-path case just fine, which is exactly what makes it "
            "dangerous -- it looks correct in normal testing and only fails on the "
            "specific error case it was supposed to handle."
        ),
    },
    {
        "title": "Diff 4 -- adding a tool no one asked to make an MCP dependency",
        "snippet": '''\
# A teammate's proposal, not yet merged:
+ @mcp.tool()
+ def run_shell_command(workspace: str, command: str) -> str:
+     """Run an arbitrary shell command inside the workspace and return output."""
+     result = subprocess.run(command, shell=True, cwd=workspace, capture_output=True, text=True)
+     return result.stdout
''',
        "flaw": (
            "run_shell_command's entire point is running whatever arbitrary command "
            "string the model composes for a specific task -- there's no fixed behavior "
            "to standardize the way a fixed `git status --porcelain` call has, so moving "
            "it behind MCP doesn't buy the reuse benefit that justified git_status/"
            "git_diff's move. It also drops Chapter 8's SHELL_DENYLIST check entirely -- "
            "this version runs ANY command with no mitigation at all, a real regression "
            "from Chapter 8's already-honestly-limited version, now also harder to see "
            "because it's in a separate file the reviewer might not think to check as "
            "carefully as the main agent file."
        ),
        "checklist_question": (
            "Question 3 (is there a change with no clear justification?) and Question 4 "
            "(consistent with the rest of the codebase's patterns?) -- this diff both "
            "silently drops an existing safety mitigation (the denylist) with no stated "
            "reason, and applies MCP to a tool that this chapter's own criteria (generic, "
            "reusable, low-blast-radius) explicitly argue against."
        ),
    },
]


def main():
    for i, d in enumerate(DIFFS, start=1):
        print(f"\n{'=' * 70}")
        print(f"Diff {i}: {d['title']}")
        print("=" * 70)
        print(d["snippet"])
        print("--- ANSWER KEY ---")
        print(f"Flaw: {d['flaw']}")
        print(f"\nWhich checklist question catches it: {d['checklist_question']}")


if __name__ == "__main__":
    main()
