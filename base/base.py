from datetime import datetime
from pathlib import Path
import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base.logger import get_logger
from base.project_path import img_file


logger = get_logger(__name__)


def _normalize_screenshot_name(name):
    normalized_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name or "screenshot").strip("_")
    return normalized_name or "screenshot"


def take_screenshot(driver, name=None, file_path=None):
    if file_path is None:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = _normalize_screenshot_name(name)
        file_path = img_file(f"{screenshot_name}_{now}.png")

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(file_path))
    screenshot_path = str(file_path)
    logger.info("Screenshot saved: %s", screenshot_path)
    return screenshot_path


class BasePage:
    DEFAULT_TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver

    def get_current_url(self):
        return self.driver.current_url

    def go_url(self, url):
        self.driver.get(url)

    def find(self, value, by=By.XPATH):
        return self.driver.find_element(by, value)

    def wait_present(self, value, by=By.XPATH, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_visible(self, value, by=By.XPATH, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, value))
        )

    def wait_clickable(self, value, by=By.XPATH, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def click_element(self, value, by=By.XPATH, timeout=DEFAULT_TIMEOUT):
        self.wait_clickable(value, by=by, timeout=timeout).click()

    def input_text(
        self,
        value,
        input_txt,
        by=By.XPATH,
        timeout=DEFAULT_TIMEOUT,
        clear_first=True,
    ):
        element = self.wait_visible(value, by=by, timeout=timeout)
        if clear_first:
            element.clear()
        element.send_keys(input_txt)

    def get_text(self, value, by=By.XPATH, timeout=DEFAULT_TIMEOUT):
        element = self.wait_present(value, by=by, timeout=timeout)
        return element.get_attribute("textContent")

    def is_element_visible(self, value, by=By.XPATH, timeout=3):
        try:
            self.wait_visible(value, by=by, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def take_screenshot(self, file_path=None, name=None):
        return take_screenshot(self.driver, name=name, file_path=file_path)

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    def execute_async_script(self, script, *args):
        return self.driver.execute_async_script(script, *args)
