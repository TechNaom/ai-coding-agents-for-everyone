# Review Answer Key: flawed_pr/

Read this after doing your own review pass — not before. Six items:
five real flaws and one line that's deliberately fine.

---

## Flaw 1 — `export_csv.py`: `DictWriter.write_all()` doesn't exist

```python
writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
writer.writeheader()
writer.write_all(rows)
```

**Category:** Hallucinated API — wrong method name.

**What's actually wrong:** `csv.DictWriter` has no `write_all()`
method. The real method for writing multiple rows at once is
`writerows(rows)`. `write_all` is a plausible-sounding name — it reads
exactly like something a well-designed writer class should have — but
it was never implemented.

**Why a quick glance misses it:** `writeheader()` on the line right
above is real and spelled correctly, which lends the whole block
borrowed credibility. The two calls are visually and structurally
identical (`writer.<verb>(...)`), so nothing about the shape of the
broken line looks different from the working line next to it.

**How it's actually caught:** `hasattr(csv.DictWriter, "write_all")`
is `False` — a one-line check, or simply running `write_report()` once
against any sample data, which raises `AttributeError` immediately
every single time this function is called. This is the "cheap and
crashes reliably" category the lesson opens with.

---

## Flaw 2 — `notify.py`: `EmailMessage.set_content()` doesn't return `self`

```python
msg.set_content("See the attached weekly sales report.").add_attachment(
    csv_bytes, maintype="text", subtype="csv", filename="report.csv"
)
```

**Category:** Hallucinated API — wrong assumption about a real
method's return value (a fluent/chainable API that doesn't exist).

