"""
test_12_asset_unassign_new.py: tests for the Asset Un Assign screen (Fixed Asset
> Asset Transaction > Asset Un Assign).

Built from automation/element_catalog/asset_unassign.md. The asset is NOT
created here: it is the saved Furniture asset, read with
registrations.get_approved("furniture", "spot", AAQ_ASSET_GROUP)
(test_data/saved_assets.json). Its saved record is never changed. Un Assign only
works on an assigned asset, so each test reads the asset's real Assign Status
from the Asset Serial Global List and assigns it first when needed
(`transactions.ensure_assigned()`, utils/transaction_helper.py). The whole file
logs in once and every test reuses that session.

The asset is handed over to the employee in HANDOVER_SEARCH (see
test_data/asset_transaction_data.py), who must be a different employee from the
current holder.

The tests run top to bottom:
    1. The form: the assigned asset, Search By, employee-PIN search, same-employee refusal
    2. LAST: Draft, Transaction List (Details, Edit, Submit), Transaction Approval
       List (Details, Approve), and the asset is UNASSIGNED (this one test is a
       little longer than the others because it is the whole flow)

The last test must stay last in the file: it leaves the asset UNASSIGNED, so the
next run starts clean.

To run part of the file:
    pytest tests/test_12_asset_unassign_new.py -k "same_employee"
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
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, build_expected, submit_draft_from_list

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
def test_unassign_serial_search_shows_assigned_asset(page, unassign_page, transactions, take_screenshot):
    """Asset Un Assign: selecting the assigned asset shows its details and current assignee."""
    # Step 1: get the saved asset, assigned
    serial = transactions.ensure_assigned()

    # Step 2: open Asset Un Assign, type the serial, search, and pick the suggestion
    unassign_page.navigate_here()
    unassign_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")

    # Step 3: the form shows the Furniture asset, ASSIGNED, with its current assignee
    expected = {
        "assetName": FURNITURE_FORM_DETAILS["assetName"],
        "previousAssignStatus": ASSIGNED,
        "assignedEmployeePinNo": ASSIGNEE_PIN,
        "assignedEmployeeName": ASSIGNEE_NAME,
    }
    unassign_page.verify_form_shows(serial, expected)


@pytest.mark.regression
def test_unassign_search_by_options(page, unassign_page, take_screenshot):
    """Asset Un Assign: Search By offers Serial (the default) and Employee Pin."""
    # Step 1: open the screen
    unassign_page.navigate_here()
    take_screenshot("search by options")

    # Step 2: both choices are there and Serial is selected
    unassign_page.verify_search_by_options()


@pytest.mark.regression
def test_unassign_search_by_employee_pin_loads_assets(page, unassign_page, transactions, take_screenshot):
    """Asset Un Assign: searching by Employee Pin loads that employee's assigned assets."""
    # Step 1: get the saved asset, assigned to the test employee
    serial = transactions.ensure_assigned()

    # Step 2: switch Search By to Employee Pin and search the employee
    unassign_page.navigate_here()
    unassign_page.choose_search_by_employee_pin()
    unassign_page.load_assets_of_employee(ASSIGNEE_PIN)
    take_screenshot("assets of the employee loaded")

    # Step 3: the Asset List holds the employee's assets, including the saved asset
    unassign_page.verify_asset_in_list(serial)


@pytest.mark.regression
def test_unassign_to_same_employee_is_refused(page, unassign_page, transactions, take_screenshot):
    """Asset Un Assign: the asset cannot be handed over to the employee who already holds it."""
    # Step 1: add the assigned asset
    serial = transactions.ensure_assigned()
    unassign_page.navigate_here()
    unassign_page.select_asset_by_serial(serial)
    unassign_page.add_to_grid()

    # Step 2: pick the current holder as the hand-over employee and click Draft
    unassign_page.select_employee(ASSIGNEE_PIN)
    unassign_page.draft_and_verify_toast("Asset assigned to same employee!")
    take_screenshot("same employee refused")


# ---------------------------------------------------------------------------
# 2. LAST: the full flow (leaves the asset UNASSIGNED)
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
    unassign_page.draft_and_verify_toast("Asset Un-Assign Draft Successfully")
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
