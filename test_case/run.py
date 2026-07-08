import argparse
import sys
import unittest
from datetime import datetime
from pathlib import Path


TEST_CASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_CASE_DIR.parent
DEFAULT_PROJECT = "open_web"
PROJECT_TEST_DIRS = {
    "open_web": TEST_CASE_DIR / "open_web",
}

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from BeautifulReport import BeautifulReport
from base.project_path import report_path


def _project_test_dir(project):
    try:
        return PROJECT_TEST_DIRS[project]
    except KeyError as error:
        supported_projects = ", ".join(sorted(PROJECT_TEST_DIRS))
        raise ValueError(
            f"Unsupported project '{project}'. Supported projects: {supported_projects}."
        ) from error


def _test_pattern(module):
    if module is None:
        return "test_*.py"
    if not module.isidentifier():
        raise ValueError(
            f"Invalid module '{module}'. Use a Python module name such as 'login'."
        )
    return f"test_{module}.py"


def _available_modules(project=DEFAULT_PROJECT):
    project_test_dir = _project_test_dir(project)
    return {
        path.stem.removeprefix("test_"): path.relative_to(TEST_CASE_DIR).as_posix()
        for path in sorted(project_test_dir.glob("test_*.py"))
        if path.is_file()
    }


def _validate_module(project, module):
    if module is None:
        return

    _test_pattern(module)
    available_modules = _available_modules(project)
    if module not in available_modules:
        supported_modules = ", ".join(sorted(available_modules)) or "none"
        raise ValueError(
            f"Unsupported module '{module}' for project '{project}'. "
            f"Available modules: {supported_modules}."
        )


def _discover_test_files(project=DEFAULT_PROJECT, module=None):
    _validate_module(project, module)
    project_test_dir = _project_test_dir(project)
    pattern = _test_pattern(module)
    return sorted(
        path.relative_to(TEST_CASE_DIR).as_posix()
        for path in project_test_dir.rglob(pattern)
    )


def _build_suite(project=DEFAULT_PROJECT, module=None):
    _validate_module(project, module)
    project_test_dir = _project_test_dir(project)
    return unittest.defaultTestLoader.discover(
        start_dir=str(project_test_dir),
        pattern=_test_pattern(module),
        top_level_dir=str(TEST_CASE_DIR),
    )


def _parse_args():
    parser = argparse.ArgumentParser(description="Run project tests with BeautifulReport.")
    parser.add_argument(
        "--project",
        choices=sorted(PROJECT_TEST_DIRS),
        default=DEFAULT_PROJECT,
        help=f"Project to run (default: {DEFAULT_PROJECT}).",
    )
    parser.add_argument(
        "--module",
        help="Module name without the test_ prefix or .py suffix, for example: login.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List runnable modules without executing tests or generating a report.",
    )
    return parser.parse_args()


def _configure_beautiful_report_template():
    template_path = PROJECT_ROOT / "BeautifulReport" / "template" / "template"
    if template_path.exists():
        BeautifulReport.config_tmp_path = str(template_path)


def run(project=DEFAULT_PROJECT, module=None):
    discovered_files = _discover_test_files(project, module)

    print("Discovered test files:")
    for file_name in discovered_files:
        print(f"  - {file_name}")
    sys.stdout.flush()

    if not discovered_files:
        pattern = _test_pattern(module)
        project_test_dir = _project_test_dir(project)
        raise RuntimeError(f"No {pattern} files found under {project_test_dir}.")

    _configure_beautiful_report_template()
    suite_tests = _build_suite(project, module)
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


def list_modules(project=DEFAULT_PROJECT):
    available_modules = _available_modules(project)
    print(f"Available modules for {project}:")
    if not available_modules:
        print("  - none")
        return 0

    for module, file_name in sorted(available_modules.items()):
        print(f"  - {module}: {file_name}")
    return 0


if __name__ == "__main__":
    args = _parse_args()
    try:
        if args.list:
            sys.exit(list_modules(project=args.project))
        sys.exit(run(project=args.project, module=args.module))
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
