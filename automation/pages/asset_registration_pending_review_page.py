"""
AssetRegistrationPendingReviewPage: HOFA (Fixed Asset) > Registration > Asset
Registration Pending/Review List.

A bill submitted in HOFIN (an asset registration or an asset addition) is
listed here as PENDING. The HOFA acknowledger finds it by its Transaction No.
(the "Payable Number" filter), opens it with View and clicks Acknowledge. See
`automation/element_catalog/asset_registration_pending_review_list.md`.
"""
from pages.base_page import BasePage
from test_data import hofin_asset_data as data
from utils.logger import assertion_logger

LIST_LINK_NAME = "Asset Registration Pending/Review List"


class AssetRegistrationPendingReviewPage(BasePage):
    """Page object for the Asset Registration Pending/Review List screen."""

    def __init__(self, page):
        super().__init__(page)
        # Filter: the Transaction No. of the bill is typed here
        self.payable_number_field = page.get_by_placeholder("Enter Payable Number(Min 3 char...)")
        self.search_button = page.get_by_role("button", name="Search")
        # Button on the detail screen that acknowledges the request
        self.acknowledge_button = page.get_by_role("button", name="Acknowledge")

    def navigate_here(self) -> None:
        """Open the list from the Registration menu of the Fixed Asset module."""
        self.open_registration_submenu(LIST_LINK_NAME)
        self.wait_until_visible(self.payable_number_field, "Payable Number filter")

    def search_by_transaction_no(self, transaction_no: str) -> None:
        """Filter by Transaction No. and wait until its row is shown."""
        self.type_with_keys(self.payable_number_field, transaction_no, "Payable Number filter")
        self.click(self.search_button, "Search button")
        self.wait_until_visible(self.get_row(transaction_no), f"row of {transaction_no}")

    def get_row(self, transaction_no: str):
        """Return the grid row that contains this Transaction No."""
        return self.page.locator("table tbody tr", has_text=transaction_no).first

    def verify_status(self, transaction_no: str, expected_status: str) -> None:
        """
        Confirm the row of this Transaction No. shows the expected Status (PENDING,
        ACKNOWLEDGED or APPROVED). The row text is shown in the failure message.
        """
        assertion_logger.info(f"Verifying the status of {transaction_no}")
        row_text = self.get_row(transaction_no).inner_text().replace("\t", " | ").strip()
        assert expected_status in row_text.split(" | "), (
            f"The status of {transaction_no} should be {expected_status} but the row shows: {row_text}"
        )

    def acknowledge(self, transaction_no: str) -> None:
        """Open the row with View, click Acknowledge and check the success message."""
        view_link = self.get_row(transaction_no).get_by_text("View", exact=True)
        self.click(view_link, f"View link of {transaction_no}")
        self.wait_until_visible(self.acknowledge_button, "Acknowledge button")
        self.click(self.acknowledge_button, "Acknowledge button")
        toast = self.get_toast_text()
        self.verify_toast_contains(toast, data.ACKNOWLEDGED_TOAST, "Acknowledge")
