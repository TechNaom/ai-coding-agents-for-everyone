"""
Chapter 7 Reference Implementation: A Minimal Coding Agent

This is the exact agent built across the lesson -- a system prompt, three
real tools (read_file, write_file, run_shell_command), and a loop that
calls the model, dispatches any tool calls, appends real results, and
repeats until a clean stop (no tool call) or a step cap (Chapter 4's
stop conditions, made real).

This isn't a fill-in-the-blank exercise -- it's the reference agent the
Module 3 Level 2 project (unlocking after Chapter 8) will have you extend
with a new tool, and what project/ai-paired.html has you pair with an AI
assistant to extend right now, then critique the result. Read it, run it,
and get comfortable with every line before pairing.

Requires a local Ollama server with a tool-calling-capable model pulled
(this course used `llama3.2`, ~2GB download, runs on modest hardware --
see the lesson for the exact setup). If Ollama isn't running, this script
detects that and exits cleanly with a message instead of crashing, so it
never fails CI or a fresh clone with nothing installed yet.

Run it:

    pip install openai
    ollama pull llama3.2
    python3 starter.py
"""
import json
import os
import subprocess
import sys

MODEL = "llama3.2"
MAX_STEPS = 8
WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")

SYSTEM_PROMPT = """You are a minimal coding agent. You have three tools:
read_file, write_file, and run_shell_command. All paths are relative to
the workspace root. Use tools to accomplish the user's task, then reply
with a plain text summary and no tool call when you are done. Only touch
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
            "description": "Write text content to a file, given a path relative to the workspace. Overwrites the file if it exists, creates it if not.",
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
            "name": "run_shell_command",
            "description": "Run a shell command inside the workspace directory and return its stdout, stderr, and exit code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run"}
                },
                "required": ["command"],
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


def run_shell_command(command):
    result = subprocess.run(
        command, shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=15
    )
    return json.dumps({"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode})


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_shell_command": run_shell_command,
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
    """The plan/act/observe/repeat loop, made real."""
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
        "Write a file named hello.txt in the workspace containing the "
        "single line: Hello from the minimal agent. Then read it back "
        "to confirm the contents are correct."
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
