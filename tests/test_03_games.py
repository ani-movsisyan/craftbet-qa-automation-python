"""3. Game Interaction: several casino games, only demo mode."""
import logging

from pages.casino_page import CasinoPage
from pages.game_page import GamePage

log = logging.getLogger("test_games")


def test_demo_games(driver):
    casino = CasinoPage(driver)
    casino.open_casino()
    # only games with Demo button (no real money), same game can be in several rows - remove duplicates
    games = list(dict((link, name) for name, link in casino.demo_games()).items())
    assert games, "No demo games in the lobby"

    game = GamePage(driver)
    played = []
    for link, name in games[:6]:
        if len(played) == 3:
            break
        if not game.open_demo_game(name, link):
            continue
        game.screenshot(f"loaded_{name}")

        before = game.game_screenshot()
        game.play_demo()
        assert game.game_screenshot() != before, f"{name} did not change after clicks"
        assert "/demo/" in driver.current_url, "Game must stay in demo mode"
        game.screenshot(f"played_{name}")
        played.append(name)

    log.info("Played demo games: %s", played)
    assert len(played) >= 2, f"Less than 2 demo games worked: {played}"
