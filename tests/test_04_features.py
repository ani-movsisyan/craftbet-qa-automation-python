"""4. Additional Functionalities & User Interactions (without deposit / real money)."""
import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.casino_page import CasinoPage
from pages.content_page import AccountPage
from pages.header import Header


def test_change_language(driver):
    header = Header(driver)
    header.open("home")
    casino_menu = header.menu_item("group/7")
    assert header.find(casino_menu).text == "Casino"

    header.switch_language("Русский", "ru")
    assert driver.execute_script("return localStorage.getItem('lang')") == "ru"
    WebDriverWait(driver, 15).until(lambda d: header.find(casino_menu).text not in ("", "Casino"))
    assert header.is_logged_in(timeout=5), "User was logged out after language change"

    header.switch_language("English", "en")
    WebDriverWait(driver, 15).until(lambda d: header.find(casino_menu).text == "Casino")


@pytest.mark.parametrize("text", ["book", "roulette"])
def test_search_game(driver, text):
    casino = CasinoPage(driver)
    casino.open_casino()
    results = casino.search(text)
    assert results, f"Nothing found for {text}"
    wrong = [name for name in results if text not in name.lower()]
    assert not wrong, f"Wrong results: {wrong}"


def test_add_and_remove_favorite(driver):
    casino = CasinoPage(driver)
    casino.open_casino()
    name = casino.demo_games()[0][0]
    if casino.is_favorite(name):
        # left from previous failed run - remove it first
        casino.click_favorite(name)
        WebDriverWait(driver, 10).until(lambda d: not casino.is_favorite(name))

    # add to favorites
    casino.click_favorite(name)
    WebDriverWait(driver, 10).until(lambda d: casino.is_favorite(name))
    casino.select_category("Favorites")
    WebDriverWait(driver, 15).until(lambda d: name in casino.game_names())

    # remove from favorites - the game disappears from Favorites tab
    casino.click_favorite(name)
    WebDriverWait(driver, 15).until(lambda d: name not in casino.game_names())

    # check that it is saved: open lobby again, heart must be empty
    casino.open_casino()
    WebDriverWait(driver, 15).until(lambda d: not casino.is_favorite(name))


@pytest.mark.parametrize("page_name", ["bets history", "transactions", "payments", "bonuses"])
def test_account_pages(driver, page_name):
    account = AccountPage(driver)
    account.open_account_page(page_name)
    assert account.is_visible(AccountPage.DATA_AREA, timeout=15), f"{page_name} page is empty"
    assert Header(driver).is_logged_in(timeout=5), "User was logged out"
