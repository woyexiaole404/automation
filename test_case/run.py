import os
import sys
import unittest
from datetime import datetime
from pathlib import Path


TEST_CASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_CASE_DIR.parent
DEFAULT_TEST_FILES = ("open_web/test_login.py",)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from BeautifulReport import BeautifulReport
from base.project_path import report_path


def _discover_test_files():
    return sorted(path.relative_to(TEST_CASE_DIR).as_posix() for path in TEST_CASE_DIR.rglob("test_*.py"))


def _split_env_list(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _normalize_test_file(file_name):
    file_name = file_name.strip().replace("\\", "/").lstrip("./")
    if file_name.endswith(".py"):
        return file_name
    return f"{file_name}.py"


def _selected_test_files(discovered_files):
    explicit_files = [_normalize_test_file(item) for item in _split_env_list(os.environ.get("TEST_FILES"))]
    skip_files = set(_normalize_test_file(item) for item in _split_env_list(os.environ.get("TEST_SKIP_FILES")))
    run_external = os.environ.get("RUN_EXTERNAL_TESTS") == "1"
    test_scope = os.environ.get("TEST_SCOPE", "").lower()

    if explicit_files:
        candidates = [file_name for file_name in explicit_files if file_name in discovered_files]
    elif run_external or test_scope == "all":
        candidates = discovered_files
    else:
        candidates = [file_name for file_name in DEFAULT_TEST_FILES if file_name in discovered_files]

    selected_files = [file_name for file_name in candidates if file_name not in skip_files]
    skipped_files = {}

    for file_name in discovered_files:
        if file_name in selected_files:
            continue
        if file_name in skip_files:
            skipped_files[file_name] = "TEST_SKIP_FILES 指定跳过"
        elif explicit_files:
            skipped_files[file_name] = "未包含在 TEST_FILES 中"
        elif not run_external and test_scope != "all" and file_name not in DEFAULT_TEST_FILES:
            if file_name == "test_local_auth.py":
                skipped_files[file_name] = "旧 local_auth 兼容入口，已迁移为 open_web/test_login.py，默认不重复运行"
            else:
                skipped_files[file_name] = "旧外部 UI、接口或小程序测试，默认不在本地入口运行"

    return selected_files, skipped_files


def _build_suite(test_files):
    suite = unittest.TestSuite()
    for file_name in test_files:
        test_path = TEST_CASE_DIR / file_name
        suite.addTests(
            unittest.defaultTestLoader.discover(
                start_dir=str(test_path.parent),
                pattern=test_path.name,
            )
        )
    return suite


def _configure_beautiful_report_template():
    template_path = PROJECT_ROOT / "BeautifulReport" / "template" / "template"
    if template_path.exists():
        BeautifulReport.config_tmp_path = str(template_path)


def run():
    discovered_files = _discover_test_files()
    selected_files, skipped_files = _selected_test_files(discovered_files)

    print("Discovered test files:")
    for file_name in discovered_files:
        print(f"  - {file_name}")

    print("Selected test files:")
    for file_name in selected_files:
        print(f"  - {file_name}")

    print("Skipped test files:")
    for file_name, reason in skipped_files.items():
        print(f"  - {file_name}: {reason}")

    if not selected_files:
        raise RuntimeError("No test files selected. Set TEST_FILES or TEST_SCOPE=all.")

    _configure_beautiful_report_template()
    suite_tests = _build_suite(selected_files)
    report_output_dir = report_path()
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"automation_{now}"
    BeautifulReport(suite_tests).report(
        description="自动化测试报告",
        filename=filename,
        log_path=str(report_output_dir),
    )


if __name__ == "__main__":
    run()
