import base64
import os
import re
import sys

import pytest
from selenium import webdriver

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
from pages.header import Header  # noqa: E402


@pytest.fixture(scope="session")
def driver():
    """One browser for all tests. Login is done one time here, then all tests work as logged in user."""
    if not config.USERNAME or not config.PASSWORD:
        pytest.exit("No test account: write CRAFTBET_USERNAME and CRAFTBET_PASSWORD to .env file", returncode=1)

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-notifications")
    if config.HEADLESS:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)  # chromedriver is downloaded by Selenium Manager
    driver.set_page_load_timeout(60)
    try:
        # site opens in Armenian by default, I switch it to English so texts in tests are stable
        driver.get(config.BASE_URL + "/home")
        driver.execute_script("localStorage.setItem('lang', 'en')")
        driver.refresh()

        header = Header(driver)
        header.login(config.USERNAME, config.PASSWORD)
        logged_in = header.is_logged_in()
        if not logged_in:
            os.makedirs("reports", exist_ok=True)
            driver.save_screenshot("reports/login_failed.png")
    except Exception:
        driver.quit()
        raise
    if not logged_in:
        driver.quit()
        # stop all tests: without login the other scenarios make no sense
        pytest.exit("Login failed - check login and password in .env (screenshot: reports/login_failed.png)",
                    returncode=1)
    yield driver
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add screenshot of the browser to the html report after each test."""
    outcome = yield
    report = outcome.get_result()
    driver = item.funcargs.get("driver")
    if report.when != "call" or driver is None:
        return
    os.makedirs("reports/screenshots", exist_ok=True)
    file_name = re.sub(r"[^\w-]", "_", item.name)  # test names can have "/" from parameters
    path = f"reports/screenshots/{'FAILED' if report.failed else 'PASSED'}_{file_name}.png"
    try:
        driver.save_screenshot(path)
    except Exception:
        return
    from pytest_html import extras
    with open(path, "rb") as f:
        image = base64.b64encode(f.read()).decode()
    report.extras = getattr(report, "extras", []) + [extras.png(image)]
