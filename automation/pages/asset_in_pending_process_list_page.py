"""
AssetInPendingProcessListPage: Fixed Asset > Asset Profile > Asset In
Pending Process List screen.

Shows assets that are in the middle of a process (a challan, an assignment,
a transfer, ...) and the screen each one is pending in. The list can be
exported to Excel. See
`automation/element_catalog/asset_in_pending_process_list.md`.
"""
from pages.base_page import BasePage
from utils.logger import action_logger


class AssetInPendingProcessListPage(BasePage):
    """Page object for the Asset In Pending Process List screen."""

    def __init__(self, page):
        super().__init__(page)
        # Filters
        self.asset_serial_filter = page.locator("#assetSerial")
        self.pending_feature_filter = page.locator("#pendingFeature")
        self.status_filter = page.locator("#assetStatus")
        # Buttons
        self.search_button = page.get_by_role("button", name="Search")
        self.reset_button = page.locator("#resetUpdate")
        self.export_button = page.locator("#exportBtn")
        # Results grid
        self.results_table = page.locator("#pendingAssetTable")

    def navigate_here(self) -> None:
        """Open the Asset In Pending Process List screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset In Pending Process List")
        self.wait_until_visible(self.search_button, "Search button")

    def search_by_serial(self, serial: str) -> None:
        """Filter by Asset Serial and wait for the result (or the empty message)."""
        self.type_text(self.asset_serial_filter, serial, "Asset Serial filter")
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()
        self.wait_for_row_or_no_data(self.results_table, serial)

    def filter_by_status(self, status: str) -> None:
        """Pick a Status (PENDING / APPROVED / DRAFT / SENDBACK) and search."""
        action_logger.info(f"Filter: Status -> {status}")
        self.status_filter.select_option(status)
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_visible_statuses(self) -> list:
        """Return the Status of every result row (the Status column is the 14th, index 13)."""
        rows = self.results_table.locator("tbody tr")
        statuses = []
        for i in range(rows.count()):
            cells = rows.nth(i).locator("td")
            if cells.count() > 13:
                statuses.append(cells.nth(13).inner_text().strip())
        return statuses

    def has_data_rows(self) -> bool:
        """Return True if the grid shows real rows (not the empty message)."""
        no_data = self.results_table.locator("tbody tr", has_text="No data available in table")
        return no_data.count() == 0 and self.results_table.locator("tbody tr").count() > 0

    def export_to_file(self, save_path: str) -> str:
        """
        Click Export, save the downloaded Excel file to `save_path`, and
        return the file name the site gave it.
        """
        with self.page.expect_download() as download_info:
            self.click(self.export_button, "Export button")
        download = download_info.value
        download.save_as(save_path)
        action_logger.info(f"Exported file: {download.suggested_filename}")
        return download.suggested_filename
