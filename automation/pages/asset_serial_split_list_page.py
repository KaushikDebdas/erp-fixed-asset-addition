"""
AssetSerialSplitListPage: Fixed Asset > Asset Profile > Asset Serial Split
List screen.

Lists the splits a user has made, with their approval status. The Asset Split
No. of a row opens the read-only Asset Split View popup. See
`automation/element_catalog/asset_serial_split_list.md`.
"""
from playwright.sync_api import expect

from pages.asset_split_view_popup import AssetSplitViewPopup
from pages.base_page import OPEN_LIST_ATTEMPTS, BasePage
from utils.logger import action_logger, assertion_logger


class AssetSerialSplitListPage(BasePage):
    """Page object for the Asset Serial Split List screen."""

    def __init__(self, page):
        super().__init__(page)
        # Filters (the view popup has its own #assetSerial, so the filter is found by name)
        self.asset_serial_filter = page.locator('input[name="assetSerial"]')
        self.created_by_filter = page.locator("#createdBy")
        self.approved_by_filter = page.locator("#approvedBy")
        # Magnifier icon next to Created By; the suggestions only open after it is clicked
        self.created_by_icon = self.created_by_filter.locator(
            "xpath=ancestor::div[contains(@class,'form-group')][1]"
        ).locator("i.fa-search")
        # Suggestion list of the employee search
        self.suggestions = page.locator("ul.ui-autocomplete li:visible")
        # Buttons
        self.search_button = page.get_by_role("button", name="Search")
        self.reset_button = page.locator("#resetUpdate")
        # Results grid, the line under it and the Records per page drop-down
        self.results_table = page.locator("#assetSplitList")
        self.entries_info = page.locator("#assetSplitList_info")
        self.records_per_page = page.locator("select[name=assetSplitList_length]")
        # Asset Split View popup
        self.view_popup = AssetSplitViewPopup(page)

    def navigate_here(self) -> None:
        """Open the Asset Serial Split List screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Split List")
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

    def get_grid_text(self) -> str:
        """Return the visible text of the results grid body (rows or the empty message)."""
        return self.results_table.locator("tbody").inner_text()

    def verify_grid_headers(self, expected: list) -> None:
        """Confirm the grid shows exactly these column headings, in order."""
        assertion_logger.info("Verifying the grid column headings")
        found = self.get_grid_headers()
        assert found == expected, f"Expected the column headings {expected} but found {found}."

    def verify_grid_is_empty(self, what_was_searched: str) -> None:
        """Confirm the grid shows the empty message (no row for what was searched)."""
        assertion_logger.info(f"Verifying no rows for {what_was_searched}")
        text = self.get_grid_text()
        assert "No data available in table" in text, (
            f"Expected no rows for {what_was_searched} but the grid shows: {text}"
        )

    # ---- reading a split's row ----------------------------------------------------

    def get_row_status(self, serial: str) -> str:
        """Return the Status of the split row of this serial, or an empty text when it has no row."""
        if self.results_table.locator("tbody tr", has_text=serial).count() == 0:
            return ""
        return self.read_row_values(self.results_table, serial)["Status"]

    def get_split_number(self, serial: str) -> str:
        """Return the Asset Split No. of the row of this serial."""
        return self.read_row_values(self.results_table, serial)["Asset Split No."]

    def verify_row_shows(self, serial: str, expected: dict) -> None:
        """Confirm the row of this serial shows every value in `expected` ({column heading: text})."""
        self.verify_row_values(self.results_table, serial, expected)

    def verify_row_status(self, serial: str, status: str) -> None:
        """Confirm the row of this serial has this Status."""
        assertion_logger.info(f"Verifying the split of {serial} is {status}")
        found = self.get_row_status(serial)
        assert found == status, f"Expected the split of {serial} to be {status} but the list shows '{found}'."

    # ---- the Asset Split View popup -------------------------------------------------

    def open_split_view(self, serial: str) -> None:
        """Click the Asset Split No. of this serial's row and wait for the Asset Split View popup."""
        link = self.results_table.locator("tbody tr", has_text=serial).locator("a").first
        self.click(link, f"Asset Split No. link of {serial}")
        self.view_popup.wait_until_open()

    def verify_popup_shows(self, expected: dict, line_count: int) -> None:
        """Confirm the open popup shows these field values ({field id: text}) and this many split lines."""
        self.view_popup.verify_shows(expected, line_count)

    def close_popup(self) -> None:
        """Close the Asset Split View popup."""
        self.view_popup.close()

    # ---- Created By filter -------------------------------------------------------------

    def pick_created_by(self, typed_text: str, employee_name: str) -> None:
        """
        Type at least 3 characters in Created By, click the magnifier icon
        until the suggestion list shows the employee, then pick that suggestion.
        """
        self.type_text(self.created_by_filter, typed_text, "Created By filter")
        suggestion = self.suggestions.filter(has_text=employee_name).first
        for attempt in range(OPEN_LIST_ATTEMPTS):
            self.click(self.created_by_icon, "Created By search icon")
            if self.is_shown_within(suggestion, f"Suggestion for {employee_name}"):
                break
        self.wait_until_visible(suggestion, f"Suggestion for {employee_name}")
        self.click(suggestion, f"Suggestion for {employee_name}")

    def search_and_wait_for(self, row_text: str) -> None:
        """Click Search and wait until the grid shows a row with `row_text` or the empty message."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()
        self.wait_for_row_or_no_data(self.results_table, row_text)

    def get_column_values(self, heading: str) -> list:
        """Return the text of one column for every row shown (nothing when the grid is empty)."""
        if "No data available in table" in self.get_grid_text():
            return []
        index = self.get_grid_headers().index(heading)
        rows = self.results_table.locator("tbody tr")
        values = []
        for row_number in range(rows.count()):
            cell = rows.nth(row_number).locator("td:visible").nth(index)
            values.append(cell.inner_text().strip())
        return values

    def verify_all_rows_have(self, heading: str, expected: str) -> None:
        """Confirm at least one row is shown and every row has `expected` in this column."""
        assertion_logger.info(f"Verifying every row has {heading} = {expected}")
        values = self.get_column_values(heading)
        assert values, f"Expected rows with {heading} '{expected}' but the grid is empty."
        assert set(values) == {expected}, f"Expected every {heading} to be '{expected}' but found {set(values)}."

    # ---- reset and paging --------------------------------------------------------------

    def reset_filters(self) -> None:
        """Click Reset to clear the filter boxes and reload the grid."""
        self.click(self.reset_button, "Reset button")
        self.wait_for_grid_refresh()

    def verify_filters_are_empty(self) -> None:
        """Confirm the Asset Serial and Created By filter boxes are empty."""
        assertion_logger.info("Verifying the filter boxes are empty")
        expect(self.asset_serial_filter).to_have_value("")
        expect(self.created_by_filter).to_have_value("")

    def choose_records_per_page(self, size: int) -> None:
        """Pick a Records per page value (10, 20, 30, 50 or 100)."""
        action_logger.info(f"Records per page -> {size}")
        self.records_per_page.select_option(str(size))
        self.wait_for_grid_refresh()

    def verify_records_per_page(self, size: int) -> None:
        """Confirm the chosen page size is selected and the grid shows no more rows than that."""
        assertion_logger.info(f"Verifying the grid shows at most {size} rows")
        selected = self.records_per_page.input_value()
        assert selected == str(size), f"Expected Records per page {size} to be selected but found '{selected}'."
        shown = self.results_table.locator("tbody tr").count()
        assert shown <= size, f"Expected at most {size} rows but the grid shows {shown}."
