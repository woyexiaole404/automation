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
from base.dependency_manager import DependencyAwareSuite, DependencyManager
from base.project_path import report_path
from base.test_metadata import get_metadata_from_test
from base.test_suite_manager import TestSuiteManager
from base.test_tag_manager import TestTagManager


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


def _suite_modules(project, suite):
    if suite is None:
        return None

    available_modules = _available_modules(project)
    return TestSuiteManager().validate_suite(suite, available_modules)


def _discover_test_files(project=DEFAULT_PROJECT, module=None, suite=None, tag=None):
    _validate_module(project, module)
    suite_modules = _suite_modules(project, suite)
    tag_modules = _tag_modules(project, tag)
    project_test_dir = _project_test_dir(project)
    pattern = _test_pattern(module)
    discovered_files = {
        path.stem.removeprefix("test_"): path.relative_to(TEST_CASE_DIR).as_posix()
        for path in project_test_dir.rglob(pattern)
        if path.is_file()
    }

    if module is not None:
        return sorted(discovered_files.values())

    if suite_modules is not None:
        return [discovered_files[module_name] for module_name in suite_modules]

    if tag_modules is not None:
        return [discovered_files[module_name] for module_name in tag_modules]

    dependency_manager = DependencyManager()
    return [
        discovered_files[module_name]
        for module_name in dependency_manager.order_modules(discovered_files)
    ]


def _discover_module_suites(project=DEFAULT_PROJECT, modules=None):
    available_modules = _available_modules(project)
    dependency_manager = DependencyManager()
    project_test_dir = _project_test_dir(project)
    module_suites = []
    module_names = modules or dependency_manager.order_modules(available_modules)

    for module_name in dependency_manager.order_modules(module_names):
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(project_test_dir),
            pattern=_test_pattern(module_name),
            top_level_dir=str(TEST_CASE_DIR),
        )
        module_suites.append((module_name, suite))

    return module_suites


def _tag_modules(project, tag):
    if tag is None:
        return None

    module_suites = _discover_module_suites(project)
    tagged_module_suites = _filter_module_suites_by_tag(module_suites, tag)
    if not tagged_module_suites:
        available_tags = ", ".join(_available_tags(project)) or "none"
        raise ValueError(
            f"Unsupported tag '{tag}' for project '{project}'. "
            f"Available tags: {available_tags}."
        )
    return [module_name for module_name, _ in tagged_module_suites]


def _filter_module_suites_by_tag(module_suites, tag):
    tag_manager = TestTagManager()
    tagged_module_suites = []
    for module_name, module_suite in module_suites:
        tagged_suite = tag_manager.filter_suite(module_suite, tag)
        if tagged_suite.countTestCases() > 0:
            tagged_module_suites.append((module_name, tagged_suite))
    return tagged_module_suites


def _available_tags(project=DEFAULT_PROJECT):
    module_suites = [suite for _, suite in _discover_module_suites(project)]
    return TestTagManager().list_tags(module_suites)


def _build_dependency_aware_suite(project=DEFAULT_PROJECT, modules=None):
    return DependencyAwareSuite(_discover_module_suites(project, modules=modules))


def _build_standard_suite(project=DEFAULT_PROJECT, module=None):
    project_test_dir = _project_test_dir(project)
    return unittest.defaultTestLoader.discover(
        start_dir=str(project_test_dir),
        pattern=_test_pattern(module),
        top_level_dir=str(TEST_CASE_DIR),
    )


def _build_tagged_suite(project=DEFAULT_PROJECT, tag=None):
    module_suites = _filter_module_suites_by_tag(_discover_module_suites(project), tag)
    if not module_suites:
        available_tags = ", ".join(_available_tags(project)) or "none"
        raise ValueError(
            f"Unsupported tag '{tag}' for project '{project}'. "
            f"Available tags: {available_tags}."
        )
    return DependencyAwareSuite(module_suites)


