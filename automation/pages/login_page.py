"""
LoginPage: the ERP Single Sign-On screen shown before any module loads.

Use this page object at the start of every test that needs a logged-in
user — call `login(username, password)` once the browser tab is pointed
at BASE_URL.
"""
import re

from pages.base_page import BasePage
from utils.helpers import simplify_office_text
from utils.logger import action_logger, assertion_logger

# Maximum time to wait for the browser to leave the sign-in screen after Sign In (milliseconds)
LOGIN_CHECK_TIMEOUT = 15000

# Maximum time to wait for the Office Selection screen before treating the user as single-office (milliseconds)
OFFICE_SCREEN_TIMEOUT = 5000

# Any address that is not on the sign-in server (its addresses contain /idp/)
SIGNED_IN_URL = re.compile(r"^(?!.*/idp/).*$")


class LoginPage(BasePage):
    """Page object for the "Sign in to your account" screen."""

    def __init__(self, page):
        super().__init__(page)
        # Username text box
        self.username_field = page.get_by_role("textbox", name="Username")
        # Password text box
        self.password_field = page.get_by_role("textbox", name="Password")
        # Button that submits the credentials
        self.sign_in_button = page.get_by_role("button", name="Sign In")
        # Error text shown on the sign-in screen after a wrong username or password
        self.invalid_login_message = page.get_by_text("Invalid username or password.")
        # Heading of the Office Selection screen (shown only to users with more than one office)
        self.office_heading = page.get_by_role("heading", name="Please select office to login")
        # Arrow that opens the office list
        self.office_arrow = page.locator("#officeIdDiv_arrow")
        # Box that shows the chosen office
        self.office_box = page.locator("#officeIdDiv_input")
        # Every office in the opened list
        self.office_options = page.locator("#officeIdDiv_ctr .row .col-0")
        # Button that confirms the chosen office
        self.go_button = page.get_by_role("button", name="Go", exact=True)
        # Round user icon at the top right that opens the account menu
        self.user_menu_button = page.locator("#btn_login")
        # Logout link inside the account menu
        self.logout_link = page.locator('#login_container a[href="/logout"]')

    def wait_for_login_page(self) -> None:
        """Wait until the Username field is visible, so the page is ready to use."""
        self.wait_until_visible(self.username_field, "Username field")

    def login(self, username: str, password: str) -> None:
        """
        Type the username and password and click Sign In.
        Never log the password — only the field names are logged.
        """
        self.type_text(self.username_field, username, "Username field")
        self.type_text(self.password_field, password, "Password field")
        self.click(self.sign_in_button, "Sign In button")
        self.wait_for_page_load()

    def log_out(self) -> None:
        """
        End the session: open the account menu at the top right, click Logout and wait
        for the sign-in screen. The account then has no open session, so another
        stage or test can sign in with it. Call it when a flow no longer needs the user.
        """
        self.click(self.user_menu_button, "Account menu icon")
        self.click(self.logout_link, "Logout link")
        self.wait_for_login_page()

    def verify_logged_in(self, username: str) -> None:
        """
        Check that the login worked, and stop with a clear reason if it did not.
        Call it right after `login()`. Example:
            login_page.login(ERP_USERNAME, ERP_PASSWORD)
            login_page.verify_logged_in(ERP_USERNAME)
        Only the username is written in the failure text, never the password.
        """
        # Step 1: the sign-in screen is showing its "wrong username or password" error
        if self.is_visible(self.invalid_login_message):
            reason = f"Login failed for {username}: the ERP says 'Invalid username or password.'"
            assertion_logger.error(reason)
            raise AssertionError(reason)

        # Step 2: otherwise the browser must leave the sign-in server
        try:
            self.page.wait_for_url(SIGNED_IN_URL, timeout=LOGIN_CHECK_TIMEOUT)
        except Exception:
            reason = f"Login failed for {username}: the sign-in screen was still shown after {LOGIN_CHECK_TIMEOUT // 1000} seconds."
            assertion_logger.error(reason)
            raise AssertionError(reason)
        self.wait_for_page_load()
        assertion_logger.info(f"Login worked for {username}")

    def select_office_if_asked(self, office: str = None) -> None:
        """
        Choose the office on the Office Selection screen, when the ERP shows it.
        Call it right after `verify_logged_in()`. Example:
            login_page.verify_logged_in(ERP_USERNAME)
            login_page.select_office_if_asked(DEFAULT_BRANCH)

        - A user with one office goes straight to the dashboard: nothing is done.
        - A user with several offices must have `office` set (the DEFAULT_BRANCH value
          in .env). It is matched against the office text, for example
          "- Development" or the code "6981". It must match exactly one office.
        """
        # Step 1: this screen only exists for users with more than one office
        if not self.is_shown_within(self.office_heading, "Office Selection heading", OFFICE_SCREEN_TIMEOUT):
            action_logger.info("No Office Selection screen, nothing to choose")
            return

        # Step 2: open the list and read every office name
        self.click(self.office_arrow, "Office list arrow")
        self.wait_until_visible(self.office_options.first, "First office in the list")
        office_names = self.office_options.all_inner_texts()

        # Step 3: pick the one office that matches
        chosen = self.find_office(office_names, office)
        office_list = self.page.locator("#officeIdDiv_ctr")
        self.click(office_list.get_by_text(chosen, exact=True), f"Office {chosen}")

        # Step 4: confirm and wait for the dashboard
        self.click(self.go_button, "Go button")
        self.page.wait_for_url(re.compile(r"^(?!.*selectLogInOffice).*$"), timeout=LOGIN_CHECK_TIMEOUT)
        self.wait_for_page_load()
        assertion_logger.info(f"Office selected: {chosen}")

    def find_office(self, office_names: list, office: str) -> str:
        """
        Return the one office name that matches `office`, and stop with a clear
        reason when none or several match. An exact name wins over a partial one.
        With no `office` given, a list holding a single office is accepted.
        """
        if not office:
            if len(office_names) == 1:
                return office_names[0]
            reason = f"This user has several offices but DEFAULT_BRANCH is not set in .env. Offices: {office_names}"
            assertion_logger.error(reason)
            raise AssertionError(reason)

        # Spaces and hyphens are ignored, so "[BO-0233]-Name" finds "[BO - 0233] Name"
        wanted = simplify_office_text(office)
        exact = [name for name in office_names if simplify_office_text(name) == wanted]
        partial = [name for name in office_names if wanted in simplify_office_text(name)]
        matches = exact or partial
        if len(matches) != 1:
            reason = f"Office '{office}' matched {len(matches)} offices, expected 1. Offices: {office_names}"
            assertion_logger.error(reason)
            raise AssertionError(reason)
        return matches[0]
