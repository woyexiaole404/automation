from base.base import BasePage
from base.logger import get_logger
from config.config_loader import get_web_base_url
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


logger = get_logger(__name__)


def _mask_account(account):
    if not account:
        return "<empty>"
    if "@" not in account:
        return f"{account[:1]}***"
    name, domain = account.split("@", 1)
    return f"{name[:1]}***@{domain}"


class OpenWebLoginPage(BasePage):
    EMAIL_INPUT = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    SUBMIT_BUTTON = 'button[type="submit"]'
    BODY = "body"
    ERROR_SELECTORS = (
        '[role="alert"]',
        '[data-testid*="error"]',
        '.error',
        '.text-red-500',
        '.text-danger',
        '.ant-form-item-explain-error',
    )
    AVATAR_SELECTORS = (
        (By.CSS_SELECTOR, '[data-testid="user-avatar"]'),
        (By.CSS_SELECTOR, '[data-testid="avatar"]'),
        (By.CSS_SELECTOR, '[aria-label*="avatar"]'),
        (By.CSS_SELECTOR, '[aria-label*="Avatar"]'),
        (By.CSS_SELECTOR, '[aria-label*="用户"]'),
        (By.XPATH, '//*[self::button or @role="button"][.//img]'),
        (By.XPATH, '//*[self::button or @role="button"][contains(@class, "avatar")]'),
        (By.XPATH, '//*[self::button or @role="button"][contains(@class, "rounded-full")]'),
    )
    LOGOUT_SELECTORS = (
        (By.CSS_SELECTOR, '[data-testid="logout"]'),
        (By.CSS_SELECTOR, 'button[aria-label*="Logout"]'),
        (By.CSS_SELECTOR, 'button[aria-label*="logout"]'),
        (By.XPATH, '//*[@role="menuitem" and contains(normalize-space(.), "登出")]'),
        (By.XPATH, '//*[@role="menuitem" and contains(normalize-space(.), "退出")]'),
        (By.XPATH, '//button[contains(normalize-space(.), "Logout")]'),
        (By.XPATH, '//button[contains(normalize-space(.), "Sign out")]'),
        (By.XPATH, '//button[contains(normalize-space(.), "登出")]'),
        (By.XPATH, '//button[contains(normalize-space(.), "退出")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "Logout")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "Sign out")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "登出")]'),
        (By.XPATH, '//a[contains(normalize-space(.), "退出")]'),
        (By.XPATH, '//*[contains(normalize-space(.), "登出") and (self::div or self::span)]'),
    )
    AUTH_TOKEN_KEYS = ("token", "access_token", "auth_token", "jwt")
    LOGGED_IN_SELECTORS = (
        'textarea',
        '[data-testid="chat-input"]',
        '[aria-label*="New Chat"]',
        'a[href="/workspace"]',
    )

    def open(self):
        url = get_web_base_url()
        logger.info("Open login page: %s", url)
        self.go_url(url)

    def clear_browser_state(self):
        logger.info("Clear browser state before login")
        self.open()
        self.delete_all_cookies()
        self.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        self.execute_async_script(
            """
            const done = arguments[0];
            const tasks = [];
            if (window.caches && caches.keys) {
                tasks.push(caches.keys().then(keys => Promise.all(keys.map(key => caches.delete(key)))));
            }
            if (window.indexedDB && indexedDB.databases) {
                tasks.push(
                    indexedDB.databases().then(databases => Promise.all(
                        databases
                            .filter(database => database.name)
                            .map(database => new Promise(resolve => {
                                const request = indexedDB.deleteDatabase(database.name);
                                request.onsuccess = resolve;
                                request.onerror = resolve;
                                request.onblocked = resolve;
                            }))
                    ))
                );
            }
            Promise.all(tasks).then(() => done(true)).catch(() => done(false));
            """
        )
        self.open()

    def login(self, email, password):
        self.clear_browser_state()
        self.input_email(email)
        self.input_password(password)
        self.click_login()

    def input_email(self, email):
        logger.info("Input login account: %s", _mask_account(email))
        self.input_text(self.EMAIL_INPUT, email, by=By.CSS_SELECTOR)

    def input_password(self, password):
        logger.info("Input login password")
        self.input_text(self.PASSWORD_INPUT, password, by=By.CSS_SELECTOR)

    def click_login(self):
        logger.info("Click login button")
        self.click_element(self.SUBMIT_BUTTON, by=By.CSS_SELECTOR, timeout=10)

    def get_error_message(self):
        for selector in self.ERROR_SELECTORS:
            try:
                message = self.get_text(selector, by=By.CSS_SELECTOR, timeout=2).strip()
            except TimeoutException:
                continue
            if message:
                return message

        validation_message = self.execute_script(
            """
            const selectors = arguments[0];
            for (const selector of selectors) {
                const element = document.querySelector(selector);
                if (element && element.validationMessage) {
                    return element.validationMessage;
                }
            }
            return "";
            """,
            [self.EMAIL_INPUT, self.PASSWORD_INPUT],
        )
        return validation_message or ""

    def logout(self):
        logger.info("Try logout")
        if not self.open_user_menu():
            logger.info("User avatar menu is not available on current page")
            return False

        for by, selector in self.LOGOUT_SELECTORS:
            if self.is_element_visible(selector, by=by, timeout=2):
                self.click_element(selector, by=by, timeout=5)
                logger.info("Logout clicked")
                return True
        logger.info("Logout control is not available on current page")
        return False

    def open_user_menu(self):
        logger.info("Open user menu from bottom-left avatar")
        for by, selector in self.AVATAR_SELECTORS:
            if self.is_element_visible(selector, by=by, timeout=2):
                self.click_element(selector, by=by, timeout=5)
                logger.info("User avatar clicked")
                return True

        avatar = self.execute_script(
            """
            const candidates = Array.from(document.querySelectorAll(
                'button, [role="button"], img, [class*="avatar"], [class*="rounded-full"]'
            ));
            const visible = candidates
                .map(element => {
                    const rect = element.getBoundingClientRect();
                    return { element, rect };
                })
                .filter(({ rect }) => (
                    rect.width > 0 &&
                    rect.height > 0 &&
                    rect.left < window.innerWidth * 0.35 &&
                    rect.top > window.innerHeight * 0.55
                ))
                .sort((a, b) => (b.rect.top - a.rect.top) || (a.rect.left - b.rect.left));
            if (!visible.length) {
                return null;
            }
            const target = visible[0].element.closest('button, [role="button"]') || visible[0].element;
            return target;
            """
        )
        if avatar:
            avatar.click()
            logger.info("Bottom-left avatar clicked by position fallback")
            return True
        return False

    def has_auth_token(self):
        return self.execute_script(
            """
            const keys = arguments[0];
            return keys.some(key => Boolean(window.localStorage.getItem(key) || window.sessionStorage.getItem(key)));
            """,
            list(self.AUTH_TOKEN_KEYS),
        )

    def has_logged_in_element(self):
        return any(
            self.is_element_visible(selector, by=By.CSS_SELECTOR, timeout=2)
            for selector in self.LOGGED_IN_SELECTORS
        )

    def is_login_successful(self):
        logger.info("Check login result")
        current_url = self.get_current_url()
        if "/auth" in current_url:
            logger.info("Login result: failed, still on auth page")
            return False
        result = self.has_auth_token() and self.has_logged_in_element()
        logger.info("Login result: %s", result)
        return result
