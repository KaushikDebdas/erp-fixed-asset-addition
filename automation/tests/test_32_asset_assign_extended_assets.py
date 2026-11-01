"""
test_33_asset_assign_extended_assets.py: the Asset Assign screen and the
transaction screens that follow it, for a parent asset that has extended
assets (CR FAHOV2-643, feature F02 Asset Assign, with F05 Transaction List,
F06 Transaction Approval List and F07 Asset Assign Acknowledgement).

Two parent assets are made once per run through HOFIN, HOFA and HOFIN:
    parent_with_extended           a parent with one extended asset (pair A)
    parent_with_inactive_extended  a parent with three extended assets, the third
                                   written off, so it is inactive (pair B)
The first test of a run that needs a pair makes it (a few minutes). Built from
automation/element_catalog/asset_assign.md and the live checks of 2026-10-10.

The screens are used by the Asset Assign user (ASSIGN_USER_USERNAME and
ASSIGN_USER_PASSWORD in .env), who is also the employee the assets are assigned
to (ASSIGNEE_PIN in test_data/asset_transaction_data.py).

The tests run top to bottom. Each group below follows one assignment, so run a
group together:
    1. The search (pair A): an extended serial is not found; the parent is the only suggestion
    2. The Asset List (pair A): the extended asset is added below the parent; removing the parent removes it too
    3. One assignment (pair A): Submit, Approval List popup, Approve (both ASSIGNED),
       Transaction List popup, Acknowledgement popup, Acknowledge
    4. Several and inactive extended assets (pair B): all active extended assets are listed,
       the disposed one is not; Draft, Submit from the Transaction List, Approve, Acknowledge;
       a new extended asset added to the assigned parent is assigned automatically

To run part of the file:
    pytest tests/test_33_asset_assign_extended_assets.py -k "not_found or suggests"
"""
import pytest

from test_data.asset_transaction_data import ASSIGN, ASSIGNEE_NAME, ASSIGNEE_PIN
from test_data.toast_messages import (
    ACKNOWLEDGE_TOAST,
    ASSIGN_DRAFT_TOAST,
    ASSIGN_SUBMIT_TOAST,
    TRANSACTION_APPROVE_TOAST,
)
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, build_expected, submit_draft_from_list

NOTE = "AUTOMATION_TEST assign parent with extended asset"


