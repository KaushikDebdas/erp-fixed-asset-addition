"""
TransactionGridPage: what the Transaction List and the Transaction Approval
List (Fixed Asset > Asset Transaction) have in common.

Both screens filter Assign / Un Assign / Internal Movement transactions by
type and status, show them in one grid, and open a read-only "Asset
Transaction Details" popup from each row's Details link. See
`automation/element_catalog/transaction_list.md` and
`transaction_approval_list.md`.
"""
from pages.base_page import BasePage
from utils.logger import action_logger

# How many rows are looked at when searching for the row that holds a serial
MAX_ROWS_TO_CHECK = 10


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
        self.wait_for_grid_refresh()

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

    def open_details_of_row_with_serial(self, serial: str, transaction_type: str, status: str) -> int:
        """
        Search by type and status, then open Details on each row (newest
        first) until the popup lists `serial`. Leaves that popup open and
        returns the row's index. This guarantees the test acts on its own
        transaction and never on one made by someone else.
        """
        self.search(transaction_type, status)
        row_count = min(self.results_table.locator("tbody tr").count(), MAX_ROWS_TO_CHECK)
        assert self.has_data_rows(), f"No {transaction_type} transaction with status {status} was found."
        for row_index in range(row_count):
            self.open_details_of_row(row_index)
            if serial in self.get_popup_asset_serials():
                return row_index
            self.close_popup()
        raise AssertionError(
            f"None of the first {row_count} {transaction_type} transactions with status "
            f"{status} lists asset {serial}."
        )
