"""
AssetSerialSplitApprovalListPage: Fixed Asset > Asset Profile > Asset
Serial Split Approval List screen and its "Asset Split View" popup.

Used to approve or reject split requests. The Approve and Reject buttons are
only checked for presence here: using them would change real data. See
`automation/element_catalog/asset_serial_split_approval_list.md`.
"""
from pages.base_page import BasePage
from utils.logger import action_logger


class AssetSerialSplitApprovalListPage(BasePage):
    """Page object for the Asset Serial Split Approval List screen and its view popup."""

    def __init__(self, page):
        super().__init__(page)
        # Filters
        self.asset_serial_filter = page.locator("#assetSerial")
        # Buttons
        self.search_button = page.get_by_role("button", name="Search")
        self.approve_button = page.locator("#btnApprove")
        self.reject_button = page.locator("#btnReject")
        # Results grid
        self.results_table = page.locator("#assetSplitList")
        # "Asset Split View" popup
        self.popup = page.locator(".modal.in, .modal.show")
        self.popup_close_button = self.popup.get_by_role("button", name="Close").first
        self.popup_split_grid = self.popup.locator("#assetSerialSplitList")

    def navigate_here(self) -> None:
        """Open the Asset Serial Split Approval List screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Split Approval List")
        self.wait_until_visible(self.search_button, "Search button")

    def search(self) -> None:
        """Run the search with the default filters and wait for the grid."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def has_data_rows(self) -> bool:
        """Return True if the grid shows real rows (not the empty message)."""
        no_data = self.results_table.locator("tbody tr", has_text="No data available in table")
        return no_data.count() == 0 and self.results_table.locator("tbody tr").count() > 0

    def get_first_row_split_number(self) -> str:
        """Return the Asset Split No. of the first row."""
        return self.results_table.locator("tbody tr a").first.inner_text().strip()

    def get_first_row_asset_serial(self) -> str:
        """Return the Asset Serial No. of the first row (the 7th cell, index 6)."""
        first_row = self.results_table.locator("tbody tr").first
        return first_row.locator("td").nth(6).inner_text().strip()

    def open_first_row_popup(self) -> None:
        """Click the Asset Split No. link of the first row to open the Asset Split View popup."""
        link = self.results_table.locator("tbody tr a").first
        self.click(link, "Asset Split No. link of the first row")
        self.wait_until_visible(self.popup.locator("#splitInto"), "Split Into field")

    def get_popup_value(self, field_id: str) -> str:
        """Return the value of a read-only field in the popup, e.g. 'assetSerial'."""
        action_logger.info(f"Read value of popup field: {field_id}")
        return self.popup.locator(f"#{field_id}").input_value().strip()

    def get_popup_title(self) -> str:
        """Return the popup's heading."""
        return self.popup.locator("h4, .modal-title").first.inner_text().strip()

    def get_popup_split_line_count(self) -> int:
        """Return how many split lines the popup's grid shows."""
        return self.popup_split_grid.locator("tbody tr").count()

    def close_popup(self) -> None:
        """Close the Asset Split View popup."""
        self.click(self.popup_close_button, "Close button of Asset Split View popup")
