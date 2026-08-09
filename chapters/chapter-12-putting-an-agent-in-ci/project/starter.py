"""
Chapter 12 Project: Wire a Minimal Agent Into a CI Check

Per docs/curriculum/CURRICULUM_MAP.md, Module 5's second lab is exactly
this: "wire a minimal agent into a CI check." This file is Chapter 11's
exact permission-scoped agent (TOOL_POLICY, check_permission,
confirm_with_human, dispatch_tool_call, git_commit -- all copied
forward unchanged, none of it is a TODO) plus everything CI needs on
top of it, which IS your job: a SECOND, separate, more restrictive
policy (TOOL_POLICY_CI), and two new scope checks (a CI-scratch write
boundary and a protected-branch check on commits) that stand in for
the human confirmation CI cannot provide.

THE CORE IDEA, IN ONE PARAGRAPH: drop Chapter 11's agent into CI
unchanged and it is SAFE but USELESS -- every REQUIRES_CONFIRMATION
tool call hits `confirm_with_human`, which hits EOFError on CI's closed
stdin, and denies. That's the correct outcome for an agent that hasn't
been told anything else, but it also means the agent can't do a single
useful write. The WRONG fix is making `confirm_with_human` auto-answer
"yes" in CI -- that recreates Chapter 8's exact self-granted-permission
flaw, just one layer up. The RIGHT fix is a SEPARATE policy, decided by
a human ahead of time and reviewed via the same PR process this whole
course has taught, where each tool that becomes more permissive in CI
is paired with a narrower, code-level scope that substitutes for the
human confirmation CI cannot give.

Your task, in order:

  1. Inside `write_file` (TODO 1): before writing anything, if CI_MODE
     is on and the path is NOT inside CI_SCRATCH_PREFIX, return a clean
     error string instead of writing. `_in_ci_scratch(path)` is already
     provided.

  2. Build `TOOL_POLICY_CI` (TODO 2): a policy dict, same shape as
     `TOOL_POLICY` above it, for CI runs specifically. Read-only tools
     stay ALLOWED. `run_tests` (new, narrow, bounded) is ALLOWED.
     `write_file` and `git_commit` become ALLOWED -- but only because
     TODOs 1 and 3 add code-level scope checks inside their own
     function bodies that substitute for the confirmation CI can't
     give. `edit_file` and `run_shell_command` become BLOCKED outright
     (no narrow scope exists for either). `send_email` stays BLOCKED.

  3. Inside `git_commit` (TODO 3): before committing, if CI_MODE is on,
     check the current branch via `_current_branch()` (already
     provided). If it's in PROTECTED_BRANCHES, return a clean error
     string instead of committing.

  4. Inside `run_agent` (TODO 4): add a wall-clock budget check. Before
     each step, if CI_MODE is on and `time.monotonic()` has passed a
     deadline (`CI_WALL_CLOCK_BUDGET_SECONDS` after the loop started),
     stop and return `messages` instead of continuing -- a run that
     hangs or thrashes in CI wastes real, metered CI minutes and blocks
     a real PR, a cost Chapter 5's abstract discussion of stalling and
     thrashing didn't have to reckon with.

Run it:

    python3 starter.py                       # interactive-mode demo (Chapter 11's exact behavior)
    ACAFE_CI_MODE=1 python3 starter.py        # CI-mode demo (this chapter's new policy)

Both run entirely offline -- no live model needed for either demo (see
`demo_interactive_mode()` and `demo_ci_mode()`). Compare your output
against `solution.py`'s once every TODO is filled in.
"""
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

MODEL = "llama3.2"
WORKSPACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")

# ---------------------------------------------------------------------------
# CI_MODE -- read ONCE, at startup, from an environment variable the CI
# workflow sets. This is the harness deciding which policy applies, before
# the model has produced a single token -- not something a tool call, a
# system-prompt instruction, or any part of the model's own output can
# change mid-run. Compare this to Chapter 8's `confirm=True`: that failed
# because the checked thing controlled the check. CI_MODE is read from the
# process's own environment at import time and never touched again --
# nothing downstream of this line, including every function below, has any
# way to change it.
# ---------------------------------------------------------------------------
CI_MODE = os.environ.get("ACAFE_CI_MODE") == "1"

