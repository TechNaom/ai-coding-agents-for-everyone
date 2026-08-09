"""
notify.py -- part of the "Weekly Sales Report" PR.

Builds and (in a real deployment) sends the email carrying the weekly
report CSV to a distribution list. `send_report` is left disconnected
from a real SMTP server in this PR on purpose -- see README.md -- so
`build_message` is the piece actually under review here.
"""
from email.message import EmailMessage


def build_message(csv_path, recipients, subject="Weekly Sales Report", headers={}):
    """
    Build an EmailMessage with the report CSV attached, addressed to
    `recipients`, with any extra `headers` set on it (e.g. a tracking
    header set by the caller).
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["To"] = ", ".join(recipients)

    for key, value in headers.items():
        msg[key] = value
    headers["X-Report-Built-By"] = "weekly_report_job"

    with open(csv_path, "rb") as f:
        csv_bytes = f.read()

    msg.set_content("See the attached weekly sales report.").add_attachment(
        csv_bytes, maintype="text", subtype="csv", filename="report.csv"
    )
    return msg
