"""
Chapter 9 Level 3 Project: Swap git_status/git_diff for MCP-Based Versions

This is Chapter 8's exact agent (read_file, write_file, edit_file,
run_shell_command, _safe_path, dispatch_tool_call's defensive handling,
run_agent's loop) with git_status and git_diff removed as local Python
functions. They now live in `mcp_git_server.py`, a separate, standalone
MCP server file in this same directory (read it -- it's short, and
you'll want to know its two tools' names and argument shapes before
touching the code below). Nothing about run_agent changed at all, and
nothing needs to: this project's entire point is that the loop doesn't
know or care whether a tool call ends up running a local Python
function or making a round trip to an MCP server.

Your task: implement `connect_git_tools()` below, marked with TODOs.
When you're done, calling it should:

  1. Start `mcp_git_server.py` as a subprocess and open an MCP client
     connection to it over the stdio transport.
  2. Call the MCP server's `list_tools()` to discover what tools it
     exposes (you should find exactly two: `git_status`, `git_diff`).
  3. Convert each discovered tool's MCP metadata (name, description,
     input schema) into this course's existing `{"type": "function",
     "function": {...}}` shape, and append it to the module-level
     `TOOLS` list -- the SAME shape the hand-typed entries above it
     already use. The model should not be able to tell, just by
     reading `TOOLS`, which tools are local and which came from MCP.
  4. Register each discovered tool's name in `MCP_TOOL_NAMES`, so
     `dispatch_tool_call` (already provided, unchanged, below) knows to
     route a call for that name to the MCP server instead of looking
     for it in `TOOL_FUNCTIONS`.
  5. One thing to get right and easy to miss: the MCP server's tools
     require a `workspace` argument (an absolute path) that the MODEL
     should never see or set -- it's injected by the harness via
     `MCP_INJECTED_ARGS`, the same what-the-model-controls-vs-what-the-
     harness-enforces boundary Chapter 8's `_safe_path` drew for local
     file paths. Strip `workspace` out of the schema you show the
     model in step 3 (or it'll try to guess a path and get it wrong).

The `MCPBridge` class below is fully provided -- it's the plumbing that
lets a synchronous loop (`run_agent`, unchanged since Chapter 7) call
an inherently async MCP client without turning the whole file into
`async def` everything. Read its docstring for why it's built the way
it is (a single persistent background event loop + thread-safe queue,
not two separately-scheduled coroutines) -- that's genuinely useful to
understand, but building it yourself isn't this project's learning
goal; wiring `TOOLS`/`TOOL_FUNCTIONS`/`dispatch_tool_call` up to a real
MCP server is. `connect_git_tools()` only needs to call
`MCPBridge(sys.executable, [GIT_SERVER_SCRIPT])`, then
`bridge.list_tools()`, then build and append schema entries.

Once `connect_git_tools()` works, `dispatch_tool_call`'s existing
MCP-routing branch (already provided, unchanged) will pick up the rest.

Run it:

    pip install openai "mcp[cli]"
    ollama pull llama3.2
    python3 starter.py

Both `openai` and `mcp` are optional at import time -- if either is
missing, or if connecting to the MCP git server fails, this exits 0
with a clear message instead of crashing (same graceful-degradation
behavior Chapters 7-8 established). Compare against `solution.py` if
you get stuck -- it's this exact file with `connect_git_tools()` filled
in.
"""
import asyncio
import json
import os
import queue
import re
import subprocess
import sys
import threading

MODEL = "llama3.2"
MAX_STEPS = 8
WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")
GIT_SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_git_server.py")

SYSTEM_PROMPT = """You are a coding agent with these tools: read_file,
write_file, edit_file, run_shell_command, git_status, and git_diff. All
paths are relative to the workspace root.

Prefer edit_file over write_file when you're changing part of an
existing file -- it fails safely instead of risking overwriting content
you didn't mean to touch. Use write_file for brand-new files or when you
genuinely need to replace a whole file's contents. Use git_status and
git_diff to check your own work before declaring a task done -- don't
just assume a write succeeded because no error came back.

Reply with plain text and no tool call when you are done. Only touch
files needed for the task."""

