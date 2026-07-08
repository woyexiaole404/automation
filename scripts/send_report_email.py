import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from base.email_sender import send_email
from base.report_manager import ReportManager


def main():
    report_manager = ReportManager()
    summary = report_manager.parse_summary()
    report_path = summary["report_path"]
    subject = report_manager.build_email_subject(summary)
    body = report_manager.build_email_body(summary)
    send_email(subject=subject, body=body, attachment_path=report_path)
    print(f"Report email sent: {report_path}")


if __name__ == "__main__":
    main()
