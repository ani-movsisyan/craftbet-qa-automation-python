import logging
import os
import re
from datetime import datetime

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


class BasePage:
    """Common methods for all pages."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.TIMEOUT, ignored_exceptions=[StaleElementReferenceException])
        self.log = logging.getLogger(self.__class__.__name__)

    def open(self, path=""):
        url = f"{config.BASE_URL}/{path.lstrip('/')}"
        self.log.info("Open %s", url)
        self.driver.get(url)
        self.wait_page_loaded()

    def wait_page_loaded(self):
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        # site has some hidden duplicates (mobile menu), so I take only visible elements
        visible = []
        for element in self.driver.find_elements(*locator):
            try:
                if element.is_displayed():
                    visible.append(element)
            except StaleElementReferenceException:
                pass  # element was re-rendered by Angular, skip it
        return visible

    def click(self, locator_or_element):
        if isinstance(locator_or_element, tuple):
            element = self.wait.until(EC.element_to_be_clickable(locator_or_element))
        else:
            element = locator_or_element
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        try:
            element.click()
        except ElementClickInterceptedException:
            # chat widget sometimes covers buttons
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def hover(self, element):
        ActionChains(self.driver).move_to_element(element).perform()

    def is_visible(self, locator, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_url_contains(self, text):
        self.wait.until(EC.url_contains(text))

    def page_text(self):
        return self.driver.execute_script("return document.body.innerText")

    def screenshot(self, name):
        os.makedirs("reports/screenshots", exist_ok=True)
        name = re.sub(r"[^\w-]", "_", name)
        path = f"reports/screenshots/{datetime.now():%H%M%S}_{name}.png"
        self.driver.save_screenshot(path)
        return path
