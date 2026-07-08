import json
import os
import re
from datetime import datetime
from pathlib import Path


class ReportManager:
    SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━"

    def __init__(self, report_dir=None):
        self.project_root = Path(__file__).resolve().parent.parent
        self.report_dir = Path(report_dir) if report_dir else self.project_root / "report"

    def get_latest_report(self):
        reports = sorted(
            self.report_dir.glob("*.html"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not reports:
            raise FileNotFoundError(
                f"No BeautifulReport html file found under {self.report_dir}"
            )
        return reports[0]

    def parse_summary(self, report_path=None):
        report = Path(report_path) if report_path else self.get_latest_report()
        result_data = self._load_result_data(report)
        summary = {
            "report_path": report,
            "report_file": report.name,
            "total": int(result_data.get("testAll", 0)),
            "passed": int(result_data.get("testPass", 0)),
            "failed": int(result_data.get("testFail", 0)),
            "error": int(result_data.get("testError", 0)),
            "skipped": int(result_data.get("testSkip", 0)),
            "begin_time": result_data.get("beginTime", ""),
            "total_time": result_data.get("totalTime", ""),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        summary["status"] = self._get_status(summary)
        return summary

    def build_email_subject(self, summary=None):
        data = summary or self.parse_summary()
        return f"【Open Web】自动化测试报告 - {data['status']}"

    def build_email_body(self, summary=None):
        data = summary or self.parse_summary()
        lines = [
            self.SEPARATOR,
            "Open Web 自动化测试报告",
            self.SEPARATOR,
            "",
            "执行状态：",
            "",
            f"{'✅' if data['status'] == 'SUCCESS' else '❌'} {data['status']}",
            "",
            "执行时间：",
            "",
            data["generated_at"],
            "",
            "测试统计：",
            "",
            f"Total：{data['total']}",
            f"Passed：{data['passed']}",
            f"Failed：{data['failed']}",
            f"Skipped：{data['skipped']}",
            f"Error：{data['error']}",
            "",
            f"Runner：{os.environ.get('RUNNER_NAME', '-')}",
            f"Branch：{self._get_branch()}",
            f"Commit：{self._get_short_sha()}",
            f"Workflow：{os.environ.get('GITHUB_WORKFLOW', '-')}",
            f"GitHub Actions：{self.build_github_run_url() or '-'}",
            "",
            "附件：",
            "",
            data["report_file"],
            "",
            "说明：",
            "",
            "由于邮件客户端限制，",
            "HTML 报告可能无法完整显示。",
            "请优先：",
            "",
            "1. 下载附件查看。",
            "2. 或到 GitHub Artifacts 下载。",
            "",
            self.SEPARATOR,
        ]
        return "\n".join(lines)

    def build_github_run_url(self):
        server_url = os.environ.get("GITHUB_SERVER_URL")
        repository = os.environ.get("GITHUB_REPOSITORY")
        run_id = os.environ.get("GITHUB_RUN_ID")
        if server_url and repository and run_id:
            return f"{server_url}/{repository}/actions/runs/{run_id}"
        return ""

    def export_pdf(self, *args, **kwargs):
        raise NotImplementedError("PDF export is reserved for a future version.")

    def export_json(self, *args, **kwargs):
        raise NotImplementedError("JSON export is reserved for a future version.")

    def _load_result_data(self, report_path):
        content = report_path.read_text(encoding="utf-8")
        match = re.search(
            r"var\s+resultData\s*=\s*(\{.*?\})\s*;",
            content,
            re.DOTALL,
        )
        if not match:
            raise RuntimeError(f"BeautifulReport resultData not found: {report_path}")
        return json.loads(match.group(1))

    def _get_status(self, summary):
        if summary["failed"] > 0 or summary["error"] > 0:
            return "FAILED"
        return "SUCCESS"

    def _get_branch(self):
        ref_name = os.environ.get("GITHUB_REF_NAME")
        if ref_name:
            return ref_name

        ref = os.environ.get("GITHUB_REF", "")
        prefixes = ("refs/heads/", "refs/tags/")
        for prefix in prefixes:
            if ref.startswith(prefix):
                return ref[len(prefix):]
        return ref or "-"

    def _get_short_sha(self):
        sha = os.environ.get("GITHUB_SHA", "-")
        if sha == "-":
            return sha
        return sha[:8]
