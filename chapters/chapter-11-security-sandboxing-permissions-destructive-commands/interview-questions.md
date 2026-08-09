# Interview Questions: Security, Sandboxing, Permissions, Destructive Commands

Plain-markdown mirror of `interview-questions.html`. Grouped by level.
Each includes a strong answer, a red flag, and a follow-up.

## 1. (Beginner) Why doesn't a `confirm=True` argument on a tool like `git_commit` actually provide a real permission check?

**Strong answer:** A tool call, since this course's agent loop was
built, is entirely produced by the model — the function name and every
argument, including a `confirm` field, are values the model itself
chose to write. There is nothing stopping the model from simply
including `confirm: true` in the exact same JSON blob it uses to call
the tool in the first place. A permission check has to be based on
information the entity being checked can't alter — putting it inside
the checked entity's own request defeats the point entirely.

**Red flag:** Thinks a confirm flag is "mostly fine" because a
well-behaved model probably wouldn't set it carelessly — misses that
the check needs to hold even when the model is wrong, confused, or (in
an adversarial framing) deliberately manipulated, not just when it's
behaving typically.

**Follow-up:** "Where in the code does the REAL confirmation check
live instead, and what makes that location trustworthy in a way the
tool argument wasn't?"

**What this proves:** Understands the actual mechanism of why the flag
fails, not just that it "feels unsafe."

## 2. (Beginner) What does it mean for a permission check to "fail closed," and why does `check_permission()` default an unclassified tool to BLOCKED rather than ALLOWED?

**Strong answer:** "Fail closed" means that when something goes wrong
or is ambiguous — here, a tool nobody explicitly classified in the
policy — the safe outcome (refuse) is what happens automatically,
rather than requiring someone to have remembered to set it up
correctly. Defaulting to BLOCKED means a developer who adds a new tool
and forgets to add a policy entry for it gets a tool that doesn't run
(annoying, but safe) instead of a tool that runs completely unguarded
the first time the model calls it (a real, silent security gap). The
cost of the mistake is contained by the default, not by hoping the
mistake never happens.

**Red flag:** Can define "fail closed" abstractly but can't explain the
concrete consequence of getting the default backward in this specific
code.

**Follow-up:** "What's the equivalent 'fail open' mistake someone could
make in this exact function, and what would it look like in code?"

**What this proves:** Connects a security principle to its specific,
concrete implementation, not just the vocabulary.

## 3. (Intermediate) `_safe_path()` (Chapter 7) and `TOOL_POLICY` (this chapter) are both harness-enforced checks the model can't override. Why does this agent need both, instead of just one general-purpose "harness says no" mechanism?

