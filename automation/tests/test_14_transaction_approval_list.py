"""
test_14_transaction_approval_list.py: tests for the Transaction Approval List
screen (Fixed Asset > Asset Transaction > Transaction Approval List).

Built from automation/element_catalog/transaction_approval_list.md. The whole
file logs in once and every test reuses that session. These tests read the
list only: Approve, Reject and Sendback are never clicked here. The full
Details > Approve path of each transaction type is tested in test_10,
test_11 and test_12.
"""
import pytest

from test_data.asset_transaction_data import ASSIGN, TRANSFER, UNASSIGN
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_approval_list_grid_columns(page, transaction_approval_page, take_screenshot):
    """Transaction Approval List: the grid shows the documented columns."""
    # Step 1: open the Transaction Approval List
    transaction_approval_page.navigate_here()
    take_screenshot("transaction approval list opened")

    # Step 2: the column headings (no Edit column here)
    assert transaction_approval_page.get_grid_headers() == [
        "SL",
        "Details",
        "Transaction Type",
        "Transaction Date",
        "Branch",
        "Created By",
        "Approved By",
        "Approval Date",
        "Transaction Status",
    ]


@pytest.mark.regression
def test_approval_list_filter_values(page, transaction_approval_page, take_screenshot):
    """Transaction Approval List: the Type filter offers the three types and the Status filter has no DRAFT."""
    # Step 1: open the Transaction Approval List
    transaction_approval_page.navigate_here()

    # Step 2: the Transaction Type values
    assert transaction_approval_page.get_type_options() == [
        "-Select Transaction Type-",
        ASSIGN,
        UNASSIGN,
        TRANSFER,
    ]

    # Step 3: the Transaction Status values (a Draft is not up for approval)
    assert transaction_approval_page.get_status_options() == [
        "-Select Transaction Status-",
        "PENDING",
        "APPROVED",
        "REJECTED",
        "SENDBACK",
        "ACKNOWLEDGED",
    ]


@pytest.mark.regression
@pytest.mark.parametrize("transaction_type", [ASSIGN, UNASSIGN, TRANSFER])
def test_approval_list_filter_by_type(
    page, transaction_approval_page, transaction_type, take_screenshot
):
    """Transaction Approval List: filtering by a type shows only transactions of that type."""
    # Step 1: open the list and filter by the type
    transaction_approval_page.navigate_here()
    transaction_approval_page.search(transaction_type=transaction_type)
    take_screenshot(f"filtered by {transaction_type}")
    if not transaction_approval_page.has_data_rows():
        pytest.skip(f"There is no {transaction_type} transaction on this environment yet.")

    # Step 2: every row is of that type
    assert set(transaction_approval_page.get_all_row_types()) == {transaction_type}


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
    assert set(transaction_approval_page.get_all_row_statuses()) == {"APPROVED"}


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
    assert transaction_approval_page.get_popup_value("assetTransactionType") == row_type
    assert transaction_approval_page.get_popup_value("oldTransactionStatus") == "APPROVED"

    # Step 4: an approved transaction offers no decision: no Comment box and no Approve button
    assert not transaction_approval_page.comment_field.is_visible()
    assert not transaction_approval_page.approve_button.is_visible()

    # Step 5: close the popup
    transaction_approval_page.close_popup()
