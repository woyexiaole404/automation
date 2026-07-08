import unittest

from base.logger import get_logger


MODULE_DEPENDENCIES = {
    "login": [],
    "home": ["login"],
    "chat": ["home"],
}


class DependencyManager:
    def __init__(self, dependencies=None):
        self.dependencies = dependencies or MODULE_DEPENDENCIES
        self.logger = get_logger(__name__)

    def order_modules(self, modules):
        ordered_modules = [module for module in self.dependencies if module in modules]
        unordered_modules = sorted(module for module in modules if module not in self.dependencies)
        return ordered_modules + unordered_modules

    def get_dependencies(self, module):
        return self.dependencies.get(module, [])

    def get_blocked_dependency(self, module, unavailable_modules):
        for dependency in self.get_dependencies(module):
            if dependency in unavailable_modules:
                return dependency
        return None

    def build_skip_reason(self, module, dependency):
        return f"因为 {dependency} 模块失败，跳过 {module} 模块用例。"

    def log_skip(self, module, dependency):
        self.logger.warning(self.build_skip_reason(module, dependency))


class DependencyAwareSuite(unittest.TestSuite):
    def __init__(self, module_suites, dependency_manager=None):
        super().__init__()
        self.module_suites = module_suites
        self.dependency_manager = dependency_manager or DependencyManager()

    def run(self, result, debug=False):
        unavailable_modules = set()

        for module, suite in self.module_suites:
            blocked_dependency = self.dependency_manager.get_blocked_dependency(
                module, unavailable_modules
            )

            if blocked_dependency:
                reason = self.dependency_manager.build_skip_reason(module, blocked_dependency)
                self.dependency_manager.log_skip(module, blocked_dependency)
                self._skip_suite(suite, result, reason)
                unavailable_modules.add(module)
                continue

            failure_count = self._get_failure_count(result)
            error_count = self._get_error_count(result)
            suite.run(result, debug=debug)

            if (
                self._get_failure_count(result) > failure_count
                or self._get_error_count(result) > error_count
            ):
                unavailable_modules.add(module)

            if result.shouldStop:
                break

        return result

    def countTestCases(self):
        return sum(suite.countTestCases() for _, suite in self.module_suites)

    def _skip_suite(self, suite, result, reason):
        for test in self._iter_tests(suite):
            if result.shouldStop:
                break
            result.startTest(test)
            result.addSkip(test, reason)
            result.stopTest(test)

    def _iter_tests(self, suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from self._iter_tests(test)
            elif test is not None:
                yield test

    def _get_failure_count(self, result):
        return getattr(result, "failure_count", len(getattr(result, "failures", [])))

    def _get_error_count(self, result):
        return getattr(result, "error_count", len(getattr(result, "errors", [])))
