from base.base import BasePage
from config.config_loader import get_web_base_url
from selenium.webdriver.common.by import By


class OpenWebLoginPage(BasePage):
    EMAIL_INPUT = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    SUBMIT_BUTTON = 'button[type="submit"]'
    BODY = "body"
    AUTH_TOKEN_KEYS = ("token", "access_token", "auth_token", "jwt")
    LOGGED_IN_SELECTORS = (
        'textarea',
        '[data-testid="chat-input"]',
        '[aria-label*="New Chat"]',
        'a[href="/workspace"]',
    )

    def open(self):
        self.go_url(get_web_base_url())

    def clear_browser_state(self):
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
        self.input_text(self.EMAIL_INPUT, email, by=By.CSS_SELECTOR)
        self.input_text(self.PASSWORD_INPUT, password, by=By.CSS_SELECTOR)
        self.click_element(self.SUBMIT_BUTTON, by=By.CSS_SELECTOR, timeout=10)

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
        current_url = self.get_current_url()
        if "/auth" in current_url:
            return False
        return self.has_auth_token() and self.has_logged_in_element()
