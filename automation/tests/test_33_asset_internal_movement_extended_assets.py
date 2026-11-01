"""
test_34_asset_internal_movement_extended_assets.py: the Asset Internal Movement
screen and the Transaction Approval List for a parent asset that has an
extended asset (CR FAHOV2-643, feature F04 Asset Internal Movement, with F06
Transaction Approval List).

The parent asset and its extended asset are made once per run through HOFIN,
HOFA and HOFIN (`parent_with_extended`), then ASSIGNED to the test employee and
acknowledged (`assigned_parent_with_extended`), because an asset with an
acknowledgement pending is not offered in Asset Internal Movement. Both
fixtures do only the steps that are missing, so this file runs alone or after
test_33. Built from automation/element_catalog/asset_internal_movement.md and
the live check of 2026-10-10.

The screens are used by the Asset Assign user (ASSIGN_USER_USERNAME and
ASSIGN_USER_PASSWORD in .env), who is also the employee the asset is assigned to.

The tests run top to bottom. The last three follow one movement of the parent
asset, so run them together:
    1. The search by serial: an extended serial is not found; the parent is the only suggestion
    2. The Asset List: by serial and by Employee Pin the extended asset is listed below
       the parent; removing the parent removes it too
    3. One movement: Submit, the Details popup of the Transaction Approval List,
       Approve (both assets show the new location)

To run part of the file:
    pytest tests/test_34_asset_internal_movement_extended_assets.py -k "not_found or suggests"
"""
import pytest

from test_data.asset_transaction_data import ASSIGNEE_PIN, MOVE_BUILDING
from test_data.toast_messages import MOVEMENT_SUBMIT_TOAST, TRANSACTION_APPROVE_TOAST
from utils.run_context import trace_one_test

NOTE = "AUTOMATION_TEST move parent with extended asset"
# Transaction Type shown in the Transaction Approval List for an Internal Movement
TRANSFER = "TRANSFER"


