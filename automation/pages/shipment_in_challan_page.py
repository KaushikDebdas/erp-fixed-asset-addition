"""
ShipmentInChallanPage: Fixed Asset > Asset Transfer > Asset Shipment
In-Challan screen.

Lists approved challans waiting to be acknowledged by the receiving side. The
challan is opened from its Out Challan No link and acknowledged in a popup.
Used by the Asset Shipment end-to-end flow
(projects/fixedasset/e2e-flows/asset-transfer-shipment.md, steps 24 and 25).
Locators come from automation/element_catalog/asset_shipment_in_challan.md.
"""
from playwright.sync_api import expect

from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Name of the menu link under Fixed Asset > Asset Transfer
MENU_LINK_NAME = "Asset Shipment In-Challan"

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

# Maximum time to wait for a popup to open or close (milliseconds)
POPUP_TIMEOUT = 15000


class ShipmentInChallanPage(BasePage):
    """Page object for the Asset Shipment In-Challan screen."""

    def __init__(self, page):
        super().__init__(page)
        # Out Challan No filter (free text)
        self.out_challan_filter = page.locator("#outChallanNo")
        # Challan Status filter: offers only APPROVED and ACKNOWLEDGED
        self.status_filter = page.locator("#challanStatus")
        # Runs the filter
        self.search_button = page.get_by_role("button", name=" Search")
        # Clears the filter boxes
        self.reset_button = page.locator("#resetUpdate")
        # Results grid and the line under it, e.g. "Showing 1 to 10 of 5 entries"
        self.grid = page.locator("#challanListTable")
        self.entries_info = page.locator("#challanListTable_info")
        # Challan popup opened from an Out Challan No link
        self.popup = page.locator("#inChallanDetailsModal")
        # Loading overlay that covers the page for a few seconds after Acknowledge
        self.modal_loader = page.locator(".modalLoader")
        # Acknowledge button in the popup
        self.acknowledge_button = page.locator("#acknowledge")
        # LOCATOR_REQUIRES_REVIEW: Close button of the popup is not in the catalog by id; found by its name inside the popup
        self.popup_close_button = self.popup.get_by_role("button", name="Close")

    def navigate_here(self) -> None:
        """Open the Asset Shipment In-Challan list via the Asset Transfer menu."""
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
        """Choose a Challan Status ('APPROVED' or 'ACKNOWLEDGED') and run the search."""
        action_logger.info(f"Filter: Challan Status -> {status}")
        self.status_filter.select_option(label=status)
        self.search()

    def reset_filters(self) -> None:
        """Click Reset, which empties the filter boxes (it does not search again)."""
        self.click(self.reset_button, "Reset button")

    def read_status_filter_options(self) -> list:
        """Return the options of the Challan Status filter, in order."""
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
        text (e.g. values["In Challan No"]). A field that is empty gives "".
        """
        values = {}
        for field_name, selector in POPUP_FIELDS:
            field = self.popup.locator(selector)
            text = field.evaluate("e => (e.value !== undefined ? e.value : e.textContent)")
            values[field_name] = text.strip()
        return values

    def read_popup_actions(self) -> list:
        """Return the names of the action buttons visible in the popup, among Acknowledge."""
        actions = []
        if self.acknowledge_button.is_visible():
            actions.append("Acknowledge")
        return actions

    def acknowledge(self) -> None:
        """
        Click Acknowledge in the popup and wait until the loading overlay that
        follows it is gone. No message is checked, because the success toast
        has not been confirmed. Callers should search again and check the row
        status with verify_row_status.
        """
        self.click(self.acknowledge_button, "Acknowledge button")
        expect(self.modal_loader.first).to_be_hidden(timeout=POPUP_TIMEOUT)

    def close_popup(self) -> None:
        """Close the challan popup."""
        self.click(self.popup_close_button, "Challan popup Close button")
        expect(self.popup).to_be_hidden(timeout=POPUP_TIMEOUT)

    def close_popup_if_open(self) -> None:
        """Close the challan popup when it is still open (after Acknowledge it may already have closed)."""
        if self.popup.is_visible():
            self.close_popup()

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

    def verify_in_challan_no_filled(self, out_challan_no: str) -> None:
        """Confirm the grid row of this Out Challan No already shows an In Challan No."""
        found = self.read_row(out_challan_no).get("In Challan No", "")
        assertion_logger.info(f"Verifying challan {out_challan_no} has an In Challan No")
        if found == "":
            raise AssertionError(
                f"Expected challan {out_challan_no} to show an In Challan No but the cell is empty."
            )
