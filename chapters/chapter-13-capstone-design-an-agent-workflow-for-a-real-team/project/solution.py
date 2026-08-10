"""
Chapter 13 Capstone Project: A CI Agent Policy for a Regulated Org -- Worked Reference

This is `starter.py` with every TODO filled in. It is NOT a new agent
loop -- Chapters 7-9 already built that, and it doesn't change here.
This file's whole job is to show, in real code, what Chapters 11-12's
TOOL_POLICY / TOOL_POLICY_CI pattern has to become once "unattended
CI agent" meets "regulated engineering org." The lesson's design
document is the real capstone deliverable; this file is the one piece
of that design worth showing precisely in code, the same way Chapters
11-12 did for their own policy layers.

THE SCENARIO: Meridian Ledger, a fictional payments-infrastructure
company. It operates card-payment processing rails for mid-market
e-commerce merchants and a reconciliation/general-ledger product used
by its own (and merchants') finance teams. Two regulatory regimes
apply, and they constrain this design in different, concrete ways:

  - PCI-DSS Level 1 Service Provider: any code that touches cardholder
    data (PAN, CVV, track data) lives in a Cardholder Data Environment
    (CDE) that must be tightly access-controlled and fully audit-logged.
    A PAN leaking into a log line, or a masking routine silently
    breaking, is a reportable compliance event, not just a bug.
  - SOX Section 404 (Meridian Ledger is publicly traded; its ledger's
    output feeds audited financial statements): code that posts to the
    general ledger or drives reconciliation is "in scope" for internal
    controls over financial reporting (ICFR). A change to that logic
    needs individual, attributable accountability -- a SOX auditor has
    to be able to answer "who approved this change, and when" for any
    system in ICFR scope, not just "the CI bot did it."

WHAT THIS FILE ADDS ON TOP OF CHAPTER 12'S TOOL_POLICY_CI (unchanged
in shape, extended in content):

  1. REGULATED_PATH_PATTERNS -- a path classifier (CDE vs. GL vs.
     neither) that write_file() and git_commit() consult IN ADDITION
     to Chapter 12's ci-scratch/protected-branch checks. A regulated
     path is blocked even if it's nominally inside ci-scratch/ -- the
     regulated-path check is a HARD block that the scratch-prefix
     check cannot override, because "this write technically lands in
     the scratch area" was never the actual question a compliance
     reviewer would ask.
  2. Actor attribution -- git_commit() now takes a *required* `actor`
     argument in CI mode (never optional the way Chapter 12's was) and
     refuses to commit at all if no accountable human identity is
     available. This is the direct fix for SOX's individual-
     accountability requirement: a shared "ci-bot" identity commit is
     not attributable to a specific decision-maker.
  3. A structured, append-only audit log (`audit_log()`) -- every tool
     call this harness dispatches gets one JSON line: who triggered
     the run, what was called, what was decided, and why -- written
     BEFORE the tool call's own result is known, so even a call that
     crashes the process still leaves a record it was attempted.
  4. `redact_card_data()` -- a narrow, defense-in-depth scrub applied
     to anything written to the audit log, so the audit trail itself
     -- which is read by more people than the codebase is -- can never
     become a second place a PAN-shaped number leaks.

Run it:

    python3 solution.py                 # runs every demo, entirely offline

Nothing here needs Ollama or any live model -- like Chapters 11-12,
this chapter's actual subject is harness-side policy logic, fully
verifiable on its own.
"""
import contextlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

# ---------------------------------------------------------------------------
# Chapter 11-12's exact three-tier vocabulary, unchanged.
# ---------------------------------------------------------------------------
ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"

CI_MODE = os.environ.get("ACAFE_CI_MODE") == "1"

# Chapter 12's interactive policy, unchanged -- reproduced here so this file
# stays fully self-contained (this course's convention: each chapter's own
# files don't import a prior chapter's module).
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