@pytest.fixture
def page(assign_user_logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once, as the Asset Assign user."""
    yield from trace_one_test(assign_user_logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The search (pair A)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_assign_extended_serial_is_not_found(page, assign_page, parent_with_extended, take_screenshot):
    """Asset Assign (CR F02S01): the serial of an extended asset cannot be searched on its own; the message "No asset found" is shown."""
    # Step 1: open Asset Assign
    assign_page.navigate_here()

    # Step 2: search the extended asset's serial: "No asset found" and no suggestion
    assign_page.verify_serial_not_found(parent_with_extended["extended"])
    take_screenshot("extended serial not found")


@pytest.mark.regression
def test_assign_parent_search_suggests_only_the_parent(page, assign_page, parent_with_extended, take_screenshot):
    """Asset Assign (CR F02S01): searching the parent serial offers the parent only, never its extended asset."""
    # Step 1: open Asset Assign
    assign_page.navigate_here()

    # Step 2: search the parent serial: one suggestion, the parent's
    assign_page.verify_only_parent_suggested(parent_with_extended["parent"], parent_with_extended["extended"])
    take_screenshot("only the parent is suggested")


# ---------------------------------------------------------------------------
# 2. The Asset List (pair A)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_assign_parent_adds_extended_asset_below_it(page, assign_page, parent_with_extended, take_screenshot):
    """Asset Assign (CR F02S01): adding the parent to the list adds its extended asset below it, indented, without an SL number or a delete button."""
    # Step 1: select the parent and add it to the Asset List
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(parent_with_extended["parent"])
    assign_page.add_to_grid()
    take_screenshot("parent and extended asset in the list")

    # Step 2: the extended asset is listed directly below the parent, indented, without SL or buttons
    assign_page.verify_extended_assets_in_list(parent_with_extended["parent"], [parent_with_extended["extended"]])


@pytest.mark.regression
def test_assign_removing_parent_removes_extended_asset(page, assign_page, parent_with_extended, take_screenshot):
    """Asset Assign (CR F02S01): removing the parent from the Asset List removes its extended asset too."""
    # Step 1: select the parent and add it to the Asset List
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(parent_with_extended["parent"])
    assign_page.add_to_grid()

    # Step 2: delete the parent row: the list is empty
    assign_page.remove_parent_from_list()
    take_screenshot("list empty after removing the parent")
    assign_page.verify_asset_list_empty()


# ---------------------------------------------------------------------------
# 3. One assignment of pair A (run these together)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_assign_submit_parent_with_extended_asset(page, assign_page, parent_with_extended, take_screenshot):
    """Asset Assign (CR F02S01): the parent and its extended asset are submitted together for assignment."""
    # Step 1: fill the form with the parent, the employee and a note
    assign_page.navigate_here()
    assign_page.fill_form(parent_with_extended["parent"], ASSIGNEE_PIN, NOTE)
    assign_page.verify_extended_assets_in_list(parent_with_extended["parent"], [parent_with_extended["extended"]])
    take_screenshot("form filled")

    # Step 2: Submit shows the success message
    toast = assign_page.submit_and_get_toast()
    assign_page.verify_toast_text(toast, ASSIGN_SUBMIT_TOAST, "Submit on Asset Assign")


@pytest.mark.regression
def test_approval_details_list_extended_asset_below_parent(
    page, transaction_approval_page, parent_with_extended, take_screenshot
):
    """Transaction Approval List (CR F06S01): the Details popup of the assignment lists the extended asset below its parent, indented, without an SL number."""
    # Step 1: open the Details popup of the pending assignment of the parent
    transaction_approval_page.navigate_here()
    transaction_approval_page.open_details_of_row_with_serial(parent_with_extended["parent"], ASSIGN, "PENDING")
    take_screenshot("approval details popup")

    # Step 2: the extended asset is listed below the parent
    transaction_approval_page.verify_popup_extended_assets_below_parent(
        parent_with_extended["parent"], [parent_with_extended["extended"]]
    )
    transaction_approval_page.close_popup()


@pytest.mark.regression
def test_approve_assign_assigns_parent_and_extended_asset(
    page, transaction_approval_page, asset_serial_global_list_page, parent_with_extended, take_screenshot
):
    """Asset Assign (CR F02S01): approving the assignment of the parent assigns its extended asset too."""
    # Step 1: approve the pending assignment of the parent
    transaction_approval_page.navigate_here()
    toast = transaction_approval_page.approve_transaction_for_serial(ASSIGN, parent_with_extended["parent"])
    transaction_approval_page.verify_toast_text(toast, TRANSACTION_APPROVE_TOAST, "Approve of the assignment")

    # Step 2: the parent and its extended asset are both ASSIGNED in the Asset Serial Global List
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_all_assigned(
        [parent_with_extended["parent"], parent_with_extended["extended"]]
    )
    take_screenshot("parent and extended asset assigned")


@pytest.mark.regression
def test_transaction_list_details_show_extended_asset(
    page, transaction_list_page, parent_with_extended, take_screenshot
):
    """Transaction List (CR F02S01, F05S01): the Details popup of the approved assignment lists the extended asset below its parent, indented, without an SL number."""
    # Step 1: open the Details popup of the approved assignment of the parent
    transaction_list_page.navigate_here()
    transaction_list_page.open_details_of_row_with_serial(parent_with_extended["parent"], ASSIGN, "APPROVED")
    take_screenshot("transaction list details popup")

    # Step 2: the extended asset is listed below the parent
    transaction_list_page.verify_popup_extended_assets_below_parent(
        parent_with_extended["parent"], [parent_with_extended["extended"]]
    )
    transaction_list_page.close_popup()


@pytest.mark.regression
def test_acknowledgement_details_show_extended_asset(
    page, acknowledgement_page, parent_with_extended, take_screenshot
):
    """Asset Assign Acknowledgement (CR F07S01): the Details popup lists the extended asset below its parent, indented, without an SL number."""
    # Step 1: open the Details popup of the assignment waiting for acknowledgement
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(parent_with_extended["parent"])
    take_screenshot("acknowledgement details popup")

    # Step 2: the extended asset is listed below the parent
    acknowledgement_page.verify_popup_extended_assets_below_parent(
        parent_with_extended["parent"], [parent_with_extended["extended"]]
    )
    acknowledgement_page.close_popup()


@pytest.mark.regression
def test_acknowledge_assign_covers_parent_and_extended_asset(
    page, acknowledgement_page, parent_with_extended, take_screenshot
):
    """Asset Assign Acknowledgement (CR F02S01): acknowledging the assignment of the parent acknowledges its extended asset too; both are in My Assigned Asset."""
    # Step 1: acknowledge the assignment of the parent from its Details popup
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(parent_with_extended["parent"])
    toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
    acknowledgement_page.verify_toast_contains(toast, ACKNOWLEDGE_TOAST, "Acknowledge of the assignment")
    take_screenshot("assignment acknowledged")

    # Step 2: the parent and its extended asset are in My Assigned Asset
    acknowledgement_page.verify_my_assets_include([parent_with_extended["parent"], parent_with_extended["extended"]])


# ---------------------------------------------------------------------------
# 4. Several and inactive extended assets (pair B, run these together)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_assign_lists_all_active_extended_assets_below_parent(
    page, assign_page, parent_with_inactive_extended, take_screenshot
):
    """Asset Assign (CR F02S01): a parent with several extended assets brings all its active ones below it, in order; the disposed one is not among them."""
    # Step 1: select the parent and add it to the Asset List
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(parent_with_inactive_extended["parent"])
    assign_page.add_to_grid()
    take_screenshot("parent and its active extended assets in the list")

    # Step 2: the two active extended assets are listed below the parent and nothing else (3 rows)
    assign_page.verify_extended_assets_in_list(
        parent_with_inactive_extended["parent"], parent_with_inactive_extended["active"]
    )


@pytest.mark.regression
def test_assign_does_not_offer_disposed_extended_asset(
    page, assign_page, parent_with_inactive_extended, take_screenshot
):
    """Asset Assign (CR F02S01 exception): an extended asset that was written off is inactive; it cannot be searched and the parent does not bring it."""
    # Step 1: the disposed extended asset's serial is not found
    assign_page.navigate_here()
    assign_page.verify_serial_not_found(parent_with_inactive_extended["inactive"])

    # Step 2: the parent's list does not hold it
    assign_page.select_asset_by_serial(parent_with_inactive_extended["parent"])
    assign_page.add_to_grid()
    take_screenshot("disposed extended asset is not listed")
    assign_page.verify_serial_not_in_list(parent_with_inactive_extended["inactive"])


@pytest.mark.regression
def test_assign_draft_shows_active_extended_assets(
    page, assign_page, transaction_list_page, parent_with_inactive_extended, take_screenshot
):
    """Asset Assign (CR F02S01): a Draft of the parent is listed in the Transaction List with its active extended assets below it and without the disposed one."""
    # Step 1: fill the form and save it as a Draft
    pair = parent_with_inactive_extended
    assign_page.navigate_here()
    assign_page.fill_form(pair["parent"], ASSIGNEE_PIN, NOTE)
    assign_page.draft_and_verify_toast(ASSIGN_DRAFT_TOAST)

    # Step 2: the Draft's Details popup lists the active extended assets below the parent
    transaction_list_page.navigate_here()
    transaction_list_page.open_details_of_row_with_serial(pair["parent"], ASSIGN, "DRAFT")
    take_screenshot("draft details popup")
    transaction_list_page.verify_popup_extended_assets_below_parent(pair["parent"], pair["active"])
    transaction_list_page.verify_popup_does_not_list(pair["inactive"])
    transaction_list_page.close_popup()


@pytest.mark.regression
def test_assign_draft_submit_approve_assigns_all_active(
    page, assign_page, transaction_list_page, transaction_approval_page, asset_serial_global_list_page,
    parent_with_inactive_extended, take_screenshot
):
    """Asset Assign (CR F02S01): the Draft submitted from the Transaction List and approved assigns the parent and its active extended assets."""
    # Step 1: the expected values of the Draft made by the previous test
    pair = parent_with_inactive_extended
    assign_page.navigate_here()
    transaction_date = assign_page.get_transaction_date().replace("-", "/")
    expected = build_expected(ASSIGNEE_PIN, ASSIGNEE_NAME, NOTE, transaction_date)

    # Step 2: Submit the Draft from the Transaction List, then Approve it
    submit_draft_from_list(transaction_list_page, assign_page, ASSIGN, pair["parent"], expected, ASSIGN_SUBMIT_TOAST, take_screenshot)
    approve_and_verify(transaction_approval_page, ASSIGN, pair["parent"], expected, take_screenshot)

    # Step 3: the parent and its active extended assets are ASSIGNED; the disposed one is not listed
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_all_assigned([pair["parent"]] + pair["active"])
    asset_serial_global_list_page.search_by_exact_serial(pair["inactive"])
    asset_serial_global_list_page.verify_serial_not_listed(pair["inactive"])


@pytest.mark.regression
def test_acknowledge_assign_lists_all_active_extended(
    page, acknowledgement_page, parent_with_inactive_extended, take_screenshot
):
    """Asset Assign Acknowledgement (CR F02S01): acknowledging the assignment puts the parent and its active extended assets in My Assigned Asset."""
    # Step 1: acknowledge the assignment of the parent from its Details popup
    pair = parent_with_inactive_extended
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(pair["parent"])
    toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
    acknowledgement_page.verify_toast_contains(toast, ACKNOWLEDGE_TOAST, "Acknowledge of the assignment")
    take_screenshot("assignment acknowledged")

    # Step 2: the parent and its active extended assets are in My Assigned Asset
    acknowledgement_page.verify_my_assets_include([pair["parent"]] + pair["active"])


@pytest.mark.regression
def test_new_extended_asset_of_assigned_parent_is_auto_assigned(
    page, hofin_flow, asset_serial_global_list_page, parent_with_inactive_extended, take_screenshot
):
    """Asset Assign (CR F02S01): an extended asset added to an assigned parent is assigned automatically to the same employee, in the same building, floor and room."""
    # Step 1: the extended assets the parent has before the addition
    pair = parent_with_inactive_extended
    asset_serial_global_list_page.navigate_here()
    known_serials = asset_serial_global_list_page.read_addition_history_serials(pair["parent"])

    # Step 2: add one more extended asset through HOFIN, HOFA and HOFIN
    hofin_flow.add_extended_asset(pair["parent"])

    # Step 3: the parent's Addition History has one new extended asset
    asset_serial_global_list_page.navigate_here()
    all_serials = asset_serial_global_list_page.read_addition_history_serials(pair["parent"])
    new_serials = [serial for serial in all_serials if serial not in known_serials]
    assert len(new_serials) == 1, f"Expected one new extended asset after the addition but found {new_serials}."

    # Step 4: the new extended asset is assigned like its parent, without any assignment made for it
    asset_serial_global_list_page.verify_same_assignment_as_parent(pair["parent"], new_serials[0])
    take_screenshot("new extended asset assigned")
