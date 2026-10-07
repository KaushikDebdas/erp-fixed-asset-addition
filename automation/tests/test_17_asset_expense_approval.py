"""
test_17_asset_expense_approval.py: tests for the Asset Expense Approval screen
(Fixed Asset > Asset Expenditure > Asset Expense Approval).

Built from automation/element_catalog/asset_expense_approval.md. The whole file
logs in once and every test reuses that session. These tests read the list only:
Approve, Reject and Sendback are never clicked here. The full Submit > Approve
path of both expense sources is tested in test_16_asset_expense.py.

The expense they check is the APPROVED Inventory expense saved in
test_data/saved_assets.json (the `expenses` fixture, utils/expense_helper.py).
When none is saved, one is made first (create, Submit, Approve).
"""
import pytest

from test_data.asset_expense_data import INVENTORY
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
def test_approval_list_filter_by_approved(page, expense_approval_page, expenses, take_screenshot):
    """Asset Expense Approval: filtering by APPROVED lists the saved expense as APPROVED."""
    # Step 1: take the saved approved expense
    expense_id = expenses.get_approved_expense(INVENTORY)["expense_id"]

    # Step 2: open the list and filter by APPROVED
    expense_approval_page.navigate_here()
    expense_approval_page.find_expense(expense_id, "APPROVED")
    take_screenshot("filtered by approved")

    # Step 3: the saved expense is listed as APPROVED
    found_status = expense_approval_page.get_row_status(expense_id)
    assert found_status == "APPROVED", f"Expected {expense_id} to be listed as 'APPROVED' but found '{found_status}'."


@pytest.mark.regression
def test_approval_popup_of_approved_expense_is_read_only(
    page, expense_approval_page, expenses, take_screenshot
):
    """Asset Expense Approval: the saved expense opened from the list shows read-only values and its own asset."""
    # Step 1: take the saved approved expense and open it from the list
    record = expenses.get_approved_expense(INVENTORY)
    expense_approval_page.navigate_here()
    expense_approval_page.find_expense(record["expense_id"], "APPROVED")
    expense_approval_page.open_expense(record["expense_id"])
    take_screenshot(f"details of {record['expense_id']}")

    # Step 2: the values cannot be typed in, and the expense lists the saved asset
    for field_id in ("expenseRef", "expenseAmount", "remarks", "dateOfEntry"):
        assert expense_approval_page.is_popup_field_read_only(field_id), f"{field_id} should be read-only."
    popup_serials = expense_approval_page.get_popup_asset_serials()
    assert record["serial"] in popup_serials, (
        f"Expected Asset Serial '{record['serial']}' in the expense popup but found {popup_serials}."
    )

    # Step 3: the popup shows what was entered
    found_ref = expense_approval_page.get_popup_value("expenseRef")
    assert found_ref == record["expected"]["expense_ref"], (
        f"Expected Expense Ref. '{record['expected']['expense_ref']}' but found '{found_ref}'."
    )

    # Step 4: close the popup
    expense_approval_page.close_popup()