# Real, kernel-enforced CI cost, not an abstract one: Chapter 5 discussed
# thrashing/looping/stalling in the abstract. In CI, a run that thrashes
# burns real, metered CI minutes and blocks a real PR from merging while it
# does it. MAX_STEPS is lower in CI mode than interactive mode for exactly
# this reason, and a wall-clock budget backs it up independently of step
# count (a single step that itself hangs -- e.g. a shell command near its
# own timeout, repeated -- could still burn a lot of wall-clock time even
# under a low step cap).
MAX_STEPS_INTERACTIVE = 8
MAX_STEPS_CI = 5
CI_WALL_CLOCK_BUDGET_SECONDS = 90

SYSTEM_PROMPT = """You are a coding agent with these tools: read_file,
write_file, edit_file, list_directory, run_shell_command, run_tests,
git_status, git_diff, and git_commit. All paths are relative to the
workspace root.

Some of your tools require a human to approve them before they run, or
are unavailable entirely in this run -- if a tool call comes back with
"requires human confirmation, which was not granted" or "is blocked by
policy," that is not an error to retry with different arguments; it
means the harness's policy for this run decided the answer already.
Report that outcome honestly instead of trying to work around it.

When running in CI mode, you cannot write outside a scratch directory
and cannot commit to a protected branch -- work within those bounds
rather than treating them as bugs to route around. Reply with plain
text and no tool call when you are done."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the full contents of a text file, given a path relative to the workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path relative to the workspace root"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file, given a path relative to the workspace. In CI mode, only paths inside the ci-scratch/ prefix are accepted.",
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
            "description": "Replace one exact, unambiguous occurrence of text in an existing file. Not available in CI mode at all -- a CI agent proposes changes via write_file inside ci-scratch/ instead of editing tracked files in place.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root"},
                    "find": {"type": "string", "description": "The exact text to find -- must appear exactly once"},
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
            "description": "List the names of files and subdirectories directly inside a directory in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Path relative to the workspace root; use \".\" for the root"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run an ARBITRARY shell command inside the workspace. Requires human confirmation interactively; BLOCKED entirely in CI mode -- there is no narrow scope that makes an arbitrary command safe to run unattended.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "The shell command to run"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run this workspace's fixed test command (no arguments accepted) and return its output. Narrow and bounded by design -- unlike run_shell_command, it cannot run anything other than the test suite, which is why it's ALLOWED in both interactive and CI mode.",
            "parameters": {"type": "object", "properties": {}, "required": []},
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
                "properties": {"path": {"type": "string", "description": "Optional: limit the diff to this path"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Commit all staged changes with the given message. Requires human confirmation interactively. In CI mode, allowed WITHOUT a human confirmation, but only on a non-protected branch -- refused outright on main/master regardless of arguments.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string", "description": "The commit message"}},
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send a real email to an external address. Not available to this agent under any circumstances, interactively or in CI -- included only to demonstrate the BLOCKED tier persisting across both policies.",
            "parameters": {
                "type": "object",
                "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject", "body"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# _safe_path -- unchanged from Chapters 7-11. Independent of everything
# else in this file, including CI_MODE: a path that escapes the workspace
# is rejected the exact same way whether this run is interactive or CI.
# ---------------------------------------------------------------------------
def _safe_path(path):
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


# ---------------------------------------------------------------------------
# CI-scratch scoping -- a THIRD independent boundary, alongside _safe_path
# (workspace boundary) and TOOL_POLICY_CI (per-tool tier). It answers a
# question neither of the other two can: given that write_file is ALLOWED
# in CI mode at all, WHICH paths inside the workspace is it allowed to
# touch? This is exactly the "scoped, pre-approved" idea the lesson
# describes -- a human decided this prefix ahead of time, it's reviewed the
# same way any other code change is, and nothing at runtime (not the model,
# not this file's own CI_MODE flag once set) can widen it.
# ---------------------------------------------------------------------------
CI_SCRATCH_PREFIX = "ci-scratch/"


def _in_ci_scratch(path):
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.startswith(CI_SCRATCH_PREFIX)


def write_file(path, content):
    # TODO 1: if CI_MODE is True and `path` is NOT inside CI_SCRATCH_PREFIX
    # (use the provided _in_ci_scratch(path) helper), return a clean
    # "error: ..." string here and do NOT write anything. Do not touch
    # anything below this comment.
    full = _safe_path(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return f"wrote {len(content)} bytes to {path}"


def edit_file(path, find, replace):
    # In CI mode this is never reached -- TOOL_POLICY_CI["edit_file"] is
    # BLOCKED, so dispatch_tool_call refuses the call before this function
    # runs at all. The function body is unchanged from Chapter 11 for the
    # interactive case.
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
except ImportError:
    _HAVE_RESOURCE_LIMITS = False

SHELL_CPU_SECONDS = 5
SHELL_MEMORY_BYTES = 512 * 1024 * 1024


def _restricted_preexec():
    resource.setrlimit(resource.RLIMIT_CPU, (SHELL_CPU_SECONDS, SHELL_CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (SHELL_MEMORY_BYTES, SHELL_MEMORY_BYTES))


def _restricted_env():
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}


def run_shell_command(command):
    # Interactive mode only, in practice -- TOOL_POLICY_CI blocks this tool
    # outright, so in CI mode dispatch_tool_call never reaches this body.
    # Kept identical to Chapter 11's hardened version for the interactive
    # case: denylist first, then real resource limits and a stripped
    # environment.
    reason = _blocked_reason(command)
    if reason:
        return f"error: command blocked ({reason}): {command!r}"
    kwargs = dict(shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=15, env=_restricted_env())
    if _HAVE_RESOURCE_LIMITS:
        kwargs["preexec_fn"] = _restricted_preexec
    try:
        result = subprocess.run(command, **kwargs)
    except subprocess.TimeoutExpired:
        return f"error: command timed out after 15s: {command!r}"
    return json.dumps({"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode})


# ---------------------------------------------------------------------------
# run_tests -- a NEW tool this chapter adds, deliberately narrow. Chapter
# 11's least-privilege retrospective already named the fix for
# run_shell_command's "structurally over-privileged by nature" problem:
# replace one broad capability with several named, bounded ones. This is
# that fix, applied to exactly the one CI use case that needs it -- running
# the test suite is common enough, and bounded enough (it takes no
# arguments at all; there is nothing to inject), to deserve its own tool
# rather than routing through run_shell_command's much larger attack
# surface. It still gets the same resource-limit hardening.
#
# Uses `unittest` (Python's own standard library) rather than pytest, on
# purpose: this file needs to run cleanly in THIS course's own CI, which
# has no reason to have a third-party test runner installed just to
# demonstrate a tool that could call any test runner in a real project.
# ---------------------------------------------------------------------------
TEST_COMMAND = [sys.executable, "-m", "unittest", "test_app", "-v"]


def run_tests():
    kwargs = dict(cwd=WORKSPACE, capture_output=True, text=True, timeout=30, env=_restricted_env())
    if _HAVE_RESOURCE_LIMITS:
        kwargs["preexec_fn"] = _restricted_preexec
    try:
        result = subprocess.run(TEST_COMMAND, **kwargs)
    except FileNotFoundError:
        return "error: could not launch the test runner in this environment"
    except subprocess.TimeoutExpired:
        return "error: test run timed out after 30s"
    return json.dumps(
        {"stdout": result.stdout[-4000:], "stderr": result.stderr[-2000:], "exit_code": result.returncode}
    )


def git_status():
    result = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE, capture_output=True, text=True, timeout=15)
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


# ---------------------------------------------------------------------------
# Protected-branch scoping -- the second CI-specific scope check, alongside
# CI-scratch write scoping above. Same shape: a human-decided boundary,
# checked in code, that substitutes for the confirmation CI cannot give.
# ---------------------------------------------------------------------------
PROTECTED_BRANCHES = {"main", "master"}


def _current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=WORKSPACE, capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_commit(message):
    """Unchanged signature from Chapter 11 -- still no `confirm` parameter
    at all. TODO 3: before the real commit runs, if CI_MODE is True, look
    up the current branch via _current_branch() (already provided). If it
    couldn't be determined (returns None), or if it's in
    PROTECTED_BRANCHES, return a clean "error: ..." string and do NOT
    commit. This is what lets git_commit be ALLOWED in TOOL_POLICY_CI
    without reopening Chapter 8's flaw -- the thing that decides whether
    the commit is safe (which branch it lands on) is read from git
    itself, not from any argument the model provided."""
    result = subprocess.run(["git", "commit", "-m", message], cwd=WORKSPACE, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return f"error: git commit failed: {result.stderr.strip()}"
    return result.stdout.strip() or f"committed: {message!r}"


def send_email(to, subject, body):
    return "error: this should never execute -- send_email is BLOCKED by policy in every mode"


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "list_directory": list_directory,
    "run_shell_command": run_shell_command,
    "run_tests": run_tests,
    "git_status": git_status,
    "git_diff": git_diff,
    "git_commit": git_commit,
    "send_email": send_email,
}


# ---------------------------------------------------------------------------
# TWO policies, not one loosened at runtime. Both are plain dicts in this
# file -- reviewed the same way any other code change in this repo is
# reviewed, via a real pull request a human reads before it merges. Neither
# the model nor any script running in CI can add, remove, or promote a
# single entry in either dict; the only thing a CI run can do is select
# WHICH of these two already-decided policies applies, via CI_MODE, before
# any tool call happens.
# ---------------------------------------------------------------------------
ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"

# Chapter 11's exact interactive policy, unchanged.
TOOL_POLICY = {
    "read_file": ALLOWED,
    "list_directory": ALLOWED,
    "git_status": ALLOWED,
    "git_diff": ALLOWED,
    "run_tests": ALLOWED,
    "write_file": REQUIRES_CONFIRMATION,
    "edit_file": REQUIRES_CONFIRMATION,
    "run_shell_command": REQUIRES_CONFIRMATION,
    "git_commit": REQUIRES_CONFIRMATION,
    "send_email": BLOCKED,
}

# TODO 2: build TOOL_POLICY_CI, this chapter's new policy for unattended
# CI runs. Same shape as TOOL_POLICY above -- a dict from tool name to
# ALLOWED / REQUIRES_CONFIRMATION / BLOCKED. Fill in every tool:
#
#   read_file, list_directory, git_status, git_diff, run_tests -> ALLOWED
#       (all read-only or narrowly bounded; nothing here changes between
#       interactive and CI mode)
#   write_file -> ALLOWED (relies on TODO 1's scratch-scope check inside
#       write_file() itself -- the tier alone is not what makes this safe)
#   git_commit -> ALLOWED (relies on TODO 3's protected-branch check
#       inside git_commit() itself, same idea)
#   edit_file -> BLOCKED (no narrow scope exists for an in-place edit of
#       a tracked file with nobody watching)
#   run_shell_command -> BLOCKED (no narrow scope exists for an arbitrary
#       command either -- explicit BLOCKED, not a relied-upon
#       EOFError-triggered auto-deny)
#   send_email -> BLOCKED (unchanged from TOOL_POLICY -- there was never
#       a confirmation step here to lose)
TOOL_POLICY_CI = {
    # TODO 2: fill this in
}


def active_policy():
    """The ONE place CI_MODE actually branches policy selection. Everything
    downstream (check_permission, dispatch_tool_call) is identical in both
    modes -- it's the SAME code path, just consulting a different,
    already-decided dict. This mirrors Chapter 11's own point about
    _safe_path vs TOOL_POLICY: two boundaries, checked independently, never
    merged into one 'harness says no' blob that would be harder to reason
    about."""
    return TOOL_POLICY_CI if CI_MODE else TOOL_POLICY


def check_permission(name):
    """Unchanged shape from Chapter 11: any tool NOT in the active policy
    defaults to BLOCKED, not ALLOWED -- fail closed, in both modes."""
    return active_policy().get(name, BLOCKED)


def confirm_with_human(tool_name, args):
    """UNCHANGED from Chapter 11, verbatim -- this is deliberate, not an
    oversight. This chapter does NOT touch confirm_with_human at all. In
    interactive mode it behaves exactly as Chapter 11 built it. In CI
    mode, TOOL_POLICY_CI simply routes every write-capable tool to either
    ALLOWED (with its own scope check) or BLOCKED -- so this function is
    never even called during a CI run, because nothing is
    REQUIRES_CONFIRMATION in TOOL_POLICY_CI. That's the point: the WRONG
    fix would have been editing THIS function to auto-answer "yes" when
    CI_MODE is set. The RIGHT fix, built above, makes that edit
    unnecessary -- CI mode routes around confirm_with_human entirely
    rather than defeating it."""
    summary = json.dumps(args)
    prompt = f"[confirmation required] allow {tool_name}({summary})? [y/N]: "
    try:
        answer = input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("[no human available to confirm on stdin -- denying by default]")
        return False
    return answer.strip().lower() in ("y", "yes")


def dispatch_tool_call(tc):
    """Identical control flow to Chapter 11's version. The only change
    anywhere in this function, versus Chapter 11, is that check_permission
    now consults active_policy() instead of a single hardcoded dict --
    everything else, including the ordering (parse args, check unknown
    tool, check policy tier, confirm if required, only then call the real
    function), is unchanged."""
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

    try:
        return TOOL_FUNCTIONS[name](**args)
    except KeyError as e:
        return f"error: missing required argument {e} for {name}"
    except Exception as e:
        return f"error: tool {name} failed: {e}"


def run_agent(task, client):
    """The plan/act/observe/repeat loop -- unchanged from Chapter 7 in
    shape, but the step cap and a wall-clock budget both now depend on
    CI_MODE. A run that thrashes interactively wastes a learner's own
    patience; a run that thrashes in CI wastes real, metered CI minutes
    and blocks a real PR -- Chapter 5's failure modes get a concrete new
    cost here, not just a new setting."""
    os.makedirs(WORKSPACE, exist_ok=True)
    max_steps = MAX_STEPS_CI if CI_MODE else MAX_STEPS_INTERACTIVE
    # TODO 4: if CI_MODE is True, compute a deadline
    # (time.monotonic() + CI_WALL_CLOCK_BUDGET_SECONDS); otherwise leave it
    # None. Store it in a variable named `deadline` -- the loop below
    # already checks it.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    for step in range(1, max_steps + 1):
        # TODO 4 (continued): before each step, if `deadline` is set and
        # time.monotonic() has passed it, print a clear message and
        # `return messages` instead of continuing -- do not let the loop
        # keep calling the model past its CI wall-clock budget.

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

    print(f"[step cap reached after {max_steps} steps without a clean stop -- CI_MODE={CI_MODE}]")
    return messages


class _FakeToolCall:
    class _Fn:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments

    def __init__(self, name, arguments_dict):
        self.function = self._Fn(name, json.dumps(arguments_dict))


def _call(name, args):
    return dispatch_tool_call(_FakeToolCall(name, args))


# ---------------------------------------------------------------------------
# Two use cases this chapter covers, both demonstrated live below with no
# model needed: (1) a PR review bot -- entirely read-only, needs zero
# policy changes at all, fits under either policy unchanged; (2) a CI
# troubleshooting agent -- needs real write capability, is where
# TOOL_POLICY_CI's scoping actually earns its keep.
# ---------------------------------------------------------------------------
def demo_pr_review_bot(diff_text):
    """Reads a diff and produces a review comment. Entirely read-only:
    every tool this scenario needs (read_file, git_diff) is ALLOWED under
    BOTH policies unchanged -- a PR review bot needed no new mechanism at
    all, which is the point the lesson makes about this being the easy
    half of "putting an agent in CI." No git_commit, no write_file, no
    policy tension whatsoever."""
    print("=== PR review bot: read-only, works under either policy unchanged ===")
    lines = diff_text.splitlines()
    added = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
    comment = (
        f"Automated review: this diff adds {added} line(s) and removes "
        f"{removed} line(s). No destructive shell commands or file writes "
        "were needed to produce this comment -- read_file/git_diff cover "
        "the entire task, so this scenario never touches TOOL_POLICY_CI at all."
    )
    print(comment)
    return comment


@contextlib.contextmanager
def _temp_git_workspace():
    """Points the module-level WORKSPACE at a throwaway directory OUTSIDE
    this repo entirely (a real `tempfile.mkdtemp()`, not the persistent
    `project/workspace/` folder Chapter 11 used) and cleans it up
    afterward. This matters specifically because this scenario runs a
    real `git init` -- doing that inside this course's own tracked
    `project/workspace/` would leave a real nested git repository sitting
    inside this repo's own working tree, which is exactly the kind of
    side effect the task briefing for this chapter says this file must
    not have. Everything this function touches is deleted before it
    returns, real side effects fully contained to a directory the OS
    already considered temporary."""
    global WORKSPACE
    previous = WORKSPACE
    WORKSPACE = tempfile.mkdtemp(prefix="acafe-ch12-ci-")
    try:
        yield WORKSPACE
    finally:
        shutil.rmtree(WORKSPACE, ignore_errors=True)
        WORKSPACE = previous


def _init_scratch_repo():
    """Builds a small, disposable git repo with a deliberately failing
    test -- entirely inside whatever WORKSPACE currently points at (a
    temp directory during the CI-mode demo, via `_temp_git_workspace()`
    above), never touching this course repo's real history."""
    if os.path.exists(WORKSPACE):
        shutil.rmtree(WORKSPACE)
    os.makedirs(WORKSPACE)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "config", "user.email", "ci-demo@example.com"], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "config", "user.name", "CI Demo"], cwd=WORKSPACE, check=True)

    with open(os.path.join(WORKSPACE, "app.py"), "w") as f:
        f.write("def add(a, b):\n    return a - b  # bug: should be a + b\n")
    with open(os.path.join(WORKSPACE, "test_app.py"), "w") as f:
        f.write(
            "import unittest\nfrom app import add\n\n"
            "class TestAdd(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n    unittest.main()\n"
        )
    subprocess.run(["git", "add", "."], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial commit with a bug"], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "checkout", "-q", "-b", "ci/auto-fix"], cwd=WORKSPACE, check=True)


def demo_ci_mode():
    """The CI troubleshooting agent, driven through scripted calls (no
    live model needed) against TOOL_POLICY_CI, on a real disposable repo
    with a real failing test. This is the load-bearing demo in this
    chapter, the same role demo_permission_layer() played in Chapter 11:
    it proves the CI-specific scoping actually holds, not just that it
    reads correctly."""
    global CI_MODE
    previous = CI_MODE
    CI_MODE = True
    try:
        with _temp_git_workspace():
            _init_scratch_repo()

            print("\n=== 1. run_tests (ALLOWED in CI) -- runs the real, failing test ===")
            print(_call("run_tests", {}))

            print("\n=== 2. write_file inside ci-scratch/ (ALLOWED -- inside scope) ===")
            print(_call("write_file", {
                "path": "ci-scratch/summary.md",
                "content": "run_tests failed: test_add expected 5, got -1. Likely a sign flip in app.add.\n",
            }))

            print("\n=== 3. write_file outside ci-scratch/ (ALLOWED tier, but scope-refused) ===")
            print(_call("write_file", {"path": "app.py", "content": "def add(a, b):\n    return a + b\n"}))

            print("\n=== 4. edit_file (BLOCKED outright in CI mode, no prompt at all) ===")
            print(_call("edit_file", {"path": "app.py", "find": "a - b", "replace": "a + b"}))

            print("\n=== 5. run_shell_command (BLOCKED outright in CI mode -- no narrow scope exists) ===")
            print(_call("run_shell_command", {"command": "echo hi"}))

            print("\n=== 6. git_commit on a scratch branch (ALLOWED -- not a protected branch) ===")
            # check=False deliberately: if write_file was refused (e.g. an
            # unfinished TODO 1), there's nothing new to stage -- `git add`
            # on a nonexistent path would otherwise raise and crash this
            # whole demo instead of letting the remaining scenarios still
            # run and show their own outcomes.
            subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, check=False)
            print(_call("git_commit", {"message": "ci: add automated failure summary"}))

            print("\n=== 7. git_commit after checking out main (refused -- protected branch) ===")
            subprocess.run(["git", "checkout", "-q", "main"], cwd=WORKSPACE, check=True)
            with open(os.path.join(WORKSPACE, "ci-scratch-oops.txt"), "w") as f:
                f.write("irrelevant\n")
            subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, check=False)
            print(_call("git_commit", {"message": "should be refused: on main"}))

            print("\n=== 8. send_email (BLOCKED in every mode) ===")
            print(_call("send_email", {"to": "oncall@example.com", "subject": "build failed", "body": "..."}))
    finally:
        CI_MODE = previous


