"""
Chapter 11 Project: Add Permission Scoping to the Module 3 Agent

Per docs/curriculum/CURRICULUM_MAP.md, Module 5's lab is: "add
permission scoping to the Module 3 agent." This file IS that agent --
Chapter 8's read_file/write_file/edit_file/list_directory/
run_shell_command/git_status/git_diff, copied forward unchanged, plus
one new tool schema (git_commit) that Chapter 8 discussed but
deliberately did not ship. Your job is the permission-scope layer
itself: the thing that decides whether a given tool call is allowed to
run at all, BEFORE dispatch_tool_call ever calls the real function.

Why this matters, concretely: Chapter 8 sketched a `git_commit(message,
confirm=False)` tool and immediately pointed out the flaw -- nothing
stops the model from just setting `confirm=True` itself, because that
flag lives inside the tool call's own arguments, which the model fully
controls. A permission check that the thing being checked can turn off
is not a permission check. The fix has to live somewhere the model has
no reach: a policy the harness consults BEFORE the tool function runs,
and (for anything genuinely destructive) an actual pause for a human,
answered on real stdin -- not a token in the model's own output.

Your task, in order:

  1. Define three named constants: ALLOWED, REQUIRES_CONFIRMATION,
     BLOCKED (plain strings are fine -- see TODO 1).

  2. Build TOOL_POLICY: a dict mapping every tool name in
     TOOL_FUNCTIONS to one of the three tiers above (TODO 2). Read-only
     tools (read_file, list_directory, git_status, git_diff) should be
     ALLOWED. Every tool that changes state (write_file, edit_file,
     run_shell_command, git_commit) should be at least
     REQUIRES_CONFIRMATION. send_email -- a stub included below purely
     to give you a third tier to wire up -- should be BLOCKED
     outright: this agent has no legitimate reason to ever contact an
     external party.

  3. Write check_permission(name) (TODO 3): looks up name in
     TOOL_POLICY. Critically, if name ISN'T in TOOL_POLICY at all, it
     should return BLOCKED, not ALLOWED -- a tool nobody classified is
     safer to refuse than to silently allow. This is a "fail closed"
     default, not an oversight.

  4. Write confirm_with_human(tool_name, args) (TODO 4): prints a
     prompt describing the tool call and reads a real answer from
     input(). Returns True only if the human typed "y" or "yes"
     (case-insensitive, whitespace-stripped). Wrap the input() call in
     a try/except for (EOFError, KeyboardInterrupt) -- if stdin is
     closed or unavailable (this agent running unattended, no human
     actually there), that should DENY by default, not hang or crash.

  5. Rewire dispatch_tool_call (TODO 5): before calling the real tool
     function, look up its policy via check_permission(). If BLOCKED,
     return a clean "error: ... is blocked by policy ..." string and
     stop -- do not call confirm_with_human at all for a blocked tool
     (there's nothing to confirm; it's not happening either way). If
     REQUIRES_CONFIRMATION, call confirm_with_human(name, args); if it
     returns False, return a clean "error: ... requires human
     confirmation, which was not granted" string and stop. Only if the
     policy is ALLOWED, or REQUIRES_CONFIRMATION and the human said
     yes, should the real function actually get called.

When you're done, run this file directly -- it calls
demo_permission_layer() first (no live model needed), which exercises
all three tiers with scripted tool calls so you can see your own
policy layer work before ever touching a live agent run. Compare your
output against solution.py's once every check passes.

Run it:

    pip install openai
    ollama pull llama3.2
    python3 starter.py

If Ollama isn't reachable (or the demo above is all you're testing),
this exits 0 with a clear message instead of crashing or hanging.
"""
import json
import os
import re
import subprocess
import sys

MODEL = "llama3.2"
MAX_STEPS = 8
WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")

