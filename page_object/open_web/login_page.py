from base.base import BasePage
from config.config_loader import get_web_base_url
from selenium.webdriver.common.by import By


class OpenWebLoginPage(BasePage):
    EMAIL_INPUT = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    SUBMIT_BUTTON = 'button[type="submit"]'
    BODY = "body"

    def open(self):
        self.go_url(get_web_base_url())

    def login(self, email, password):
        self.open()
        self.input_text(self.EMAIL_INPUT, email, by=By.CSS_SELECTOR)
        self.input_text(self.PASSWORD_INPUT, password, by=By.CSS_SELECTOR)
        self.click_element(self.SUBMIT_BUTTON, by=By.CSS_SELECTOR, timeout=10)

    def is_login_successful(self):
        current_url = self.driver_url()
        if "/auth" not in current_url:
            return True

        page_text = self.get_text(self.BODY, by=By.CSS_SELECTOR)
        success_keywords = ("退出", "用户", "首页", "dashboard", "logout")
        return any(keyword in page_text for keyword in success_keywords)
