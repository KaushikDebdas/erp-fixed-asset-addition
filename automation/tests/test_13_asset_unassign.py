"""
test_13_asset_unassign.py: tests for the Asset Un Assign screen (Fixed Asset
> Asset Transaction > Asset Un Assign).

Built from automation/element_catalog/asset_unassign.md. The assets are NOT created
here: they are the two usage assets of the asset pool (test_data/asset_slots.py),
usage_a for the Draft + Submit path and usage_b for the Submit-only path. Un Assign
only works on an assigned asset, so each test reads the asset's real Assign Status
from the Asset Serial Global List and assigns it first when needed
(`transactions.ensure_assigned()`, utils/transaction_helper.py). The whole file
logs in once and every test reuses that session. The Asset Un Assign form has the same
Search By and Employee Pin search as Asset Internal Movement, which test_12 checks.

The asset is handed over to the employee in HANDOVER_SEARCH (see
test_data/asset_transaction_data.py), who must be a different employee from the
current holder.

The tests run top to bottom:
    1. The form: the assigned asset, same-employee refusal
    2. The Draft + Submit path (usage_a): Draft, Transaction List (Details, Edit, Submit),
       Transaction Approval List (Details, Approve), and the asset is UNASSIGNED (this one
       test is a little longer than the others because it is the whole flow)
    3. The Submit-only path (usage_b): Submit straight from the form, Approve, UNASSIGNED

Both assets end UNASSIGNED, which is the state the expense (test_16) and write-off
(test_27) files use them in.

To run part of the file:
    pytest tests/test_13_asset_unassign.py -k "same_employee"
"""
import pytest

from test_data.asset_transaction_data import (
    ASSIGNED,
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    FURNITURE_FORM_DETAILS,
    HANDOVER_NAME,
    HANDOVER_PIN,
    HANDOVER_SEARCH,
    UNASSIGN,
    UNASSIGNED,
)
from test_data.toast_messages import (
    UNASSIGN_DRAFT_TOAST,
    UNASSIGN_SAME_EMPLOYEE_TOAST,
)
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, build_expected, submit_draft_from_list
from utils.transaction_helper import USAGE_B

NOTE = "AUTOMATION_TEST unassign note"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The form
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_unassign_to_same_employee_is_refused(page, unassign_page, transactions, take_screenshot):
    """Asset Un Assign: the form shows the assigned asset with its current assignee, and it cannot be handed over to the employee who already holds it."""
    # Step 1: select the assigned asset; the form shows the Furniture asset, ASSIGNED, with its current assignee
    serial = transactions.ensure_assigned()
    unassign_page.navigate_here()
    unassign_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")
    expected = {
        "assetName": FURNITURE_FORM_DETAILS["assetName"],
        "previousAssignStatus": ASSIGNED,
        "assignedEmployeePinNo": ASSIGNEE_PIN,
        "assignedEmployeeName": ASSIGNEE_NAME,
    }
    unassign_page.verify_form_shows(serial, expected)

    # Step 2: add the asset, pick the current holder as the hand-over employee and click Draft
    unassign_page.add_to_grid()
    unassign_page.select_employee(ASSIGNEE_PIN)
    unassign_page.draft_and_verify_toast(UNASSIGN_SAME_EMPLOYEE_TOAST)
    take_screenshot("same employee refused")


# ---------------------------------------------------------------------------
# 2. The Draft + Submit path (usage_a): leaves the asset UNASSIGNED
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_unassign_full_flow_draft_submit_approve(
    page, unassign_page, transaction_list_page, transaction_approval_page,
    asset_serial_global_list_page, transactions, take_screenshot
):
    """Asset Un Assign: Draft, Submit from the Transaction List, Approve, and the asset becomes UNASSIGNED."""
    # Step 1: get the assigned asset, fill the form (hand over to a different employee) and save a Draft
    serial = transactions.ensure_assigned()
    unassign_page.navigate_here()
    transaction_date = unassign_page.fill_form(serial, HANDOVER_SEARCH, NOTE)
    unassign_page.verify_employee_selected(HANDOVER_PIN, HANDOVER_NAME)
    take_screenshot("unassign form filled")
    unassign_page.draft_and_verify_toast(UNASSIGN_DRAFT_TOAST)
    take_screenshot("unassign draft saved")
    expected = build_expected(HANDOVER_PIN, HANDOVER_NAME, NOTE, transaction_date)

    # Step 2: Transaction List: check the Draft, open Edit, and Submit
    submit_draft_from_list(
        transaction_list_page, unassign_page, UNASSIGN, serial, expected,
        "Asset Un-Assign Submit Successfully", take_screenshot,
    )

    # Step 3: Transaction Approval List: check the popup, Approve, confirm APPROVED
    approve_and_verify(transaction_approval_page, UNASSIGN, serial, expected, take_screenshot)

    # Step 4: the Global List shows the asset UNASSIGNED
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("asset is unassigned")
    asset_serial_global_list_page.verify_assign_status(serial, UNASSIGNED)


# ---------------------------------------------------------------------------
# 3. The Submit-only path (usage_b): leaves the asset UNASSIGNED
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_unassign_submit_only_flow(page, transactions, asset_serial_global_list_page, take_screenshot):
    """Asset Un Assign: an unassign submitted straight from the form (no Draft) and approved makes the asset UNASSIGNED."""
    # Step 1: get the second usage asset, assigned
    serial = transactions.ensure_assigned(USAGE_B)

    # Step 2: Submit straight from the Asset Un Assign form and Approve (the messages of both are checked)
    transactions.unassign(serial)

    # Step 3: the Global List shows the asset UNASSIGNED
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("asset is unassigned")
    asset_serial_global_list_page.verify_assign_status(serial, UNASSIGNED)
