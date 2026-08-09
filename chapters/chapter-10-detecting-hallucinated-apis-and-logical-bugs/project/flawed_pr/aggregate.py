"""
aggregate.py -- part of the "Weekly Sales Report" PR.

Aggregates raw daily sales records (list of dicts with "date" and
"amount" keys) into the numbers the weekly report needs: which records
fall in the reporting week, the total revenue, and the average order
value.
"""
import statistics
from datetime import timedelta


def week_range(as_of):
    """
    Return (start, end) for the 7 days STRICTLY BEFORE as_of -- not
    including as_of itself, since today's sales are still coming in
    and shouldn't be counted in a "last week" total.
    """
    start = as_of - timedelta(days=7)
    return start, as_of


def filter_week(records, as_of):
    """Return only the records that fall in the reporting week."""
    start, end = week_range(as_of)
    return [r for r in records if start <= r["date"] <= end]


def total_revenue(records):
    """Total revenue across the given records, rounded to whole cents."""
    # Amounts arrive as floats from the upstream JSON feed, so a raw
    # sum can carry binary floating-point noise (e.g. 40.31999999999).
    # Rounding to 2 decimals here is intentional -- this is a display
    # value for the report, not the value written back to billing
    # records, which are computed and stored separately in Decimal
    # arithmetic upstream of this module.
    return round(sum(r["amount"] for r in records), 2)


def average_order_value(records):
    """Average order amount across the given records."""
    if not records:
        return 0.0
    amounts = [r["amount"] for r in records]
    return statistics.average(amounts)
