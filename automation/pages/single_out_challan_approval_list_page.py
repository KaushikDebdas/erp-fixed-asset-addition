"""
SingleOutChallanApprovalListPage: Asset Single Out Challan Approval List (Fixed
Asset > Single Challan > Asset Single Out Challan Approval List).

A PENDING challan is opened from its Out Challan Number link; the popup has a
Comment and the Approve, Reject and Sendback buttons. Approve also generates
the gate pass. The grid and the popup come from `SingleChallanListPage`.
See `automation/element_catalog/asset_single_out_challan_approval_list.md`.
"""
from pages.single_challan_list_page import SingleChallanListPage
from test_data.toast_messages import SINGLE_CHALLAN_APPROVE_TOAST


class SingleOutChallanApprovalListPage(SingleChallanListPage):
    """Page object for the Asset Single Out Challan Approval List screen."""

    MENU_LINK = "Asset Single Out Challan Approval List"

    def __init__(self, page):
        super().__init__(page)
        # Comment box and the three action buttons of the challan popup
        self.comment_box = page.locator("#singleChallanhallanComment")
        self.approve_button = page.locator("#approveChallan")
        self.reject_button = page.locator("#rejectChallan")
        self.sendback_button = page.locator("#sendBackChallan")

    def read_popup_actions(self) -> list:
        """Return the names of the action buttons visible in the popup, among Approve, Reject and Sendback."""
        actions = []
        if self.approve_button.is_visible():
            actions.append("Approve")
        if self.reject_button.is_visible():
            actions.append("Reject")
        if self.sendback_button.is_visible():
            actions.append("Sendback")
        return actions

    def enter_comment(self, text: str) -> None:
        """Type a comment in the popup's Comment box."""
        self.type_text(self.comment_box, text, "Comment box")

    def approve_and_verify(self) -> None:
        """Click Approve in the popup and confirm both messages (challan approved, gate pass generated)."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button")
        self.verify_toast_text(self.get_toast_text(), SINGLE_CHALLAN_APPROVE_TOAST, "Approve of the challan")