SYSTEM_PROMPT = """You are a coding agent with these tools: read_file,
write_file, edit_file, list_directory, run_shell_command, git_status,
git_diff, and git_commit. All paths are relative to the workspace root.

Some of your tools require a human to approve them before they run --
if a tool call comes back with "requires human confirmation, which was
not granted," that is not an error to retry with different arguments;
it means a human was asked and either said no or wasn't available.
Report that outcome honestly instead of trying to work around it.

Prefer edit_file over write_file when you're changing part of an
existing file. Use git_status and git_diff to check your own work
before ever calling git_commit. Reply with plain text and no tool call
when you are done. Only touch files needed for the task."""

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
            "description": "Write text content to a file, given a path relative to the workspace. Overwrites the ENTIRE file if it exists, creates it if not.",
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
            "description": "Replace one exact, unambiguous occurrence of text in an existing file, given a path relative to the workspace.",
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
            "name": "list_directory",
            "description": "List the names of files and subdirectories directly inside a directory (not a file) in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root; use \".\" for the workspace root itself"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run a shell command inside the workspace directory and return its stdout, stderr, and exit code. Commands matching a denylist of destructive patterns are refused before they run, and the command runs with a restricted environment and CPU/memory limits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run"}
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Show the working tree's status inside the workspace. Read-only -- makes no changes.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Show unstaged changes inside the workspace, optionally limited to one file. Read-only -- makes no changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Optional: limit the diff to this path relative to the workspace root"}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Commit all currently staged changes in the workspace with the given message. This is a real, permanent, write-capable git action -- the harness will pause and ask a human to approve it before it runs, no matter what arguments you provide.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The commit message"}
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send a real email to an external address. Not available to this agent under any circumstances -- included only to demonstrate the BLOCKED policy tier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
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


def list_directory(path):
    full = _safe_path(path)
    if not os.path.exists(full):
        return f"error: no such directory: {path}"
    if not os.path.isdir(full):
        return f"error: not a directory: {path}"
    return json.dumps(sorted(os.listdir(full)))


SHELL_DENYLIST = [
    (r"rm\s+-rf\s+/(\s|$)", "recursive delete of the filesystem root"),
    (r"rm\s+-rf\s+~", "recursive delete of the home directory"),
    (r"\bsudo\b", "privilege escalation"),
    (r"git\s+push\b.*--force", "force-push (can destroy remote history)"),
    (r">\s*/dev/sd[a-z]", "writing directly to a raw disk device"),
    (r":\(\)\s*\{\s*:\|:", "fork bomb"),
    (r"\bmkfs\b", "filesystem-formatting command"),
    (r"\bshutdown\b|\breboot\b", "shutting down or rebooting the host"),
    (r"\bcurl\b.*\|\s*sh\b|\bwget\b.*\|\s*sh\b", "piping a downloaded script directly into a shell"),
]


def _blocked_reason(command):
    for pattern, reason in SHELL_DENYLIST:
        if re.search(pattern, command):
            return reason
    return None


try:
    import resource
    _HAVE_RESOURCE_LIMITS = True
except ImportError:  # resource is POSIX-only; not available on Windows
    _HAVE_RESOURCE_LIMITS = False

SHELL_CPU_SECONDS = 5
SHELL_MEMORY_BYTES = 512 * 1024 * 1024  # 512MB address space cap


def _restricted_preexec():
    """Runs in the CHILD process, after fork, before exec -- real,
    kernel-enforced CPU and memory limits the command can't opt out of."""
    resource.setrlimit(resource.RLIMIT_CPU, (SHELL_CPU_SECONDS, SHELL_CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (SHELL_MEMORY_BYTES, SHELL_MEMORY_BYTES))


def _restricted_env():
    """A minimal environment -- PATH only -- so a shell command can't read
    or exfiltrate this process's real environment variables (API keys,
    tokens) just by running `env`."""
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}


