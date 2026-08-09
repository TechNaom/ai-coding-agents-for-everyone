# Interview Questions: Putting an Agent in CI

Plain-markdown mirror of `interview-questions.html`. Grouped by level.
Each includes a strong answer, a red flag, and a follow-up.

## 1. (Beginner) Chapter 11's agent, dropped into CI unchanged with no code changes at all, is described in this chapter as "safe but useless." Walk through exactly why both halves of that are true.

**Strong answer:** It's safe because `confirm_with_human()`'s
`except (EOFError, KeyboardInterrupt)` branch, built in Chapter 11,
denies by default the instant `input()` can't read from a real human —
CI's stdin is closed or redirected, so every `REQUIRES_CONFIRMATION`
tool call hits that branch and gets refused. Nothing dangerous happens.
It's useless because `write_file`, `edit_file`, `run_shell_command`, and
`git_commit` are ALL `REQUIRES_CONFIRMATION` in Chapter 11's policy —
so EVERY tool capable of doing real work gets denied the same way,
every single time, with nobody able to say yes. The agent can still
read files and run read-only git commands, but it cannot change a
single thing about the codebase, which makes it useless for any task
that isn't purely diagnostic.

**Red flag:** Says the agent "crashes" or "hangs" in CI — misses that
Chapter 11's fail-closed design specifically prevents both outcomes;
the agent runs to completion, just without accomplishing anything that
required a write.

**Follow-up:** "If you only fixed the 'useless' half without touching
anything about the 'safe' half, what would that fix have to look like?"

**What this proves:** Understands Chapter 11's exact mechanism well
enough to trace what happens when its assumptions (a human is present)
stop holding, not just that "CI is different somehow."

## 2. (Beginner) Why is auto-answering "yes" inside `confirm_with_human` when `CI_MODE` is set the WRONG fix, even though it would make the agent immediately useful in CI?

