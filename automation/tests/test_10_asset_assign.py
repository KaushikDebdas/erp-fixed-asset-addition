"""
test_10_asset_assign.py: tests for the Asset Assign screen (Fixed Asset >
Asset Transaction > Asset Assign).

Built from automation/element_catalog/asset_assign.md. The tests use a
freshly approved, unassigned asset (the `unassigned_asset` fixture in
conftest.py). The whole file logs in once and every test reuses that session.

The last test takes the asset all the way: Draft on Asset Assign, then
Transaction List (Details, Edit, Submit), then Transaction Approval List
(Details, Approve), and finally checks the asset is ASSIGNED. It must stay
the last test of the file because it uses up the unassigned asset.
"""
import pytest

from test_data.asset_transaction_data import ASSIGN, ASSIGNEE_NAME, ASSIGNEE_PIN, USER_BRANCH
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, submit_draft_from_list

NOTE = "AUTOMATION_TEST assign note"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_assign_serial_search_fills_asset_details(
    page, assign_page, unassigned_asset, take_screenshot
):
    """Asset Assign: selecting an Asset Serial fills the asset details, and they belong to the serial entered."""
    serial = unassigned_asset["serial"]

    # Step 1: open Asset Assign
    assign_page.navigate_here()

    # Step 2: type the serial, search, and pick the suggestion
    assign_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")

    # Step 3: the box holds the serial that was entered
    assert assign_page.get_value("assetSerialId").startswith(serial)

    # Step 4: the details that filled in are those of this asset
    assert assign_page.get_value("assetName") == "Cabinet Table"
    assert assign_page.get_value("subCategoryName") == "Wooden Furniture"
    assert assign_page.get_value("categoryName") == "Furniture"
    assert assign_page.get_value("groupName") == "Furniture and Fixture"
    assert assign_page.get_value("projectName") == "Microfinance (Dabi)"
    assert assign_page.get_value("previousAssignStatus") == "UNASSIGNED"


@pytest.mark.regression
def test_assign_add_to_grid(page, assign_page, unassigned_asset, take_screenshot):
    """Asset Assign: Add to Grid puts the asset in the Asset List."""
    serial = unassigned_asset["serial"]

    # Step 1: select the asset
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)

    # Step 2: add it to the grid
    assign_page.add_to_grid()
    take_screenshot("asset added to grid")

    # Step 3: the Asset List holds it, unassigned
    assert serial in assign_page.get_asset_list_serials()
    assert "UNASSIGNED" in assign_page.get_asset_list_row_text(serial)

    # Step 4: the top section is cleared, ready for the next asset
    assert assign_page.get_value("assetName") == ""


@pytest.mark.regression
def test_assign_employee_search_fills_employee_and_branch(
    page, assign_page, unassigned_asset, take_screenshot
):
    """Asset Assign: searching an Employee PIN fills the employee, and Branch Name is the logged-in user's branch."""
    # Step 1: open Asset Assign and add the asset
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(unassigned_asset["serial"])
    assign_page.add_to_grid()

    # Step 2: search the employee PIN and pick the suggestion
    assign_page.select_employee(ASSIGNEE_PIN)
    take_screenshot("employee selected")

    # Step 3: the employee's PIN and name filled in
    assert assign_page.get_employee_pin() == ASSIGNEE_PIN
    assert assign_page.get_employee_name() == ASSIGNEE_NAME

    # Step 4: Branch Name shows the branch the user is logged in to
    logged_in_branch = assign_page.get_branch_name()
    assert logged_in_branch == USER_BRANCH, f"The user is logged in to '{logged_in_branch}'."


@pytest.mark.regression
def test_assign_requires_employee(page, assign_page, unassigned_asset, take_screenshot):
    """Asset Assign: Draft without an employee is stopped by the 'This field is required' message."""
    # Step 1: add the asset but leave the employee empty
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(unassigned_asset["serial"])
    assign_page.add_to_grid()

    # Step 2: click Draft
    assign_page.click_draft_without_waiting_for_toast()
    take_screenshot("draft stopped without employee")

    # Step 3: the required message is shown
    assert assign_page.is_required_message_visible()


@pytest.mark.smoke
@pytest.mark.regression
def test_assign_full_flow_draft_submit_approve(
    page, assign_page, transaction_list_page, transaction_approval_page,
    asset_serial_global_list_page, unassigned_asset, take_screenshot
):
    """Asset Assign: Draft, Submit from the Transaction List, Approve, and the asset becomes ASSIGNED."""
    serial = unassigned_asset["serial"]

    # Step 1: fill the form and save it as a Draft
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)
    assign_page.add_to_grid()
    assign_page.select_employee(ASSIGNEE_PIN)
    assign_page.enter_note(NOTE)
    transaction_date = assign_page.get_transaction_date().replace("-", "/")
    take_screenshot("assign form filled")
    toast = assign_page.draft_and_get_toast()
    take_screenshot("assign draft saved")
    assert toast == "Asset Assign Draft Successfully", f"Unexpected toast: '{toast}'"

    expected = {
        "employee_pin": ASSIGNEE_PIN,
        "employee_name": ASSIGNEE_NAME,
        "note": NOTE,
        "transaction_date": transaction_date,
    }

    # Step 2: Transaction List: check the Draft, open Edit, and Submit
    submit_draft_from_list(
        transaction_list_page, assign_page, ASSIGN, serial, expected,
        "Asset Assign Submit Successfully", take_screenshot,
    )

    # Step 3: Transaction Approval List: check the popup, Approve, confirm APPROVED
    approve_and_verify(transaction_approval_page, ASSIGN, serial, expected, take_screenshot)

    # Step 4: the asset is now ASSIGNED to the employee
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    assert asset_serial_global_list_page.get_assign_status(serial) == "ASSIGNED"
    asset_serial_global_list_page.open_asset_popup(serial)
    assert asset_serial_global_list_page.get_popup_value("employeePin") == ASSIGNEE_PIN
    assert asset_serial_global_list_page.get_popup_value("assignedEmployee") == ASSIGNEE_NAME
    take_screenshot("asset is assigned")
    asset_serial_global_list_page.close_popup()
