import json
import asyncio
import importlib.util
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


class ReportManager:
    SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━"
    CHROME_EXECUTABLES = (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/local/bin/google-chrome",
        "/opt/homebrew/bin/google-chrome",
    )

    def __init__(self, report_dir=None):
        self.project_root = Path(__file__).resolve().parent.parent
        self.report_dir = Path(report_dir) if report_dir else self.project_root / "report"
        self.last_pdf_exporter = ""

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

    def build_email_body(self, summary=None, attachments=None):
        data = summary or self.parse_summary()
        attachment_names = attachments or [data["report_file"]]
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
            *[Path(attachment).name for attachment in attachment_names],
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

    def export_pdf(self, html_path=None):
        html_file = Path(html_path) if html_path else self.get_latest_report()
        if not html_file.exists():
            raise FileNotFoundError(f"HTML report not found: {html_file}")

        pdf_path = html_file.with_suffix(".pdf")
        if pdf_path.exists():
            pdf_path.unlink()

        exporters = (
            self._export_pdf_with_playwright,
            self._export_pdf_with_pyppeteer,
            self._export_pdf_with_weasyprint,
            self._export_pdf_with_chrome_cli,
        )
        errors = []
        self.last_pdf_exporter = ""
        for exporter in exporters:
            try:
                if exporter(html_file, pdf_path):
                    self.last_pdf_exporter = exporter.__name__.replace("_export_pdf_with_", "")
                    return pdf_path
            except Exception as exc:
                errors.append(f"{exporter.__name__}: {exc}")

        raise RuntimeError("PDF export failed. " + " | ".join(errors))

    def export_json(self, *args, **kwargs):
        raise NotImplementedError("JSON export is reserved for a future version.")

    def _export_pdf_with_playwright(self, html_path, pdf_path):
        if not importlib.util.find_spec("playwright"):
            return False

        from playwright.sync_api import sync_playwright

        chrome_path = self._find_local_chrome()
        with sync_playwright() as playwright:
            launch_options = {"headless": True}
            if chrome_path:
                launch_options["executable_path"] = chrome_path
            else:
                launch_options["channel"] = "chrome"
            browser = playwright.chromium.launch(**launch_options)
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1800})
                page.emulate_media(media="screen")
                page.goto(
                    html_path.resolve().as_uri(),
                    wait_until="load",
                    timeout=60000,
                )
                self._wait_for_report_rendered(page)
                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                )
            finally:
                browser.close()
        return pdf_path.exists()

    def _export_pdf_with_pyppeteer(self, html_path, pdf_path):
        if not importlib.util.find_spec("pyppeteer"):
            return False

        async def export():
            from pyppeteer import launch

            chrome_path = self._find_local_chrome()
            launch_options = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-setuid-sandbox"],
            }
            if chrome_path:
                launch_options["executablePath"] = chrome_path

            browser = await launch(launch_options)
            page = await browser.newPage()
            await page.goto(html_path.resolve().as_uri(), {"waitUntil": "networkidle0"})
            await page.pdf(
                {
                    "path": str(pdf_path),
                    "format": "A4",
                    "printBackground": True,
                }
            )
            await browser.close()

        asyncio.run(export())
        return pdf_path.exists()

    def _export_pdf_with_weasyprint(self, html_path, pdf_path):
        if not importlib.util.find_spec("weasyprint"):
            return False

        from weasyprint import HTML

        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return pdf_path.exists()

    def _export_pdf_with_chrome_cli(self, html_path, pdf_path):
        chrome_path = self._find_local_chrome()
        if not chrome_path:
            return False

        with tempfile.TemporaryDirectory(prefix="open_web_pdf_chrome_") as user_data_dir:
            command = [
                chrome_path,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                f"--user-data-dir={user_data_dir}",
                f"--print-to-pdf={pdf_path}",
                html_path.resolve().as_uri(),
            ]
            try:
                subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
            except subprocess.TimeoutExpired:
                if pdf_path.exists():
                    return True
                raise
        return pdf_path.exists()

    def _wait_for_report_rendered(self, page):
        page.wait_for_function(
            "() => document.readyState === 'complete'",
            timeout=60000,
        )
        page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
        page.wait_for_function(
            """() => {
                if (!window.echarts) {
                    return true;
                }

                const chartRoots = Array.from(
                    document.querySelectorAll('[_echarts_instance_]')
                );
                if (chartRoots.length === 0) {
                    return true;
                }

                return chartRoots.every((element) => {
                    const instance = window.echarts.getInstanceByDom(element);
                    if (!instance) {
                        return false;
                    }

                    const hasRenderedCanvas = Boolean(element.querySelector('canvas'));
                    const hasRenderedSvg = Boolean(element.querySelector('svg'));
                    const rect = element.getBoundingClientRect();
                    return (hasRenderedCanvas || hasRenderedSvg)
                        && rect.width > 0
                        && rect.height > 0;
                });
            }""",
            timeout=15000,
        )
        self._expand_detail_rows_for_pdf(page)
        self._wait_for_images_loaded(page)
        page.wait_for_timeout(1500)

    def _expand_detail_rows_for_pdf(self, page):
        page.evaluate(
            """() => {
                const buttons = Array.from(document.querySelectorAll('button[buttonIndex]'));
                buttons.forEach((button) => {
                    if (button.textContent.trim() === '展开') {
                        button.click();
                    }
                });
            }"""
        )

    def _wait_for_images_loaded(self, page):
        page.wait_for_function(
            """() => Array.from(document.images).every((image) => {
                return image.complete && image.naturalWidth > 0;
            })""",
            timeout=30000,
        )

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

    def _find_local_chrome(self):
        for executable in self.CHROME_EXECUTABLES:
            path = Path(executable)
            if path.exists():
                return str(path)
        return ""
