from base.base import BasePage
from base.logger import get_logger
from selenium.webdriver.common.by import By


logger = get_logger(__name__)


class OpenWebHomePage(BasePage):
    MODEL_BUTTON = "button"
    CHAT_INPUT = 'textarea, [contenteditable="true"], [data-testid="chat-input"]'
    NEW_CHAT_LINK = 'a[href="/"]'
    USER_MENU_BUTTON = 'button[aria-label="用户菜单"], button[aria-label*="用户"], button[aria-label*="User"]'
    SIDEBAR_SELECTORS = (
        (By.CSS_SELECTOR, 'a[href="/"]'),
        (By.CSS_SELECTOR, 'a[href="/notes"]'),
        (By.CSS_SELECTOR, 'a[href="/workspace"]'),
        (By.CSS_SELECTOR, USER_MENU_BUTTON),
        (By.XPATH, '//*[self::a or self::button][contains(normalize-space(.), "新对话")]'),
        (By.XPATH, '//*[self::a or self::button][contains(normalize-space(.), "搜索")]'),
        (By.XPATH, '//*[self::a or self::button][contains(normalize-space(.), "笔记")]'),
        (By.XPATH, '//*[self::a or self::button][contains(normalize-space(.), "工作空间")]'),
        (By.XPATH, '//*[self::button][contains(normalize-space(.), "展开侧边栏")]'),
    )

    def is_home_loaded(self):
        return self.is_chat_input_visible() and bool(self.get_current_model())

    def get_current_model(self):
        return self.execute_script(
            """
            const buttons = Array.from(document.querySelectorAll('button'));
            const modelButton = buttons.find(button => {
                const text = (button.innerText || '').trim();
                return text && text.includes(':') && !text.includes('\\n');
            });
            return modelButton ? modelButton.innerText.trim() : '';
            """
        )

    def is_chat_input_visible(self):
        return self.is_element_visible(self.CHAT_INPUT, by=By.CSS_SELECTOR, timeout=5)

    def is_sidebar_visible(self):
        return any(
            self.is_element_visible(selector, by=by, timeout=2)
            for by, selector in self.SIDEBAR_SELECTORS
        )

    def click_new_chat(self):
        logger.info("Click new chat")
        self.click_element(self.NEW_CHAT_LINK, by=By.CSS_SELECTOR, timeout=5)
        return True

    def open_user_menu(self):
        logger.info("Open user menu from home page")
        if self.is_element_visible(self.USER_MENU_BUTTON, by=By.CSS_SELECTOR, timeout=3):
            self.click_element(self.USER_MENU_BUTTON, by=By.CSS_SELECTOR, timeout=5)
            return True

        user_menu = self.execute_script(
            """
            const candidates = Array.from(document.querySelectorAll(
                'button, [role="button"], img, [class*="avatar"], [class*="rounded-full"]'
            ));
            const visible = candidates
                .map(element => ({ element, rect: element.getBoundingClientRect() }))
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
            return visible[0].element.closest('button, [role="button"]') || visible[0].element;
            """
        )
        if user_menu:
            user_menu.click()
            return True
        return False
