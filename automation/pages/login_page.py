"""
LoginPage: the ERP Single Sign-On screen shown before any module loads.

Use this page object at the start of every test that needs a logged-in
user — call `login(username, password)` once the browser tab is pointed
at BASE_URL.
"""
from urllib.parse import urlsplit

from pages.base_page import BasePage
from utils.logger import action_logger

# Maximum time to wait for the sign-in screen to show after logging out (milliseconds)
LOG_OUT_TIMEOUT = 30000


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

    def wait_for_login_page(self) -> None:
        """Wait until the Username field is visible, so the page is ready to use."""
        self.wait_until_visible(self.username_field, "Username field")

    def log_out(self) -> None:
        """
        End the session by opening the site's /logout address; the sign-in screen
        is then shown. Call it when a test or flow no longer needs the user, so
        the account has no session left open (the ERP allows one session per user
        and a second login ends the first).
        """
        parts = urlsplit(self.page.url)
        action_logger.info("Log out")
        self.page.goto(f"{parts.scheme}://{parts.netloc}/logout", wait_until="domcontentloaded")
        self.page.wait_for_url("**/openid-connect/auth**", timeout=LOG_OUT_TIMEOUT)

    def login(self, username: str, password: str) -> None:
        """
        Type the username and password and click Sign In.
        Never log the password — only the field names are logged.
        """
        self.type_text(self.username_field, username, "Username field")
        self.type_text(self.password_field, password, "Password field")
        self.click(self.sign_in_button, "Sign In button")
        self.wait_for_page_load()
