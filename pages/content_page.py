from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class ContentPage(BasePage):
    """Any page of the site. Page body is inside .router_section (without header and footer)."""
    PAGE_BODY = (By.CSS_SELECTOR, ".router_section > :not(router-outlet)")
    ERRORS = ["404", "page not found", "something went wrong", "server error"]

    def body_text(self):
        return " ".join(e.text for e in self.driver.find_elements(*self.PAGE_BODY)).strip()

    def wait_body_loaded(self, min_text=50):
        """Page body must have text, or pictures (Live Casino), or iframe (Sport)."""
        def loaded(driver):
            for body in driver.find_elements(*self.PAGE_BODY):
                if body.size["height"] < 150:
                    continue
                if len(body.text) >= min_text:
                    return True
                if any(i.is_displayed() for i in body.find_elements(By.TAG_NAME, "img")):
                    return True
                if any(f.size["height"] > 200 for f in body.find_elements(By.TAG_NAME, "iframe")):
                    return True
            return False

        WebDriverWait(self.driver, 30).until(loaded)

    def has_error(self):
        first_lines = self.page_text().lower().split("\n")[:40]
        return any(error in line for line in first_lines for error in self.ERRORS)


class AccountPage(BasePage):
    PAGES = {
        "bets history": "user/1/history",
        "transactions": "user/1/transactions",
        "payments": "user/1/payments",
        "bonuses": "user/1/bonuses",
    }
    DATA_AREA = (By.CSS_SELECTOR, "table, [class*='history' i], [class*='no-data' i], [class*='empty' i]")

    def open_account_page(self, name):
        self.open(self.PAGES[name])
        self.wait_url_contains(self.PAGES[name].split("/")[-1])
