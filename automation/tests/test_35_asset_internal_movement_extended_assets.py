"""
test_35_asset_internal_movement_extended_assets.py: the Asset Internal Movement
screen, the Transaction List and the Transaction Approval List for a parent
asset that has an extended asset (CR FAHOV2-643, feature F04 Asset Internal
Movement, with F05 Transaction List, F06 Transaction Approval List and F01S01).

The parent asset and its one extended asset are made once per run through HOFIN,
HOFA and HOFIN (`parent_with_extended`, the REAL serials are read from the HOFA
Global List), then ASSIGNED to the HOFA acknowledger and acknowledged
(`assigned_parent_with_extended`), because an asset with an acknowledgement
pending is not offered in Asset Internal Movement. Both fixtures do only the
steps that are missing, so this file runs alone or after test_33 (which assigns
and acknowledges the same pair). Built from
automation/element_catalog/asset_internal_movement.md.

The screens are used in HOFA (HOFA_URL) by the HOFA acknowledger (HOFA_ACK_USERNAME
and HOFA_ACK_PASSWORD in .env), who is also the employee the assets are assigned to.

The tests run top to bottom. Group 3 follows one movement of the parent, so run
it together:
    1. The search by serial: an extended serial is not found; the parent is the only suggestion
    2. The Asset List: by serial and by Employee Pin the extended asset is listed below the
       parent; removing the parent removes it too
    3. One movement: Submit; the Transaction List and Transaction Approval List popups list the
       extended asset below the parent; HOFIN refuses an addition to the parent while the movement
       is pending; Approve moves both; both have an approved TRANSFER in their Transaction History

Not covered here: "inactive extended assets are not listed", which needs a written-off
extended asset (covered for Asset Assign in test_33).

To run part of the file:
    pytest tests/test_35_asset_internal_movement_extended_assets.py -k "not_found or suggests"
"""
import pytest

from test_data.asset_transaction_data import TRANSFER
from test_data.hofin_asset_data import ADDITION_PARENT_PENDING_MESSAGE, HOFA_ACK_EMPLOYEE_PIN
from test_data.toast_messages import MOVEMENT_SUBMIT_TOAST, TRANSACTION_APPROVE_TOAST
from utils.run_context import trace_one_test

NOTE = "AUTOMATION_TEST move parent with extended asset"

# The employee the assets are assigned to and moved for: the HOFA acknowledger, the user of this file
ASSIGNEE_PIN = HOFA_ACK_EMPLOYEE_PIN


@pytest.fixture
def page(hofa_logged_in_page, request):
    """Every test in this file reuses the one HOFA tab that logged in once, as the HOFA acknowledger."""
    assert ASSIGNEE_PIN, "HOFA_ACK_USERNAME must be a numeric login name (the employee PIN) to assign assets to it."
    yield from trace_one_test(hofa_logged_in_page, request)


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


@pytest.mark.smoke
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
    """Asset Internal Movement (CR F04S01): Search By Employee Pin loads the employee's assets with the extended asset below its parent, indented, without an SL number or a button."""
    # Step 1: switch Search By to Employee Pin and load the assets of the employee
    internal_movement_page.navigate_here()
    internal_movement_page.choose_search_by_employee_pin()
    internal_movement_page.load_assets_of_employee(ASSIGNEE_PIN)
    take_screenshot("assets of the employee")

    # Step 2: the extended asset is listed directly below its parent, indented, without SL or button
    internal_movement_page.verify_extended_assets_in_list(
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
# 3. One movement of the parent asset (run these together)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_movement_submit_parent_with_extended_asset(
    page, internal_movement_page, assigned_parent_with_extended, hofin_flow_data, take_screenshot
):
    """Asset Internal Movement (CR F04S01): the parent and its extended asset are submitted together for the movement."""
    # Step 1: fill the form with the parent, the employee, the first building and floor, and a note
    internal_movement_page.navigate_here()
    internal_movement_page.fill_form(assigned_parent_with_extended["parent"], ASSIGNEE_PIN, NOTE, True)
    internal_movement_page.verify_extended_assets_in_list(
        assigned_parent_with_extended["parent"], [assigned_parent_with_extended["extended"]]
    )
    take_screenshot("form filled")

    # Step 2: Submit shows the success message
    building = internal_movement_page.get_building()
    toast = internal_movement_page.submit_and_get_toast()
    internal_movement_page.verify_toast_text(toast, MOVEMENT_SUBMIT_TOAST, "Submit on Asset Internal Movement")

    # Step 3: keep the chosen building for the approval test
    hofin_flow_data["moved_to_building"] = building


