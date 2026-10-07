"""
test_14_transaction_approval_list_new.py: tests for the Transaction Approval
List screen (Fixed Asset > Asset Transaction > Transaction Approval List).

Built from automation/element_catalog/transaction_approval_list.md. The whole
file logs in once and every test reuses that session. These tests read the list
only: Approve, Reject and Sendback are never clicked here. The full Details >
Approve path of each transaction type is tested in test_10, test_11 and test_12.

The per-asset test checks the transactions of the saved Furniture asset (see
utils/transaction_helper.py): its own APPROVED ASSIGN, TRANSFER (Internal
Movement) and UNASSIGN transactions, made by test_10, test_11 and test_12. Run
on its own, only a transaction that is missing is made first, and the asset's
saved record is never changed.

The tests run top to bottom:
    1. The page: columns and filters
    2. Filter by type and by status, the Details popup
    3. The saved asset's own transactions

To run part of the file:
    pytest tests/test_14_transaction_approval_list_new.py -k "asset"
"""
import pytest

from test_data.asset_transaction_data import ASSIGN, TRANSFER, UNASSIGN
from utils.run_context import trace_one_test

# Column headings of the grid, in order (no Edit column here)
GRID_COLUMNS = [
    "SL", "Details", "Transaction Type", "Transaction Date", "Branch",
    "Created By", "Approved By", "Approval Date", "Transaction Status",
]

# Values of the Transaction Type filter and the Transaction Status filter (a Draft is not up for approval)
TYPE_OPTIONS = ["-Select Transaction Type-", ASSIGN, UNASSIGN, TRANSFER]
STATUS_OPTIONS = [
    "-Select Transaction Status-", "PENDING", "APPROVED", "REJECTED", "SENDBACK", "ACKNOWLEDGED",
]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The page: columns and filters
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_approval_list_grid_columns(page, transaction_approval_page, take_screenshot):
    """Transaction Approval List: the grid shows the documented columns."""
    # Step 1: open the Transaction Approval List
    transaction_approval_page.navigate_here()
    take_screenshot("transaction approval list opened")

    # Step 2: the column headings (no Edit column here)
    transaction_approval_page.verify_grid_headers(GRID_COLUMNS)


@pytest.mark.regression
def test_approval_list_filter_values(page, transaction_approval_page, take_screenshot):
    """Transaction Approval List: the Type filter offers the three types and the Status filter has no DRAFT."""
    # Step 1: open the Transaction Approval List
    transaction_approval_page.navigate_here()
    take_screenshot("filters shown")

    # Step 2: the Transaction Type and Transaction Status values
    transaction_approval_page.verify_filter_options(TYPE_OPTIONS, STATUS_OPTIONS)


# ---------------------------------------------------------------------------
# 2. Filter by type and by status, the Details popup
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.parametrize("transaction_type", [ASSIGN, UNASSIGN, TRANSFER])
def test_approval_list_filter_by_type(page, transaction_approval_page, transaction_type, take_screenshot):
    """Transaction Approval List: filtering by a type shows only transactions of that type."""
    # Step 1: open the list and filter by the type
    transaction_approval_page.navigate_here()
    transaction_approval_page.search(transaction_type=transaction_type)
    take_screenshot(f"filtered by {transaction_type}")
    if not transaction_approval_page.has_data_rows():
        pytest.skip(f"There is no {transaction_type} transaction on this environment yet.")

    # Step 2: every row is of that type
    transaction_approval_page.verify_all_rows_are_type(transaction_type)


@pytest.mark.regression
def test_approval_list_filter_by_status(page, transaction_approval_page, take_screenshot):
    """Transaction Approval List: filtering by APPROVED shows only approved transactions."""
    # Step 1: open the list and filter by APPROVED
    transaction_approval_page.navigate_here()
    transaction_approval_page.search(status="APPROVED")
    take_screenshot("filtered by approved")
    if not transaction_approval_page.has_data_rows():
        pytest.skip("There is no approved transaction on this environment yet.")

    # Step 2: every row is APPROVED
    transaction_approval_page.verify_all_rows_are_status("APPROVED")


@pytest.mark.regression
def test_approval_list_details_popup(page, transaction_approval_page, take_screenshot):
    """Transaction Approval List: Details of an approved transaction opens a popup with no decision buttons."""
    # Step 1: open the list and search approved transactions
    transaction_approval_page.navigate_here()
    transaction_approval_page.search(status="APPROVED")
    if not transaction_approval_page.has_data_rows():
        pytest.skip("There is no approved transaction on this environment yet.")
    row_type = transaction_approval_page.get_row_values(0)["type"]

    # Step 2: open Details on the first row
    transaction_approval_page.open_details_of_row(0)
    take_screenshot("approval details popup")

    # Step 3: the popup is for the same type and shows its status
    transaction_approval_page.verify_popup_value("assetTransactionType", row_type)
    transaction_approval_page.verify_popup_value("oldTransactionStatus", "APPROVED")

    # Step 4: an approved transaction offers no decision, then the popup is closed
    transaction_approval_page.verify_no_decision_buttons()
    transaction_approval_page.close_popup()


# ---------------------------------------------------------------------------
# 3. The saved asset's own transactions
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("transaction_type", [ASSIGN, TRANSFER, UNASSIGN])
def test_approval_list_shows_the_assets_transaction(
    page, transaction_approval_page, transactions, transaction_type, take_screenshot
):
    """Transaction Approval List: the saved Furniture asset has an APPROVED transaction of each type, with no decision buttons."""
    # Step 1: get the asset; a transaction of this type is made only when none exists
    serial = transactions.ensure_transaction(transaction_type)

    # Step 2: open the list and find the asset's APPROVED transaction of this type
    transaction_approval_page.navigate_here()
    transaction_approval_page.open_transaction_of_asset(serial, transaction_type, "APPROVED")
    take_screenshot(f"{transaction_type} of {serial}")

    # Step 3: the popup offers no decision on an approved transaction
    transaction_approval_page.verify_no_decision_buttons()
    transaction_approval_page.close_popup()