**Strong answer:** They answer genuinely different questions and catch
genuinely different mistakes. `_safe_path()` asks "is this specific
path even allowed to be touched at all" — independent of which tool is
asking. `TOOL_POLICY` asks "does this specific TOOL need a human's
approval before it runs at all" — independent of which path or
argument it's being called with. A call to `write_file("notes.txt",
...)` passes `_safe_path()` easily (the path is inside the workspace)
but should still require confirmation, because the risk of writing is
about changing state, not about where the state happens to live.
Collapsing them into one check would either make every read subject to
confirmation friction it doesn't need, or make every write skip a
check it does need, depending on which check "won."

**Red flag:** Treats the two mechanisms as redundant or
interchangeable, or can't name a concrete case where a call passes one
and needs the other.

**Follow-up:** "Can you think of a tool call that would FAIL
`_safe_path()` but be ALLOWED under TOOL_POLICY, or vice versa?"

**What this proves:** Understands that layered security mechanisms are
deliberate, purpose-specific checks, not redundant belt-and-suspenders
for the same risk.

## 4. (Intermediate) A teammate proposes replacing this chapter's `resource.setrlimit`-based hardening with the claim "this makes run_shell_command sandboxed." What's your response?

**Strong answer:** That's overselling what it actually does.
`resource.setrlimit` gives real, kernel-enforced CPU and memory caps on
the subprocess, and a restricted environment hides the host's real
secrets from it — both genuine, verifiable protections. But it gives
the command no separate filesystem view (it can still write anywhere
the OS and `_safe_path()`'s boundary allow), no network isolation, and
no process namespace isolation. A real sandbox — where even an
unrestricted `rm -rf /` only destroys a disposable container image —
needs OS or container-runtime primitives (Linux namespaces, cgroups,
Docker, or a VM) underneath the Python process, which pure Python code
cannot construct for itself. Calling resource limits "sandboxing" would
mislead anyone reading the code about what's actually covered.

**Red flag:** Either dismisses resource limits as worthless because
they're "not a real sandbox," or accepts the "sandboxed" framing
without pushing back on the specific gaps (filesystem, network, process
namespace).

**Follow-up:** "If you had access to Docker in this environment, what's
the smallest change you'd make to actually close the
filesystem-isolation gap?"

**What this proves:** Can precisely scope a security claim instead of
accepting or rejecting it wholesale — exactly the "don't oversell"
discipline this course has applied to every prior mitigation (the
denylist, MCP's trade-offs).

## 5. (Senior) Walk through exactly what happens, step by step, when this chapter's agent runs as an unattended cron job and the model calls `write_file`.

**Strong answer:** `dispatch_tool_call` parses the arguments and finds
`write_file` in `TOOL_FUNCTIONS`. It looks up the tool's tier via
`check_permission("write_file")`, which returns
`REQUIRES_CONFIRMATION`. That triggers `confirm_with_human("write_file",
args)`, which prints a prompt and calls `input()`. Because this is a
cron job with stdin closed (or redirected from `/dev/null`), `input()`
immediately raises `EOFError`. The `except (EOFError,
KeyboardInterrupt)` block catches it, prints a message noting no human
was available, and returns `False`. Back in `dispatch_tool_call`, that
`False` means the function returns an "error: write_file requires human
confirmation, which was not granted" string WITHOUT ever calling the
real `write_file` function — the model sees that error as a tool result
and has to continue the loop without the file ever having been
written.

**Red flag:** Says the agent "hangs" or "crashes" in this scenario,
missing that the EOFError handling specifically prevents both of those
outcomes — or skips the mechanical detail of WHERE in the call chain
the decision actually happens.

**Follow-up:** "What would you need to change about this design if you
actually wanted SOME confirmations to be auto-approved in an unattended
CI context, without reopening the 'the model sets its own flag'
problem?"

**What this proves:** Can trace a multi-function control-flow path
precisely, not just describe the intended behavior at a high level.

## 6. (Senior) Design a threat-model argument for why `send_email` should be BLOCKED outright rather than REQUIRES_CONFIRMATION, when a human confirming it would seem to provide equivalent protection to git_commit's confirmation.

**Strong answer:** The two tools differ in a way that matters for
confirmation-based defenses specifically: git_commit's blast radius is
fully contained and inspectable BEFORE approval — a human can run
git_diff first and see exactly what they're approving, and even a bad
commit is locally reversible. send_email's effect is external,
immediate, and irreversible the moment it's approved — there's no
equivalent to "look at the diff first" for an email that's about to
leave the system, and a human under time pressure, asked to approve a
plausible-sounding "notify the on-call engineer" request, is exactly
the kind of rushed, pattern-matched "yes" that confirmation prompts are
vulnerable to. Because this agent has no legitimate task that requires
contacting an external party at all, removing the decision from the
runtime path entirely (BLOCKED) is safer than trusting every future
confirmation prompt to be given carefully, especially for an action a
human can't meaningfully undo after the fact.

**Red flag:** Argues that "more human oversight is always safer,"
missing that a confirmation prompt is only as protective as the
human's ability to actually evaluate what they're approving under real
conditions — for some actions, that ability is structurally limited
regardless of how carefully the prompt is worded.

**Follow-up:** "Is there ANY legitimate coding-agent task where an
email tool would be worth having at REQUIRES_CONFIRMATION instead of
BLOCKED? What would have to be true?"

**What this proves:** Reasons about WHY a tier is appropriate for a
specific tool's risk shape, rather than applying "more confirmation =
more safety" as a blanket rule.

## 7. (Architect) You're adapting this chapter's agent for a real, sensitive production codebase. Would you keep `run_shell_command` as a single general-purpose tool, or redesign it? Justify your answer with a concrete trade-off, not just a preference.

**Strong answer:** I'd replace it with several narrower, purpose-built
tools — `run_tests`, `run_linter`, `install_declared_dependency` — each
with its own policy tier, rather than keep one broad, gated capability.
The trade-off is real in both directions: a single `run_shell_command`
covers any task the denylist doesn't explicitly block, including tasks
nobody anticipated, at the cost of a genuinely large worst-case blast
radius per call (anything not on the denylist is fair game). Narrow,
named tools shrink the worst case per tool dramatically — `run_tests`
can realistically only run the test suite, full stop — at the direct
cost of covering fewer unanticipated situations, meaning the model (or
a human) has to explicitly add a new narrow tool every time a genuinely
new capability is needed, which is friction Chapter 7-8's
minimal-tool philosophy was originally built to avoid. For a real
production codebase, I'd accept that friction; the whole point of least
privilege is that the friction is the cost of the safety, not a bug in
the design.

**Red flag:** Picks a side without naming the concrete cost of that
choice, or claims the narrow-tools redesign has no downside at all.

**Follow-up:** "How would you decide, concretely, which shell
capabilities are common enough to deserve their own named tool versus
rare enough to leave uncovered entirely?"

**What this proves:** Architect-level judgment — makes a real design
trade-off explicit instead of treating "more granular is always
better" as a free win.

## 8. (Architect) A stakeholder asks: "We already have the denylist from Chapter 8 and the workspace boundary from Chapter 7 — why do we need a whole separate permission-scope system on top of that?" How do you respond?

**Strong answer:** Because the denylist and the workspace boundary
defend against two specific, narrow risks — a known-dangerous shell
PATTERN, and a path escaping a known BOUNDARY — and neither one answers
the question "should this tool, this specific capability, ever run
without a human deciding, regardless of what arguments it's called
with." `git_commit` is the clearest case: no denylist pattern applies
to it (committing isn't a dangerous string), and it operates entirely
inside the workspace (so `_safe_path()` has nothing to say about it) —
yet it's exactly the kind of action (real, permanent, discoverable by
every downstream consumer) that this course has argued since Chapter 3
deserves a human checkpoint before it becomes part of a project's real
history. The permission-scope layer is the piece that generalizes
"should a human decide this" into an explicit, auditable policy,
instead of leaving it as an implicit property that happens to fall out
of whichever narrower check gets checked first.

**Red flag:** Claims the denylist and workspace boundary are
"basically already doing this," without being able to name a real
action (like git_commit) that neither one meaningfully restricts.

**Follow-up:** "If budget only allowed building ONE of the three
mechanisms (workspace boundary, denylist, permission-scope layer),
which would you prioritize for a genuinely production agent, and why?"

**What this proves:** Can explain to a non-technical stakeholder not
just WHAT a new layer does, but WHY the existing layers, however real,
leave a specific gap this one closes.
