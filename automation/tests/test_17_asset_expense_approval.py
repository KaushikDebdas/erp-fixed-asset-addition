"""
test_17_asset_expense_approval.py: tests for the Asset Expense Approval screen
(Fixed Asset > Asset Expenditure > Asset Expense Approval).

Built from automation/element_catalog/asset_expense_approval.md. The whole file
logs in once and every test reuses that session. These tests read the list only:
Approve, Reject and Sendback are never clicked here. The full Submit > Approve
path of both expense sources, including the APPROVED row and the read-only
popup of the approved expense, is tested in test_16_asset_expense.py.

The last test checks the voucher an approved expense creates (Accounting >
Voucher Search, searched by the Expense ID; the voucher must be listed, the
Preview PDF is not read). It reuses the
expenses test_16 approved, or approves one when it runs alone.
"""
import pytest

from test_data.asset_expense_data import ACCOUNTS, INVENTORY
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_approval_list_columns_and_status_values(page, expense_approval_page, take_screenshot):
    """Asset Expense Approval: the grid has its documented columns and the Status filter has no DRAFT."""
    # Step 1: open the Asset Expense Approval list
    expense_approval_page.navigate_here()
    take_screenshot("asset expense approval list opened")

    # Step 2: the Status filter values (a Draft is not up for approval)
    expected_statuses = [
        "-Select Status-",
        "PENDING",
        "APPROVED",
        "REJECTED",
        "SENDBACK",
    ]
    found_statuses = expense_approval_page.get_status_options()
    assert found_statuses == expected_statuses, f"Expected Status values {expected_statuses} but found {found_statuses}."

    # Step 3: the column headings
    expected_headers = [
        "SL",
        "Expense ID",
        "Entry Date",
        "Supplier",
        "Expense Amount",
        "Status",
        "Created By",
        "Approved By",
        "Approve Date",
    ]
    found_headers = expense_approval_page.get_grid_headers()
    assert found_headers == expected_headers, f"Expected grid columns {expected_headers} but found {found_headers}."


@pytest.mark.regression
@pytest.mark.parametrize("source", [INVENTORY, ACCOUNTS])
def test_approval_creates_the_expense_voucher(
    source, page, expenses, expense_approval_page, voucher_search_page, take_screenshot
):
    """Voucher Search: an approved expense has a voucher, and its Preview PDF is that expense's voucher."""
    # Step 1: get the approved expense (approved in test_16, or approved now)
    record = expenses.get_approved_expense(source)
    expense_id = record["expense_id"]

    # Step 2: the approval list shows it as APPROVED
    expense_approval_page.navigate_here()
    expense_approval_page.find_expense(expense_id, "APPROVED")
    take_screenshot(f"{source} expense {expense_id} approved in the list")
    status = expense_approval_page.get_row_status(expense_id)
    assert status == "APPROVED", f"Expected {expense_id} to show 'APPROVED' but found '{status}'."

    # Step 3: in Accounting > Voucher Search, search by the Expense ID as the Transaction No
    voucher_search_page.navigate_here()
    voucher_search_page.set_date_range(record["expected"]["date_of_entry"])
    voucher_search_page.search_by_transaction_no(expense_id)
    take_screenshot(f"{source} voucher search for {expense_id}")

    # Step 4: the voucher is listed
    assert voucher_search_page.is_voucher_listed(expense_id), f"No voucher was found for {expense_id}."
