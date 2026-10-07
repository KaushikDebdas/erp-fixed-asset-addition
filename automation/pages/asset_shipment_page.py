"""
AssetShipmentPage: Fixed Asset > Asset Transfer > Asset Shipment screen.

Covers the Shipment List (filters and grid), the Create Shipment popup, the
Update Shipment popup (opened with the Edit link) and the Shipment Details
popup (tabs Details, Transfer Challans, Add Serial, and the Approve button).

The Transfer Challans tab and everything inside it (Create Challan popup,
Challan Details popup, Add Asset Serial popup) belong to
`pages/shipment_challan_page.py`, which works on the same browser tab.

The small functions at the top of this file (read_field_value, read_headings,
find_column_index, row_to_dict, table_rows_to_dicts) are
shared with `ShipmentChallanPage`.

Facts used here come from automation/element_catalog/asset_shipment.md.
"""
from playwright.sync_api import expect

from pages.base_page import BasePage
from utils.helpers import today
from utils.logger import action_logger, assertion_logger

# Maximum time to wait for a popup or a grid row to appear (milliseconds)
POPUP_TIMEOUT = 15000

# Text a grid shows when it has no rows
NO_DATA_TEXT = "No data available in table"


# ----------------------------------------------------------------------
# Small shared functions (also used by ShipmentChallanPage)
# ----------------------------------------------------------------------

def read_field_value(field) -> str:
    """
    Return what a form field shows, whatever kind of element it is:
    the typed value of a text box or text area, the chosen option of a
    dropdown, or the plain text of any other element.
    """
    tag_name = field.evaluate("element => element.tagName")
    if tag_name == "INPUT" or tag_name == "TEXTAREA":
        return field.input_value().strip()
    if tag_name == "SELECT":
        return field.locator("option:checked").inner_text().strip()
    return field.inner_text().strip()


def read_headings(table) -> list:
    """Return the column headings of a grid, in order, with spaces trimmed."""
    headings = []
    for text in table.locator("thead th").all_inner_texts():
        headings.append(text.strip())
    return headings


def find_column_index(headings: list, name: str) -> int:
    """
    Return the 0-based position of the column whose heading contains `name`
    (e.g. "Shipment No" finds "Shipment No"; "Out Challan No" finds
    "Out Challan No."). Raises AssertionError listing the headings when the
    column does not exist.
    """
    for index in range(len(headings)):
        if name in headings[index]:
            return index
    raise AssertionError(f"Expected a grid column containing '{name}' but the headings are {headings}.")


def row_to_dict(headings: list, row) -> dict:
    """
    Turn one grid row into a dict keyed by column heading.
    Raises AssertionError when the row has a different number of cells than
    the grid has headings, because the cells could not be matched to headings.
    """
    cells = row.locator("td").all_inner_texts()
    if len(cells) != len(headings):
        raise AssertionError(
            f"Expected {len(headings)} cells (one per heading {headings}) but the row has {len(cells)}: {cells}."
        )
    values = {}
    for index in range(len(headings)):
        values[headings[index]] = cells[index].strip()
    return values


def table_rows_to_dicts(table) -> list:
    """
    Return every row of a grid as a dict keyed by column heading.
    Waits for the grid to show a first row (or the "No data" row) and returns
    an empty list when the grid has no data.
    """
    table.locator("tbody tr").first.wait_for(state="visible", timeout=POPUP_TIMEOUT)
    headings = read_headings(table)
    rows = table.locator("tbody tr")
    result = []
    for index in range(rows.count()):
        row = rows.nth(index)
        if NO_DATA_TEXT in row.inner_text():
            continue
        result.append(row_to_dict(headings, row))
    return result


