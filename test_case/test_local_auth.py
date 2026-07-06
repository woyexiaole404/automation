import time
import unittest

from base.base import create_chrome_driver
from config.config_loader import get_account
from page_object.local_auth_page import LocalAuthPage


class TestLocalAuth(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = create_chrome_driver()
        self.driver.maximize_window()
        self.account = get_account("default")

    def tearDown(self) -> None:
        self.driver.quit()

    def test_01_login(self):
        """本地项目登录成功"""
        LocalAuthPage(self.driver).login(self.account["email"], self.account["password"])
        time.sleep(1)
        self.assertTrue(LocalAuthPage(self.driver).is_login_successful())


if __name__ == "__main__":
    unittest.main()
