# Interview Questions: Capstone — Design an Agent Workflow for a Real Team

Plain-markdown mirror of `interview-questions.html`. Grouped by level.
Each includes a strong answer, a red flag, and a follow-up. As the
course's capstone, these lean toward architect-level synthesis
questions more than most prior chapters' beginner-level questions do.

## 1. (Beginner) Why does the PR review bot need zero changes to Chapter 11's original permission policy at all, even for a regulated org like Meridian Ledger?

**Strong answer:** A PR review bot's entire job is reading a diff and
producing a comment — every tool it needs (`read_file`, `git_diff`) is
already `ALLOWED` under Chapter 11's exact original policy, in every
path, regulated or not, because reading a file and commenting on it
has no write side effect anywhere. Nothing about being regulated
changes what "read-only" means. The regulated-path classifier this
chapter adds only matters for tools that WRITE — `write_file` and
`git_commit` — so a purely read-only use case never touches it at all.

**Red flag:** Assumes a regulated org needs a stricter version of
EVERY tool, including read-only ones — misses that the actual risk
this chapter's design manages is write access to sensitive systems,
not read access to a diff.

**Follow-up:** "If the review bot's comment itself might quote a few
lines from a CDE file for context, does that change your answer?"

**What this proves:** Understands that "regulated" constrains specific
capabilities (writes to specific paths), not the agent's existence in
general — a distinction this chapter's whole design depends on.

## 2. (Beginner) In `write_file`, why does the regulated-path check run BEFORE the `ci-scratch/` scope check, rather than after or instead of it?

**Strong answer:** Because a path can be both "inside `ci-scratch/`"
and "matching a regulated pattern" at the same time (e.g.
`ci-scratch/payments/tokenization/notes.txt`), and the scratch-prefix
allowance was never a legitimate reason for a regulated pattern to
stop mattering. Running the regulated check first means it wins
regardless of ordering tricks — nothing about wrapping a regulated
path in a scratch-looking prefix can make the write succeed. If the
scratch check ran first and returned early on success, a regulated
path nested under `ci-scratch/` would slip through undetected.

**Red flag:** Says the order doesn't matter because "both checks would
catch it eventually" — misses that if the scratch check runs first and
ALLOWS the write (because the path IS inside the prefix), the function
would need a second, later check specifically to still catch the
regulated pattern; ordering the regulated check first makes that
one unconditional, not a second chance.

**Follow-up:** "Rewrite `write_file` with the checks in the opposite
order, but still correct — what would that require, and why is the
current ordering simpler?"

**What this proves:** Traces actual control flow rather than treating
"there are two checks" as sufficient on its own.

## 3. (Intermediate) Explain what `TOOL_POLICY_CI["write_file"] == ALLOWED` actually guarantees in this chapter's design, and what it does NOT guarantee, now that a THIRD layer (the regulated-path classifier) sits alongside Chapter 12's scratch-scope check.

**Strong answer:** `ALLOWED` in `TOOL_POLICY_CI` only guarantees that
the harness's dispatch layer won't refuse the call at the policy-TIER
level — it will proceed to call `write_file()`. It does NOT guarantee
the write succeeds. `write_file()`'s own body then runs TWO
independent, ordered checks before touching the filesystem: first,
whether the path is regulated (refuses unconditionally if so);
second, whether the path is inside `ci-scratch/` (refuses if not).
Three layers total, checked in a fixed order — tier, then regulated
path, then scratch scope — each one able to refuse independently, none
of them redundant with the others.

**Red flag:** Collapses all three checks into "the policy blocks
regulated writes," missing that the regulated-path check and the
scratch-scope check are two separate, differently-scoped mechanisms
that happen to both live inside the same function.

**Follow-up:** "If you had to remove exactly one of these three checks
and could only keep two, which would you remove, and what specific
attack or mistake would that reopen?"

**What this proves:** Can hold multiple independent, stacked checks in
mind simultaneously rather than treating "there's a policy for that"
as a single monolithic answer.

## 4. (Intermediate) A colleague says "Meridian Ledger's design is basically Chapter 12's TOOL_POLICY_CI with a stricter scratch prefix." Is that accurate?

