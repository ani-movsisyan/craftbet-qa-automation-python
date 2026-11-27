from pages.casino_page import CasinoPage
from pages.content_page import AccountPage, ContentPage
from pages.game_page import GamePage
from pages.header import Header


def test_user_journey(driver):
    """Expected outcome of the task: complete user journey with many actions in one run.
    login (fixture) -> sport -> live casino -> casino tab -> search -> demo game -> bets history"""
    header = Header(driver)
    assert header.is_logged_in()

    header.click_menu("sport/prematch#/prematch")
    ContentPage(driver).wait_body_loaded()

    header.click_menu("products/5")
    ContentPage(driver).wait_body_loaded()

    casino = CasinoPage(driver)
    casino.open_casino()
    casino.select_category("Slots")
    casino.go_back_to_lobby()
    assert casino.search("hot"), "Search returned nothing"

    # play the first demo game from results that really works
    game = GamePage(driver)
    played = None
    for name, link in casino.demo_games()[:5]:
        if game.open_demo_game(name, link):
            game.play_demo()
            played = name
            break
    assert played, "No demo game could be played"

    account = AccountPage(driver)
    account.open_account_page("bets history")
    assert account.is_visible(AccountPage.DATA_AREA, timeout=15)
    assert header.is_logged_in(timeout=5)
