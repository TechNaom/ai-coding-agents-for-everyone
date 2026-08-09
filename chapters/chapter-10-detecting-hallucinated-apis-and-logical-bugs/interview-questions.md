# Chapter 10 Interview Questions: Detecting Hallucinated APIs and Logical Bugs

These mirror `interview-questions.html` exactly. Grouped by level. Each
includes a strong answer, a red flag, and a natural follow-up an
interviewer might ask next.

---

### 1. (Beginner) What's the actual difference between a hallucinated API and a typo?

**Strong answer:** A typo looks broken -- `improt pandas` or
`df.sort_vlaues()` fails immediately and obviously, and nobody would
mistake it for real code. A hallucinated API looks exactly like a real
call: correctly spelled, correctly formatted, syntactically valid,
often sitting right next to a genuinely real argument on the same line
(like `ignore_na=True` next to the real `na_position="last"`). The
danger isn't that it looks wrong -- it's that it looks completely
right and is still not real.

**Red flags:** Treats "hallucinated API" as a synonym for "syntax
error" or "misspelled name," missing that the defining trait is
plausibility, not brokenness.

**Follow-up:** "If a hallucinated call is syntactically perfect,
what's the one thing that reliably catches it?"

---

### 2. (Beginner) Name the three situations this chapter says hallucinated APIs cluster around, and give a one-sentence reason for each.

**Strong answer:** First, less-common libraries -- less training data
means less real signal pulling a prediction toward the actual API
surface. Second, APIs that changed after the model's training data --
a removed or renamed method can still be exactly what the model
predicts, because that call shape was genuinely common in what it
learned from. Third, structural similarity to a more common library --
a model reaching for a call shape (like method chaining) that's
idiomatic in one library can confidently apply it to a different
library that doesn't actually support it.

**Red flags:** Can only name one or two, or explains them all as "the
model doesn't know the library," without the specific mechanism behind
each.

**Follow-up:** "Which of these three would you expect to get WORSE
over time, and which would you expect to stay roughly constant?"

---

### 3. (Intermediate) Walk through why "the code imports cleanly" is not sufficient evidence that a specific call in it is real.

**Strong answer:** Importing a module only proves the package is
installed and the module-level code runs without error -- it says
nothing about whether a specific method, attribute, or keyword
argument used later in the file actually exists, because Python (and
most languages) don't validate a method call's existence until that
exact line actually executes. A hallucinated keyword argument on a
real function, or a hallucinated method on a real class, will sit
completely silent through an import and even through calls to other,
real methods on the same object -- it only surfaces the moment that
exact line runs. This is why the chapter's second check is "does it
actually run with real arguments," not "does it import."

**Red flags:** Conflates "imports without error" with "is correct," or
can't explain why a hallucinated argument specifically survives an
import.

**Follow-up:** "Given that, what's the risk of only running a 'smoke
test' that imports every module and calls one or two happy-path
functions?"

---

### 4. (Intermediate) A teammate says a suspiciously confident comment explaining why an unusual API call works is reassuring -- "at least they explained their reasoning." What's your response?

**Strong answer:** A comment explaining why a line works is not
independent verification that it actually works -- if the code and the
comment were both produced by the same generation process, the comment
is just more plausible-sounding text conditioned on the same context
that produced the (possibly hallucinated) call itself, not a separate
check against the real library. A confident explanation should raise
your attention, not lower it, precisely because Chapter 5 already
established that a model's tone carries no reliable correlation with
whether it's actually right. The comment being present and articulate
is not evidence; running the call against the real library is
evidence.

**Red flags:** Treats a well-written explanatory comment as
corroborating evidence, without recognizing it can come from the
identical unverified source as the code it's explaining.

**Follow-up:** "Is there ANY circumstance where a comment like that
should increase your confidence rather than your suspicion?"

---

### 5. (Senior) The mutable-default-argument example (`headers={}`) passes a single-call smoke test cleanly. Explain exactly why, and what kind of test would actually catch it.

