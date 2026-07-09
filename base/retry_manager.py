import time
import unittest

from base.logger import get_logger


VALID_RETRY_COUNTS = {0, 1, 2}
DEFAULT_RETRY_COUNT = 0
DEFAULT_RETRY_INTERVAL_SECONDS = 10


logger = get_logger(__name__)


class RetryManager:
    def __init__(self, count=DEFAULT_RETRY_COUNT, interval_seconds=DEFAULT_RETRY_INTERVAL_SECONDS):
        self.count = self.validate_retry_count(count)
        self.interval_seconds = int(interval_seconds)

    @staticmethod
    def validate_retry_count(count):
        retry_count = int(count)
        if retry_count not in VALID_RETRY_COUNTS:
            raise ValueError("--retry only supports 0, 1, or 2")
        return retry_count

    @property
    def enabled(self):
        return self.count > 0

    def wrap_suite(self, suite_factory, name="test suite"):
        if not self.enabled:
            return suite_factory()
        return RetrySuite(
            suite_factory=suite_factory,
            retry_count=self.count,
            interval_seconds=self.interval_seconds,
            name=name,
        )


class RetrySuite(unittest.TestSuite):
    def __init__(self, suite_factory, retry_count, interval_seconds, name="test suite"):
        super().__init__()
        self.suite_factory = suite_factory
        self.retry_count = retry_count
        self.interval_seconds = interval_seconds
        self.name = name

    def run(self, result, debug=False):
        failed_test_ids = self._run_and_collect_failures(self.suite_factory(), result, debug)
        if not failed_test_ids:
            return result

        for retry_number in range(1, self.retry_count + 1):
            self._remove_test_results(result, failed_test_ids)
            logger.warning("Retry #%s: %s", retry_number, self.name)
            logger.warning("Retry waiting %s seconds", self.interval_seconds)
            time.sleep(self.interval_seconds)

            retry_suite = self._build_suite_for_tests(failed_test_ids)
            failed_test_ids = self._run_and_collect_failures(retry_suite, result, debug)
            if not failed_test_ids:
                logger.info("Retry Passed: %s", self.name)
                return result

        logger.error("Retry Failed: %s", self.name)
        return result

    def countTestCases(self):
        return self.suite_factory().countTestCases()

    def __iter__(self):
        return iter(self.suite_factory())

    def _run_and_collect_failures(self, suite, result, debug=False):
        recording_result = RecordingResult(result)
        suite.run(recording_result, debug=debug)
        return recording_result.failed_test_ids()

    def _build_suite_for_tests(self, test_ids):
        retry_suite = unittest.TestSuite()
        fixture_class_ids = self._fixture_class_ids(test_ids)
        added_test_ids = set()
        for test in self._iter_tests(self.suite_factory()):
            test_id = test.id()
            if test_id in test_ids or self._test_belongs_to_fixture_failure(
                test,
                fixture_class_ids,
            ):
                if test_id in added_test_ids:
                    continue
                retry_suite.addTest(test)
                added_test_ids.add(test_id)
        return retry_suite

    def _fixture_class_ids(self, test_ids):
        fixture_class_ids = set()
        for test_id in test_ids:
            if "(" not in test_id or ")" not in test_id:
                continue
            fixture_class_ids.add(test_id.rsplit("(", 1)[1].split(")", 1)[0])
        return fixture_class_ids

    def _test_belongs_to_fixture_failure(self, test, fixture_class_ids):
        if not fixture_class_ids:
            return False
        test_class = test.__class__
        class_id = f"{test_class.__module__}.{test_class.__qualname__}"
        return class_id in fixture_class_ids

    def _iter_tests(self, suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from self._iter_tests(test)
            elif test is not None:
                yield test

    def _remove_test_results(self, result, test_ids):
        if not test_ids:
            return

        if hasattr(result, "result_list"):
            self._remove_beautiful_report_results(result, test_ids)
            return

        result.failures = [
            failure for failure in getattr(result, "failures", []) if failure[0].id() not in test_ids
        ]
        result.errors = [
            error for error in getattr(result, "errors", []) if error[0].id() not in test_ids
        ]
        result.testsRun = max(0, getattr(result, "testsRun", 0) - len(test_ids))

    def _remove_beautiful_report_results(self, result, test_ids):
        retry_result_keys = self._build_result_keys(test_ids)
        kept_results = []

        for case_result in result.result_list:
            result_key = self._case_result_key(case_result)
            if result_key not in retry_result_keys:
                kept_results.append(case_result)

        removed_count = len(result.result_list) - len(kept_results)
        result.result_list = kept_results
        result.testsRun = max(0, getattr(result, "testsRun", 0) - removed_count)
        self._recalculate_beautiful_report_counts(result)

    def _build_result_keys(self, test_ids):
        result_keys = set()
        for test_id in test_ids:
            parts = test_id.split(".")
            if len(parts) < 2:
                continue
            result_keys.add((parts[-2], parts[-1]))
        return result_keys

    def _case_result_key(self, case_result):
        class_name = case_result[0]
        method_name = case_result[1]
        return class_name.split(".")[-1], method_name

    def _recalculate_beautiful_report_counts(self, result):
        result.success_count = 0
        result.failure_count = 0
        result.error_count = 0
        result.skipped = 0

        for case_result in result.result_list:
            status = case_result[4]
            if status == "成功":
                result.success_count += 1
            elif status == "失败":
                result.failure_count += 1
            elif status == "错误":
                result.error_count += 1
            elif status == "跳过":
                result.skipped += 1

    def _get_failure_count(self, result):
        return getattr(result, "failure_count", len(getattr(result, "failures", [])))

    def _get_error_count(self, result):
        return getattr(result, "error_count", len(getattr(result, "errors", [])))


class RecordingResult:
    def __init__(self, result):
        self._result = result
        self._failed_test_ids = set()

    def failed_test_ids(self):
        return set(self._failed_test_ids)

    def startTest(self, test):
        self._result.startTest(test)

    def stopTest(self, test):
        self._result.stopTest(test)

    def startTestRun(self):
        if hasattr(self._result, "startTestRun"):
            self._result.startTestRun()

    def stopTestRun(self):
        if hasattr(self._result, "stopTestRun"):
            self._result.stopTestRun()

    def addSuccess(self, test):
        self._result.addSuccess(test)

    def addFailure(self, test, err):
        self._failed_test_ids.add(test.id())
        self._result.addFailure(test, err)

    def addError(self, test, err):
        self._failed_test_ids.add(test.id())
        self._result.addError(test, err)

    def addSkip(self, test, reason):
        self._result.addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self._result.addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self._failed_test_ids.add(test.id())
        self._result.addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self._failed_test_ids.add(test.id())
        self._result.addSubTest(test, subtest, err)

    def __getattr__(self, name):
        return getattr(self._result, name)