**Strong answer:** Not quite, and the difference matters. A "stricter
scratch prefix" would still be a NARROWING of where writes are
allowed, the same kind of mechanism `CI_SCRATCH_PREFIX` already is —
just a smaller allowed zone. This chapter's regulated-path check is
structurally different: it's an override that can refuse a write
EVEN INSIDE an otherwise-allowed scratch zone, and it's checked
against a completely separate classification (CDE/GL patterns) that
has nothing to do with where the scratch directory happens to be. The
mandatory actor attribution on `git_commit` is a second, genuinely new
mechanism Chapter 12 never needed at all — Chapter 12's `git_commit`
takes no `actor` argument and has no accountability concept.
Describing this design as "a stricter prefix" undersells both.

**Red flag:** Treats every addition in this chapter as a variation on
Chapter 12's existing scope-checking pattern, missing that actor
attribution answers a genuinely different question (who is
accountable) that Chapter 12 never asked.

**Follow-up:** "Which of this chapter's two new mechanisms — the
regulated-path override or actor attribution — would a PCI-DSS QSA
care about, and which would a SOX auditor care about? Are they the
same mechanism serving both audiences, or two different mechanisms
each serving one?"

**What this proves:** Distinguishes mechanisms by which specific
requirement they satisfy, not just by their surface resemblance to a
prior chapter's pattern.

## 5. (Senior) Design an argument for why `git_commit`'s regulated-path check reads `git diff --cached --name-only` rather than trusting a `paths_changed` argument the agent's own tool call could pass in directly.

**Strong answer:** The same reasoning Chapter 12 applied to
`_current_branch()` reading git directly instead of trusting a
model-provided branch name: a value the model provides as part of its
own tool call is not independent verification, it's the model's own
claim about its own action, and a model under pressure to get a commit
through has a real incentive (not malicious, just structural, exactly
Chapter 3's root-cause-vs-symptom framing) to describe its changes as
narrowly as possible. Reading actual staged files from git itself
means the check is verifying REALITY — what's actually about to be
committed — not the model's DESCRIPTION of reality. This closes off an
entire class of bug where the model's stated intent and its actual
diff diverge, whether by mistake or by a model that's learned partial
compliance gets things through faster.

**Red flag:** Argues a `paths_changed` argument would be "just as
good" if the model is "well-behaved" — misses that the whole point of
a harness-level check is to not depend on the model behaving well,
the exact framing Chapters 8 and 11 both established for every other
harness-side check in this course.

**Follow-up:** "What's the ONE way a malicious or badly-mistaken model
could still get a regulated file committed despite this check reading
git directly? (Hint: think about what happens BEFORE `git add`.)"

**What this proves:** Applies "verify against ground truth, not the
model's self-report" as a general principle to a new mechanism, not
just remembers it as a fact specific to Chapter 12's branch check.

## 6. (Senior) A stakeholder proposes removing `audit_log()`'s redaction step (`redact_card_data()`) because "the audit log is only accessible to compliance staff who are already authorized to see cardholder data." How do you respond?

**Strong answer:** Being authorized to see cardholder data in the
CONTEXT it's supposed to appear in (a payment record, a PCI-scoped
system with its own controls) is not the same as it being acceptable
for that data to appear UNEXPECTEDLY in a system that was never
designed or assessed as part of the CDE — an audit log is exactly this
kind of secondary surface. PCI-DSS scopes systems specifically; a log
file that starts containing PAN data becomes, functionally, part of
the CDE whether or not anyone intended that, which likely expands the
audit scope of the QSA assessment itself and creates a new place PAN
data can leak if that log is ever exported, backed up, or accessed by
someone whose authorization was scoped to "sees audit events," not
"sees cardholder data." The redaction step exists specifically to keep
the audit log OUT of CDE scope in the first place, which is a
different and arguably more valuable property than "only authorized
people see it."

**Red flag:** Agrees redaction is unnecessary based only on "who can
access the log," without considering whether the log's EXISTENCE with
unredacted PAN data changes what system boundary it now sits inside.

