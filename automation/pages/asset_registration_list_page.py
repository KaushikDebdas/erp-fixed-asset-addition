"""
AssetRegistrationListPage: Fixed Asset > Registration > Asset Registration
List screen.

Shows every AAQ registration (Draft or Submitted) created by the current
user's branch. Used here to find the registration just created on the AAQ
form (which does not show its own Registration Number after Draft), and to
reopen a Draft record so it can be Submitted.
"""
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Column order of the results grid, 0-based, used to read the Status cell
# of a specific row (see automation/element_catalog/asset_registration_list.md)
STATUS_COLUMN_INDEX = 9


class AssetRegistrationListPage(BasePage):
    """Page object for the Asset Registration List screen."""

    def __init__(self, page):
        super().__init__(page)
        # Status filter dropdown: -Select Status-, PENDING, APPROVED, REJECTED, DRAFT, SENDBACK
        self.status_filter = page.locator("#status")
        # Registration Number filter (free text)
        self.registration_id_filter = page.locator("#registrationId")
        # Runs the filter
        self.search_button = page.get_by_role("button", name=" Search")
        # Results grid
        self.results_table = page.locator("table")
        # Registration Type filter: MRR, AAQ, LEASE
        self.registration_type_filter = page.locator("#registrationType")
        # Vendor/Supplier/Lessor Name filter (free text)
        self.vendor_filter = page.locator("#supplierName")
        # MRR Number filter (free text)
        self.mrr_filter = page.locator("#referenceNo")
        # Created By filter; starts with the logged-in user's name
        self.created_by_filter = page.locator("#createdBy")
        # Project Name & Number filter
        self.project_filter = page.locator("#projectId")
        # Read-only date filters, filled through the calendar pop-up
        self.registration_from_date = page.locator("#registrationFromDate")
        self.registration_to_date = page.locator("#registrationToDate")
        self.approve_from_date = page.locator("#approveFromDate")
        self.approve_to_date = page.locator("#approveToDate")
        # Clears the filter boxes (it does not run the search again)
        self.reset_button = page.locator("#reset")
        # The results grid itself, and the line under it, e.g. "Showing 1 to 10 of 124 entries"
        self.grid = page.locator("#assetRegistrationList")
        self.entries_info = page.locator(".dataTables_info")
        # Records per page dropdown: 10, 20, 30, 50, 100
        self.page_size_select = page.locator("select[name=assetRegistrationList_length]")
        # Asset Registration View popup opened from a Registration Number link
        self.modal = page.locator("#commonModal")
        self.modal_close_button = page.get_by_role("button", name="Close")

    def navigate_here(self) -> None:
        """Open the Asset Registration List screen via the left/top menu."""
        self.open_registration_submenu("Asset Registration List")
        self.wait_until_visible(self.search_button, "Search button")

    def filter_by_status(self, status: str) -> None:
        """Set the Status filter (e.g. 'DRAFT', 'PENDING') and run the search."""
        action_logger.info(f"Filter: Status -> {status}")
        self.status_filter.select_option(status)
        self.search()

    def filter_by_registration_number(self, registration_number: str) -> None:
        """Filter the grid down to one Registration Number and run the search."""
        self.type_text(
            self.registration_id_filter, registration_number, "Registration Number filter"
        )
        self.search()

    def search(self) -> None:
        """Click Search and wait until the grid shows the result."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_to_reload(self.entries_info)

    def filter_by_registration_type(self, registration_type: str) -> None:
        """Set the Registration Type filter (MRR, AAQ or LEASE) and search."""
        action_logger.info(f"Filter: Registration Type -> {registration_type}")
        self.registration_type_filter.select_option(registration_type)
        self.search()

    def filter_by_project(self, project: str) -> None:
        """Set the Project Name & Number filter and search."""
        action_logger.info(f"Filter: Project -> {project}")
        self.project_filter.select_option(label=project)
        self.search()

    def filter_by_vendor(self, vendor_name: str) -> None:
        """Type into the Vendor/Supplier/Lessor Name filter and search."""
        self.type_text(self.vendor_filter, vendor_name, "Vendor/Supplier/Lessor Name filter")
        self.search()

    def clear_created_by(self) -> None:
        """Empty the Created By filter, so records made by every user are listed after a search."""
        self.type_text(self.created_by_filter, "", "Created By filter")

    def pick_date(self, date_field, date_text: str) -> None:
        """
        Set a read-only date filter by clicking its day in the calendar pop-up.
        `date_text` is dd/mm/yyyy. The pop-up opens on the current business
        month, so the date must be in that month.
        """
        day = str(int(date_text.split("/")[0]))
        self.click(date_field, f"Date filter {date_text}")
        day_cell = self.page.locator(".datepicker-dropdown:visible td.day:not(.old):not(.new)")
        self.click(day_cell.get_by_text(day, exact=True), f"Calendar day {day}")

    def set_registration_dates(self, from_date: str, to_date: str) -> None:
        """Set the Registration From Date and Registration To Date."""
        self.pick_date(self.registration_from_date, from_date)
        self.pick_date(self.registration_to_date, to_date)

    def set_approve_dates(self, from_date: str, to_date: str) -> None:
        """Set the Approve From Date and Approve To Date."""
        self.pick_date(self.approve_from_date, from_date)
        self.pick_date(self.approve_to_date, to_date)

    def reset_filters(self) -> None:
        """Click Reset, which empties every filter box."""
        self.click(self.reset_button, "Reset button")

    def read_headers(self) -> list:
        """Return the grid's column headings, in order."""
        return [h.strip() for h in self.grid.locator("thead th").all_inner_texts()]

    def read_filter_options(self, select) -> list:
        """Return the options of a filter dropdown."""
        return [o.strip() for o in select.locator("option").all_inner_texts()]

    def grid_is_empty(self) -> bool:
        """Return True if the grid shows "No data available in table"."""
        return self.grid.locator("tbody tr", has_text="No data available in table").count() > 0

    def read_column(self, heading: str) -> list:
        """Return what every row on this page shows in the column with this heading."""
        index = self.read_headers().index(heading) + 1
        if self.grid_is_empty():
            return []
        return [c.strip() for c in self.grid.locator(f"tbody tr td:nth-child({index})").all_inner_texts()]

    def read_total_entries(self) -> int:
        """Return N from the line "Showing 1 to 10 of N entries" (0 when the grid is empty)."""
        text = self.entries_info.inner_text()
        if " of " not in text:
            return 0
        return int(text.split(" of ")[1].split(" ")[0].replace(",", ""))

    def set_page_size(self, size: int) -> None:
        """Choose how many records the grid shows per page."""
        action_logger.info(f"Select: Records per page -> {size}")
        total_entries = self.read_total_entries()
        self.page_size_select.select_option(str(size))
        self.wait_for_rows_per_page(self.grid.locator("tbody tr"), size, total_entries)

    def go_to_page(self, page_number: int) -> None:
        """Click a page number under the grid and wait until that page is shown."""
        size = int(self.page_size_select.input_value())
        button = self.page.locator(".paginate_button", has_text=str(page_number)).first
        self.click(button, f"Page {page_number} button")
        self.wait_for_page_shown(self.entries_info, page_number, size)

    def open_registration_popup(self, registration_number: str) -> None:
        """Click a Registration Number link to open its Asset Registration View popup."""
        link = self.grid.get_by_role("link", name=registration_number, exact=True)
        self.click(link, f"Registration Number {registration_number} link")
        self.wait_until_visible(self.modal, "Asset Registration View popup")

    def read_popup_text(self) -> str:
        """Return everything the open popup shows, including what is typed in its boxes."""
        text = self.get_text(self.modal, "Asset Registration View popup")
        values = self.modal.evaluate(
            "m => Array.from(m.querySelectorAll('input, textarea, select')).map(e => e.value).join(' ')"
        )
        return f"{text} {values}"

    def close_popup(self) -> None:
        """Close the Asset Registration View popup."""
        self.click(self.modal_close_button, "Close button")

    def is_registration_listed(self, registration_number: str) -> bool:
        """Return True if a grid row for this Registration Number is shown."""
        row = self._row_for_registration(registration_number)
        try:
            row.first.wait_for(state="visible", timeout=10000)
        except Exception:
            return False
        return True

    def _row_for_registration(self, registration_number: str):
        """Return the <tr> locator for a given Registration Number."""
        return self.results_table.locator("tr", has_text=registration_number)

    def get_newest_registration_number(self) -> str:
        """
        Return the highest Registration Number currently shown in the grid.

        The AAQ form does not display the Registration Number it just
        created (Draft resets the form to blank), and this list has no
        filter that uniquely identifies "the record this test just made".
        Registration Numbers are issued as increasing integers, so after
        filtering to this run's own records (Created By defaults to the
        logged-in user), the highest number in the grid is the one just
        created.
        """
        number_cells = self.results_table.locator("tbody tr td:nth-child(2)")
        no_data_row = self.results_table.locator("tbody tr", has_text="No data available in table")
        # Wait until the grid shows either a number or the "No data" row
        number_cells.first.or_(no_data_row.first).wait_for(state="visible")
        if self.grid_is_empty():
            raise AssertionError("Expected at least one registration row but the grid is empty.")
        count = number_cells.count()
        numbers = [int(number_cells.nth(i).inner_text().strip()) for i in range(count)]
        newest = str(max(numbers))
        action_logger.info(f"Newest registration number in grid: {newest}")
        return newest

    def verify_status(self, registration_number: str, expected_status: str) -> None:
        """Confirm the row for `registration_number` shows `expected_status`."""
        row = self._row_for_registration(registration_number)
        actual_status = row.locator("td").nth(STATUS_COLUMN_INDEX).inner_text().strip()
        assertion_logger.info(
            f"Verifying Registration {registration_number} has Status {expected_status}"
        )
        assert actual_status == expected_status, (
            f"Expected Registration {registration_number} to have Status "
            f"'{expected_status}' but found '{actual_status}'."
        )

    # ------------------------------------------------------------------
    # Filter boxes: typing, choosing and reading
    # ------------------------------------------------------------------

    def select_status(self, status: str) -> None:
        """Choose a Status in the Status filter without running the search."""
        action_logger.info(f"Select: Status -> {status}")
        self.status_filter.select_option(status)

    def select_registration_type(self, registration_type: str) -> None:
        """Choose a Registration Type in its filter without running the search."""
        action_logger.info(f"Select: Registration Type -> {registration_type}")
        self.registration_type_filter.select_option(registration_type)

    def type_registration_number(self, text: str) -> None:
        """Type into the Registration Number filter without running the search."""
        self.type_text(self.registration_id_filter, text, "Registration Number filter")

    def type_vendor(self, text: str) -> None:
        """Type into the Vendor/Supplier/Lessor Name filter without running the search."""
        self.type_text(self.vendor_filter, text, "Vendor/Supplier/Lessor Name filter")

    def type_mrr_number(self, text: str) -> None:
        """Type into the MRR Number filter without running the search."""
        self.type_text(self.mrr_filter, text, "MRR Number filter")

    def filter_by_mrr_number(self, mrr_number: str) -> None:
        """Type an MRR Number into its filter and run the search."""
        self.type_mrr_number(mrr_number)
        self.search()

    def read_status_filter(self) -> str:
        """Return the value chosen in the Status filter ('' when nothing is chosen)."""
        return self.status_filter.input_value()

    def read_registration_type_filter(self) -> str:
        """Return the value chosen in the Registration Type filter."""
        return self.registration_type_filter.input_value()

    def read_registration_number_filter(self) -> str:
        """Return the text in the Registration Number filter."""
        return self.registration_id_filter.input_value()

    def read_vendor_filter(self) -> str:
        """Return the text in the Vendor/Supplier/Lessor Name filter."""
        return self.vendor_filter.input_value()

    def read_created_by(self) -> str:
        """Return the text in the Created By filter."""
        return self.created_by_filter.input_value()

    def read_entries_info(self) -> str:
        """Return the line under the grid, e.g. "Showing 1 to 10 of 124 entries"."""
        return self.entries_info.inner_text()

    def _read_filter_value(self, filter_name: str) -> str:
        """Return the current value of a filter box, found by its name (e.g. "Status")."""
        if filter_name == "Status":
            return self.read_status_filter()
        if filter_name == "Registration Type":
            return self.read_registration_type_filter()
        if filter_name == "Registration Number":
            return self.read_registration_number_filter()
        if filter_name == "Vendor":
            return self.read_vendor_filter()
        if filter_name == "Created By":
            return self.read_created_by()
        raise AssertionError(f"Unknown filter name '{filter_name}'.")

    def read_options_of(self, select_name: str) -> list:
        """Return the options of a dropdown found by name: "Status", "Registration Type" or "Records per page"."""
        if select_name == "Status":
            return self.read_filter_options(self.status_filter)
        if select_name == "Registration Type":
            return self.read_filter_options(self.registration_type_filter)
        if select_name == "Records per page":
            return self.read_filter_options(self.page_size_select)
        raise AssertionError(f"Unknown dropdown name '{select_name}'.")

    # ------------------------------------------------------------------
    # Values read from the grid
    # ------------------------------------------------------------------

    def read_first_value(self, heading: str) -> str:
        """Return what the first row shows in the column with this heading ('' when the grid is empty)."""
        values = self.read_column(heading)
        if len(values) == 0:
            return ""
        return values[0]

    def read_first_filled_value(self, heading: str) -> str:
        """Return the first non-empty value in the column with this heading ('' when every cell is empty)."""
        for value in self.read_column(heading):
            if value != "":
                return value
        return ""

    # ------------------------------------------------------------------
    # Checks: each one raises AssertionError saying what was expected and found
    # ------------------------------------------------------------------

    def verify_headers(self, expected_headers: list) -> None:
        """Confirm the grid's column headings are exactly `expected_headers`, in order."""
        found = self.read_headers()
        assertion_logger.info("Verifying the grid column headings")
        assert found == expected_headers, (
            f"Expected column headings {expected_headers} but found {found}."
        )

    def verify_filter_options(self, select_name: str, expected_options: list) -> None:
        """Confirm a dropdown ("Status", "Registration Type" or "Records per page") offers exactly `expected_options`."""
        found = self.read_options_of(select_name)
        assertion_logger.info(f"Verifying the {select_name} options")
        assert found == expected_options, (
            f"Expected {select_name} options {expected_options} but found {found}."
        )

    def verify_created_by_contains(self, text: str) -> None:
        """Confirm the Created By filter holds `text` (e.g. the logged-in user's pin)."""
        found = self.read_created_by()
        assertion_logger.info(f"Verifying Created By contains {text}")
        assert text in found, f"Expected Created By to contain '{text}' but found '{found}'."

    def verify_filters_are_empty(self, filter_names: list) -> None:
        """Confirm each named filter box ("Status", "Registration Type", "Registration Number", "Vendor", "Created By") is empty."""
        assertion_logger.info(f"Verifying these filters are empty: {filter_names}")
        for filter_name in filter_names:
            found = self._read_filter_value(filter_name)
            assert found == "", f"Expected the {filter_name} filter to be empty but found '{found}'."

    def verify_newest_first(self) -> None:
        """Confirm the Registration Numbers on this page go from the highest to the lowest."""
        numbers = []
        for text in self.read_column("Registration Number"):
            numbers.append(int(text))
        assertion_logger.info("Verifying registrations are listed newest first")
        for i in range(len(numbers) - 1):
            assert numbers[i] >= numbers[i + 1], (
                f"Expected newest first (high to low) but found {numbers}."
            )

    def verify_all_rows_have(self, heading: str, expected_value: str) -> None:
        """
        Confirm every row shows `expected_value` in the column `heading`.
        A grid with no rows passes, because nothing contradicts the filter.
        """
        found = self.read_column(heading)
        assertion_logger.info(f"Verifying every row has {heading} {expected_value}")
        for value in found:
            assert value == expected_value, (
                f"Expected only {heading} '{expected_value}' but found '{value}' in {found}."
            )

    def verify_rows_listed_and_all_have(self, heading: str, expected_value: str) -> None:
        """Confirm the grid has rows and every row shows `expected_value` in the column `heading`."""
        self.verify_grid_has_rows(f"rows with {heading} '{expected_value}'")
        self.verify_all_rows_have(heading, expected_value)

    def verify_grid_has_rows(self, what_was_expected: str) -> None:
        """Confirm the grid is not empty; `what_was_expected` names what should be listed."""
        assertion_logger.info(f"Verifying the grid lists {what_was_expected}")
        assert not self.grid_is_empty(), f"Expected {what_was_expected} but the grid is empty."

    def verify_grid_is_empty(self, what_was_filtered: str) -> None:
        """Confirm the grid shows "No data available in table"; `what_was_filtered` names the filter used."""
        assertion_logger.info(f"Verifying the grid is empty for {what_was_filtered}")
        assert self.grid_is_empty(), (
            f"Expected the grid to be empty for {what_was_filtered} but found rows: "
            f"{self.read_column('Registration Number')}."
        )

    def verify_column_equals(self, heading: str, expected_values: list) -> None:
        """Confirm the column `heading` shows exactly `expected_values`, row by row."""
        found = self.read_column(heading)
        assertion_logger.info(f"Verifying column {heading}")
        assert found == expected_values, (
            f"Expected column {heading} to be {expected_values} but found {found}."
        )

    def verify_total_entries_above(self, smaller_total: int) -> None:
        """Confirm the total in "Showing 1 to 10 of N entries" is bigger than `smaller_total`."""
        found = self.read_total_entries()
        assertion_logger.info(f"Verifying more than {smaller_total} registrations are listed")
        assert found > smaller_total, (
            f"Expected more than {smaller_total} registrations but found {found}."
        )

    def verify_rows_per_page(self, size: int) -> None:
        """Confirm the grid shows `size` rows and the line under it starts "Showing 1 to <size> of"."""
        row_count = len(self.read_column("Registration Number"))
        info = self.read_entries_info()
        assertion_logger.info(f"Verifying the grid shows {size} rows")
        assert row_count == size, f"Expected {size} rows on the page but found {row_count}."
        assert info.startswith(f"Showing 1 to {size} of"), (
            f"Expected the line under the grid to start 'Showing 1 to {size} of' but found '{info}'."
        )

    def verify_second_page_continues(self, first_page_numbers: list) -> None:
        """
        Confirm page 2 is shown ("Showing 11 to 20 of") and holds different,
        older registrations than `first_page_numbers` (the numbers read on page 1).
        """
        info = self.read_entries_info()
        assertion_logger.info("Verifying page 2 continues the list")
        assert info.startswith("Showing 11 to 20 of"), (
            f"Expected the line under the grid to start 'Showing 11 to 20 of' but found '{info}'."
        )
        lowest_on_first_page = int(first_page_numbers[0])
        for text in first_page_numbers:
            lowest_on_first_page = min(lowest_on_first_page, int(text))
        for text in self.read_column("Registration Number"):
            assert int(text) < lowest_on_first_page, (
                f"Expected page 2 to show registrations older than {lowest_on_first_page} "
                f"but found {text}. Page 1 had {first_page_numbers}."
            )

    def verify_popup_contains(self, expected_values: list) -> None:
        """Confirm the open popup shows every value in `expected_values`."""
        popup = self.read_popup_text()
        assertion_logger.info("Verifying the popup shows every entered value")
        missing = []
        for value in expected_values:
            if value not in popup:
                missing.append(value)
        assert len(missing) == 0, f"The popup is missing {missing}. Popup text: {popup}"

    def open_registration(self, registration_number: str) -> None:
        """Click the Registration Number link to open/reopen that record."""
        link = self.results_table.get_by_role("link", name=registration_number, exact=True)
        self.click(link, f"Registration Number {registration_number} link")
        self.wait_for_page_load()
        # The saved values are filled into the form after it appears, so
        # wait until the Project has its saved value before going on
        self.page.wait_for_function(
            "document.querySelector('#project') && document.querySelector('#project').value"
        )