def run_shell_command(command):
    reason = _blocked_reason(command)
    if reason:
        return f"error: command blocked ({reason}): {command!r}"
    kwargs = dict(
        shell=True,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=15,
        env=_restricted_env(),
    )
    if _HAVE_RESOURCE_LIMITS:
        kwargs["preexec_fn"] = _restricted_preexec
    try:
        result = subprocess.run(command, **kwargs)
    except subprocess.TimeoutExpired:
        return f"error: command timed out after 15s: {command!r}"
    return json.dumps({"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode})


def git_status():
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=WORKSPACE, capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return f"error: git status failed: {result.stderr.strip()}"
    return result.stdout or "(clean -- no changes)"


def git_diff(path=None):
    cmd = ["git", "diff"]
    if path:
        cmd += ["--", path]
    result = subprocess.run(cmd, cwd=WORKSPACE, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return f"error: git diff failed: {result.stderr.strip()}"
    return result.stdout or "(no changes)"


def git_commit(message):
    """Notice there is no `confirm` parameter here, unlike Chapter 8's
    sketch -- approval happens one layer up, in dispatch_tool_call,
    before this function is ever called. By the time this code runs, a
    human has already said yes."""
    result = subprocess.run(
        ["git", "commit", "-m", message], cwd=WORKSPACE, capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return f"error: git commit failed: {result.stderr.strip()}"
    return result.stdout.strip() or f"committed: {message!r}"


def send_email(to, subject, body):
    """Deliberately never reached once TODO 2/TODO 5 are done: BLOCKED in
    TOOL_POLICY, so dispatch_tool_call refuses the call before this
    function is ever invoked, regardless of arguments."""
    return "error: this should never execute -- send_email is BLOCKED by policy"


def _unclassified_demo_tool():
    """A real, registered function -- deliberately left OUT of TOOL_POLICY,
    used only by demo_permission_layer() to prove your fail-closed
    default (TODO 3) actually works."""
    return "this should never print -- the policy default should block it first"


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "list_directory": list_directory,
    "run_shell_command": run_shell_command,
    "git_status": git_status,
    "git_diff": git_diff,
    "git_commit": git_commit,
    "send_email": send_email,
    "_unclassified_demo_tool": _unclassified_demo_tool,
}


# ---------------------------------------------------------------------------
# TODO 1: define ALLOWED, REQUIRES_CONFIRMATION, and BLOCKED as three
# distinct string constants (their exact string values don't matter, as
# long as they're distinct and you use them consistently below).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# TODO 2: build TOOL_POLICY, a dict mapping each tool name above to one of
# your three constants. read_file/list_directory/git_status/git_diff are
# read-only -> ALLOWED. write_file/edit_file/run_shell_command/git_commit
# change state -> REQUIRES_CONFIRMATION. send_email -> BLOCKED. Leave
# _unclassified_demo_tool OUT of this dict entirely, on purpose.
# ---------------------------------------------------------------------------
TOOL_POLICY = {
    # TODO 2: fill this in
}


def check_permission(name):
    """TODO 3: look up `name` in TOOL_POLICY. If it's present, return its
    tier. If it is NOT present, return your BLOCKED constant -- fail
    closed, not open."""
    raise NotImplementedError("TODO 3: implement check_permission")


def confirm_with_human(tool_name, args):
    """TODO 4: print a prompt describing `tool_name` and `args`, then
    call input() to read a real answer from stdin. Return True only if
    the (stripped, lowercased) answer is "y" or "yes". Wrap the input()
    call in try/except for (EOFError, KeyboardInterrupt) and return
    False in that case -- if there's no human to ask, the safe default
    is to deny, not to hang or to assume yes."""
    raise NotImplementedError("TODO 4: implement confirm_with_human")


def dispatch_tool_call(tc):
    """TODO 5: rewire this so the permission check runs BEFORE the real
    tool function is called:

      1. Parse args as JSON (already done below).
      2. If name isn't in TOOL_FUNCTIONS, return "error: unknown tool: ..."
         (already done below).
      3. Look up the tool's policy tier via check_permission(name).
      4. If BLOCKED: return a clean "error: {name} is blocked by policy
         ..." string. Do not call confirm_with_human.
      5. If REQUIRES_CONFIRMATION: call confirm_with_human(name, args).
         If it returns False, return a clean "error: {name} requires
         human confirmation, which was not granted" string.
      6. Only now -- ALLOWED, or REQUIRES_CONFIRMATION that was granted
         -- actually call TOOL_FUNCTIONS[name](**args), same as every
         prior chapter.
    """
    name = tc.function.name
    try:
        args = json.loads(tc.function.arguments)
    except json.JSONDecodeError:
        return f"error: invalid JSON arguments: {tc.function.arguments!r}"

    if name not in TOOL_FUNCTIONS:
        return f"error: unknown tool: {name}"

    # TODO 5: insert the permission check here, before the try/except
    # below ever runs.

    try:
        return TOOL_FUNCTIONS[name](**args)
    except KeyError as e:
        return f"error: missing required argument {e} for {name}"
    except Exception as e:
        return f"error: tool {name} failed: {e}"


def run_agent(task, client):
    """The plan/act/observe/repeat loop, unchanged from Chapter 7 -- your
    permission-scope work above should not require touching this
    function at all."""
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


class _FakeToolCall:
    """A tiny stand-in for the openai SDK's tool-call object shape
    (`.function.name` / `.function.arguments`), used below to exercise
    dispatch_tool_call directly with scripted calls -- no live model
    needed."""

    class _Fn:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments

    def __init__(self, name, arguments_dict):
        self.function = self._Fn(name, json.dumps(arguments_dict))


def demo_permission_layer():
    """Runs scripted tool calls straight through dispatch_tool_call, one
    per policy tier, without needing a live model. Once TODOs 1-5 are
    done, run this file and confirm: (1) read_file runs immediately with
    no prompt, (2) write_file prints a confirmation prompt and (denying
    on stdin EOF, as this will in an unattended run) refuses, (3)
    send_email is refused instantly with no prompt at all, (4) the
    unclassified tool is refused instantly too, defaulting to BLOCKED."""
    os.makedirs(WORKSPACE, exist_ok=True)
    with open(os.path.join(WORKSPACE, "demo.txt"), "w") as f:
        f.write("original content\n")

    print("=== 1. ALLOWED tool: read_file -- should run immediately, no prompt ===")
    print(dispatch_tool_call(_FakeToolCall("read_file", {"path": "demo.txt"})))

    print("\n=== 2. REQUIRES_CONFIRMATION tool: write_file -- should pause for a human ===")
    print(dispatch_tool_call(_FakeToolCall("write_file", {"path": "demo.txt", "content": "changed\n"})))

    print("\n=== 3. BLOCKED tool: send_email -- should be refused before dispatch, no prompt ===")
    print(dispatch_tool_call(_FakeToolCall(
        "send_email", {"to": "someone@example.com", "subject": "hi", "body": "test"}
    )))

    print("\n=== 4. Registered but unclassified tool -- should default to BLOCKED, fail closed ===")
    print(dispatch_tool_call(_FakeToolCall("_unclassified_demo_tool", {})))

    print("\n=== 5. Unknown tool name entirely -- should be rejected before any policy check ===")
    print(dispatch_tool_call(_FakeToolCall("delete_everything", {})))


def main():
    demo_permission_layer()

    try:
        from openai import OpenAI
    except ImportError:
        print("\nThe openai package isn't installed. Run: pip install openai")
        print("(the permission-layer demo above doesn't need it -- only a live agent run does)")
        sys.exit(0)

    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=8.0)
    task = (
        "Read demo.txt, then use write_file to change its contents to "
        "'updated by agent', then run git_status to check your work."
    )
    print("\n=== Attempting a live agent run against Ollama (may be skipped if unreachable) ===")
    try:
        run_agent(task, client)
    except Exception as e:
        message = str(e).lower()
        if "connect" in message or "connection" in message or "timeout" in message or "timed out" in message:
            print(
                "Could not reach a local Ollama server at http://localhost:11434 (or it "
                "didn't respond in time) -- install Ollama (https://ollama.com), run "
                "`ollama pull llama3.2`, and make sure `ollama serve` is running, then try again. "
                "The permission-layer demo above already ran and needed no live model."
            )
            sys.exit(0)
        raise


if __name__ == "__main__":
    main()
