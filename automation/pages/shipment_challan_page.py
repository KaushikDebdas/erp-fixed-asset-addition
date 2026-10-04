"""
ShipmentChallanPage: the Transfer Challans part of the Asset Shipment screen.

Works on the same browser tab as `AssetShipmentPage`. It assumes the Shipment
Details popup (`#commonModal`) is already open. On top of it this page object
drives:
    - the Transfer Challans tab and its challan list
    - the Create / Update Challan popup (`#challanResponsive`)
    - the Challan Details popup (`#challanDetailsModal`)
    - the Add Asset Serial popup (`#addAssetSerialModal`)

Several popups exist in the page at the same time, so every locator is
scoped to the popup that holds it.

Facts used here come from automation/element_catalog/asset_shipment.md.
"""
from playwright.sync_api import expect

from pages.asset_shipment_page import (
    NO_DATA_TEXT,
    POPUP_TIMEOUT,
    check_toast_lines,
    read_field_value,
    read_headings,
    row_to_dict,
    table_rows_to_dicts,
)
from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger


class ShipmentChallanPage(BasePage):
    """Page object for the Transfer Challans tab and the challan popups of a shipment."""

    def __init__(self, page):
        super().__init__(page)

        # ---- Shipment Details popup: Transfer Challans tab ----
        # The Shipment Details popup that holds the tabs
        self.shipment_modal = page.locator("#commonModal")
        # LOCATOR_REQUIRES_REVIEW: the tab element type is not recorded in the catalog;
        # standard Bootstrap tab links inside the popup are assumed
        self.shipment_tabs = self.shipment_modal.locator(".nav-tabs a")
        # Create button that opens the Create Challan popup
        self.create_challan_button = page.locator("#addChallanBtn")
        # Challan list of the shipment
        self.challan_list = page.locator("#challanListTable")

        # ---- Create / Update Challan popup ----
        # The popup itself
        self.challan_popup = page.locator("#challanResponsive")
        # Out Challan No (shows AUTO until drafted)
        self.out_challan_no_field = self.challan_popup.locator("#outChallanNo")
        # Sending Branch (read-only)
        self.sending_branch_field = self.challan_popup.locator("#fromBranchId")
        # Out Challan Date (read-only)
        self.challan_date_field = self.challan_popup.locator("#faOutChallanDate")
        # Hidden native dropdowns behind the From Project, Receiving Branch and To Project boxes
        self.from_project_select = self.challan_popup.locator("#fromProject")
        self.receiving_branch_select = self.challan_popup.locator("#toOffice")
        self.to_project_select = self.challan_popup.locator("#toProject")
        # Note box
        self.note_field = self.challan_popup.locator("#challanRemarks")
        # Chosen text of the Asset Item Name box and its hidden native dropdown
        # LOCATOR_REQUIRES_REVIEW: the `.select2-chosen` text element is not recorded in the catalog
        self.asset_item_chosen_text = self.challan_popup.locator("#s2id_asset .select2-chosen")
        self.asset_item_select = self.challan_popup.locator("#asset")
        # Read-only item classification boxes filled after an item is chosen
        self.category_field = self.challan_popup.locator("#assetCategory")
        self.sub_category_field = self.challan_popup.locator("#assetSubCategory")
        self.group_field = self.challan_popup.locator("#assetGroup")
        self.unit_field = self.challan_popup.locator("#uom")
        # Quantity box
        # LOCATOR_REQUIRES_REVIEW: the catalog lists Quantity among the read-only boxes; it is typed into here
        self.quantity_field = self.challan_popup.locator("#quantity")
        # Add button that puts the item line in the grid
        self.add_item_button = self.challan_popup.locator("#addToAssetItemGrid")
        # Grid of added item lines, and only its real rows (not the "No data" row)
        self.item_grid = self.challan_popup.locator("#assetItemsTable")
        self.item_rows = self.item_grid.locator("tbody tr").filter(has_not_text=NO_DATA_TEXT)
        # Popup buttons
        self.draft_button = self.challan_popup.locator("#createChallan")
        self.submit_button = self.challan_popup.locator("#submitChallan")
        self.reset_button = self.challan_popup.locator("#resetChalan")
        self.update_button = self.challan_popup.locator("#updateChallan")
        self.delete_button = self.challan_popup.locator("#deleteChallan")
        # LOCATOR_REQUIRES_REVIEW: the Update Challan popup is assumed to be the same container (#challanResponsive)
        self.challan_close_button = self.challan_popup.locator(".btn:visible", has_text="Close")

        # ---- Challan Details popup ----
        # The popup itself
        self.details_modal = page.locator("#challanDetailsModal")
        # Tab links of the popup: Details, Asset Serials, Posted Accounts
        # LOCATOR_REQUIRES_REVIEW: the tab element type is not recorded; standard Bootstrap tab links are assumed
        self.details_tabs = self.details_modal.locator(".nav-tabs a")
        # Read-only fields of the Challan Details popup
        self.details_out_challan_no = self.details_modal.locator("#outChallanNoDetails")
        self.details_out_challan_date = self.details_modal.locator("#outChallanDateDetails")
        self.details_from_project = self.details_modal.locator("#fromProjectDetails")
        self.details_to_project = self.details_modal.locator("#toProjectDetails")
        self.details_status = self.details_modal.locator("#status")
        self.details_from_branch = self.details_modal.locator("#fromBranchDetails")
        self.details_to_branch = self.details_modal.locator("#toBranchDetails")
        # Item grid of the Details tab, and the Add Serial link in its item row
        self.details_item_grid = self.details_modal.locator("#assetItemsTableDetails")
        self.add_serial_link = self.details_item_grid.get_by_role("link", name="Add Serial").first
        # Grid of the Asset Serials tab
        # LOCATOR_REQUIRES_REVIEW: the column headings of this grid are not recorded; a heading containing "Asset Serial" is assumed
        self.asset_serials_table = self.details_modal.locator("#assetSerialTableShipmentChallan")
        # Close button of the Challan Details popup
        self.details_close_button = self.details_modal.locator(".btn:visible", has_text="Close")

        # ---- Add Asset Serial popup ----
        # The popup itself
        self.serial_popup = page.locator("#addAssetSerialModal")
        # LOCATOR_REQUIRES_REVIEW: the Serial No dropdown box id is not recorded; the same naming
        # as the other dropdown boxes (#s2id_ + select id) is assumed
        self.serial_dropdown_css = "#s2id_assetSerialSelect"
        # Read-only boxes filled after a serial is chosen
        self.serial_item_name = self.serial_popup.locator("#addItemName")
        self.serial_quantity = self.serial_popup.locator("#addItemQuantity")
        self.serial_sub_category = self.serial_popup.locator("#addSubCategory")
        self.serial_category = self.serial_popup.locator("#addCategory")
        # Add button that puts the serial in the popup grid
        self.serial_add_button = self.serial_popup.locator("#addChallanSerial")
        # Save button (it reuses the id createChallan, so it is found inside the popup by its text)
        self.serial_save_button = self.serial_popup.locator("#createChallan", has_text="Save")
        # Grid of serials added in the popup, and only its real rows
        self.serial_grid = self.serial_popup.locator("#assetSerialItemAdditionTable")
        self.serial_rows = self.serial_grid.locator("tbody tr").filter(has_not_text=NO_DATA_TEXT)

    # ------------------------------------------------------------------
    # Shared helper for the dropdown boxes
    # ------------------------------------------------------------------

    def choose_from_dropdown(self, container_css: str, search_text: str, option_text: str) -> None:
        """
        Choose a value in one of the search dropdown boxes (From Project,
        Receiving Branch, To Project, Asset Item, Serial No): click the box,
        type `search_text` in its search field, then click the result whose
        text contains `option_text`. Choosing through the hidden native
        dropdown does not work, so this is the one way every box is filled.
        """
        action_logger.info(f"Choose in dropdown {container_css}: {option_text}")
        box = self.page.locator(container_css)
        self.click(box.locator("a.select2-choice"), f"{container_css} box")
        search_field = self.page.locator(".select2-drop-active:visible input.select2-input")
        self.wait_until_visible(search_field, "dropdown search field")
        self.type_text(search_field, search_text, "dropdown search field")
        option = self.page.locator(".select2-drop-active:visible .select2-result-label", has_text=option_text).first
        self.wait_until_visible(option, f"dropdown result {option_text}")
        self.click(option, f"dropdown result {option_text}")

    # ------------------------------------------------------------------
    # Transfer Challans tab and the Create Challan popup
    # ------------------------------------------------------------------

    def open_transfer_challans_tab(self) -> None:
        """Open the Transfer Challans tab of the open Shipment Details popup and wait for its Create button."""
        tab = self.shipment_tabs.filter(has_text="Transfer Challans")
        self.click(tab, "Transfer Challans tab")
        self.wait_until_visible(self.create_challan_button, "Create challan button")

    def click_create_challan(self) -> None:
        """Click Create on the Transfer Challans tab and wait until the Create Challan popup is ready."""
        self.click(self.create_challan_button, "Create challan button")
        self.wait_until_visible(self.out_challan_no_field, "Create Challan popup")

    def read_challan_popup_defaults(self) -> dict:
        """Return what the open Create Challan popup is pre-filled with: keys out_challan_no, sending_branch, challan_date."""
        # Until the challan is saved the Out Challan No box is empty and only
        # shows the hint AUTO (its placeholder)
        out_challan_no = read_field_value(self.out_challan_no_field)
        if out_challan_no == "":
            out_challan_no = self.out_challan_no_field.get_attribute("placeholder")
        return {
            "out_challan_no": out_challan_no,
            "sending_branch": read_field_value(self.sending_branch_field),
            "challan_date": read_field_value(self.challan_date_field),
        }

    def choose_from_project(self, project_text: str) -> None:
        """Choose the From Project, e.g. '[015] Microfinance (Dabi)'."""
        self.choose_from_dropdown("#s2id_fromProject", project_text, project_text)

    def choose_receiving_branch(self, text: str) -> None:
        """Choose the Receiving Branch, e.g. '[HO - BDHO] Head Office'."""
        self.choose_from_dropdown("#s2id_toOffice", text, text)

    def choose_to_project(self, text: str) -> None:
        """Choose the To Project, e.g. '[060] Progoti'."""
        self.choose_from_dropdown("#s2id_toProject", text, text)

    def choose_asset_item(self, search_text: str, option_text: str) -> None:
        """Search the Asset Item Name box with `search_text` (e.g. 'Cabinet') and click the result containing `option_text`."""
        self.choose_from_dropdown("#s2id_asset", search_text, option_text)

    def read_item_classification(self) -> dict:
        """
        Wait until the chosen asset item has filled the classification boxes, then
        return them: keys category, sub_category, group, unit.
        """
        expect(self.category_field).not_to_have_value("", timeout=POPUP_TIMEOUT)
        expect(self.unit_field).not_to_have_value("", timeout=POPUP_TIMEOUT)
        return {
            "category": read_field_value(self.category_field),
            "sub_category": read_field_value(self.sub_category_field),
            "group": read_field_value(self.group_field),
            "unit": read_field_value(self.unit_field),
        }

    def enter_quantity(self, quantity: int) -> None:
        """Type the Quantity of the item line."""
        self.type_text(self.quantity_field, str(quantity), "Quantity")

    def enter_note(self, text: str) -> None:
        """Type the optional Note of the challan."""
        self.type_text(self.note_field, text, "Note")

    def add_item_line(self) -> None:
        """Click Add and wait until the new line shows in the item grid."""
        lines_before = self.item_rows.count()
        self.click(self.add_item_button, "Add item button")
        expect(self.item_rows).to_have_count(lines_before + 1, timeout=POPUP_TIMEOUT)

    def click_add_and_get_toast(self) -> str:
        """Click Add and return the toast text; used when Add is expected to refuse (e.g. 'Please select to project')."""
        self.wait_for_toast_to_clear()
        self.click(self.add_item_button, "Add item button")
        return self.get_toast_text()

    def read_item_lines(self) -> list:
        """Return the lines of the item grid as a list of dicts keyed by heading (Asset Item Name, Quantity, ...)."""
        return table_rows_to_dicts(self.item_grid)

    def remove_first_item_line(self) -> None:
        """Click Remove on the first item line and wait until one line fewer is shown."""
        lines_before = self.item_rows.count()
        remove_link = self.item_rows.first.get_by_role("link", name="Remove")
        self.click(remove_link, "Remove item line")
        expect(self.item_rows).to_have_count(lines_before - 1, timeout=POPUP_TIMEOUT)

    def verify_item_grid_is_empty(self) -> None:
        """Confirm the item grid has no lines."""
        found = self.item_rows.count()
        assertion_logger.info("Verifying the item grid is empty")
        if found != 0:
            raise AssertionError(f"Expected the item grid to be empty but found {found} line(s).")

    def read_item_fields_after_remove(self) -> dict:
        """
        Return the item fields: keys asset_item_text (chosen text of the Asset
        Item Name box), asset_item_value (its hidden dropdown value) and quantity.
        After removing a line the value and quantity are empty.
        """
        return {
            "asset_item_text": self.asset_item_chosen_text.inner_text().strip(),
            "asset_item_value": self.asset_item_select.input_value().strip(),
            "quantity": self.quantity_field.input_value().strip(),
        }

    def draft_and_get_toast(self) -> str:
        """Click Draft on the Create Challan popup and return the toast text (expected: 'Challan drafted successfully')."""
        self.wait_for_toast_to_clear()
        self.click(self.draft_button, "Draft button")
        return self.get_toast_text()

    def submit_and_get_toast(self) -> str:
        """Click Submit on the Create Challan popup and return the toast text."""
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        return self.get_toast_text()

    def reset_challan_form(self) -> None:
        """Click Reset on the Create Challan popup, which clears the form."""
        self.click(self.reset_button, "Reset button")

    def close_challan_popup(self) -> None:
        """Close the Create or Update Challan popup and wait until it is gone."""
        self.click(self.challan_close_button, "Close button")
        expect(self.challan_popup).to_be_hidden(timeout=POPUP_TIMEOUT)

    # ------------------------------------------------------------------
    # Challan list on the Transfer Challans tab
    # ------------------------------------------------------------------

    def read_challan_numbers(self) -> list:
        """Return the Out Challan No of every row in the challan list (empty list when there is none)."""
        numbers = []
        for row in self.read_challan_rows():
            for heading in row:
                if "Out Challan No" in heading:
                    numbers.append(row[heading])
        return numbers

    def find_new_challan_no(self, numbers_before: list) -> str:
        """
        Return the Out Challan No that was added to the list after `numbers_before`
        was read. Waits until the list has one more row, then returns the number
        that was not there before. Out Challan Numbers do not grow in creation
        order, so the newest one cannot be found by comparing the numbers.
        Raises AssertionError when no new number shows.
        """
        expected_rows = len(numbers_before) + 1
        expect(self.challan_list.locator("tbody tr")).to_have_count(expected_rows, timeout=POPUP_TIMEOUT)
        for number in self.read_challan_numbers():
            if number not in numbers_before:
                return number
        raise AssertionError(f"Expected a new challan after {numbers_before} but the list shows {self.read_challan_numbers()}.")

    def read_challan_rows(self) -> list:
        """Return every row of the challan list as a dict keyed by column heading (empty list when none)."""
        return table_rows_to_dicts(self.challan_list)

    def get_newest_challan_no(self) -> str:
        """
        Return the newest Out Challan No in the list: the one whose last number
        is the highest (e.g. OC-BBDSHP00000009-594 ends in 594).
        Raises AssertionError when the list is empty.
        """
        rows = self.read_challan_rows()
        if len(rows) == 0:
            raise AssertionError("Expected at least one challan row but the challan list shows no data.")
        heading = rows[0]
        challan_heading = ""
        for name in heading:
            if "Out Challan No" in name:
                challan_heading = name
        if challan_heading == "":
            raise AssertionError(f"Expected an 'Out Challan No' column but the headings are {list(heading)}.")
        newest = ""
        newest_number = -1
        for row in rows:
            challan_no = row[challan_heading]
            number = int(challan_no.split("-")[-1])
            if number > newest_number:
                newest_number = number
                newest = challan_no
        action_logger.info(f"Newest challan number in list: {newest}")
        return newest

    def read_challan_row(self, challan_no: str) -> dict:
        """Return the list row of one challan as a dict keyed by column heading. Raises AssertionError when there is none."""
        self.wait_for_row_or_no_data(self.challan_list, challan_no)
        row = self.challan_list.locator("tbody tr", has_text=challan_no)
        if row.count() == 0:
            raise AssertionError(f"Expected a challan row for {challan_no} but the challan list shows none.")
        return row_to_dict(read_headings(self.challan_list), row.first)

    def verify_challan_status(self, challan_no: str, expected_status: str) -> None:
        """Confirm the challan list row shows `expected_status` (DRAFT, PENDING, APPROVED, ACKNOWLEDGED)."""
        found = self.read_challan_row(challan_no)["Status"]
        assertion_logger.info(f"Verifying challan {challan_no} has Status {expected_status}")
        if found != expected_status:
            raise AssertionError(f"Expected challan {challan_no} to have Status '{expected_status}' but found '{found}'.")

    def verify_all_serial_added(self, challan_no: str, expected_value: str) -> None:
        """Confirm the challan list column 'All Serial Added' shows `expected_value` ('Yes' or 'No')."""
        found = self.read_challan_row(challan_no)["All Serial Added"]
        assertion_logger.info(f"Verifying challan {challan_no} has All Serial Added {expected_value}")
        if found != expected_value:
            raise AssertionError(
                f"Expected challan {challan_no} to have All Serial Added '{expected_value}' but found '{found}'."
            )

    # ------------------------------------------------------------------
    # Challan Details popup
    # ------------------------------------------------------------------

    def open_challan_details(self, challan_no: str) -> None:
        """Click the Out Challan No link in the list and wait until the Challan Details popup shows."""
        self.wait_for_row_or_no_data(self.challan_list, challan_no)
        row = self.challan_list.locator("tbody tr", has_text=challan_no)
        self.click(row.get_by_role("link", name=challan_no, exact=True), f"Out Challan No {challan_no} link")
        self.wait_until_visible(self.details_out_challan_no, "Challan Details popup")

    def read_challan_details_values(self) -> dict:
        """
        Return the read-only fields of the Challan Details popup: keys out_challan_no,
        out_challan_date, from_project, to_project, status, from_branch, to_branch.
        """
        return {
            "out_challan_no": read_field_value(self.details_out_challan_no),
            "out_challan_date": read_field_value(self.details_out_challan_date),
            "from_project": read_field_value(self.details_from_project),
            "to_project": read_field_value(self.details_to_project),
            "status": read_field_value(self.details_status),
            "from_branch": read_field_value(self.details_from_branch),
            "to_branch": read_field_value(self.details_to_branch),
        }

    def read_challan_details_tab_names(self) -> list:
        """Return the tab names of the Challan Details popup, e.g. ['Details', 'Asset Serials', 'Posted Accounts']."""
        names = []
        for text in self.details_tabs.all_inner_texts():
            names.append(text.strip())
        return names

    def open_challan_details_tab(self, name: str) -> None:
        """Click a tab of the Challan Details popup ('Details', 'Asset Serials' or 'Posted Accounts')."""
        tab = self.details_tabs.filter(has_text=name)
        self.click(tab, f"{name} tab")

    def read_asset_serials_tab(self) -> list:
        """Open the Asset Serials tab and return the serial numbers listed there (empty list when none)."""
        self.open_challan_details_tab("Asset Serials")
        self.wait_until_visible(self.asset_serials_table, "Asset Serials grid")
        rows = table_rows_to_dicts(self.asset_serials_table)
        serials = []
        for row in rows:
            serial_heading = ""
            for heading in row:
                if "Asset Serial" in heading:
                    serial_heading = heading
            if serial_heading == "":
                raise AssertionError(f"Expected an 'Asset Serial' column but the headings are {list(row)}.")
            serials.append(row[serial_heading])
        return serials

    def close_challan_details(self) -> None:
        """Close the Challan Details popup and wait until it is gone."""
        self.click(self.details_close_button, "Close button")
        expect(self.details_modal).to_be_hidden(timeout=POPUP_TIMEOUT)

    # ------------------------------------------------------------------
    # Add Asset Serial popup
    # ------------------------------------------------------------------

    def click_add_serial_link(self) -> None:
        """On the Details tab of Challan Details click the Add Serial link of the item row and wait for the popup."""
        self.open_challan_details_tab("Details")
        self.wait_until_visible(self.add_serial_link, "Add Serial link")
        self.click(self.add_serial_link, "Add Serial link")
        self.wait_until_visible(self.serial_add_button, "Add Asset Serial popup")

    def choose_serial(self, serial_no: str) -> None:
        """Choose an Asset Serial No in the Add Asset Serial popup by searching for it."""
        self.choose_from_dropdown(self.serial_dropdown_css, serial_no, serial_no)

    def read_serial_popup_values(self) -> dict:
        """
        Wait until the chosen serial has filled the read-only boxes, then return
        them: keys item_name, quantity, sub_category, category.
        """
        expect(self.serial_item_name).not_to_have_value("", timeout=POPUP_TIMEOUT)
        return {
            "item_name": read_field_value(self.serial_item_name),
            "quantity": read_field_value(self.serial_quantity),
            "sub_category": read_field_value(self.serial_sub_category),
            "category": read_field_value(self.serial_category),
        }

    def add_serial_to_popup_grid(self) -> None:
        """Click Add (no toast is shown) and wait until the serial shows in the popup grid."""
        rows_before = self.serial_rows.count()
        self.click(self.serial_add_button, "Add serial button")
        expect(self.serial_rows).to_have_count(rows_before + 1, timeout=POPUP_TIMEOUT)

    def read_serial_popup_grid(self) -> list:
        """Return the serials in the Add Asset Serial popup grid as a list of dicts keyed by heading."""
        return table_rows_to_dicts(self.serial_grid)

    def remove_first_serial_in_popup(self) -> None:
        """Click Remove on the first serial of the popup grid and wait until one row fewer is shown."""
        rows_before = self.serial_rows.count()
        remove_link = self.serial_rows.first.get_by_role("link", name="Remove")
        self.click(remove_link, "Remove serial")
        expect(self.serial_rows).to_have_count(rows_before - 1, timeout=POPUP_TIMEOUT)

    def save_serial_and_get_toast(self) -> str:
        """Click Save in the Add Asset Serial popup and return the toast text (expected: 'Asset serial added Successfuly')."""
        self.wait_for_toast_to_clear()
        self.click(self.serial_save_button, "Save serial button")
        return self.get_toast_text()

    # ------------------------------------------------------------------
    # Update Challan popup (Edit link of a Draft challan)
    # ------------------------------------------------------------------

    def open_update_challan(self, challan_no: str) -> None:
        """Click the Edit link of a challan's row and wait until the Update Challan popup is ready."""
        self.wait_for_row_or_no_data(self.challan_list, challan_no)
        row = self.challan_list.locator("tbody tr", has_text=challan_no)
        self.click(row.get_by_role("link", name="Edit"), f"Edit link of {challan_no}")
        self.wait_until_visible(self.update_button, "Update Challan popup Update button")

    def find_editable_fixed_fields(self) -> list:
        """
        Return the names of the fields that must be read-only in the Update Challan
        popup (Sending Branch, Receiving Branch, From Project, To Project, Date)
        but can still be edited. An empty list means they are all read-only.
        """
        fields = {
            "Sending Branch": self.sending_branch_field,
            "Receiving Branch": self.receiving_branch_select,
            "From Project": self.from_project_select,
            "To Project": self.to_project_select,
            "Out Challan Date": self.challan_date_field,
        }
        editable = []
        for name in fields:
            is_locked = fields[name].evaluate("element => element.readOnly || element.disabled")
            if not is_locked:
                editable.append(name)
        return editable

    def is_update_popup_read_only(self) -> bool:
        """Return True when the branches, projects and date of the Update Challan popup are all read-only."""
        return len(self.find_editable_fixed_fields()) == 0

    def verify_update_popup_read_only(self) -> None:
        """Confirm the branches, projects and date of the Update Challan popup are read-only."""
        editable = self.find_editable_fixed_fields()
        assertion_logger.info("Verifying the Update Challan popup fields are read-only")
        if len(editable) != 0:
            raise AssertionError(f"Expected these fields to be read-only but they can be edited: {editable}.")

    def submit_update_challan_and_get_toast(self) -> str:
        """Click Submit on the Update Challan popup and return the toast text (expected: 'Challan submitted successfully')."""
        self.wait_for_toast_to_clear()
        self.click(self.submit_button, "Submit button")
        return self.get_toast_text()

    def delete_update_challan_and_get_toast(self) -> str:
        """Click Delete on the Update Challan popup (no confirmation) and return the toast text (expected: 'Challan deleted successfuly')."""
        self.wait_for_toast_to_clear()
        self.click(self.delete_button, "Delete button")
        return self.get_toast_text()

    def verify_toast(self, found_text: str, expected_lines: list) -> None:
        """
        Confirm a toast text (returned by a *_and_get_toast method) has exactly
        `expected_lines`, e.g. ['Challan drafted successfully'].
        """
        check_toast_lines(found_text, expected_lines)
