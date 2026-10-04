"""
test_12_asset_unassign.py: tests for the Asset Un Assign screen (Fixed Asset
> Asset Transaction > Asset Un Assign).

Built from automation/element_catalog/asset_unassign.md. The tests use a
freshly approved asset that is already assigned (the `assigned_asset` fixture
in conftest.py). The whole file logs in once and every test reuses that
session.

The asset is handed over to the employee in HANDOVER_SEARCH (see
test_data/asset_transaction_data.py), who must be a different employee from
the current holder. The last test takes the asset all the way: Draft,
Transaction List (Details, Edit, Submit), Transaction Approval List (Details,
Approve), and finally checks the asset is UNASSIGNED.
"""
import pytest

from test_data.asset_transaction_data import (
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    HANDOVER_NAME,
    HANDOVER_PIN,
    HANDOVER_SEARCH,
    UNASSIGN,
)
from utils.run_context import trace_one_test
from utils.transaction_flow import approve_and_verify, submit_draft_from_list

NOTE = "AUTOMATION_TEST unassign note"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_unassign_serial_search_shows_assigned_asset(
    page, unassign_page, assigned_asset, take_screenshot
):
    """Asset Un Assign: selecting an assigned asset shows its details and current assignee."""
    serial = assigned_asset["serial"]

    # Step 1: open Asset Un Assign
    unassign_page.navigate_here()

    # Step 2: type the serial, search, and pick the suggestion
    unassign_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")

    # Step 3: the box holds the serial that was entered
    assert unassign_page.get_value("assetSerialId").startswith(serial)

    # Step 4: the asset is assigned, and the current assignee is shown
    assert unassign_page.get_value("assetName") == "Cabinet Table"
    assert unassign_page.get_value("previousAssignStatus") == "ASSIGNED"
    assert unassign_page.get_value("assignedEmployeePinNo") == ASSIGNEE_PIN
    assert unassign_page.get_value("assignedEmployeeName") == ASSIGNEE_NAME


@pytest.mark.regression
def test_unassign_search_by_options(page, unassign_page, take_screenshot):
    """Asset Un Assign: Search By offers Serial (the default) and Employee Pin."""
    # Step 1: open the screen
    unassign_page.navigate_here()
    take_screenshot("search by options")

    # Step 2: both choices are there and Serial is selected
    assert unassign_page.search_by_serial_radio.is_visible()
    assert unassign_page.search_by_employee_pin_radio.is_visible()
    assert unassign_page.search_by_serial_radio.is_checked()
    assert not unassign_page.search_by_employee_pin_radio.is_checked()


@pytest.mark.regression
def test_unassign_search_by_employee_pin_loads_assets(
    page, unassign_page, assigned_asset, take_screenshot
):
    """Asset Un Assign: searching by Employee Pin loads that employee's assigned assets."""
    # Step 1: switch Search By to Employee Pin
    unassign_page.navigate_here()
    unassign_page.choose_search_by_employee_pin()

    # Step 2: search the employee the asset is assigned to
    unassign_page.load_assets_of_employee(ASSIGNEE_PIN)
    take_screenshot("assets of the employee loaded")

    # Step 3: the Asset List holds the employee's assets, including the test asset
    assert assigned_asset["serial"] in unassign_page.get_asset_list_serials()


@pytest.mark.regression
def test_unassign_to_same_employee_is_refused(
    page, unassign_page, assigned_asset, take_screenshot
):
    """Asset Un Assign: the asset cannot be handed over to the employee who already holds it."""
    # Step 1: add the assigned asset
    unassign_page.navigate_here()
    unassign_page.select_asset_by_serial(assigned_asset["serial"])
    unassign_page.add_to_grid()

    # Step 2: pick the current holder as the hand-over employee and click Draft
    unassign_page.select_employee(ASSIGNEE_PIN)
    toast = unassign_page.draft_and_get_toast()
    take_screenshot("same employee refused")

    # Step 3: the screen refuses it and saves nothing
    assert toast == "Asset assigned to same employee!", f"Unexpected toast: '{toast}'"


@pytest.mark.smoke
@pytest.mark.regression
def test_unassign_full_flow_draft_submit_approve(
    page, unassign_page, transaction_list_page, transaction_approval_page,
    asset_serial_global_list_page, assigned_asset, take_screenshot
):
    """Asset Un Assign: Draft, Submit from the Transaction List, Approve, and the asset becomes UNASSIGNED."""
    serial = assigned_asset["serial"]

    # Step 1: fill the form (hand over to a different employee) and save it as a Draft
    unassign_page.navigate_here()
    unassign_page.select_asset_by_serial(serial)
    unassign_page.add_to_grid()
    unassign_page.select_employee(HANDOVER_SEARCH)
    assert unassign_page.get_employee_pin() == HANDOVER_PIN
    unassign_page.enter_note(NOTE)
    transaction_date = unassign_page.get_transaction_date().replace("-", "/")
    take_screenshot("unassign form filled")
    toast = unassign_page.draft_and_get_toast()
    take_screenshot("unassign draft saved")
    assert toast == "Asset Un-Assign Draft Successfully", f"Unexpected toast: '{toast}'"

    expected = {
        "employee_pin": HANDOVER_PIN,
        "employee_name": HANDOVER_NAME,
        "note": NOTE,
        "transaction_date": transaction_date,
    }

    # Step 2: Transaction List: check the Draft, open Edit, and Submit
    submit_draft_from_list(
        transaction_list_page, unassign_page, UNASSIGN, serial, expected,
        "Asset Un-Assign Submit Successfully", take_screenshot,
    )

    # Step 3: Transaction Approval List: check the popup, Approve, confirm APPROVED
    approve_and_verify(transaction_approval_page, UNASSIGN, serial, expected, take_screenshot)

    # Step 4: the asset is now UNASSIGNED
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("asset is unassigned")
    assert asset_serial_global_list_page.get_assign_status(serial) == "UNASSIGNED"
