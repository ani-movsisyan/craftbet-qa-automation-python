# Test scenarios

## Part 1 – UI (Selenium + Pytest)

Login is done one time at the start (fixture `driver`, one browser for all tests), then all scenarios run as logged in user.

### 1. Website Access & Authentication — `test_01_login.py`

| Test | Steps | Validation |
|------|-------|------------|
| test_login | Open craftbet.com, log in with the test account | Site is opened, user is logged in, Log In button is hidden, balance is shown |

### 2. Website Navigation — `test_02_navigation.py`

| Test | Steps | Validation |
|------|-------|------------|
| test_menu_sections | Click Sport, Live, Casino, Live Casino in the menu | Correct URL, page content is loaded, no error |
| test_more_menu | Open "More" menu, click Skill Games | Menu has items, page is loaded |
| test_info_pages | Open Terms, Privacy, AML pages | Page has text, no error |
| test_casino_tabs | Click casino tabs Slots, Table Games, Top | Tab is active, games are shown, each tab has own URL |
| test_back_forward_and_logo_buttons | Casino → Live Casino → browser Back → Forward → Logo | Correct page after each button |

### 3. Game Interaction — `test_03_games.py`

| Test | Steps | Validation |
|------|-------|------------|
| test_demo_games | Open 3 different games in Demo mode, click Play, press SPACE (spin) | Game container is loaded, game is in demo mode, game is drawn (canvas), picture changes after actions |

Games without Demo button (real money only), blocked games and games with provider error are skipped.

### 4. Additional Functionalities — `test_04_features.py`, `test_05_user_journey.py`

| Test | Steps | Validation |
|------|-------|------------|
| test_change_language | English → Русский → English | Menu text is translated, user stays logged in |
| test_search_game | Search "book" and "roulette" | All results contain the text |
| test_add_and_remove_favorite | Add game to favorites, open Favorites tab, remove it | Heart icon changes, game is shown in Favorites, after removing it is not favorite after reload |
| test_account_pages | Open Bets history, Transactions, Payments, Bonuses | Page is opened, user is still logged in |
| test_user_journey | Sport → Live Casino → Casino tab → search → demo game → bets history | All steps pass in one flow |

### Challenges

- Site opens in Armenian, so English is set in `localStorage` before tests.
- Angular site: elements are re-rendered, some exist twice (hidden copy), so only visible elements are used and stale elements are skipped.
- Games are in iframe and drawn on `<canvas>`, there is no HTML to check. I check canvas inside iframe and compare screenshots before/after actions.
- Some games don't start: "Not available in your region", provider error "Your stall disabled" (Legacy Of Dead), empty game (Book Of 4 Horsemen). They are skipped.
- Bug: Promotions page is empty (guest and logged in user).

## Part 2 – API (Postman)

API documentation was not provided, endpoints were found in DevTools → Network tab.
Base URL: `https://websitewebapi.craftbet.com/1/api/Main/`. All 10 requests are **GET** and only read data.

Authorization: token of logged in user (`Token` in request body) and header `Origin: https://craftbet.com`.
This API reads parameters from JSON body also for GET requests, so GET requests have a body.

| # | Category | Endpoint | Validation |
|---|----------|----------|------------|
| 01 | Account Status | GetClientByToken | account found, currency, email verification status; saves clientId and new token |
| 02 | Client Information | GetClientInfo | profile of my account, user name or email, password is not returned |
| 03 | Account Balance | GetClientBalance | balance is number >= 0, my currency, balances list |
| 04 | Payment Methods | GetPartnerPaymentSystems (Type 2) | list of deposit payment methods, each has id |
| 05 | Game Information | GetProductInfo | game name, provider, picture of this game |
| 06 | Deposit Information | GetClientInfo | my account, total deposit amount >= 0, deposit threshold flag |
| 07 | Withdrawal Information | GetPartnerPaymentSystems (Type 1) | list of withdrawal methods, each has id |
| 08 | Transaction History | GetClientInfo | totals of deposits, withdrawals, bets, wins >= 0; withdrawals <= deposits + wins |
| 09 | Bonus Information | GetPartnerShopItems | available bonuses (bonus shop) not empty, each has name and price |
| 10 | Betting History | getbets | bets list, each has game, amount, date; only wins; user names hidden |

For every request: status 200, response time < 3 s, JSON, `ResponseCode` = 0.

### Challenges

- Request 01 returns a new session token and the old one stops working (the site is logged out in the browser). The collection saves the new token for next requests.
- Lists of deposits, withdrawals, transactions, bonuses and bets of the client are returned only by `POST /ApiRequest`.
  This endpoint answers `138 RestrictedDestination` to requests made outside the browser, even with the same body and headers.
  So for these categories GET endpoints with summary data are used (totals from `GetClientInfo`, withdrawal methods, bonus shop, bets widget).
