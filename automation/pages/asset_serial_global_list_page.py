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
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Position of a cell in a result row (0-based; a hidden ID column comes first)
ASSIGN_STATUS_COLUMN_INDEX = 9
UTILIZATION_STATUS_COLUMN_INDEX = 10

# Tab name -> the id of the tab's content pane
TAB_PANES = {
    "Details": "#tab_details",
    "Depreciation History": "#tab_dep_history",
    "Revaluation History": "#tab_rev_history",
    "Transaction History": "#tab_transfer_history",
    "Expenditure": "#tab_expenditure",
    "Disposal Info": "#tab_disposal_info",
    "Attachment": "#tab_attachment",
}


class AssetSerialGlobalListPage(BasePage):
    """Page object for the Asset Serial Global List screen and its detail popup."""

    def __init__(self, page):
        super().__init__(page)
        # Filters
        self.asset_serial_filter = page.locator("#assetSerial")
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

    # ---- search -----------------------------------------------------------

    def navigate_here(self) -> None:
        """Open the Asset Serial Global List screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Global List")
        self.wait_until_visible(self.search_button, "Search button")

    def search_by_serial(self, serial: str) -> None:
        """Filter by Asset Serial and wait for the result (or the empty message)."""
        self.type_text(self.asset_serial_filter, serial, "Asset Serial filter")
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()
        self.wait_for_row_or_no_data(self.results_table, serial)

    def filter_by_utilization_status(self, status: str) -> None:
        """Pick an Asset Utilization Status in the filter (does not search yet)."""
        action_logger.info(f"Filter: Asset Utilization Status -> {status}")
        self.utilization_status_filter.select_option(status)

    def filter_by_assign_status(self, status: str) -> None:
        """Pick an Assign Status (ASSIGNED / UNASSIGNED) in the filter (does not search yet)."""
        action_logger.info(f"Filter: Assign Status -> {status}")
        self.assign_status_filter.select_option(status)

    def is_serial_listed(self, serial: str) -> bool:
        """Return True if a result row for this Asset Serial is shown."""
        return self.results_table.locator("tbody tr", has_text=serial).count() > 0

    def _row_cell(self, serial: str, column_index: int) -> str:
        row = self.results_table.locator("tbody tr", has_text=serial)
        return row.locator("td").nth(column_index).inner_text().strip()

    def get_utilization_status(self, serial: str) -> str:
        """Return the Utilization Status shown in the row for this serial."""
        return self._row_cell(serial, UTILIZATION_STATUS_COLUMN_INDEX)

    def get_assign_status(self, serial: str) -> str:
        """Return the Assign Status shown in the row for this serial."""
        return self._row_cell(serial, ASSIGN_STATUS_COLUMN_INDEX)

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

    def close_popup(self) -> None:
        """Close the Asset Profile Details popup."""
        self.click(self.popup_close_button, "Close button of Asset Profile Details popup")

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
