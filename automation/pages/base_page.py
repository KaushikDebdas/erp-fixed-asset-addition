"""
BasePage: the small set of actions every page object needs.

Why this file exists:
    Every page (login, dashboard, reports, ...) needs to do the same basic
    things: open a URL, click, type, read text, wait for something to show up.
    Instead of repeating those lines in every page class, we write them ONCE
    here and let each page class "inherit" them.

How to use it:
    class LoginPage(BasePage):
        def __init__(self, page):
            super().__init__(page)   # <- gives you self.page and all methods below

Keep this file small and boring. Only add an action here when at least two
different pages need it. Page-specific actions belong in that page's class.
"""
from urllib.parse import urlsplit

from playwright.sync_api import Locator, Page, expect

from utils.logger import action_logger

# Maximum time to wait for a grid to show its new rows after a Search (milliseconds)
GRID_RELOAD_TIMEOUT = 15000

# Maximum time to wait for a suggestion list or a calendar to open (milliseconds)
POPUP_OPEN_TIMEOUT = 8000

# Number of times a search button / calendar icon is used to open its list
OPEN_LIST_ATTEMPTS = 3

# Path of the Fixed Asset module on the ERP site
FIXED_ASSET_PATH = "/nodef/fixedasset"


class BasePage:
    """Common actions shared by every page object."""

    def __init__(self, page: Page):
        """
        Remember the Playwright page (the browser tab) we are working in.
        Every page object receives it from the test through a fixture.
        """
        self.page = page

    def open(self, url: str) -> None:
        """Open a URL in the browser tab."""
        action_logger.info(f"Open URL: {url}")
        self.page.goto(url)
        self.wait_for_page_load()

    def wait_for_page_load(self) -> None:
        """Wait until the page and all its scripts, styles and images have finished loading."""
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("load")

    def click(self, element: Locator, element_name: str) -> None:
        """
        Click an element.
        `element_name` is a human-readable name (e.g. "Sign In button"). It is
        only used in the log, so whoever reads the log knows what was clicked.
        """
        action_logger.info(f"Click: {element_name}")
        element.click()

    def type_text(self, element: Locator, text: str, element_name: str) -> None:
        """
        Clear a text box and type into it.
        We log the field name but NOT the text, because the text may be a
        password. Never print secrets to logs.
        """
        action_logger.info(f"Type into: {element_name}")
        element.fill(text)

    def get_text(self, element: Locator, element_name: str) -> str:
        """Return the visible text of an element."""
        action_logger.info(f"Read text of: {element_name}")
        return element.inner_text()

    def is_visible(self, element: Locator) -> bool:
        """Return True if the element is currently shown on the page."""
        return element.is_visible()

    def wait_until_visible(self, element: Locator, element_name: str) -> None:
        """
        Wait (up to Playwright's default 30 seconds) until the element appears.
        Use this after an action that loads something new, instead of sleeping
        for a fixed number of seconds.
        """
        action_logger.info(f"Wait until visible: {element_name}")
        element.wait_for(state="visible")

    def is_shown_within(self, element: Locator, element_name: str, timeout: int = POPUP_OPEN_TIMEOUT) -> bool:
        """
        Wait up to `timeout` milliseconds for an element to appear and return
        True if it did, False if it did not. Use it in a short loop that
        opens a suggestion list or a calendar and checks it is shown:

            for attempt in range(OPEN_LIST_ATTEMPTS):
                self.click(search_icon, "Search button")
                if self.is_shown_within(suggestion, "Suggestion"):
                    break
        """
        try:
            element.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            action_logger.info(f"Not shown yet: {element_name}")
            return False

    def open_fixed_asset_module(self) -> None:
        """
        Open the Fixed Asset module from the ERP home page that shows after
        login. The module lives on the same site as the page we are on, so
        its address is built from the current site address.
        """
        parts = urlsplit(self.page.url)
        self.open(f"{parts.scheme}://{parts.netloc}{FIXED_ASSET_PATH}")
        self.wait_until_visible(
            self.page.get_by_text("Registration", exact=True).first, "Registration menu"
        )

    def open_registration_submenu(self, link_name: str) -> None:
        """
        Open a link from the Fixed Asset module's "Registration" flyout menu.

        The top navigation bar inside the Fixed Asset module shows category
        names ("Setup", "Registration", "Asset Profile", ...) that are plain
        text, not links — hovering over one opens a flyout list of real
        links. This is shared by every Registration-area page (Asset
        Registration by AAQ, Asset Registration List, Asset Registration
        Approval List), so it lives here instead of being copied three times.

        `link_name` is the visible text of the flyout link to click, e.g.
        "Asset Registration by AAQ".
        """
        # Start from a freshly loaded module so the next screen opens as a
        # clean form, whatever screen the previous test left behind.
        self.open_fixed_asset_module()
        # The dashboard also has a "Registration" tile, so take the first
        # match, which is the menu bar item.
        registration_menu = self.page.get_by_text("Registration", exact=True).first
        self.click(registration_menu, "Registration menu")
        link = self.page.get_by_role("link", name=link_name)
        self.wait_until_visible(link, f"{link_name} menu link")
        self.click(link, f"{link_name} menu link")
        self.wait_for_page_load()

    def open_asset_profile_submenu(self, link_name: str) -> None:
        """
        Open a link from the Fixed Asset module's "Asset Profile" menu
        (Asset Serial Global List, Generate Barcode, Asset In Pending
        Process List, Asset Serial Split, Asset Serial Split List, Asset
        Serial Split Approval List). Works like `open_registration_submenu`.
        """
        self.open_fixed_asset_module()
        asset_profile_menu = self.page.get_by_text("Asset Profile", exact=True).first
        self.click(asset_profile_menu, "Asset Profile menu")
        link = self.page.get_by_role("link", name=link_name, exact=True)
        self.wait_until_visible(link, f"{link_name} menu link")
        self.click(link, f"{link_name} menu link")
        self.wait_for_page_load()

    def open_asset_transaction_submenu(self, link_name: str) -> None:
        """
        Open a link from the Fixed Asset module's "Asset Transaction" menu
        (Asset Assign, Asset Un Assign, Asset Internal Movement, Transaction
        List, Transaction Approval List, Asset Assign Acknowledgement).
        Works like `open_registration_submenu`.
        """
        self.open_fixed_asset_module()
        asset_transaction_menu = self.page.get_by_text("Asset Transaction", exact=True).first
        self.click(asset_transaction_menu, "Asset Transaction menu")
        link = self.page.get_by_role("link", name=link_name, exact=True)
        self.wait_until_visible(link, f"{link_name} menu link")
        self.click(link, f"{link_name} menu link")
        self.wait_for_page_load()

    def open_asset_transfer_submenu(self, link_name: str) -> None:
        """
        Open a link from the Fixed Asset module's "Asset Transfer" menu (Asset
        Shipment, Asset Shipment Challan Approval List, Asset Shipment
        In-Challan, Gate Pass Generation). Works like `open_registration_submenu`.
        """
        self.open_fixed_asset_module()
        asset_transfer_menu = self.page.get_by_text("Asset Transfer", exact=True).first
        self.click(asset_transfer_menu, "Asset Transfer menu")
        link = self.page.get_by_role("link", name=link_name, exact=True)
        self.wait_until_visible(link, f"{link_name} menu link")
        self.click(link, f"{link_name} menu link")
        self.wait_for_page_load()

    def open_asset_expenditure_submenu(self, link_name: str) -> None:
        """
        Open a link from the Fixed Asset module's "Asset Expenditure" menu
        (Asset Expense, Asset Expense Approval, Asset Addition From
        Inventory / Vendor and their approvals). Works like
        `open_registration_submenu`.
        """
        self.open_fixed_asset_module()
        expenditure_menu = self.page.get_by_text("Asset Expenditure", exact=True).first
        self.click(expenditure_menu, "Asset Expenditure menu")
        link = self.page.get_by_role("link", name=link_name, exact=True)
        self.wait_until_visible(link, f"{link_name} menu link")
        self.click(link, f"{link_name} menu link")
        self.wait_for_page_load()

    def wait_for_grid_refresh(self) -> None:
        """
        Wait until a grid has finished reloading after a Search. The page
        has no spinner to watch, so this waits for the network to go quiet,
        for at most 10 seconds, and then carries on.
        """
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            action_logger.info("Network still busy after 10 seconds, continuing")

    def wait_for_grid_to_reload(self, entries_info: Locator) -> None:
        """
        Wait until a grid has shown the result of a Search.

        The line under the grid ("Showing 1 to 10 of 124 entries") is emptied
        the moment Search is clicked and filled again when the new rows
        arrive, so waiting for it to have text means the new rows are shown.
        `entries_info` is that line, e.g. page.locator(".dataTables_info").
        """
        action_logger.info("Wait until: grid shows the search result")
        expect(entries_info).not_to_have_text("", timeout=GRID_RELOAD_TIMEOUT)

    def wait_for_rows_per_page(self, rows: Locator, size: int, total_entries: int) -> None:
        """
        Wait until a grid shows the number of rows a new "Records per page"
        choice should give: `size` rows, or all of them when there are fewer.
        `rows` is the grid's body rows, e.g. page.locator("#grid tbody tr").
        """
        action_logger.info(f"Wait until: grid shows {size} rows per page")
        expected_rows = min(size, total_entries)
        expect(rows).to_have_count(expected_rows, timeout=GRID_RELOAD_TIMEOUT)

    def wait_for_page_shown(self, entries_info: Locator, page_number: int, size: int) -> None:
        """
        Wait until the line under a grid says it is showing the given page,
        e.g. page 2 with 10 rows per page shows "Showing 11 to 20 of ...".
        """
        action_logger.info(f"Wait until: grid shows page {page_number}")
        first_row_number = (page_number - 1) * size + 1
        expect(entries_info).to_contain_text(f"Showing {first_row_number} to", timeout=GRID_RELOAD_TIMEOUT)

    def wait_for_row_or_no_data(self, table: Locator, text: str) -> None:
        """
        Wait until the grid shows either a row containing `text` or the
        "No data available in table" message, so a check made right after a
        Search never reads the previous result.
        """
        row = table.locator("tbody tr", has_text=text)
        no_data = table.locator("tbody tr", has_text="No data available in table")
        row.or_(no_data).first.wait_for(state="visible")

    def wait_for_toast_to_clear(self, timeout: int = 15000) -> None:
        """
        Wait until no toast is on screen. Call this before an action that
        shows its own toast, so the toast read afterwards is the new one
        and not the previous action's message still fading out.
        """
        self.page.locator(".toast-message").first.wait_for(state="hidden", timeout=timeout)

    def get_toast_text(self, timeout: int = 10000) -> str:
        """
        Return the text of the toast/notification message currently shown
        on screen (e.g. after Draft, Submit or Approve). Toasts use the
        `.toast-message` class and fade out after a few seconds, so this
        must be called immediately after the action that triggers one.
        """
        toast = self.page.locator(".toast-message").first
        toast.wait_for(state="visible", timeout=timeout)
        text = toast.inner_text()
        action_logger.info(f"Toast message shown: {text}")
        return text

    def close_popup_if_present(self, timeout: int = 3000) -> None:
        """
        Close the image/announcement popup that sometimes appears after login
        (id="modals", e.g. the "Discover Authentic Bangladesh" banner).
        It is a custom component, not an ARIA dialog, so it needs its own
        selector instead of a role-based locator.

        The popup is closed by clicking the dark overlay behind it, near the
        top-left corner of the page, which is always outside the popup box.
        The close (x) button is not used because on a small screen the popup
        is taller than the window and the button is above the visible area.

        If the popup never shows up within `timeout` ms, this does nothing
        and moves on — it is expected to be absent most of the time.
        """
        popup = self.page.locator("#modals.active")
        try:
            popup.wait_for(state="visible", timeout=timeout)
        except Exception:
            action_logger.info("Popup not shown, nothing to close")
            return
        action_logger.info("Close: popup image (click outside the popup)")
        self.page.locator("#overlay.active").click(position={"x": 5, "y": 5})
        popup.wait_for(state="hidden")