# The hand-rolled, workspace-local tools -- unchanged from Chapter 8.
# These stay hand-rolled on purpose: read_file/write_file/edit_file are
# tightly coupled to THIS agent's workspace boundary (_safe_path), and
# run_shell_command's whole point is running arbitrary commands the
# model composes -- there's no generic "run any shell command" MCP
# server worth depending on for that. git_status/git_diff are different:
# they're generic, reusable, and exactly the kind of tool worth getting
# from a shared MCP server instead of rewriting per project. See the
# lesson's "when hand-rolled is still the right call" section.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a text file, given a path relative to the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file, given a path relative to the workspace. Overwrites the ENTIRE file if it exists, creates it if not. Use edit_file instead if you only need to change part of an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root"},
                    "content": {"type": "string", "description": "The full text content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace one exact, unambiguous occurrence of text in an existing file, given a path relative to the workspace. Fails with a clear error if the text isn't found or appears more than once, instead of guessing which occurrence you meant. Use write_file if you need to replace an entire file's contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root"},
                    "find": {"type": "string", "description": "The exact text to find -- must appear exactly once in the file"},
                    "replace": {"type": "string", "description": "The text to replace it with"},
                },
                "required": ["path", "find", "replace"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run a shell command inside the workspace directory and return its stdout, stderr, and exit code. Commands matching a denylist of destructive patterns (e.g. rm -rf /, sudo, force-pushing) are refused before they run.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run"}
                },
                "required": ["command"],
            },
        },
    },
    # TODO: git_status and git_diff belong here too, but hand-typing them
    # would defeat the point -- connect_git_tools() below appends them at
    # startup, built FROM the MCP server's own list_tools() response.
]


def _safe_path(path):
    """Reject any path that would resolve outside the workspace directory."""
    full = os.path.abspath(os.path.join(WORKSPACE, path))
    if not full.startswith(os.path.abspath(WORKSPACE) + os.sep) and full != os.path.abspath(WORKSPACE):
        raise ValueError(f"path escapes workspace: {path}")
    return full


def read_file(path):
    try:
        with open(_safe_path(path)) as f:
            return f.read()
    except FileNotFoundError:
        return f"error: no such file: {path}"


