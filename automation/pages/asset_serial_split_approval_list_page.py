"""
AssetSerialSplitApprovalListPage: Fixed Asset > Asset Profile > Asset
Serial Split Approval List screen and its "Asset Split View" popup.

Used to approve or reject split requests: tick a row, then click Approve or
Reject. Approving makes the new asset serials. Reject is never clicked by the
tests. See `automation/element_catalog/asset_serial_split_approval_list.md`.
"""
import re

from playwright.sync_api import expect

from pages.asset_split_view_popup import AssetSplitViewPopup
from pages.base_page import GRID_RELOAD_TIMEOUT, BasePage
from utils.logger import action_logger, assertion_logger

# Message shown when Approve or Reject is clicked with no row ticked
NOTHING_TICKED_MESSAGE = "You have to select a split first"

# Text the success message of Approve contains
APPROVED_MESSAGE = "Asset Split approved successfully"

# How a date is shown in the grid, e.g. 20/09/2026
DATE_PATTERN = r"\d{2}/\d{2}/\d{4}"


class AssetSerialSplitApprovalListPage(BasePage):
    """Page object for the Asset Serial Split Approval List screen and its view popup."""

    def __init__(self, page):
        super().__init__(page)
        # Filters (the view popup has its own #assetSerial, so the filter is found by name)
        self.asset_serial_filter = page.locator('input[name="assetSerial"]')
        # Buttons (the popup has its own #btnApprove / #btnReject, so the grid buttons are found by onclick)
        self.search_button = page.get_by_role("button", name="Search")
        self.approve_button = page.locator('button[onclick="submit();"]')
        self.reject_button = page.locator('button[onclick="reject();"]')
        # Results grid
        self.results_table = page.locator("#assetSplitList")
        # "Asset Split View" popup
        self.popup = page.locator(".modal.in, .modal.show")
        self.popup_close_button = self.popup.get_by_role("button", name="Close").first
        self.popup_split_grid = self.popup.locator("#assetSerialSplitList")
        self.view_popup = AssetSplitViewPopup(page)

    def navigate_here(self) -> None:
        """Open the Asset Serial Split Approval List screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Split Approval List")
        self.wait_until_visible(self.search_button, "Search button")

    def search(self) -> None:
        """Run the search with the default filters and wait for the grid."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()

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

    def verify_grid_headers(self, expected: list) -> None:
        """Confirm the grid shows exactly these column headings, in order."""
        assertion_logger.info("Verifying the grid column headings")
        found = self.get_grid_headers()
        assert found == expected, f"Expected the column headings {expected} but found {found}."

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

    # ---- reading a split's row -----------------------------------------------------

    def verify_row_shows(self, serial: str, expected: dict) -> None:
        """Confirm the row of this serial shows every value in `expected` ({column heading: text})."""
        self.verify_row_values(self.results_table, serial, expected)

    def verify_row_is_approved(self, serial: str, approved_by: str) -> None:
        """Confirm the row of this serial is APPROVED, by this person, with an approval date."""
        self.verify_row_values(self.results_table, serial, {"Status": "APPROVED", "Approved By": approved_by})
        date = self.read_row_values(self.results_table, serial)["Approval Date"]
        assert re.fullmatch(DATE_PATTERN, date), (
            f"Expected an Approval Date like 20/09/2026 on the row of {serial} but found '{date}'."
        )

    def wait_for_status(self, serial: str, status: str) -> None:
        """Wait until the row of this serial shows this Status (the grid refreshes after Approve)."""
        row = self.results_table.locator("tbody tr", has_text=serial)
        expect(row).to_contain_text(status, timeout=GRID_RELOAD_TIMEOUT)

    # ---- the Asset Split View popup ----------------------------------------------------

    def open_first_row_popup(self) -> None:
        """Click the Asset Split No. link of the first row to open the Asset Split View popup."""
        link = self.results_table.locator("tbody tr a").first
        self.click(link, "Asset Split No. link of the first row")
        self.wait_until_visible(self.popup.locator("#splitInto"), "Split Into field")

    def open_split_view(self, serial: str) -> None:
        """Click the Asset Split No. of this serial's row and wait for the Asset Split View popup."""
        link = self.results_table.locator("tbody tr", has_text=serial).locator("a").first
        self.click(link, f"Asset Split No. link of {serial}")
        self.view_popup.wait_until_open()

    def verify_popup_shows(self, expected: dict, line_count: int) -> None:
        """Confirm the open popup shows these field values ({field id: text}) and this many split lines."""
        self.view_popup.verify_shows(expected, line_count)

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

    def close_split_view(self) -> None:
        """Close the Asset Split View popup and wait until it is gone."""
        self.view_popup.close()

    # ---- Approve and Reject ------------------------------------------------------------

    def tick_row(self, serial: str) -> None:
        """Tick the checkbox of the row of this serial."""
        checkbox = self.results_table.locator("tbody tr", has_text=serial).locator("input[name=assetSplitApproval]")
        action_logger.info(f"Tick the row of {serial}")
        checkbox.check()

    def verify_nothing_ticked_message(self, button_name: str) -> None:
        """Click Approve or Reject with no row ticked and confirm the message asking to select a split."""
        button = self.approve_button if button_name == "Approve" else self.reject_button
        self.wait_for_toast_to_clear()
        self.click(button, f"{button_name} button")
        toast = self.get_toast_text()
        self.verify_toast_text(toast, NOTHING_TICKED_MESSAGE, f"{button_name} clicked with nothing ticked")

    def click_approve_and_get_toast(self) -> str:
        """Click Approve for the ticked rows and return the message shown, or an empty text if none was seen."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button")
        return self.get_toast_text_or_empty()

    def verify_approve_message(self, toast: str) -> None:
        """Confirm the Approve message (when one was seen) says the split was approved."""
        self.verify_toast_if_shown(toast, APPROVED_MESSAGE, "Approve of the split")

    def approve_split(self, serial: str) -> None:
        """
        Approve the split of one serial: search it, tick its row, click
        Approve, confirm the message and wait until the row shows APPROVED.
        """
        self.search_by_serial(serial)
        self.tick_row(serial)
        toast = self.click_approve_and_get_toast()
        self.verify_approve_message(toast)
        self.wait_for_status(serial, "APPROVED")
