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
    attachments = [report_path]

    try:
        pdf_path = report_manager.export_pdf(report_path)
        attachments = [pdf_path, report_path]
        print(f"PDF report exported: {pdf_path}")
    except Exception as exc:
        print(f"PDF export failed, continue with HTML report only: {exc}")

    subject = report_manager.build_email_subject(summary)
    body = report_manager.build_email_body(summary, attachments=attachments)
    send_email(subject=subject, body=body, attachment_path=attachments)
    print(f"Report email sent: {', '.join(str(item) for item in attachments)}")


if __name__ == "__main__":
    main()