**What's actually wrong:** `EmailMessage.set_content()` is real and
correctly named — it mutates `msg` in place and returns `None`, the
same way most of Python's standard-library mutating methods do
(`list.append()`, `dict.update()`, etc.). Chaining `.add_attachment()`
onto its return value raises
`AttributeError: 'NoneType' object has no attribute 'add_attachment'`.
The bug isn't a wrong name at all — every name here is spelled
correctly and real. It's a wrong assumption, borrowed from libraries
where this exact chaining pattern (like pandas' `df.dropna().reset_index()`)
genuinely works.

**Why a quick glance misses it:** Method chaining is a common,
idiomatic pattern the reviewer has seen work correctly hundreds of
times in other contexts — the line reads as "well-styled, modern
code," not as a red flag.

**How it's actually caught:** Running `build_message()` once, with
real arguments, raises immediately. Nothing here survives even the
lightest real invocation — which makes it a strong argument for why
"I imported the module and it didn't error" is worthless as a
verification claim.

---

## Flaw 3 — `aggregate.py`: `statistics.average()` doesn't exist

```python
def average_order_value(records):
    if not records:
        return 0.0
    amounts = [r["amount"] for r in records]
    return statistics.average(amounts)
```

**Category:** Hallucinated API — wrong module function name, on an
untested code path.

**What's actually wrong:** The `statistics` module has no `average()`
function. The real function is `statistics.mean()`. This is a
near-miss on a real name — "average" and "mean" mean the same thing in
plain English, which is exactly what makes this the easiest kind of
hallucination to write past without noticing, and to read past too.

**Why this one is the most dangerous of the three hallucinations:**
Unlike Flaws 1 and 2, this crashes only when `average_order_value` is
actually **called**. Re-read the agent's own closing message in
`README.md`: it explicitly says the smoke test called `total_revenue()`
and `write_report()` — never `average_order_value()`. The agent's own
"I tested it" claim is technically true and still leaves this
completely unverified. This is the concrete version of the lesson's
warning that a hallucinated API surviving a shallow smoke test isn't
a hypothetical — it's the default outcome any time a test doesn't
happen to reach the exact line.

**How it's actually caught:** Not by reading the smoke-test summary
and trusting it — by actually calling `average_order_value()` yourself
with real data, which is exactly what the review harness's Check 2
does, deliberately, for every function in the PR, not just the ones
the agent mentioned testing.

---

## Flaw 4 — `aggregate.py`: `filter_week` contradicts its own docstring

```python
def week_range(as_of):
    """Return (start, end) for the 7 days STRICTLY BEFORE as_of --
    not including as_of itself, ..."""
    start = as_of - timedelta(days=7)
    return start, as_of

def filter_week(records, as_of):
    start, end = week_range(as_of)
    return [r for r in records if start <= r["date"] <= end]
```

**Category:** Logical bug — off-by-one / inclusive boundary.

**What's actually wrong:** The docstring is explicit: 7 days, not
including `as_of`. The filter uses `<=` on BOTH ends. For `as_of` =
day 10, `start` = day 3, so the inclusive range `[3, 10]` covers 8
days (3 through 10), and it includes day 10 — `as_of` itself — which
the docstring explicitly says should be excluded. The correct
condition is `start <= r["date"] < end` (7 days: 3 through 9,
excluding day 10).

**Why a quick glance misses it:** Every name here is real —
`timedelta`, comparison chaining, a list comprehension — nothing would
fail `hasattr()` or raise on import or on a normal call. It runs
cleanly and returns a plausible-looking list of records. The only way
to catch it is to compute the actual output for a concrete `as_of` and
compare against the function's own stated contract, exactly the
tracing discipline the lesson's `week_range` example walks through
line for line.

**How it's actually caught:** `trace_week_boundary()` in the review
harness builds 10 days of fake records and checks, concretely, whether
day 10 is included and whether exactly 7 records come back. It isn't
(8 records, day 10 included) — a direct, checkable contradiction of
the docstring's own promise.

---

## Flaw 5 — `notify.py`: `headers={}` is a mutable default argument

```python
def build_message(csv_path, recipients, subject="Weekly Sales Report", headers={}):
    ...
    for key, value in headers.items():
        msg[key] = value
    headers["X-Report-Built-By"] = "weekly_report_job"
```

**Category:** Logical bug — shared mutable state via a default
argument.

**What's actually wrong:** Python evaluates a default argument's value
exactly once, at function-definition time — not fresh on every call.
Every call to `build_message()` that doesn't pass its own `headers`
argument shares the exact same dict object. The first call mutates it
(adds `"X-Report-Built-By"`); the second call's own `for key, value in
headers.items()` loop then sets that header on the SECOND message too
— a header meant to be a per-call tracking marker leaks across every
subsequent call in the same process.

**Why this is the hardest of the five to catch:** It does not crash on
a single call — a one-shot smoke test (exactly the kind the agent's
own closing message describes running) cannot see it, no matter how
carefully that single call is inspected. It only becomes observable
across at least two calls in the same process, comparing the second
call's actual headers against what a fresh call should have produced.
Concretely:

```python
>>> msg1, h1 = build_message(path, ["a@x.com"])   # h1 == {"X-Report-Built-By": "weekly_report_job"}
>>> msg2, h2 = build_message(path, ["b@x.com"])   # h2 IS THE SAME DICT OBJECT as h1
>>> id(h1) == id(h2)
True
```

**How it's actually caught:** Inspecting the function's real signature
(`inspect.signature(notify.build_message).parameters["headers"].default`)
and confirming it's a mutable object — a static check that flags the
risk before you even need two calls to observe the actual leak. This
is exactly `has_mutable_default` from the exercises, applied here.

---

## Not a flaw — `aggregate.py`: `total_revenue`'s `round()`

```python
def total_revenue(records):
    # Amounts arrive as floats from the upstream JSON feed, so a raw
    # sum can carry binary floating-point noise ... Rounding to 2
    # decimals here is intentional -- this is a display value for the
    # report, not the value written back to billing records, which
    # are computed and stored separately in Decimal arithmetic
    # upstream of this module.
    return round(sum(r["amount"] for r in records), 2)
```

**Why this looks suspicious:** Chapter 3's own hook was built around
a `round()` call hiding a float-accumulation rounding bug — a reviewer
who's internalized that lesson well might reflexively flag any
`round()` near a monetary sum as the same pattern.

**Why it's actually fine here:** The comment explicitly states what
Chapter 3's flawed example never had: this is a display-only value for
a report, and the real monetary calculation and storage happen
elsewhere, in `Decimal` arithmetic, unaffected by this function. There
is no evidence in this file that this `round()` is hiding anything —
it's doing exactly what a currency-display step should do, with an
honest justification attached. Flagging it anyway, on pattern-match
alone, without checking whether the actual justification holds, is
itself a review mistake: it wastes review attention Chapter 3's
"reviewing efficiently, not evenly" section explicitly warned against
spending on a line that isn't actually the risk.

**The teaching point:** Recognizing a known bad pattern is only half
of review discipline. The other half is checking whether THIS instance
of the pattern is actually the bad case, instead of flagging on
resemblance alone — over-flagging has a real cost too, since it
trains reviewers (and teams) to eventually tune out warnings that
turn out to be noise.

---

## Summary table

| # | File | Category | Crashes on any call? | Caught by |
|---|------|----------|----------------------|-----------|
| 1 | `export_csv.py` | Hallucinated API (wrong name) | Yes, always | `hasattr()` or one real call |
| 2 | `notify.py` | Hallucinated API (wrong return-type assumption) | Yes, always | One real call |
| 3 | `aggregate.py` | Hallucinated API (wrong name, untested path) | Yes, but only if called | Calling every function, not just the ones the agent mentioned testing |
| 4 | `aggregate.py` | Logical bug (off-by-one boundary) | No | Tracing a concrete `as_of` against the docstring |
| 5 | `notify.py` | Logical bug (mutable default, cross-call leak) | No, not on one call | Inspecting the signature, or calling twice and comparing |
| — | `aggregate.py` `round()` | Not a bug | — | Checking the stated justification, not just pattern-matching |
