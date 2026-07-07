import os
from pathlib import Path
import shutil
import tempfile

from base.logger import get_logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


logger = get_logger(__name__)


class DriverManager:
    DEFAULT_WINDOW_SIZE = (1920, 1080)

    def __init__(
        self,
        headless=False,
        window_size=DEFAULT_WINDOW_SIZE,
        extra_arguments=None,
        options=None,
    ):
        self.headless = headless
        self.window_size = window_size
        self.extra_arguments = tuple(extra_arguments or ())
        self.options = options
        self._driver = None
        self._profile_dir = None

    @classmethod
    def create_options(
        cls,
        headless=False,
        window_size=DEFAULT_WINDOW_SIZE,
        extra_arguments=None,
        profile_dir=None,
    ):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")

        width, height = window_size
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-application-cache")
        options.add_experimental_option(
            "prefs",
            {
                "autofill.profile_enabled": False,
                "credentials_enable_service": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.password_manager_enabled": False,
            },
        )
        if profile_dir:
            options.add_argument(f"--user-data-dir={profile_dir}")
        for argument in extra_arguments or ():
            options.add_argument(argument)
        return options

    @staticmethod
    def _driver_from_environment():
        configured_path = os.environ.get("CHROMEDRIVER_PATH")
        if not configured_path:
            return None

        driver_path = Path(configured_path).expanduser()
        if not driver_path.is_file():
            raise FileNotFoundError(
                f"CHROMEDRIVER_PATH does not point to a file: {driver_path}"
            )
        return str(driver_path)

    @staticmethod
    def _driver_from_selenium_cache():
        cache_root = Path.home() / ".cache" / "selenium" / "chromedriver"
        if not cache_root.exists():
            return None

        candidates = [path for path in cache_root.rglob("chromedriver") if path.is_file()]
        if not candidates:
            return None
        return str(max(candidates, key=lambda path: path.stat().st_mtime))

    @classmethod
    def _resolve_driver(cls):
        driver_path = cls._driver_from_environment()
        if driver_path:
            return driver_path, "CHROMEDRIVER_PATH"

        driver_path = cls._driver_from_selenium_cache()
        if driver_path:
            return driver_path, "Selenium Cache"

        driver_path = shutil.which("chromedriver")
        if driver_path:
            return driver_path, "system PATH"

        return None, "Selenium Manager"

    @classmethod
    def _resolve_driver_path(cls):
        driver_path, _ = cls._resolve_driver()
        return driver_path

    def get_driver(self):
        if self._driver is not None:
            return self._driver

        logger.info("Starting Chrome driver, headless=%s", self.headless)

        if self.options is None:
            self._profile_dir = tempfile.mkdtemp(prefix="open_web_chrome_")
            logger.info("Using temporary Chrome profile: %s", self._profile_dir)
            options = self.create_options(
                headless=self.headless,
                window_size=self.window_size,
                extra_arguments=self.extra_arguments,
                profile_dir=self._profile_dir,
            )
        else:
            logger.info("Using provided ChromeOptions")
            options = self.options

        try:
            driver_path, driver_source = self._resolve_driver()
            logger.info("Chrome driver source: %s", driver_source)
            if driver_path:
                self._driver = webdriver.Chrome(
                    service=Service(driver_path),
                    options=options,
                )
            else:
                self._driver = webdriver.Chrome(options=options)
        except Exception:
            logger.exception("Failed to start Chrome driver")
            if self._profile_dir:
                shutil.rmtree(self._profile_dir, ignore_errors=True)
                self._profile_dir = None
            raise
        return self._driver

    def quit_driver(self):
        try:
            if self._driver is not None:
                logger.info("Quit Chrome driver")
                self._driver.quit()
        finally:
            self._driver = None
            if self._profile_dir:
                logger.info("Remove temporary Chrome profile: %s", self._profile_dir)
                shutil.rmtree(self._profile_dir, ignore_errors=True)
                self._profile_dir = None
