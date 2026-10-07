"""
AssetRegistrationApprovalListPage: Fixed Asset > Registration > Asset
Registration Approval List screen.

Used to review a submitted (PENDING) AAQ registration in detail and to
approve it. See
automation/element_catalog/asset_registration_approval_list.md for the
full field list, the popup structure, and the known staging data issue
that currently blocks Approve from succeeding.
"""
import re

from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger

# Position of the Asset Serial cell in a row of the Asset Serials grid
# (0-based: a hidden ID column comes first, then SL, then Asset Serial)
ASSET_SERIAL_COLUMN_INDEX = 2

# Exact toast shown when an Approve succeeds
APPROVE_SUCCESS_TOAST = "Asset registration approved successfully."


class AssetRegistrationApprovalListPage(BasePage):
    """Page object for the Asset Registration Approval List screen and its detail popup."""

    def __init__(self, page):
        super().__init__(page)
        # Registration Number filter
        self.registration_id_filter = page.locator("#registrationId")
        # Runs the filter
        self.search_button = page.get_by_role("button", name=" Search")
        # Results grid
        self.results_table = page.locator("table")
        # Page-level bulk Approve button. NOT a generic name="Approve" match:
        # there are two other same-labelled approve controls on this page
        # (a per-row quick-approve, and a modal-context approve never reached).
        self.approve_button = page.locator("#btnApprove")
        # "Asset Registration View" detail popup
        self.modal = page.locator("#commonModal")
        self.modal_close_button = page.get_by_role("button", name="Close")
        # Approve button inside the popup (the page-level #btnApprove is a different button)
        self.popup_approve_button = self.modal.locator("#approve")
        # Asset Serials tab link inside the popup
        self.asset_serials_tab_link = page.locator('a[href="#tab_asset_serials"]')
        # Asset Serials tab content pane
        self.asset_serials_pane = page.locator("#tab_asset_serials")
        # Status filter: PENDING, APPROVED, REJECTED, SENDBACK
        self.status_filter = page.locator("#status")
        # Registration Type filter: MRR, AAQ, LEASE
        self.registration_type_filter = page.locator("#registrationType")
        # Vendor/Supplier/Lessor Name and MRR Number filters (free text)
        self.vendor_filter = page.locator("#supplierName")
        self.mrr_filter = page.locator("#referenceNo")
        # Project Name & Number filter
        self.project_filter = page.locator("#projectId")
        # Created By and Approved By filters (employee search boxes)
        self.created_by_filter = page.locator("#createdBy")
        self.approved_by_filter = page.locator("#approvedBy")
        # Clears the filter boxes (it does not run the search again)
        self.reset_button = page.locator("#reset")
        # The results grid itself, and the line under it, e.g. "Showing 1 to 10 of 124 entries"
        self.grid = page.locator("#assetRegistrationList")
        self.entries_info = page.locator(".dataTables_info")
        # Records per page dropdown: 10, 20, 30, 50, 100
        self.page_size_select = page.locator("select[name=assetRegistrationList_length]")
        # Header checkbox that ticks every row that can be approved
        self.select_all_checkbox = page.locator("#assetRegistrationList thead input[type=checkbox]")
        # Comment box inside the popup (maximum 500 characters)
        self.comment_field = self.modal.locator("#comment")
        # Read-only date filters, filled through the calendar pop-up
        self.registration_from_date = page.locator("#registrationFromDate")
        self.registration_to_date = page.locator("#registrationToDate")
        self.approve_from_date = page.locator("#approveFromDate")
        self.approve_to_date = page.locator("#approveToDate")

    def navigate_here(self) -> None:
        """Open the Asset Registration Approval List screen via the left/top menu."""
        self.open_registration_submenu("Asset Registration Approval List")
        self.wait_until_visible(self.search_button, "Search button")

    def filter_by_registration_number(self, registration_number: str) -> None:
        """Filter the grid down to one Registration Number and run the search."""
        self.type_text(
            self.registration_id_filter, registration_number, "Registration Number filter"
        )
        self.search()

    def search(self) -> None:
        """Click Search and wait for the grid to finish reloading."""
        self.click(self.search_button, "Search button")
        self.wait_for_grid_to_reload(self.entries_info)

    def filter_by_status(self, status: str) -> None:
        """Set the Status filter (PENDING, APPROVED, REJECTED or SENDBACK) and search."""
        action_logger.info(f"Filter: Status -> {status}")
        self.status_filter.select_option(status)
        self.search()

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

    def reset_filters(self) -> None:
        """Click Reset, which empties every filter box."""
        self.click(self.reset_button, "Reset button")

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

    def set_page_size(self, size: int) -> None:
        """Choose how many records the grid shows per page."""
        action_logger.info(f"Select: Records per page -> {size}")
        # The line "Showing 1 to 10 of N entries" is empty while the grid loads; read N once it has text
        self.wait_for_grid_to_reload(self.entries_info)
        total_entries = self.read_total_entries()
        self.page_size_select.select_option(str(size))
        self.wait_for_rows_per_page(self.grid.locator("tbody tr"), size, total_entries)

    def go_to_page(self, page_number: int) -> None:
        """Click a page number under the grid and wait until that page is shown."""
        size = int(self.page_size_select.input_value())
        button = self.page.locator(".paginate_button", has_text=str(page_number)).first
        self.click(button, f"Page {page_number} button")
        self.wait_for_page_shown(self.entries_info, page_number, size)

    def read_popup_text(self) -> str:
        """Return everything the open popup shows, including what is typed in its boxes."""
        text = self.get_text(self.modal, "Asset Registration View popup")
        values = self.modal.evaluate(
            "m => Array.from(m.querySelectorAll('input, textarea, select')).map(e => e.value).join(' ')"
        )
        return f"{text} {values}"

    def read_headers(self) -> list:
        """Return the grid's column headings, in order (the first, a checkbox column, is empty)."""
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

    def row_has_checkbox(self, registration_number: str) -> bool:
        """Return True if the row of this registration has a tick box (only rows that can still be approved do)."""
        row = self.grid.locator("tbody tr", has_text=registration_number)
        return row.locator("input[type=checkbox]").count() > 0

    def tick_first_rows(self, how_many: int) -> list:
        """Tick the first `how_many` rows of the grid and return their Registration Numbers."""
        numbers = self.read_column("Registration Number")[:how_many]
        for index in range(how_many):
            checkbox = self.grid.locator("tbody tr").nth(index).locator("input[type=checkbox]")
            self.click(checkbox, f"Row {index + 1} checkbox")
        return numbers

    def approve_ticked_rows_and_get_toast(self) -> str:
        """Click the page-level Approve for the ticked rows and return the toast text."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button (ticked rows)")
        return self.get_toast_text()

    def enter_comment(self, comment: str) -> None:
        """Type into the popup's Comment box."""
        self.type_text(self.comment_field, comment, "Comment box")

    def open_registration_popup_by_number(self, registration_number: str) -> None:
        """Filter by a Registration Number, then open its popup."""
        self.filter_by_registration_number(registration_number)
        self.open_registration_popup(registration_number)

    def read_row(self, registration_number: str) -> dict:
        """Return the cells of a registration's row keyed by column heading."""
        headings = self.read_headers()
        row = self.grid.locator("tbody tr", has_text=registration_number).first
        cells = [c.strip() for c in row.locator("td").all_inner_texts()]
        return dict(zip(headings, cells))

    def open_registration_popup(self, registration_number: str) -> None:
        """Click the Registration Number link to open the Asset Registration View popup."""
        link = self.results_table.get_by_role("link", name=registration_number, exact=True)
        self.click(link, f"Registration Number {registration_number} link")
        self.wait_until_visible(self.modal, "Asset Registration View popup")

    def verify_popup_details(self, expected_values: list) -> None:
        """
        Confirm every value in `expected_values` appears somewhere in the
        popup's Details tab. The catalog only documents the Details tab at
        panel level (Registration Details / Vendor Details / Asset Details
        grid), not individual field locators, so this reads the popup's
        full visible text and checks each expected value is present in it.
        A missing value names exactly what was expected and was not found.
        """
        modal_text = self.get_text(self.modal, "Asset Registration View popup")
        # Field values sit inside input boxes, which are not part of the visible text
        input_values = self.modal.evaluate(
            "m => Array.from(m.querySelectorAll('input, textarea, select'))"
            ".map(e => e.value).join(' ')"
        )
        modal_text = f"{modal_text} {input_values}"
        assertion_logger.info("Verifying Asset Registration View popup fields")
        missing = [value for value in expected_values if value not in modal_text]
        assert not missing, (
            f"Asset Registration View popup is missing expected value(s): {missing}. "
            f"Popup text was: {modal_text}"
        )
        assertion_logger.info("All expected values found in the Asset Registration View popup")

    def close_popup(self) -> None:
        """Close the Asset Registration View popup."""
        self.click(self.modal_close_button, "Close button")

    def select_row_checkbox(self, registration_number: str) -> None:
        """Tick the row checkbox for `registration_number`, scoped to that row."""
        row = self.results_table.locator("tr", has_text=registration_number)
        checkbox = row.locator("input[type=checkbox]")
        self.click(checkbox, f"Row checkbox for Registration {registration_number}")

    def verify_popup_registration_number(self, registration_number: str) -> None:
        """
        Confirm the open popup is for `registration_number`, the number
        taken from the Asset Registration List, by reading the popup's
        Registration No field.
        """
        popup_number = self.modal.evaluate(
            "m => { const label = Array.from(m.querySelectorAll('label'))"
            ".find(l => l.innerText.trim().startsWith('Registration No'));"
            " const field = label && label.closest('div').parentElement.querySelector('input');"
            " return field ? field.value : ''; }"
        )
        assertion_logger.info(
            f"Verifying popup shows Registration No {registration_number} from the Asset Registration List"
        )
        assert popup_number.strip() == registration_number, (
            f"Expected the popup to show Registration No '{registration_number}' "
            f"(from the Asset Registration List) but it shows '{popup_number}'."
        )

    def approve_from_popup_and_verify_success(self, registration_number: str) -> None:
        """
        Click Approve inside the open popup and confirm the exact success
        toast is shown. Any other message fails the test and is reported
        with its full text.
        """
        self.wait_for_toast_to_clear()
        self.click(self.popup_approve_button, "Approve button in popup")
        toast_text = self.get_toast_text()
        assertion_logger.info(f"Verifying Approve success toast for Registration {registration_number}")
        assert toast_text == APPROVE_SUCCESS_TOAST, (
            f"Expected Approve toast '{APPROVE_SUCCESS_TOAST}' for Registration "
            f"{registration_number} but found '{toast_text}'."
        )
        assertion_logger.info("Approve success toast matched exactly")

    def open_asset_serials_tab(self) -> None:
        """Switch the open popup to its Asset Serials tab."""
        self.click(self.asset_serials_tab_link, "Asset Serials tab")
        self.wait_until_visible(self.asset_serials_pane, "Asset Serials tab content")

    def get_asset_serials_text(self) -> str:
        """Return the visible text of the Asset Serials tab (the grid, or its empty message)."""
        return self.get_text(self.asset_serials_pane, "Asset Serials tab content")

    def get_all_generated_asset_serials(self) -> list:
        """Return every Asset Serial listed on the open Asset Serials tab (one per row)."""
        rows = self.asset_serials_pane.locator("table tbody tr")
        rows.first.wait_for(state="visible")
        serials = []
        for index in range(rows.count()):
            cell = rows.nth(index).locator("td").nth(ASSET_SERIAL_COLUMN_INDEX)
            serials.append(cell.inner_text().strip())
        return serials

    def get_generated_asset_serial(self) -> str:
        """
        Return the Asset Serial value from the first row of the Asset
        Serials tab grid (populated only after a successful Approve).
        """
        first_row = self.asset_serials_pane.locator("table tbody tr").first
        serial = first_row.locator("td").nth(ASSET_SERIAL_COLUMN_INDEX).inner_text().strip()
        action_logger.info(f"Generated Asset Serial Number: {serial}")
        return serial

    # ------------------------------------------------------------------
    # Filter helpers (type or choose a value in one filter box)
    # ------------------------------------------------------------------

    def get_filter(self, filter_name: str):
        """
        Return the filter box with this name: "Status", "Registration Type",
        "Registration Number", "Vendor", "MRR Number", "Created By" or
        "Approved By". Fails with a clear message for any other name.
        """
        if filter_name == "Status":
            return self.status_filter
        if filter_name == "Registration Type":
            return self.registration_type_filter
        if filter_name == "Registration Number":
            return self.registration_id_filter
        if filter_name == "Vendor":
            return self.vendor_filter
        if filter_name == "MRR Number":
            return self.mrr_filter
        if filter_name == "Created By":
            return self.created_by_filter
        if filter_name == "Approved By":
            return self.approved_by_filter
        raise AssertionError(f"There is no filter called '{filter_name}' on the approval list.")

    def select_status(self, status: str) -> None:
        """Choose a value in the Status filter without running the search."""
        action_logger.info(f"Select: Status -> {status}")
        self.status_filter.select_option(status)

    def select_registration_type(self, registration_type: str) -> None:
        """Choose a value in the Registration Type filter without running the search."""
        action_logger.info(f"Select: Registration Type -> {registration_type}")
        self.registration_type_filter.select_option(registration_type)

    def type_registration_number(self, text: str) -> None:
        """Type into the Registration Number filter without running the search."""
        self.type_text(self.registration_id_filter, text, "Registration Number filter")

    def type_vendor_name(self, text: str) -> None:
        """Type into the Vendor/Supplier/Lessor Name filter without running the search."""
        self.type_text(self.vendor_filter, text, "Vendor/Supplier/Lessor Name filter")

    def filter_by_mrr_number(self, mrr_number: str) -> None:
        """Type into the MRR Number filter and search."""
        self.type_text(self.mrr_filter, mrr_number, "MRR Number filter")
        self.search()

    def read_first_value(self, heading: str) -> str:
        """Return what the first row shows in the column with this heading (fails if the grid is empty)."""
        values = self.read_column(heading)
        if len(values) == 0:
            raise AssertionError(f"Expected at least one row to read '{heading}' from, but the grid is empty.")
        return values[0]

    def read_first_reference_number(self) -> str:
        """Return the first non-empty Reference Number (MRR Number) shown in the grid."""
        for reference in self.read_column("Reference Number"):
            if reference != "":
                return reference
        raise AssertionError("Expected a row with a Reference Number but every Reference Number is empty.")

    # ------------------------------------------------------------------
    # Tick boxes
    # ------------------------------------------------------------------

    def count_rows_with_checkbox(self) -> int:
        """Return how many rows in the grid have a tick box."""
        return self.grid.locator("tbody input[type=checkbox]").count()

    def count_ticked_rows(self) -> int:
        """Return how many rows in the grid are ticked."""
        return self.grid.locator("tbody input[type=checkbox]:checked").count()

    def tick_select_all(self) -> None:
        """Tick the header box, which ticks every row that can be approved."""
        action_logger.info("Tick: select all checkbox")
        self.select_all_checkbox.check()

    def untick_select_all(self) -> None:
        """Untick the header box, which unticks every row."""
        action_logger.info("Untick: select all checkbox")
        self.select_all_checkbox.uncheck()

    def verify_all_rows_ticked(self) -> None:
        """Confirm the grid has rows with tick boxes and every one of them is ticked."""
        total = self.count_rows_with_checkbox()
        ticked = self.count_ticked_rows()
        assertion_logger.info("Verifying every row is ticked")
        assert total > 0, "Expected rows with tick boxes in the grid but found none."
        assert ticked == total, f"Expected all {total} rows to be ticked but {ticked} are ticked."

    def verify_no_rows_ticked(self) -> None:
        """Confirm no row in the grid is ticked."""
        ticked = self.count_ticked_rows()
        assertion_logger.info("Verifying no row is ticked")
        assert ticked == 0, f"Expected no ticked rows but {ticked} are ticked."

    def verify_row_has_checkbox(self, registration_number: str) -> None:
        """Confirm the row of this registration has a tick box."""
        assertion_logger.info(f"Verifying Registration {registration_number} has a tick box")
        assert self.row_has_checkbox(registration_number), (
            f"Expected Registration {registration_number} to have a tick box but it has none."
        )

    def verify_row_has_no_checkbox(self, registration_number: str) -> None:
        """Confirm the row of this registration has no tick box."""
        assertion_logger.info(f"Verifying Registration {registration_number} has no tick box")
        assert not self.row_has_checkbox(registration_number), (
            f"Expected Registration {registration_number} to have no tick box but it has one."
        )

    # ------------------------------------------------------------------
    # Checks on the page (each says what was expected and what was found)
    # ------------------------------------------------------------------

    def verify_headers(self, expected_headers: list) -> None:
        """Confirm the grid's column headings are exactly `expected_headers`, in order."""
        found = self.read_headers()
        assertion_logger.info("Verifying the grid column headings")
        assert found == expected_headers, f"Expected column headings {expected_headers} but found {found}."

    def verify_filter_options(self, filter_name: str, expected_options: list) -> None:
        """Confirm a dropdown offers exactly `expected_options`. `filter_name` is "Status" or "Registration Type"."""
        found = self.read_filter_options(self.get_filter(filter_name))
        assertion_logger.info(f"Verifying the {filter_name} filter options")
        assert found == expected_options, f"Expected {filter_name} options {expected_options} but found {found}."

    def verify_page_size_options(self, expected_options: list) -> None:
        """Confirm the Records per page dropdown offers exactly `expected_options`."""
        found = self.read_filter_options(self.page_size_select)
        assertion_logger.info("Verifying the Records per page options")
        assert found == expected_options, f"Expected page size options {expected_options} but found {found}."

    def verify_filters_empty(self, filter_names: list) -> None:
        """Confirm each named filter box (see get_filter for the names) has no value."""
        assertion_logger.info(f"Verifying these filters are empty: {filter_names}")
        for filter_name in filter_names:
            value = self.get_filter(filter_name).input_value()
            assert value == "", f"Expected the {filter_name} filter to be empty but it holds '{value}'."

    def verify_newest_first(self) -> None:
        """Confirm the Registration Numbers on this page go from high to low (newest first)."""
        numbers = self.read_column("Registration Number")
        assertion_logger.info("Verifying registrations are listed newest first")
        for index in range(len(numbers) - 1):
            assert int(numbers[index]) > int(numbers[index + 1]), (
                f"Expected newest first (high to low) but found {numbers}."
            )

    def verify_all_rows_have(self, heading: str, expected: str, must_have_rows: bool = False) -> None:
        """
        Confirm every row shows `expected` in the column `heading`.
        With must_have_rows=True an empty grid also fails; otherwise an
        empty grid passes (a filter value nobody has lists nothing).
        """
        found = self.read_column(heading)
        assertion_logger.info(f"Verifying every row has {heading} = {expected}")
        if must_have_rows:
            assert len(found) > 0, f"Expected rows with {heading} '{expected}' but the grid is empty."
        for value in found:
            assert value == expected, f"Expected only {heading} '{expected}' but found {found}."

    def verify_column_equals(self, heading: str, expected_values: list) -> None:
        """Confirm the column `heading` shows exactly `expected_values`, row by row."""
        found = self.read_column(heading)
        assertion_logger.info(f"Verifying the {heading} column")
        assert found == expected_values, f"Expected {heading} {expected_values} but found {found}."

    def verify_grid_is_empty(self) -> None:
        """Confirm the grid shows "No data available in table"."""
        assertion_logger.info("Verifying the grid is empty")
        assert self.grid_is_empty(), (
            f"Expected an empty grid but it lists: {self.read_column('Registration Number')}."
        )

    def verify_grid_has_rows(self, what: str) -> None:
        """Confirm the grid lists at least one row. `what` names the filter, e.g. "vendor 'ACE IT'"."""
        assertion_logger.info(f"Verifying the grid has rows for {what}")
        assert not self.grid_is_empty(), f"Expected registrations for {what} but the grid is empty."

    def verify_registration_row(self, registration_number: str, project: str, registration_type: str, status: str) -> None:
        """Confirm the grid lists exactly this one registration, with this project, type and Status."""
        self.verify_column_equals("Registration Number", [registration_number])
        self.verify_column_equals("Project Name", [project])
        self.verify_column_equals("Registration Type", [registration_type])
        self.verify_column_equals("Status", [status])

    def verify_rows_per_page(self, size: int) -> None:
        """Confirm the grid shows `size` rows and the line under it says "Showing 1 to <size> of ..."."""
        rows = len(self.read_column("Registration Number"))
        assertion_logger.info(f"Verifying the grid shows {size} rows")
        assert rows == size, f"Expected {size} rows on the page but found {rows}."
        self.verify_entries_info_starts_with(f"Showing 1 to {size} of")

    def read_entries_info(self) -> str:
        """Return the line under the grid, e.g. "Showing 1 to 10 of 124 entries"."""
        return self.get_text(self.entries_info, "entries line under the grid")

    def verify_entries_info_starts_with(self, expected_start: str) -> None:
        """Confirm the line under the grid starts with `expected_start`."""
        found = self.read_entries_info()
        assertion_logger.info(f"Verifying the entries line starts with '{expected_start}'")
        assert found.startswith(expected_start), f"Expected the entries line to start with '{expected_start}' but found '{found}'."

    def verify_page_two_is_older(self, first_page: list, second_page: list) -> None:
        """Confirm page 2 holds different, older registrations than page 1 (both are lists of Registration Numbers)."""
        assertion_logger.info("Verifying page 2 continues the list")
        for number in second_page:
            assert number not in first_page, (
                f"Expected page 2 to show different registrations but {number} is on both pages."
            )
        lowest_on_first = min(int(n) for n in first_page)
        highest_on_second = max(int(n) for n in second_page)
        assert highest_on_second < lowest_on_first, (
            f"Expected page 2 to hold older registrations (below {lowest_on_first}) but it holds {highest_on_second}."
        )

    def verify_toast(self, expected_text: str) -> None:
        """Confirm the toast on screen has exactly `expected_text`; any other message, or none, fails."""
        found = self.get_toast_text()
        assertion_logger.info(f"Verifying toast '{expected_text}'")
        assert found == expected_text, f"Expected toast '{expected_text}' but found '{found}'."

    def approve_ticked_rows(self) -> None:
        """Click the page-level Approve for the ticked rows (read the result with verify_toast)."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button (ticked rows)")

    def verify_registration_is_approved(self, registration_number: str) -> None:
        """Open the approval list, find this registration and confirm its Status is APPROVED."""
        self.navigate_here()
        self.filter_by_registration_number(registration_number)
        status = self.read_row(registration_number)["Status"]
        assertion_logger.info(f"Verifying Registration {registration_number} is APPROVED")
        assert status == "APPROVED", f"Expected Registration {registration_number} to be APPROVED but its Status is '{status}'."

    def verify_approved_row(self, registration_number: str) -> None:
        """Confirm the row shows APPROVED, an approver and a dd/mm/yyyy approval date, and has no tick box."""
        row = self.read_row(registration_number)
        assertion_logger.info(f"Verifying the approved row of Registration {registration_number}")
        assert row["Status"] == "APPROVED", f"Expected Status APPROVED but the row is {row}."
        assert row["Approved By"] != "", f"Expected an Approved By name but the row is {row}."
        assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", row["Approval Date"]), (
            f"Expected an Approval Date as dd/mm/yyyy but the row is {row}."
        )
        self.verify_row_has_no_checkbox(registration_number)

    # ------------------------------------------------------------------
    # Popup helpers
    # ------------------------------------------------------------------

    def read_comment(self) -> str:
        """Return what is typed in the popup's Comment box."""
        return self.comment_field.input_value()

    def verify_comment_length(self, expected_length: int) -> None:
        """Confirm the popup's Comment box holds exactly `expected_length` characters."""
        found = len(self.read_comment())
        assertion_logger.info(f"Verifying the comment box holds {expected_length} characters")
        assert found == expected_length, f"Expected {expected_length} characters in the comment box but found {found}."

    def is_popup_approve_visible(self) -> bool:
        """Return True if the popup shows an Approve button."""
        return self.is_visible(self.popup_approve_button)

    def verify_popup_has_no_approve_button(self) -> None:
        """Confirm the open popup shows no Approve button."""
        assertion_logger.info("Verifying the popup has no Approve button")
        assert not self.is_popup_approve_visible(), "Expected no Approve button in the popup but it is shown."

    def verify_asset_serials_empty(self) -> None:
        """Confirm the open Asset Serials tab says "No data available in table"."""
        serials_text = self.get_asset_serials_text()
        assertion_logger.info("Verifying the Asset Serials tab is empty")
        assert "No data available in table" in serials_text, (
            f"Expected an empty Asset Serials grid before approval but found: {serials_text}"
        )

    def verify_asset_serial_generated(self, asset_serial: str) -> None:
        """Confirm an Asset Serial Number was read from the Asset Serials tab (not empty)."""
        assertion_logger.info("Verifying an Asset Serial Number was generated")
        assert asset_serial, (
            "Expected a generated Asset Serial Number on the Asset Serials tab "
            "after a successful Approve, but none was found."
        )

    def read_asset_serial_of(self, registration_number: str) -> str:
        """Reopen the approval list, open this registration's popup and return its first Asset Serial."""
        self.navigate_here()
        self.open_registration_popup_by_number(registration_number)
        self.open_asset_serials_tab()
        return self.get_generated_asset_serial()

    def verify_asset_serial_shown(self, expected_serial: str) -> None:
        """On the open Asset Serials tab, confirm the first serial looks like BBDASR00227761 and equals `expected_serial`."""
        serial = self.get_generated_asset_serial()
        assertion_logger.info("Verifying the Asset Serial on the tab")
        assert re.fullmatch(r"[A-Z]+\d+", serial), f"Expected an Asset Serial like BBDASR00227761 but found '{serial}'."
        assert serial == expected_serial, f"Expected Asset Serial {expected_serial} but found {serial}."
