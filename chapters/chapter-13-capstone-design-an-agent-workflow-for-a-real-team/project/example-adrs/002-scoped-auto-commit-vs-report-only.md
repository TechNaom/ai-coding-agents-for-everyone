# ADR-002: The CI Troubleshooting Agent May Auto-Commit, But Only to Non-Regulated Scratch Paths on a Disposable Branch

Status: Accepted
Date: 2026-08-10
Deciders: Platform Engineering Lead + Head of Compliance Engineering (Meridian Ledger)

## Context

Given ADR-001's split, the CI troubleshooting agent still needs a
concrete answer to the question Chapter 12 itself raised and resolved
for a lower-stakes context: should it be allowed to auto-commit
anything at all in an unattended CI run, or should it be report-only
(propose a fix as text, never write it)? Chapter 12's own answer
(scoped `write_file`/`git_commit`, per-tool code-level checks
substituting for the confirmation CI can't give) was built for a
general-purpose internal-tools context. Meridian Ledger is a public
company under SOX; a wrong committed fix -- even on a scratch branch
nobody merges automatically -- still represents an unattended write
against company source control, which is a materially different risk
posture than an unregulated startup's CI.

## Decision

The CI troubleshooting agent may auto-commit, but only under all of
the following, enforced in code (not just documented): the target
branch must not be `main`/`master`; every staged file's
`regulated_category()` must be `None`; a real triggering actor
identity must be attached to the commit as a `Triggered-By` trailer;
and the resulting commit only ever reaches `main` via a **draft** pull
request a compliance-eligible human reviewer opens for real review --
the agent never merges anything, ever, under any condition.

## Options Considered

- **Full auto-commit privilege, identical to Chapter 12's
  `TOOL_POLICY_CI` unmodified.** Maximizes usefulness, matches the
  course's own reference design exactly. Rejected as insufficient on
  its own for this org: Chapter 12's design has no regulated-path
  concept and no mandatory actor attribution, both of which SOX and
  PCI-DSS require here specifically. Using it unmodified would pass a
  general code review and fail a compliance review.
- **Report-only -- the agent never calls `write_file` or `git_commit`
  at all; its final message is a structured diagnosis a human copies
  into a fix by hand.** Maximizes safety -- there is no unattended
  write path to defend, period. Rejected as leaving too much value on
  the table: for the 80% of the codebase this agent is even allowed
  near (per ADR-001), most proposed fixes are small and mechanical
  (a config typo, a flaky-test retry count, a missing test fixture),
  and requiring a human to manually re-type every one of them
  reintroduces exactly the friction this course's Module 5 built
  scoped automation to remove. It also produces a weaker audit trail:
  a human manually re-applying a fix from a chat message has no
  structured record connecting the CI run's diagnosis to the eventual
  code change at all.
- **Scoped auto-commit to non-regulated paths, disposable branch, draft
  PR only, mandatory actor attribution.** Chosen. Keeps the value of
  auto-commit for the low-risk majority of the codebase while making
  the two things a regulated org actually needs -- "it structurally
  cannot touch regulated code" and "every committed change traces to a
  specific accountable human" -- true by construction rather than by
  policy alone.

## Consequences

The troubleshooting agent is meaningfully less capable than Chapter
12's reference design near any path a future refactor might
misclassify -- a false negative in `regulated_category()` (a regulated
file that the classifier fails to recognize as regulated) is the
single biggest residual risk this ADR accepts, and is exactly why
ADR-001's consequences section names path-pattern drift as an ongoing
cost, not a solved problem. In exchange, every commit this agent
produces is individually defensible to an auditor: which branch,
which files (verified as non-regulated at commit time, not just
assumed), and who triggered the run. This ADR would need revisiting if
Meridian Ledger's QSA or auditor found the current CDE_PATH_PATTERNS/
GL_PATH_PATTERNS classification insufficiently conservative -- in that
case the fallback is tightening toward the rejected report-only
option for the specific subset of paths in question, not weakening the
attribution or draft-PR requirements.

## Compliance Note

PCI-DSS Requirement 10 (track and monitor all access to network
resources and cardholder data) is satisfied for the CDE specifically by
ADR-001's hard block, not by this ADR -- this ADR's job is narrower:
ensuring that even the NON-regulated writes this agent makes are
individually attributable (Triggered-By trailer, audit log entry) and
reversible before merge (draft PR, human-gated), which is the SOX
Section 404 control this ADR exists to satisfy.
