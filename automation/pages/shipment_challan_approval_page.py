"""
ShipmentChallanApprovalPage: Fixed Asset > Asset Transfer > Asset Shipment
Challan Approval List screen.

Lists the transfer challans of a shipment. A PENDING challan is opened from its
Out Challan No link, reviewed in a popup (details, Show Serial) and then
approved. Used by the Asset Shipment end-to-end flow
(projects/fixedasset/e2e-flows/asset-transfer-shipment.md, steps 19 to 21).
Locators come from automation/element_catalog/asset_shipment_challan_approval_list.md.
"""
from playwright.sync_api import expect

from pages.asset_shipment_page import find_column_index, read_headings
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Name of the menu link under Fixed Asset > Asset Transfer
MENU_LINK_NAME = "Asset Shipment Challan Approval List"

# Read-only fields of the challan popup: (name shown in results, element id)
POPUP_FIELDS = [
    ("In Challan No", "#inChallanNoDetails"),
    ("In Challan Date", "#inChallanDateDetails"),
    ("Out Challan No", "#outChallanNoDetails"),
    ("Out Challan Date", "#outChallanDateDetails"),
    ("From Project", "#fromProjectDetails"),
    ("To Project", "#toProjectDetails"),
    ("Status", "#challanStatusDetails"),
    ("From Branch", "#fromBranchDetails"),
    ("To Branch", "#toBranchDetails"),
    ("Created By", "#challanCreatedByDetails"),
    ("Approval Date", "#challanApprovalDateDetails"),
    ("Approved By", "#challanApprovedByDetails"),
]

# Maximum time to wait for a popup or the loading overlay (milliseconds)
POPUP_TIMEOUT = 15000


