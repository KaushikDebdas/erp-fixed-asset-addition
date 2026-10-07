"""
test_13_transaction_list_new.py: tests for the Transaction List screen (Fixed
Asset > Asset Transaction > Transaction List).

Built from automation/element_catalog/transaction_list.md. The whole file logs
in once and every test reuses that session. These tests read the list only. The
full Draft > Edit > Submit path of each transaction type is tested in test_10,
test_11 and test_12.

The per-asset test checks the transactions of the saved Furniture asset (see
utils/transaction_helper.py): its own APPROVED ASSIGN, TRANSFER (Internal
Movement) and UNASSIGN transactions, made by test_10, test_11 and test_12. Run
on its own, only a transaction that is missing is made first, and the asset's
saved record is never changed.

The tests run top to bottom:
    1. The page: columns, filters, Created By
    2. Filter by type and by status, the Details popup, the Edit link
    3. The saved asset's own transactions

To run part of the file:
    pytest tests/test_13_transaction_list_new.py -k "asset"
"""
import pytest

from config.settings import TEST_USERNAME
from test_data.asset_transaction_data import ASSIGN, TRANSFER, UNASSIGN
from utils.run_context import trace_one_test

# Column headings of the grid, in order
GRID_COLUMNS = [
    "SL", "Details", "Edit", "Transaction Type", "Transaction Date", "Branch",
    "Created By", "Approved By", "Approval Date", "Transaction Status",
]

# Values of the Transaction Type filter and the Transaction Status filter
TYPE_OPTIONS = ["-Select Transaction Type-", ASSIGN, UNASSIGN, TRANSFER]
STATUS_OPTIONS = [
    "-Select Transaction Status-", "PENDING", "APPROVED", "REJECTED", "DRAFT", "SENDBACK", "ACKNOWLEDGED",
]

# Column headings of the asset list inside the Details popup
POPUP_ASSET_COLUMNS = [
    "SL", "Asset Serial", "Asset Item Name", "Sub Category", "Category", "Project Name",
    "Department Name", "Assign Status", "Assigned Before Approval", "Utilization Status",
]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The page: columns, filters, Created By
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_transaction_list_grid_columns(page, transaction_list_page, take_screenshot):
    """Transaction List: the grid shows the documented columns."""
    # Step 1: open the Transaction List
    transaction_list_page.navigate_here()
    take_screenshot("transaction list opened")

    # Step 2: the column headings
    transaction_list_page.verify_grid_headers(GRID_COLUMNS)


@pytest.mark.regression
def test_transaction_list_filter_values(page, transaction_list_page, take_screenshot):
    """Transaction List: the Type filter offers ASSIGN, UNASSIGN and TRANSFER, and the Status filter its six statuses."""
    # Step 1: open the Transaction List
    transaction_list_page.navigate_here()
    take_screenshot("filters shown")

    # Step 2: the Transaction Type and Transaction Status values
    transaction_list_page.verify_filter_options(TYPE_OPTIONS, STATUS_OPTIONS)


@pytest.mark.regression
def test_transaction_list_created_by_defaults_to_logged_in_user(page, transaction_list_page, take_screenshot):
    """Transaction List: Created By starts filled with the logged-in user."""
    # Step 1: open the Transaction List
    transaction_list_page.navigate_here()
    take_screenshot("created by prefilled")

    # Step 2: the Created By filter holds the user that logged in
    transaction_list_page.verify_created_by_filter_contains(TEST_USERNAME)


# ---------------------------------------------------------------------------
# 2. Filter by type and by status, the Details popup, the Edit link
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.parametrize("transaction_type", [ASSIGN, UNASSIGN, TRANSFER])
def test_transaction_list_filter_by_type(page, transaction_list_page, transaction_type, take_screenshot):
    """Transaction List: filtering by a type shows only transactions of that type."""
    # Step 1: open the list and filter by the type
    transaction_list_page.navigate_here()
    transaction_list_page.search(transaction_type=transaction_type)
    take_screenshot(f"filtered by {transaction_type}")
    if not transaction_list_page.has_data_rows():
        pytest.skip(f"The user has no {transaction_type} transaction on this environment yet.")

    # Step 2: every row is of that type
    transaction_list_page.verify_all_rows_are_type(transaction_type)


@pytest.mark.regression
def test_transaction_list_filter_by_status(page, transaction_list_page, take_screenshot):
    """Transaction List: filtering by APPROVED shows only approved transactions."""
    # Step 1: open the list and filter by APPROVED
    transaction_list_page.navigate_here()
    transaction_list_page.search(status="APPROVED")
    take_screenshot("filtered by approved")
    if not transaction_list_page.has_data_rows():
        pytest.skip("The user has no approved transaction on this environment yet.")

    # Step 2: every row is APPROVED
    transaction_list_page.verify_all_rows_are_status("APPROVED")


@pytest.mark.regression
def test_transaction_list_details_popup(page, transaction_list_page, take_screenshot):
    """Transaction List: Details opens a read-only popup for the same transaction type as the row."""
    # Step 1: open the list and search
    transaction_list_page.navigate_here()
    transaction_list_page.search(status="APPROVED")
    if not transaction_list_page.has_data_rows():
        pytest.skip("The user has no approved transaction on this environment yet.")
    row_type = transaction_list_page.get_row_values(0)["type"]

    # Step 2: open Details on the first row
    transaction_list_page.open_details_of_row(0)
    take_screenshot("transaction details popup")

    # Step 3: the popup is for the same type and lists its assets with the documented columns
    transaction_list_page.verify_popup_value("assetTransactionType", row_type)
    transaction_list_page.verify_popup_asset_headers(POPUP_ASSET_COLUMNS)

    # Step 4: close the popup
    transaction_list_page.close_popup()


@pytest.mark.regression
def test_transaction_list_only_drafts_have_edit(page, transaction_list_page, take_screenshot):
    """Transaction List: an approved transaction has no Edit link."""
    # Step 1: open the list and filter by APPROVED
    transaction_list_page.navigate_here()
    transaction_list_page.search(status="APPROVED")
    if not transaction_list_page.has_data_rows():
        pytest.skip("The user has no approved transaction on this environment yet.")
    take_screenshot("approved transactions")

    # Step 2: the first approved row has no Edit link
    transaction_list_page.verify_row_has_no_edit_link(0)


# ---------------------------------------------------------------------------
# 3. The saved asset's own transactions
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("transaction_type", [ASSIGN, TRANSFER, UNASSIGN])
def test_list_shows_the_assets_transaction(page, transaction_list_page, transactions, transaction_type, take_screenshot):
    """Transaction List: the saved Furniture asset has an APPROVED transaction of each type, with no Edit link."""
    # Step 1: get the asset; a transaction of this type is made only when none exists
    serial = transactions.ensure_transaction(transaction_type)

    # Step 2: open the list and find the asset's APPROVED transaction of this type
    transaction_list_page.navigate_here()
    row_index = transaction_list_page.open_transaction_of_asset(serial, transaction_type, "APPROVED")
    take_screenshot(f"{transaction_type} of {serial}")

    # Step 3: the popup lists the asset; the approved row cannot be edited
    transaction_list_page.close_popup()
    transaction_list_page.verify_row_has_no_edit_link(row_index)