def write_file(path, content):
    full = _safe_path(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return f"wrote {len(content)} bytes to {path}"


def edit_file(path, find, replace):
    full = _safe_path(path)
    try:
        with open(full) as f:
            content = f.read()
    except FileNotFoundError:
        return f"error: no such file: {path}"

    count = content.count(find)
    if count == 0:
        return f"error: text not found in {path}: {find!r}"
    if count > 1:
        return (
            f"error: text {find!r} appears {count} times in {path} -- "
            "edit_file only replaces an exact, unambiguous match; include "
            "more surrounding context to make it unique"
        )

    new_content = content.replace(find, replace, 1)
    with open(full, "w") as f:
        f.write(new_content)
    return f"replaced 1 occurrence in {path} ({len(new_content)} bytes now)"


SHELL_DENYLIST = [
    (r"rm\s+-rf\s+/(\s|$)", "recursive delete of the filesystem root"),
    (r"rm\s+-rf\s+~", "recursive delete of the home directory"),
    (r"\bsudo\b", "privilege escalation"),
    (r"git\s+push\b.*--force", "force-push (can destroy remote history)"),
    (r">\s*/dev/sd[a-z]", "writing directly to a raw disk device"),
    (r":\(\)\s*\{\s*:\|:", "fork bomb"),
    (r"\bmkfs\b", "filesystem-formatting command"),
    (r"\bshutdown\b|\breboot\b", "shutting down or rebooting the host"),
]


def _blocked_reason(command):
    for pattern, reason in SHELL_DENYLIST:
        if re.search(pattern, command):
            return reason
    return None


def run_shell_command(command):
    reason = _blocked_reason(command)
    if reason:
        return f"error: command blocked ({reason}): {command!r}"
    result = subprocess.run(
        command, shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=15
    )
    return json.dumps({"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode})


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "run_shell_command": run_shell_command,
    # git_status and git_diff are deliberately NOT here -- they're not
    # local functions anymore. See MCP_TOOL_NAMES / dispatch_tool_call.
}


# ---------------------------------------------------------------------------
# The MCP integration -- MCPBridge is fully provided (see its docstring
# for why it's built this way); connect_git_tools() below is your job.
# ---------------------------------------------------------------------------
class MCPBridge:
    """A synchronous facade over one persistent MCP client connection,
    for use from a synchronous caller (this chapter's run_agent).

    Implementation note, found the hard way while building this: a
    naive version of this class that scheduled `client.__aenter__()` and
    `client.__aexit__()` as two SEPARATE `run_coroutine_threadsafe`
    calls raised a real error from the `anyio` library underneath MCP's
    stdio transport: "Attempted to exit cancel scope in a different task
    than it was entered in." anyio's task groups tie a cancel scope to
    the specific async task that opened it, and two separately-scheduled
    coroutines on the same event loop still count as two different
    tasks. The fix, used below: the client's entire connected lifetime
    runs inside ONE coroutine (`_worker`), and the background thread
    talks to it through a plain thread-safe queue instead of re-entering
    the context manager from separate calls.
    """

    def __init__(self, command, args, timeout=20):
        self._timeout = timeout
        self._requests = queue.Queue()
        self._ready = threading.Event()
        self._error = None
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop, args=(command, args), daemon=True
        )
        self._thread.start()
        self._ready.wait(timeout=self._timeout)
        if self._error:
            raise self._error

    def _run_loop(self, command, args):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._worker(command, args))

    async def _worker(self, command, args):
        from mcp import Client, StdioServerParameters, stdio_client

        params = StdioServerParameters(command=command, args=args)
        try:
            async with Client(stdio_client(params)) as client:
                self._ready.set()
                while True:
                    kind, payload, result_q = await self._loop.run_in_executor(
                        None, self._requests.get
                    )
                    if kind == "stop":
                        result_q.put(("ok", None))
                        return
                    try:
                        if kind == "list_tools":
                            result = await client.list_tools()
                            result_q.put(("ok", result.tools))
                        elif kind == "call_tool":
                            name, call_args = payload
                            result = await client.call_tool(name, call_args)
                            if result.is_error:
                                text = (
                                    result.content[0].text
                                    if result.content
                                    else "unknown MCP error"
                                )
                                result_q.put(
                                    ("ok", f"error: MCP tool {name!r} failed: {text}")
                                )
                            elif result.content:
                                result_q.put(("ok", result.content[0].text))
                            else:
                                result_q.put(("ok", str(result.structured_content)))
                    except Exception as e:  # noqa: BLE001 -- surfaced to the caller, not swallowed
                        result_q.put(("error", e))
        except Exception as e:
            self._error = e
            self._ready.set()

    def _call(self, kind, payload=None):
        result_q = queue.Queue()
        self._requests.put((kind, payload, result_q))
        status, value = result_q.get(timeout=self._timeout)
        if status == "error":
            raise value
        return value

    def list_tools(self):
        return self._call("list_tools")

    def call_tool(self, name, args):
        return self._call("call_tool", (name, args))

    def close(self):
        try:
            self._call("stop")
        except Exception:
            pass
        self._thread.join(timeout=self._timeout)


# Tools sourced from the MCP git server, filled in by connect_git_tools().
MCP_BRIDGE = None
MCP_TOOL_NAMES = set()
# Arguments the harness injects itself before forwarding a call to the
# MCP server -- NOT something the model supplies. The git MCP server's
# tools require an absolute `workspace` path (it has no built-in concept
# of "this agent's workspace"), but the model has no reliable way to
# know that absolute path, and shouldn't need to -- the same
# what-the-model-controls-vs-what-the-harness-enforces boundary Chapter
# 8's _safe_path lesson drew for file paths, generalized to an MCP tool
# argument instead of a local one.
MCP_INJECTED_ARGS = {"workspace": WORKSPACE}


def connect_git_tools():
    """
    TODO: implement this function. See the module docstring above for
    the full walkthrough. In short:

    1. TODO 1 -- construct an MCPBridge pointed at mcp_git_server.py,
       running as a subprocess via sys.executable. Wrap it in a
       try/except: on failure, print a clear message and `return False`
       -- do NOT let a missing/unreachable MCP server crash the whole
       agent. Losing git_status/git_diff for one run is a real
       capability loss, not a reason to abort a task that might not
       have needed git tools anyway.

    2. TODO 2 -- call bridge.list_tools() to discover the server's
       tools. Wrap in try/except the same way; on failure, close the
       bridge and `return False`.

    3. TODO 3 -- for each discovered tool, strip MCP_INJECTED_ARGS keys
       out of its input schema's `properties`/`required` (the model
       should never see or set `workspace`), then append a
       {"type": "function", "function": {"name": ..., "description":
       ..., "parameters": ...}} entry to the module-level TOOLS list,
       and add the tool's name to MCP_TOOL_NAMES.

    4. TODO 4 -- set the module-level MCP_BRIDGE to the connected
       bridge, print a confirmation message naming the discovered
       tools, and `return True`.
    """
    global MCP_BRIDGE
    raise NotImplementedError("connect_git_tools: fill in TODOs 1-4 -- see the docstring above")


