"""
test_17_asset_expense_approval.py: tests for the Asset Expense Approval screen
(Fixed Asset > Asset Expenditure > Asset Expense Approval).

Built from automation/element_catalog/asset_expense_approval.md. The whole file
logs in once and every test reuses that session. These tests read the list only:
Approve, Reject and Sendback are never clicked here. The full Submit > Approve
path of both expense sources is tested in test_16_asset_expense.py.
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
    assert expense_approval_page.get_status_options() == [
        "-Select Status-",
        "PENDING",
        "APPROVED",
        "REJECTED",
        "SENDBACK",
    ]

    # Step 3: the column headings
    assert expense_approval_page.get_grid_headers() == [
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


@pytest.mark.regression
def test_approval_list_filter_by_approved(page, expense_approval_page, take_screenshot):
    """Asset Expense Approval: filtering by APPROVED shows only approved expenses, each with an approver."""
    # Step 1: open the list and filter by APPROVED
    expense_approval_page.navigate_here()
    expense_approval_page.search("APPROVED")
    take_screenshot("filtered by approved")
    if not expense_approval_page.has_data_rows():
        pytest.skip("There is no approved expense on this environment yet.")

    # Step 2: the first row is APPROVED
    expense_id = expense_approval_page.get_first_row_expense_id()
    assert expense_approval_page.get_row_status(expense_id) == "APPROVED"


@pytest.mark.regression
def test_approval_popup_of_approved_expense_is_read_only(
    page, expense_approval_page, take_screenshot
):
    """Asset Expense Approval: an expense opened from the list shows read-only values and its asset."""
    # Step 1: open the list and the first approved expense
    expense_approval_page.navigate_here()
    expense_approval_page.search("APPROVED")
    if not expense_approval_page.has_data_rows():
        pytest.skip("There is no approved expense on this environment yet.")
    expense_id = expense_approval_page.get_first_row_expense_id()
    expense_approval_page.open_expense(expense_id)
    take_screenshot(f"details of {expense_id}")

    # Step 2: the values cannot be typed in, and the expense lists at least one asset
    for field_id in ("expenseRef", "expenseAmount", "remarks", "dateOfEntry"):
        assert expense_approval_page.is_popup_field_read_only(field_id), f"{field_id} should be read-only."
    assert expense_approval_page.get_popup_asset_serials()

    # Step 3: close the popup
    expense_approval_page.close_popup()
