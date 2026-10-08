"""
test_17_asset_expense_approval.py: tests for the Asset Expense Approval screen
(Fixed Asset > Asset Expenditure > Asset Expense Approval).

Built from automation/element_catalog/asset_expense_approval.md. The whole file
logs in once and every test reuses that session. This test reads the list only:
Approve, Reject and Sendback are never clicked here. The full Submit > Approve
path of both expense sources, including the APPROVED row and the read-only
popup of the approved expense, is tested in test_16_asset_expense.py.
"""
import pytest

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