**Strong answer:** It recreates Chapter 8's exact flaw, one layer up.
Chapter 8's `git_commit(message, confirm=True)` failed because the
thing being checked (the model's own tool call) could set the value
that answered the check. Auto-answering "yes" inside
`confirm_with_human` when `CI_MODE` is set does the same thing
structurally: `CI_MODE` — set once, true for the entire run — becomes a
value that, once true, effectively pre-answers every single
confirmation for the rest of that run, regardless of WHICH tool or
WHICH arguments are being confirmed. It's not the model setting the
flag this time, but the check has still been reduced to "did someone
turn on the mode that always says yes," which is exactly as
unconditional and exactly as blind to the specific action being
approved as the original flaw was.

**Red flag:** Argues this is fine because "a human decided to turn on
CI_MODE, so it's still human-approved somewhere" — misses that the
human approved *the mode*, once, in the abstract, not any specific
action the agent later takes under that mode; that's a categorically
weaker guarantee than confirming an actual proposed action.

**Follow-up:** "What's the minimum change to this 'auto-yes' approach
that WOULD make it acceptable — and does that minimum change end up
looking like this chapter's actual `TOOL_POLICY_CI` design?"

**What this proves:** Can connect a new-looking mistake back to a
previously-established failure pattern, rather than treating every
chapter's problems as unrelated.

## 3. (Intermediate) Explain what `write_file` being `ALLOWED` in `TOOL_POLICY_CI` actually guarantees, and what it does NOT guarantee on its own.

**Strong answer:** `ALLOWED` in `TOOL_POLICY_CI` only guarantees that
`dispatch_tool_call` won't refuse the call at the POLICY-TIER level —
it will proceed to actually invoke `write_file()`. It does NOT
guarantee the write will succeed, and it does NOT mean write_file can
write anywhere. `write_file()`'s own body still checks
`CI_SCRATCH_PREFIX` before touching the filesystem, and refuses with a
clean error if the path is outside that scope, even though the tier
already cleared it. The tier and the scope check are two independent
layers doing two different jobs — the tier says "this TOOL is
allowed to run in CI at all," the scope check says "THIS SPECIFIC
call, given its actual arguments, stays inside the boundary a human
pre-approved."

**Red flag:** Treats `ALLOWED` in `TOOL_POLICY_CI` as the complete
answer to "is this call safe," without mentioning the scope check
inside the function body at all.

**Follow-up:** "Where exactly, in the actual call sequence, does the
scope check run relative to the policy-tier check — before
`dispatch_tool_call` decides to call the function, or after, inside the
function itself? Why does that ordering matter?"

**What this proves:** Understands that a permissive tier and a safe
outcome are not the same claim — this chapter's whole design depends on
that distinction holding.

## 4. (Intermediate) A colleague says "CI mode is basically the same policy as interactive mode, just with the REQUIRES_CONFIRMATION tools switched to ALLOWED." Is that accurate?

**Strong answer:** Not quite — it's accurate for `write_file` and
`git_commit` (REQUIRES_CONFIRMATION becomes ALLOWED, each paired with a
new scope check), but NOT for `edit_file` or `run_shell_command`, both
of which go from REQUIRES_CONFIRMATION to BLOCKED, not ALLOWED. The
difference is whether a narrow, code-checkable scope exists for the
tool at all. `write_file` can be scoped to a path prefix;
`git_commit` can be scoped to a non-protected branch. `edit_file`
modifies a TRACKED file in place — there's no equivalent narrow prefix
that makes an arbitrary in-place edit safe without a human looking
first. `run_shell_command` accepts an arbitrary string — there's no
scope narrow enough to pre-approve every possible command. So CI mode
isn't "confirmation becomes automatic yes" uniformly; it's "each
formerly-confirmed tool gets re-evaluated on whether a safe, narrow,
pre-decidable scope exists for it at all," and the answer differs per
tool.

**Red flag:** Assumes every REQUIRES_CONFIRMATION tool becomes ALLOWED
in CI mode, missing that `edit_file` and `run_shell_command` actually
become MORE restrictive (BLOCKED), not less.

**Follow-up:** "If your team later wanted to make `run_shell_command`
usable in CI too, what would have to be true about it first, using the
same reasoning that made `write_file` and `git_commit` work?"

**What this proves:** Has actually looked at the specific per-tool
decisions in `TOOL_POLICY_CI`, not just absorbed a one-line summary of
"CI mode is more permissive."

## 5. (Senior) Walk through exactly what happens, step by step, when a CI troubleshooting agent built on this chapter's code calls `git_commit("apply fix")` while the CI runner happens to have the workspace checked out on `main` instead of a scratch branch.

**Strong answer:** `dispatch_tool_call` parses the arguments, finds
`git_commit` in `TOOL_FUNCTIONS`. It calls `check_permission("git_commit")`,
which calls `active_policy()` — since `CI_MODE` is True, this returns
`TOOL_POLICY_CI`, where `git_commit` is `ALLOWED`. Because the tier is
`ALLOWED` (not `REQUIRES_CONFIRMATION`), `confirm_with_human` is never
called at all — there's no prompt, nothing waiting on stdin. Control
reaches the real `git_commit(message)` function. Because `CI_MODE` is
True, it calls `_current_branch()`, which runs `git rev-parse
--abbrev-ref HEAD` and gets back `"main"`. Since `"main"` is in
`PROTECTED_BRANCHES`, the function returns a clean "error: ... refused
on protected branch 'main' ..." string WITHOUT ever running `git
commit`. The model sees that error as a tool result and has to
continue without the commit having happened — no exception, no crash,
no partial commit, no prompt anyone had to answer.

**Red flag:** Assumes `confirm_with_human` gets involved somewhere in
this path — it doesn't, because the tier is ALLOWED, not
REQUIRES_CONFIRMATION; conflates the branch check with the
confirmation mechanism when they're two structurally different things.

**Follow-up:** "What's the ONE piece of information this whole check
depends on being trustworthy, and where does that information actually
come from — could the model influence it?"

**What this proves:** Can trace a precise multi-function control-flow
path through a design with two independent gating mechanisms (policy
tier, then a mode-specific scope check inside the function body), not
just describe the intended behavior at a high level.

## 6. (Senior) Design an argument for why `run_shell_command` is BLOCKED outright in `TOOL_POLICY_CI`, when a narrower, explicitly-scoped alternative (`run_tests`) was built and shipped ALLOWED in the very same policy.

**Strong answer:** The difference isn't "shell commands are dangerous
and tests aren't" in the abstract — it's that `run_tests` has a scope
narrow enough to state and verify completely: it takes ZERO arguments,
runs exactly one fixed command (`TEST_COMMAND`), and nothing about its
call shape lets a caller (model or otherwise) change what actually
executes. `run_shell_command` accepts an arbitrary string as its
entire argument — there is no way to write a scope check for
"arbitrary string" that isn't itself either infinitely permissive or a
second denylist trying to enumerate danger, which Chapter 8 already
showed is inherently incomplete (a list can only cover patterns
someone thought of). Chapter 11's least-privilege retrospective already
named the fix for this exact tension: replace one broad, gated
capability with several narrow, purpose-built ones. `run_tests` is
that fix, applied concretely; `run_shell_command` staying BLOCKED in CI
is the honest acknowledgment that the broad version was never going to
get a real scope check, only ever a confirmation — and CI has no one
to give one.

**Red flag:** Argues run_shell_command should just get "a good enough
denylist" for CI too, missing that Chapter 8 and Chapter 11 already
established why a denylist is a real, honestly-scoped mitigation but
not a substitute for either a human's judgment or a narrow, arguable
scope.

**Follow-up:** "Your team wants ONE more narrow shell-adjacent tool for
CI, alongside run_tests. What's the best candidate, and how would you
argue its scope is as narrow and verifiable as run_tests's?"

**What this proves:** Connects this chapter's specific design decision
back to Chapter 11's least-privilege framing as the actual reasoning,
not just "shell is scary."

## 7. (Architect) You're designing the CI wiring for a regulated engineering org (e.g. handling financial or health data). Would you reuse this chapter's exact `TOOL_POLICY_CI`, or would you design something stricter? Justify a concrete change, not just "be more careful."

**Strong answer:** I would keep the STRUCTURE (two separate,
human-reviewed policy dicts, code-level scope checks standing in for
confirmation, a mode flag read once at startup) but tighten specific
tiers for this context. Concretely: I'd move `write_file` from ALLOWED
back to BLOCKED even inside `ci-scratch/`, and instead have the agent's
only output be a structured report (a diff-shaped string in its final
message, or a single well-defined artifact upload) that a SEPARATE,
human-triggered step turns into an actual scratch-branch commit — this
removes even the scoped write capability from the unattended path
entirely, accepting reduced usefulness (the agent can propose but never
itself write) in exchange for a strictly smaller blast radius, which is
the right trade for a regulated environment where "a scratch write that
turned out to matter more than expected" is a worse failure mode than
in a typical internal tools repo. I would NOT simply add more
confirmation prompts, since CI still has no one to answer them — the
fix has to be tightening the ALREADY-unattended-safe design, not
reintroducing a human-shaped gap that isn't actually there.

**Red flag:** Says "add more logging/monitoring" as the primary answer
without changing what the agent is actually ALLOWED to do — observability
after the fact doesn't reduce blast radius before the fact, which is
what a regulated context specifically needs.

**Follow-up:** "If write_file is fully BLOCKED, how does the agent's
proposed fix actually reach a human at all — walk through the concrete
mechanism, not just 'a report.'"

**What this proves:** Architect-level judgment — proposes a specific,
justified structural change rather than a vague "more security" gesture,
and reasons about the trade-off explicitly.

## 8. (Architect) A stakeholder asks: "If TOOL_POLICY_CI is just a dict a human writes once, reviewed once via PR, what actually stops it from silently becoming wrong over time — a tool changing behavior, a scratch prefix quietly becoming load-bearing, a branch-naming convention changing?" How do you respond?

**Strong answer:** Nothing in this chapter's code detects that kind of
DRIFT automatically — that's an honest gap, not something to paper
over. What the design DOES guarantee is that any CHANGE to
`TOOL_POLICY_CI`, `CI_SCRATCH_PREFIX`, or `PROTECTED_BRANCHES` is a
visible, reviewable diff in version control, the same PR-review
discipline this entire course has taught since Chapter 3 — so a human
widening the policy (intentionally or by accident) leaves a trace
someone could have caught, unlike a runtime auto-approval that leaves
no artifact at all. For the DRIFT risk specifically (the scratch prefix
becoming load-bearing without anyone updating the policy, a branch
convention changing without updating PROTECTED_BRANCHES), the right
answer is the same discipline this course applies to everything else
security-adjacent: periodic, deliberate re-review of the policy against
current reality — the same kind of retrospective Chapter 11 did for
Chapters 7-9's tools — not a claim that the policy, once written, stays
correct forever on its own. A policy dict is a snapshot of a decision,
not a live guarantee; treating it as the latter is exactly the kind of
overselling this course has avoided with every other mechanism
(the denylist, resource limits, MCP's trade-offs).

**Red flag:** Claims the PR-review process alone is sufficient forever,
without acknowledging that a correct-at-review-time policy can still
become stale as the surrounding system changes — or, in the other
direction, dismisses the whole design as fragile without crediting what
version-controlled review actually does provide (an auditable trail,
a deliberate human decision point) versus a runtime auto-approval.

**Follow-up:** "Design one concrete, lightweight process (not more
code) that would catch this policy going stale over, say, a year of a
real team's changes."

**What this proves:** Can hold two things at once — genuine confidence
in what a mechanism actually guarantees, and honesty about what it
doesn't — the same balance this course has modeled for every security
mechanism since Chapter 8.
