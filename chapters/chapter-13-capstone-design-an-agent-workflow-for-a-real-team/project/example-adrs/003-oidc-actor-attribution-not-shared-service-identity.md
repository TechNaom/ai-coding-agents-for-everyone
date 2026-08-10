# ADR-003: Every Agent Action Is Attributed to the Triggering Human via Propagated Identity, Not a Shared CI Service Account

Status: Accepted
Date: 2026-08-10
Deciders: Platform Engineering Lead + Head of Compliance Engineering (Meridian Ledger)

## Context

Chapters 11-12's `dispatch_tool_call` and `TOOL_POLICY_CI` answer "is
this tool call allowed" but never ask "allowed on WHOSE authority."
That question was out of scope for a general internal-tools agent, but
it isn't optional here: SOX Section 404 requires that a change to an
ICFR-scoped system be traceable to a specific accountable individual,
and a PCI-DSS QSA assessment will ask, concretely, "who approved this
change" for anything touching the CDE -- "the CI bot" is not an
acceptable answer to either question. Every tool call this agent
makes, and every commit it produces, needs a real answer to "which
human is accountable for this specific action having happened."

## Decision

Propagate the identity of the human who actually triggered the CI run
-- in a real GitHub Actions deployment, via the workflow's OIDC token
claims (`github.actor`, tied to the PR or workflow-dispatch event that
started the run) rather than any value the run itself could set -- into
every audit-log entry (`audit_log()`'s `actor` field) and into every
commit the agent produces (`Triggered-By` trailer). `git_commit`
refuses to commit at all if no actor identity is available, rather
than falling back to a shared placeholder.

## Options Considered

- **A shared CI service-account identity for every run** (e.g. every
  commit authored by `ci-bot@meridianledger.example`, no per-run
  distinction). Simplest to implement -- no OIDC wiring needed at all.
  Rejected: this is the exact failure mode this ADR exists to prevent.
  A shared identity answers "what made this commit" but not "who is
  accountable for it," and a SOX auditor's actual question is the
  second one. It also makes a compromised or malfunctioning CI
  pipeline harder to investigate -- every action looks identical
  regardless of which PR, which human, or which trigger produced it.
- **Propagate the triggering human's identity via OIDC-token claims,
  refuse to act without one.** Chosen. Ties every action back to a
  specific PR/workflow-dispatch event and the human who caused it to
  run, using a mechanism (OIDC) the CI platform itself verifies rather
  than a plain environment variable a workflow step could set to
  anything.
- **Require an explicit, additional human "run approver" step even for
  CI-mode runs (e.g. a second person must click "approve" before the
  agent starts).** Rejected for reasons Chapter 12 already established
  in a different but structurally identical case: this reintroduces a
  human-in-the-loop requirement into a context (CI) that is
  unattended by construction, exactly the mistake Chapter 12's
  Section 3 diagnosed in the "auto-answer `confirm_with_human`" wrong
  fix. A required approval step for the agent to even START either
  becomes a rubber-stamp click nobody meaningfully evaluates (weakening
  the guarantee it claims to provide) or becomes a bottleneck that
  defeats the whole point of an unattended troubleshooting agent.
  Attribution and authorization are different questions -- this ADR
  answers "who is accountable," not "did a second human bless this
  specific run before it started."

## Consequences

Requires real OIDC integration work in the CI platform (out of scope
for `project/solution.py`'s offline demo, which simulates the
propagated identity via the `MERIDIAN_TRIGGERED_BY` environment
variable rather than a verified token, and says so in its own
docstring) -- a genuine implementation gap between this ADR's decision
and the demo code that accompanies it, disclosed rather than hidden.
In exchange, the audit trail answers the actual compliance question
directly: `git log` alone on any agent-produced commit already shows
who triggered it, without cross-referencing a separate system. A
future incident review or QSA sampling of agent-produced commits can
be answered from source control history alone.

## Compliance Note

Directly satisfies PCI-DSS Requirement 10.2 (audit trails that link
each action to an individual user, not a shared account) and the
individual-accountability expectation underlying SOX Section 404's
change-management controls. This ADR does NOT by itself satisfy PCI-DSS's
broader logging-retention requirements (Requirement 10.5.1: audit
trail history retained for at least 12 months, with 3 months
immediately available) -- that's a separate, unresolved design item,
named explicitly in the lesson's "what this design does not solve"
discussion rather than silently assumed to be handled here.
