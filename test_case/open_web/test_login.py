import time
import unittest

from base.base import take_screenshot
from base.data_manager import DataManager
from base.driver_manager import DriverManager
from base.logger import get_logger
from config.config_loader import get_account
from page_object.open_web.login_page import OpenWebLoginPage


logger = get_logger(__name__)


class TestOpenWebLogin(unittest.TestCase):
    def setUp(self) -> None:
        self.account_role = "default"
        logger.info("Open Web login test setup started, account_role=%s", self.account_role)
        self.driver_manager = DriverManager()
        self.addCleanup(self.driver_manager.quit_driver)
        self.addCleanup(self._capture_screenshot_on_failure)
        self.driver = self.driver_manager.get_driver()
        self.driver.maximize_window()
        self.account = get_account(self.account_role)
        self.login_data = DataManager.get_data("open_web", "login")

    def _capture_screenshot_on_failure(self):
        if not self._has_failure_or_error():
            return

        self._capture_failure_screenshot()

    def _capture_failure_screenshot(self):
        driver = getattr(self, "driver", None)
        if driver is None:
            logger.warning("Skip failure screenshot: driver is not available")
            return

        screenshot_name = self.id().replace(".", "_")
        try:
            screenshot_path = take_screenshot(driver, name=screenshot_name)
        except Exception:
            logger.exception("Failed to capture failure screenshot")
            return

        logger.info("Failure screenshot path: %s", screenshot_path)

    def _callTestMethod(self, method):
        try:
            method()
        except Exception:
            self._capture_failure_screenshot()
            raise

    def _has_failure_or_error(self):
        outcome = getattr(self, "_outcome", None)
        if getattr(outcome, "success", True) is False:
            return True

        result = getattr(outcome, "result", None)
        if result is None:
            return False

        test_id = self.id()
        failed_tests = list(getattr(result, "failures", ())) + list(getattr(result, "errors", ()))
        return any(test.id() == test_id for test, _ in failed_tests)

    def test_01_login(self):
        """Open Web 登录成功"""
        logger.info("Open Web login test started, account_role=%s", self.account_role)
        self.addCleanup(
            logger.info,
            "Open Web login test finished, account_role=%s",
            self.account_role,
        )
        login_page = OpenWebLoginPage(self.driver)
        login_page.login(self.account["email"], self.account["password"])
        time.sleep(1)
        self.assertEqual(
            login_page.is_login_successful(),
            self.login_data["expected_success"]["login_success"],
        )


if __name__ == "__main__":
    unittest.main()
