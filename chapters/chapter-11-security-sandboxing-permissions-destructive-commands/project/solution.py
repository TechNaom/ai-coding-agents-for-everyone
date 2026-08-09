"""
Chapter 11 Project: A Permission-Scoped Agent -- Worked Solution

This is `starter.py` with every TODO filled in. It takes Chapter 8's
reference agent (read_file, write_file, edit_file, list_directory,
run_shell_command, git_status, git_diff -- copied forward unchanged)
and adds exactly one new layer: a harness-enforced permission-scope
check that runs BEFORE any tool is dispatched, plus one new tool
(git_commit) that Chapter 8 discussed but deliberately did not ship,
because it had no real answer yet for "what stops the model from
approving its own commit." This file is that answer.

Read this top-to-bottom once before touching starter.py -- the whole
point of the lab is that the permission layer lives ENTIRELY in code
the model never sees and cannot influence, which is easiest to
understand by seeing the finished version first.

THE CORE IDEA, IN ONE PARAGRAPH: Chapter 8 sketched a `git_commit`
tool with a `confirm=True` argument and immediately pointed out the
flaw -- nothing stops the model from just setting `confirm=True`
itself, because the flag lives inside the tool's own arguments, which
the model fully controls. This file's fix is to move the check
somewhere the model has no reach at all: a `TOOL_POLICY` dict defined
in this file, consulted by `dispatch_tool_call` BEFORE a tool
function is ever called, with three tiers (ALLOWED /
REQUIRES_CONFIRMATION / BLOCKED). "Requires confirmation" doesn't mean
"the model includes a flag" -- it means execution actually pauses and
a REAL human is asked, via real `input()` on real stdin, out-of-band
from anything in the model's conversation. If no human is there to
answer (stdin closed, EOF, running unattended), the default is DENY,
not allow -- a permission check that fails open is not a permission
check.

Run it:

    pip install openai
    ollama pull llama3.2
    python3 solution.py

Runs a scripted demonstration of the permission layer against real
tool calls first (no live model needed for this part -- see
`demo_permission_layer()`), then optionally attempts a real agent run
against Ollama, exactly like Chapters 7-9, exiting cleanly with a
plain message if Ollama isn't reachable rather than crashing or
hanging (the live model call uses a short request timeout for exactly
this reason -- see the `main()` docstring below).
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


# ---------------------------------------------------------------------------
# _safe_path -- unchanged from Chapter 7/8. The workspace boundary check is
# orthogonal to the permission-scope layer below: _safe_path answers "is
# this path even allowed to be touched at all," permission scoping answers
# "does THIS tool need a human's yes before it runs." A tool can pass both,
# either, or neither -- they're independent checks, not one merged into the
# other, exactly because they defend against different threats (scope
# escape vs. an irreversible action a human never saw coming).
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Real, minimal process-level isolation -- honestly scoped. This is NOT a
# sandbox in the container/VM sense: it does not give the command its own
# filesystem, its own network namespace, or its own process namespace. What
# it DOES do, for real, enforced by the kernel rather than requested of the
# subprocess: cap how much CPU time the command can burn before it's killed,
# cap how much memory it can allocate before it gets a MemoryError instead
# of taking the host down, and strip the environment down to a minimal PATH
# so the subprocess doesn't inherit every secret and API key sitting in
# THIS process's environment (Chapter 5/6's context isn't the only thing
# that leaks by being present -- an unfiltered os.environ handed to a
# subprocess is exactly this kind of accidental exposure). See the lesson's
# "Sandboxing, Honestly Scoped" section for exactly what this does and does
# not buy you, and why real isolation needs a container or VM, not more
# Python.
# ---------------------------------------------------------------------------
try:
    import resource
    _HAVE_RESOURCE_LIMITS = True
except ImportError:  # resource is POSIX-only; not available on Windows
    _HAVE_RESOURCE_LIMITS = False

SHELL_CPU_SECONDS = 5
SHELL_MEMORY_BYTES = 512 * 1024 * 1024  # 512MB address space cap


def _restricted_preexec():
    """Runs in the CHILD process, after fork, before exec -- sets real
    kernel-enforced limits the command itself cannot opt out of. Note
    what's deliberately NOT set here: RLIMIT_NPROC (max processes) is a
    per-real-uid limit shared across the ENTIRE host user account, not
    scoped to this subprocess tree -- setting it low here can starve
    unrelated processes the same user is already running, which is worse
    than not setting it at all. That's a real, honest limitation of what
    `resource.setrlimit` can safely do outside a container -- one more
    reason this is "meaningfully reduced risk," not "a sandbox.\""""
    resource.setrlimit(resource.RLIMIT_CPU, (SHELL_CPU_SECONDS, SHELL_CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (SHELL_MEMORY_BYTES, SHELL_MEMORY_BYTES))


def _restricted_env():
    """A minimal environment -- PATH only, nothing else. Strips out every
    other variable in this process's real environment (API keys, tokens,
    cloud credentials -- anything a learner's own shell happens to have
    exported) so a shell command the model asked for can't read or exfiltrate
    them just by running `env` or `printenv`."""
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
    """The tool Chapter 8 discussed and deliberately did NOT ship. Notice
    what's different from Chapter 8's sketch: there is no `confirm`
    parameter here at all. The model has no argument it can set to
    approve its own commit -- approval is not part of this function's
    signature, it happens one layer up, in dispatch_tool_call, before
    this function is ever called. By the time this code runs, a human
    has already said yes."""
    result = subprocess.run(
        ["git", "commit", "-m", message], cwd=WORKSPACE, capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return f"error: git commit failed: {result.stderr.strip()}"
    return result.stdout.strip() or f"committed: {message!r}"


def send_email(to, subject, body):
    """Deliberately never reached: BLOCKED in TOOL_POLICY below, so
    dispatch_tool_call refuses the call before this function is ever
    invoked, regardless of arguments. The function body existing at all
    is not what makes this safe -- the policy check is."""
    return "error: this should never execute -- send_email is BLOCKED by policy"


def _unclassified_demo_tool():
    """A real, registered function -- deliberately left OUT of TOOL_POLICY
    below, used only by demo_permission_layer() to prove the fail-closed
    default. If this were ever reachable, it would just return a string;
    the point is that check_permission() blocks it before it's ever
    called at all, purely because nobody classified it."""
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
# THE PERMISSION-SCOPE LAYER -- the actual subject of this chapter.
# ---------------------------------------------------------------------------

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"

# This dict is the entire policy. It lives in the harness's own source
# file, not in anything the model's context window ever contains, and the
# model has no tool call, no argument, and no phrasing that can change a
# single entry in it. That is the whole point: Chapter 8's `confirm=True`
# sketch failed because the "permission" lived inside data the model
# controlled (its own function-call arguments). This dict lives outside
# that boundary entirely.
#
# Read-only tools are ALLOWED: nothing they do is destructive, so gating
# them behind a human would just be friction with no safety benefit.
# Every write-capable tool is at least REQUIRES_CONFIRMATION.
# send_email is BLOCKED outright -- this agent has no legitimate reason to
# ever contact an external party, so there is no argument-checking, no
# confirmation prompt, nothing worth building for it; it simply cannot run.
TOOL_POLICY = {
    "read_file": ALLOWED,
    "list_directory": ALLOWED,
    "git_status": ALLOWED,
    "git_diff": ALLOWED,
    "write_file": REQUIRES_CONFIRMATION,
    "edit_file": REQUIRES_CONFIRMATION,
    "run_shell_command": REQUIRES_CONFIRMATION,
    "git_commit": REQUIRES_CONFIRMATION,
    "send_email": BLOCKED,
}


def check_permission(name):
    """The harness's own lookup -- never influenced by the model. Any tool
    name NOT explicitly listed in TOOL_POLICY defaults to BLOCKED, not
    ALLOWED: if a new tool ever gets added to TOOLS/TOOL_FUNCTIONS and
    someone forgets to classify it here, the safe failure is "it doesn't
    run," not "it silently runs unguarded." Fail closed, not open."""
    return TOOL_POLICY.get(name, BLOCKED)


def confirm_with_human(tool_name, args):
    """Pause execution and ask a REAL human, out-of-band from the model's
    conversation entirely, using actual stdin. This is what makes
    "requires confirmation" real instead of decorative: the model cannot
    answer this prompt, cannot see it, and cannot pass an argument that
    skips it -- input() here reads from this process's real stdin, which
    in an interactive terminal is a person at a keyboard, not a token the
    model produced.

    Fails CLOSED (denies) if stdin is closed, hits EOF, or anything
    unexpected happens while reading it -- e.g. this agent running
    unattended in a script or CI job with no human actually watching.
    A confirmation step that defaults to "yes" when it can't reach anyone
    isn't a confirmation step; it's a no-op with extra code around it.
    """
    summary = json.dumps(args)
    prompt = f"[confirmation required] allow {tool_name}({summary})? [y/N]: "
    try:
        answer = input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("[no human available to confirm on stdin -- denying by default]")
        return False
    return answer.strip().lower() in ("y", "yes")


def dispatch_tool_call(tc):
    """Turn one tool_use block into a real function call. Never raises.

    The permission check happens FIRST, before args are even trusted
    enough to look up the function -- actually, args are parsed first
    (we need them to know what we'd be confirming), but the function
    itself is never invoked until the policy check clears. That ordering
    is the whole mechanism: nothing about this function's shape lets a
    tool run before its policy tier has been checked.
    """
    name = tc.function.name
    try:
        args = json.loads(tc.function.arguments)
    except json.JSONDecodeError:
        return f"error: invalid JSON arguments: {tc.function.arguments!r}"

    if name not in TOOL_FUNCTIONS:
        return f"error: unknown tool: {name}"

    policy = check_permission(name)

    if policy == BLOCKED:
        return f"error: {name} is blocked by policy and cannot be called, regardless of arguments"

    if policy == REQUIRES_CONFIRMATION:
        if not confirm_with_human(name, args):
            return f"error: {name} requires human confirmation, which was not granted"

    # policy == ALLOWED, or REQUIRES_CONFIRMATION that was just granted --
    # only now does the real function actually run.
    try:
        return TOOL_FUNCTIONS[name](**args)
    except KeyError as e:
        return f"error: missing required argument {e} for {name}"
    except Exception as e:
        return f"error: tool {name} failed: {e}"


def run_agent(task, client):
    """The plan/act/observe/repeat loop, unchanged from Chapter 7. This is
    the point the lesson keeps making: the permission layer above changed
    dispatch_tool_call, not this function. run_agent has no idea a
    confirmation prompt might block mid-call -- it just calls
    dispatch_tool_call and reads back whatever string comes out, exactly
    like every other tool result since Chapter 7."""
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
    needed to prove the permission layer itself works. This mirrors the
    same "test dispatch logic independent of a live model" discipline
    Chapter 7's exercises established."""

    class _Fn:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments

    def __init__(self, name, arguments_dict):
        self.function = self._Fn(name, json.dumps(arguments_dict))


def demo_permission_layer():
    """Runs three scripted tool calls straight through dispatch_tool_call,
    one per policy tier, without needing a live model at all. Reading
    stdin from an unattended run (no terminal attached, or piped from a
    closed/empty source) hits EOFError inside confirm_with_human, which
    denies by default -- so this demo is safe to run in CI or any
    non-interactive environment: it demonstrates the fail-closed behavior
    for real, rather than skipping the confirmation path entirely."""
    os.makedirs(WORKSPACE, exist_ok=True)
    with open(os.path.join(WORKSPACE, "demo.txt"), "w") as f:
        f.write("original content\n")

    print("=== 1. ALLOWED tool: read_file -- runs immediately, no prompt ===")
    print(dispatch_tool_call(_FakeToolCall("read_file", {"path": "demo.txt"})))

    print("\n=== 2. REQUIRES_CONFIRMATION tool: write_file -- pauses for a human ===")
    print(dispatch_tool_call(_FakeToolCall("write_file", {"path": "demo.txt", "content": "changed\n"})))

    print("\n=== 3. BLOCKED tool: send_email -- refused before dispatch, no prompt at all ===")
    print(dispatch_tool_call(_FakeToolCall(
        "send_email", {"to": "someone@example.com", "subject": "hi", "body": "test"}
    )))

    print("\n=== 4. Registered but unclassified tool -- defaults to BLOCKED, fails closed ===")
    print(dispatch_tool_call(_FakeToolCall("_unclassified_demo_tool", {})))

    print("\n=== 5. Unknown tool name entirely -- rejected before any policy check ===")
    print(dispatch_tool_call(_FakeToolCall("delete_everything", {})))


def main():
    demo_permission_layer()

    try:
        from openai import OpenAI
    except ImportError:
        print("\nThe openai package isn't installed. Run: pip install openai")
        print("(the permission-layer demo above doesn't need it -- only a live agent run does)")
        sys.exit(0)

    # A short request timeout matters here specifically: an unreachable or
    # hung Ollama server should fail fast and gracefully, the same
    # posture Chapters 7-9 use, not hang the whole script.
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