def dispatch_tool_call(tc):
    """Turn one tool_use block into a real function call. Never raises.

    Unchanged from Chapter 8 except for one new branch: if `name` isn't
    a local Python function, check whether it's an MCP tool before
    calling it unknown. Everything else -- the JSON-parsing guard, the
    unknown-tool guard, the KeyError/generic-Exception handling -- is
    identical to Chapters 7 and 8. Provided as-is; this is not your
    TODO -- it already knows how to route to MCP_BRIDGE once
    connect_git_tools() has populated MCP_TOOL_NAMES."""
    name = tc.function.name
    try:
        args = json.loads(tc.function.arguments)
    except json.JSONDecodeError:
        return f"error: invalid JSON arguments: {tc.function.arguments!r}"

    if name in TOOL_FUNCTIONS:
        try:
            return TOOL_FUNCTIONS[name](**args)
        except KeyError as e:
            return f"error: missing required argument {e} for {name}"
        except Exception as e:
            return f"error: tool {name} failed: {e}"

    if name in MCP_TOOL_NAMES:
        if MCP_BRIDGE is None:
            return f"error: tool {name} is an MCP tool but no MCP connection is active"
        full_args = {**args, **{k: v for k, v in MCP_INJECTED_ARGS.items() if k in _mcp_full_schema_params(name)}}
        try:
            return MCP_BRIDGE.call_tool(name, full_args)
        except Exception as e:
            return f"error: MCP call to {name} failed: {e}"

    return f"error: unknown tool: {name}"


def _mcp_full_schema_params(name):
    """Every MCP tool this agent knows about takes `workspace` -- both
    of mcp_git_server.py's tools do. Kept as a tiny helper rather than
    re-fetching the full (untrimmed) schema per call."""
    return set(MCP_INJECTED_ARGS)


def run_agent(task, client):
    """The plan/act/observe/repeat loop -- unchanged from Chapter 7 and
    Chapter 8. Nothing here knows or cares whether a given tool call is
    about to be handled by a local Python function or a round trip to
    an MCP server; that decision was already made by connect_git_tools()
    and dispatch_tool_call() before this function ever runs."""
    os.makedirs(WORKSPACE, exist_ok=True)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    for step in range(1, MAX_STEPS + 1):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            print(f"[clean stop after {step} step(s)]")
            print(msg.content)
            return messages

        for tc in msg.tool_calls:
            result = dispatch_tool_call(tc)
            print(f"  step {step}: {tc.function.name}({tc.function.arguments}) -> {str(result)[:200]}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})

    print(f"[step cap reached after {MAX_STEPS} steps without a clean stop]")
    return messages


def main():
    try:
        from openai import OpenAI
    except ImportError:
        print("The openai package isn't installed. Run: pip install openai")
        sys.exit(0)

    try:
        import mcp  # noqa: F401 -- import-checked here, used inside MCPBridge
    except ImportError:
        print('The mcp package isn\'t installed. Run: pip install "mcp[cli]"')
        print("Continuing is possible without it, but this chapter's whole point is the MCP-backed git tools, so exiting instead.")
        sys.exit(0)

    try:
        connect_git_tools()
    except NotImplementedError as e:
        print(f"connect_git_tools() isn't implemented yet: {e}")
        print("Fill in the TODOs in connect_git_tools() (see this file's module docstring), then run again.")
        sys.exit(0)

    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    task = (
        "Create a file named notes.txt containing the line 'first draft'. "
        "Then use edit_file to change 'first draft' to 'final draft'. "
        "Then run git_status to confirm the file shows up as a change."
    )
    try:
        run_agent(task, client)
    except Exception as e:
        message = str(e).lower()
        if "connect" in message or "connection" in message:
            print(
                "Could not reach a local Ollama server at http://localhost:11434 -- "
                "install Ollama (https://ollama.com), run `ollama pull llama3.2`, "
                "and make sure `ollama serve` is running, then try again."
            )
            sys.exit(0)
        raise
    finally:
        if MCP_BRIDGE is not None:
            MCP_BRIDGE.close()


if __name__ == "__main__":
    main()