def demo_interactive_mode():
    """Chapter 11's exact demo, unchanged, run here to show the same
    policy still governs a normal (non-CI) run of this exact file --
    nothing about adding TOOL_POLICY_CI changed TOOL_POLICY's own
    behavior at all. Explicitly forces CI_MODE to False for the duration
    of this demo -- regardless of how THIS script itself was invoked
    (e.g. under `ACAFE_CI_MODE=1`, to run every demo in one process for
    this course's own CI) -- so this demo always shows the interactive
    policy, and demo_ci_mode() below always shows the CI policy,
    independent of the real environment variable the harness read once
    at import time."""
    global CI_MODE
    previous = CI_MODE
    CI_MODE = False
    try:
        print("=== Interactive mode (CI_MODE=False): Chapter 11's exact policy, unchanged ===")
        os.makedirs(WORKSPACE, exist_ok=True)
        with open(os.path.join(WORKSPACE, "demo.txt"), "w") as f:
            f.write("original content\n")

        print(_call("read_file", {"path": "demo.txt"}))
        print(_call("write_file", {"path": "demo.txt", "content": "changed\n"}))
        print(_call("send_email", {"to": "a@example.com", "subject": "hi", "body": "test"}))
    finally:
        CI_MODE = previous


def main():
    global CI_MODE
    print(f"CI_MODE = {CI_MODE} (from ACAFE_CI_MODE={os.environ.get('ACAFE_CI_MODE')!r})\n")

    demo_pr_review_bot(
        "--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def add(a, b):\n-    return a - b\n+    return a + b\n"
    )
    demo_interactive_mode()
    demo_ci_mode()

    try:
        from openai import OpenAI
    except ImportError:
        print("\nThe openai package isn't installed. Run: pip install openai")
        print("(every demo above already ran and needed no live model)")
        sys.exit(0)

    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama", timeout=8.0)
    task = "Run the test suite, summarize why it's failing, and write that summary to ci-scratch/summary.md."
    print("\n=== Attempting a live agent run against Ollama, in CI mode (may be skipped if unreachable) ===")
    previous_ci_mode = CI_MODE
    CI_MODE = True
    try:
        with _temp_git_workspace():
            _init_scratch_repo()
            run_agent(task, client)
    except Exception as e:
        message = str(e).lower()
        if "connect" in message or "connection" in message or "timeout" in message or "timed out" in message:
            print(
                "Could not reach a local Ollama server at http://localhost:11434 (or it "
                "didn't respond in time) -- install Ollama (https://ollama.com), run "
                "`ollama pull llama3.2`, and make sure `ollama serve` is running, then try again. "
                "Every demo above already ran and needed no live model."
            )
            sys.exit(0)
        raise
    finally:
        CI_MODE = previous_ci_mode


if __name__ == "__main__":
    main()
