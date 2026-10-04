"""
AssetSerialSplitListPage: Fixed Asset > Asset Profile > Asset Serial Split
List screen.

Lists the splits a user has made, with their approval status. See
`automation/element_catalog/asset_serial_split_list.md`.
"""
from pages.base_page import BasePage


class AssetSerialSplitListPage(BasePage):
    """Page object for the Asset Serial Split List screen."""

    def __init__(self, page):
        super().__init__(page)
        # Filters
        self.asset_serial_filter = page.locator("#assetSerial")
        self.created_by_filter = page.locator("#createdBy")
        self.approved_by_filter = page.locator("#approvedBy")
        # Buttons
        self.search_button = page.get_by_role("button", name="Search")
        self.reset_button = page.locator("#resetUpdate")
        # Results grid
        self.results_table = page.locator("#assetSplitList")

    def navigate_here(self) -> None:
        """Open the Asset Serial Split List screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Split List")
        self.wait_until_visible(self.search_button, "Search button")

    def search_by_serial(self, serial: str) -> None:
        """Filter by Asset Serial and wait for the result (or the empty message)."""
        self.type_text(self.asset_serial_filter, serial, "Asset Serial filter")
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()
        self.wait_for_row_or_no_data(self.results_table, serial)

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_grid_text(self) -> str:
        """Return the visible text of the results grid body (rows or the empty message)."""
        return self.results_table.locator("tbody").inner_text()
