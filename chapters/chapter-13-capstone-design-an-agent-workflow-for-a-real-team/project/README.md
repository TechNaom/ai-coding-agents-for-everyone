# Chapter 13 Capstone Project: Design an Agent Workflow for a Real Team

This is the L4 Architecture Challenge, per
`docs/curriculum/CURRICULUM_MAP.md`: "Design an agentic CI workflow (a
PR review bot or CI troubleshooting agent) for a regulated engineering
org; business problem only." Unlike Chapters 7-12's labs, the center
of this project is a **design document**, not a new agent
implementation. `starter.py`/`solution.py` in this folder are provided
because one concrete mechanism (a regulated-path-aware CI policy)
genuinely benefits from being shown precisely in code, the same way
Chapters 11-12 did for their own policy layers -- but writing that code
is a small part of this project, not the point of it.

## What's provided

- **`solution.py`** -- a worked reference implementation extending
  Chapter 12's `TOOL_POLICY`/`TOOL_POLICY_CI` pattern with a
  regulated-path classifier, mandatory actor attribution on CI-mode
  commits, and a structured, redacted audit log. Read its module
  docstring first -- it lays out the Meridian Ledger scenario this
  whole chapter builds on.
- **`starter.py`** -- the same file with three connected TODOs removed
  (`regulated_category`, `write_file`'s CI-mode checks, `git_commit`'s
  CI-mode checks). Optional to complete -- see "Your task" below.
- **`adr-template.md`** -- the format every ADR in this project (and
  your own submission) should follow.
- **`example-adrs/`** -- three real, filled-out ADRs for genuinely
  contestable decisions in this chapter's own worked design: which CI
  use case(s) to build (`001`), whether the troubleshooting agent may
  auto-commit at all (`002`), and how every action gets attributed to
  an accountable human (`003`). Read these as a model for your own
  submission's ADRs, not as the only correct answers -- a different,
  well-argued decision on any of these three would be a legitimate
  submission too.
- **`capstone-rubric.md`** -- the actual assessment for this module,
  per the curriculum map ("capstone rubric, architecture challenge,
  Level 4"). Seven scored criteria, each with Does-Not-Meet / Meets /
  Exceeds levels, plus a cross-cutting honesty-about-gaps check.

## Your task

**Primary deliverable (required):** a design document for your OWN
regulated-org scenario -- pick a real regulatory domain (it does not
have to be Meridian Ledger's payments/SOX scenario; HIPAA, a
government-contractor framework, or a different financial-services
angle are all legitimate) and produce:

1. A specific business scenario (rubric criterion 1).
2. A permission-scope design for both interactive and CI modes
   (criterion 2).
3. A regulated-path/blast-radius scoping mechanism specific to your
   scenario (criterion 3).
4. An audit-trail and attribution design (criterion 4).
5. An explicit statement of what still needs human review, and by whom
   (criterion 5).
6. At least one Chapter 5 failure mode addressed concretely in your
   unattended context (criterion 6).
7. At least two ADRs for genuinely contestable decisions in YOUR
   design, using `adr-template.md` (criterion 7).
8. At least one explicitly named gap your design does not solve.

**Secondary, optional exercise:** complete `starter.py`'s three TODOs
and confirm your output matches `solution.py`'s (see "Before you call
it done" below). This exercises the one mechanism in this chapter
concrete enough to be worth typing out, but completing it is not a
substitute for the design document above -- the design document is
graded against `capstone-rubric.md`; the code is not separately
scored.

## Before you call it done (if you complete starter.py)

Run both:

```
python3 starter.py < /dev/null
ACAFE_CI_MODE=1 python3 starter.py < /dev/null
```

Confirm scenario 2 (a write nested under `ci-scratch/` that also
matches a CDE pattern) is refused -- if it silently succeeds, your
`regulated_category()` is checking a leading prefix instead of
substring containment, and the scratch-scope allowance is winning over
the regulated-path block when it should never be able to. Confirm
scenario 4 (no actor set) is refused, and scenario 5 (actor set)
succeeds and shows both trailers in `git log`. Compare your full output
against `solution.py`'s.

## Grading your own design document

Use `capstone-rubric.md` directly. Score yourself honestly against all
seven criteria before considering this project done -- a submission
that would land "Does Not Meet" on even one criterion has a real gap
worth closing before calling this capstone, and this course, complete.
