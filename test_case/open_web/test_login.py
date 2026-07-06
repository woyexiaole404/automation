import time
import unittest

from base.driver_manager import DriverManager
from config.config_loader import get_account
from page_object.open_web.login_page import OpenWebLoginPage


class TestOpenWebLogin(unittest.TestCase):
    def setUp(self) -> None:
        self.driver_manager = DriverManager()
        self.addCleanup(self.driver_manager.quit_driver)
        self.driver = self.driver_manager.get_driver()
        self.driver.maximize_window()
        self.account = get_account("default")

    def test_01_login(self):
        """Open Web 登录成功"""
        login_page = OpenWebLoginPage(self.driver)
        login_page.login(self.account["email"], self.account["password"])
        time.sleep(1)
        self.assertTrue(login_page.is_login_successful())


if __name__ == "__main__":
    unittest.main()
