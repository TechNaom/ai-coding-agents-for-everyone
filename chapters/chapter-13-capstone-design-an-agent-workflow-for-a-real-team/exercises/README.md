# Chapter 13 Exercises: The Regulated-Path Policy Layer's Building Blocks

These exercises don't need Ollama, a live model, network access, or a
real git repo to verify — `starter.py` and `solution.py` in this folder
rebuild the regulated-CI-policy layer's own building blocks (a
substring-based path classifier, a card-number redaction scrub, and a
mode-aware tier resolver where a regulated-path hit overrides an
otherwise-`ALLOWED` tier) as small, independently testable functions.

## Exercise standard

Six tasks below. At least three are production-gear: harder, ambiguous,
real-world judgment calls rather than clean textbook cases.

1. **Implement `classify_path`.** Fill in TODO 1: a regulated-path
   classifier using SUBSTRING containment, not a leading-prefix match —
   a pattern nested under a scratch prefix must still be caught. Get
   the first six checks to `PASS`.
2. **Implement `redact_pan`.** Fill in TODO 2: a one-line redaction
   using `PAN_PATTERN.sub`. Get the next four checks to `PASS`.
3. **Implement `resolve_ci_tier_for_regulated_org`.** Fill in TODO 3:
   the combined tier-lookup-plus-regulated-override function. Get the
   remaining five checks to `PASS`.
4. **(Production-gear) Design the classification for a genuinely
   ambiguous path.** Your team adds a new directory,
   `analytics/payments_dashboards/`, that reads (but never writes)
   aggregated, already-anonymized transaction counts — no PAN, no raw
   transaction records, nothing SOX's ICFR scope would call a
   ledger-posting path. Should `classify_path` treat this directory as
   CDE, GL, or neither? Write 3-4 sentences defending your answer,
   including what specifically about "reads aggregated, anonymized
   data" does or doesn't matter to a classifier that operates purely on
   path STRINGS, with no actual knowledge of what a file's contents
   are.
5. **(Production-gear) Trace a false negative.** A new subsystem,
   `checkout/apple_pay_bridge/`, is added to the codebase. It handles
   tokenized card data from a third-party wallet provider — squarely
   CDE in substance — but nobody updates `CDE_PATH_PATTERNS` to include
   it. Using `classify_path`'s actual behavior (not a guess), what
   happens the first time the CI troubleshooting agent's `write_file`
   call targets a file under this new directory? Is this a bug in
   `classify_path` itself, or a bug in the PROCESS that maintains it?
   What does your answer suggest about how `CDE_PATH_PATTERNS` should
   be reviewed going forward?
6. **(Production-gear) Review a policy change that only updates one
   pattern list.** A PR adds a genuinely new regulated subsystem to
   `GL_PATH_PATTERNS` but doesn't touch `CDE_PATH_PATTERNS`, `TOOL_POLICY_CI`,
   or the audit-log redaction logic at all. Using
   `resolve_ci_tier_for_regulated_org`'s actual behavior, confirm
   whether that's sufficient on its own, or whether a change to one
   pattern list has implications for the other two mechanisms that a
   reviewer should specifically check for. Write 3-4 sentences citing
   the actual code path.
