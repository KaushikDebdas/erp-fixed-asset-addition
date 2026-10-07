"""
TransactionGridPage: what the Transaction List and the Transaction Approval
List (Fixed Asset > Asset Transaction) have in common.

Both screens filter Assign / Un Assign / Internal Movement transactions by
type and status, show them in one grid, and open a read-only "Asset
Transaction Details" popup from each row's Details link. See
`automation/element_catalog/transaction_list.md` and
`transaction_approval_list.md`.
"""
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# How many rows are looked at when searching for the row that holds a serial
MAX_ROWS_TO_CHECK = 10

# Number of times a row's Details popup is opened when its asset list does not load
DETAILS_OPEN_ATTEMPTS = 2


class TransactionGridPage(BasePage):
    """Shared page object for the two transaction grids."""

    def __init__(self, page):
        super().__init__(page)
        # Filters
        # The popup has a field with the same id, so the filters are matched as <select>
        self.type_filter = page.locator("select#assetTransactionType")
        self.status_filter = page.locator("select#assetTransactionStatus")
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid
        self.results_table = page.locator("#assetTransactionList")
        # "Asset Transaction Details" popup
        self.popup = page.locator(".modal.in")
        self.popup_close_button = self.popup.get_by_role("button", name="Close").first
        self.popup_assets_table = self.popup.locator("#transactionDetailsList")

    # ---- filters and grid -------------------------------------------------

    def search(self, transaction_type: str = None, status: str = None) -> None:
        """Pick the type and/or status (when given), click Search and wait for the grid."""
        if transaction_type:
            action_logger.info(f"Filter: Transaction Type -> {transaction_type}")
            self.type_filter.select_option(transaction_type)
        if status:
            action_logger.info(f"Filter: Transaction Status -> {status}")
            self.status_filter.select_option(status)
        self.click(self.search_button, "Search button")
        self.wait_for_table_to_reload(self.results_table)

    def get_type_options(self) -> list:
        """Return every value of the Transaction Type filter, placeholder first."""
        return self.type_filter.evaluate("s => Array.from(s.options).map(o => o.text.trim())")

    def get_status_options(self) -> list:
        """Return every value of the Transaction Status filter, placeholder first."""
        return self.status_filter.evaluate("s => Array.from(s.options).map(o => o.text.trim())")

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def has_data_rows(self) -> bool:
        """Return True if the grid shows real rows (not the empty message)."""
        rows = self.results_table.locator("tbody tr")
        no_data = rows.filter(has_text="No data available in table")
        return rows.count() > 0 and no_data.count() == 0

    def get_row_values(self, row_index: int) -> dict:
        """Return a row's Transaction Type, Transaction Status and Created By."""
        cells = self.results_table.locator("tbody tr").nth(row_index).locator("td").all_inner_texts()
        cells = [c.strip() for c in cells]
        # cells: hidden id, SL, Details, [Edit,] Type, Date, Branch, Created By, Approved By, Approval Date, Status
        return {"type": cells[-7], "created_by": cells[-4], "status": cells[-1]}

    def get_all_row_types(self) -> list:
        """Return the Transaction Type of every row shown."""
        rows = self.results_table.locator("tbody tr")
        return [self.get_row_values(i)["type"] for i in range(rows.count())]

    def get_all_row_statuses(self) -> list:
        """Return the Transaction Status of every row shown."""
        rows = self.results_table.locator("tbody tr")
        return [self.get_row_values(i)["status"] for i in range(rows.count())]

    # ---- the Details popup ----------------------------------------------------

    def open_details_of_row(self, row_index: int) -> None:
        """Click Details on a row and wait until the popup has loaded its asset list."""
        row = self.results_table.locator("tbody tr").nth(row_index)
        self.click(row.get_by_role("link", name="Details"), f"Details link of row {row_index + 1}")
        real_asset_row = self.popup_assets_table.locator("tbody tr").filter(has_not_text="No data available")
        real_asset_row.first.wait_for(state="visible", timeout=30000)

    def open_details_when_loaded(self, row_index: int) -> bool:
        """
        Open a row's Details popup. When its asset list does not load in time,
        close the popup and try again. Returns True when the list loaded and
        False when it never did (no popup is left open then).
        """
        for attempt in range(DETAILS_OPEN_ATTEMPTS):
            try:
                self.open_details_of_row(row_index)
                return True
            except PlaywrightTimeoutError:
                action_logger.info(f"Asset list of row {row_index + 1} did not load (attempt {attempt + 1})")
                self.close_popup()
        return False

    def get_popup_value(self, field_id: str) -> str:
        """Return the value of a read-only field in the popup, e.g. 'assetTransactionType'."""
        action_logger.info(f"Read value of popup field: {field_id}")
        return self.popup.locator(f"#{field_id}").input_value().strip()

    def get_popup_asset_serials(self) -> list:
        """Return the Asset Serial of every asset listed in the popup (second cell of each row)."""
        rows = self.popup_assets_table.locator("tbody tr")
        return [rows.nth(i).locator("td:visible").nth(1).inner_text().strip() for i in range(rows.count())]

    def get_popup_asset_headers(self) -> list:
        """Return the column headings of the popup's asset list."""
        headers = self.popup_assets_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def close_popup(self) -> None:
        """Close the Details popup."""
        self.click(self.popup_close_button, "Close button of Details popup")
        self.popup.wait_for(state="hidden")

    def find_row_with_serial(self, serial: str, transaction_type: str, status: str) -> int:
        """
        Search by type and status, then open Details on each row (newest
        first) until the popup lists `serial`. Leaves that popup open and
        returns the row's index. Returns -1 (no popup left open) when none of
        the first rows lists the serial.
        """
        self.search(transaction_type, status)
        if not self.has_data_rows():
            return -1
        row_count = min(self.results_table.locator("tbody tr").count(), MAX_ROWS_TO_CHECK)
        for row_index in range(row_count):
            if not self.open_details_when_loaded(row_index):
                continue
            if serial in self.get_popup_asset_serials():
                return row_index
            self.close_popup()
        return -1

    def open_details_of_row_with_serial(self, serial: str, transaction_type: str, status: str) -> int:
        """
        Open the Details popup of the newest transaction of this type and
        status that lists `serial`, and return its row index. This guarantees
        the test acts on its own transaction and never on one made by someone
        else. Fails with a clear message when there is none.
        """
        row_index = self.find_row_with_serial(serial, transaction_type, status)
        assert row_index >= 0, (
            f"None of the first {MAX_ROWS_TO_CHECK} {transaction_type} transactions with status "
            f"{status} lists asset {serial}."
        )
        return row_index

    # ---- checks ---------------------------------------------------------------

    def verify_grid_headers(self, expected: list) -> None:
        """Confirm the grid's column headings are exactly `expected`."""
        assertion_logger.info("Verifying the grid column headings")
        found = self.get_grid_headers()
        assert found == expected, f"Expected the column headings {expected} but found {found}."

    def verify_filter_options(self, expected_types: list, expected_statuses: list) -> None:
        """Confirm the Transaction Type and Transaction Status filters offer exactly these values."""
        assertion_logger.info("Verifying the filter values")
        found_types = self.get_type_options()
        assert found_types == expected_types, f"Expected the Type filter {expected_types} but found {found_types}."
        found_statuses = self.get_status_options()
        assert found_statuses == expected_statuses, (
            f"Expected the Status filter {expected_statuses} but found {found_statuses}."
        )

    def verify_all_rows_are_type(self, transaction_type: str) -> None:
        """Confirm every row shown is of this Transaction Type."""
        assertion_logger.info(f"Verifying every row is {transaction_type}")
        found = set(self.get_all_row_types())
        assert found == {transaction_type}, f"Expected only {transaction_type} rows but found the types {found}."

    def verify_all_rows_are_status(self, status: str) -> None:
        """Confirm every row shown has this Transaction Status."""
        assertion_logger.info(f"Verifying every row is {status}")
        found = set(self.get_all_row_statuses())
        assert found == {status}, f"Expected only {status} rows but found the statuses {found}."

    def verify_popup_value(self, field_id: str, expected: str) -> None:
        """Confirm a read-only field of the open Details popup holds `expected`."""
        found = self.get_popup_value(field_id)
        assert found == expected, f"Details popup field '{field_id}': expected '{expected}' but found '{found}'."

    def verify_popup_asset_headers(self, expected: list) -> None:
        """Confirm the popup's asset list has exactly these column headings."""
        found = self.get_popup_asset_headers()
        assert found == expected, f"Expected the popup asset columns {expected} but found {found}."

    def open_transaction_of_asset(self, serial: str, transaction_type: str, status: str) -> int:
        """
        Find the newest transaction of this type and status that lists the
        asset, confirm its grid row and its Details popup show that type and
        status, and leave the popup open. Returns the row's index.
        """
        assertion_logger.info(f"Verifying a {status} {transaction_type} transaction lists {serial}")
        row_index = self.open_details_of_row_with_serial(serial, transaction_type, status)
        row = self.get_row_values(row_index)
        assert (row["type"], row["status"]) == (transaction_type, status), (
            f"Expected the row to be {transaction_type} / {status} but it is {row['type']} / {row['status']}."
        )
        self.verify_popup_value("assetTransactionType", transaction_type)
        self.verify_popup_value("oldTransactionStatus", status)
        return row_index
