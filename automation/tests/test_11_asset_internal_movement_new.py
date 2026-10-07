"""
test_11_asset_internal_movement_new.py: tests for the Asset Internal Movement
screen (Fixed Asset > Asset Transaction > Asset Internal Movement).

Built from automation/element_catalog/asset_internal_movement.md. The asset is
NOT created here: it is the saved Furniture asset, read with
registrations.get_approved("furniture", "spot", AAQ_ASSET_GROUP)
(test_data/saved_assets.json). Its saved record is never changed. Internal
Movement only works on an assigned asset, so each test reads the asset's real
Assign Status from the Asset Serial Global List and assigns it first when needed
(`transactions.ensure_assigned()`, utils/transaction_helper.py). The whole file
logs in once and every test reuses that session.

The tests run top to bottom:
    1. The form: the assigned asset, Search By, employee-PIN search, required message
    2. LAST: Draft, Transaction List (Details, Edit, Submit), Transaction Approval
       List (Details, Approve), and the asset shows its new building and floor
       (this one test is a little longer than the others because it is the whole flow)

The asset stays ASSIGNED, which is the state test_12 starts from.

To run part of the file:
    pytest tests/test_11_asset_internal_movement_new.py -k "employee"
"""
import pytest

from test_data.asset_transaction_data import (
    ASSIGNED,
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    FURNITURE_FORM_DETAILS,
    MOVE_BUILDING,
    TRANSFER,
)
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, build_expected, submit_draft_from_list

NOTE = "AUTOMATION_TEST internal movement note"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The form
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_internal_movement_serial_search_shows_assigned_asset(
    page, internal_movement_page, transactions, take_screenshot
):
    """Asset Internal Movement: selecting the assigned asset shows its details and current assignee."""
    # Step 1: get the saved asset, assigned
    serial = transactions.ensure_assigned()

    # Step 2: open Asset Internal Movement, type the serial, search, and pick the suggestion
    internal_movement_page.navigate_here()
    internal_movement_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")

    # Step 3: the form shows the Furniture asset, ASSIGNED, with its current assignee
    expected = {
        "assetName": FURNITURE_FORM_DETAILS["assetName"],
        "previousAssignStatus": ASSIGNED,
        "assignedEmployeePinNo": ASSIGNEE_PIN,
        "assignedEmployeeName": ASSIGNEE_NAME,
    }
    internal_movement_page.verify_form_shows(serial, expected)


@pytest.mark.regression
def test_internal_movement_search_by_options(page, internal_movement_page, take_screenshot):
    """Asset Internal Movement: Search By offers Serial (the default) and Employee Pin."""
    # Step 1: open the screen
    internal_movement_page.navigate_here()
    take_screenshot("search by options")

    # Step 2: both choices are there and Serial is selected
    internal_movement_page.verify_search_by_options()


@pytest.mark.regression
def test_internal_movement_search_by_employee_pin_loads_assets(
    page, internal_movement_page, transactions, take_screenshot
):
    """Asset Internal Movement: searching by Employee Pin loads that employee's assigned assets."""
    # Step 1: get the saved asset, assigned to the test employee
    serial = transactions.ensure_assigned()

    # Step 2: switch Search By to Employee Pin and search the employee
    internal_movement_page.navigate_here()
    internal_movement_page.choose_search_by_employee_pin()
    internal_movement_page.load_assets_of_employee(ASSIGNEE_PIN)
    take_screenshot("assets of the employee loaded")

    # Step 3: the Asset List holds the employee's assets, including the saved asset
    internal_movement_page.verify_asset_in_list(serial)


@pytest.mark.regression
def test_internal_movement_requires_employee(page, internal_movement_page, transactions, take_screenshot):
    """Asset Internal Movement: Draft without an employee is stopped by the 'This field is required' message."""
    # Step 1: add the assigned asset but leave the employee empty
    serial = transactions.ensure_assigned()
    internal_movement_page.navigate_here()
    internal_movement_page.select_asset_by_serial(serial)
    internal_movement_page.add_to_grid()

    # Step 2: click Draft; the required message is shown
    internal_movement_page.click_draft_without_waiting_for_toast()
    take_screenshot("draft stopped without employee")
    internal_movement_page.verify_required_message_shown()


# ---------------------------------------------------------------------------
# 2. LAST: the full flow (the asset stays ASSIGNED)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_internal_movement_full_flow_draft_submit_approve(
    page, internal_movement_page, transaction_list_page, transaction_approval_page,
    asset_serial_global_list_page, transactions, take_screenshot
):
    """Asset Internal Movement: Draft, Submit from the Transaction List, Approve, and the asset shows its new location."""
    # Step 1: get the assigned asset, fill the form and save it as a Draft
    serial = transactions.ensure_assigned()
    internal_movement_page.navigate_here()
    transaction_date = internal_movement_page.fill_form(serial, ASSIGNEE_PIN, NOTE, MOVE_BUILDING)
    floor = internal_movement_page.get_floor()
    take_screenshot("internal movement form filled")
    internal_movement_page.draft_and_verify_toast("Asset Internal-Movement Draft Successfully")
    take_screenshot("internal movement draft saved")
    expected = build_expected(ASSIGNEE_PIN, ASSIGNEE_NAME, NOTE, transaction_date, MOVE_BUILDING, floor)

    # Step 2: Transaction List: check the Draft, open Edit, and Submit
    submit_draft_from_list(
        transaction_list_page, internal_movement_page, TRANSFER, serial, expected,
        "Asset Internal-Movement Submit Successfully", take_screenshot,
    )

    # Step 3: Transaction Approval List: check the popup, Approve, confirm APPROVED
    approve_and_verify(transaction_approval_page, TRANSFER, serial, expected, take_screenshot)

    # Step 4: the asset is still ASSIGNED and its profile shows the new building and floor
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.verify_assign_status(serial, ASSIGNED)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.verify_popup_fields({"buildingName": MOVE_BUILDING, "floorNo": floor})
    take_screenshot("asset shows its new location")
    asset_serial_global_list_page.close_popup()