class ShipmentChallanApprovalPage(BasePage):
    """Page object for the Asset Shipment Challan Approval List screen."""

    def __init__(self, page):
        super().__init__(page)
        # Out Challan No filter (free text)
        self.out_challan_filter = page.locator("#outChallanNo")
        # Approval Status filter: PENDING, APPROVED, REJECTED, ACKNOWLEDGED, SENDBACK
        self.status_filter = page.locator("#challanStatus")
        # Runs the filter
        self.search_button = page.get_by_role("button", name=" Search")
        # Clears the filter boxes
        self.reset_button = page.locator("#resetUpdate")
        # Results grid and the line under it, e.g. "Showing 1 to 10 of 102 entries"
        self.grid = page.locator("#challanListTable")
        self.entries_info = page.locator("#challanListTable_info")
        # Challan popup opened from an Out Challan No link
        self.popup = page.locator("#inChallanDetailsModal")
        # Popup action buttons
        self.approve_button = page.locator("#approveChallan")
        self.reject_button = page.locator("#rejectChallan")
        self.sendback_button = page.locator("#sendBackChallan")
        # Comment box in the popup
        self.comment_box = page.locator("#challanCommentNew")
        # Show Serial link in the popup's item row
        self.show_serial_link = self.popup.get_by_role("link", name="Show Serial")
        # Show Asset Serial popup, its table and the loading overlay shown after Show Serial
        self.serial_popup = page.locator("#addAssetSerialShipmentChallanModal")
        self.serial_table = page.locator("#assetSerialAdditionShipmentChallanTable")
        self.modal_loader = page.locator(".modalLoader")
        # LOCATOR_REQUIRES_REVIEW: Close button of the popups is not in the catalog by id; found by its name inside each popup
        self.popup_close_button = self.popup.get_by_role("button", name="Close")
        self.serial_close_button = self.serial_popup.get_by_role("button", name="Close")

    def navigate_here(self) -> None:
        """Open the Asset Shipment Challan Approval List via the Asset Transfer menu."""
        self.open_asset_transfer_submenu(MENU_LINK_NAME)
        self.wait_until_visible(self.search_button, "Search button")

    def search(self) -> None:
        """Click Search and wait until the grid shows the result."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_to_reload(self.entries_info)

    def filter_by_out_challan_no(self, out_challan_no: str) -> None:
        """Type an Out Challan No into its filter and run the search."""
        self.type_text(self.out_challan_filter, out_challan_no, "Out Challan No filter")
        self.search()

    def filter_by_status(self, status: str) -> None:
        """Choose an Approval Status (e.g. 'PENDING', 'APPROVED') and run the search."""
        action_logger.info(f"Filter: Approval Status -> {status}")
        self.status_filter.select_option(label=status)
        self.search()

    def reset_filters(self) -> None:
        """Click Reset, which empties the filter boxes (it does not search again)."""
        self.click(self.reset_button, "Reset button")

    def read_status_filter_options(self) -> list:
        """Return the options of the Approval Status filter, in order."""
        options = []
        for text in self.status_filter.locator("option").all_inner_texts():
            options.append(text.strip())
        return options

    def read_headers(self) -> list:
        """Return the grid's column headings, in order."""
        headers = []
        for text in self.grid.locator("thead th").all_inner_texts():
            headers.append(text.strip())
        return headers

    def _row_for(self, out_challan_no: str):
        """Return the grid row (locator) that contains this Out Challan No."""
        return self.grid.locator("tbody tr", has_text=out_challan_no).first

    def read_row(self, out_challan_no: str) -> dict:
        """
        Return the grid row of this Out Challan No as a dict: column heading ->
        cell text, e.g. row["Challan Status"]. Waits for the row to be shown.
        """
        row = self._row_for(out_challan_no)
        self.wait_until_visible(row, f"grid row of {out_challan_no}")
        headers = self.read_headers()
        cells = row.locator("td").all_inner_texts()
        result = {}
        for index in range(len(headers)):
            if index < len(cells):
                result[headers[index]] = cells[index].strip()
        return result

    def row_has_preview_link(self, out_challan_no: str) -> bool:
        """Return True if the last cell (Preview) of this challan's row holds a link."""
        row = self._row_for(out_challan_no)
        self.wait_until_visible(row, f"grid row of {out_challan_no}")
        return row.locator("td").last.locator("a").count() > 0

    def open_popup(self, out_challan_no: str) -> None:
        """Click the Out Challan No link to open the challan popup."""
        link = self.grid.get_by_role("link", name=out_challan_no, exact=True)
        self.click(link, f"Out Challan No {out_challan_no} link")
        self.wait_until_visible(self.popup, "Challan popup")

    def read_popup_values(self) -> dict:
        """
        Return the read-only fields of the open popup as a dict: field name ->
        text (e.g. values["Status"]). A field that is empty gives "".
        """
        values = {}
        for field_name, selector in POPUP_FIELDS:
            field = self.popup.locator(selector)
            text = field.evaluate("e => (e.value !== undefined ? e.value : e.textContent)")
            values[field_name] = text.strip()
        return values

    def read_popup_actions(self) -> list:
        """Return the names of the action buttons visible in the popup, among Approve, Reject, Sendback."""
        actions = []
        if self.approve_button.is_visible():
            actions.append("Approve")
        if self.reject_button.is_visible():
            actions.append("Reject")
        if self.sendback_button.is_visible():
            actions.append("Sendback")
        return actions

    def enter_comment(self, text: str) -> None:
        """Type a comment into the popup's comment box."""
        self.type_text(self.comment_box, text, "Comment box")

    def click_show_serial(self) -> None:
        """Click Show Serial, then wait until the serial popup is open and the loading overlay is gone."""
        self.click(self.show_serial_link, "Show Serial link")
        self.wait_until_visible(self.serial_popup, "Show Asset Serial popup")
        self.modal_loader.first.wait_for(state="hidden", timeout=POPUP_TIMEOUT)

    def read_shown_serials(self) -> list:
        """Return the Asset Serial numbers listed in the Show Asset Serial popup (the 'Asset Serial' column)."""
        headings = read_headings(self.serial_table)
        column_number = find_column_index(headings, "Asset Serial") + 1
        serials = []
        for text in self.serial_table.locator(f"tbody tr td:nth-child({column_number})").all_inner_texts():
            serials.append(text.strip())
        return serials

    def close_show_serial_popup(self) -> None:
        """Close the Show Asset Serial popup, leaving the challan popup open."""
        self.click(self.serial_close_button, "Show Asset Serial Close button")
        expect(self.serial_popup).to_be_hidden(timeout=POPUP_TIMEOUT)

    def approve_and_get_toast(self) -> str:
        """Click Approve in the popup and return the toast text that appears."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button")
        return self.get_toast_text()

    def close_popup(self) -> None:
        """Close the challan popup."""
        self.click(self.popup_close_button, "Challan popup Close button")
        expect(self.popup).to_be_hidden(timeout=POPUP_TIMEOUT)

    # ------------------------------------------------------------------
    # Checks: each one raises AssertionError saying what was expected and found
    # ------------------------------------------------------------------

    def verify_row_status(self, out_challan_no: str, expected_status: str) -> None:
        """Confirm the grid row of this Out Challan No shows `expected_status` in Challan Status."""
        found = self.read_row(out_challan_no).get("Challan Status", "")
        assertion_logger.info(f"Verifying challan {out_challan_no} has status {expected_status}")
        if found != expected_status:
            raise AssertionError(
                f"Expected challan {out_challan_no} to have status '{expected_status}' but found '{found}'."
            )

    def verify_popup_actions(self, expected_actions: list) -> None:
        """Confirm the popup shows exactly these action buttons (among Approve, Reject, Sendback)."""
        found = self.read_popup_actions()
        assertion_logger.info("Verifying the popup action buttons")
        if found != expected_actions:
            raise AssertionError(f"Expected popup actions {expected_actions} but found {found}.")

    def verify_shown_serials(self, expected_serial: str) -> None:
        """Confirm the Show Asset Serial popup lists `expected_serial`."""
        found = self.read_shown_serials()
        assertion_logger.info(f"Verifying the serial popup lists {expected_serial}")
        if expected_serial not in found:
            raise AssertionError(f"Expected serial '{expected_serial}' in the popup but found {found}.")

    def verify_toast(self, found_text: str, expected_text: str) -> None:
        """Confirm a toast text (e.g. from approve_and_get_toast) contains the expected message."""
        assertion_logger.info(f"Verifying the toast says: {expected_text}")
        if expected_text not in found_text:
            raise AssertionError(f"Expected the toast '{expected_text}' but found '{found_text}'.")
