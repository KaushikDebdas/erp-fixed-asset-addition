"""
AssetSerialGlobalListPage: Fixed Asset > Asset Profile > Asset Serial Global
List screen and its "Asset Profile Details" popup.

Lists every asset by Asset Serial. Clicking a serial opens the popup with the
asset's details, seven tabs, and four "Change" buttons. See
`automation/element_catalog/asset_serial_global_list.md` for every field and
`asset_profile_reference_values.md` for the drop-down values.

Nothing here saves a change: the Update buttons are only clicked with a
missing value, to read the validation message.
"""
import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from test_data.toast_messages import STATUS_UPDATED_TOAST
from utils.logger import action_logger, assertion_logger

# Heading of each result column that is read. The cells are found by these headings, because
# some offices have a Department column in the grid and some do not, which moves the columns.
SERIAL_HEADING = "Asset Serial"
ITEM_NAME_HEADING = "Asset Item Name"
SUB_CATEGORY_HEADING = "Sub Category"
CATEGORY_HEADING = "Category Name"
GROUP_HEADING = "Group Name"
PROJECT_HEADING = "Project Name"
ASSIGN_STATUS_HEADING = "Assign Status"
UTILIZATION_STATUS_HEADING = "Utilization Status"

# Popup fields that describe an asset's assignment: status, employee PIN and name, building, floor, room
ASSIGNMENT_FIELDS = ["assignUnassignStatus", "employeePin", "assignedEmployee", "buildingName", "floorNo", "roomNo"]

# An extended asset's serial is its parent's serial plus "-1", "-2", ...
EXTENDED_SERIAL_SUFFIX = re.compile(r"-\d+$")

# Tab name -> the id of the tab's content pane
TAB_PANES = {
    "Details": "#tab_details",
    "Depreciation History": "#tab_dep_history",
    "Revaluation History": "#tab_rev_history",
    "Transaction History": "#tab_transfer_history",
    "Expenditure": "#tab_expenditure",
    "Addition History": "#tab_addition_history",
    "Disposal Info": "#tab_disposal_info",
    "Attachment": "#tab_attachment",
}


