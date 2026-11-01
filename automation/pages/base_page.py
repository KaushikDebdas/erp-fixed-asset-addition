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
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.helpers import find_one_text, search_word_of
from utils.logger import action_logger, assertion_logger

# Maximum time to wait for a grid to show its new rows after a Search (milliseconds)
GRID_RELOAD_TIMEOUT = 15000

# Maximum time to wait for a suggestion list or a calendar to open (milliseconds)
POPUP_OPEN_TIMEOUT = 8000

# Maximum time to wait for a menu link to show before reporting that the user has no right to it (milliseconds)
MENU_LINK_TIMEOUT = 10000

# Maximum time to wait for the Accounting Date box in the top right corner (milliseconds)
BUSINESS_DAY_TIMEOUT = 10000

# Maximum time to wait for the loader to show after an action (milliseconds). The loader
# shows a few tens of milliseconds after the click, so the wait starts by waiting for it.
LOADER_APPEAR_TIMEOUT = 1000

# Number of times a search button / calendar icon is used to open its list
OPEN_LIST_ATTEMPTS = 3

# Path of the Fixed Asset module on the ERP site
FIXED_ASSET_PATH = "/nodef/fixedasset"

# Text the ERP puts before the serial of an extended asset in an asset list (CR FAHOV2-643: four spaces)
EXTENDED_SERIAL_INDENT = "\xa0" * 4


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

    def read_business_day(self) -> str:
        """
        Return the text of the Accounting Date box in the top right corner of the
        Fixed Asset module, for example "Accounting Date : 20-09-2026 [DAY CLOSED]".
        Fails with a clear message when the box does not show.
        """
        box = self.page.locator("#sessionBusinessDateReload")
        assert self.is_shown_within(box, "Accounting Date box", BUSINESS_DAY_TIMEOUT), (
            "The Accounting Date box (top right corner) is not shown, so the business day cannot be checked."
        )
        return " ".join(box.inner_text().split())

    def verify_business_day_open(self) -> None:
        """
        Stop with a clear reason when the Accounting Date is marked [DAY CLOSED].
        Call it before steps that register or approve something: on a closed day the
        ERP refuses the approval ("Business day not open for Fixed Asset."), so
        checking first avoids doing all the earlier steps for nothing.
        """
        from utils.login_session import user_of

        day_text = self.read_business_day()
        action_logger.info(f"Business day: {day_text}")
        if "CLOSED" in day_text.upper():
            username = user_of(self.page)[0]
            reason = (
                f"The business day is closed for user {username}: '{day_text}'. "
                f"Open the day for this office, or sign in to an office whose day is open."
            )
            assertion_logger.error(reason)
            raise AssertionError(reason)
        assertion_logger.info(f"Business day is open: {day_text}")

    def click_menu_link(self, link: Locator, link_name: str) -> None:
        """
        Click a menu link of the Fixed Asset module. When the link is not on the
        menu, the signed-in user has no menu right for it: stop with a message that
        names the user and the menu, instead of a plain timeout.
        """
        if not self.is_shown_within(link, f"{link_name} menu link", MENU_LINK_TIMEOUT):
            from utils.login_session import user_of

            username = user_of(self.page)[0]
            reason = (
                f"User {username} has no access to the menu '{link_name}': the link is not on the menu. "
                f"Ask for the menu right, or sign in with a user who has it."
            )
            assertion_logger.error(reason)
            raise AssertionError(reason)
        self.click(link, f"{link_name} menu link")

    def open_fixed_asset_module(self) -> None:
        """
        Open the Fixed Asset module from the ERP home page that shows after
        login. The module lives on the same site as the page we are on, so
        its address is built from the current site address.
        """
        parts = urlsplit(self.page.url)
        module_url = f"{parts.scheme}://{parts.netloc}{FIXED_ASSET_PATH}"
        for attempt in range(OPEN_LIST_ATTEMPTS):
            action_logger.info(f"Open URL: {module_url}")
            response = self.page.goto(module_url)
            self.wait_for_page_load()
            if response is not None and response.status >= 500:
                action_logger.info(f"The server answered {response.status}; opening the module again")
                continue
            if self.sign_in_form_is_shown():
                self.sign_in_again()
                continue
            break
        self.wait_until_visible(
            self.page.get_by_text("Registration", exact=True).first, "Registration menu"
        )

    def sign_in_form_is_shown(self) -> bool:
        """Return True when the ERP sign-in form is on screen, which means the session has ended."""
        username_field = self.page.get_by_role("textbox", name="Username")
        return username_field.is_visible()

    def sign_in_again(self) -> None:
        """Sign in again, after the ERP ended the session, as the user this tab was signed in as."""
        from pages.login_page import LoginPage
        from utils.login_session import user_of

        action_logger.info("The session ended; signing in again")
        username, password, branch = user_of(self.page)
        login_page = LoginPage(self.page)
        login_page.login(username, password)
        login_page.verify_logged_in(username)
        login_page.select_office_if_asked(branch)
        login_page.close_popup_if_present()

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
        self.click_menu_link(link, link_name)
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
        self.click_menu_link(link, link_name)
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
        self.click_menu_link(link, link_name)
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
        self.click_menu_link(link, link_name)
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
        self.click_menu_link(link, link_name)
        self.wait_for_page_load()

    def open_single_challan_submenu(self, link_name: str) -> None:
        """
        Open a link from the Fixed Asset module's "Single Challan" menu (Asset
        Single Out Challan, Asset Single Out Challan Approval List, Asset
        Single In-Challan, Gate Pass Generation, ...). Works like
        `open_registration_submenu`.
        """
        self.open_fixed_asset_module()
        single_challan_menu = self.page.get_by_text("Single Challan", exact=True).first
        self.click(single_challan_menu, "Single Challan menu")
        link = self.page.get_by_role("link", name=link_name, exact=True)
        self.click_menu_link(link, link_name)
        self.wait_for_page_load()

    def open_select2(self, container_css: str, what: str, search_text: str):
        """
        Open a select2 box and type `search_text` in its search field: click the box `container_css`
        until its drop-down shows the search field and the text is typed, at most
        OPEN_LIST_ATTEMPTS times. Returns the search field. Stops with a message when the
        drop-down never stays open. `what` names the box in the log and the message.
        """
        search_field = self.page.locator(".select2-drop-active:visible input.select2-input")
        for attempt in range(OPEN_LIST_ATTEMPTS):
            self.click(self.page.locator(f"{container_css} a.select2-choice"), f"{what} box")
            if not self.is_shown_within(search_field, "drop-down search field", POPUP_OPEN_TIMEOUT):
                continue
            try:
                action_logger.info("Type into: drop-down search field")
                search_field.fill(search_text, timeout=POPUP_OPEN_TIMEOUT)
                return search_field
            except PlaywrightTimeoutError:
                action_logger.info(f"The drop-down of {what} closed before the text was typed")
        raise AssertionError(f"The drop-down of {what} did not stay open after {OPEN_LIST_ATTEMPTS} clicks.")

    def choose_office_from_select2(self, container_css: str, text: str, what: str) -> None:
        """
        Choose a branch in a select2 box. `text` can be written in any style that identifies
        one branch (spaces, hyphens and leading zeros are ignored), e.g. '[BO-0233] Chagalnaiya'.
        Stops with a message listing the matching entries when none or several match.
        `what` names the box in the log and in that message, e.g. "Receiving Branch".
        """
        action_logger.info(f"Choose {what}: {text}")
        for attempt in range(OPEN_LIST_ATTEMPTS):
            self.open_select2(container_css, what, search_word_of(text))
            labels = self.page.locator(".select2-drop-active:visible .select2-result-label")
            if not self.is_shown_within(labels.first, f"{what} list"):
                continue
            chosen = find_one_text([name.strip() for name in labels.all_inner_texts()], text, what)
            try:
                labels.filter(has_text=chosen).first.click(timeout=POPUP_OPEN_TIMEOUT)
                action_logger.info(f"Click: {what} {chosen}")
                return
            except PlaywrightTimeoutError:
                action_logger.info(f"{what} {chosen} could not be clicked; opening the drop-down again")
        raise AssertionError(f"{what} '{text}' could not be chosen after {OPEN_LIST_ATTEMPTS} attempts.")

    def choose_from_select2(self, container_css: str, search_text: str, option_text: str) -> None:
        """
        Choose a value in a search drop-down box (a select2 box): click the box
        `container_css` (for example "#s2id_fromProject"), type `search_text`
        in its search field, then click the result whose text contains
        `option_text`. The hidden native drop-down behind the box cannot be
        used, so this is the one way these boxes are filled.
        """
        action_logger.info(f"Choose in drop-down {container_css}: {option_text}")
        for attempt in range(OPEN_LIST_ATTEMPTS):
            self.open_select2(container_css, container_css, search_text)
            option = self.page.locator(".select2-drop-active:visible .select2-result-label", has_text=option_text).first
            if not self.is_shown_within(option, f"drop-down result {option_text}"):
                continue
            try:
                option.click(timeout=POPUP_OPEN_TIMEOUT)
                action_logger.info(f"Click: drop-down result {option_text}")
                return
            except PlaywrightTimeoutError:
                action_logger.info(f"Drop-down result {option_text} could not be clicked; opening the drop-down again")
        raise AssertionError(f"'{option_text}' could not be chosen in {container_css} after {OPEN_LIST_ATTEMPTS} attempts.")

    def verify_extended_rows_below_parent(self, table: Locator, parent: str, extended_serials: list, where: str) -> None:
        """
        Confirm an asset list shows `extended_serials` directly below the row of `parent`, in
        that order and no other extended asset of it: each with an empty SL cell, its serial
        indented by four spaces and no button. In these lists the SL is the first shown cell
        and the Asset Serial the second. `where` names the list in the failure text.
        """
        assertion_logger.info(f"Verifying the extended assets of {parent} in the {where}")
        rows = table.locator("tbody tr")
        serials = [rows.nth(i).locator("td:visible").nth(1).inner_text().strip() for i in range(rows.count())]
        assert parent in serials, f"The {where} does not list {parent}. Serials listed: {serials}"
        first = serials.index(parent) + 1
        after_parent = [serial for serial in serials[first:] if serial.startswith(parent + "-")]
        assert after_parent == extended_serials and serials[first:first + len(extended_serials)] == extended_serials, (
            f"The {where} should list {extended_serials} directly below {parent}. Serials listed: {serials}"
        )
        problems = []
        for position in range(first, first + len(extended_serials)):
            row = rows.nth(position)
            cells = row.locator("td:visible").all_inner_texts()
            if cells[0].strip() != "":
                problems.append(f"{serials[position]} has SL '{cells[0].strip()}'")
            if not cells[1].startswith(EXTENDED_SERIAL_INDENT):
                problems.append(f"{serials[position]} is not indented by four spaces: {cells[1]!r}")
            if row.locator("button").count() > 0:
                problems.append(f"{serials[position]} has a button")
        assert not problems, f"The extended assets in the {where} are not shown as expected: {problems}"

    def type_with_keys(self, element: Locator, text: str, element_name: str) -> None:
        """
        Clear a text box and type into it key by key, so the page's own key
        handlers run (the HOFIN forms ignore a value that is only set).
        The text is not logged, only the field name.
        """
        action_logger.info(f"Type into: {element_name}")
        element.click()
        element.press("Control+A")
        element.press("Backspace")
        element.press_sequentially(text)

    def choose_from_ng_select(self, input_box: Locator, search_text: str, option_text: str) -> None:
        """
        Choose a value in a search drop-down box (an ng-select box of HOFIN):
        click `input_box` (the box's text input), type `search_text` when it is
        not empty, then click the option whose text contains `option_text`.
        Example:
            self.choose_from_ng_select(self.vendor_input, "SU0006", "SU000634 -3DEVs")
        """
        action_logger.info(f"Choose in drop-down: {option_text}")
        option = self.page.get_by_role("option", name=option_text).first
        for attempt in range(OPEN_LIST_ATTEMPTS):
            input_box.click()
            if search_text != "":
                input_box.press("Control+A")
                input_box.press("Backspace")
                input_box.press_sequentially(search_text)
            if not self.is_shown_within(option, f"drop-down option {option_text}"):
                continue
            try:
                option.click(timeout=POPUP_OPEN_TIMEOUT)
                action_logger.info(f"Click: drop-down option {option_text}")
                return
            except PlaywrightTimeoutError:
                action_logger.info(f"Drop-down option {option_text} could not be clicked; opening the drop-down again")
        raise AssertionError(f"'{option_text}' could not be chosen in the drop-down after {OPEN_LIST_ATTEMPTS} attempts.")

    def open_asset_disposal_submenu(self, link_name: str) -> None:
        """
        Open a link from the Fixed Asset module's "Asset Disposal" menu (Asset
        Write-off, Asset Write-off List, Asset Write-off Approval List, Asset
        Sale, ...). Works like `open_registration_submenu`.
        """
        self.open_fixed_asset_module()
        disposal_menu = self.page.get_by_text("Asset Disposal", exact=True).first
        self.click(disposal_menu, "Asset Disposal menu")
        link = self.page.get_by_role("link", name=link_name, exact=True)
        self.click_menu_link(link, link_name)
        self.wait_for_page_load()

    def wait_for_table_to_reload(self, table: Locator) -> None:
        """
        Wait until a grid has shown the result of a Search. The line under the
        grid ("Showing 1 to 10 of N entries") is emptied when Search is clicked
        and filled again when the rows arrive. A grid without that line is
        ready when its first row (or the "No data" row) is shown.
        """
        info = table.locator("xpath=ancestor::div[contains(@class,'dataTables_wrapper')][1]//div[contains(@class,'dataTables_info')]")
        if info.count() == 0:
            table.locator("tbody tr").first.wait_for(state="visible")
            return
        self.wait_for_grid_to_reload(info)

    def wait_for_loader_to_finish(self) -> None:
        """
        Wait until the full-screen loading overlay (`.modalLoader`) that shows
        for a moment after a Search is gone. The overlay appears a few tens of
        milliseconds after the click, so this first waits up to LOADER_APPEAR_TIMEOUT
        for it to show, then for it to go. When it never shows, nothing was loading
        and this returns.
        """
        action_logger.info("Wait until: the loader has finished")
        loader = self.page.locator(".modalLoader").first
        try:
            loader.wait_for(state="visible", timeout=LOADER_APPEAR_TIMEOUT)
        except PlaywrightTimeoutError:
            return
        loader.wait_for(state="hidden")

    def scroll_into_view(self, element: Locator, element_name: str) -> None:
        """
        Scroll the page until the element is on screen, so on a small screen
        the person watching the test sees what the test is looking at. The
        scrolling is only for the viewer: when it cannot be done (for example
        the grid reloads at that moment) the test goes on.
        """
        action_logger.info(f"Scroll to: {element_name}")
        try:
            element.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            action_logger.info(f"Could not scroll to {element_name}; the next action scrolls to it itself")

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
        Search never reads the previous result. The loader that shows after Search
        must be gone first: until then the grid still holds the previous result,
        which can already contain a row with `text`. It then scrolls that row into view.
        """
        self.wait_for_loader_to_finish()
        row = table.locator("tbody tr", has_text=text)
        no_data = table.locator("tbody tr", has_text="No data available in table")
        row.or_(no_data).first.wait_for(state="visible")
        # Show the result on a small screen, where the grid is below the filters
        self.scroll_into_view(row.or_(no_data).first, "search result")

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

    def get_toast_text_or_empty(self, timeout: int = 8000) -> str:
        """
        Return the text of the toast on screen, or an empty text when no toast
        was seen within `timeout` ms. Use it for a success message that fades
        quickly, together with `verify_toast_if_shown`.
        """
        try:
            return self.get_toast_text(timeout=timeout)
        except Exception:
            action_logger.info("No toast message was seen on screen")
            return ""

    def verify_toast_text(self, actual: str, expected, action: str) -> None:
        """
        Confirm the toast read after `action` is exactly `expected`; the failure
        names both texts. `expected` is the text of a one-line toast, or a list
        with one entry per line for a toast with several lines (the screen's
        lines are compared with it, empty lines ignored).
        """
        assertion_logger.info(f"Verifying the message after: {action}")
        found = actual
        if isinstance(expected, list):
            found = [line.strip() for line in actual.split(chr(10)) if line.strip() != ""]
        assert found == expected, (
            f"After {action} the expected message was {expected!r} but the message on screen was {found!r}."
        )

    def verify_toast_contains(self, actual: str, expected_text: str, action: str) -> None:
        """Confirm the toast read after `action` contains `expected_text`; the failure names both texts."""
        assertion_logger.info(f"Verifying the message after: {action}")
        assert expected_text in actual, (
            f"After {action} the expected message was '{expected_text}' but the message on screen was '{actual}'."
        )

    def verify_toast_if_shown(self, actual: str, expected_text: str, action: str) -> None:
        """
        Confirm a toast read after `action` contains `expected_text` (ignoring
        capital letters). An empty `actual` means no toast was seen and is
        accepted, because the caller then checks the result on the screen.
        """
        assertion_logger.info(f"Verifying the message after: {action}")
        if actual == "":
            return
        assert expected_text.lower() in actual.lower(), (
            f"After {action} the expected message was '{expected_text}' but the message on screen was '{actual}'."
        )

    def read_row_values(self, table: Locator, row_text: str) -> dict:
        """
        Return the visible cells of the first row of `table` that contains
        `row_text`, as {column heading: cell text}. Columns with no heading
        (for example a checkbox column) are left out.
        """
        headers = [h.strip() for h in table.locator("thead th:visible").all_inner_texts()]
        row = table.locator("tbody tr", has_text=row_text).first
        cells = [c.strip() for c in row.locator("td:visible").all_inner_texts()]
        values = {}
        for index, header in enumerate(headers):
            if header and index < len(cells):
                values[header] = cells[index]
        return values

    def verify_row_values(self, table: Locator, row_text: str, expected: dict) -> None:
        """Confirm the row containing `row_text` shows every value in `expected` ({column heading: text}); names each difference."""
        found = self.read_row_values(table, row_text)
        assertion_logger.info(f"Verifying the grid row of {row_text}")
        problems = []
        for heading, wanted in expected.items():
            actual = found.get(heading, "<column not found>")
            if actual != wanted:
                problems.append(f"{heading}: expected '{wanted}' but found '{actual}'")
        assert not problems, f"The row of {row_text} is not as expected: {problems}"

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
