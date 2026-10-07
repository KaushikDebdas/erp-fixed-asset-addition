"""
AssetTransactionFormPage: the form shared by Asset Assign, Asset Un Assign
and Asset Internal Movement (Fixed Asset > Asset Transaction).

All three screens work the same way: pick an asset (by its serial, or on
Un Assign and Internal Movement by an employee's PIN), add it to the Asset
List, choose the employee in the lower section, then Draft or Submit. The
three small page classes that inherit this one only add the menu link name.
See `automation/element_catalog/asset_assign.md`, `asset_unassign.md` and
`asset_internal_movement.md`.

The search boxes are autocompletes: type, click the small purple search
icon, then click the suggestion. Only the click on the suggestion fills in
the screen.
"""
from pages.base_page import OPEN_LIST_ATTEMPTS, BasePage
from utils.logger import action_logger, assertion_logger


class AssetTransactionFormPage(BasePage):
    """Page object for the Assign / Un Assign / Internal Movement form."""

    # Set by each subclass: the text of the Asset Transaction menu link
    MENU_LINK = ""

    def __init__(self, page):
        super().__init__(page)
        # "Search By" choice (Un Assign and Internal Movement only)
        self.search_by_serial_radio = page.locator("#serialWise")
        self.search_by_employee_pin_radio = page.locator("#employeePinWise")
        # Search by serial
        self.asset_serial_box = page.locator("#assetSerialId")
        self.asset_serial_search_icon = self.asset_serial_box.locator(
            "xpath=following::i[contains(@class,'fa-search')][1]"
        )
        # Search by employee PIN (Un Assign and Internal Movement only)
        self.employee_pin_search_box = page.locator("#employeeByPinId")
        self.employee_pin_search_icon = self.employee_pin_search_box.locator(
            "xpath=following::i[contains(@class,'fa-search')][1]"
        )
        # The suggestion list that every search shows
        self.suggestions = page.locator("ul.ui-autocomplete li:visible")
        # Asset List
        self.add_to_grid_button = page.locator("#addToGrid")
        self.asset_list_table = page.locator("#assetDetailsTable")
        # Lower section: the employee, branch, location and note
        self.employee_box = page.locator("#newEmployeePin")
        self.employee_search_icon = page.locator("#myButtonclickforEmployee .btn")
        self.employee_pin_field = page.locator("#newEmployeeName2")
        self.employee_name_field = page.locator("#newEmployeeName")
        self.branch_select = page.locator("#newBranch")
        self.transaction_date_field = page.locator("#newAssignDate")
        self.building_select = page.locator("#building")
        self.floor_select = page.locator("#floor")
        self.note_field = page.locator("#newRemarks")
        # Buttons
        self.draft_button = page.locator("#draft")
        self.submit_button = page.locator("#save")

    # ---- opening the screen -----------------------------------------------

    def navigate_here(self) -> None:
        """Open this screen via the Asset Transaction menu."""
        self.open_asset_transaction_submenu(self.MENU_LINK)
        self.wait_until_visible(self.asset_serial_box, "Asset Serial box")

    # ---- picking a suggestion -----------------------------------------------

    def _search_and_pick_suggestion(self, search_icon, text: str, what: str) -> None:
        """
        Click a search button until the suggestion list shows `text`, then
        click that suggestion.
        """
        suggestion = self.suggestions.filter(has_text=text).first
        for attempt in range(OPEN_LIST_ATTEMPTS):
            self.click(search_icon, f"{what} search button")
            if self.is_shown_within(suggestion, f"Suggestion for {text}"):
                break
        self.wait_until_visible(suggestion, f"Suggestion for {text}")
        self.click(suggestion, f"Suggestion for {text}")

    # ---- the asset ----------------------------------------------------------

    def select_asset_by_serial(self, serial: str) -> None:
        """Type the serial, click search, click the suggestion; the asset details fill in."""
        self.type_text(self.asset_serial_box, serial, "Asset Serial box")
        self._search_and_pick_suggestion(self.asset_serial_search_icon, serial, "Asset Serial")
        self.page.wait_for_function("document.querySelector('#assetName') && document.querySelector('#assetName').value !== ''")

    def get_value(self, field_id: str) -> str:
        """Return the text of an input or text area on the form, e.g. 'assetName'."""
        action_logger.info(f"Read value of: {field_id}")
        return self.page.locator(f"#{field_id}").first.input_value().strip()

    def get_selected_text(self, select_id: str) -> str:
        """Return the visible text of the option chosen in a drop-down, e.g. 'newBranch'."""
        action_logger.info(f"Read selected option of: {select_id}")
        return self.page.locator(f"#{select_id}").evaluate(
            "select => (select.options[select.selectedIndex] || {}).text || ''"
        ).strip()

    def add_to_grid(self) -> None:
        """Click Add to Grid and wait for the asset to appear in the Asset List."""
        self.click(self.add_to_grid_button, "Add to Grid button")
        real_row = self.asset_list_table.locator("tbody tr").filter(has_not_text="No data available")
        self.wait_until_visible(real_row.first, "Asset List row")

    def get_asset_list_row_text(self, serial: str) -> str:
        """Return the text of the Asset List row for this serial, cells separated by ' | '."""
        row = self.asset_list_table.locator("tbody tr", has_text=serial)
        cells = row.first.locator("td:visible").all_inner_texts()
        return " | ".join(c.strip() for c in cells)

    def get_asset_list_serials(self) -> list:
        """Return the Asset Serial of every row in the Asset List (second visible cell, after SL)."""
        rows = self.asset_list_table.locator("tbody tr").filter(has_not_text="No data available")
        return [rows.nth(i).locator("td:visible").nth(1).inner_text().strip() for i in range(rows.count())]

    # ---- search by employee PIN (Un Assign and Internal Movement) -----------

    def choose_search_by_employee_pin(self) -> None:
        """Switch Search By from Serial to Employee Pin."""
        self.click(self.search_by_employee_pin_radio, "Search By Employee Pin radio")
        self.wait_until_visible(self.employee_pin_search_box, "Employee search box")

    def load_assets_of_employee(self, pin: str) -> None:
        """Search an employee; every asset assigned to them is loaded into the Asset List."""
        self.type_text(self.employee_pin_search_box, pin, "Employee search box")
        self._search_and_pick_suggestion(self.employee_pin_search_icon, pin, "Employee")
        real_row = self.asset_list_table.locator("tbody tr").filter(has_not_text="No data available")
        self.wait_until_visible(real_row.first, "Asset List row")

    # ---- the employee in the lower section ---------------------------------

    def select_employee(self, pin: str) -> None:
        """Type the PIN, click search, click the suggestion; employee PIN and name fill in."""
        self.type_text(self.employee_box, pin, "Employee PIN Search box")
        self._search_and_pick_suggestion(self.employee_search_icon, pin, "Employee PIN")
        self.page.wait_for_function("document.querySelector('#newEmployeeName') && document.querySelector('#newEmployeeName').value !== ''")

    def get_employee_pin(self) -> str:
        """Return the Employee PIN filled in after selecting an employee."""
        return self.employee_pin_field.input_value().strip()

    def get_employee_name(self) -> str:
        """Return the Employee Name filled in after selecting an employee."""
        return self.employee_name_field.input_value().strip()

    def get_branch_name(self) -> str:
        """Return the Branch Name; it is always the logged-in user's branch."""
        return self.get_selected_text("newBranch")

    def get_transaction_date(self) -> str:
        """Return the read-only transaction (business) date shown on the form, dd-mm-yyyy."""
        return self.transaction_date_field.input_value().strip()

    def select_building_and_first_floor(self, building: str) -> str:
        """Choose a building, then its first real floor; return the floor's name."""
        action_logger.info(f"Select: Building -> {building}")
        self.building_select.select_option(label=building)
        self.page.wait_for_function("document.querySelectorAll('#floor option').length > 1")
        self.floor_select.select_option(index=1)
        return self.get_selected_text("floor")

    def enter_note(self, note: str) -> None:
        """Type the Note/Remarks text."""
        self.type_text(self.note_field, note, "Note/Remarks field")

    # ---- saving ---------------------------------------------------------------

    def draft_and_get_toast(self) -> str:
        """Click Draft and return the message shown."""
        self.wait_for_toast_to_clear()
        self.click(self.draft_button, "Draft button")
        return self.get_toast_text()

    def submit_and_get_toast(self) -> str:
        """Click Submit and return the message shown."""
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        return self.get_toast_text()

    def click_draft_without_waiting_for_toast(self) -> None:
        """Click Draft when no message is expected (a required field is empty)."""
        self.click(self.draft_button, "Draft button")

    def is_required_message_visible(self) -> bool:
        """Return True if the inline 'This field is required' message is on screen."""
        return self.page.get_by_text("This field is required").first.is_visible()

    # ---- filling the whole form ----------------------------------------------

    def fill_form(self, serial: str, employee_search: str, note: str, building: str = "") -> str:
        """
        Fill the form the way a user does: select the asset, add it to the
        grid, select the employee, choose the building (only when `building`
        is given, for Internal Movement) and type the note. Returns the
        transaction date shown on the form as dd/mm/yyyy, which the Details
        popup shows in the same format.
        """
        self.select_asset_by_serial(serial)
        self.add_to_grid()
        self.select_employee(employee_search)
        if building != "":
            self.select_building_and_first_floor(building)
        self.enter_note(note)
        return self.get_transaction_date().replace("-", "/")

    def get_floor(self) -> str:
        """Return the floor chosen on the form (Internal Movement)."""
        return self.get_selected_text("floor")

    def draft_and_verify_toast(self, expected_toast: str) -> None:
        """Click Draft and confirm the message shown is exactly `expected_toast`."""
        toast = self.draft_and_get_toast()
        self.verify_toast_text(toast, expected_toast, "Draft on the transaction form")

    # ---- checks ---------------------------------------------------------------

    def verify_form_shows(self, serial: str, expected: dict) -> None:
        """
        Confirm the form shows the selected asset: the Asset Serial box starts
        with `serial`, and every field in `expected` ({field id: text}) holds
        that text. Names every difference.
        """
        assertion_logger.info(f"Verifying the form shows asset {serial}")
        problems = []
        box_text = self.get_value("assetSerialId")
        if not box_text.startswith(serial):
            problems.append(f"assetSerialId: expected a text starting with '{serial}' but found '{box_text}'")
        for field_id, wanted in expected.items():
            found = self.get_value(field_id)
            if found != wanted:
                problems.append(f"{field_id}: expected '{wanted}' but found '{found}'")
        assert not problems, f"The form does not show asset {serial} as expected: {problems}"

    def verify_fields_read_only(self, field_ids: list) -> None:
        """Confirm none of the fields can be typed in. Names every field that can."""
        assertion_logger.info("Verifying the auto-filled fields are read-only")
        editable = []
        for field_id in field_ids:
            if self.page.locator(f"#{field_id}").first.is_editable():
                editable.append(field_id)
        assert not editable, f"Expected these fields to be read-only but they can be edited: {editable}"

    def verify_asset_in_list(self, serial: str, assign_status: str = "") -> None:
        """
        Confirm the Asset List holds `serial`. When `assign_status` is given,
        the row must also show that Assign Status.
        """
        assertion_logger.info(f"Verifying the Asset List holds {serial}")
        serials = self.get_asset_list_serials()
        assert serial in serials, f"Expected {serial} in the Asset List but it holds {serials}."
        if assign_status != "":
            row_text = self.get_asset_list_row_text(serial)
            assert assign_status in row_text, (
                f"Expected the Asset List row of {serial} to show {assign_status} but it shows '{row_text}'."
            )

    def verify_asset_details_cleared(self) -> None:
        """Confirm the top section is empty again (it clears after Add to Grid)."""
        found = self.get_value("assetName")
        assert found == "", f"Expected the asset details to be cleared after Add to Grid but Asset Item Name is '{found}'."

    def verify_employee_selected(self, pin: str, name: str) -> None:
        """Confirm the employee's PIN and name filled in after selecting the employee."""
        assertion_logger.info(f"Verifying employee {pin} is selected")
        found = (self.get_employee_pin(), self.get_employee_name())
        assert found == (pin, name), f"Expected employee PIN and name {(pin, name)} but found {found}."

    def verify_branch(self, branch: str) -> None:
        """Confirm Branch Name shows the branch the user is logged in to."""
        found = self.get_branch_name()
        assert found == branch, f"Expected Branch Name '{branch}' but found '{found}'."

    def verify_required_message_shown(self) -> None:
        """Confirm the 'This field is required' message is on screen."""
        assertion_logger.info("Verifying the 'This field is required' message")
        assert self.is_required_message_visible(), (
            "Expected the 'This field is required' message after Draft without an employee but it was not shown."
        )

    def verify_search_by_options(self) -> None:
        """Confirm Search By offers Serial (selected) and Employee Pin (not selected)."""
        assertion_logger.info("Verifying the Search By choices")
        assert self.search_by_serial_radio.is_visible(), "Expected the Search By Serial choice to be shown."
        assert self.search_by_employee_pin_radio.is_visible(), "Expected the Search By Employee Pin choice to be shown."
        assert self.search_by_serial_radio.is_checked(), "Expected Search By Serial to be selected by default."
        assert not self.search_by_employee_pin_radio.is_checked(), (
            "Expected Search By Employee Pin not to be selected by default."
        )
