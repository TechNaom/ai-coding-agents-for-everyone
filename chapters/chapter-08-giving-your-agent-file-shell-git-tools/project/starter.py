"""
Chapter 8 Level 2 Project: Extend the Agent With One New Tool of Your Own

This is Chapter 7's reference agent (read_file, write_file,
run_shell_command, the loop, dispatch_tool_call's defensive handling)
extended with the tools this chapter built: edit_file (a safer,
targeted alternative to overwriting a whole file), git_status and
git_diff (read-only, safe git integration), and a hardened
run_shell_command that checks commands against a denylist before
running them. None of that is your job to write -- it's provided,
tested scaffold, the same way Chapter 7's whole file was provided
scaffold for pairing with an AI assistant.

Your job: add ONE new tool of your own choosing. Some ideas, roughly in
order of difficulty:

  - list_directory(path) -- list a directory's contents (this chapter's
    lesson builds this one in full; project/solution.py shows it as the
    worked example, so if you want a real challenge, pick a different
    tool and only peek at solution.py once you've tried your own).
  - append_to_file(path, content) -- append text to an existing file
    without overwriting it, erroring cleanly if the file doesn't exist.
  - git_log(n) -- return the last n commit messages (read-only).
  - file_exists(path) -- a cheap existence check the model can call
    before deciding whether to read_file or write_file.
  - count_lines(path) -- return how many lines a file has.

Whatever you pick, follow the exact pattern every tool above already
uses:

  1. A schema entry in TOOLS: name, a precise description (say exactly
     what it operates on -- "a file" vs. "a directory" -- Chapter 8's
     lesson explains why that precision matters), and an argument
     schema.
  2. A real function that routes every path argument through
     _safe_path() -- no exceptions, no "just this once."
  3. Clean, descriptive "error: ..." strings for expected failure
     cases (missing file, missing directory, wrong type) -- matching
     the pattern read_file/edit_file/list_directory below already
     establish. Don't let an exception fall through to
     dispatch_tool_call's generic handler if you can return a specific
     message instead.
  4. A new entry in TOOL_FUNCTIONS.

When you're done, review your own diff against Chapter 3's five-question
checklist before calling it finished -- specifically question 2 (did it
touch anything outside the stated boundary?) and question 4 (is it
consistent with the rest of the file's patterns?). Those are exactly
the two questions the AI-produced list_files tool in Chapter 7's
project/solution.py failed, and exactly the two this project is
designed to test whether you now catch in your own work.

Run it:

    pip install openai
    ollama pull llama3.2
    python3 starter.py

If Ollama isn't reachable, this exits 0 with a clear message instead of
crashing (same graceful-degradation behavior as Chapter 7).
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
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Show the working tree's status (which files are modified, staged, or untracked) inside the workspace. Read-only -- makes no changes.",
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
    # TODO: add your own tool's schema entry here. See the module
    # docstring above for ideas and the exact pattern to follow.
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


# A denylist, not an allowlist: a small, named set of patterns for
# commands that are almost never what a coding-task agent should be
# running unsupervised. This is a speed bump, not a sandbox -- see the
# lesson's "what this doesn't solve" section. Real isolation is
# Chapter 11's subject.
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
    """Return a human-readable reason if `command` matches the denylist, else None."""
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


# TODO: implement your own tool function here, using _safe_path() for
# any path argument, and returning a clean "error: ..." string (not a
# raised exception) for expected failure cases.


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "run_shell_command": run_shell_command,
    "git_status": git_status,
    "git_diff": git_diff,
    # TODO: register your new tool function here, e.g.:
    # "list_directory": list_directory,
}


def dispatch_tool_call(tc):
    """Turn one tool_use block into a real function call. Never raises."""
    name = tc.function.name
    try:
        args = json.loads(tc.function.arguments)
    except json.JSONDecodeError:
        return f"error: invalid JSON arguments: {tc.function.arguments!r}"

    if name not in TOOL_FUNCTIONS:
        return f"error: unknown tool: {name}"

    try:
        return TOOL_FUNCTIONS[name](**args)
    except KeyError as e:
        return f"error: missing required argument {e} for {name}"
    except Exception as e:
        return f"error: tool {name} failed: {e}"


def run_agent(task, client):
    """The plan/act/observe/repeat loop, unchanged from Chapter 7."""
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


if __name__ == "__main__":
    main()
