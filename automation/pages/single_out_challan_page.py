"""
SingleOutChallanPage: Asset Single Out Challan (Fixed Asset > Single Challan >
Asset Single Out Challan).

Create a challan (Draft or Submit), open a Draft with its Edit link, open a
challan from its Out Challan Number and add the asset serial with "Add Serial".
The grid and the challan popup come from `SingleChallanListPage`.
See `automation/element_catalog/asset_single_out_challan.md`.
"""
from playwright.sync_api import expect

from pages.single_challan_list_page import POPUP_TIMEOUT, SingleChallanListPage
from test_data.toast_messages import SINGLE_CHALLAN_SERIAL_ADDED_TOAST
from utils.logger import action_logger


class SingleOutChallanPage(SingleChallanListPage):
    """Page object for the Asset Single Out Challan screen."""

    MENU_LINK = "Asset Single Out Challan"

    def __init__(self, page):
        super().__init__(page)
        # Create button above the grid
        self.create_button = page.locator("a.btn", has_text="Create")
        # Create / Edit Challan popup
        self.challan_popup = page.locator("#challanResponsiveSingleChallan")
        self.challan_number_field = self.challan_popup.locator("#challanNumber")
        self.sending_branch_chosen = self.challan_popup.locator("#s2id_office .select2-chosen")
        self.note_field = self.challan_popup.locator("#remarks")
        self.quantity_field = self.challan_popup.locator("#quantity")
        self.add_item_button = self.challan_popup.locator("#addToAssetItemGrid")
        self.item_rows = self.challan_popup.locator("#assetItemsTable tbody tr").filter(has_not_text="No data available")
        self.draft_button = self.challan_popup.locator("#createChallan")
        self.submit_button = self.challan_popup.locator("#submitChallan")
        # Add Serial link of the challan popup's item row
        self.add_serial_link = self.popup.get_by_role("link", name="Add Serial").first
        # Add Asset Serial popup
        self.serial_popup = page.locator("#addAssetSerialModal")
        self.serial_add_button = self.serial_popup.locator("a.btn", has_text="Add")
        self.serial_save_button = self.serial_popup.locator("#saveAssetSerial")
        self.serial_rows = self.serial_popup.locator("#assetSerialItemAdditionTable tbody tr").filter(
            has_not_text="No data available"
        )
        # Asset Serials tab of the challan popup
        self.serials_tab = self.popup.locator(".nav-tabs a", has_text="Asset Serials")
        self.serials_table = self.popup.locator("#assetSerialTable")

    # ---- Create / Edit popup ----------------------------------------------

    def click_create(self) -> None:
        """Click Create and wait until the Create Challan popup is shown."""
        self.click(self.create_button, "Create button")
        self.wait_until_visible(self.challan_number_field, "Create Challan popup")

    def fill_challan_form(self, data: dict) -> None:
        """
        Fill the Create Challan popup from `data` (see build_challan_data in
        test_data/asset_shipment_data.py) and add the item line to the grid.
        The Sending Branch is already the user's branch.
        """
        self.choose_from_select2("#s2id_fromProject", data["from_project"], data["from_project"])
        self.choose_from_select2("#s2id_destinationBranch", data["receiving_branch_search"], data["receiving_branch"])
        self.choose_from_select2("#s2id_destinationProject", data["to_project_search"], data["to_project"])
        self.choose_from_select2("#s2id_asset", data["item_search"], data["item_name"])
        self.type_text(self.quantity_field, str(data["quantity"]), "Quantity")
        self.type_text(self.note_field, data["note"], "Challan Note")
        self.add_item_line()

    def add_item_line(self) -> None:
        """Click Add and wait until the new line shows in the item grid."""
        lines_before = self.item_rows.count()
        self.click(self.add_item_button, "Add item button")
        expect(self.item_rows).to_have_count(lines_before + 1, timeout=POPUP_TIMEOUT)

    def draft(self) -> None:
        """Click Draft; the popup closes and the challan is listed as DRAFT (no message is shown)."""
        self.click(self.draft_button, "Draft button")
        expect(self.challan_popup).to_be_hidden(timeout=POPUP_TIMEOUT)

    def submit(self) -> None:
        """Click Submit; the popup closes and the challan is listed as PENDING (no message is shown)."""
        self.click(self.submit_button, "Submit button")
        expect(self.challan_popup).to_be_hidden(timeout=POPUP_TIMEOUT)

    def open_draft_for_edit(self, out_challan_no: str) -> None:
        """Click Edit on the row of a Draft challan and wait until its popup (with Update and Submit) is shown."""
        row = self._row_for(out_challan_no)
        self.wait_until_visible(row, f"grid row of {out_challan_no}")
        self.click(row.get_by_role("link", name="Edit", exact=True), f"Edit link of {out_challan_no}")
        self.wait_until_visible(self.submit_button, "Edit Challan popup")

    # ---- Add Serial ---------------------------------------------------------

    def add_serial(self, serial: str) -> None:
        """
        In the open challan popup: click Add Serial, choose `serial` in the
        Serial No box, click Add, click Save and confirm the message, then close
        the challan popup.
        """
        self.click(self.add_serial_link, "Add Serial link")
        self.wait_until_visible(self.serial_popup, "Add Asset Serial popup")
        self.choose_from_select2("#s2id_assetSerialSelect", serial, serial)
        lines_before = self.serial_rows.count()
        self.click(self.serial_add_button, "Add serial button")
        expect(self.serial_rows).to_have_count(lines_before + 1, timeout=POPUP_TIMEOUT)
        self.wait_for_toast_to_clear()
        self.click(self.serial_save_button, "Save serial button")
        self.verify_toast_text(self.get_toast_text(), SINGLE_CHALLAN_SERIAL_ADDED_TOAST, "saving the serial")
        expect(self.serial_popup).to_be_hidden(timeout=POPUP_TIMEOUT)
        self.close_popup()

    def read_serials(self) -> list:
        """Open the Asset Serials tab of the open challan popup and return the Asset Serial of every row."""
        self.click(self.serials_tab, "Asset Serials tab")
        self.wait_until_visible(self.serials_table, "Asset Serials table")
        serials = []
        rows = self.serials_table.locator("tbody tr").filter(has_not_text="No data available")
        for index in range(rows.count()):
            serials.append(rows.nth(index).locator("td:visible").nth(1).inner_text().strip())
        action_logger.info(f"Serials on the challan: {serials}")
        return serials
