"""
AssetSerialSplitPage: Fixed Asset > Asset Profile > Asset Serial Split
screen and its Asset Split form.

Lists assets that can be split. Each row has a SPLIT button; it opens the
Asset Split form only for an asset whose Measurement is above zero, otherwise
a message is shown. The form splits the asset into 2 to 100 lines and Submit
sends the split for approval. See `automation/element_catalog/asset_serial_split.md`.

Submit really splits the asset: its serial leaves this screen and new serials
are made when the split is approved. Only the saved Land asset is submitted
(see utils/split_helper.py).
"""
import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from test_data.toast_messages import SPLIT_REFUSED_MESSAGE, SPLIT_SUBMITTED_MESSAGE
from utils.logger import action_logger, assertion_logger

# Message shown when SPLIT is clicked for an asset with no measurement

# Text the success message of Submit contains

# Two numbers closer than this are treated as equal (the grid shows 2 decimals)
NUMBER_TOLERANCE = 0.005


class AssetSerialSplitPage(BasePage):
    """Page object for the Asset Serial Split screen and its form."""

    def __init__(self, page):
        super().__init__(page)
        # Filter and buttons (the form has its own #assetSerial, so the filter is found by name)
        self.asset_serial_filter = page.locator('input[name="assetSerial"]')
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid
        self.results_table = page.locator("#assetSerialGlobalList")
        # Asset Split form (opens in place of the list)
        self.split_into_field = page.locator("#splitInto")
        self.remarks_field = page.locator("#remarks")
        self.split_button = page.locator("#splitAsset")
        self.submit_button = page.locator("#submit1")
        self.form_reset_button = page.locator("#resetEditButton")
        self.back_link = page.get_by_role("link", name="Back")
        self.result_grid = page.locator("#assetSerialSplitList")
        # Percentage box of every split line shown (ids percentage_0, percentage_1, ...)
        self.line_percentage_boxes = page.locator('input[id^="percentage_"]:visible')
        # Totals in the footer of the result grid
        self.total_percentage = page.locator("#totalPercentage")
        self.total_value = page.locator("#totalWrittenDownValue")
        self.total_measurement = page.locator("#totalMeasurement")

    def navigate_here(self) -> None:
        """Open the Asset Serial Split screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Asset Serial Split")
        self.wait_until_visible(self.search_button, "Search button")
        # The list loads its first rows after the screen appears; a search started
        # before that is overwritten by the first load
        self.results_table.locator("tbody tr").first.wait_for(state="visible")

    def search_by_serial(self, serial: str) -> None:
        """Filter by Asset Serial and wait for the result (or the empty message)."""
        self.type_text(self.asset_serial_filter, serial, "Asset Serial filter")
        self.click(self.search_button, "Search button")
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

    def verify_split_button_shown(self, serial: str) -> None:
        """Confirm the row of this serial has a SPLIT button."""
        assertion_logger.info(f"Verifying {serial} has a SPLIT button")
        assert self.has_split_button(serial), f"Expected a SPLIT button on the row of {serial} but there is none."

    def verify_serial_not_listed(self, serial: str) -> None:
        """Confirm no result row shows this Asset Serial (call after searching it)."""
        assertion_logger.info(f"Verifying {serial} is not listed on the Split screen")
        found = self.results_table.locator("tbody tr", has_text=serial).count()
        assert found == 0, f"Expected {serial} not to be listed on the Split screen but {found} row(s) show it."

    def click_split_and_get_toast(self, serial: str) -> str:
        """Click SPLIT for this serial and return the message shown (used when the split is refused)."""
        self.wait_for_toast_to_clear()
        self.click(self._split_button_for(serial), f"SPLIT button for {serial}")
        return self.get_toast_text()

    def verify_split_is_refused(self, serial: str) -> None:
        """Click SPLIT for an asset with no measurement and confirm the refusal message."""
        toast = self.click_split_and_get_toast(serial)
        self.verify_toast_text(toast, SPLIT_REFUSED_MESSAGE, f"SPLIT clicked for {serial} (no measurement)")

    def open_split_form(self, serial: str) -> None:
        """Click SPLIT for this serial and wait for the Asset Split form."""
        self.click(self._split_button_for(serial), f"SPLIT button for {serial}")
        self.wait_until_visible(self.split_into_field, "Split Into field")

    def open_split_form_for_serial(self, serial: str) -> None:
        """Open the Split screen, search the serial and open its Asset Split form."""
        self.navigate_here()
        self.search_by_serial(serial)
        self.open_split_form(serial)

    # ---- the form's details ---------------------------------------------------

    def get_form_value(self, field_id: str) -> str:
        """Return the value of a field on the Asset Split form, e.g. 'measurementFront'."""
        action_logger.info(f"Read value of split form field: {field_id}")
        return self.page.locator(f"input#{field_id}:visible").first.input_value().strip()

    def verify_form_shows(self, expected: dict) -> None:
        """Confirm the form shows every value in `expected` ({field id: text}); names each difference."""
        assertion_logger.info("Verifying the details shown on the Asset Split form")
        problems = []
        for field_id, wanted in expected.items():
            found = self.get_form_value(field_id)
            if found != wanted:
                problems.append(f"{field_id}: expected '{wanted}' but found '{found}'")
        assert not problems, f"The Asset Split form is not as expected: {problems}"

    def is_split_into_editable(self) -> bool:
        """Return True if the Split Into box can be typed in."""
        return self.split_into_field.is_editable()

    def get_split_into_value(self) -> str:
        """Return what is typed in the Split Into box."""
        return self.split_into_field.input_value()

    def verify_split_into_is_empty_and_editable(self) -> None:
        """Confirm the Split Into box is empty and can be typed in."""
        assertion_logger.info("Verifying Split Into is empty and editable")
        found = self.get_split_into_value()
        assert found == "", f"Expected Split Into to be empty but it holds '{found}'."
        assert self.is_split_into_editable(), "Expected the Split Into box to be editable but it is not."

    def is_split_button_visible(self) -> bool:
        """Return True if the Split button is shown on the form."""
        return self.split_button.is_visible()

    def get_result_grid_headers(self) -> list:
        """Return the visible column headings of the form's result grid."""
        headers = self.result_grid.locator("thead th:visible").all_inner_texts()
        return [" ".join(h.split()) for h in headers if h.strip()]

    # ---- building the split lines ---------------------------------------------

    def type_split_into(self, value: str) -> None:
        """Type the number of parts in the Split Into box."""
        self.type_text(self.split_into_field, value, "Split Into field")

    def type_remarks(self, text: str) -> None:
        """Type the split's remarks."""
        self.type_text(self.remarks_field, text, "Remarks field")

    def click_split_and_get_form_toast(self) -> str:
        """Click the form's Split button and return the message shown (used for invalid Split Into values)."""
        self.wait_for_toast_to_clear()
        self.click(self.split_button, "Split button")
        return self.get_toast_text()

    def verify_split_into_message(self, split_into: str, expected_message: str) -> None:
        """Type a Split Into value, click Split and confirm the message shown is `expected_message`."""
        self.type_split_into(split_into)
        toast = self.click_split_and_get_form_toast()
        self.verify_toast_text(toast, expected_message, f"Split with Split Into '{split_into}'")

    def build_split_lines(self, split_into: str) -> None:
        """Type Split Into, click Split and wait until the result lines are shown."""
        self.type_split_into(split_into)
        self.click(self.split_button, "Split button")
        self.wait_until_visible(self.line_percentage_boxes.first, "first split line")

    def get_line_count(self) -> int:
        """Return how many split lines the result grid shows."""
        return self.line_percentage_boxes.count()

    def verify_line_count(self, expected: int) -> None:
        """Confirm the result grid shows `expected` split lines."""
        assertion_logger.info(f"Verifying the result grid has {expected} lines")
        found = self.get_line_count()
        assert found == expected, f"Expected {expected} split lines but the grid shows {found}."

    def type_line_percentage(self, line: int, value: str) -> None:
        """
        Type a percentage in a split line (line 0 is the first) and leave the
        box. The last line then takes the balance, so wait until it is filled.
        """
        box = self.page.locator(f"#percentage_{line}")
        self.type_text(box, value, f"Percentage box of line {line + 1}")
        box.press("Tab")
        expect(self.line_percentage_boxes.last).not_to_have_value(re.compile(r"^(0(\.0+)?)?$"))

    def _read(self, element) -> str:
        """Return the value of an input box, or the text of any other element."""
        script = "e => (e.tagName === 'INPUT' ? e.value : e.innerText)"
        return element.evaluate(script).strip()

    def _difference(self, name: str, found_text: str, expected: float) -> str:
        """Return a sentence if `found_text` is not the number `expected`, otherwise an empty text."""
        try:
            found = float(found_text.replace(",", ""))
        except ValueError:
            return f"{name}: expected {expected} but found '{found_text}'"
        if abs(found - expected) > NUMBER_TOLERANCE:
            return f"{name}: expected {expected} but found {found_text}"
        return ""

    def _line_value_text(self, line: int, column: str) -> str:
        """Return the text of one cell of a split line, found by its column heading."""
        index = self.get_result_grid_headers().index(column)
        cell = self.result_grid.locator("tbody tr").nth(line).locator("td").nth(index)
        return self._read(cell)

    def verify_line_values(self, line: int, percentage: float, measurement: float, value: float) -> None:
        """Confirm a split line (0 is the first) shows this percentage, measurement and written down value."""
        assertion_logger.info(f"Verifying the values of split line {line + 1}")
        checks = [
            self._difference("percentage", self._read(self.page.locator(f"#percentage_{line}")), percentage),
            self._difference("measurement", self._read(self.page.locator(f"#measurement_{line}")), measurement),
            self._difference("written down value", self._line_value_text(line, "Written Down Value"), value),
        ]
        problems = [text for text in checks if text]
        assert not problems, f"Split line {line + 1} is not as expected: {problems}"

    def verify_totals(self, percentage: float, value: float, measurement: float) -> None:
        """Confirm the Grand Total row shows these totals."""
        assertion_logger.info("Verifying the Grand Total row")
        checks = [
            self._difference("total percentage", self._read(self.total_percentage), percentage),
            self._difference("total written down value", self._read(self.total_value), value),
            self._difference("total measurement", self._read(self.total_measurement), measurement),
        ]
        problems = [text for text in checks if text]
        assert not problems, f"The Grand Total row is not as expected: {problems}"

    def verify_line_boxes_editable(self, line: int, expected_editable: bool) -> None:
        """Confirm the percentage and measurement boxes of a split line are editable (or read-only)."""
        assertion_logger.info(f"Verifying the boxes of split line {line + 1} editable = {expected_editable}")
        percentage_editable = self.page.locator(f"#percentage_{line}").is_editable()
        measurement_editable = self.page.locator(f"#measurement_{line}").is_editable()
        assert (percentage_editable, measurement_editable) == (expected_editable, expected_editable), (
            f"Expected the percentage and measurement boxes of line {line + 1} to be editable = {expected_editable} "
            f"but found percentage {percentage_editable}, measurement {measurement_editable}."
        )

    # ---- reset, back and submit -----------------------------------------------

    def reset_form(self) -> None:
        """Click the form's Reset button."""
        self.click(self.form_reset_button, "Reset button of the split form")

    def verify_split_values_are_reset(self, lines: int) -> None:
        """Confirm Reset zeroed every line and the totals, and kept the Split Into value and the lines."""
        assertion_logger.info("Verifying Reset zeroed the split values")
        expect(self.split_into_field).to_have_value(str(lines))
        found = self.get_line_count()
        assert found == lines, f"Expected {lines} split lines after Reset but the grid shows {found}."
        for line in range(lines):
            self.verify_line_values(line, 0, 0, 0)
        self.verify_totals(0, 0, 0)

    def go_back(self) -> None:
        """Leave the form without splitting."""
        self.click(self.back_link.first, "Back link")

    def verify_form_closed(self) -> None:
        """Confirm the Asset Split form is closed and the search screen is shown again."""
        assertion_logger.info("Verifying the Asset Split form is closed")
        expect(self.split_into_field).to_be_hidden()
        expect(self.search_button).to_be_visible()

    def submit_split_and_get_toast(self) -> str:
        """Click Submit and return the message shown, or an empty text if none was seen."""
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        return self.get_toast_text_or_empty()

    def verify_submit_message(self, toast: str) -> None:
        """Confirm the Submit message (when one was seen) says the split was submitted."""
        self.verify_toast_if_shown(toast, SPLIT_SUBMITTED_MESSAGE, "Submit of the split")

    def submit_split(self) -> None:
        """Click Submit, confirm the message and wait until the Split screen is shown again."""
        toast = self.submit_split_and_get_toast()
        self.verify_submit_message(toast)
        self.wait_until_visible(self.search_button, "Search button after Submit")

    def fill_and_submit_split(self, serial: str, split_into: str, remarks: str, first_percentage: str) -> None:
        """
        Split one asset from start to finish: open its form, type the remarks,
        build the lines, type the first line's percentage (the last line takes
        the balance) and Submit.
        """
        self.open_split_form_for_serial(serial)
        self.type_remarks(remarks)
        self.build_split_lines(split_into)
        self.type_line_percentage(0, first_percentage)
        self.submit_split()
