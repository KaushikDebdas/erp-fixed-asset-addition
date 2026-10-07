"""
TransactionApprovalListPage: Fixed Asset > Asset Transaction > Transaction
Approval List.

One shared approval screen for Assign, Un Assign and Internal Movement. Open
a row's Details popup, check it, then Approve (or Reject / Sendback, which
are only checked for presence here). See
`automation/element_catalog/transaction_approval_list.md`.
"""
from pages.transaction_grid_page import TransactionGridPage
from utils.logger import action_logger, assertion_logger


class TransactionApprovalListPage(TransactionGridPage):
    """Page object for the Transaction Approval List screen."""

    def __init__(self, page):
        super().__init__(page)
        # Decision controls inside the Details popup
        self.comment_field = self.popup.locator("#comment")
        self.approve_button = self.popup.locator("#btnApproved")
        self.reject_button = self.popup.locator("#btnReject")
        self.sendback_button = self.popup.locator("#btnSendBack")

    def navigate_here(self) -> None:
        """Open the Transaction Approval List via the Asset Transaction menu."""
        self.open_asset_transaction_submenu("Transaction Approval List")
        self.wait_until_visible(self.search_button, "Search button")

    def enter_comment(self, comment: str) -> None:
        """Type the optional comment for the decision."""
        self.type_text(self.comment_field, comment, "Comment field")

    def are_decision_buttons_visible(self) -> bool:
        """Return True if Approve, Reject and Sendback are all shown in the popup."""
        return (
            self.approve_button.is_visible()
            and self.reject_button.is_visible()
            and self.sendback_button.is_visible()
        )

    def verify_no_decision_buttons(self) -> None:
        """Confirm the open popup offers no decision: no Comment box and no Approve button."""
        assertion_logger.info("Verifying the popup offers no decision")
        assert not self.comment_field.is_visible(), "Expected no Comment box on a decided transaction but it is shown."
        assert not self.approve_button.is_visible(), "Expected no Approve button on a decided transaction but it is shown."

    def approve_and_get_toast(self) -> str:
        """Click Approve in the open popup, return the message shown and wait for the popup to close."""
        self.wait_for_toast_to_clear()
        self.click(self.approve_button, "Approve button")
        toast_text = self.get_toast_text()
        self.popup.wait_for(state="hidden")
        return toast_text

    def approve_transaction_for_serial(self, transaction_type: str, serial: str) -> str:
        """
        Find the PENDING transaction of this type that lists `serial`, approve
        it, and return the message shown. Used to prepare test data.
        """
        self.open_details_of_row_with_serial(serial, transaction_type, "PENDING")
        action_logger.info(f"Approving {transaction_type} transaction for asset {serial}")
        return self.approve_and_get_toast()