**Strong answer:** Python evaluates a default argument's value exactly
once, at function-definition time, not fresh on every call -- so a
single call to `build_message()` gets a fresh-looking empty dict
(since it's the first and only mutation so far) and returns a result
that looks entirely correct. The bug only becomes observable across
MULTIPLE calls in the same process, where the second call's `headers`
starts from whatever the first call already mutated it into, not from
a fresh `{}`. A test that calls the function once, checks its output,
and moves on will never see this; a test needs to call it at least
twice in sequence and check that the second call's output doesn't
carry state from the first.

**Red flags:** Describes the mutable-default gotcha in the abstract
without connecting it to WHY a single-call test specifically misses
it, or thinks any test at all would catch it.

**Follow-up:** "If this function were called once per request in a
long-running web server process, how would this bug actually manifest
in production, and how long would it take to notice?"

---

### 6. (Senior) Compare the actual cost of catching a hallucinated API versus catching a logical bug like an inverted boolean condition. Are they the same kind of review problem?

**Strong answer:** No -- they require genuinely different verification
strategies, even though both survive a shallow read. A hallucinated
API has a binary, checkable answer: it either appears in `dir()`/real
documentation or it doesn't, and a single `hasattr()` call or one real
function call settles it definitively and cheaply, independent of the
surrounding logic. A logical bug like an inverted condition has no
such lookup -- `customer.is_first_purchase or not
customer.account_in_good_standing` is entirely valid, real,
correctly-called code, and the only way to catch it is to trace
specific concrete values (a first-time buyer in good standing,
specifically) through the actual logic and compare the result against
intent. The first is a fact-checking problem; the second is a
reasoning-tracing problem, and conflating them leads to reviewers who
are good at spotting fake APIs but still get burned by correct-looking
wrong logic.

**Red flags:** Claims they're basically the same problem ("just read
carefully for both"), missing that one has a mechanical,
source-of-truth check and the other fundamentally doesn't.

**Follow-up:** "If you had to automate ONE of these two checks in CI,
which is actually feasible to automate well, and why?"

---

### 7. (Architect) Design a lightweight, repeatable process your team could adopt so hallucinated APIs and logical bugs are caught before merge, without turning every review into a multi-hour audit.

**Strong answer:** Two cheap, separate gates, matched to the two
different failure types. For hallucinated APIs: require that any
unfamiliar or newly-introduced library call in a diff actually be
executed (not just imported) against the real installed dependency
during review or CI -- a `hasattr()`/introspection check plus one real
invocation with realistic arguments is seconds of work per call and
catches the entire category deterministically. For logical bugs:
require the diff's own PR description to state, in one sentence, what
boundary case was traced by hand (not just what test passed) for any
changed conditional, loop bound, or default-argument -- forcing the
author to name a boundary case surfaces most inverted-logic and
off-by-one bugs during the diff's own authoring, and gives a reviewer
something concrete to independently re-check rather than re-deriving
the whole function from scratch. Neither gate requires reviewing every
line with equal intensity -- both are targeted at exactly the two
things a green test suite and a clean import don't already prove.

**Red flags:** Proposes "review more carefully" or "add more tests"
without a specific, low-cost mechanism, or proposes one gate that
tries to catch both failure types at once despite them needing
different verification strategies.

**Follow-up:** "How would you keep the 'name the boundary case you
traced' requirement from becoming a box-checking formality that gets
filled in with something vague?"

---

### 8. (Architect) A stakeholder asks: "If the model is this likely to hallucinate an API or get logic backwards, why trust agent-generated code at all?" How do you respond?

**Strong answer:** The honest framing isn't "trust or don't trust" --
it's that agent-generated code is a claim, exactly like a human
colleague's PR is a claim, and both require verification proportional
to the risk of being wrong; the difference this course has been
building toward since Chapter 3 is that an agent's claim doesn't carry
the same social-pressure filtering a human's does, so more of the
verification burden falls explicitly on process rather than on trust
in the author. Concretely: a hallucinated API is one of the cheapest
classes of bug to catch mechanically (introspection, one real call)
precisely because it's binary -- real or not real -- so a team that
builds that check into review or CI removes most of the actual risk at
very low cost. Logical bugs are harder and always were, with or
without an agent involved -- the same boundary-tracing discipline that
catches a human's off-by-one error catches an agent's. The right
takeaway isn't "trust agent code less than human code" or "trust it
the same" -- it's "verify agent code with the same rigor a good team
already applies to human code, using checks specifically shaped for
where agent-generated code tends to fail."

**Red flags:** Either oversells agent code as trustworthy-by-default,
or dismisses it as categorically unreliable -- both skip the actual
point, which is that verification cost is the right lever, not blanket
trust or distrust.

**Follow-up:** "Does this mean agent-generated code should go through
MORE review than human code, less, or the same amount -- and does
your answer change for a hallucinated-API-prone task versus a
well-trodden one?"

## Strategy Tips

- If asked to spot a hallucinated API live, reach for `hasattr()`/
  `dir()` or an actual call with real arguments first -- don't reason
  from memory about whether a call "sounds right," the exact trap this
  chapter is about.
- If asked about logic review in general, name the specific boundary
  case you'd trace by hand (the first-time buyer, the eighth day, the
  second call in the same process) rather than saying "I'd read it
  carefully" -- carefulness alone doesn't catch precedence or
  off-by-one bugs, tracing a concrete value does.
