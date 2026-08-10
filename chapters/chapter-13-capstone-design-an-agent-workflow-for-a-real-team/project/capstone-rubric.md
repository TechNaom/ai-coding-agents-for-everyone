# Capstone Rubric: Design an Agent Workflow for a Real Team

This is Module 6's stated assessment (`docs/curriculum/CURRICULUM_MAP.md`:
"capstone rubric (architecture challenge, Level 4)") -- there is no
separate written exam for this module. Evaluate a learner's own
submitted design document against the seven criteria below. Each has
three levels: **Does Not Meet**, **Meets**, **Exceeds**. A real
submission is expected to land at "Meets" on most criteria and
"Exceeds" on at least one or two -- landing at "Does Not Meet" on any
single criterion should block calling the submission complete,
regardless of how strong the rest of the document is, because each
criterion below corresponds to a specific mechanism this course spent
a full chapter establishing as non-negotiable.

---

## 1. Business Scenario Specificity

**Does Not Meet:** The org is generic ("a healthcare company," "a
bank") with no concrete detail about what it actually builds, what
data it handles, or which regulatory regime applies and why. "It's
regulated" functions as a label, not a constraint.

**Meets:** Names one real regulatory regime (HIPAA, PCI-DSS, SOX, a
government-contractor framework like FedRAMP, etc.), states concretely
what the org builds and what data/system is in scope, and states at
least one specific consequence of getting the design wrong (a fine, a
lost certification, a reportable incident, a material weakness
disclosure).

**Exceeds:** The regulatory constraint visibly and specifically shapes
multiple downstream design decisions (not just the security section) --
e.g. the org's actual system boundaries determine where a regulated-path
classifier draws its lines, and the submission can point to which
named requirement (not just "compliance") drove which specific
architecture choice.

## 2. Correct Application of the Permission-Scope Model (Chapters 11-12)

**Does Not Meet:** No three-tier (ALLOWED/REQUIRES_CONFIRMATION/BLOCKED)
model, or a model that defaults to allow rather than fail-closed, or a
single policy reused unchanged for both interactive and CI modes
without acknowledging CI structurally cannot provide a human
confirmation.

**Meets:** A real two-policy design (interactive vs. CI), fail-closed
default explicitly stated, and for every tool made more permissive in
CI mode, a corresponding code-level scope check identified (not just
asserted) that substitutes for the confirmation CI can't give --
matching Chapter 12's `write_file`/`git_commit` pattern.

**Exceeds:** Explicitly reasons about WHICH tools have no narrow scope
at all and should be `BLOCKED` outright in CI rather than loosened
(Chapter 12's `edit_file`/`run_shell_command` reasoning, applied to a
tool genuinely new to this submission's scenario) -- not just copying
Chapter 12's specific tool list unchanged.

## 3. Regulated-Path / Blast-Radius Scoping Specific to This Org

**Does Not Meet:** No mechanism distinguishing regulated code/data from
the rest of the codebase -- the agent's write capability is either
uniformly granted or uniformly denied across the whole repo, with no
reasoning about why that's the right (or only feasible) granularity.

**Meets:** A concrete classification mechanism (a path pattern, a
tag, a directory boundary -- something checkable in code, not "the
agent should know not to touch sensitive stuff") that blocks writes to
regulated code/data, checked against ACTUAL changed files/paths, not
against the model's own claims about what it changed.

**Exceeds:** Names a genuine drift risk in the classification mechanism
itself (a directory getting refactored, a new regulated subsystem not
yet added to the pattern list) and proposes a concrete, lightweight
process for catching it, rather than presenting the classifier as a
permanently-solved problem.

## 4. Audit Trail and Attributability

**Does Not Meet:** No audit trail beyond default CI logs, or an audit
trail that records outcomes but not WHO triggered the action, or an
audit trail attributed to a shared bot/service identity for every run.

**Meets:** Every agent action traceable to a specific triggering human
or event (not a shared identity), recorded in a structured, durable
form (not just console output), with enough detail (tool, arguments,
decision, timestamp) to answer "what happened and who is accountable"
without re-running anything.

**Exceeds:** Explicitly addresses a realistic failure of the audit
mechanism itself -- e.g. sensitive data (a card number, a patient
identifier) accidentally landing IN the audit log, and a concrete
mitigation for that specific risk (redaction, field-level scoping) --
not just "logs go to a secure system."

## 5. Human Review Gate Correctly Distinguished from What's Safe to Automate

**Does Not Meet:** No explicit statement of what still requires human
review after the automated policy runs, or the submission treats a
passing CI run / a scoped commit as equivalent to "safe to merge."

**Meets:** A clear, explicit list (matching Chapter 12's Section 5
shape) of what's safe to land unreviewed (comments, scoped commits on
disposable branches, draft PRs) vs. what still needs Chapter 3's full
review discipline every time (merging, trusting the agent's own
narrative/diagnosis, changing the policy itself).

**Exceeds:** Names who specifically is qualified to grant the review
this design still requires (a role, a designation -- e.g.
"compliance-designated reviewer," not just "a human" or "a senior
engineer") when the regulatory context makes that distinction matter,
and explains why an ordinary code reviewer isn't sufficient for that
specific gate.

## 6. At Least One Chapter 5 Failure Mode Addressed Concretely in the Unattended Context

**Does Not Meet:** No mention of thrashing/stalling/going-off-the-rails/
premature-done, or a mention that stays entirely abstract ("the agent
might make mistakes") without connecting to what's different about an
unattended, regulated CI run specifically.

**Meets:** At least one of Chapter 5's four failure modes is named and
connected to a concrete consequence specific to THIS scenario (e.g.
premature "done" on a reconciliation-logic claim risking a financial
misstatement, not just "wasted CI time") and at least one concrete
mitigation beyond a generic step cap.

**Exceeds:** Connects the mitigation to an INDEPENDENT check outside
the model's own output (an automated verification step, a required
re-run of a specific test, a mandatory second look at any claim
touching regulated logic) rather than trusting the model's own
self-report that it succeeded -- the same "acceptance criteria run
independently" principle Chapter 5 named as the actual fix.

## 7. ADR Quality

**Does Not Meet:** Fewer than two ADRs, or ADRs that document only the
chosen option with no real alternatives, or alternatives that are
obvious strawmen included to flatter the chosen option.

**Meets:** At least two ADRs for genuinely contestable decisions in
this design, each naming real alternatives that a reasonable engineer
could have proposed, with honest trade-offs (not just benefits) for
the chosen option, and a stated consequence.

**Exceeds:** At least one ADR explicitly ties its decision to a named
compliance requirement (not just "compliance requires this" in the
abstract) and states what would have to change for the decision to be
revisited -- treating the ADR as a living record, not a one-time
justification.

---

## Honesty About Gaps (cross-cutting, applies to the whole submission)

Independent of the seven scored criteria above: does the submission
explicitly name at least one thing its own design does NOT solve? A
submission that reads as fully solved, with no acknowledged gap, is a
red flag regardless of how the seven criteria above scored --
every real design this course has built (Chapter 8's denylist,
Chapter 11's sandboxing, Chapter 12's policy-drift risk) had an honest,
named limitation. A capstone submission with zero acknowledged gaps
either hasn't thought hard enough about its own design, or is
overselling it -- both are worth flagging in review, separate from and
in addition to the seven criteria's own scores.
