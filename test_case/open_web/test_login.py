import time
import unittest
from urllib.parse import urljoin

from base.base import take_screenshot
from base.data_manager import DataManager
from base.driver_manager import DriverManager
from base.logger import get_logger
from config.config_loader import get_account, get_default_invalid_password, get_web_base_url
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
        self.login_page = OpenWebLoginPage(self.driver)

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
        except unittest.SkipTest:
            raise
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
        self.login_page.login(self.account["email"], self.account["password"])
        time.sleep(1)
        self.assertEqual(
            self.login_page.is_login_successful(),
            self.login_data["valid_login"]["expected_login_success"],
        )

    def test_02_invalid_password_login_failed(self):
        """Open Web 错误密码登录失败"""
        scenario = self.login_data["invalid_password"]
        self.login_page.login(self.account["email"], get_default_invalid_password())
        time.sleep(1)
        self.assertEqual(
            self.login_page.is_login_successful(),
            scenario["expected_login_success"],
        )
        self.assertEqual(
            bool(self.login_page.get_error_message()),
            scenario["expected_error_visible"],
        )

    def test_03_empty_email_login_failed(self):
        """Open Web 邮箱为空登录失败"""
        scenario = self.login_data["empty_email"]
        self.login_page.login(scenario["email"], self.account["password"])
        self.assert_login_failed_with_error(scenario)

    def test_04_empty_password_login_failed(self):
        """Open Web 密码为空登录失败"""
        scenario = self.login_data["empty_password"]
        self.login_page.login(self.account["email"], scenario["password"])
        self.assert_login_failed_with_error(scenario)

    def test_05_empty_email_password_login_failed(self):
        """Open Web 邮箱和密码都为空登录失败"""
        scenario = self.login_data["empty_email_password"]
        self.login_page.login(scenario["email"], scenario["password"])
        self.assert_login_failed_with_error(scenario)

    def test_06_invalid_email_format_login_failed(self):
        """Open Web 无效邮箱格式登录失败"""
        scenario = self.login_data["invalid_email_format"]
        self.login_page.login(scenario["email"], self.account["password"])
        self.assert_login_failed_with_error(scenario)

    def test_07_logout_after_login(self):
        """Open Web 登录成功后退出登录"""
        scenario = self.login_data["logout"]
        if not scenario["supported"]:
            self.skipTest("当前页面未配置退出登录能力")

        self.login_page.login(self.account["email"], self.account["password"])
        time.sleep(1)
        self.assertTrue(self.login_page.is_login_successful())
        if not self.login_page.logout():
            self.skipTest("当前页面未找到明确的退出登录入口")
        time.sleep(1)
        self.assertEqual(
            self.login_page.is_login_successful(),
            scenario["expected_login_success"],
        )

    def test_08_unauthenticated_protected_access(self):
        """Open Web 未登录访问受保护页面"""
        scenario = self.login_data["protected_access"]
        if not scenario["supported"]:
            self.skipTest("当前系统未配置明确的受保护页面")

        self.login_page.clear_browser_state()
        protected_url = urljoin(get_web_base_url(), scenario["path"])
        self.driver.get(protected_url)
        time.sleep(1)
        self.assertIn(scenario["expected_url_contains"], self.driver.current_url)

    def assert_login_failed_with_error(self, scenario):
        self.assertEqual(
            self.login_page.is_login_successful(),
            scenario["expected_login_success"],
        )
        self.assertEqual(
            bool(self.login_page.get_error_message()),
            scenario["expected_error_visible"],
        )


if __name__ == "__main__":
    unittest.main()
