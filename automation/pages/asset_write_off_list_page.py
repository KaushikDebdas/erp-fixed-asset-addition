"""
AssetWriteOffListPage: Asset Write-off List (Fixed Asset > Asset Disposal >
Asset Write-off List).

Lists every write-off with its Status. A write-off saved as DRAFT has an Edit
link that opens the Asset Write-off form (`AssetWriteOffPage`) with the asset
already in the grid, where it can be submitted. See
`automation/element_catalog/asset_write_off_list.md`.
"""
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Position of the ID cell in a result row (0-based)
WRITE_OFF_ID_COLUMN_INDEX = 1


class AssetWriteOffListPage(BasePage):
    """Page object for the Asset Write-off List screen. Asset Sale List inherits it and changes the names below."""

    # Link in the Asset Disposal menu, the results grid, and the position of the Status cell (0-based)
    MENU_LINK = "Asset Write-off List"
    GRID_ID = "#assetWriteOffScheduleList"
    STATUS_COLUMN_INDEX = 13

    def __init__(self, page):
        super().__init__(page)
        # Filters
        self.status_filter = page.locator("#status")
        # Runs the filter
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid (newest write-off first)
        self.results_table = page.locator(self.GRID_ID)

    def navigate_here(self) -> None:
        """Open this list via the Asset Disposal menu."""
        self.open_asset_disposal_submenu(self.MENU_LINK)
        self.wait_until_visible(self.search_button, "Search button")

    def filter_by_status(self, status: str) -> None:
        """Choose a Status (PENDING, APPROVED, REJECTED, DRAFT, SENDBACK), click Search and wait for the grid."""
        action_logger.info(f"Filter: Status -> {status}")
        self.status_filter.select_option(label=status)
        self.click(self.search_button, "Search button")
        self.wait_for_table_to_reload(self.results_table)

    def get_newest_write_off_id(self) -> str:
        """Return the ID (Write Off ID or Disposal Sale ID) of the first (newest) row of the grid."""
        first_row = self.results_table.locator("tbody tr").first
        return first_row.locator("td").nth(WRITE_OFF_ID_COLUMN_INDEX).inner_text().strip()

    def open_write_off_for_edit(self, write_off_id: str) -> None:
        """Click Edit on the row of this ID; the Asset Write-off form opens with its asset in the grid."""
        row = self.results_table.locator("tbody tr", has_text=write_off_id)
        edit_link = row.get_by_role("link", name="Edit", exact=True)
        self.click(edit_link, f"Edit link of write-off {write_off_id}")
        self.wait_for_page_load()

    def get_status(self, write_off_id: str) -> str:
        """Return the Status shown in the row of this ID."""
        row = self.results_table.locator("tbody tr", has_text=write_off_id)
        return row.first.locator("td").nth(self.STATUS_COLUMN_INDEX).inner_text().strip()

    def verify_status(self, write_off_id: str, expected: str) -> None:
        """Confirm the row of this ID shows the expected Status (the screen must already list it)."""
        assertion_logger.info(f"Verifying the Status of write-off {write_off_id}")
        assert self.results_table.locator("tbody tr", has_text=write_off_id).count() > 0, (
            f"Expected write-off {write_off_id} to be listed but it was not."
        )
        found = self.get_status(write_off_id)
        assert found == expected, f"Expected the Status of write-off {write_off_id} to be {expected} but found {found}."
