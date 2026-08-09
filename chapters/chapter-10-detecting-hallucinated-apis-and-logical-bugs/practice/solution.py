"""
Chapter 10 Practice: Find the Flaw in Six Short Snippets (solution)

Six small, plausible-looking code snippets, each with exactly one
deliberate flaw -- some hallucinated APIs, some logical bugs, spanning
the categories the lesson names (wrong method name, hallucinated
argument, wrong-return-type assumption, off-by-one, inverted boolean,
operator precedence). No pandas, no requests, no network -- just
Python.

    python3 --version
    python3 starter.py

Before running it, read each of the six SNIPPETS below and, for each
one, predict: (1) is the flaw a hallucinated API or a logical bug, and
(2) what's the one thing wrong. Write your six predictions down. Then
run the script -- it prints each snippet followed by its own answer
key -- and compare.
"""

SNIPPETS = [
    {
        "title": "Snippet 1 -- the requests call with a familiar-sounding argument",
        "code": '''\
import requests

def fetch_with_retries(url):
    return requests.get(url, timeout=5, retries=3)
''',
        "category": "Hallucinated API (nonexistent argument)",
        "flaw": (
            "requests.get() has no `retries` keyword argument -- it isn't part of "
            "requests' real signature, which passes through to Session.request(). "
            "Retrying a request in `requests` requires wiring up a Session with an "
            "HTTPAdapter and a urllib3 Retry object, or writing your own retry loop; "
            "there's no single keyword that does it. `retries=3` reads exactly like "
            "something requests SHOULD have, which is exactly why it's a plausible "
            "hallucination -- and it raises TypeError the instant this line actually runs."
        ),
    },
    {
        "title": "Snippet 2 -- the os.path check that sounds like it should exist",
        "code": '''\
import os

def is_usable_path(path):
    return os.path.exists_and_readable(path)
''',
        "category": "Hallucinated API (wrong method name)",
        "flaw": (
            "os.path has no exists_and_readable() function -- the real module exposes "
            "os.path.exists() and os.access(path, os.R_OK) as two SEPARATE checks; "
            "there's no single combined convenience function with this name. This is a "
            "structurally-plausible name (it reads like a real, well-designed API) that "
            "simply was never implemented. AttributeError on the first real call."
        ),
    },
    {
        "title": "Snippet 3 -- the dict lookup that assumes a fallback that isn't there",
        "code": '''\
def get_config_value(config, key):
    return config.get_or_default(key, "unset")
''',
        "category": "Hallucinated API (wrong method name)",
        "flaw": (
            "Python's dict has no get_or_default() method -- the real, equivalent method "
            "is just dict.get(key, default), which already does exactly what "
            "get_or_default's name promises. This is a near-miss on a real method's "
            "actual name, not a completely invented concept -- the kind of hallucination "
            "that's especially easy to skim past because SOMETHING with roughly that "
            "shape genuinely does exist, just under a different name."
        ),
    },
    {
        "title": "Snippet 4 -- the discount check that reads right and runs backwards",
        "code": '''\
def gets_bulk_discount(order):
    # Orders of 10 or more items get a bulk discount
    return order.item_count < 10
''',
        "category": "Logical bug (inverted condition)",
        "flaw": (
            "The comment says 10 or more items qualifies; the code returns True for "
            "FEWER than 10 items -- the comparison operator is backwards relative to the "
            "comment's own stated intent. This runs cleanly, returns a real boolean, and "
            "will pass any test that only checks a small order (which correctly returns "
            "False for the WRONG reason) without ever checking a 10+-item order, which "
            "is exactly the case this function exists to handle correctly."
        ),
    },
    {
        "title": "Snippet 5 -- the moving-average loop with a boundary that's off by one",
        "code": '''\
def last_three_average(values):
    """Average of the most recent 3 values."""
    window = values[-3:-1]
    return sum(window) / len(window)
''',
        "category": "Logical bug (off-by-one / slicing boundary)",
        "flaw": (
            "values[-3:-1] is a slicing mistake -- it takes only the 2 values BEFORE the "
            "last one (indices -3 and -2), excluding the most recent value entirely, "
            "instead of the last 3 values. The correct slice for 'the most recent 3 "
            "values' is values[-3:] (no upper bound at all). This runs without error and "
            "returns a plausible-looking average of the wrong 2 numbers -- it will never "
            "raise, and a test that only checks the return value is roughly the right "
            "MAGNITUDE could miss this the first several times."
        ),
    },
    {
        "title": "Snippet 6 -- the access check with precedence that doesn't do what it reads like",
        "code": '''\
def can_edit(user, doc):
    # Admins can always edit; otherwise the doc owner can edit if it's unlocked
    return user.is_admin or user.id == doc.owner_id and not doc.locked
''',
        "category": "Logical bug (operator precedence, reads correct but is a trap)",
        "flaw": (
            "`and` binds tighter than `or` in Python, so this actually parses as "
            "`user.is_admin or (user.id == doc.owner_id and not doc.locked)` -- which "
            "HAPPENS to match the comment's intent exactly as written. That's the trap: "
            "it's correct today, by accident of how it happens to be phrased, with no "
            "parentheses making the grouping explicit. The instant someone reorders the "
            "clauses (e.g. adds `or doc.is_public` before the `and`) without adding "
            "parentheses, the actual grouping can silently stop matching the intended "
            "one. Flag missing parentheses around mixed and/or even when the current "
            "precedence happens to produce the right answer."
        ),
    },
]


def main():
    for i, s in enumerate(SNIPPETS, start=1):
        print(f"\n{'=' * 70}")
        print(f"Snippet {i}: {s['title']}")
        print("=" * 70)
        print(s["code"])
        print("--- ANSWER KEY ---")
        print(f"Category: {s['category']}")
        print(f"Flaw: {s['flaw']}")


if __name__ == "__main__":
    main()
