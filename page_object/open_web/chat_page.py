from base.base import BasePage
from base.logger import get_logger
from selenium.webdriver.common.by import By


logger = get_logger(__name__)


class OpenWebChatPage(BasePage):
    CHAT_INPUT = 'textarea, [contenteditable="true"], [data-testid="chat-input"]'
    NEW_CHAT_LINK = 'a[href="/"]'

    def is_chat_input_visible(self):
        return self.is_element_visible(self.CHAT_INPUT, by=By.CSS_SELECTOR, timeout=5)

    def input_message(self, text):
        logger.info("Input chat message")
        element = self.wait_visible(self.CHAT_INPUT, by=By.CSS_SELECTOR, timeout=5)
        element.click()
        self._set_message_value(text)

    def clear_message(self):
        logger.info("Clear chat message")
        self._set_message_value("")

    def get_message_value(self):
        return self.execute_script(
            """
            const element = document.querySelector(arguments[0]);
            if (!element) {
                return '';
            }
            if ('value' in element) {
                return (element.value || '').trim();
            }
            return (element.innerText || element.textContent || '').trim();
            """,
            self.CHAT_INPUT,
        )

    def click_new_chat(self):
        logger.info("Click new chat from chat page")
        self.click_element(self.NEW_CHAT_LINK, by=By.CSS_SELECTOR, timeout=5)

    def is_send_button_enabled(self):
        return bool(
            self.execute_script(
                """
                const input = document.querySelector(arguments[0]);
                if (!input) {
                    return false;
                }
                const container = input.closest('form') || input.parentElement;
                const buttons = Array.from((container || document).querySelectorAll('button'));
                const candidates = buttons.filter(button => {
                    const text = (button.innerText || button.getAttribute('aria-label') || '').trim();
                    const rect = button.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0 && !/voice|语音/i.test(text);
                });
                const sendButton = candidates[candidates.length - 1];
                return Boolean(sendButton && !sendButton.disabled && sendButton.getAttribute('aria-disabled') !== 'true');
                """,
                self.CHAT_INPUT,
            )
        )

    def _set_message_value(self, text):
        self.execute_script(
            """
            const element = document.querySelector(arguments[0]);
            const value = arguments[1];
            if (!element) {
                return;
            }
            element.focus();
            if ('value' in element) {
                element.value = value;
            } else {
                element.innerText = value;
                element.textContent = value;
                element.innerHTML = value;
            }
            element.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: value }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            self.CHAT_INPUT,
            text,
        )
