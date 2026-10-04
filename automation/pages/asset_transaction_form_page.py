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
from pages.base_page import BasePage
from utils.logger import action_logger


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
        Click a search button and click the suggestion that contains `text`.
        If the suggestion list does not open, the search button is clicked
        again (up to three times) before giving up.
        """
        suggestion = self.suggestions.filter(has_text=text).first
        for attempt in range(3):
            self.click(search_icon, f"{what} search button")
            try:
                suggestion.wait_for(state="visible", timeout=8000)
                break
            except Exception:
                action_logger.info(f"No suggestion for {text} yet, trying again")
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
