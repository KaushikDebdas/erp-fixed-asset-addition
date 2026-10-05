"""
AssetInPendingProcessListPage: Fixed Asset > Asset Profile > Asset In
Pending Process List screen.

Shows assets that are in the middle of a process (a challan, an assignment,
a transfer, ...) and the screen each one is pending in. The list can be
exported to Excel. See
`automation/element_catalog/asset_in_pending_process_list.md`.
"""
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger


# Maximum time to wait for the Excel download to start after Export is clicked (milliseconds)
EXPORT_DOWNLOAD_TIMEOUT = 30000


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
        # The list loads its first rows after the page appears; a search or export
        # started before that is overwritten by the first load
        self.results_table.locator("tbody tr").first.wait_for(state="visible")
        self.wait_for_grid_refresh()

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
        try:
            with self.page.expect_download(timeout=EXPORT_DOWNLOAD_TIMEOUT) as download_info:
                self.click(self.export_button, "Export button")
        except PlaywrightTimeoutError:
            raise AssertionError(
                f"Export did not start a download within {EXPORT_DOWNLOAD_TIMEOUT // 1000} seconds after the Export button was clicked."
            )
        download = download_info.value
        download.save_as(save_path)
        action_logger.info(f"Exported file: {download.suggested_filename}")
        return download.suggested_filename

    def search_serial_and_wait_for_result(self, serial: str) -> None:
        """
        Filter by Asset Serial and wait until the grid shows the answer: a row
        with this serial, or the "No data available in table" message. The
        message can take several seconds to appear.
        """
        self.type_text(self.asset_serial_filter, serial, "Asset Serial filter")
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()
        self.page.wait_for_function(
            "([tableId, serial]) => {"
            " const body = document.querySelector(tableId + ' tbody');"
            " return body !== null && (body.innerText.includes('No data available in table') || body.innerText.includes(serial)); }",
            arg=["#pendingAssetTable", serial],
            timeout=45000,
        )

    def verify_serial_is_not_pending(self, serial: str) -> None:
        """Confirm the asset is in no pending process: its search finds no row. Fails with the row that was found."""
        assertion_logger.info(f"Verifying {serial} is not in the pending list")
        found = self.read_rows_with_serial(serial)
        assert not found, f"Expected {serial} to be in no pending process but found: {found}"

    def read_rows(self) -> list:
        """Return every result row as a dictionary keyed by column heading (an empty list when the grid has no data)."""
        if not self.has_data_rows():
            return []
        headings = [h.strip() for h in self.results_table.locator("thead th:visible").all_inner_texts()]
        rows = []
        for row in self.results_table.locator("tbody tr").all():
            cells = [c.strip() for c in row.locator("td:visible").all_inner_texts()]
            rows.append(dict(zip(headings, cells)))
        return rows

    def read_rows_with_serial(self, serial: str) -> list:
        """Return the result rows whose Asset Serial is this serial."""
        found = []
        for row in self.read_rows():
            if row.get("Asset Serial") == serial:
                found.append(row)
        return found
