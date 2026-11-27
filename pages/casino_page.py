from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class CasinoPage(BasePage):
    URL = "group/7"
    CATEGORY_TABS = (By.CSS_SELECTOR, ".nav-bar.casino-menu-nav-bar li")
    ACTIVE_TAB = (By.CSS_SELECTOR, ".nav-bar.casino-menu-nav-bar li.active")
    BACK_LINK = (By.XPATH, "//*[normalize-space()='Back' and (self::a or self::div or self::span)]")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='Search your game...']")
    GAME_CARD = (By.CSS_SELECTOR, ".casino-game")
    GAME_NAME = (By.CSS_SELECTOR, ".hidden-game-name")
    DEMO_BUTTON = (By.CSS_SELECTOR, "a.game-btn_demo")
    FAVORITE_ICON = (By.CSS_SELECTOR, ".icon-star-info")

    def open_casino(self):
        self.open(self.URL)
        self.wait_games_loaded()

    def wait_games_loaded(self, minimum=1):
        WebDriverWait(self.driver, 30, ignored_exceptions=[StaleElementReferenceException]).until(
            lambda d: len(self.find_all(self.GAME_CARD)) >= minimum)
        return len(self.find_all(self.GAME_CARD))

    def game_names(self):
        # textContent works also for hidden name element
        names = []
        for card in self.find_all(self.GAME_CARD):
            try:
                names.append(card.find_element(*self.GAME_NAME).get_attribute("textContent").strip())
            except StaleElementReferenceException:
                pass
        return names

    def demo_games(self):
        """Returns [(name, demo_link)] only for games that have Demo button.
        Games with only Real button need real money, so I skip them."""
        games = []
        for card in self.find_all(self.GAME_CARD):
            demo = card.find_elements(*self.DEMO_BUTTON)
            if demo:
                name = card.find_element(*self.GAME_NAME).get_attribute("textContent").strip()
                games.append((name, demo[0].get_dom_attribute("href")))
        return games

    def get_card(self, name):
        return self.driver.find_element(
            By.XPATH, f"//div[contains(concat(' ', @class, ' '), ' casino-game ')]"
                      f"[.//*[contains(@class,'hidden-game-name')][normalize-space()='{name}']]")

    def open_demo_by_click(self, name):
        card = self.get_card(name)
        self.hover(card)
        self.click(card.find_element(*self.DEMO_BUTTON))

    # categories
    def category_names(self):
        return [tab.text.strip() for tab in self.find_all(self.CATEGORY_TABS)]

    def select_category(self, name):
        self.log.info("Select category %s", name)
        tab = (By.XPATH, f"//*[contains(@class,'casino-menu-nav-bar')]//li[normalize-space()='{name}']")
        self.click(tab)
        WebDriverWait(self.driver, 10).until(lambda d: self.active_category() == name)

    def active_category(self):
        tabs = self.driver.find_elements(*self.ACTIVE_TAB)
        return tabs[0].get_attribute("textContent").strip() if tabs else ""

    def go_back_to_lobby(self):
        # in category view the tabs are hidden and there is a "Back" link
        self.click(self.find_all(self.BACK_LINK)[-1])
        WebDriverWait(self.driver, 15).until(lambda d: self.find_all(self.CATEGORY_TABS))

    # search
    def search(self, text):
        self.log.info("Search game: %s", text)
        self.type_text(self.SEARCH_INPUT, text)
        self.find(self.SEARCH_INPUT).send_keys(Keys.ENTER)
        self.wait_url_contains(f"pattern={text}")
        # wait until list is updated with search results
        WebDriverWait(self.driver, 20).until(
            lambda d: self.game_names() and text.lower() in self.game_names()[0].lower())
        return self.game_names()

    # favorites
    def is_favorite(self, name):
        # empty heart = "far" icon, filled heart = "fas" icon
        svg = self.get_card(name).find_element(*self.FAVORITE_ICON).find_element(By.TAG_NAME, "svg")
        return svg.get_attribute("data-prefix") == "fas"

    def click_favorite(self, name):
        icon = self.get_card(name).find_element(*self.FAVORITE_ICON)
        self.driver.execute_script("arguments[0].click();", icon)
