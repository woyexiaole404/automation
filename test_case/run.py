import sys
import unittest
from datetime import datetime
from pathlib import Path


TEST_CASE_DIR = Path(__file__).resolve().parent
OPEN_WEB_TEST_DIR = TEST_CASE_DIR / "open_web"
PROJECT_ROOT = TEST_CASE_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from BeautifulReport import BeautifulReport
from base.project_path import report_path


def _discover_test_files():
    return sorted(
        path.relative_to(TEST_CASE_DIR).as_posix()
        for path in OPEN_WEB_TEST_DIR.rglob("test_*.py")
    )


def _build_suite():
    return unittest.defaultTestLoader.discover(
        start_dir=str(OPEN_WEB_TEST_DIR),
        pattern="test_*.py",
        top_level_dir=str(TEST_CASE_DIR),
    )


def _configure_beautiful_report_template():
    template_path = PROJECT_ROOT / "BeautifulReport" / "template" / "template"
    if template_path.exists():
        BeautifulReport.config_tmp_path = str(template_path)


def run():
    discovered_files = _discover_test_files()

    print("Discovered test files:")
    for file_name in discovered_files:
        print(f"  - {file_name}")

    if not discovered_files:
        raise RuntimeError(f"No test_*.py files found under {OPEN_WEB_TEST_DIR}.")

    _configure_beautiful_report_template()
    suite_tests = _build_suite()
    report_output_dir = report_path()
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"automation_{now}"
    report_file = report_output_dir / f"{filename}.html"
    report = BeautifulReport(suite_tests)
    report.report(
        description="自动化测试报告",
        filename=filename,
        log_path=str(report_output_dir),
    )
    print("Test summary:")
    print(f"  total: {report.testsRun}")
    print(f"  passed: {report.success_count}")
    print(f"  failed: {report.failure_count}")
    print(f"  error: {report.error_count}")
    print(f"  report: {report_file}")
    return 1 if report.failure_count or report.error_count else 0


if __name__ == "__main__":
    sys.exit(run())
