"""
Chapter 13 Capstone Project: A CI Agent Policy for a Regulated Org -- Starter

Read `solution.py`'s module docstring first -- it explains the scenario
(Meridian Ledger, a fictional payments-infrastructure company under
PCI-DSS Level 1 and SOX Section 404) in full. This file is that same
structure with three connected TODOs removed, matching Chapters 11-12's
lab pattern: the interesting logic lives in a place the model never sees
and cannot influence, and your job is filling in exactly that logic.

Everything else in this file (the policy dicts, git plumbing, audit-log
writer, demo scaffolding) is provided as-is, unchanged from `solution.py`.

Run it once before touching anything, to see what "not yet implemented"
looks like:

    python3 starter.py

Then fill in the three TODOs and re-run until your output matches
`solution.py`'s.
"""
import contextlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"

CI_MODE = os.environ.get("ACAFE_CI_MODE") == "1"

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

TOOL_POLICY_CI = {
    "read_file": ALLOWED,
    "list_directory": ALLOWED,
    "git_status": ALLOWED,
    "git_diff": ALLOWED,
    "run_tests": ALLOWED,
    "write_file": ALLOWED,
    "edit_file": BLOCKED,
    "run_shell_command": BLOCKED,
    "git_commit": ALLOWED,
    "send_email": BLOCKED,
}


def active_policy():
    return TOOL_POLICY_CI if CI_MODE else TOOL_POLICY


def check_permission(name):
    return active_policy().get(name, BLOCKED)


CI_SCRATCH_PREFIX = "ci-scratch/"


def _in_ci_scratch(path):
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.startswith(CI_SCRATCH_PREFIX)


CDE_PATH_PATTERNS = ("payments/card_intake/", "payments/tokenization/", "vendor/psp_adapter/")
GL_PATH_PATTERNS = ("ledger/gl_posting/", "ledger/reconciliation/")


def regulated_category(path):
    """TODO 1: classify `path` as "CDE" (cardholder-data-environment
    patterns), "GL" (general-ledger / SOX-ICFR-scope patterns), or None
    (neither). Use SUBSTRING containment against CDE_PATH_PATTERNS and
    GL_PATH_PATTERNS, not a leading-prefix match -- a regulated pattern
    nested under ci-scratch/ (e.g. "ci-scratch/payments/card_intake/x.txt")
    must still be caught. Normalize the path the same way
    `_in_ci_scratch` does (backslashes to forward slashes, strip a
    literal leading "./") before checking.
    """
    raise NotImplementedError("TODO 1: implement regulated_category")


PAN_PATTERN = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")


def redact_card_data(text):
    return PAN_PATTERN.sub("[REDACTED-PAN]", text)


def get_actor():
    return os.environ.get("MERIDIAN_TRIGGERED_BY")


AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ci-audit-log.jsonl")


def audit_log(event):
    record = dict(event)
    record["ts"] = time.time()
    record["ci_mode"] = CI_MODE
    if "args" in record:
        record["args"] = redact_card_data(json.dumps(record["args"]))
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


WORKSPACE = None


def _safe_path(path):
    full = os.path.abspath(os.path.join(WORKSPACE, path))
    if not full.startswith(os.path.abspath(WORKSPACE) + os.sep) and full != os.path.abspath(WORKSPACE):
        raise ValueError(f"path escapes workspace: {path}")
    return full


def write_file(path, content):
    """TODO 2: in CI mode, refuse the write in two independent cases,
    checked in this order:
      (a) `regulated_category(path)` is not None -- refuse unconditionally,
          regardless of ci-scratch/ scoping. Return a clear error string
          naming the category and explaining a compliance-designated human
          must make this change interactively, outside CI.
      (b) otherwise, if the path is not inside CI_SCRATCH_PREFIX (use
          `_in_ci_scratch`), refuse with Chapter 12's original scratch-scope
          error.
    If neither case applies, perform the real write (see `solution.py`
    for the exact file-writing code, unchanged from Chapter 12).
    """
    raise NotImplementedError("TODO 2: implement write_file's CI-mode checks")


PROTECTED_BRANCHES = {"main", "master"}


def _current_branch():
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=WORKSPACE, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _staged_files():
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=WORKSPACE, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def git_commit(message, actor=None):
    """TODO 3: in CI mode, refuse the commit in any of these three cases,
    checked in this order:
      (a) branch is None or in PROTECTED_BRANCHES (Chapter 12's check,
          unchanged)
      (b) any file returned by `_staged_files()` has a non-None
          `regulated_category()` -- refuse, naming every regulated file
          and its category
      (c) `actor` is falsy -- refuse, explaining SOX individual
          accountability requires a real triggering identity, not a
          shared CI service account
    If none of those apply and CI_MODE is True, append two trailers to
    `message` before committing: an `Agent-Run-Id` line (from the
    `GITHUB_RUN_ID` env var, defaulting to "local-demo") and a
    `Triggered-By` line (the actor). Then perform the real commit (see
    `solution.py` for the unchanged subprocess call).
    """
    raise NotImplementedError("TODO 3: implement git_commit's CI-mode checks")


