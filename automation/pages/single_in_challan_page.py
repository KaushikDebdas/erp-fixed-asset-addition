"""
SingleInChallanPage: Asset Single In-Challan (Fixed Asset > Single Challan >
Asset Single In-Challan).

Lists the approved challans waiting to be acknowledged by the receiving side.
The challan is opened from its Out Challan Number link and acknowledged in the
popup. The grid and the popup come from `SingleChallanListPage`.
See `automation/element_catalog/asset_single_in_challan.md`.
"""
from playwright.sync_api import expect

from pages.single_challan_list_page import POPUP_TIMEOUT, SingleChallanListPage


class SingleInChallanPage(SingleChallanListPage):
    """Page object for the Asset Single In-Challan screen."""

    MENU_LINK = "Asset Single In-Challan"

    def __init__(self, page):
        super().__init__(page)
        # Acknowledge button of the challan popup
        self.acknowledge_button = page.locator("#acknowledge")
        # Loading overlay that covers the page for a few seconds after Acknowledge
        self.modal_loader = page.locator(".modalLoader")

    def read_popup_actions(self) -> list:
        """Return the names of the action buttons visible in the popup, among Acknowledge."""
        actions = []
        if self.acknowledge_button.is_visible():
            actions.append("Acknowledge")
        return actions

    def acknowledge(self) -> None:
        """
        Click Acknowledge in the popup and wait until the loading overlay that
        follows it is gone. No message is checked, because the success message
        has not been confirmed; callers search again and check the row status
        with verify_row_status.
        """
        self.click(self.acknowledge_button, "Acknowledge button")
        expect(self.modal_loader.first).to_be_hidden(timeout=POPUP_TIMEOUT)
