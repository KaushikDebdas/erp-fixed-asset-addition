"""
test_11_asset_internal_movement.py: tests for the Asset Internal Movement
screen (Fixed Asset > Asset Transaction > Asset Internal Movement).

Built from automation/element_catalog/asset_internal_movement.md. The tests
use a freshly approved asset that is already assigned (the `assigned_asset`
fixture in conftest.py), because Internal Movement only works on an assigned
asset. The whole file logs in once and every test reuses that session.

The last test takes the asset all the way: Draft, Transaction List (Details,
Edit, Submit), Transaction Approval List (Details, Approve), and finally
checks the asset's new building and floor.
"""
import pytest

from test_data.asset_transaction_data import (
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    MOVE_BUILDING,
    TRANSFER,
)
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, submit_draft_from_list

NOTE = "AUTOMATION_TEST internal movement note"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_internal_movement_serial_search_shows_assigned_asset(
    page, internal_movement_page, assigned_asset, take_screenshot
):
    """Asset Internal Movement: selecting an assigned asset shows its details and current assignee."""
    serial = assigned_asset["serial"]

    # Step 1: open Asset Internal Movement
    internal_movement_page.navigate_here()

    # Step 2: type the serial, search, and pick the suggestion
    internal_movement_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")

    # Step 3: the box holds the serial that was entered
    assert internal_movement_page.get_value("assetSerialId").startswith(serial)

    # Step 4: the asset is assigned, and the current assignee is shown
    assert internal_movement_page.get_value("assetName") == "Cabinet Table"
    assert internal_movement_page.get_value("previousAssignStatus") == "ASSIGNED"
    assert internal_movement_page.get_value("assignedEmployeePinNo") == ASSIGNEE_PIN
    assert internal_movement_page.get_value("assignedEmployeeName") == ASSIGNEE_NAME


@pytest.mark.regression
def test_internal_movement_search_by_options(
    page, internal_movement_page, take_screenshot
):
    """Asset Internal Movement: Search By offers Serial (the default) and Employee Pin."""
    # Step 1: open the screen
    internal_movement_page.navigate_here()
    take_screenshot("search by options")

    # Step 2: both choices are there and Serial is selected
    assert internal_movement_page.search_by_serial_radio.is_visible()
    assert internal_movement_page.search_by_employee_pin_radio.is_visible()
    assert internal_movement_page.search_by_serial_radio.is_checked()
    assert not internal_movement_page.search_by_employee_pin_radio.is_checked()


@pytest.mark.regression
def test_internal_movement_search_by_employee_pin_loads_assets(
    page, internal_movement_page, assigned_asset, take_screenshot
):
    """Asset Internal Movement: searching by Employee Pin loads that employee's assigned assets."""
    # Step 1: switch Search By to Employee Pin
    internal_movement_page.navigate_here()
    internal_movement_page.choose_search_by_employee_pin()

    # Step 2: search the employee the asset is assigned to
    internal_movement_page.load_assets_of_employee(ASSIGNEE_PIN)
    take_screenshot("assets of the employee loaded")

    # Step 3: the Asset List holds the employee's assets, including the test asset
    assert assigned_asset["serial"] in internal_movement_page.get_asset_list_serials()


@pytest.mark.regression
def test_internal_movement_requires_employee(
    page, internal_movement_page, assigned_asset, take_screenshot
):
    """Asset Internal Movement: Draft without an employee is stopped by the 'This field is required' message."""
    # Step 1: add the asset but leave the employee empty
    internal_movement_page.navigate_here()
    internal_movement_page.select_asset_by_serial(assigned_asset["serial"])
    internal_movement_page.add_to_grid()

    # Step 2: click Draft
    internal_movement_page.click_draft_without_waiting_for_toast()
    take_screenshot("draft stopped without employee")

    # Step 3: the required message is shown
    assert internal_movement_page.is_required_message_visible()


@pytest.mark.smoke
@pytest.mark.regression
def test_internal_movement_full_flow_draft_submit_approve(
    page, internal_movement_page, transaction_list_page, transaction_approval_page,
    asset_serial_global_list_page, assigned_asset, take_screenshot
):
    """Asset Internal Movement: Draft, Submit from the Transaction List, Approve, and the asset shows its new location."""
    serial = assigned_asset["serial"]

    # Step 1: fill the form and save it as a Draft
    internal_movement_page.navigate_here()
    internal_movement_page.select_asset_by_serial(serial)
    internal_movement_page.add_to_grid()
    internal_movement_page.select_employee(ASSIGNEE_PIN)
    floor = internal_movement_page.select_building_and_first_floor(MOVE_BUILDING)
    internal_movement_page.enter_note(NOTE)
    transaction_date = internal_movement_page.get_transaction_date().replace("-", "/")
    take_screenshot("internal movement form filled")
    toast = internal_movement_page.draft_and_get_toast()
    take_screenshot("internal movement draft saved")
    assert toast == "Asset Internal-Movement Draft Successfully", f"Unexpected toast: '{toast}'"

    expected = {
        "employee_pin": ASSIGNEE_PIN,
        "employee_name": ASSIGNEE_NAME,
        "note": NOTE,
        "transaction_date": transaction_date,
        "building": MOVE_BUILDING,
        "floor": floor,
    }

    # Step 2: Transaction List: check the Draft, open Edit, and Submit
    submit_draft_from_list(
        transaction_list_page, internal_movement_page, TRANSFER, serial, expected,
        "Asset Internal-Movement Submit Successfully", take_screenshot,
    )

    # Step 3: Transaction Approval List: check the popup, Approve, confirm APPROVED
    approve_and_verify(transaction_approval_page, TRANSFER, serial, expected, take_screenshot)

    # Step 4: the asset's profile shows the new building and floor
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    assert asset_serial_global_list_page.get_popup_value("buildingName") == MOVE_BUILDING
    assert asset_serial_global_list_page.get_popup_value("floorNo") == floor
    take_screenshot("asset shows its new location")
    asset_serial_global_list_page.close_popup()