@pytest.fixture
def page(assign_user_logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once, as the Asset Assign user."""
    yield from trace_one_test(assign_user_logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The search by serial
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_movement_extended_serial_is_not_found(
    page, internal_movement_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Internal Movement (CR F04S01): the serial of an extended asset cannot be searched on its own; the message "No asset found" is shown."""
    # Step 1: open Asset Internal Movement
    internal_movement_page.navigate_here()

    # Step 2: search the extended asset's serial: "No asset found" and no suggestion
    internal_movement_page.verify_serial_not_found(assigned_parent_with_extended["extended"])
    take_screenshot("extended serial not found")


@pytest.mark.regression
def test_movement_parent_search_suggests_only_the_parent(
    page, internal_movement_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Internal Movement (CR F04S01): searching the parent serial offers the parent only, never its extended asset."""
    # Step 1: open Asset Internal Movement
    internal_movement_page.navigate_here()

    # Step 2: search the parent serial: one suggestion, the parent's
    internal_movement_page.verify_only_parent_suggested(
        assigned_parent_with_extended["parent"], assigned_parent_with_extended["extended"]
    )
    take_screenshot("only the parent is suggested")


# ---------------------------------------------------------------------------
# 2. The Asset List
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_movement_parent_adds_extended_asset_below_it(
    page, internal_movement_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Internal Movement (CR F04S01): adding the parent to the list adds its extended asset below it, indented, without an SL number or a delete button."""
    # Step 1: select the parent and add it to the Asset List
    internal_movement_page.navigate_here()
    internal_movement_page.select_asset_by_serial(assigned_parent_with_extended["parent"])
    internal_movement_page.add_to_grid()
    take_screenshot("parent and extended asset in the list")

    # Step 2: the extended asset is listed directly below the parent, indented, without SL or buttons
    internal_movement_page.verify_extended_assets_in_list(
        assigned_parent_with_extended["parent"], [assigned_parent_with_extended["extended"]]
    )


@pytest.mark.regression
def test_movement_employee_pin_lists_extended_assets(
    page, internal_movement_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Internal Movement (CR F04S01): Search By Employee Pin loads the employee's assets with each extended asset below its parent, indented, without an SL number or a button."""
    # Step 1: switch Search By to Employee Pin and load the assets of the employee
    internal_movement_page.navigate_here()
    internal_movement_page.choose_search_by_employee_pin()
    internal_movement_page.load_assets_of_employee(ASSIGNEE_PIN)
    take_screenshot("assets of the employee")

    # Step 2: the extended asset is listed directly below its parent, indented, without SL or button
    internal_movement_page.verify_extended_assets_in_full_list(
        assigned_parent_with_extended["parent"], [assigned_parent_with_extended["extended"]]
    )


@pytest.mark.regression
def test_movement_removing_parent_removes_extended_asset(
    page, internal_movement_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Internal Movement (CR F04S01): removing the parent from the Asset List removes its extended asset too."""
    # Step 1: select the parent and add it to the Asset List
    internal_movement_page.navigate_here()
    internal_movement_page.select_asset_by_serial(assigned_parent_with_extended["parent"])
    internal_movement_page.add_to_grid()

    # Step 2: delete the parent row: the list is empty
    internal_movement_page.remove_parent_from_list()
    take_screenshot("list empty after removing the parent")
    internal_movement_page.verify_asset_list_empty()


# ---------------------------------------------------------------------------
# 3. One movement of the parent asset (run these three together)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_movement_submit_parent_with_extended_asset(
    page, internal_movement_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Internal Movement (CR F04S01): the parent and its extended asset are submitted together for the movement."""
    # Step 1: fill the form with the parent, the employee, the new building and a note
    internal_movement_page.navigate_here()
    internal_movement_page.fill_form(assigned_parent_with_extended["parent"], ASSIGNEE_PIN, NOTE, MOVE_BUILDING)
    internal_movement_page.verify_extended_assets_in_list(
        assigned_parent_with_extended["parent"], [assigned_parent_with_extended["extended"]]
    )
    take_screenshot("form filled")

    # Step 2: Submit shows the success message
    toast = internal_movement_page.submit_and_get_toast()
    internal_movement_page.verify_toast_text(toast, MOVEMENT_SUBMIT_TOAST, "Submit on Asset Internal Movement")


@pytest.mark.regression
def test_movement_approval_details_show_extended_asset(
    page, transaction_approval_page, assigned_parent_with_extended, take_screenshot
):
    """Transaction Approval List (CR F06S01): the Details popup of the movement lists the extended asset below its parent, indented, without an SL number."""
    # Step 1: open the Details popup of the pending movement of the parent
    transaction_approval_page.navigate_here()
    transaction_approval_page.open_details_of_row_with_serial(assigned_parent_with_extended["parent"], TRANSFER, "PENDING")
    take_screenshot("approval details popup")

    # Step 2: the extended asset is listed below the parent
    transaction_approval_page.verify_popup_extended_assets_below_parent(
        assigned_parent_with_extended["parent"], [assigned_parent_with_extended["extended"]]
    )
    transaction_approval_page.close_popup()


@pytest.mark.regression
def test_approve_movement_moves_parent_and_extended_asset(
    page, transaction_approval_page, asset_serial_global_list_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Internal Movement (CR F04S01): approving the movement of the parent moves its extended asset to the same building and floor."""
    # Step 1: approve the pending movement of the parent
    transaction_approval_page.navigate_here()
    toast = transaction_approval_page.approve_transaction_for_serial(TRANSFER, assigned_parent_with_extended["parent"])
    transaction_approval_page.verify_toast_text(toast, TRANSACTION_APPROVE_TOAST, "Approve of the movement")

    # Step 2: the parent and its extended asset show the new building and the same floor
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_moved_together(
        assigned_parent_with_extended["parent"], assigned_parent_with_extended["extended"], MOVE_BUILDING
    )
    take_screenshot("parent and extended asset moved")