def _build_suite(project=DEFAULT_PROJECT, module=None, suite=None, tag=None):
    _validate_module(project, module)
    suite_modules = _suite_modules(project, suite)
    if tag is not None:
        return _build_tagged_suite(project, tag)
    if module is None:
        return _build_dependency_aware_suite(project, modules=suite_modules)
    return _build_standard_suite(project, module)


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
        "--suite",
        choices=sorted(TestSuiteManager().list_suites()),
        help="Test suite name, for example: smoke, regression, or nightly.",
    )
    parser.add_argument(
        "--tag",
        help="Run tests by metadata tag, for example: smoke, regression, ui, login, chat, or p0.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List runnable modules without executing tests or generating a report.",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Show test metadata when used with --list.",
    )
    args = parser.parse_args()
    selected_filters = [bool(args.module), bool(args.suite), bool(args.tag)]
    if sum(selected_filters) > 1:
        parser.error("--module, --suite, and --tag cannot be used together.")
    return args


def _configure_beautiful_report_template():
    template_path = PROJECT_ROOT / "BeautifulReport" / "template" / "template"
    if template_path.exists():
        BeautifulReport.config_tmp_path = str(template_path)


def run(project=DEFAULT_PROJECT, module=None, suite=None, tag=None):
    discovered_files = _discover_test_files(project, module, suite, tag)

    print("Discovered test files:")
    for file_name in discovered_files:
        print(f"  - {file_name}")
    sys.stdout.flush()

    if not discovered_files:
        pattern = _test_pattern(module)
        project_test_dir = _project_test_dir(project)
        raise RuntimeError(f"No {pattern} files found under {project_test_dir}.")

    _configure_beautiful_report_template()
    suite_tests = _build_suite(project, module, suite, tag)
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
    print(f"  skipped: {report.skipped}")
    print(f"  report: {report_file}")
    return 1 if report.failure_count or report.error_count else 0


def list_modules(project=DEFAULT_PROJECT):
    available_modules = _available_modules(project)
    print(f"Available modules for {project}:")
    if not available_modules:
        print("  - none")
    else:
        for module, file_name in sorted(available_modules.items()):
            print(f"  - {module}: {file_name}")

    print()
    print("Available suites:")
    for suite_name, suite_info in TestSuiteManager().list_suites().items():
        modules = ", ".join(suite_info["modules"])
        print(f"  - {suite_name}: {modules}")

    print()
    print("Available tags:")
    for tag in _available_tags(project):
        print(f"  - {tag}")

    return 0


def _iter_suite_tests(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _iter_suite_tests(test)
        elif test is not None:
            yield test


def list_metadata_details(project=DEFAULT_PROJECT):
    available_modules = _available_modules(project)
    dependency_manager = DependencyManager()
    project_test_dir = _project_test_dir(project)

    for module_name in dependency_manager.order_modules(available_modules):
        print(module_name)
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(project_test_dir),
            pattern=_test_pattern(module_name),
            top_level_dir=str(TEST_CASE_DIR),
        )
        for test in _iter_suite_tests(suite):
            metadata = get_metadata_from_test(test) or {}
            print(f"    {test._testMethodName}")
            print(f"        priority: {metadata.get('priority', '-')}")
            print(f"        tags: {', '.join(metadata.get('tags', [])) or '-'}")
            print(f"        feature: {metadata.get('feature', '-')}")
            print(f"        description: {metadata.get('description', '-')}")
        print()

    print("Suites")
    for suite_name, suite_info in TestSuiteManager().list_suites().items():
        print(f"    {suite_name}")
        print(f"        description: {suite_info['description']}")
        print(f"        modules: {', '.join(suite_info['modules'])}")
        print()

    print("Tags")
    for tag in _available_tags(project):
        print(f"    {tag}")
    return 0


if __name__ == "__main__":
    args = _parse_args()
    try:
        if args.list:
            if args.detail:
                sys.exit(list_metadata_details(project=args.project))
            sys.exit(list_modules(project=args.project))
        sys.exit(
            run(project=args.project, module=args.module, suite=args.suite, tag=args.tag)
        )
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