# Chapter 12's CI policy, unchanged shape -- this is the org's baseline
# before any regulated-path reasoning is added on top of it.
TOOL_POLICY_CI = {
    "read_file": ALLOWED,
    "list_directory": ALLOWED,
    "git_status": ALLOWED,
    "git_diff": ALLOWED,
    "run_tests": ALLOWED,
    "write_file": ALLOWED,        # scoped -- see write_file() below
    "edit_file": BLOCKED,
    "run_shell_command": BLOCKED,
    "git_commit": ALLOWED,        # scoped -- see git_commit() below
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


# ---------------------------------------------------------------------------
# NEW in this chapter: regulated-path classification. This is the mechanism
# ADR-001 and ADR-002 (project/example-adrs/) both reference directly -- read
# those alongside this code, not instead of it.
#
# Deliberately conservative: these are SUBSTRING prefix matches over the
# repo-relative path, checked against the path as WRITTEN (write_file) or
# the set of paths actually staged (git_commit, via `git diff --cached
# --name-only`) -- never against anything the model merely SAYS about its
# own intent. A model claiming "this doesn't touch cardholder data" in its
# own text has no bearing on this check; only the actual path being touched
# does.
# ---------------------------------------------------------------------------
CDE_PATH_PATTERNS = ("payments/card_intake/", "payments/tokenization/", "vendor/psp_adapter/")
GL_PATH_PATTERNS = ("ledger/gl_posting/", "ledger/reconciliation/")


def regulated_category(path):
    """Returns "CDE", "GL", or None. A path is checked against both
    pattern sets independently -- a real repo layout could in principle
    have a path match neither, and this function is deliberately not
    exhaustive (see the lesson's honest-gaps section): it demonstrates the
    MECHANISM a real org would extend with its own actual directory
    layout, not a claim that these three prefixes are Meridian Ledger's
    complete regulated surface.
    """
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    # Substring containment, not just a leading-prefix match: a regulated
    # pattern anywhere in the path (e.g. nested under ci-scratch/, per the
    # demo below) still counts. This is deliberately broader than Chapter
    # 12's CI_SCRATCH_PREFIX check (a pure prefix match), because the thing
    # being guarded against here -- a regulated-code write landing
    # somewhere technically "in scope" -- doesn't stop mattering just
    # because a scratch directory sits in front of it.
    if any(p in normalized for p in CDE_PATH_PATTERNS):
        return "CDE"
    if any(p in normalized for p in GL_PATH_PATTERNS):
        return "GL"
    return None


PAN_PATTERN = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")


def redact_card_data(text):
    """A narrow, defense-in-depth scrub for anything written to the audit
    log -- 13-19 digit sequences (the PAN length range) get masked before
    they ever reach a log file. This is NOT the org's real PCI masking
    control (that lives in the payment-processing code itself, out of
    scope for this file) -- it exists so the AUDIT TRAIL, which is read by
    more people (compliance, auditors) than the codebase itself, cannot
    become a second, easier place for a card number to leak."""
    return PAN_PATTERN.sub("[REDACTED-PAN]", text)


# ---------------------------------------------------------------------------
# Actor attribution. `get_actor()` reads the identity of whoever actually
# triggered this CI run -- in a real GitHub Actions OIDC-based workflow this
# would come from the verified OIDC token claims / `github.actor`, not a
# plain environment variable a workflow step could fake; MERIDIAN_TRIGGERED_BY
# stands in for that here so this file stays runnable without a real OIDC
# setup. The point this chapter's design makes does NOT depend on which
# specific mechanism supplies the identity -- it depends on refusing to
# commit at all when no identity is available, which the code below enforces
# regardless of how `get_actor()` is implemented.
# ---------------------------------------------------------------------------
def get_actor():
    return os.environ.get("MERIDIAN_TRIGGERED_BY")


AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ci-audit-log.jsonl")


def audit_log(event):
    """Appends one JSON line per tool-call decision. Written BEFORE the
    tool call itself runs, so even a call that crashes the process still
    leaves a record that it was attempted -- an audit trail that only
    records successful completions is blind to exactly the runs a
    compliance reviewer would most want visibility into."""
    record = dict(event)
    record["ts"] = time.time()
    record["ci_mode"] = CI_MODE
    if "args" in record:
        record["args"] = redact_card_data(json.dumps(record["args"]))
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


WORKSPACE = None  # set per-demo via _temp_git_workspace()


def _safe_path(path):
    full = os.path.abspath(os.path.join(WORKSPACE, path))
    if not full.startswith(os.path.abspath(WORKSPACE) + os.sep) and full != os.path.abspath(WORKSPACE):
        raise ValueError(f"path escapes workspace: {path}")
    return full


def write_file(path, content):
    """CI-mode checks run in this order, on purpose: regulated-path FIRST,
    scratch-scope SECOND. A path that is both "inside ci-scratch/" and
    "matches a regulated pattern" (e.g. someone stages a scratch copy at
    ci-scratch/payments/card_intake/notes.txt) is still refused -- the
    regulated check is a hard block the scratch-prefix allowance cannot
    override. This ordering is itself a decision worth an ADR in a real
    submission: which check should win when two independent boundaries
    disagree."""
    if CI_MODE:
        category = regulated_category(path)
        if category is not None:
            return (
                f"error: {path!r} falls inside this org's {category} "
                "(regulated) path patterns -- write_file is refused "
                "unconditionally in CI mode, regardless of ci-scratch/ "
                "scoping. A compliance-designated human must make this "
                "change directly, interactively, outside CI."
            )
        if not _in_ci_scratch(path):
            return f"error: in CI mode, write_file may only write inside {CI_SCRATCH_PREFIX!r} -- refused: {path!r}."
    full = _safe_path(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    return f"wrote {len(content)} bytes to {path}"


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
    """Three independent checks in CI mode, each able to refuse the
    commit on its own: (1) not on a protected branch (Chapter 12's
    check, unchanged), (2) no staged file falls inside a regulated
    path -- checked against what git itself reports as staged, not
    against anything the model claims it changed, (3) a real actor
    identity is attached -- SOX's individual-accountability
    requirement, enforced as a hard refusal rather than a best-effort
    label. On success, the actor and the CI run's identifying
    information are written into the commit message itself as
    trailers, so `git log` alone -- without cross-referencing the
    audit log -- already answers "who triggered this.\""""
    if CI_MODE:
        branch = _current_branch()
        if branch is None or branch in PROTECTED_BRANCHES:
            return f"error: in CI mode, git_commit is refused on protected branch {branch!r}."

        staged = _staged_files()
        regulated_hits = [(f, regulated_category(f)) for f in staged if regulated_category(f)]
        if regulated_hits:
            names = ", ".join(f"{f} ({cat})" for f, cat in regulated_hits)
            return (
                f"error: refusing to commit -- staged changes touch regulated "
                f"paths: {names}. A commit touching CDE or GL-scoped code "
                "must be made and reviewed by a compliance-designated human, "
                "never by an unattended CI run, regardless of branch."
            )

        if not actor:
            return (
                "error: refusing to commit in CI mode with no attributable "
                "actor -- SOX individual-accountability requires every "
                "change to be traceable to a specific triggering human, not "
                "a shared CI service identity."
            )
        message = f"{message}\n\nAgent-Run-Id: {os.environ.get('GITHUB_RUN_ID', 'local-demo')}\nTriggered-By: {actor}"

    result = subprocess.run(["git", "commit", "-m", message], cwd=WORKSPACE, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return f"error: git commit failed: {result.stderr.strip()}"
    return result.stdout.strip() or f"committed: {message!r}"


def dispatch(tool_name, args):
    """A minimal stand-in for Chapter 7-12's `dispatch_tool_call` --
    checks policy tier, logs the decision, then calls the real function.
    Every call is audit-logged BEFORE the tool runs, capturing the
    decision the policy made, and the actor attached to this run."""
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
    print(
        "\nEvery scenario above ran entirely offline against a real, "
        "disposable git repo -- no live model needed. This is the same "
        "'the interesting code lives in the harness' discipline Chapters "
        "11-12 modeled; the design document (lesson.html, this chapter's "
        "ADRs and rubric) is the actual capstone deliverable."
    )


if __name__ == "__main__":
    main()