class AssetSerialGlobalListPage(BasePage):
    """Page object for the Asset Serial Global List screen and its detail popup."""

    def __init__(self, page):
        super().__init__(page)
        # Filters
        # The popup also has an #assetSerial field, which stays on the page after the popup closes,
        # so the filter box is found by its name, which only the filter box has
        self.asset_serial_filter = page.locator('input[name="assetSerial"]')
        self.utilization_status_filter = page.locator("#status")
        self.assign_status_filter = page.locator("#assetAssignStatus")
        # Runs the filter
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid
        self.results_table = page.locator("#assetSerialGlobalList")
        # "Asset Profile Details" popup. Several ids repeat on this page (for
        # example #assetName), so popup fields are always read inside it.
        self.popup = page.locator("#commonModal")
        self.popup_close_button = self.popup.get_by_role("button", name="Close").first
        # The four "Change" buttons in the popup
        self.source_of_fund_change_button = self.popup.locator("#sourceOfFundChange")
        self.status_change_button = self.popup.locator("#statusChange")
        self.item_change_button = self.popup.locator("#itemChange")
        self.measurement_change_button = self.popup.locator("#enableMeasurement")
        self.measurement_update_button = self.popup.locator("#setMeasurement")
        self.measurement_field = self.popup.locator("#measurement")
        # The small popup that Source Of Fund, Utilization Status and Item open
        self.change_popup = page.locator("#changeStatus")
        self.new_source_of_fund_select = page.locator("#newSourceOfFund")
        self.source_of_fund_update_button = page.locator("#updateAssetSourceOfFund")
        self.new_status_select = page.locator("#updateStatus")
        self.status_note_field = page.locator("#updateNote")
        self.status_update_button = page.locator("#updateAssetBtn")
        self.new_item_specification_field = page.locator("#newItemSpecification")
        self.item_update_button = page.locator("#updateItemSpecification")
        # The Asset Serial Number field of the popup (it shows which asset the popup is about)
        self.popup_serial_field = self.popup.locator("#assetSerial")
        # Addition History tab of the popup (parent assets only): its pane, grid,
        # "Records per page" box and the "Showing 1 to 3 of 3 entries" text
        self.addition_history_pane = self.popup.locator("#tab_addition_history")
        self.addition_history_grid = self.popup.locator("#assetAdditionHistoryList")
        self.records_per_page_select = self.addition_history_pane.get_by_label("Records per page")
        self.addition_history_info = self.addition_history_pane.get_by_role("status")

    # ---- search -----------------------------------------------------------

    def navigate_here(self) -> None:
        """Open the Asset Serial Global List screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Global List")
        self.wait_until_visible(self.search_button, "Search button")

    def search_by_serial(self, serial: str) -> None:
        """Filter by Asset Serial and wait for the result (or the empty message)."""
        self.type_text(self.asset_serial_filter, serial, "Asset Serial filter")
        self.click(self.search_button, "Search button")
        self.wait_for_row_or_no_data(self.results_table, serial)

    def filter_by_utilization_status(self, status: str) -> None:
        """Pick an Asset Utilization Status in the filter (does not search yet)."""
        action_logger.info(f"Filter: Asset Utilization Status -> {status}")
        self.utilization_status_filter.select_option(status)

    def filter_by_assign_status(self, status: str) -> None:
        """Pick an Assign Status (ASSIGNED / UNASSIGNED) in the filter (does not search yet)."""
        action_logger.info(f"Filter: Assign Status -> {status}")
        self.assign_status_filter.select_option(status)

    def _row_of(self, serial: str):
        """
        Return the result row whose Asset Serial link is exactly `serial`. Searching a parent
        also lists its extended assets ('<serial>-1', ...), so a row is never matched by text alone.
        """
        serial_link = self.page.get_by_role("link", name=serial, exact=True)
        return self.results_table.locator("tbody tr").filter(has=serial_link)

    def is_serial_listed(self, serial: str) -> bool:
        """Return True if a result row for this Asset Serial is shown."""
        return self._row_of(serial).count() > 0

    def _read_row_by_heading(self, serial: str) -> dict:
        """
        Return the cells of the row for this serial as {column heading: text}. The headings and the
        cells are both read with the hidden ID column included, so they line up one to one.
        """
        headings = [h.strip() for h in self.results_table.locator("thead th").all_text_contents()]
        row = self._row_of(serial).first
        cells = [c.strip() for c in row.locator("td").all_text_contents()]
        assert len(headings) == len(cells), (
            f"The Global List has {len(headings)} column headings {headings} but the row of {serial} has {len(cells)} cells."
        )
        return dict(zip(headings, cells))

    def _row_cell(self, serial: str, heading: str) -> str:
        """Return the text of one cell of the row for this serial, found by its column heading."""
        row = self._read_row_by_heading(serial)
        assert heading in row, f"The Global List has no '{heading}' column. Its columns: {list(row)}"
        return row[heading]

    def get_utilization_status(self, serial: str) -> str:
        """Return the Utilization Status shown in the row for this serial."""
        return self._row_cell(serial, UTILIZATION_STATUS_HEADING)

    def get_assign_status(self, serial: str) -> str:
        """Return the Assign Status shown in the row for this serial."""
        return self._row_cell(serial, ASSIGN_STATUS_HEADING)

    def get_row_values(self, serial: str) -> dict:
        """Return the cells of the row for this serial: item, sub category, category, group, project, assign and utilization status."""
        row = self._read_row_by_heading(serial)
        return {
            "serial": row[SERIAL_HEADING],
            "item_name": row[ITEM_NAME_HEADING],
            "sub_category": row[SUB_CATEGORY_HEADING],
            "category": row[CATEGORY_HEADING],
            "group": row[GROUP_HEADING],
            "project_in_grid": row[PROJECT_HEADING],
            "assign_status": row[ASSIGN_STATUS_HEADING],
            "utilization_status": row[UTILIZATION_STATUS_HEADING],
        }

    def verify_row_shows(self, serial: str, expected: dict) -> None:
        """Confirm the row of this serial shows the values in `expected` (see build_asset_profile). Names every difference."""
        found = self.get_row_values(serial)
        assertion_logger.info(f"Verifying the grid row of {serial}")
        problems = []
        for name, value in found.items():
            if value != expected[name]:
                problems.append(f"{name}: expected '{expected[name]}' but found '{value}'")
        assert not problems, f"The row of {serial} is not as expected: {problems}"

    def verify_statuses(self, serial: str, assign_status: str, utilization_status: str) -> None:
        """Confirm the row of this serial shows the given Assign Status and Utilization Status."""
        assertion_logger.info(f"Verifying the statuses of {serial}")
        assert self.is_serial_listed(serial), f"Expected {serial} to be listed on the Global List but it was not."
        found_assign = self.get_assign_status(serial)
        found_utilization = self.get_utilization_status(serial)
        assert (found_assign, found_utilization) == (assign_status, utilization_status), (
            f"Expected {serial} to be {assign_status} / {utilization_status} "
            f"but found {found_assign} / {found_utilization}."
        )

    def open_and_read_assign_status(self, serial: str) -> str:
        """
        Open the Global List, search the serial and return the asset's real
        Assign Status (ASSIGNED or UNASSIGNED). Fails with a clear message when
        the serial is not listed.
        """
        self.navigate_here()
        self.search_by_serial(serial)
        assert self.is_serial_listed(serial), f"Expected {serial} to be listed on the Global List but it was not."
        return self.get_assign_status(serial)

    def verify_assign_status(self, serial: str, expected: str) -> None:
        """Confirm the row of this serial (after searching it) shows this Assign Status."""
        assertion_logger.info(f"Verifying the Assign Status of {serial}")
        assert self.is_serial_listed(serial), f"Expected {serial} to be listed on the Global List but it was not."
        found = self.get_assign_status(serial)
        assert found == expected, f"Expected the Assign Status of {serial} to be {expected} but found {found}."

    def verify_popup_fields(self, expected: dict) -> None:
        """Confirm the open popup shows every field in `expected` ({field id: text}). Names every difference."""
        assertion_logger.info("Verifying the popup fields")
        problems = []
        for field_id, wanted in expected.items():
            found = self.get_popup_value(field_id)
            if found != wanted:
                problems.append(f"{field_id}: expected '{wanted}' but found '{found}'")
        assert not problems, f"The popup is not as expected: {problems}"

    def verify_serial_not_listed(self, serial: str) -> None:
        """Confirm no result row shows this Asset Serial (call after searching it)."""
        assertion_logger.info(f"Verifying {serial} is not listed")
        assert not self.is_serial_listed(serial), f"Expected {serial} not to be listed on the Global List but it was."

    def verify_popup_shows(self, expected: dict) -> None:
        """Confirm the open popup shows the values in `expected` (see build_asset_profile). Names every difference."""
        fields = {
            "assetSerial": expected["serial"],
            "registrationNumber": expected["registration_number"],
            "assetName": expected["item_name"],
            "subCategory": expected["sub_category"],
            "category": expected["category"],
            "group": expected["group"],
            "projectName": expected["project_in_popup"],
            "utilizationStatusName": expected["utilization_status"],
            "measurement": expected["measurement"],
            "measurementUnit": expected["measurement_unit"],
            "netAssetValue": expected["net_asset_value"],
        }
        assertion_logger.info(f"Verifying the popup of {expected['serial']}")
        problems = []
        for field_id, wanted in fields.items():
            found = self.get_popup_value(field_id)
            if found != wanted:
                problems.append(f"{field_id}: expected '{wanted}' but found '{found}'")
        assert not problems, f"The popup of {expected['serial']} is not as expected: {problems}"

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    # ---- asset popup ------------------------------------------------------

    def open_asset_popup(self, serial: str) -> None:
        """Click the Asset Serial link to open the Asset Profile Details popup."""
        link = self.results_table.get_by_role("link", name=serial, exact=True)
        self.click(link, f"Asset Serial {serial} link")
        self.wait_until_visible(self.popup, "Asset Profile Details popup")
        self.wait_until_visible(self.popup.locator("#assetSerial"), "Asset Serial Number field")

    def get_popup_value(self, field_id: str) -> str:
        """Return the value of a read-only field in the popup, e.g. 'measurement'."""
        action_logger.info(f"Read value of popup field: {field_id}")
        return self.popup.locator(f"#{field_id}").input_value().strip()

    def get_tab_names(self) -> list:
        """Return the names of the popup's tabs, in order."""
        names = self.popup.locator("a[data-toggle=tab]").all_inner_texts()
        return [n.strip() for n in names]

    def get_tab_text(self, tab_name: str) -> str:
        """Open a tab and return the visible text of its content."""
        pane_id = TAB_PANES[tab_name]
        tab_link = self.popup.locator("a[data-toggle=tab]", has_text=tab_name)
        self.click(tab_link, f"{tab_name} tab")
        pane = self.popup.locator(pane_id)
        self.wait_until_visible(pane, f"{tab_name} tab content")
        return pane.inner_text()

    def get_expenditure_row(self, expense_ref: str) -> dict:
        """
        Open the Expenditure tab of the open popup and return the row whose Reference Number is
        `expense_ref` as {column heading: text}. Stops with the rows shown when there is no such row.
        """
        self.get_tab_text("Expenditure")
        grid = self.popup.locator("#assetExpenditureList")
        headings = [h.strip() for h in grid.locator("thead th").all_text_contents()]
        rows = []
        for row in grid.locator("tbody tr").all():
            cells = [c.strip() for c in row.locator("td").all_text_contents()]
            rows.append(dict(zip(headings, cells)))
        for row in rows:
            if row.get("Reference Number") == expense_ref:
                return row
        assert False, f"The Expenditure tab has no row with Reference Number '{expense_ref}'. Its rows: {rows}"

    def close_popup(self) -> None:
        """Close the Asset Profile Details popup."""
        self.click(self.popup_close_button, "Close button of Asset Profile Details popup")

    # ---- parent assets and extended assets --------------------------------

    def read_parent_serials_on_first_page(self, item_name: str) -> list:
        """
        Return the Asset Serials of the PARENT assets of this item on the first page of
        the Global List, newest first. Call it before any search: the list shows the newest
        asset first, and an extended asset is told apart by its serial, "<parent serial>-1", ...
        """
        self.wait_for_loader_to_finish()
        headings = [h.strip() for h in self.results_table.locator("thead th").all_text_contents()]
        serial_column = headings.index(SERIAL_HEADING)
        item_column = headings.index(ITEM_NAME_HEADING)
        serials = []
        for row in self.results_table.locator("tbody tr").all():
            cells = [c.strip() for c in row.locator("td").all_text_contents()]
            if cells[item_column] == item_name and not EXTENDED_SERIAL_SUFFIX.search(cells[serial_column]):
                serials.append(cells[serial_column])
        return serials

    def read_newest_parent_serial(self, item_name: str) -> str:
        """
        Return the Asset Serial of the newest PARENT asset of this item (see
        read_parent_serials_on_first_page). Stops when the first page has none.
        """
        serials = self.read_parent_serials_on_first_page(item_name)
        assert serials, f"The first page of the Global List has no parent asset of '{item_name}'."
        action_logger.info(f"Newest parent asset of {item_name}: {serials[0]}")
        return serials[0]

    def find_newest_parent_by_specification(self, item_name: str, specification: str) -> str:
        """
        Return the serial of the newest parent asset of this item whose Item Specification
        is `specification`. Other users register the same item at the same time, so each
        parent asset on the first page is opened, newest first, until the specification
        matches. Stops with the serials checked when none matches.
        """
        self.navigate_here()
        candidates = self.read_parent_serials_on_first_page(item_name)
        for serial in candidates:
            self.open_asset_popup(serial)
            found = self.get_popup_value("itemSpecification")
            self.close_popup()
            self.popup.wait_for(state="hidden")
            if found == specification:
                action_logger.info(f"Asset with Item Specification {specification}: {serial}")
                return serial
        assert False, (
            f"No parent asset of '{item_name}' on the first page of the Global List has the Item "
            f"Specification '{specification}'. Parent assets checked: {candidates}"
        )

    def read_popup_fields(self, serial: str, field_ids: list) -> dict:
        """Search the serial, open its popup and return {field id: text} for these fields. Closes the popup."""
        self.search_by_serial(serial)
        self.open_asset_popup(serial)
        values = {}
        for field_id in field_ids:
            values[field_id] = self.get_popup_value(field_id)
        self.close_popup()
        self.popup.wait_for(state="hidden")
        return values

    def is_popup_field_shown(self, field_id: str) -> bool:
        """Return True when the open popup has a visible field with this id."""
        field = self.popup.locator(f"#{field_id}")
        return field.count() > 0 and field.first.is_visible()

    def verify_popup_field_not_shown(self, field_id: str, rule: str) -> None:
        """Confirm the open popup has no visible field with this id. `rule` names the CR rule in the failure text."""
        assertion_logger.info(f"Verifying the popup has no {field_id} field")
        assert not self.is_popup_field_shown(field_id), f"The popup should not show the field '{field_id}': {rule}"

    def verify_tab_shown(self, tab_name: str, expected_shown: bool) -> None:
        """Confirm the open popup has (True) or has not (False) the tab named `tab_name`."""
        assertion_logger.info(f"Verifying the tab {tab_name} is {'shown' if expected_shown else 'absent'}")
        tab_names = self.get_tab_names()
        assert (tab_name in tab_names) == expected_shown, (
            f"Expected the tab '{tab_name}' to be {'shown' if expected_shown else 'absent'} but the tabs are {tab_names}."
        )

    def open_addition_history(self, serial: str) -> None:
        """Search a parent asset, open its popup and open its Addition History tab."""
        self.search_by_serial(serial)
        self.open_asset_popup(serial)
        self.get_tab_text("Addition History")

    def read_addition_history_headings(self) -> list:
        """Return the column headings of the Addition History grid of the open popup."""
        return [h.strip() for h in self.addition_history_grid.locator("thead th").all_text_contents()]

    def get_records_per_page_options(self) -> list:
        """Return the choices of the Addition History "Records per page" box."""
        return [text.strip() for text in self.records_per_page_select.locator("option").all_inner_texts()]

    def get_selected_records_per_page(self) -> str:
        """Return the choice selected in the Addition History "Records per page" box."""
        return self.records_per_page_select.input_value()

    def get_addition_history_entries_text(self) -> str:
        """Return the Addition History entries text, e.g. 'Showing 1 to 2 of 2 entries'."""
        return self.addition_history_info.inner_text().strip()

    def open_extended_from_addition_history(self, extended_serial: str) -> None:
        """Click the extended asset's serial in the Addition History grid and wait until the popup shows that asset."""
        link = self.addition_history_grid.get_by_role("link", name=extended_serial, exact=True)
        self.click(link, f"Addition History link {extended_serial}")
        expect(self.popup_serial_field).to_have_value(extended_serial)

    def close_popup_back_to(self, serial: str) -> None:
        """
        Close the popup of an extended asset that was opened from the Addition History and
        confirm the popup of `serial` (its parent) is shown again.
        """
        self.close_popup()
        assertion_logger.info(f"Verifying the popup of {serial} is shown again")
        expect(self.popup).to_be_visible()
        expect(self.popup_serial_field).to_have_value(serial)

    def read_addition_history_rows(self) -> list:
        """
        Open the Addition History tab of the open popup and return its rows as a list of
        {column heading: text}. Only a parent asset has this tab.
        """
        self.get_tab_text("Addition History")
        grid = self.popup.locator("#assetAdditionHistoryList")
        headings = [h.strip() for h in grid.locator("thead th").all_text_contents()]
        rows = []
        for row in grid.locator("tbody tr").all():
            cells = [c.strip() for c in row.locator("td").all_text_contents()]
            rows.append(dict(zip(headings, cells)))
        return rows

    def read_addition_history_serials(self, parent_serial: str) -> list:
        """Search the parent asset, open its popup and return the serials listed in its Addition History tab."""
        self.search_by_serial(parent_serial)
        self.open_asset_popup(parent_serial)
        rows = self.read_addition_history_rows()
        self.close_popup()
        self.popup.wait_for(state="hidden")
        return [row[SERIAL_HEADING] for row in rows]

    def verify_extended_asset_popup(self, extended_serial: str, parent_serial: str) -> None:
        """
        Open the popup of an extended asset (already searched) and confirm it names its
        parent asset in the Parent Asset field and has no Addition History tab. Closes the popup.
        """
        assertion_logger.info(f"Verifying the popup of extended asset {extended_serial}")
        self.open_asset_popup(extended_serial)
        found_parent = self.get_popup_value("parentAssetSerial")
        tab_names = self.get_tab_names()
        self.close_popup()
        self.popup.wait_for(state="hidden")
        assert found_parent == parent_serial, (
            f"Expected the Parent Asset of {extended_serial} to be {parent_serial} but found '{found_parent}'."
        )
        assert "Addition History" not in tab_names, (
            f"The extended asset {extended_serial} should have no Addition History tab but its tabs are {tab_names}."
        )

    def verify_all_assigned(self, serials: list) -> None:
        """Search each serial and confirm its Assign Status is ASSIGNED. Names every serial that is not."""
        problems = []
        for serial in serials:
            self.search_by_serial(serial)
            found = self.get_assign_status(serial) if self.is_serial_listed(serial) else "not listed"
            if found != "ASSIGNED":
                problems.append(f"{serial}: {found}")
        assert not problems, f"Expected {serials} to be ASSIGNED but: {problems}"

    def read_assignment(self, serial: str) -> dict:
        """Search the serial, open its popup and return its assignment: status, employee PIN and name, building, floor, room."""
        self.search_by_serial(serial)
        self.open_asset_popup(serial)
        assignment = {}
        for field_id in ASSIGNMENT_FIELDS:
            assignment[field_id] = self.get_popup_value(field_id)
        self.close_popup()
        self.popup.wait_for(state="hidden")
        return assignment

    def verify_same_assignment_as_parent(self, parent_serial: str, extended_serial: str) -> None:
        """
        Confirm the extended asset is ASSIGNED to the same employee, building, floor and
        room as its parent (read from both popups). Names every difference.
        """
        assertion_logger.info(f"Verifying {extended_serial} has the assignment of {parent_serial}")
        parent = self.read_assignment(parent_serial)
        extended = self.read_assignment(extended_serial)
        assert parent["assignUnassignStatus"] == "ASSIGNED", f"The parent {parent_serial} is not ASSIGNED: {parent}"
        problems = []
        for field_id in ASSIGNMENT_FIELDS:
            if extended[field_id] != parent[field_id]:
                problems.append(f"{field_id}: parent '{parent[field_id]}', extended '{extended[field_id]}'")
        assert not problems, f"{extended_serial} is not assigned like its parent {parent_serial}: {problems}"

    def verify_moved_together(self, parent_serial: str, extended_serial: str, building: str) -> None:
        """
        After an Internal Movement of the parent: confirm the parent shows the new `building`
        and a floor, and that its extended asset has the same assignment (employee, building,
        floor, room). Names every difference.
        """
        assertion_logger.info(f"Verifying {parent_serial} and {extended_serial} moved together to {building}")
        parent = self.read_assignment(parent_serial)
        assert parent["buildingName"] == building, (
            f"Expected the parent {parent_serial} in building '{building}' but it shows '{parent['buildingName']}'."
        )
        assert parent["floorNo"] != "", f"Expected the parent {parent_serial} to show a floor but the Floor Number is empty."
        self.verify_same_assignment_as_parent(parent_serial, extended_serial)

    def verify_parent_addition_history(self, parent_serial: str, extended_serial: str, expected: dict) -> None:
        """
        Open the popup of a parent asset (already searched) and confirm its Addition History
        has a row for `extended_serial` with the values in `expected` ({column heading: text}).
        Names every difference. Closes the popup.
        """
        assertion_logger.info(f"Verifying the Addition History of {parent_serial}")
        self.open_asset_popup(parent_serial)
        rows = self.read_addition_history_rows()
        self.close_popup()
        self.popup.wait_for(state="hidden")
        matching = [row for row in rows if row.get(SERIAL_HEADING) == extended_serial]
        assert matching, (
            f"The Addition History of {parent_serial} has no row for {extended_serial}. "
            f"Serials listed: {[row.get(SERIAL_HEADING) for row in rows]}"
        )
        problems = []
        for heading, wanted in expected.items():
            if matching[0].get(heading) != wanted:
                problems.append(f"{heading}: expected '{wanted}' but found '{matching[0].get(heading)}'")
        assert not problems, f"The Addition History row of {extended_serial} is not as expected: {problems}"

    def read_transaction_history_rows(self, serial: str) -> list:
        """
        Search the serial, open its popup and return the rows of its Transaction History
        tab as a list of {column heading: text}. Closes the popup.
        """
        self.search_by_serial(serial)
        self.open_asset_popup(serial)
        self.get_tab_text("Transaction History")
        grid = self.popup.locator(TAB_PANES["Transaction History"]).locator("table").first
        headings = [h.strip() for h in grid.locator("thead th").all_text_contents()]
        rows = []
        for row in grid.locator("tbody tr").all():
            cells = [c.strip() for c in row.locator("td").all_text_contents()]
            rows.append(dict(zip(headings, cells)))
        self.close_popup()
        self.popup.wait_for(state="hidden")
        return rows

    def verify_transaction_in_history(self, serial: str, transaction_type: str, status: str) -> None:
        """Confirm the asset's Transaction History tab has a `transaction_type` transaction with Transaction Status `status`."""
        assertion_logger.info(f"Verifying {serial} has a {status} {transaction_type} transaction")
        rows = self.read_transaction_history_rows(serial)
        found = [(row.get("Transaction Type"), row.get("Transaction Status")) for row in rows]
        assert (transaction_type, status) in found, (
            f"The Transaction History of {serial} should have a {status} {transaction_type} transaction "
            f"but its (type, status) rows are {found}."
        )

    def verify_addition_history_empty(self) -> None:
        """Confirm the open Addition History tab lists no extended asset ('Showing 0 to 0 of 0 entries')."""
        assertion_logger.info("Verifying the Addition History is empty")
        entries = self.get_addition_history_entries_text()
        assert entries == "Showing 0 to 0 of 0 entries", (
            f"Expected an empty Addition History but it shows '{entries}' and rows {self.read_addition_history_rows()}."
        )

    def verify_extended_serial_format(self, parent_serial: str, extended_serials: list) -> None:
        """
        Confirm the extended serials are the parent's serial with "-1", "-2", ... in the
        order they were added, and that no two are the same (CR F01S01).
        """
        assertion_logger.info(f"Verifying the serials of the extended assets of {parent_serial}")
        expected = []
        for number in range(1, len(extended_serials) + 1):
            expected.append(f"{parent_serial}-{number}")
        assert extended_serials == expected, (
            f"The extended assets of {parent_serial} should be {expected} but are {extended_serials}."
        )
        assert len(set(extended_serials)) == len(extended_serials), f"Two extended assets share a serial: {extended_serials}"

    def verify_listed_on_their_own(self, serials: list, assign_status: str, utilization_status: str) -> None:
        """Search each serial on its own and confirm it has its own row with these statuses."""
        for serial in serials:
            self.search_by_serial(serial)
            self.verify_statuses(serial, assign_status, utilization_status)

    def verify_extended_asset_popups(self, extended_serials: list, parent_serial: str) -> None:
        """Search each extended asset and confirm its popup names the parent and has no Addition History tab."""
        for serial in extended_serials:
            self.search_by_serial(serial)
            self.verify_extended_asset_popup(serial, parent_serial)

    def read_addition_history_row(self, parent_serial: str, extended_serial: str) -> dict:
        """Return the Addition History row of `extended_serial` in the parent's popup ({column heading: text}). Closes the popup."""
        self.open_addition_history(parent_serial)
        rows = self.read_addition_history_rows()
        self.close_popup()
        self.popup.wait_for(state="hidden")
        for row in rows:
            if row.get(SERIAL_HEADING) == extended_serial:
                return row
        assert False, f"The Addition History of {parent_serial} has no row for {extended_serial}. Rows: {rows}"

    def verify_addition_history_rows(self, extended_serials: list, expected: dict, reference_prefix: str) -> None:
        """
        Confirm the open Addition History tab has one row per extended asset, in the order they
        were added (SL 1, 2, ...), each with the values in `expected` ({column heading: text}) and
        a Reference Number starting with `reference_prefix`. Names every difference.
        """
        assertion_logger.info("Verifying the rows of the Addition History")
        rows = self.read_addition_history_rows()
        listed = [row.get(SERIAL_HEADING) for row in rows]
        assert listed == extended_serials, f"The Addition History should list {extended_serials} but lists {listed}."
        problems = []
        for number, row in enumerate(rows, start=1):
            wanted = {**expected, "SL": str(number)}
            for heading, value in wanted.items():
                if row.get(heading) != value:
                    problems.append(f"{row.get(SERIAL_HEADING)} {heading}: expected '{value}' but found '{row.get(heading)}'")
            if not row.get("Reference Number", "").startswith(reference_prefix):
                problems.append(f"{row.get(SERIAL_HEADING)} Reference Number: expected '{reference_prefix}...' but found '{row.get('Reference Number')}'")
        assert not problems, f"The Addition History rows are not as expected: {problems}"

    # ---- the Change buttons -----------------------------------------------

    def open_source_of_fund_change(self) -> None:
        """Click Change next to Source Of Fund and wait for its small popup."""
        self.click(self.source_of_fund_change_button, "Source Of Fund Change button")
        self.wait_until_visible(self.new_source_of_fund_select.locator("xpath=.."), "Source Of Fund popup")

    def get_source_of_fund_options(self) -> list:
        """Return every value of the New Source Of Fund drop-down, placeholder first."""
        options = self.new_source_of_fund_select.evaluate(
            "select => Array.from(select.options).map(o => o.text.trim())"
        )
        return options

    def click_source_of_fund_update_and_get_toast(self) -> str:
        """Click Update in the Source Of Fund popup and return the message shown."""
        self.wait_for_toast_to_clear()
        self.click(self.source_of_fund_update_button, "Source Of Fund Update button")
        return self.get_toast_text()

    def open_status_change(self) -> None:
        """Click Change next to Asset Utilization Status and wait for its small popup."""
        self.click(self.status_change_button, "Utilization Status Change button")
        self.wait_until_visible(self.new_status_select.locator("xpath=.."), "Utilization Status popup")

    def get_status_options(self) -> list:
        """Return every value of the Utilization Status drop-down, placeholder first."""
        return self.new_status_select.evaluate(
            "select => Array.from(select.options).map(o => o.text.trim())"
        )

    def get_selected_status(self) -> str:
        """Return the status currently selected in the Utilization Status popup."""
        return self.new_status_select.input_value()

    def click_status_update_with_empty_note_and_get_toast(self) -> str:
        """Clear the Note, click Update in the Utilization Status popup, return the message shown."""
        self.type_text(self.status_note_field, "", "Utilization Status Note field")
        self.wait_for_toast_to_clear()
        self.click(self.status_update_button, "Utilization Status Update button")
        return self.get_toast_text()

    def mark_asset_damaged(self, serial: str, note: str) -> None:
        """Set the Utilization Status of an asset to DAMAGE (see change_utilization_status)."""
        self.change_utilization_status(serial, "DAMAGE", note)

    def change_utilization_status(self, serial: str, status: str, note: str) -> None:
        """
        Set the Utilization Status of an asset: search the serial, open its popup,
        click Change next to Asset Utilization Status, choose `status`, write the
        note and click Update. Then confirm the success message.
        """
        self.navigate_here()
        self.search_by_serial(serial)
        self.open_asset_popup(serial)
        self.open_status_change()
        action_logger.info(f"Choose Utilization Status: {status}")
        self.new_status_select.select_option(status)
        self.type_text(self.status_note_field, note, "Utilization Status Note field")
        self.wait_for_toast_to_clear()
        self.click(self.status_update_button, "Utilization Status Update button")
        self.verify_toast_text(self.get_toast_text(), STATUS_UPDATED_TOAST, f"changing the Utilization Status to {status}")

    def verify_utilization_statuses(self, expected: dict) -> None:
        """Search each serial of `expected` ({serial: status}) and confirm its Utilization Status. Names every difference."""
        problems = []
        for serial, status in expected.items():
            self.search_by_serial(serial)
            found = self.get_utilization_status(serial) if self.is_serial_listed(serial) else "not listed"
            if found != status:
                problems.append(f"{serial}: expected {status} but found {found}")
        assert not problems, f"The Utilization Statuses are not as expected: {problems}"

    def open_item_change(self) -> None:
        """Click Change next to Item and wait for its small popup."""
        self.click(self.item_change_button, "Item Change button")
        self.wait_until_visible(self.new_item_specification_field, "New Item Specification field")

    def click_item_update_with_empty_specification_and_get_toast(self) -> str:
        """Clear the specification, click Update in the Item popup, return the message shown."""
        self.type_text(self.new_item_specification_field, "", "New Item Specification field")
        self.wait_for_toast_to_clear()
        self.click(self.item_update_button, "Item Update button")
        return self.get_toast_text()

    def close_change_popup(self) -> None:
        """Close the small Change popup without saving."""
        close_button = self.change_popup.locator("button", has_text="Close").first
        self.click(close_button, "Close button of Change popup")
        self.change_popup.wait_for(state="hidden")

    def unlock_measurement(self) -> None:
        """Click Change next to Measurement; the box becomes editable in place."""
        self.click(self.measurement_change_button, "Measurement Change button")
        self.wait_until_visible(self.measurement_update_button, "Measurement Update button")

    def is_measurement_editable(self) -> bool:
        """Return True if the Measurement box can be typed in."""
        return self.measurement_field.is_editable()
