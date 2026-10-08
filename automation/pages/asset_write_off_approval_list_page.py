"""
AssetWriteOffApprovalListPage: Asset Write-off Approval List (Fixed Asset >
Asset Disposal > Asset Write-off Approval List).

The approver ticks a PENDING write-off and clicks Approve. The user who
created the write-off can approve it, if that user has the approval permission. See
`automation/element_catalog/asset_write_off_approval_list.md`.
"""
from pages.base_page import BasePage
from test_data.toast_messages import WRITE_OFF_APPROVE_TOAST
from utils.logger import action_logger, assertion_logger


class AssetWriteOffApprovalListPage(BasePage):
    """Page object for the Asset Write-off Approval List screen. Asset Sale Approval List inherits it and changes the names below."""

    # Link in the Asset Disposal menu, the results grid, the Status cell position (0-based) and the Approve toast
    MENU_LINK = "Asset Write-off Approval List"
    GRID_ID = "#assetWriteOffScheduleList"
    STATUS_COLUMN_INDEX = 11
    APPROVE_TOAST = WRITE_OFF_APPROVE_TOAST

    def __init__(self, page):
        super().__init__(page)
        # Filters
        self.status_filter = page.locator("#status")
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid (newest write-off first; only PENDING rows have a checkbox)
        self.results_table = page.locator(self.GRID_ID)
        # Approves every ticked row
        self.approve_button = page.locator("#btnApprove")

    def navigate_here(self) -> None:
        """Open this list via the Asset Disposal menu."""
        self.open_asset_disposal_submenu(self.MENU_LINK)
        self.wait_until_visible(self.search_button, "Search button")

    def filter_by_status(self, status: str) -> None:
        """Choose a Status (PENDING, APPROVED, ...), click Search and wait for the grid."""
        action_logger.info(f"Filter: Status -> {status}")
        self.status_filter.select_option(label=status)
        self.click(self.search_button, "Search button")
        self.wait_for_table_to_reload(self.results_table)

    def select_write_off(self, write_off_id: str) -> None:
        """Tick the checkbox of the PENDING write-off with this ID."""
        row = self.results_table.locator("tbody tr", has_text=write_off_id).first
        checkbox = row.locator("input[type=checkbox]")
        self.wait_until_visible(checkbox, f"checkbox of write-off {write_off_id}")
        action_logger.info(f"Tick: write-off {write_off_id}")
        checkbox.check()

    def select_all_pending(self) -> None:
        """Tick the select-all checkbox in the grid heading, which ticks every PENDING row shown."""
        select_all = self.results_table.locator("thead input[type=checkbox]")
        self.wait_until_visible(select_all, "select-all checkbox")
        action_logger.info("Tick: select all pending")
        select_all.check()

    def approve_selected_and_verify(self) -> None:
        """Click Approve and confirm the two success messages (approved, journal voucher submitted)."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button")
        self.verify_toast_text(self.get_toast_text(), self.APPROVE_TOAST, "Approve")

    def verify_status(self, write_off_id: str, expected: str) -> None:
        """Confirm the row of this ID shows the expected Status."""
        assertion_logger.info(f"Verifying the Status of write-off {write_off_id}")
        row = self.results_table.locator("tbody tr", has_text=write_off_id)
        assert row.count() > 0, f"Expected write-off {write_off_id} to be listed but it was not."
        found = row.first.locator("td").nth(self.STATUS_COLUMN_INDEX).inner_text().strip()
        assert found == expected, f"Expected the Status of write-off {write_off_id} to be {expected} but found {found}."