@pytest.mark.regression
def test_movement_transaction_list_details_show_extended_asset(
    page, transaction_list_page, assigned_parent_with_extended, take_screenshot
):
    """Transaction List (CR F04S01, F05S01): the Details popup of the pending movement lists the extended asset below its parent, indented, without an SL number."""
    # Step 1: open the Details popup of the pending movement of the parent
    transaction_list_page.navigate_here()
    transaction_list_page.open_details_of_row_with_serial(assigned_parent_with_extended["parent"], TRANSFER, "PENDING")
    take_screenshot("transaction list details popup")

    # Step 2: the extended asset is listed below the parent
    transaction_list_page.verify_popup_extended_assets_below_parent(
        assigned_parent_with_extended["parent"], [assigned_parent_with_extended["extended"]]
    )
    transaction_list_page.close_popup()


@pytest.mark.regression
def test_movement_approval_details_show_extended_asset(
    page, transaction_approval_page, assigned_parent_with_extended, take_screenshot
):
    """Transaction Approval List (CR F04S01, F06S01): the Details popup of the movement lists the extended asset below its parent, indented, without an SL number."""
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
def test_hofin_addition_is_refused_while_movement_is_pending(hofin_flow, assigned_parent_with_extended):
    """HOFIN Vendor Bill Payable (CR F01S01): an addition to a parent whose Internal Movement waits for approval is refused with the CR message."""
    parent = assigned_parent_with_extended["parent"]
    expected = ADDITION_PARENT_PENDING_MESSAGE.format(parent)

    # Step 1: the HOFIN creator fills an addition bill for the parent and clicks Submit
    message = hofin_flow.submit_addition_and_read_refusal(parent)

    # Step 2: HOFIN refuses it with the CR message instead of submitting the bill
    assert message != "", f"The addition to {parent} was submitted, but the parent's Internal Movement is still pending."
    assert expected in message, f"Expected the message '{expected}' but HOFIN showed '{message}'."


@pytest.mark.smoke
@pytest.mark.regression
def test_approve_movement_moves_parent_and_extended_asset(
    page, transaction_approval_page, asset_serial_global_list_page, assigned_parent_with_extended,
    hofin_flow_data, take_screenshot
):
    """Asset Internal Movement (CR F04S01): approving the movement of the parent moves its extended asset to the same building, floor and room."""
    building = hofin_flow_data.get("moved_to_building", "")
    assert building != "", "No movement was submitted in this run. Run test_movement_submit_parent_with_extended_asset first."

    # Step 1: approve the pending movement of the parent
    transaction_approval_page.navigate_here()
    toast = transaction_approval_page.approve_transaction_for_serial(TRANSFER, assigned_parent_with_extended["parent"])
    transaction_approval_page.verify_toast_text(toast, TRANSACTION_APPROVE_TOAST, "Approve of the movement")

    # Step 2: the parent shows the new building and a floor, and its extended asset the same location
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_moved_together(
        assigned_parent_with_extended["parent"], assigned_parent_with_extended["extended"], building
    )
    take_screenshot("parent and extended asset moved")


@pytest.mark.regression
def test_moved_assets_have_an_approved_transfer_record(
    page, asset_serial_global_list_page, assigned_parent_with_extended, take_screenshot
):
    """Asset Serial Global List (CR F04S01): the movement is applied to the parent and to the extended asset alike; both have an approved TRANSFER in their Transaction History."""
    # Step 1: the parent has an approved TRANSFER transaction
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_transaction_in_history(assigned_parent_with_extended["parent"], TRANSFER, "APPROVED")

    # Step 2: the extended asset has one too
    asset_serial_global_list_page.verify_transaction_in_history(assigned_parent_with_extended["extended"], TRANSFER, "APPROVED")
    take_screenshot("transfer records checked")
