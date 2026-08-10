"""
Chapter 13 Practice Bank: Six Tool Calls Under Meridian Ledger's CI Policy -- Worked Solution

`starter.py` with the TODO filled in. This script hands you six real
tool calls a CI troubleshooting agent might make, and prints what this
chapter's regulated-org policy decides for each one, with the specific
reason. Predict each outcome yourself before running it -- the
`practice/index.html` scenarios extend this same judgment to situations
these six calls don't cover.

Run:

    python3 solution.py
"""
import re

ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"

CDE_PATH_PATTERNS = ("payments/card_intake/", "payments/tokenization/", "vendor/psp_adapter/")
GL_PATH_PATTERNS = ("ledger/gl_posting/", "ledger/reconciliation/")

PROTECTED_BRANCHES = {"main", "master"}

TOOL_POLICY_CI = {
    "read_file": ALLOWED,
    "write_file": ALLOWED,
    "edit_file": BLOCKED,
    "run_shell_command": BLOCKED,
    "git_commit": ALLOWED,
}

PAN_PATTERN = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")


def classify_path(path):
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if any(p in normalized for p in CDE_PATH_PATTERNS):
        return "CDE"
    if any(p in normalized for p in GL_PATH_PATTERNS):
        return "GL"
    return None


def decide(call):
    """Given a scripted tool call dict (see `CALLS` below), returns a
    (decision, reason) tuple. Same five-step order every time: policy
    tier first, then tool-specific scope checks, exactly mirroring the
    real dispatch order in `project/solution.py` (tier check happens in
    `dispatch()`, before any tool-specific function body ever runs)."""
    tool = call["tool"]
    tier = TOOL_POLICY_CI.get(tool, BLOCKED)
    if tier == BLOCKED:
        return "BLOCKED", "not permitted by TOOL_POLICY_CI"

    if tool == "write_file":
        category = classify_path(call["path"])
        if category is not None:
            return "REFUSED", f"regulated path ({category})"
        normalized = call["path"][2:] if call["path"].startswith("./") else call["path"]
        if not normalized.startswith("ci-scratch/"):
            return "REFUSED", "outside ci-scratch/"
        return "ALLOWED", "passes every check"

    if tool == "git_commit":
        if call["branch"] in PROTECTED_BRANCHES:
            return "REFUSED", "protected branch"
        for p in call["staged_paths"]:
            category = classify_path(p)
            if category is not None:
                return "REFUSED", f"staged regulated path ({category})"
        if not call.get("actor"):
            return "REFUSED", "no attributable actor"
        return "ALLOWED", "passes every check"

    return "ALLOWED", "passes every check"


CALLS = [
    {"tool": "read_file", "path": "tools/ci_helper.py"},
    {"tool": "write_file", "path": "ci-scratch/diagnosis.md"},
    {"tool": "write_file", "path": "ci-scratch/payments/tokenization/scratch.txt"},
    {"tool": "write_file", "path": "app/internal_tools/flaky_retry.py"},
    {
        "tool": "git_commit",
        "branch": "ci/auto-fix-4821",
        "staged_paths": ["ci-scratch/diagnosis.md"],
        "actor": "priya.nair@meridianledger.example (PR #4821 author)",
    },
    {"tool": "git_commit", "branch": "main", "staged_paths": ["ci-scratch/diagnosis.md"], "actor": "priya.nair@meridianledger.example"},
]


def main():
    for i, call in enumerate(CALLS, 1):
        decision, reason = decide(call)
        print(f"{i}. {call['tool']}({ {k: v for k, v in call.items() if k != 'tool'} }) -> {decision} ({reason})")


if __name__ == "__main__":
    main()
