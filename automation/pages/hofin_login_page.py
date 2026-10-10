"""
HofinLoginPage: the sign-in screen of HOFIN (the finance application).

Use it at the start of every HOFIN role of the asset registration / addition
flow (creator and approver). HOFA, the Fixed Asset application, has a different
sign-in screen: use `LoginPage` for that one.
"""
import re

from pages.base_page import BasePage
from utils.logger import action_logger

# Maximum time to wait for the HOFIN sign-in screen or the dashboard (milliseconds).
# The first request to HOFIN can take a minute.
HOFIN_LOAD_TIMEOUT = 120000


class HofinLoginPage(BasePage):
    """Page object for the HOFIN "HO Finance" sign-in screen."""

    def __init__(self, page):
        super().__init__(page)
        # Email address text box
        self.username_field = page.get_by_placeholder("Your email address")
        # Password text box
        self.password_field = page.get_by_placeholder("Password")
        # Button that submits the credentials
        self.login_button = page.get_by_role("button", name="Login")
        # Button at the top right that shows the user's name and ID, e.g. "Dijendra Nath Mondal [87200]"
        self.user_menu_button = page.locator("button", has_text=re.compile(r"\[\d+\]")).first
        # Item of the user menu that ends the session
        self.log_out_item = page.get_by_text("Log Out", exact=True)

    def open_login_page(self, hofin_url: str) -> None:
        """Open HOFIN and wait until the sign-in form is shown."""
        action_logger.info(f"Open URL: {hofin_url}")
        self.page.goto(hofin_url, wait_until="domcontentloaded", timeout=HOFIN_LOAD_TIMEOUT)
        self.login_button.wait_for(state="visible", timeout=HOFIN_LOAD_TIMEOUT)
        self.wait_for_page_load()

    def log_out(self) -> None:
        """
        End the session: open the user menu at the top right and click Log Out; the
        sign-in form is then shown. Call it when a flow no longer needs the user.
        """
        self.click(self.user_menu_button, "user menu")
        self.click(self.log_out_item, "Log Out item")
        self.login_button.wait_for(state="visible", timeout=HOFIN_LOAD_TIMEOUT)

    def login(self, username: str, password: str) -> None:
        """
        Type the email address and password, click Login and wait for the
        dashboard. Never logs the password.
        """
        self.type_text(self.username_field, username, "Email address field")
        self.type_text(self.password_field, password, "Password field")
        self.click(self.login_button, "Login button")
        try:
            self.page.wait_for_url("**/brac/dashboard**", timeout=HOFIN_LOAD_TIMEOUT)
        except Exception:
            raise AssertionError(
                "HOFIN did not open the dashboard after Login. Check the HOFIN user name "
                f"and password in .env. The page shows: {self.page.url}"
            )
        self.wait_for_page_load()
