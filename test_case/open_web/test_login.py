import shutil
import tempfile
import time
import unittest

from base.base import create_chrome_driver, create_chrome_options
from config.config_loader import get_account
from page_object.open_web.login_page import OpenWebLoginPage


class TestOpenWebLogin(unittest.TestCase):
    def setUp(self) -> None:
        self.chrome_profile_dir = tempfile.mkdtemp(prefix="open_web_chrome_")
        options = create_chrome_options(
            f"--user-data-dir={self.chrome_profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-application-cache",
        )
        self.driver = create_chrome_driver(options=options)
        self.driver.maximize_window()
        self.account = get_account("default")

    def tearDown(self) -> None:
        self.driver.quit()
        shutil.rmtree(self.chrome_profile_dir, ignore_errors=True)

    def test_01_login(self):
        """Open Web 登录成功"""
        login_page = OpenWebLoginPage(self.driver)
        login_page.login(self.account["email"], self.account["password"])
        time.sleep(1)
        self.assertTrue(login_page.is_login_successful())


if __name__ == "__main__":
    unittest.main()
