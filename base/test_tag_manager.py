import unittest

from base.test_metadata import get_metadata_from_test


class TestTagManager:
    def normalize_tag(self, tag):
        return str(tag).strip().lower()

    def get_test_tags(self, test):
        metadata = get_metadata_from_test(test) or {}
        return metadata.get("tags", [])

    def test_matches_tag(self, test, tag):
        expected_tag = self.normalize_tag(tag)
        return any(self.normalize_tag(test_tag) == expected_tag for test_tag in self.get_test_tags(test))

    def filter_suite(self, suite, tag):
        filtered_suite = unittest.TestSuite()
        for test in self.iter_tests(suite):
            if self.test_matches_tag(test, tag):
                filtered_suite.addTest(test)
        return filtered_suite

    def list_tags(self, suites):
        tags = {}
        for suite in suites:
            for test in self.iter_tests(suite):
                for tag in self.get_test_tags(test):
                    normalized_tag = self.normalize_tag(tag)
                    tags.setdefault(normalized_tag, str(tag))
        return [tags[tag] for tag in sorted(tags)]

    def iter_tests(self, suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from self.iter_tests(test)
            elif test is not None:
                yield test
