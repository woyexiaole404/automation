import time
import unittest

from base.base import take_screenshot
from base.data_manager import DataManager
from base.driver_manager import DriverManager
from base.logger import get_logger
from base.test_data_manager import TestDataManager
from base.test_metadata import metadata
from config.config_loader import get_account
from config.config_loader import get_web_base_url
from page_object.open_web.chat_page import OpenWebChatPage
from page_object.open_web.home_page import OpenWebHomePage
from page_object.open_web.login_page import OpenWebLoginPage


logger = get_logger(__name__)


ERROR_TEXT_KEYWORDS = (
    "api rate limit exceeded",
    "internal server error",
    "bad gateway",
    "service unavailable",
    "gateway timeout",
    "application error",
    "network error",
)


class TestOpenWebChat(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.account_role = "default"
        logger.info("Open Web chat class setup started, account_role=%s", cls.account_role)
        cls.driver_manager = DriverManager()
        cls.driver = cls.driver_manager.get_driver()
        cls.driver.maximize_window()
        cls.account = cls.get_test_account("normal", cls.account_role)
        cls.chat_data = DataManager.get_data("open_web", "chat")
        cls.login_page = OpenWebLoginPage(cls.driver)
        cls.home_page = OpenWebHomePage(cls.driver)
        cls.chat_page = OpenWebChatPage(cls.driver)
        cls.login_page.login(cls.account["email"], cls.account["password"])
        cls._wait_login_successful()
        cls.driver.get(cls._home_url())
        cls._wait_chat_ready()

    @classmethod
    def tearDownClass(cls) -> None:
        logger.info("Open Web chat class teardown")
        cls.driver_manager.quit_driver()

    def setUp(self) -> None:
        self.addCleanup(self._capture_screenshot_on_failure)
        self._reset_chat_state()

    @staticmethod
    def get_test_account(name, fallback_role):
        if TestDataManager.exists(f"accounts.{name}"):
            account = TestDataManager.get_account(name)
            if account.get("email") and account.get("password"):
                return account
        return get_account(fallback_role)

    @classmethod
    def get_chat_message(cls):
        if TestDataManager.exists("chat.question_normal"):
            return TestDataManager.get_chat_data("question_normal")
        return cls.chat_data["message"]["text"]

    @classmethod
    def _wait_login_successful(cls, timeout=30):
        deadline = time.time() + timeout
        while time.time() < deadline:
            body_text = cls._get_body_text()
            body_text_lower = body_text.lower()
            if "api rate limit exceeded" in body_text_lower:
                logger.error(
                    "API rate limit exceeded during chat setup login, current_url=%s",
                    cls.driver.current_url,
                )
                raise AssertionError("API rate limit exceeded during chat setup")

            if cls.login_page.is_login_successful():
                return

            time.sleep(0.5)

        current_url = cls.driver.current_url
        body_text = cls._get_body_text()
        body_preview = body_text[:300]
        if "/auth" in current_url:
            raise AssertionError(
                "Open Web chat setup login failed, still on auth page. "
                f"current_url={current_url}, "
                f"rate_limit_detected={'api rate limit exceeded' in body_text.lower()}, "
                f"body_preview={body_preview!r}"
            )
        raise AssertionError(
            "Open Web chat setup login failed. "
            f"current_url={current_url}, "
            f"rate_limit_detected={'api rate limit exceeded' in body_text.lower()}, "
            f"body_preview={body_preview!r}"
        )

    @classmethod
    def _wait_chat_ready(cls, timeout=30):
        deadline = time.time() + timeout
        while time.time() < deadline:
            current_url = cls.driver.current_url
            body_text = cls._get_body_text()
            body_text_lower = body_text.lower()
            has_rate_limit = "api rate limit exceeded" in body_text_lower
            if has_rate_limit:
                logger.error(
                    "API rate limit exceeded during chat setup, current_url=%s",
                    current_url,
                )
                raise AssertionError("API rate limit exceeded during chat setup")

            matched_error = cls._get_visible_error_text(body_text_lower)
            if matched_error:
                logger.warning(
                    "Potential Open Web page error during chat setup, current_url=%s, error=%s",
                    current_url,
                    matched_error,
                )

            if cls.chat_page.is_chat_input_visible():
                return
            time.sleep(0.5)

        current_url = cls.driver.current_url
        body_text = cls._get_body_text()
        has_rate_limit = "api rate limit exceeded" in body_text.lower()
        body_preview = body_text[:300]
        raise AssertionError(
            "Open Web chat input did not load after login. "
            f"current_url={current_url}, "
            f"rate_limit_detected={has_rate_limit}, "
            f"body_preview={body_preview!r}"
        )

    def _reset_chat_state(self):
        if self._has_rate_limit_message():
            logger.warning("API rate limit exceeded is visible before test starts")
            self.skipTest("API rate limit exceeded")
        self.driver.get(self._home_url())
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

    @classmethod
    def _home_url(cls):
        base_url = get_web_base_url().rstrip("/")
        if base_url.endswith("/auth"):
            base_url = base_url[: -len("/auth")]
        return base_url.rstrip("/") + "/"

    @classmethod
    def _get_body_text(cls):
        try:
            return cls.driver.find_element("tag name", "body").text
        except Exception:
            logger.exception("Failed to read Open Web page body text")
            return ""

    @classmethod
    def _get_visible_error_text(cls, body_text_lower):
        for keyword in ERROR_TEXT_KEYWORDS:
            if keyword in body_text_lower:
                return keyword
        return ""

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
        message = self.get_chat_message()
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
        self.chat_page.input_message(self.get_chat_message())
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
