"""
test_10_asset_assign.py: tests for the Asset Assign screen (Fixed Asset >
Asset Transaction > Asset Assign).

Built from automation/element_catalog/asset_assign.md. The asset is NOT created
here: it is the saved Furniture asset, read with
registrations.get_approved("furniture", "spot", AAQ_ASSET_GROUP)
(test_data/saved_assets.json). Its saved record is never changed. Each test reads
the asset's real Assign Status from the Asset Serial Global List and unassigns it
first when needed (`transactions.ensure_unassigned()`, utils/transaction_helper.py).
The whole file logs in once and every test reuses that session.

The tests run top to bottom:
    1. The form: asset details, read-only fields, Add to Grid, employee, required message
    2. LAST: Draft, Transaction List (Details, Edit, Submit), Transaction Approval
       List (Details, Approve), and the asset is ASSIGNED (this one test is a
       little longer than the others because it is the whole flow)

The last test must stay last in the file: it leaves the asset ASSIGNED, which is
the state test_11 and test_12 start from. Run on its own, each test prepares the
asset it needs.

To run part of the file:
    pytest tests/test_10_asset_assign.py -k "employee"
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
    """Asset Assign: selecting the Asset Serial fills the asset details, and they match the Global List record."""
    # Step 1: get the saved asset, unassigned, and read its Global List record
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


@pytest.mark.regression
def test_assign_details_are_read_only(page, assign_page, transactions, take_screenshot):
    """Asset Assign: the auto-filled asset details cannot be typed in."""
    # Step 1: select the unassigned asset
    serial = transactions.ensure_unassigned()
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)
    take_screenshot("asset details filled")

    # Step 2: none of the auto-filled fields can be edited
    assign_page.verify_fields_read_only(FORM_READ_ONLY_FIELDS)


@pytest.mark.regression
def test_assign_add_to_grid(page, assign_page, transactions, take_screenshot):
    """Asset Assign: Add to Grid puts the asset in the Asset List and clears the top section."""
    # Step 1: select the unassigned asset
    serial = transactions.ensure_unassigned()
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)

    # Step 2: add it to the grid
    assign_page.add_to_grid()
    take_screenshot("asset added to grid")

    # Step 3: the Asset List holds it, unassigned, and the top section is cleared
    assign_page.verify_asset_in_list(serial, UNASSIGNED)
    assign_page.verify_asset_details_cleared()


@pytest.mark.regression
def test_assign_employee_search_fills_employee_and_branch(page, assign_page, transactions, take_screenshot):
    """Asset Assign: searching an Employee PIN fills the employee, and Branch Name is the logged-in user's branch."""
    # Step 1: open Asset Assign and add the unassigned asset
    serial = transactions.ensure_unassigned()
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)
    assign_page.add_to_grid()

    # Step 2: search the employee PIN and pick the suggestion
    assign_page.select_employee(ASSIGNEE_PIN)
    take_screenshot("employee selected")

    # Step 3: the employee's PIN and name filled in, and Branch Name is the user's branch
    assign_page.verify_employee_selected(ASSIGNEE_PIN, ASSIGNEE_NAME)
    assign_page.verify_branch(USER_BRANCH)


@pytest.mark.regression
def test_assign_requires_employee(page, assign_page, transactions, take_screenshot):
    """Asset Assign: Draft without an employee is stopped by the 'This field is required' message."""
    # Step 1: add the unassigned asset but leave the employee empty
    serial = transactions.ensure_unassigned()
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)
    assign_page.add_to_grid()

    # Step 2: click Draft; the required message is shown
    assign_page.click_draft_without_waiting_for_toast()
    take_screenshot("draft stopped without employee")
    assign_page.verify_required_message_shown()


# ---------------------------------------------------------------------------
# 2. LAST: the full flow (leaves the asset ASSIGNED)
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
