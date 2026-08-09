# Module 1 Written Exam — Using Coding Agents Well

Covers: Chapter 1 (Why Coding Agents Aren't Just Autocomplete), Chapter 2
(Prompting and Scoping Tasks for an Agent), Chapter 3 (Reading and
Reviewing an Agent's Diff Like a Senior Engineer).

Assessment type (per `docs/curriculum/CURRICULUM_MAP.md`): concept +
judgment quiz. Expect a mix of multiple choice, short answer, and
scenario/judgment questions that ask you to apply what Chapters 1–3
actually taught — not just recall definitions.

No open resources needed beyond the three chapters themselves. For
short-answer and scenario questions, write full sentences — a bullet
list of keywords doesn't demonstrate understanding.

---

## Part A — Multiple Choice

Choose the single best answer for each.

**A1.** What is the actual structural difference that makes a coding
agent something other than "a bigger, smarter autocomplete"?

- (a) It was trained on a larger code corpus
- (b) It has a larger context window than inline-suggestion tools
- (c) It runs a loop that decides its own next step and acts through
  real tools (search, read, run, edit) across multiple turns, reacting
  to what those tools actually return
- (d) It has a chat-style interface instead of inline suggestions

**A2.** Per Chapter 2, which of the following is *not* one of the three
jobs a fact has to do in order to count as "enough context" in a
prompt?

- (a) Help the agent locate the right part of the codebase
- (b) Establish what "correct" looks like for this specific task
- (c) Make the agent's summary sound more confident and detailed
- (d) State what the agent is and isn't allowed to touch

**A3.** Per Chapter 3, what does it mean for an agent's output to be
"confidently wrong"?

- (a) The agent hedges its language whenever it's uncertain about a
  change
- (b) The agent's output is stated with the same tone and formatting
  whether it's actually right or actually wrong, so tone carries no
  reliable signal
- (c) The agent refuses to make a change unless it is fully certain
- (d) The agent flags every risky change with an explicit warning
  comment

**A4.** In Chapter 3's review triage order, what should a reviewer
check *first*, before reading a single line of code?

- (a) Whether variable names follow the team's style guide
- (b) The list of changed files, compared against the prompt's stated
  boundary
- (c) The total number of lines changed
- (d) Whether the commit message is well-written

---

## Part B — Concept / Short Answer

Answer in your own words, in full sentences.

**B1.** Chapter 1 says "autocomplete predicts, an agent decides."
Explain what this means mechanically, using the plan/act/observe/repeat
loop. In your answer, be specific about why the "act" step has "no
autocomplete equivalent."

**B2.** Chapter 2 distinguishes a task scoped "too small" from one
scoped "too large." Explain the real cost of each — not just "it's
inefficient" or "it's risky," but the specific mechanism each failure
produces.

**B3.** List Chapter 3's five diff-review checklist questions in your
own words. For each one, give a one-sentence explanation of the
specific failure it's designed to catch (a passing-but-wrong fix, an
out-of-scope edit, etc.).

---

## Part C — Scenario / Judgment Questions

**C1. Rank these three prompts.** A teammate is about to hand a coding
agent one of the following three prompts for the same underlying bug —
a shopping cart total that double-counts a promo discount when a user
applies two stackable codes in the same session. Rank them from
best-scoped to worst-scoped, and justify the ranking using Chapter 2's
concepts (context, scope, boundary, acceptance criterion) — not just a
gut feeling about which "sounds better."

- **Prompt X:** "Users say the cart total is wrong sometimes when they
  use promo codes. Fix it."
- **Prompt Y:** "Rework the whole promo-code system in `cart/promos.py`
  to be more robust, and fix anything else that looks off while you're
  there."
- **Prompt Z:** "In `cart/promos.py`, applying two stackable promo
  codes in the same session double-counts the second discount
  (repro: `tests/cart/test_promos.py::test_stacked_codes`). Find the
  root cause and fix only that file and its test file. Don't touch
  `cart/checkout.py` without asking first. Acceptance:
  `test_stacked_codes` passes and `pytest tests/cart/` still passes."

**C2. Diagnose the scoping failure.** An agent was given the prompt:
"Add rate limiting to the `/api/upload` endpoint, and clean up any
other issues you notice in that file while you're in there." It comes
back having added rate limiting *and* having refactored three helper
functions, renamed a shared constant that two other endpoints import,
and reformatted roughly half the file. Using Chapter 2's vocabulary,
explain specifically what was missing from the original prompt that
allowed this to happen, and rewrite the prompt so the same outcome
couldn't occur.

**C3. Apply the five-question checklist.** A prompt reads: "In
`notifications/email.py`, customers with multi-package shipments
receive a duplicate 'order shipped' email per extra package. Reproduce
with `tests/notifications/test_email.py::test_multi_package_shipment`.
Fix the root cause in `notifications/email.py`; don't touch the queue
consumer in `workers/queue.py`. Acceptance: the named test passes and
`pytest tests/notifications/` still passes." The agent returns this
diff:

```
--- a/notifications/email.py
+++ b/notifications/email.py
@@
-def send_shipped_email(order):
-    for package in order.packages:
-        _send(order.customer_email, "order_shipped", package)
+SENT_CACHE = set()
+
+def send_shipped_email(order):
+    for package in order.packages:
+        key = (order.id, package.id)
+        if key in SENT_CACHE:
+            continue
+        SENT_CACHE.add(key)
+        _send(order.customer_email, "order_shipped", package)

--- a/workers/queue.py
+++ b/workers/queue.py
@@
-RETRY_LIMIT = 3
+RETRY_LIMIT = 5
```

The named test passes, and so does `pytest tests/notifications/`.
Walk through Chapter 3's five checklist questions against this diff.
For at least two of the five, identify a concrete problem — naming the
specific line or file involved — and explain why a green test run
didn't catch it.

---

## Part D — Architecture / Production Question

**D1.** You're writing a team-wide standard for what fields every
agent prompt must include before a task is handed off (similar to what
Chapter 2's interview questions describe). List the non-negotiable
fields, and for each one, name the specific Chapters 1–3 failure it
directly guards against (e.g., guesswork from an under-specified
request, uncontrolled blast radius, an unverifiable "done" claim, a
diff nobody can trace back to a stated boundary). Then explain, in one
or two sentences, how you'd keep this standard from becoming pure
overhead on genuinely small, low-risk tasks.

---

## Answer Key

**Part A (Multiple Choice):**

1. A1 — (c)
2. A2 — (c)
3. A3 — (b)
4. A4 — (b)

**Parts B, C, and D — self-check, not a published key.**

These questions have no single correct sentence — they're graded on
whether your reasoning traces back to specific chapter content, not on
matching a exact phrase. To check your own answers:

- Compare Part B against each chapter's "Points to Remember" section
  and its `interview-questions.html` page (especially the Beginner and
  Intermediate questions, which cover the same ground in a different
  format).
- Compare Part C against Chapter 2's "Scoping the Task" and "Boundaries"
  sections, and Chapter 3's "What to Actually Check" and "Reviewing
  Efficiently, Not Evenly" sections. If your ranking in C1 puts Prompt Z
  first and can name at least three concrete things it has that X and Y
  lack (a specific file, a repro, an explicit boundary, a checkable
  acceptance condition), you've answered it well. If your C3 answer
  flags both the out-of-boundary `workers/queue.py` edit and the
  unjustified `RETRY_LIMIT` change, and questions whether an in-process
  `SENT_CACHE` set actually survives a worker restart or is shared
  across multiple worker processes (i.e., whether this is a root-cause
  fix or a symptom fix), you've applied the checklist correctly.
- Compare Part D against Chapter 2's Architect-level interview
  questions (7 and 8), which cover exactly this kind of team-standard
  design question, including the red flags for a standard that's too
  vague to audit.

If you can defend your answer against the "red flag" descriptions in
the relevant `interview-questions.html` pages, you've answered it well.
