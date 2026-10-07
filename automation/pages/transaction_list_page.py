"""
TransactionListPage: Fixed Asset > Asset Transaction > Transaction List.

Shows every Assign, Un Assign and Internal Movement transaction of the
user. A Draft row also has an Edit link, which reopens the original form with
its saved values so it can be submitted. See
`automation/element_catalog/transaction_list.md`.
"""
from pages.transaction_grid_page import TransactionGridPage
from utils.logger import assertion_logger


class TransactionListPage(TransactionGridPage):
    """Page object for the Transaction List screen."""

    def navigate_here(self) -> None:
        """Open the Transaction List via the Asset Transaction menu."""
        self.open_asset_transaction_submenu("Transaction List")
        self.wait_until_visible(self.search_button, "Search button")

    def get_created_by_filter_value(self) -> str:
        """Return what the Created By filter holds (it starts filled with the logged-in user)."""
        return self.page.locator("#createdBy").input_value().strip()

    def click_edit_of_row(self, row_index: int) -> None:
        """
        Click Edit on a row. The original Assign / Un Assign / Internal
        Movement form opens with the saved employee already filled in.
        """
        row = self.results_table.locator("tbody tr").nth(row_index)
        self.click(row.get_by_role("link", name="Edit"), f"Edit link of row {row_index + 1}")
        self.page.wait_for_function("document.querySelector('#newEmployeeName') && document.querySelector('#newEmployeeName').value !== ''")

    def has_edit_link(self, row_index: int) -> bool:
        """Return True if the row has an Edit link (only Draft rows do)."""
        row = self.results_table.locator("tbody tr").nth(row_index)
        return row.get_by_role("link", name="Edit").count() > 0

    def verify_row_has_no_edit_link(self, row_index: int) -> None:
        """Confirm the row has no Edit link (an approved transaction cannot be edited)."""
        assertion_logger.info(f"Verifying row {row_index + 1} has no Edit link")
        assert not self.has_edit_link(row_index), f"Expected row {row_index + 1} to have no Edit link but it has one."

    def verify_created_by_filter_contains(self, username: str) -> None:
        """Confirm the Created By filter starts filled with the logged-in user."""
        found = self.get_created_by_filter_value()
        assert username in found, f"Expected the Created By filter to hold '{username}' but it holds '{found}'."
