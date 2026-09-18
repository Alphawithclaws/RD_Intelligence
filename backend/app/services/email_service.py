import os

import resend
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("REPORT_FROM_EMAIL")
TO_EMAIL = os.getenv("REPORT_TO_EMAIL")


def send_report(report_file):
    if not API_KEY:
        raise ValueError(
            "RESEND_API_KEY is missing from .env"
        )

    if not FROM_EMAIL:
        raise ValueError(
            "REPORT_FROM_EMAIL is missing from .env"
        )

    if not TO_EMAIL:
        raise ValueError(
            "REPORT_TO_EMAIL is missing from .env"
        )

    if not report_file:
        raise ValueError(
            "Report file was not provided."
        )

    report_file = str(report_file)

    with open(
        report_file,
        "r",
        encoding="utf-8",
    ) as f:
        html_content = f.read()

    resend.api_key = API_KEY

    params = {
        "from": FROM_EMAIL,
        "to": [TO_EMAIL],
        "subject": "Reliance Digital Intelligence — Daily Competitor Report",
        "html": html_content,
    }

    response = resend.Emails.send(params)

    print(
        f"Report emailed successfully: {response}"
    )

    return response