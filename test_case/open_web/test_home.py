import unittest
import time
from urllib.parse import urlparse

from base.base import take_screenshot
from base.data_manager import DataManager
from base.driver_manager import DriverManager
from base.logger import get_logger
from base.test_metadata import metadata
from config.config_loader import get_account
from page_object.open_web.home_page import OpenWebHomePage
from page_object.open_web.login_page import OpenWebLoginPage


logger = get_logger(__name__)


class TestOpenWebHome(unittest.TestCase):
    def setUp(self) -> None:
        self.account_role = "default"
        logger.info("Open Web home test setup started, account_role=%s", self.account_role)
        self.driver_manager = DriverManager()
        self.addCleanup(self.driver_manager.quit_driver)
        self.addCleanup(self._capture_screenshot_on_failure)
        self.driver = self.driver_manager.get_driver()
        self.driver.maximize_window()
        self.account = get_account(self.account_role)
        self.home_data = DataManager.get_data("open_web", "home")
        self.login_page = OpenWebLoginPage(self.driver)
        self.home_page = OpenWebHomePage(self.driver)
        self.login_page.login(self.account["email"], self.account["password"])
        self._wait_home_loaded()

    def _wait_home_loaded(self, timeout=12):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.home_page.is_home_loaded():
                return
            time.sleep(0.5)
        raise AssertionError("Open Web home page did not load after login")

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

    @metadata(
        module="home",
        priority="P1",
        feature="Home",
        description="验证登录后首页加载成功",
        tags=["smoke", "regression", "ui"],
    )
    def test_01_home_loaded_after_login(self):
        """Open Web 登录后首页加载成功"""
        self.assertEqual(
            self.home_page.is_home_loaded(),
            self.home_data["home_loaded"]["expected"],
        )

    @metadata(
        module="home",
        priority="P1",
        feature="Home",
        description="验证首页 URL 为根路径",
        tags=["regression", "ui"],
    )
    def test_02_current_url_is_home(self):
        """Open Web 首页 URL 为根路径"""
        current_path = urlparse(self.driver.current_url).path or "/"
        self.assertEqual(current_path, self.home_data["current_url"]["expected_path"])

    @metadata(
        module="home",
        priority="P1",
        feature="Home",
        description="验证首页聊天输入框可见",
        tags=["smoke", "regression", "ui"],
    )
    def test_03_chat_input_visible(self):
        """Open Web 首页聊天输入框可见"""
        self.assertEqual(
            self.home_page.is_chat_input_visible(),
            self.home_data["chat_input"]["expected_visible"],
        )

    @metadata(
        module="home",
        priority="P2",
        feature="Home",
        description="验证首页当前模型名可见",
        tags=["regression", "ui"],
    )
    def test_04_current_model_visible(self):
        """Open Web 首页当前模型名可见"""
        current_model = self.home_page.get_current_model()
        self.assertTrue(current_model)
        self.assertEqual(current_model, self.home_data["model"]["expected_name"])

    @metadata(
        module="home",
        priority="P2",
        feature="Home",
        description="验证首页左侧导航可见",
        tags=["regression", "ui"],
    )
    def test_05_sidebar_visible(self):
        """Open Web 首页左侧导航可见"""
        self.assertEqual(
            self.home_page.is_sidebar_visible(),
            self.home_data["sidebar"]["expected_visible"],
        )


if __name__ == "__main__":
    unittest.main()
