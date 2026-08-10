# ADR-001: A Hybrid of Both CI Use Cases, Not a Single Agent

Status: Accepted
Date: 2026-08-10
Deciders: Platform Engineering Lead + Head of Compliance Engineering (Meridian Ledger)

## Context

Chapter 12 named two CI agent use cases: a PR review bot (reads a
diff, comments -- read-only, per Chapter 12's own account, "the easy
half") and a CI troubleshooting agent (investigates a failing build
and proposes or applies a fix -- the harder half, because it needs
real write capability). Meridian Ledger's engineering org spans two
very different kinds of code in the same monorepo: internal tooling
and test infrastructure with a low blast radius if something goes
wrong, and code inside the Cardholder Data Environment (CDE, PCI-DSS
scope) or the general-ledger/reconciliation path (SOX Section 404
ICFR scope), where an incorrect or unattributed automated change is a
compliance event, not just a bug. We need one coherent CI agent
strategy that serves both, without either starving the low-risk 80%
of the codebase of a useful troubleshooting agent, or exposing the
regulated 20% to unattended writes.

## Decision

Ship both use cases, permanently split by what they're allowed to
touch, not by which repo or team runs them: a PR review bot runs
org-wide, on every PR, in every path, comment-only, no write
capability anywhere. A CI troubleshooting agent runs only against
non-regulated paths -- enforced in code (`regulated_category()`, this
chapter's `project/solution.py`), not by convention or documentation
-- and is structurally incapable of writing to or committing anything
under a CDE or GL path pattern, regardless of branch, scratch scoping,
or how the tool call is invoked.

## Options Considered

- **One review-bot-only agent, org-wide, no troubleshooting agent at
  all.** Simplest to reason about and to get compliance sign-off on --
  there is no write-capable unattended path to defend at all. Rejected
  because it throws away real value for the 80% of the codebase that
  isn't regulated: internal tooling, test infrastructure, and
  non-CDE/non-GL application code get zero benefit from Chapter 12's
  harder use case, for a risk that only actually exists in the
  regulated 20%.
- **One troubleshooting agent, org-wide, gated the same way everywhere
  (Chapter 12's TOOL_POLICY_CI unmodified).** Maximizes usefulness
  everywhere but treats a payments-tokenization file and a CI script's
  own YAML config as equally safe to auto-write, which they are not.
  Rejected outright -- this is the design compliance would reject on
  sight, and rightly so; "our CI agent can write anywhere except we
  trust it not to" is not a control.
- **A hybrid, split by regulated-path classification, enforced in
  code.** Chosen. Both use cases exist; which one an agent effectively
  becomes for a given PR is determined by what paths that PR's own
  diff touches, checked mechanically against `CDE_PATH_PATTERNS` and
  `GL_PATH_PATTERNS`, not by a human remembering to route the PR
  correctly.

## Consequences

Two agent configurations to maintain instead of one, and a path
classifier (`regulated_category()`) that has to be kept current as the
repo's directory layout evolves -- a real ongoing cost, not a one-time
setup. In exchange: the troubleshooting agent's entire existence
becomes defensible to a PCI-DSS QSA or a SOX auditor in one sentence
("it cannot write to regulated paths, full stop, enforced in code, not
policy") instead of needing a much harder argument about why an
unattended agent with org-wide write access is safe. If Meridian
Ledger's directory layout is ever refactored (e.g. CDE code moves out
of `payments/`), `CDE_PATH_PATTERNS`/`GL_PATH_PATTERNS` must be updated
in the same PR as the refactor -- this is a real drift risk, named
explicitly in the lesson's failure-mode section, not solved by this
ADR alone.

## Compliance Note

Directly addresses PCI-DSS Requirement 7 (restrict access to
cardholder data by business need-to-know) and SOX Section 404's
requirement that changes to ICFR-scoped systems go through a
controlled, attributable process -- by making "an unattended agent has
no business need to write here at all" true by construction for both
regimes, rather than relying on the agent's own judgment per run.
