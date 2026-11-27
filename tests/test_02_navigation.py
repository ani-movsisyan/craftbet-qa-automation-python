"""2. Website Navigation: sections, pages, menus, buttons, tabs."""
import pytest
from selenium.webdriver.common.by import By

from pages.casino_page import CasinoPage
from pages.content_page import ContentPage
from pages.header import Header

SECTIONS = [
    ("sport/prematch#/prematch", "sport/prematch"),
    ("sport/live#/live", "sport/live"),
    ("group/7", "group/7"),
    ("products/5", "products/5"),
]

PAGES = ["info/terms", "info/privacy", "info/aml"]


@pytest.mark.parametrize("href, url_part", SECTIONS)
def test_menu_sections(driver, href, url_part):
    Header(driver).click_menu(href)
    page = ContentPage(driver)
    page.wait_url_contains(url_part)
    page.wait_body_loaded()
    assert not page.has_error(), f"Error on page {url_part}"


def test_more_menu(driver):
    header = Header(driver)
    links = header.open_more_menu()
    assert len(links) >= 2, f"More menu has not enough items: {links}"
    header.click((By.CSS_SELECTOR, "li.header-menu-more a[href='group/6']"))  # Skill Games
    page = ContentPage(driver)
    page.wait_url_contains("group/6")
    page.wait_body_loaded()


@pytest.mark.parametrize("path", PAGES)
def test_info_pages(driver, path):
    page = ContentPage(driver)
    page.open(path)
    page.wait_body_loaded(min_text=200)
    assert not page.has_error()
    assert len(page.body_text()) >= 200, "Page text is too short"


def test_casino_tabs(driver):
    casino = CasinoPage(driver)
    casino.open_casino()
    assert {"Top", "Slots", "Table Games"}.issubset(casino.category_names())

    urls = set()
    for tab in ["Slots", "Table Games", "Top"]:
        casino.select_category(tab)
        assert casino.wait_games_loaded() > 0, f"No games in {tab}"
        urls.add(driver.current_url)
        casino.go_back_to_lobby()
    assert len(urls) == 3, "Each tab must have own URL"


def test_back_forward_and_logo_buttons(driver):
    header = Header(driver)
    header.click_menu("group/7")
    header.wait_url_contains("group/7")
    header.click_menu("products/5")
    header.wait_url_contains("products/5")

    driver.back()
    header.wait_url_contains("group/7")
    driver.forward()
    header.wait_url_contains("products/5")

    header.click(Header.LOGO)
    header.wait_url_contains("/home")
