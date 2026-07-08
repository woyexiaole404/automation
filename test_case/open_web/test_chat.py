import time
import unittest

from base.base import take_screenshot
from base.data_manager import DataManager
from base.driver_manager import DriverManager
from base.logger import get_logger
from base.test_metadata import metadata
from config.config_loader import get_account
from page_object.open_web.chat_page import OpenWebChatPage
from page_object.open_web.home_page import OpenWebHomePage
from page_object.open_web.login_page import OpenWebLoginPage


logger = get_logger(__name__)


class TestOpenWebChat(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.account_role = "default"
        logger.info("Open Web chat class setup started, account_role=%s", cls.account_role)
        cls.driver_manager = DriverManager()
        cls.driver = cls.driver_manager.get_driver()
        cls.driver.maximize_window()
        cls.account = get_account(cls.account_role)
        cls.chat_data = DataManager.get_data("open_web", "chat")
        cls.login_page = OpenWebLoginPage(cls.driver)
        cls.home_page = OpenWebHomePage(cls.driver)
        cls.chat_page = OpenWebChatPage(cls.driver)
        cls.login_page.login(cls.account["email"], cls.account["password"])
        cls._wait_chat_ready()

    @classmethod
    def tearDownClass(cls) -> None:
        logger.info("Open Web chat class teardown")
        cls.driver_manager.quit_driver()

    def setUp(self) -> None:
        self.addCleanup(self._capture_screenshot_on_failure)
        self._reset_chat_state()

    @classmethod
    def _wait_chat_ready(cls, timeout=12):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if cls.chat_page.is_chat_input_visible():
                return
            time.sleep(0.5)
        raise AssertionError("Open Web chat input did not load after login")

    def _reset_chat_state(self):
        if self._has_rate_limit_message():
            logger.warning("API rate limit exceeded is visible before test starts")
            self.skipTest("API rate limit exceeded")
        self.driver.get("http://localhost:3000/")
        self._wait_chat_ready()
        if self._has_rate_limit_message():
            logger.warning("API rate limit exceeded after returning home")
            self.skipTest("API rate limit exceeded")
        try:
            self.chat_page.click_new_chat()
        except Exception:
            logger.info("New chat click skipped during reset; continuing with current chat")
        self._wait_chat_ready()
        self.chat_page.clear_message()
        if self._has_rate_limit_message():
            logger.warning("API rate limit exceeded after chat reset")
            self.skipTest("API rate limit exceeded")

    def _has_rate_limit_message(self):
        body_text = self.driver.find_element("tag name", "body").text.lower()
        return "api rate limit exceeded" in body_text

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
        module="chat",
        priority="P1",
        feature="Chat",
        description="验证登录后聊天输入框可见",
        tags=["smoke", "regression", "ui"],
    )
    def test_01_chat_input_visible_after_login(self):
        """Open Web 登录后聊天输入框可见"""
        self.assertEqual(
            self.chat_page.is_chat_input_visible(),
            self.chat_data["chat_input"]["expected_visible"],
        )

    @metadata(
        module="chat",
        priority="P1",
        feature="Chat",
        description="验证输入消息后内容正确",
        tags=["regression", "ui"],
    )
    def test_02_input_message_value_correct(self):
        """Open Web 输入消息后内容正确"""
        message = self.chat_data["message"]["text"]
        self.chat_page.input_message(message)
        self.assertEqual(self.chat_page.get_message_value(), message)

    @metadata(
        module="chat",
        priority="P1",
        feature="Chat",
        description="验证清空消息后输入框为空",
        tags=["regression", "ui"],
    )
    def test_03_clear_message_value_empty(self):
        """Open Web 清空消息后输入框为空"""
        self.chat_page.input_message(self.chat_data["message"]["text"])
        self.chat_page.clear_message()
        self.assertEqual(
            self.chat_page.get_message_value(),
            self.chat_data["message"]["expected_empty"],
        )

    @metadata(
        module="chat",
        priority="P2",
        feature="Chat",
        description="验证新对话入口可点击",
        tags=["regression", "ui"],
    )
    def test_04_new_chat_clickable(self):
        """Open Web 新对话入口可点击"""
        self.chat_page.click_new_chat()
        self.assertEqual(
            self.chat_page.is_chat_input_visible(),
            self.chat_data["chat_input"]["expected_visible"],
        )


if __name__ == "__main__":
    unittest.main()