def dispatch(tool_name, args):
    tier = check_permission(tool_name)
    actor = get_actor()
    audit_log({"actor": actor, "tool": tool_name, "args": args, "tier": tier})

    if tier == BLOCKED:
        return f"error: {tool_name} is blocked by policy"

    if tool_name == "write_file":
        return write_file(**args)
    if tool_name == "git_commit":
        return git_commit(actor=actor, **args)
    raise ValueError(f"demo dispatch does not implement {tool_name!r}")


@contextlib.contextmanager
def _temp_git_workspace():
    global WORKSPACE
    previous = WORKSPACE
    WORKSPACE = tempfile.mkdtemp(prefix="acafe-ch13-")
    try:
        yield WORKSPACE
    finally:
        shutil.rmtree(WORKSPACE, ignore_errors=True)
        WORKSPACE = previous


def _init_scratch_repo():
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "config", "user.email", "ci-demo@example.com"], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "config", "user.name", "CI Demo"], cwd=WORKSPACE, check=True)
    with open(os.path.join(WORKSPACE, "README.md"), "w") as f:
        f.write("Meridian Ledger demo workspace\n")
    subprocess.run(["git", "add", "."], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial commit"], cwd=WORKSPACE, check=True)
    subprocess.run(["git", "checkout", "-q", "-b", "ci/auto-fix"], cwd=WORKSPACE, check=True)


def demo():
    global CI_MODE
    previous_mode = CI_MODE
    CI_MODE = True
    if os.path.exists(AUDIT_LOG_PATH):
        os.remove(AUDIT_LOG_PATH)
    try:
        with _temp_git_workspace():
            _init_scratch_repo()

            print("=== 1. write_file inside ci-scratch/, non-regulated (ALLOWED) ===")
            print(dispatch("write_file", {"path": "ci-scratch/summary.md", "content": "build failure summary\n"}))

            print("\n=== 2. write_file inside ci-scratch/, but path matches CDE pattern (still refused) ===")
            print(dispatch("write_file", {"path": "ci-scratch/payments/card_intake/notes.txt", "content": "..."}))

            print("\n=== 3. write_file directly to a GL path (refused, regulated) ===")
            print(dispatch("write_file", {"path": "ledger/gl_posting/adjust.py", "content": "..."}))

            print("\n=== 4. commit on scratch branch, non-regulated file, no actor set (refused: no attribution) ===")
            os.environ.pop("MERIDIAN_TRIGGERED_BY", None)
            subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, check=False)
            print(dispatch("git_commit", {"message": "ci: add failure summary"}))

            print("\n=== 5. same commit, with an actor attached (ALLOWED) ===")
            os.environ["MERIDIAN_TRIGGERED_BY"] = "alex.chen@meridianledger.example (PR #4821 author)"
            print(dispatch("git_commit", {"message": "ci: add failure summary"}))
            log = subprocess.run(["git", "log", "-1", "--format=%B"], cwd=WORKSPACE, capture_output=True, text=True)
            print("commit message trailers:\n" + log.stdout.strip())

            print("\n=== 6. attempted commit that stages a CDE-path file (refused, regardless of branch/actor) ===")
            os.makedirs(os.path.join(WORKSPACE, "payments", "card_intake"), exist_ok=True)
            with open(os.path.join(WORKSPACE, "payments", "card_intake", "parse.py"), "w") as f:
                f.write("# would touch cardholder data handling\n")
            subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, check=False)
            print(dispatch("git_commit", {"message": "ci: tweak card intake parsing"}))
    finally:
        CI_MODE = previous_mode
        os.environ.pop("MERIDIAN_TRIGGERED_BY", None)

    print("\n=== 7. audit log, read back ===")
    with open(AUDIT_LOG_PATH) as f:
        for line in f:
            entry = json.loads(line)
            print(f"  actor={entry['actor']!r:55} tool={entry['tool']:12} tier={entry['tier']}")
    os.remove(AUDIT_LOG_PATH)


def main():
    print(f"CI_MODE = {CI_MODE} (Meridian Ledger CI policy demo)\n")
    demo()


if __name__ == "__main__":
    main()
