"""
AssetWriteOffPage: Asset Write-off (Fixed Asset > Asset Disposal > Asset Write-off).

Writes off assets whose Utilization Status is no longer IN_USE (for example
DAMAGE). Pick a project, search an asset serial, add a note, Add to Grid, then
Draft or Submit. See `automation/element_catalog/asset_write_off.md`.

The Asset Serial box only offers assets of the chosen project that already have
a status other than IN_USE, so set the status first (Asset Serial Global List).
"""
from pages.base_page import BasePage
from test_data.toast_messages import WRITE_OFF_DRAFT_TOAST, WRITE_OFF_SUBMIT_TOAST
from utils.logger import action_logger, assertion_logger


class AssetWriteOffPage(BasePage):
    """Page object for the Asset Write-off screen. Asset Sale inherits it and changes the three names below."""

    # Link in the Asset Disposal menu, and the toasts of Draft and Submit
    MENU_LINK = "Asset Write-off"
    DRAFT_TOAST = WRITE_OFF_DRAFT_TOAST
    SUBMIT_TOAST = WRITE_OFF_SUBMIT_TOAST

    def __init__(self, page):
        super().__init__(page)
        # Project drop-down (the real <select>; the Asset Serial box lists the assets of this project)
        self.project_select = page.locator("#project")
        # Asset Serial: a search drop-down. Click it, type 3 or more letters, click a result.
        self.asset_serial_box = page.locator("#s2id_asset .select2-choice")
        self.asset_serial_search_field = page.locator(".select2-drop-active input.select2-input")
        self.asset_serial_results = page.locator(".select2-drop-active .select2-results li")
        # Read-only fields filled in after an asset is picked
        self.asset_name_field = page.locator("#assetName")
        self.utilization_status_field = page.locator("#disposalType")
        self.written_down_value_field = page.locator("#writtenDownValue")
        # Note (maximum 200 characters)
        self.note_field = page.locator("#remarks")
        # Adds the picked asset to the grid below the form
        self.add_to_grid_button = page.locator("#addToGrid")
        self.asset_list_table = page.locator("#assetDetailsTable")
        # Save the write-off
        self.draft_button = page.locator("#draft")
        self.submit_button = page.locator("#save")

    # ---- opening the screen -----------------------------------------------

    def navigate_here(self) -> None:
        """Open this screen via the Asset Disposal menu."""
        self.open_asset_disposal_submenu(self.MENU_LINK)
        self.wait_until_visible(self.project_select.locator("xpath=.."), "Project drop-down")

    # ---- filling the form -------------------------------------------------

    def select_project(self, project: str) -> None:
        """Choose the project by its visible text, e.g. "[015] Microfinance (Dabi)"."""
        action_logger.info(f"Select project: {project}")
        self.project_select.select_option(label=project)

    def select_asset(self, search_text: str, serial: str) -> None:
        """
        Search the Asset Serial box with `search_text` (3 or more letters, e.g.
        the item name "Cabinet") and click the result for `serial`. The asset's
        name and Utilization Status then fill in.
        """
        self.click(self.asset_serial_box, "Asset Serial box")
        self.type_text(self.asset_serial_search_field, search_text, "Asset Serial search box")
        result = self.asset_serial_results.filter(has_text=serial)
        self.wait_until_visible(result.first, f"Asset Serial result {serial}")
        self.click_asset_result(serial)

    def click_asset_result(self, serial: str) -> None:
        """Click the open Asset Serial result for `serial` and wait for the asset's details to fill in."""
        result = self.asset_serial_results.filter(has_text=serial)
        self.click(result.first, f"Asset Serial result {serial}")
        self.page.wait_for_function("document.querySelector('#assetName') && document.querySelector('#assetName').value !== ''")

    def get_utilization_status(self) -> str:
        """Return the Utilization Status shown for the picked asset (it is the write-off reason)."""
        return self.utilization_status_field.input_value().strip()

    def get_written_down_value(self) -> float:
        """Return the Written Down Value shown for the picked asset."""
        return float(self.written_down_value_field.input_value().strip())

    def enter_note(self, note: str) -> None:
        """Type the write-off note."""
        self.type_text(self.note_field, note, "Note field")

    def add_to_grid(self) -> None:
        """Click Add to Grid and wait for the asset to appear in the grid."""
        self.click(self.add_to_grid_button, "Add to Grid button")
        real_row = self.asset_list_table.locator("tbody tr").filter(has_not_text="No data available")
        self.wait_until_visible(real_row.first, "Asset write-off grid row")

    def get_grid_row_values(self, serial: str) -> list:
        """Return the visible cells of the grid row for this serial, in column order."""
        row = self.asset_list_table.locator("tbody tr", has_text=serial)
        self.wait_until_visible(row.first, f"write-off grid row of {serial}")
        return [cell.strip() for cell in row.first.locator("td:visible").all_inner_texts()]

    def verify_grid_row(self, serial: str, item_name: str, utilization_status: str, note: str) -> None:
        """Confirm the grid row of this serial shows the item name, Utilization Status and note; names each difference."""
        assertion_logger.info(f"Verifying the write-off grid row of {serial}")
        cells = self.get_grid_row_values(serial)
        expected = {"item name": item_name, "utilization status": utilization_status, "note": note}
        problems = []
        for name, value in expected.items():
            if value not in cells:
                problems.append(f"{name} '{value}' is not in the row {cells}")
        assert not problems, f"The write-off grid row of {serial} is not as expected: {problems}"

    # ---- saving -----------------------------------------------------------

    def draft_and_verify(self) -> None:
        """Click Draft and confirm the success message."""
        self.wait_for_toast_to_clear()
        self.click(self.draft_button, "Draft button")
        self.verify_toast_text(self.get_toast_text(), self.DRAFT_TOAST, "Draft")

    def submit_and_verify(self) -> None:
        """Click Submit and confirm the success message."""
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        self.verify_toast_text(self.get_toast_text(), self.SUBMIT_TOAST, "Submit")

    def verify_grid_is_empty(self) -> None:
        """Confirm the grid is empty again, which is how the screen looks after a saved write-off."""
        assertion_logger.info("Verifying the write-off grid is empty")
        empty_row = self.asset_list_table.locator("tbody tr", has_text="No data available")
        self.wait_until_visible(empty_row, "empty write-off grid message")
