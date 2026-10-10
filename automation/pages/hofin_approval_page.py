"""
HofinApprovalPage: HOFIN > Approval > Approval (the "Approve Transaction" list).

The HOFIN approver finds the submitted bill by its Transaction No., opens it
with Action and clicks Approve. The Feature filter must be set to "Vendor Bill
Payable-Vendor", otherwise the search finds nothing. See
`automation/element_catalog/hofin_approval_list.md`.
"""
from pages.base_page import BasePage
from test_data import hofin_asset_data as data
from utils.logger import assertion_logger

# Number of times the list is opened again to wait for the APPROVED row
APPROVED_CHECK_ATTEMPTS = 6

# Time to wait for the row of the Transaction No. in each attempt (milliseconds)
ROW_TIMEOUT = 15000


class HofinApprovalPage(BasePage):
    """Page object for the HOFIN Approve Transaction list."""

    def __init__(self, page):
        super().__init__(page)
        # Menu: Approval, and its Approval link
        self.approval_menu = page.locator("a", has_text="Approval").first
        self.approval_link = page.locator('a[href="/brac/workflow-transaction/list"]')
        # Filters
        self.feature_input = page.locator("#feature input")
        self.status_input = page.locator("#status input")
        self.transaction_number_field = page.get_by_placeholder("Transaction Number")
        # The Search button is a link, not a button
        self.search_button = page.locator("a.btn-search")
        # Button of the transaction screen that approves the bill (found by its style:
        # its name has an icon in front of the text)
        self.approve_button = page.locator("button.btn-info").filter(has_text="Approve")

    def navigate_here(self) -> None:
        """Click Approval > Approval and wait for the filters."""
        self.click(self.approval_menu, "Approval menu")
        self.click(self.approval_link, "Approval link")
        self.wait_until_visible(self.feature_input, "Feature filter")

    def get_row(self, transaction_no: str):
        """Return the grid row that contains this Transaction No."""
        return self.page.locator("table tbody tr", has_text=transaction_no)

    def search_by_transaction_no(self, transaction_no: str, status: str = "") -> None:
        """
        Choose the Feature, optionally a Status (for example APPROVED), type the
        Transaction No., click Search and wait until its row is shown. Without a
        Status the list shows the bills still waiting for approval.
        """
        self.choose_from_ng_select(
            self.feature_input, data.APPROVAL_FEATURE_SEARCH_TEXT, data.APPROVAL_FEATURE_OPTION
        )
        if status != "":
            self.choose_from_ng_select(self.status_input, "", status)
        self.type_with_keys(self.transaction_number_field, transaction_no, "Transaction Number filter")
        self.click(self.search_button, "Search button")
        self.wait_until_visible(self.get_row(transaction_no), f"row of {transaction_no}")

    def approve(self, transaction_no: str) -> None:
        """Open the bill with Action and click Approve. The list is shown again once it is approved."""
        action_button = self.get_row(transaction_no).get_by_role("button", name="Action")
        self.click(action_button, f"Action button of {transaction_no}")
        self.wait_until_visible(self.approve_button, "Approve button")
        self.click(self.approve_button, "Approve button")
        self.page.wait_for_url("**/workflow-transaction/list**")
        self.wait_for_page_load()

    def verify_approved(self, transaction_no: str) -> None:
        """
        Confirm the bill now has the status APPROVED. The approved row appears
        a little after the click, so the list is opened again and searched with
        Status APPROVED until the row is shown.
        """
        assertion_logger.info(f"Verifying {transaction_no} is APPROVED")
        for attempt in range(APPROVED_CHECK_ATTEMPTS):
            self.page.reload(wait_until="domcontentloaded")
            self.wait_until_visible(self.feature_input, "Feature filter")
            self.choose_from_ng_select(
                self.feature_input, data.APPROVAL_FEATURE_SEARCH_TEXT, data.APPROVAL_FEATURE_OPTION
            )
            self.choose_from_ng_select(self.status_input, "", data.STATUS_APPROVED)
            self.type_with_keys(self.transaction_number_field, transaction_no, "Transaction Number filter")
            self.click(self.search_button, "Search button")
            if self.is_shown_within(self.get_row(transaction_no), f"APPROVED row of {transaction_no}", ROW_TIMEOUT):
                return
        raise AssertionError(
            f"{transaction_no} was approved but it is not listed with Status {data.STATUS_APPROVED} "
            f"after {APPROVED_CHECK_ATTEMPTS} checks."
        )
