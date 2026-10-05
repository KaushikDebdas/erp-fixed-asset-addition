"""
AssetRegistrationAaqPage: Fixed Asset > Registration > Asset Registration
by AAQ screen.

Used to register a newly purchased asset (a "Spot Purchase" or a "Gift
Item"). See `automation/element_catalog/asset_registration_aaq.md` for the
full field list and business rules this page object relies on.
"""
import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from utils.helpers import day_of_month
from utils.logger import action_logger, assertion_logger


class AssetRegistrationAaqPage(BasePage):
    """Page object for the Asset Registration by AAQ create/update form."""

    def __init__(self, page):
        super().__init__(page)
        # Project Name & Number dropdown, required
        self.project_field = page.locator("#project")
        # Spot Purchase sub-type radio button
        self.spot_purchase_radio = page.locator("#spotPurchase")
        # Read-only Registration Date, auto-filled with the business date
        self.registration_date_field = page.locator("#registrationDate")
        # Read-only Purchase Date, filled through the calendar pop-up
        self.purchase_date_field = page.locator("#purchaseDate")
        # Calendar icon button that opens the Purchase Date pop-up
        self.purchase_date_calendar_button = page.locator("#forUpdate")
        # Note/Remarks free text field
        self.remarks_field = page.locator("#remarks")
        # Vendor/Supplier/Lessor select2 trigger link (text changes once picked)
        self.vendor_trigger = page.get_by_role("link", name="-Select Party-")
        # Asset Item Name select2 trigger link (text changes once picked)
        self.item_trigger = page.get_by_role("link", name="-Select Item-")
        # The text box select2 shows once a trigger link is clicked
        self.select2_search_box = page.locator("input.select2-input[type=text]:visible")
        # Item Specification/IMEI/SL free text field
        self.item_specification_field = page.locator("#itemSpecification")
        # Quantity numeric field
        self.quantity_field = page.locator("#quantity")
        # Unit Price numeric field
        self.unit_price_field = page.locator("#unitPrice")
        # Measurement numeric field; the unit beside it follows the chosen item (Land = Decimal)
        self.measurement_field = page.locator("#mq")
        # Read-only Registration Type, always shows "AAQ"
        self.registration_type_field = page.locator("#registrationType")
        # Gift Item sub-type radio button
        self.gift_item_radio = page.locator("#giftItem")
        # Read-only boxes filled in after an Asset Item is picked
        self.asset_category_field = page.locator("#assetCategory")
        self.asset_sub_category_field = page.locator("#assetSubCategory")
        self.asset_group_field = page.locator("#assetGroup")
        self.measurement_unit_field = page.locator("#uom")
        # Read-only boxes filled in after a Vendor is picked
        self.vendor_number_field = page.locator("#supplierNumber")
        self.vendor_address_field = page.locator("#supplierAddress")
        # Asset Details grid, including its Grand Total row
        self.asset_grid = page.locator("#assetDetailsTable")
        # Trash button on a grid line
        self.grid_delete_button = page.locator("#assetDetailsTable button[name='deleteAction']")
        # Reset beside Add: clears only the Asset Details block being filled
        self.reset_details_button = page.locator("#resetDetails")
        # Reset in the page footer: clears the whole form
        self.reset_form_button = page.locator("#resetEditButton")
        # Adds the current Asset Details block as a line in the grid below
        self.add_button = page.get_by_role("button", name=" Add")
        # Saves the registration without submitting it for approval
        self.draft_button = page.get_by_role("button", name=" Draft")
        # Submits the registration for approval
        self.submit_button = page.get_by_role("button", name=" Submit")

    def navigate_here(self) -> None:
        """
        Open the Asset Registration by AAQ screen via the left/top menu.
        This SPA uses hash routing that does not reliably re-render on a
        direct page.goto() with a hash, so the real menu link must be
        clicked instead.
        """
        self.open_registration_submenu("Asset Registration by AAQ")
        self.wait_until_visible(self.project_field, "Project Name & Number field")

    def select_project(self, project: str) -> None:
        """Choose the Project Name & Number for this registration."""
        action_logger.info(f"Select: Project Name & Number dropdown -> {project}")
        self.project_field.select_option(label=project)
        self.registration_date_field.wait_for(state="visible")

    def choose_spot_purchase(self) -> None:
        """Select the "Spot Purchase" sub-type radio button."""
        self.click(self.spot_purchase_radio, "Spot Purchase radio button")

    def read_registration_date(self) -> str:
        """Return the auto-filled Registration Date shown on the form, e.g. '20/09/2026'."""
        action_logger.info("Read value of: Registration Date field")
        return self.registration_date_field.input_value()

    def set_purchase_date_equal_to_registration_date(self) -> str:
        """
        Set Purchase Date to the same value as the read-only Registration
        Date, per the business rule "Purchase Date = Registration Date".

        Returns the date string that was set (dd/mm/yyyy), so the caller
        can reuse it later (e.g. to confirm the popup shows the same date).
        """
        registration_date = self.read_registration_date()
        day_text = day_of_month(registration_date)

        self.click(self.purchase_date_calendar_button, "Purchase Date calendar icon")
        # The calendar pop-up already shows the current business month/year,
        # so clicking the matching day number is enough to match the
        # Registration Date. The open pop-up is the one appended last.
        day_cell = self.page.get_by_role("cell", name=day_text, exact=True).last
        self.click(day_cell, f"Purchase Date calendar day {day_text}")
        return registration_date

    def enter_remarks(self, remarks: str) -> None:
        """Type the Note/Remarks text."""
        self.type_text(self.remarks_field, remarks, "Note/Remarks field")

    def select_vendor(self, vendor: str) -> None:
        """Search and pick the Vendor/Supplier/Lessor Name via the select2 widget."""
        self.click(self.vendor_trigger, "Vendor/Supplier/Lessor Name trigger")
        self.type_text(self.select2_search_box, vendor, "Vendor search box")
        option = self.page.get_by_role("option", name=vendor)
        self.wait_until_visible(option, f"Vendor option '{vendor}'")
        self.click(option, f"Vendor option '{vendor}'")

    def select_asset_item(self, search_text: str, option_name: str) -> None:
        """
        Search the Asset Item Name field for `search_text` and pick the
        result whose visible name starts with `option_name`, so "Desktop
        Computer" does not also match "All In One Desktop Computer".
        """
        self.click(self.item_trigger, "Asset Item Name trigger")
        self.type_text(self.select2_search_box, search_text, "Asset Item Name search box")
        results = self.page.locator(".select2-drop-active").get_by_role("option")
        option = results.filter(has_text=re.compile("^" + re.escape(option_name)))
        self.wait_until_visible(option, f"Asset Item option '{option_name}'")
        self.click(option, f"Asset Item option '{option_name}'")

    def enter_item_details(self, item_specification: str, quantity: int, unit_price: int) -> None:
        """Fill Item Specification, Quantity and Unit Price for the current asset line."""
        self.type_text(self.item_specification_field, item_specification, "Item Specification field")
        self.type_text(self.quantity_field, str(quantity), "Quantity field")
        self.type_text(self.unit_price_field, str(unit_price), "Unit Price field")

    def enter_measurement(self, measurement: str) -> None:
        """Type the Measurement value (needed for Land and for any asset that will be split later)."""
        self.type_text(self.measurement_field, str(measurement), "Measurement field")

    def read_field(self, field) -> str:
        """Return what a box on the form shows; a dropdown gives its chosen option's text."""
        return field.evaluate(
            "el => el.tagName === 'SELECT' ? el.options[el.selectedIndex].text : el.value"
        ).strip()

    def read_registration_type(self) -> str:
        """Return the read-only Registration Type, e.g. 'AAQ'."""
        action_logger.info("Read value of: Registration Type field")
        return self.read_field(self.registration_type_field)

    def read_item_classification(self) -> dict:
        """Return the Category, Sub Category, Group and Measurement Unit filled in by the chosen item."""
        action_logger.info("Read the classification boxes filled in by the Asset Item")
        # The boxes are filled a moment after the item is picked
        expect(self.asset_category_field).not_to_have_value("", timeout=10000)
        expect(self.measurement_unit_field).not_to_have_value("", timeout=10000)
        return {
            "category": self.read_field(self.asset_category_field),
            "sub_category": self.read_field(self.asset_sub_category_field),
            "group": self.read_field(self.asset_group_field),
            "unit": self.read_field(self.measurement_unit_field),
        }

    def read_vendor_details(self) -> dict:
        """Return the Vendor Ref. Number and Address filled in by the chosen vendor."""
        action_logger.info("Read the vendor boxes filled in by the Vendor")
        # The boxes are filled a moment after the vendor is picked
        expect(self.vendor_number_field).not_to_have_value("", timeout=10000)
        expect(self.vendor_address_field).not_to_have_value("", timeout=10000)
        return {
            "number": self.read_field(self.vendor_number_field),
            "address": self.read_field(self.vendor_address_field),
        }

    def choose_gift_item(self) -> None:
        """Select the "Gift Item" sub-type radio button."""
        self.click(self.gift_item_radio, "Gift Item radio button")

    def choose_sub_type(self, sub_type: str) -> None:
        """Select Spot Purchase ("spot") or Gift Item ("gift")."""
        if sub_type == "gift":
            self.choose_gift_item()
        else:
            self.choose_spot_purchase()

    def read_remarks_max_length(self) -> int:
        """Return how many characters the Note/Remarks box accepts."""
        return int(self.remarks_field.get_attribute("maxlength"))

    def read_asset_grid_text(self) -> str:
        """Return all the text in the Asset Details grid, including the Grand Total row."""
        action_logger.info("Read the text of: Asset Details grid")
        return self.asset_grid.inner_text()

    def read_grid_first_line(self) -> dict:
        """
        Wait for a line to appear in the Asset Details grid, then return its
        cells keyed by column heading, e.g. line["Quantity"].
        """
        action_logger.info("Read the first line of: Asset Details grid")
        first_row = self.asset_grid.locator("tbody tr").first
        # The line appears a moment after Add; "No data available" is the empty grid
        expect(first_row).not_to_contain_text("No data available", timeout=10000)
        headings = [h.strip() for h in self.asset_grid.locator("thead th").all_inner_texts()]
        cells = [c.strip() for c in first_row.locator("td").all_inner_texts()]
        line = {}
        for position in range(len(headings)):
            if position < len(cells):
                line[headings[position]] = cells[position]
        return line

    def verify_form_shows_registration(self, data: dict) -> None:
        """
        Confirm the form (for example a Draft just opened from the list) shows
        the values in `data`: sub type, project, remarks, vendor number and an
        Asset Details line with the item name, specification, quantity and unit
        price. Fails and names every value that was different or missing.
        """
        action_logger.info("Verify the form shows the saved registration")
        expect(self.asset_grid.locator("tbody")).not_to_contain_text("No data available", timeout=10000)
        expect(self.vendor_number_field).not_to_have_value("", timeout=10000)
        project = self.project_field.evaluate("s => s.options[s.selectedIndex].text").strip()
        found = {
            "project": project,
            "remarks": self.remarks_field.input_value(),
            "vendor_number": self.vendor_number_field.input_value(),
        }
        problems = []
        for name, value in found.items():
            if value != data[name]:
                problems.append(f"{name}: expected '{data[name]}' but found '{value}'")
        if self.is_gift_item_selected() != (data["sub_type"] == "gift"):
            problems.append(f"sub type: '{data['sub_type']}' was expected to be selected")
        grid_text = self.read_asset_grid_text()
        # The grid shortens a long specification, so only its first 30 characters are compared
        for value in [data["grid_item_name"], data["item_specification"][:30], str(data["quantity"]), str(data["unit_price"])]:
            if value not in grid_text:
                problems.append(f"the Asset Details grid does not show '{value}'")
        assertion_logger.info("Verifying the form shows the saved registration")
        assert not problems, f"The form does not show the saved registration: {problems}. Grid text: {grid_text}"

    def wait_until_grid_is_empty(self) -> None:
        """Wait until the Asset Details grid shows "No data available"."""
        expect(self.asset_grid.locator("tbody")).to_contain_text("No data available", timeout=10000)

    def read_asset_block_values(self) -> dict:
        """Return what is typed in the Asset Details block: Specification, Quantity, Unit Price, Measurement."""
        return {
            "item_specification": self.item_specification_field.input_value(),
            "quantity": self.quantity_field.input_value(),
            "unit_price": self.unit_price_field.input_value(),
            "measurement": self.measurement_field.input_value(),
        }

    def reset_asset_details(self) -> None:
        """Click the Reset beside Add, which clears the Asset Details block."""
        self.click(self.reset_details_button, "Asset Details Reset button")

    def reset_form(self) -> None:
        """Click the Reset in the page footer, which clears the whole form."""
        self.click(self.reset_form_button, "Form Reset button")

    def delete_first_grid_line(self) -> None:
        """Click the trash button on the first line of the Asset Details grid."""
        self.click(self.grid_delete_button.first, "Grid line delete button")

    def add_asset_line(self) -> None:
        """Add the current Asset Details block as a line to the grid."""
        self.click(self.add_button, "Add button")

    def click_add_and_get_toast(self) -> str:
        """Click Add and return the toast text, for tests that expect a validation message."""
        self.wait_for_toast_to_clear()
        self.click(self.add_button, "Add button")
        return self.get_toast_text()

    def click_draft_and_get_toast(self) -> str:
        """Click Draft and return the toast text, for tests that expect a validation message."""
        self.wait_for_toast_to_clear()
        self.click(self.draft_button, "Draft button")
        return self.get_toast_text()

    def click_submit_and_get_toast(self) -> str:
        """Click Submit and return the toast text, for tests that expect a validation message."""
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        return self.get_toast_text()

    def verify_draft_and_submit_rejected(self, expected_toast: str) -> None:
        """
        Click Draft, then Submit, and confirm both are rejected with the same
        validation toast. Fails with the toast that was actually shown.
        """
        draft_toast = self.click_draft_and_get_toast()
        assertion_logger.info("Verifying Draft is rejected with the validation toast")
        assert draft_toast == expected_toast, f"Draft: expected toast '{expected_toast}' but found '{draft_toast}'."
        submit_toast = self.click_submit_and_get_toast()
        assertion_logger.info("Verifying Submit is rejected with the validation toast")
        assert submit_toast == expected_toast, f"Submit: expected toast '{expected_toast}' but found '{submit_toast}'."

    def fill_form_until_add(self, data: dict) -> str:
        """
        Fill the form from a registration data dict (see
        test_data/asset_registration_data.py) up to the point where Add can be
        clicked, without clicking it: project, sub-type, purchase date, vendor,
        asset item, item details and, only when the data has one, the Measurement.

        Returns the Purchase Date that was set (equal to the Registration Date).
        """
        self.select_project(data["project"])
        self.choose_sub_type(data.get("sub_type", "spot"))
        purchase_date = self.set_purchase_date_equal_to_registration_date()
        self.select_vendor(data["vendor"])
        self.select_asset_item(data["asset_item_search"], data["asset_item_selected"])
        self.enter_item_details(data["item_specification"], data["quantity"], data["unit_price"])
        if "measurement" in data:
            self.enter_measurement(data["measurement"])
        return purchase_date

    def fill_registration_form(self, data: dict) -> str:
        """
        Fill the whole form from a registration data dict, type the
        Note/Remarks and add one asset line.

        Returns the Purchase Date that was set (equal to the Registration Date).
        """
        purchase_date = self.fill_form_until_add(data)
        self.enter_remarks(data["remarks"])
        self.add_asset_line()
        return purchase_date

    def is_spot_purchase_selected(self) -> bool:
        """Return True when the Spot Purchase radio button is selected."""
        return self.spot_purchase_radio.is_checked()

    def is_gift_item_selected(self) -> bool:
        """Return True when the Gift Item radio button is selected."""
        return self.gift_item_radio.is_checked()

    def verify_sub_type_selected(self, sub_type: str) -> None:
        """
        Check that only the given sub-type ("spot" or "gift") is selected.
        Fails with what was expected and which radio buttons were selected.
        """
        spot = self.is_spot_purchase_selected()
        gift = self.is_gift_item_selected()
        expected_spot = sub_type != "gift"
        assert spot == expected_spot and gift == (not expected_spot), (
            f"Expected only the '{sub_type}' radio button to be selected "
            f"but Spot Purchase selected = {spot} and Gift Item selected = {gift}."
        )

    def read_remarks(self) -> str:
        """Return the text currently in the Note/Remarks box."""
        action_logger.info("Read value of: Note/Remarks field")
        return self.remarks_field.input_value()

    def verify_registration_date_format(self) -> None:
        """Check that the Registration Date is a dd/mm/yyyy date; fail with the value found."""
        registration_date = self.read_registration_date()
        assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", registration_date), (
            f"Expected a dd/mm/yyyy Registration Date but found '{registration_date}'."
        )

    def verify_item_classification_filled(self) -> None:
        """Check that Category, Sub Category, Group and Unit are all filled in after an item is picked."""
        classification = self.read_item_classification()
        for name in classification:
            value = classification[name]
            assert value != "" and value != "-Select-", (
                f"Expected {name} to be filled in but it was '{value}'."
            )

    def verify_asset_block_cleared(self) -> None:
        """Check that Item Specification, Unit Price and Measurement are empty after the block is reset."""
        values = self.read_asset_block_values()
        for name in ["item_specification", "unit_price", "measurement"]:
            assert values[name] == "", (
                f"Expected {name} to be cleared after Reset but found '{values[name]}'."
            )

    def create_draft(self, data: dict) -> None:
        """Fill the form and save it as a Draft, checking the success toast."""
        self.fill_registration_form(data)
        self.draft_and_verify_success()

    def create_and_submit(self, data: dict) -> None:
        """Fill the form and submit it for approval, checking the success toast."""
        self.fill_registration_form(data)
        self.submit_and_verify_success()

    def draft_and_verify_success(self) -> None:
        """
        Click Draft and confirm the exact success toast is shown.
        Fails with the toast's actual text if anything else appears.
        """
        self.wait_for_toast_to_clear()
        self.click(self.draft_button, "Draft button")
        toast_text = self.get_toast_text()
        expected = "Asset registration(AAQ) drafted Successfully!"
        assertion_logger.info("Verifying Draft success toast")
        assert toast_text == expected, (
            f"Expected Draft toast '{expected}' but found '{toast_text}'."
        )
        assertion_logger.info("Draft success toast matched exactly")

    def submit_and_verify_success(self) -> None:
        """
        Click Submit and confirm the exact success toast is shown.
        Fails with the toast's actual text if anything else appears.
        """
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        toast_text = self.get_toast_text()
        expected = "Asset registration(AAQ) submitted Successfully!"
        assertion_logger.info("Verifying Submit success toast")
        assert toast_text == expected, (
            f"Expected Submit toast '{expected}' but found '{toast_text}'."
        )
        assertion_logger.info("Submit success toast matched exactly")
