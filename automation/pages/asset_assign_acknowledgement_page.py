"""
AssetAssignAcknowledgementPage: Fixed Asset > Asset Transaction > Asset
Assign Acknowledgement screen.

This screen is used by the employee an asset was assigned to, to confirm
that they received it. It lists the approved assignments waiting for that
employee ("Pending Asset Acknowledgement") and the assets they have already
acknowledged ("My Assigned Asset"). There is no filter and no Search button.
See `automation/element_catalog/asset_assign_acknowledgement.md`.

The page must be created with the browser tab of the ASSIGNED employee: the
user who made the assignment does not see these rows.

A row is always found by the serial inside its Details popup, and only that
row is acknowledged. The select-all checkbox is never used, because the
pending list can also hold assignments made by other people.
"""
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# How many pending rows are looked at when searching for the row that holds a serial
MAX_ROWS_TO_CHECK = 15


class AssetAssignAcknowledgementPage(BasePage):
    """Page object for the Asset Assign Acknowledgement screen."""

    def __init__(self, page):
        super().__init__(page)
        # "Pending Asset Acknowledgement" grid
        self.pending_table = page.locator("#assetAcknowledgementList")
        # Acknowledge button for the ticked rows (the popup has its own button with the same id)
        self.page_acknowledge_button = page.locator("#btnAcknowledgement").first
        # "My Assigned Asset" grid (the id is spelled this way on the page)
        self.my_assets_table = page.locator("#afterAssetAcknowledgemenedtList")
        # Details popup
        self.popup = page.locator(".modal.in")
        self.popup_assets_table = self.popup.locator("#transactionDetailsList")
        self.popup_acknowledge_button = self.popup.locator("#btnAcknowledgement")
        self.popup_close_button = self.popup.get_by_role("button", name="Close").first

    def navigate_here(self) -> None:
        """Open the Asset Assign Acknowledgement screen via the Asset Transaction menu."""
        self.open_asset_transaction_submenu("Asset Assign Acknowledgement")
        self.wait_until_visible(self.pending_table, "Pending Asset Acknowledgement grid")
        self.wait_for_grid_refresh()

    # ---- the two grids ----------------------------------------------------------

    def get_pending_headers(self) -> list:
        """Return the visible column headings of the pending grid."""
        headers = self.pending_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_my_assets_headers(self) -> list:
        """Return the visible column headings of the My Assigned Asset grid."""
        headers = self.my_assets_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def get_pending_count(self) -> int:
        """Return how many assignments are waiting for acknowledgement."""
        rows = self.pending_table.locator("tbody tr").filter(has_not_text="No data available")
        return rows.count()

    def get_pending_assigned_employees(self) -> list:
        """Return the Assigned Employee text (`[PIN] NAME`, the 6th cell after the checkbox) of every pending row."""
        rows = self.pending_table.locator("tbody tr").filter(has_not_text="No data available")
        return [rows.nth(i).locator("td:visible").nth(5).inner_text().strip() for i in range(rows.count())]

    def get_my_assigned_serials(self) -> list:
        """Return the Asset Serial of every row in My Assigned Asset."""
        rows = self.my_assets_table.locator("tbody tr").filter(has_not_text="No data available")
        return [rows.nth(i).locator("td:visible").nth(1).inner_text().strip() for i in range(rows.count())]

    def get_my_assigned_row_text(self, serial: str) -> str:
        """Return the text of the My Assigned Asset row for this serial, cells separated by ' | '."""
        row = self.my_assets_table.locator("tbody tr", has_text=serial).first
        return " | ".join(c.strip() for c in row.locator("td:visible").all_inner_texts())

    # ---- the Details popup --------------------------------------------------------

    def open_details_of_row(self, row_index: int) -> None:
        """Click Details on a pending row and wait until the popup has loaded its asset list."""
        row = self.pending_table.locator("tbody tr").nth(row_index)
        self.click(row.get_by_role("link", name="Details"), f"Details link of pending row {row_index + 1}")
        real_asset_row = self.popup_assets_table.locator("tbody tr").filter(has_not_text="No data available")
        real_asset_row.first.wait_for(state="visible", timeout=30000)

    def get_popup_value(self, field_id: str) -> str:
        """Return the value of a read-only field in the popup, e.g. 'assignedEmployeePinNo'."""
        action_logger.info(f"Read value of popup field: {field_id}")
        return self.popup.locator(f"#{field_id}").input_value().strip()

    def get_popup_asset_serials(self) -> list:
        """Return the Asset Serial of every asset listed in the popup."""
        rows = self.popup_assets_table.locator("tbody tr")
        return [rows.nth(i).locator("td:visible").nth(1).inner_text().strip() for i in range(rows.count())]

    def close_popup(self) -> None:
        """Close the Details popup without acknowledging."""
        self.click(self.popup_close_button, "Close button of Details popup")
        self.popup.wait_for(state="hidden")

    def find_pending_row_with_serial(self, serial: str) -> int:
        """
        Open Details on each pending row until the popup lists `serial`. Leaves
        that popup open and returns the row's index. Returns -1 (no popup left
        open) when none of the first rows lists the serial.
        """
        rows = self.pending_table.locator("tbody tr").filter(has_not_text="No data available")
        row_count = min(rows.count(), MAX_ROWS_TO_CHECK)
        for row_index in range(row_count):
            self.open_details_of_row(row_index)
            if serial in self.get_popup_asset_serials():
                return row_index
            self.close_popup()
        return -1

    def open_details_of_row_with_serial(self, serial: str) -> int:
        """
        Open Details on the pending row that lists `serial`, leave that popup
        open and return the row's index. This makes sure only the test's own
        assignment is ever acknowledged.
        """
        row_index = self.find_pending_row_with_serial(serial)
        assert row_index >= 0, (
            f"None of the first {MAX_ROWS_TO_CHECK} pending acknowledgements lists asset {serial}."
        )
        return row_index

    def has_pending_for_serial(self, serial: str) -> bool:
        """Return True if an acknowledgement for this asset is waiting (the popup is closed again)."""
        row_index = self.find_pending_row_with_serial(serial)
        if row_index < 0:
            return False
        self.close_popup()
        return True

    # ---- checks -------------------------------------------------------------------

    def verify_pending_headers(self, expected: list) -> None:
        """Confirm the pending grid's column headings are exactly `expected`."""
        found = self.get_pending_headers()
        assert found == expected, f"Expected the pending grid columns {expected} but found {found}."

    def verify_my_assets_headers(self, expected: list) -> None:
        """Confirm the My Assigned Asset grid's column headings are exactly `expected`."""
        found = self.get_my_assets_headers()
        assert found == expected, f"Expected the My Assigned Asset columns {expected} but found {found}."

    def verify_acknowledge_button_shown(self) -> None:
        """Confirm the page's Acknowledge button is on the screen."""
        assert self.page_acknowledge_button.is_visible(), "Expected the Acknowledge button to be shown but it is not."

    def verify_pending_rows_belong_to(self, pin: str) -> None:
        """Confirm there is at least one pending row and every row is an assignment to the employee `pin`."""
        assertion_logger.info(f"Verifying every pending row belongs to employee {pin}")
        employees = self.get_pending_assigned_employees()
        assert employees, "Expected at least one pending acknowledgement but the grid is empty."
        for assigned_employee in employees:
            assert f"[{pin}]" in assigned_employee, (
                f"A pending row belongs to '{assigned_employee}', not to employee {pin}."
            )

    def verify_popup_shows_assignment(self, serial: str, pin: str, name: str, note_prefix: str) -> None:
        """
        Confirm the open popup is the approved ASSIGN transaction of this asset
        to this employee, and that its note starts with `note_prefix`.
        """
        assertion_logger.info(f"Verifying the Details popup of the assignment of {serial}")
        wanted = {
            "assetTransactionType": "ASSIGN",
            "assignedEmployeePinNo": pin,
            "assignedEmployee": name,
            "oldTransactionStatus": "APPROVED",
        }
        problems = []
        for field_id, expected in wanted.items():
            found = self.get_popup_value(field_id)
            if found != expected:
                problems.append(f"{field_id}: expected '{expected}' but found '{found}'")
        note = self.get_popup_value("remarks")
        if not note.startswith(note_prefix):
            problems.append(f"remarks: expected a note starting with '{note_prefix}' but found '{note}'")
        serials = self.get_popup_asset_serials()
        if serials != [serial]:
            problems.append(f"asset list: expected {[serial]} but found {serials}")
        assert not problems, f"The Details popup is not as expected: {problems}"

    def verify_acknowledged(self, serial: str, pending_before: int, pin: str) -> None:
        """
        Confirm the acknowledgement took effect: one pending row less, and the
        asset is in My Assigned Asset, assigned to the employee `pin`.
        """
        assertion_logger.info(f"Verifying {serial} was acknowledged")
        pending_after = self.get_pending_count()
        assert pending_after == pending_before - 1, (
            f"Expected {pending_before - 1} pending acknowledgements after acknowledging but found {pending_after}."
        )
        my_serials = self.get_my_assigned_serials()
        assert serial in my_serials, f"Expected {serial} in My Assigned Asset but it lists {my_serials}."
        row_text = self.get_my_assigned_row_text(serial)
        assert f"[{pin}]" in row_text, f"Expected the My Assigned Asset row of {serial} to name [{pin}] but it shows '{row_text}'."

    def acknowledge_in_popup_and_get_toast(self) -> str:
        """Click Acknowledge in the open popup, return the message shown, and wait for the popup to close."""
        self.wait_for_toast_to_clear()
        self.click(self.popup_acknowledge_button, "Acknowledge button in popup")
        toast_text = self.get_toast_text()
        self.popup.wait_for(state="hidden")
        self.wait_for_grid_refresh()
        return toast_text
