"""
AssetExpenseApprovalPage: Fixed Asset > Asset Expenditure > Asset Expense
Approval screen.

Lists the submitted expenses. Clicking an Expense ID opens a read-only popup
with the expense and three decision buttons (Approve, Reject, Sendback). Only
Approve is used by the tests. A row is always found by the stored Expense ID,
so a test never acts on somebody else's expense. See
`automation/element_catalog/asset_expense_approval.md`.
"""
import re

from pages.base_page import BasePage
from utils.logger import action_logger


class AssetExpenseApprovalPage(BasePage):
    """Page object for the Asset Expense Approval list and its popup."""

    def __init__(self, page):
        super().__init__(page)
        # Filters and grid
        self.status_filter = page.locator("select#status")
        self.search_button = page.get_by_role("button", name="Search")
        self.results_table = page.locator("#editExpenseTable")
        # The expense popup
        self.popup = page.locator(".modal.in")
        self.popup_close_button = self.popup.get_by_role("button", name="Close").first
        self.approve_button = self.popup.locator("#approveBtn")
        self.reject_button = self.popup.locator("#rejectBtn")
        self.sendback_button = self.popup.locator("#sendbackBtn")
        self.asset_grid = self.popup.locator("#assetDetailsTable")

    def navigate_here(self) -> None:
        """Open the Asset Expense Approval list via the Asset Expenditure menu."""
        self.open_asset_expenditure_submenu("Asset Expense Approval")
        self.wait_until_visible(self.search_button, "Search button")

    def search(self, status: str = None) -> None:
        """Pick a Status (when given), click Search and wait for the grid."""
        if status:
            action_logger.info(f"Filter: Status -> {status}")
            self.status_filter.select_option(status)
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()

    def get_status_options(self) -> list:
        """Return every value of the Status filter, placeholder first."""
        return self.status_filter.evaluate("s => Array.from(s.options).map(o => o.text.trim())")

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def has_data_rows(self) -> bool:
        """Return True if the grid shows real rows (not the empty message)."""
        rows = self.results_table.locator("tbody tr")
        return rows.count() > 0 and rows.filter(has_text="No data available in table").count() == 0

    def find_expense(self, expense_id: str, status: str) -> None:
        """Search by Status and wait until the row of this Expense ID is shown."""
        self.search(status)
        self.wait_for_row_or_no_data(self.results_table, expense_id)
        assert self.results_table.locator("tbody tr", has_text=expense_id).count() > 0, (
            f"Expense {expense_id} was not found with status {status} in the Asset Expense Approval list."
        )

    def get_row_status(self, expense_id: str) -> str:
        """Return the Status shown in the row of this Expense ID."""
        row = self.results_table.locator("tbody tr", has_text=expense_id).first
        status_cell = row.locator("td", has_text=re.compile(r"^(PENDING|APPROVED|REJECTED|SENDBACK)$")).first
        return status_cell.inner_text().strip()

    def get_first_row_expense_id(self) -> str:
        """Return the Expense ID of the first row (the 4th cell holds the link)."""
        return self.results_table.locator("tbody tr").first.locator("td").nth(3).inner_text().strip()

    def open_expense(self, expense_id: str) -> None:
        """Click the Expense ID of a row to open its popup."""
        row = self.results_table.locator("tbody tr", has_text=expense_id).first
        self.click(row.get_by_role("link", name=expense_id), f"Expense ID {expense_id} link")
        self.wait_until_visible(self.popup.locator("#expenseRef"), "Expense Ref. field")
        self.page.wait_for_function(
            "document.querySelector('#expenseRef') && document.querySelector('#expenseRef').value !== ''"
        )
        # The drop-downs fill in a moment after the rest of the popup
        self.page.wait_for_function(
            "document.querySelector('.modal.in #debitAccount') && document.querySelector('.modal.in #debitAccount').selectedIndex > 0"
            " && document.querySelector('.modal.in #creditAccount') && document.querySelector('.modal.in #creditAccount').selectedIndex > 0"
        )

    def get_popup_value(self, field_id: str) -> str:
        """Return the value of a read-only field in the popup, e.g. 'expenseRef'."""
        action_logger.info(f"Read value of popup field: {field_id}")
        return self.popup.locator(f"#{field_id}").input_value().strip()

    def get_popup_selected_text(self, select_id: str) -> str:
        """Return the visible text of the option chosen in a drop-down of the popup."""
        return self.popup.locator(f"select#{select_id}").evaluate(
            "s => (s.options[s.selectedIndex] || {}).text || ''"
        ).strip()

    def get_popup_asset_serials(self) -> list:
        """Return the Asset Serial of every asset in the popup's grid (second visible cell)."""
        rows = self.asset_grid.locator("tbody tr").filter(has_not_text="No data available")
        return [rows.nth(i).locator("td:visible").nth(1).inner_text().strip() for i in range(rows.count())]

    def is_popup_field_read_only(self, field_id: str) -> bool:
        """Return True if the popup field cannot be typed in."""
        return not self.popup.locator(f"#{field_id}").is_editable()

    def are_decision_buttons_visible(self) -> bool:
        """Return True if Approve, Reject and Sendback are all shown in the popup."""
        return (
            self.approve_button.is_visible()
            and self.reject_button.is_visible()
            and self.sendback_button.is_visible()
        )

    def close_popup(self) -> None:
        """Close the popup without deciding."""
        self.click(self.popup_close_button, "Close button of the expense popup")
        self.popup.wait_for(state="hidden")

    def approve_and_get_toast(self) -> str:
        """Click Approve in the popup, return the message shown, and wait for the popup to close."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button")
        toast_text = self.get_toast_text()
        self.popup.wait_for(state="hidden")
        self.wait_for_grid_refresh()
        return toast_text
