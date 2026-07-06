from base.base import BasePage
from config.config_loader import get_web_base_url
from selenium.webdriver.common.by import By


class LocalAuthPage(BasePage):
    def open(self):
        self.go_url(get_web_base_url())

    def login(self, email, password):
        self.open()
        self.safe_input('input[type="email"]', email, by=By.CSS_SELECTOR)
        self.safe_input('input[type="password"]', password, by=By.CSS_SELECTOR)
        self.safe_click('button[type="submit"]', by=By.CSS_SELECTOR)

    def is_login_successful(self):
        current_url = self.driver_url()
        if "/auth" not in current_url:
            return True

        page_text = self.driver.page_source
        success_keywords = ("退出", "用户", "首页", "dashboard", "logout")
        return any(keyword in page_text for keyword in success_keywords)
