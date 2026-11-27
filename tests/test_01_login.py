from selenium.webdriver.support.ui import WebDriverWait

import config
from pages.header import Header


def test_login(driver):
    """1. Website Access & Authentication.
    Site is opened and login is done in the "driver" fixture, here I verify the result."""
    header = Header(driver)
    WebDriverWait(driver, 20).until(lambda d: "craftbet" in d.title.lower())
    assert driver.current_url.startswith(config.BASE_URL)

    assert header.is_logged_in(), "User is not logged in"
    assert not header.is_visible(Header.LOGIN_BUTTON, timeout=2), "Log In button is still shown"
    assert header.is_balance_visible(), "Balance is not shown after login"
