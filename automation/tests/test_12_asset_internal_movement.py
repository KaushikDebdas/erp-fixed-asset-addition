"""
test_12_asset_internal_movement.py: tests for the Asset Internal Movement
screen (Fixed Asset > Asset Transaction > Asset Internal Movement).

Built from automation/element_catalog/asset_internal_movement.md. The assets are NOT
created here: they are the two usage assets of the asset pool (test_data/asset_slots.py),
usage_a for the Draft + Submit path and usage_b for the Submit-only path. Internal
Movement only works on an assigned asset, so each test reads the asset's real Assign
Status from the Asset Serial Global List and assigns it first when needed
(`transactions.ensure_assigned()`, utils/transaction_helper.py). The whole file
logs in once and every test reuses that session.

The tests run top to bottom:
    1. The form: the assigned asset, Search By, employee-PIN search
    2. The Draft + Submit path (usage_a): Draft, Transaction List (Details, Edit, Submit),
       Transaction Approval List (Details, Approve), and the asset shows its new
       building and floor (this one test is a little longer than the others because it
       is the whole flow)
    3. The Submit-only path (usage_b): Submit straight from the form, Approve

Both assets stay ASSIGNED, which is the state test_13 starts from.

To run part of the file:
    pytest tests/test_12_asset_internal_movement.py -k "employee"
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
from test_data.toast_messages import (
    MOVEMENT_DRAFT_TOAST,
)
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, build_expected, submit_draft_from_list
from utils.transaction_helper import USAGE_B

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
    # Step 1: get the asset, assigned
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
def test_internal_movement_search_by_employee_pin_loads_assets(
    page, internal_movement_page, transactions, take_screenshot
):
    """Asset Internal Movement: Search By offers Serial (the default) and Employee Pin, and searching by Employee Pin loads that employee's assigned assets."""
    # Step 1: open the screen; both choices are there and Serial is selected
    internal_movement_page.navigate_here()
    internal_movement_page.verify_search_by_options()
    take_screenshot("search by options")

    # Step 2: get the asset, assigned to the test employee
    serial = transactions.ensure_assigned()

    # Step 3: switch Search By to Employee Pin and search the employee
    internal_movement_page.navigate_here()
    internal_movement_page.choose_search_by_employee_pin()
    internal_movement_page.load_assets_of_employee(ASSIGNEE_PIN)
    take_screenshot("assets of the employee loaded")

    # Step 4: the Asset List holds the employee's assets, including the asset
    internal_movement_page.verify_asset_in_list(serial)


# ---------------------------------------------------------------------------
# 2. The Draft + Submit path (usage_a): the asset stays ASSIGNED
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
    internal_movement_page.draft_and_verify_toast(MOVEMENT_DRAFT_TOAST)
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


# ---------------------------------------------------------------------------
# 3. The Submit-only path (usage_b): the asset stays ASSIGNED
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_internal_movement_submit_only_flow(page, transactions, asset_serial_global_list_page, take_screenshot):
    """Asset Internal Movement: a movement submitted straight from the form (no Draft) and approved moves the asset."""
    # Step 1: get the second usage asset, assigned
    serial = transactions.ensure_assigned(USAGE_B)

    # Step 2: Submit straight from the Asset Internal Movement form and Approve (the messages of both are checked)
    transactions.move(serial)

    # Step 3: the asset is still ASSIGNED and its profile shows the new building
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.verify_assign_status(serial, ASSIGNED)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.verify_popup_fields({"buildingName": MOVE_BUILDING})
    take_screenshot("asset shows its new building")
    asset_serial_global_list_page.close_popup()
