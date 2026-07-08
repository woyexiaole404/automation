import os
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from base.email_sender import send_email


REPORT_DIR = PROJECT_ROOT / "report"


def find_latest_report():
    reports = sorted(
        REPORT_DIR.glob("*.html"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not reports:
        raise FileNotFoundError(f"No BeautifulReport html file found under {REPORT_DIR}")
    return reports[0]


def get_ci_status():
    status = os.environ.get("CI_TEST_STATUS", "unknown").strip().lower()
    if status == "success":
        return "成功"
    if status == "failure":
        return "失败"
    return "未知"


def get_run_url():
    server_url = os.environ.get("GITHUB_SERVER_URL")
    repository = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    if server_url and repository and run_id:
        return f"{server_url}/{repository}/actions/runs/{run_id}"
    return ""


def build_email(report_path):
    status = get_ci_status()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"Open Web 自动化测试报告 - {status} - {now}"

    lines = [
        "Open Web 自动化测试执行完成。",
        "",
        f"测试状态：{status}",
        f"报告文件：{report_path.name}",
        "",
        "GitHub Actions 信息：",
        f"Repository：{os.environ.get('GITHUB_REPOSITORY', '-')}",
        f"Workflow：{os.environ.get('GITHUB_WORKFLOW', '-')}",
        f"Run ID：{os.environ.get('GITHUB_RUN_ID', '-')}",
        f"Run Number：{os.environ.get('GITHUB_RUN_NUMBER', '-')}",
        f"Run URL：{get_run_url() or '-'}",
        f"Ref：{os.environ.get('GITHUB_REF', '-')}",
        f"SHA：{os.environ.get('GITHUB_SHA', '-')}",
        "",
        "BeautifulReport HTML 已作为附件发送。",
    ]
    return subject, "\n".join(lines)


def main():
    report_path = find_latest_report()
    subject, body = build_email(report_path)
    send_email(subject=subject, body=body, attachment_path=report_path)
    print(f"Report email sent: {report_path}")


if __name__ == "__main__":
    main()
