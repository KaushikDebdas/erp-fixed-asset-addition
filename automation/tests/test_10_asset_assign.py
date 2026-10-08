"""
test_10_asset_assign.py: tests for the Asset Assign screen (Fixed Asset >
Asset Transaction > Asset Assign).

Built from automation/element_catalog/asset_assign.md. The assets are NOT created
here: they are the two usage assets of the asset pool (test_data/asset_slots.py):
usage_a for the Draft + Submit path and usage_b for the Submit-only path. Each test
reads the asset's real Assign Status from the Asset Serial Global List and unassigns
it first when needed (`transactions.ensure_unassigned()`, utils/transaction_helper.py).
The whole file logs in once and every test reuses that session.

The tests run top to bottom:
    1. The form: asset details and read-only fields; Add to Grid, required message, employee
    2. The Draft + Submit path (usage_a): Draft, Transaction List (Details, Edit, Submit),
       Transaction Approval List (Details, Approve), and the asset is ASSIGNED (this one
       test is a little longer than the others because it is the whole flow)
    3. The Submit-only path (usage_b): Submit straight from the form, Approve, ASSIGNED

Both assets are left ASSIGNED, which is the state the acknowledgement (test_11),
movement (test_12) and unassign (test_13) files start from. Run on its own, each test
prepares the asset it needs.

To run part of the file:
    pytest tests/test_10_asset_assign.py -k "submit_only"
"""
import pytest

from test_data.asset_transaction_data import (
    ASSIGN,
    ASSIGNED,
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    FORM_READ_ONLY_FIELDS,
    FURNITURE_FORM_DETAILS,
    UNASSIGNED,
    USER_BRANCH,
    build_form_expectation,
)
from test_data.toast_messages import (
    ASSIGN_DRAFT_TOAST,
)
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, build_expected, submit_draft_from_list
from utils.transaction_helper import USAGE_B

NOTE = "AUTOMATION_TEST assign note"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The form
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_assign_serial_search_fills_asset_details(page, assign_page, transactions, take_screenshot):
    """Asset Assign: selecting the Asset Serial fills the asset details, they match the Global List record and cannot be edited."""
    # Step 1: get the asset, unassigned, and read its Global List record
    serial = transactions.ensure_unassigned()
    profile = transactions.read_profile_row(serial)

    # Step 2: open Asset Assign, type the serial, search, and pick the suggestion
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")

    # Step 3: the form shows what the Global List shows for this asset
    assign_page.verify_form_shows(serial, build_form_expectation(profile))

    # Step 4: the form shows the Furniture asset's own details and the project
    assign_page.verify_form_shows(serial, {**FURNITURE_FORM_DETAILS, "previousAssignStatus": UNASSIGNED})

    # Step 5: none of the auto-filled fields can be edited
    assign_page.verify_fields_read_only(FORM_READ_ONLY_FIELDS)


@pytest.mark.regression
def test_assign_add_to_grid_required_message_and_employee(page, assign_page, transactions, take_screenshot):
    """Asset Assign: Add to Grid fills the Asset List, Draft needs an employee, and the Employee PIN search fills the employee and branch."""
    # Step 1: select the unassigned asset and add it to the grid
    serial = transactions.ensure_unassigned()
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)
    assign_page.add_to_grid()
    take_screenshot("asset added to grid")

    # Step 2: the Asset List holds it, unassigned, and the top section is cleared
    assign_page.verify_asset_in_list(serial, UNASSIGNED)
    assign_page.verify_asset_details_cleared()

    # Step 3: Draft without an employee is stopped by the 'This field is required' message
    assign_page.click_draft_without_waiting_for_toast()
    take_screenshot("draft stopped without employee")
    assign_page.verify_required_message_shown()

    # Step 4: search the employee PIN; the employee's PIN and name fill in, and Branch Name is the user's branch
    assign_page.select_employee(ASSIGNEE_PIN)
    take_screenshot("employee selected")
    assign_page.verify_employee_selected(ASSIGNEE_PIN, ASSIGNEE_NAME)
    assign_page.verify_branch(USER_BRANCH)


# ---------------------------------------------------------------------------
# 2. The Draft + Submit path (usage_a): leaves the asset ASSIGNED
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_assign_full_flow_draft_submit_approve(
    page, assign_page, transaction_list_page, transaction_approval_page,
    asset_serial_global_list_page, transactions, take_screenshot
):
    """Asset Assign: Draft, Submit from the Transaction List, Approve, and the asset becomes ASSIGNED."""
    # Step 1: get the unassigned asset, fill the form and save it as a Draft
    serial = transactions.ensure_unassigned()
    assign_page.navigate_here()
    transaction_date = assign_page.fill_form(serial, ASSIGNEE_PIN, NOTE)
    take_screenshot("assign form filled")
    assign_page.draft_and_verify_toast(ASSIGN_DRAFT_TOAST)
    take_screenshot("assign draft saved")
    expected = build_expected(ASSIGNEE_PIN, ASSIGNEE_NAME, NOTE, transaction_date)

    # Step 2: Transaction List: check the Draft, open Edit, and Submit
    submit_draft_from_list(
        transaction_list_page, assign_page, ASSIGN, serial, expected,
        "Asset Assign Submit Successfully", take_screenshot,
    )

    # Step 3: Transaction Approval List: check the popup, Approve, confirm APPROVED
    approve_and_verify(transaction_approval_page, ASSIGN, serial, expected, take_screenshot)

    # Step 4: the Global List shows the asset ASSIGNED to the employee
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.verify_assign_status(serial, ASSIGNED)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.verify_popup_fields(
        {"employeePin": ASSIGNEE_PIN, "assignedEmployee": ASSIGNEE_NAME}
    )
    take_screenshot("asset is assigned")
    asset_serial_global_list_page.close_popup()


# ---------------------------------------------------------------------------
# 3. The Submit-only path (usage_b): leaves the asset ASSIGNED
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_assign_submit_only_flow(page, transactions, asset_serial_global_list_page, take_screenshot):
    """Asset Assign: an asset submitted straight from the form (no Draft) and approved becomes ASSIGNED."""
    # Step 1: get the second usage asset, unassigned
    serial = transactions.ensure_unassigned(USAGE_B)

    # Step 2: Submit straight from the Asset Assign form and Approve (the messages of both are checked)
    transactions.assign(serial)

    # Step 3: the Global List shows the asset ASSIGNED to the employee
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.verify_assign_status(serial, ASSIGNED)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.verify_popup_fields(
        {"employeePin": ASSIGNEE_PIN, "assignedEmployee": ASSIGNEE_NAME}
    )
    take_screenshot("asset is assigned")
    asset_serial_global_list_page.close_popup()
