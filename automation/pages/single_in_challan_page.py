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
from utils.helpers import challan_row_problems
from utils.logger import assertion_logger


class SingleInChallanPage(SingleChallanListPage):
    """Page object for the Asset Single In-Challan screen."""

    MENU_LINK = "Asset Single In-Challan"

    def __init__(self, page):
        super().__init__(page)
        # Acknowledge button of the challan popup
        self.acknowledge_button = page.locator("#acknowledge")
        # Loading overlay that covers the page for a few seconds after Acknowledge
        self.modal_loader = page.locator(".modalLoader")

    def verify_row_matches_challan(self, out_challan_no: str, challan_data: dict, sending_branch: str) -> None:
        """
        Confirm the challan's row shows what the challan was created with: status
        APPROVED, an In Challan Number, the From and To Project, the Sending Branch
        (`sending_branch` is the text the Create Challan popup showed) and the
        Receiving Branch (`challan_data["receiving_branch"]`). Names every difference in one message.
        """
        row = self.read_row(out_challan_no)
        assertion_logger.info(f"Verifying the Single In-Challan row of {out_challan_no} against the challan that was created")
        problems = challan_row_problems(row, challan_data, sending_branch, "Status", "In Challan Number")
        if problems:
            raise AssertionError(f"The Single In-Challan row of {out_challan_no} differs from the challan: {problems}")

    def read_popup_actions(self) -> list:
        """Return the names of the action buttons visible in the popup, among Acknowledge."""
        actions = []
        if self.acknowledge_button.is_visible():
            actions.append("Acknowledge")
        return actions

    def acknowledge_and_get_message(self) -> str:
        """
        Click Acknowledge in the popup, wait until the loading overlay is gone and return the message
        the ERP showed (an empty text when no message was seen). The caller searches again and checks
        the row with `verify_acknowledged`.
        """
        self.click(self.acknowledge_button, "Acknowledge button")
        message = self.get_toast_text_or_empty()
        expect(self.modal_loader.first).to_be_hidden(timeout=POPUP_TIMEOUT)
        return message

    def verify_acknowledged(self, out_challan_no: str, erp_message: str) -> None:
        """
        Confirm Acknowledge worked the way it does inside one branch: the row shows ACKNOWLEDGED and
        a Preview link. The failure names the status found and the message the ERP showed.
        """
        status = self.read_row(out_challan_no).get("Status", "")
        assertion_logger.info(f"Verifying challan {out_challan_no} was acknowledged")
        if status != "ACKNOWLEDGED":
            raise AssertionError(
                f"Acknowledge did not work: challan {out_challan_no} has status '{status}' instead of "
                f"'ACKNOWLEDGED'. The message the ERP showed: '{erp_message}'."
            )
        if not self.row_has_preview_link(out_challan_no):
            raise AssertionError(f"Challan {out_challan_no} is ACKNOWLEDGED but its row has no Preview link.")

    def acknowledge(self) -> None:
        """
        Click Acknowledge in the popup and wait until the loading overlay that
        follows it is gone. No message is checked, because the success message
        has not been confirmed; callers search again and check the row status
        with verify_row_status.
        """
        self.click(self.acknowledge_button, "Acknowledge button")
        expect(self.modal_loader.first).to_be_hidden(timeout=POPUP_TIMEOUT)