**Follow-up:** "If `redact_card_data()`'s regex has a false negative —
some PAN-shaped string it doesn't catch — what's the actual blast
radius, and how would you find out it happened?"

**What this proves:** Reasons about compliance scope as a property of
the SYSTEM (what data touches it) rather than just of the PEOPLE (who
can access it) — a distinction real PCI-DSS scoping discussions turn on.

## 7. (Architect) How would you defend this chapter's overall design to a skeptical compliance auditor who says "an AI agent touching our CI pipeline at all is an unacceptable risk, regardless of how it's scoped"?

**Strong answer:** I'd separate the auditor's actual concern into two
distinct claims and address each with what the design specifically
provides, not with reassurance. First claim: "the agent might do
something harmful." Response: the agent has zero write access to
anything in CDE or GL scope, enforced in code and checked against
git's own state, not the agent's self-report — its blast radius for
regulated systems is provably zero, not merely policed. Second claim:
"even outside regulated scope, an unattended process making changes is
inherently risky." Response: every write it CAN make lands on a
disposable scratch branch as a draft PR that a human must merge — the
agent's write capability, even at its widest, never bypasses the exact
same code-review gate a human engineer's PR goes through; it just
proposes the starting point. I'd also concede directly, not defensively,
what the design does NOT solve: pattern-list drift (a new regulated
subsystem not yet classified) and the residual risk that a human copies
an agent's scratch proposal into regulated code without extra scrutiny
— both named explicitly in this chapter's own ADRs and practice
scenarios, not hidden. An auditor is more likely to accept "here's
what's provably true and here's what we're still managing manually"
than a claim of zero risk.

**Red flag:** Responds only with reassurance ("we tested it, it's
safe") rather than pointing to specific, checkable mechanisms
(code-level path classification, draft-PR-only landing, actor
attribution) and specific, named residual risks.

**Follow-up:** "The auditor asks for the SINGLE piece of evidence that
would convince them the regulated-path block has never been bypassed
in six months of production use. What do you show them?"

**What this proves:** Can translate a design's actual mechanisms into
the specific claims a compliance audience needs verified, and is
honest about the boundary between "provably true" and "managed by
process" — the same honesty this course modeled from Chapter 1's
no-overclaiming standard onward.

## 8. (Architect) What's the single biggest blast-radius risk remaining in this design, and how is it mitigated (or explicitly not mitigated, and why that's an acceptable trade-off)?

**Strong answer:** The single biggest remaining risk is
`CDE_PATH_PATTERNS`/`GL_PATH_PATTERNS` drift — a new regulated
subsystem added to the codebase without a corresponding update to
these pattern lists, silently reopening exactly the write access this
entire design exists to prevent, with no code-level mechanism that
would catch it (the classifier can only be as accurate as the lists
it's given; it can't detect what it was never told to look for). This
is NOT fully mitigated by this chapter's design — it's named honestly
as an open gap in this chapter's practice scenarios and ADR-001's
consequences section, not solved. The mitigation offered is procedural,
not code-level: any change to those two pattern lists requires the
same compliance-designated review as a change to the regulated code
itself (Section 5's closing point), which at least ensures a human
with the standing to judge "is this actually complete" looks at every
change to the lists — but that's a process control, not a guarantee,
and a real production deployment of this design would need a
periodic, independent audit of the pattern lists against the actual
current codebase layout, which this chapter's worked example doesn't
build.

**Red flag:** Claims there is no remaining blast-radius risk, or names
a risk this chapter's mechanisms actually do fully close (e.g. "the
agent might commit to main" — already hard-blocked) instead of the one
genuinely open gap.

**Follow-up:** "Design the lightest-weight periodic audit process you
can that would catch pattern-list drift within, say, one quarter of it
occurring — without adding a second full-time review burden."

**What this proves:** Distinguishes a genuinely unsolved risk from a
solved one this chapter merely didn't spell out in exhaustive detail —
the same honest-gaps discipline the capstone rubric scores explicitly,
applied here to the chapter's own worked example rather than to a
learner's submission.
