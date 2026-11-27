import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class GamePage(BasePage):
    GAME_IFRAME = (By.ID, "main-game-iframe")
    GAME_AREA = (By.CSS_SELECTOR, ".game-content")

    def wait_game_container(self):
        iframe = self.find(self.GAME_IFRAME)
        # iframe gets provider url and correct size after some seconds
        WebDriverWait(self.driver, 40).until(
            lambda d: iframe.get_attribute("src").startswith("http")
            and iframe.size["width"] > 600 and iframe.size["height"] > 300)
        return iframe

    def game_url(self):
        return self.find(self.GAME_IFRAME).get_attribute("src")

    def is_demo_mode(self):
        # providers mark demo differently: mode=fun, demo, ...
        url = self.game_url().lower()
        return "/demo/" in self.driver.current_url and ("fun" in url or "demo" in url)

    def is_launched(self):
        # game is not started if there is no iframe or iframe shows the site itself
        frames = self.driver.find_elements(*self.GAME_IFRAME)
        if not frames:
            return False
        src = frames[0].get_attribute("src") or ""
        return src.startswith("http") and not src.startswith("https://craftbet.com")

    def is_region_blocked(self):
        areas = self.driver.find_elements(*self.GAME_AREA)
        return bool(areas) and "not available in your region" in areas[0].text.lower()

    def has_canvas(self):
        """Game is drawn on <canvas>. Some providers (Pragmatic) have one more iframe inside."""
        self.driver.switch_to.frame(self.find(self.GAME_IFRAME))
        try:
            if self.driver.find_elements(By.TAG_NAME, "canvas"):
                return True
            for inner in self.driver.find_elements(By.TAG_NAME, "iframe"):
                self.driver.switch_to.frame(inner)
                found = bool(self.driver.find_elements(By.TAG_NAME, "canvas"))
                self.driver.switch_to.parent_frame()
                if found:
                    return True
            return False
        finally:
            self.driver.switch_to.default_content()

    def wait_game_loaded(self, timeout=45):
        WebDriverWait(self.driver, timeout).until(lambda d: self.has_canvas())
        time.sleep(6)  # provider shows own loading bar, no element to wait for

    def open_demo_game(self, name, link):
        """Open demo game and wait until it is loaded.
        Returns False (game is skipped) if it is blocked, not started by provider or not drawn."""
        self.log.info("Open demo game: %s", name)
        self.open(link)
        self.wait_url_contains("/demo/")
        try:
            self.wait_game_container()
        except TimeoutException:
            pass  # blocked game may have no normal iframe, checked below
        if self.is_region_blocked() or not self.is_launched():
            self.log.warning("%s is not available - skipped", name)
            return False
        assert self.is_demo_mode(), f"{name} is not in demo mode"
        try:
            self.wait_game_loaded()
        except Exception:
            self.log.warning("%s did not load (provider error) - skipped", name)
            return False
        return True

    def game_screenshot(self):
        return self.find(self.GAME_IFRAME).screenshot_as_png

    def play_demo(self):
        """Click Play/Continue and press SPACE (spin). In demo mode it uses only fun credits."""
        iframe = self.find(self.GAME_IFRAME)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", iframe)
        height = iframe.size["height"]
        ActionChains(self.driver).move_to_element(iframe).click().perform()  # focus game
        time.sleep(1.5)
        ActionChains(self.driver).move_to_element_with_offset(iframe, 0, int(height * 0.35)).click().perform()
        time.sleep(1.5)
        for _ in range(2):
            ActionChains(self.driver).send_keys(Keys.SPACE).perform()
            time.sleep(3)
