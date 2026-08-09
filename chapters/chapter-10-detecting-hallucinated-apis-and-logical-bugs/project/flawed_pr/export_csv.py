"""
export_csv.py -- part of the "Weekly Sales Report" PR.

Writes the aggregated weekly report rows to a CSV file on disk.
"""
import csv

FIELDNAMES = ["date", "amount"]


def write_report(rows, out_path):
    """
    Write `rows` (a list of dicts with keys matching FIELDNAMES) to
    `out_path` as CSV, with a header row.
    """
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.write_all(rows)
