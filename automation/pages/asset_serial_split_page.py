"""
AssetSerialSplitPage: Fixed Asset > Asset Profile > Asset Serial Split
screen and its Asset Split form.

Lists assets that can be split. Each row has a SPLIT button; it opens the
Asset Split form only for an asset whose Measurement is above zero, otherwise
a message is shown. See `automation/element_catalog/asset_serial_split.md`.

The Split button itself is never clicked here: splitting creates new asset
serials that cannot be undone.
"""
from pages.base_page import BasePage
from utils.logger import action_logger


class AssetSerialSplitPage(BasePage):
    """Page object for the Asset Serial Split screen and its form."""

    def __init__(self, page):
        super().__init__(page)
        # Filter and buttons
        self.asset_serial_filter = page.locator("#assetSerial")
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid
        self.results_table = page.locator("#assetSerialGlobalList")
        # Asset Split form (opens in place of the list)
        self.split_into_field = page.locator("#splitInto")
        self.remarks_field = page.locator("#remarks")
        self.split_button = page.locator("#splitAsset")
        self.back_link = page.get_by_role("link", name="Back")
        self.result_grid = page.locator("#assetSerialSplitList")

    def navigate_here(self) -> None:
        """Open the Asset Serial Split screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Split")
        self.wait_until_visible(self.search_button, "Search button")

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

    def _split_button_for(self, serial: str):
        row = self.results_table.locator("tbody tr", has_text=serial)
        return row.locator("a.btn, button", has_text="SPLIT")

    def has_split_button(self, serial: str) -> bool:
        """Return True if the row for this serial has a SPLIT button."""
        return self._split_button_for(serial).count() > 0

    def click_split_and_get_toast(self, serial: str) -> str:
        """Click SPLIT for this serial and return the message shown (used when the split is refused)."""
        self.wait_for_toast_to_clear()
        self.click(self._split_button_for(serial), f"SPLIT button for {serial}")
        return self.get_toast_text()

    def open_split_form(self, serial: str) -> None:
        """Click SPLIT for this serial and wait for the Asset Split form."""
        self.click(self._split_button_for(serial), f"SPLIT button for {serial}")
        self.wait_until_visible(self.split_into_field, "Split Into field")

    def get_form_value(self, field_id: str) -> str:
        """Return the value of a field on the Asset Split form, e.g. 'measurementFront'."""
        action_logger.info(f"Read value of split form field: {field_id}")
        return self.page.locator(f"input#{field_id}:visible").first.input_value().strip()

    def is_split_into_editable(self) -> bool:
        """Return True if the Split Into box can be typed in."""
        return self.split_into_field.is_editable()

    def get_split_into_value(self) -> str:
        """Return what is typed in the Split Into box."""
        return self.split_into_field.input_value()

    def is_split_button_visible(self) -> bool:
        """Return True if the Split button is shown on the form."""
        return self.split_button.is_visible()

    def get_result_grid_headers(self) -> list:
        """Return the visible column headings of the form's result grid."""
        headers = self.result_grid.locator("thead th:visible").all_inner_texts()
        return [" ".join(h.split()) for h in headers if h.strip()]

    def go_back(self) -> None:
        """Leave the form without splitting."""
        self.click(self.back_link.first, "Back link")