class AssetShipmentPage(BasePage):
    """Page object for the Asset Shipment list and its shipment popups."""

    def __init__(self, page):
        super().__init__(page)

        # ---- Shipment List: filters ----
        # Shipment No filter (free text)
        self.shipment_no_filter = page.locator("#searchShipmentNo")
        # Shipment Status filter: PENDING, APPROVED, REJECTED
        self.status_filter = page.locator("#searchAssetShipmentStatus")
        # Runs the filter
        self.search_button = page.get_by_role("button", name=" Search")
        # Empties the filter boxes
        self.reset_filters_button = page.locator("#resetUpdate")
        # Create is a link styled as a button, so it is found by its button style and text
        self.create_button = page.locator(".btn:visible", has_text="Create")

        # ---- Shipment List: grid ----
        # The shipment list grid
        self.grid = page.locator("#shipmentListTable")
        # The line under the grid, e.g. "Showing 1 to 10 of 124 entries"
        self.entries_info = page.locator(".dataTables_info:visible").first

        # ---- Create Shipment popup (and Update Shipment popup, which has the same fields) ----
        # Shipment No (read-only, shows AUTO until saved)
        self.shipment_no_field = page.locator("#shipmentNo")
        # From Branch dropdown (only Head Office [ BDHO ])
        self.from_branch_field = page.locator("#office")
        # Shipment Date (read-only, pre-filled with today)
        self.shipment_date_field = page.locator("#faShipmentDate")
        # Courier Service Name / Transfer By
        self.courier_name_field = page.locator("#courierName")
        # Courier Number
        self.courier_number_field = page.locator("#awbNo")
        # Driver Name
        self.driver_name_field = page.locator("#driverName")
        # Transport No.
        self.transport_no_field = page.locator("#transportNo")
        # Courier Details text area
        self.courier_details_field = page.locator("#courierDetails")
        # Note/Remarks text area
        self.remarks_field = page.locator("#remarks")
        # Save button of the Create Shipment popup
        self.save_button = page.locator("#createShipment")
        # Reset button of the Create Shipment popup
        self.popup_reset_button = page.locator("#cancel")
        # Update button of the Update Shipment popup
        self.update_button = page.locator("#updateShipment")
        # Close button of whichever Create or Update popup is open
        self.popup_close_button = page.locator(".modal:visible .btn:visible", has_text="Close")

        # ---- Shipment Details popup ----
        # The Shipment Details popup
        self.details_modal = page.locator("#commonModal")
        # LOCATOR_REQUIRES_REVIEW: the tab element type is not recorded in the catalog;
        # standard Bootstrap tab links inside the popup are assumed
        self.details_tabs = self.details_modal.locator(".nav-tabs a")
        # Read-only fields of the Shipment Details popup
        self.details_shipment_no = self.details_modal.locator("#shipmentNoDetails")
        self.details_from_branch = self.details_modal.locator("#fromBranchDetails")
        self.details_driver_name = self.details_modal.locator("#driverNameDetails")
        self.details_transport_no = self.details_modal.locator("#transportNoDetails")
        self.details_courier_name = self.details_modal.locator("#courierNameDetails")
        self.details_courier_details = self.details_modal.locator("#courierDetailsDetails")
        self.details_remarks = self.details_modal.locator("#remarksDetails")
        self.details_shipment_date = self.details_modal.locator("#shipmentDateDetails")
        self.details_status = self.details_modal.locator("#statusDetails")
        self.details_date_created = self.details_modal.locator("#dateCreatedDetails")
        self.details_created_by = self.details_modal.locator("#createdByDetails")
        self.details_approval_date = self.details_modal.locator("#approvalDateDetails")
        self.details_approved_by = self.details_modal.locator("#approvedByDetails")
        # Approve button (visible on the Details tab only)
        self.approve_button = self.details_modal.locator("#approveShipment")
        # Close button of the Shipment Details popup
        self.details_close_button = self.details_modal.locator(".btn:visible", has_text="Close")
        # Grid on the Add Serial tab listing the serials of the shipment's challans
        self.add_serial_table = self.details_modal.locator("#assetSerialAdditionTable")

    # ------------------------------------------------------------------
    # Shipment List
    # ------------------------------------------------------------------

    def navigate_here(self) -> None:
        """Open Asset Transfer > Asset Shipment from the menu and wait until the list is ready."""
        self.open_asset_transfer_submenu("Asset Shipment")
        self.wait_until_visible(self.search_button, "Search button")
        self.wait_until_visible(self.grid, "Shipment list grid")

    def search(self) -> None:
        """Click Search and wait until the grid shows the result."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_to_reload(self.entries_info)

    def filter_by_shipment_no(self, shipment_no: str) -> None:
        """Type a Shipment No in its filter and run the search."""
        self.type_text(self.shipment_no_filter, shipment_no, "Shipment No filter")
        self.search()

    def filter_by_status(self, status: str) -> None:
        """Choose a Shipment Status (PENDING, APPROVED or REJECTED) and run the search."""
        action_logger.info(f"Filter: Shipment Status -> {status}")
        self.status_filter.select_option(status)
        self.search()

    def reset_filters(self) -> None:
        """Click Reset, which empties the filter boxes (it does not search again)."""
        self.click(self.reset_filters_button, "Reset button")

    def read_status_filter_options(self) -> list:
        """Return the options of the Shipment Status filter, e.g. ['-Select Status-', 'PENDING', ...]."""
        options = []
        for text in self.status_filter.locator("option").all_inner_texts():
            options.append(text.strip())
        return options

    def read_headers(self) -> list:
        """Return the column headings of the shipment list, in order."""
        return read_headings(self.grid)

    def read_row(self, shipment_no: str) -> dict:
        """
        Return the grid row of one shipment as a dict keyed by column heading
        (e.g. row["Status"]). Raises AssertionError when the grid has no such row.
        """
        self.wait_for_row_or_no_data(self.grid, shipment_no)
        row = self.grid.locator("tbody tr", has_text=shipment_no)
        if row.count() == 0:
            raise AssertionError(f"Expected a grid row for shipment {shipment_no} but the grid shows none.")
        return row_to_dict(self.read_headers(), row.first)

    def get_newest_shipment_no(self) -> str:
        """
        Return the Shipment No in the first grid row. After a Search the list
        shows the logged-in user's newest shipment first, so this is the
        shipment that was just saved. Raises AssertionError when the grid is empty.
        """
        first_row = self.grid.locator("tbody tr").first
        first_row.wait_for(state="visible", timeout=POPUP_TIMEOUT)
        if NO_DATA_TEXT in first_row.inner_text():
            raise AssertionError("Expected at least one shipment row but the grid shows 'No data available in table'.")
        headings = self.read_headers()
        index = find_column_index(headings, "Shipment No")
        shipment_no = first_row.locator("td").nth(index).inner_text().strip()
        action_logger.info(f"Newest shipment number in grid: {shipment_no}")
        return shipment_no

    def is_preview_link_shown(self, shipment_no: str) -> bool:
        """Return True when the grid row of this shipment has a Preview link (shown after approval)."""
        self.wait_for_row_or_no_data(self.grid, shipment_no)
        row = self.grid.locator("tbody tr", has_text=shipment_no)
        return row.locator("td").last.locator("a").count() > 0

    def verify_row_status(self, shipment_no: str, expected_status: str) -> None:
        """Confirm the grid row of this shipment shows `expected_status` (e.g. PENDING, APPROVED)."""
        found = self.read_row(shipment_no)["Status"]
        assertion_logger.info(f"Verifying shipment {shipment_no} has Status {expected_status}")
        if found != expected_status:
            raise AssertionError(
                f"Expected shipment {shipment_no} to have Status '{expected_status}' but found '{found}'."
            )

    # ------------------------------------------------------------------
    # Create Shipment popup
    # ------------------------------------------------------------------

    def open_create_popup(self) -> None:
        """Click Create on the list and wait until the Create Shipment popup is ready."""
        self.click(self.create_button, "Create button")
        self.wait_until_visible(self.save_button, "Create Shipment popup Save button")

    def read_create_popup_defaults(self) -> dict:
        """Return what the open Create Shipment popup is pre-filled with: keys shipment_no, from_branch, shipment_date."""
        return {
            "shipment_no": read_field_value(self.shipment_no_field),
            "from_branch": read_field_value(self.from_branch_field),
            "shipment_date": read_field_value(self.shipment_date_field),
        }

    def verify_create_popup_defaults(self) -> None:
        """
        Confirm the Create Shipment popup is pre-filled: Shipment No shows AUTO,
        From Branch is Head Office [ BDHO ], Shipment Date is today.
        """
        found = self.read_create_popup_defaults()
        assertion_logger.info("Verifying the Create Shipment popup defaults")
        if found["shipment_no"] != "AUTO":
            raise AssertionError(f"Expected Shipment No 'AUTO' but found '{found['shipment_no']}'.")
        if "BDHO" not in found["from_branch"]:
            raise AssertionError(f"Expected From Branch to contain 'BDHO' but found '{found['from_branch']}'.")
        if found["shipment_date"] != today():
            raise AssertionError(f"Expected Shipment Date '{today()}' (today) but found '{found['shipment_date']}'.")

    def fill_shipment_form(self, data: dict) -> None:
        """
        Fill the shipment boxes. `data` needs the keys courier_name, courier_number,
        driver_name, transport_no, courier_details and remarks.
        """
        self.type_text(self.courier_name_field, data["courier_name"], "Courier Service Name")
        self.type_text(self.courier_number_field, data["courier_number"], "Courier Number")
        self.type_text(self.driver_name_field, data["driver_name"], "Driver Name")
        self.type_text(self.transport_no_field, data["transport_no"], "Transport No.")
        self.type_text(self.courier_details_field, data["courier_details"], "Courier Details")
        self.type_text(self.remarks_field, data["remarks"], "Note/Remarks")

    def save_shipment_and_get_toast(self) -> str:
        """
        Click Save on the Create Shipment popup and return the toast text
        (expected: 'Asset Shipment Initiated Successfuly').
        """
        self.wait_for_toast_to_clear()
        self.click(self.save_button, "Save button")
        return self.get_toast_text()

    def reset_create_popup(self) -> None:
        """Click Reset on the Create Shipment popup, which clears the typed values."""
        self.click(self.popup_reset_button, "Reset button")

    def close_create_popup(self) -> None:
        """Close the Create Shipment popup and wait until it is gone."""
        self.click(self.popup_close_button, "Close button")
        expect(self.save_button).to_be_hidden(timeout=POPUP_TIMEOUT)

    # ------------------------------------------------------------------
    # Update Shipment popup (Edit link)
    # ------------------------------------------------------------------

    def open_edit_popup(self, shipment_no: str) -> None:
        """Click the Edit link of a shipment's row and wait until the Update Shipment popup is ready."""
        self.wait_for_row_or_no_data(self.grid, shipment_no)
        row = self.grid.locator("tbody tr", has_text=shipment_no)
        # LOCATOR_REQUIRES_REVIEW: the Update Shipment popup container id is not recorded;
        # its fields are assumed to use the same ids as the Create Shipment popup
        self.click(row.get_by_role("link", name="Edit"), f"Edit link of {shipment_no}")
        self.wait_until_visible(self.update_button, "Update Shipment popup Update button")

    def read_edit_popup_values(self) -> dict:
        """
        Return what the Update Shipment popup shows: keys shipment_no, from_branch,
        shipment_date, courier_name, courier_number, driver_name, transport_no,
        courier_details, remarks.
        """
        return {
            "shipment_no": read_field_value(self.shipment_no_field),
            "from_branch": read_field_value(self.from_branch_field),
            "shipment_date": read_field_value(self.shipment_date_field),
            "courier_name": read_field_value(self.courier_name_field),
            "courier_number": read_field_value(self.courier_number_field),
            "driver_name": read_field_value(self.driver_name_field),
            "transport_no": read_field_value(self.transport_no_field),
            "courier_details": read_field_value(self.courier_details_field),
            "remarks": read_field_value(self.remarks_field),
        }

    def close_edit_popup(self) -> None:
        """Close the Update Shipment popup and wait until it is gone."""
        self.click(self.popup_close_button, "Close button")
        expect(self.update_button).to_be_hidden(timeout=POPUP_TIMEOUT)

    # ------------------------------------------------------------------
    # Shipment Details popup
    # ------------------------------------------------------------------

    def open_details(self, shipment_no: str) -> None:
        """Click the Shipment No link in the grid and wait until the Shipment Details popup shows."""
        self.wait_for_row_or_no_data(self.grid, shipment_no)
        row = self.grid.locator("tbody tr", has_text=shipment_no)
        self.click(row.get_by_role("link", name=shipment_no, exact=True), f"Shipment No {shipment_no} link")
        self.wait_until_visible(self.details_shipment_no, "Shipment Details popup")

    def read_details_values(self) -> dict:
        """
        Return the read-only fields of the Shipment Details popup: keys shipment_no,
        from_branch, driver_name, transport_no, courier_name, courier_details,
        remarks, shipment_date, status, date_created, created_by, approval_date,
        approved_by.
        """
        return {
            "shipment_no": read_field_value(self.details_shipment_no),
            "from_branch": read_field_value(self.details_from_branch),
            "driver_name": read_field_value(self.details_driver_name),
            "transport_no": read_field_value(self.details_transport_no),
            "courier_name": read_field_value(self.details_courier_name),
            "courier_details": read_field_value(self.details_courier_details),
            "remarks": read_field_value(self.details_remarks),
            "shipment_date": read_field_value(self.details_shipment_date),
            "status": read_field_value(self.details_status),
            "date_created": read_field_value(self.details_date_created),
            "created_by": read_field_value(self.details_created_by),
            "approval_date": read_field_value(self.details_approval_date),
            "approved_by": read_field_value(self.details_approved_by),
        }

    def verify_details_values(self, data: dict, shipment_no: str) -> None:
        """
        Confirm the Shipment Details popup shows the Shipment No and the values
        typed in the form: courier_name, driver_name, transport_no,
        courier_details and remarks from `data`.
        """
        found = self.read_details_values()
        assertion_logger.info(f"Verifying the Shipment Details of {shipment_no}")
        expected = {
            "shipment_no": shipment_no,
            "courier_name": data["courier_name"],
            "driver_name": data["driver_name"],
            "transport_no": data["transport_no"],
            "courier_details": data["courier_details"],
            "remarks": data["remarks"],
        }
        for key in expected:
            if found[key] != expected[key]:
                raise AssertionError(
                    f"Expected Shipment Details {key} '{expected[key]}' but found '{found[key]}'."
                )

    def read_details_tab_names(self) -> list:
        """Return the tab names of the Shipment Details popup, e.g. ['Details', 'Transfer Challans', 'Add Serial']."""
        names = []
        for text in self.details_tabs.all_inner_texts():
            names.append(text.strip())
        return names

    def open_details_tab(self, name: str) -> None:
        """Click a tab of the Shipment Details popup ('Details', 'Transfer Challans' or 'Add Serial')."""
        tab = self.details_tabs.filter(has_text=name)
        self.click(tab, f"{name} tab")

    def read_add_serial_tab_serials(self) -> list:
        """Open the Add Serial tab and return the serial numbers listed there (empty list when none)."""
        self.open_details_tab("Add Serial")
        self.wait_until_visible(self.add_serial_table, "Add Serial grid")
        rows = table_rows_to_dicts(self.add_serial_table)
        serials = []
        for row in rows:
            for heading in row:
                if "Asset Serial" in heading:
                    serials.append(row[heading])
        return serials

    def approve_shipment_and_get_toast(self) -> str:
        """
        Switch to the Details tab (Approve is only visible there), click Approve
        and return the toast text. A successful approval shows two lines in one
        toast: 'Shipment approved successfully' and 'Gate pass generated successfully'.
        """
        self.open_details_tab("Details")
        self.wait_until_visible(self.approve_button, "Approve button")
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button")
        return self.get_toast_text()

    def close_details(self) -> None:
        """Close the Shipment Details popup and wait until it is gone."""
        self.click(self.details_close_button, "Close button")
        expect(self.details_modal).to_be_hidden(timeout=POPUP_TIMEOUT)

    def verify_toast(self, found_text: str, expected_lines: list) -> None:
        """
        Confirm a toast text (returned by a *_and_get_toast method) has exactly
        `expected_lines`, e.g. SHIPMENT_CREATED_TOAST (test_data/toast_messages.py).
        """
        self.verify_toast_text(found_text, expected_lines, "the last shipment action")
