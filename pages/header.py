from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class Header(BasePage):
    LOGO = (By.CSS_SELECTOR, "a.image-style2[href='/home']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button.global_login-btn")
    LANGUAGE_DROPDOWN = (By.CSS_SELECTOR, ".global-language .dropdown-style1-type-Dpd")
    MORE_MENU = (By.CSS_SELECTOR, "li.header-menu-more > a")
    MORE_MENU_LINKS = (By.CSS_SELECTOR, "li.header-menu-more .general-menu-sub-menu a[href]")
    BALANCE = (By.CSS_SELECTOR, "[class*='balance' i]")

    # login popup
    USERNAME_INPUT = (By.NAME, "ClientIdentifier")
    PASSWORD_INPUT = (By.NAME, "Password")
    LOGIN_SUBMIT = (By.CSS_SELECTOR, "button.login_btn")

    def menu_item(self, href):
        return By.CSS_SELECTOR, f"a.header-menu-item-style1[href='{href}']"

    def click_menu(self, href):
        self.log.info("Click menu item %s", href)
        self.click(self.menu_item(href))
        self.wait_page_loaded()

    def open_more_menu(self):
        WebDriverWait(self.driver, 15).until(lambda d: self.find_all(self.MORE_MENU))
        more = self.find_all(self.MORE_MENU)[0]  # first "More" in html is hidden, so I use visible one
        self.hover(more)
        if not self.find_all(self.MORE_MENU_LINKS):
            self.click(more)
        WebDriverWait(self.driver, 5).until(lambda d: self.find_all(self.MORE_MENU_LINKS))
        return [link.get_dom_attribute("href") for link in self.find_all(self.MORE_MENU_LINKS)]

    def switch_language(self, language_name, language_code):
        self.log.info("Switch language to %s", language_name)
        self.click(self.LANGUAGE_DROPDOWN)
        item = (By.XPATH, f"//*[contains(@class,'custom_dropdown_list_item')][.//span[text()='{language_name}']]")
        self.click(self.find(item))
        # page reloads after language change
        WebDriverWait(self.driver, 30).until(
            lambda d: d.execute_script("return document.documentElement.lang") == language_code)
        self.wait_page_loaded()

    def login(self, username, password):
        self.log.info("Login with test account from .env")
        self.wait_page_loaded()
        self.click(self.LOGIN_BUTTON)
        for locator, value in [(self.USERNAME_INPUT, username), (self.PASSWORD_INPUT, password)]:
            self.type_text(locator, value)
            # check that the field has exactly the value from .env (page can re-render while typing)
            WebDriverWait(self.driver, 5).until(lambda d: self.find(locator).get_attribute("value") == value
                                                or self.type_text(locator, value))
        self.click(self.LOGIN_SUBMIT)

    def is_logged_in(self, timeout=20):
        # after login the "Log In" button disappears and the site saves token in localStorage
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: not self.find_all(self.LOGIN_BUTTON))
            # note: chat widget also has a key "twk_token_...", so I check only the site's own keys
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script(
                "return !!localStorage.getItem('token') || Object.keys(localStorage)"
                ".some(k => /user$/i.test(k) && localStorage[k].includes('\"Token\"'))"))
            return True
        except Exception:
            return False

    def is_balance_visible(self):
        try:
            WebDriverWait(self.driver, 10).until(lambda d: self.find_all(self.BALANCE))
            return True
        except Exception:
            return False
