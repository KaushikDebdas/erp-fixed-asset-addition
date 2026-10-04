"""
test_15_asset_assign_acknowledgement.py: tests for the Asset Assign
Acknowledgement screen (Fixed Asset > Asset Transaction > Asset Assign
Acknowledgement).

Built from automation/element_catalog/asset_assign_acknowledgement.md.

Two logins are involved:
    - the main user (TEST_USERNAME) registers an asset, assigns it to the test
      employee and approves the assignment. The `assigned_asset` fixture in
      conftest.py does this.
    - the ASSIGNED employee (ASSGN_USER_USERNAME / ASSIGN_USER_PASSWROD in
      .env) opens the Asset Assign Acknowledgement screen in a second browser
      tab (the `assignee_logged_in_page` fixture) and acknowledges it.

The assigned employee's pending list can hold other people's assignments as
well, so the test finds its own row by the serial inside the Details popup
and acknowledges only that row. The full-flow test is the last test of the
file, because acknowledging uses up the pending assignment.
"""
import pytest

from test_data.asset_transaction_data import (
    ACKNOWLEDGE_TOAST,
    ASSIGN,
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    SETUP_ASSIGN_NOTE,
)


@pytest.mark.smoke
@pytest.mark.regression
def test_acknowledgement_screen_layout(acknowledgement_page, assignee_screenshot):
    """Asset Assign Acknowledgement: the screen shows the pending grid, My Assigned Asset and the Acknowledge button."""
    # Step 1: the assigned employee opens Asset Assign Acknowledgement
    acknowledgement_page.navigate_here()
    assignee_screenshot("asset assign acknowledgement opened")

    # Step 2: the Pending Asset Acknowledgement grid has its documented columns
    assert acknowledgement_page.get_pending_headers() == [
        "SL",
        "Transaction Type",
        "Project",
        "Branch",
        "Assigned Employee",
        "Assigned By",
        "Approval Date",
        "Details",
    ]

    # Step 3: the My Assigned Asset grid has its documented columns
    assert acknowledgement_page.get_my_assets_headers() == [
        "SL",
        "Asset Serial",
        "Asset Item Name",
        "Branch Name",
        "Project Name",
        "Building Name",
        "Floor Name",
        "Room Name",
        "Assigned Employee",
        "Assigned By",
        "Utilization Status",
    ]

    # Step 4: the Acknowledge button is on the screen
    assert acknowledgement_page.page_acknowledge_button.is_visible()


@pytest.mark.regression
def test_pending_rows_belong_to_the_logged_in_employee(
    acknowledgement_page, assigned_asset, assignee_screenshot
):
    """Asset Assign Acknowledgement: every pending row is an assignment to the employee who is logged in."""
    # Step 1: open the screen (the fixture has just assigned an asset to this employee)
    acknowledgement_page.navigate_here()
    assignee_screenshot("pending assignments")
    assert acknowledgement_page.get_pending_count() > 0

    # Step 2: every pending row names this employee as the Assigned Employee
    for assigned_employee in acknowledgement_page.get_pending_assigned_employees():
        assert f"[{ASSIGNEE_PIN}]" in assigned_employee, (
            f"A pending row belongs to '{assigned_employee}', not to employee {ASSIGNEE_PIN}."
        )


@pytest.mark.regression
def test_details_popup_shows_the_assignment(
    acknowledgement_page, assigned_asset, assignee_screenshot
):
    """Asset Assign Acknowledgement: Details shows the approved assignment and the assigned asset's serial."""
    serial = assigned_asset["serial"]

    # Step 1: open the screen and find the row that holds the test asset
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(serial)
    assignee_screenshot(f"details of the assignment of {serial}")

    # Step 2: the popup shows the approved ASSIGN transaction for this employee
    popup = acknowledgement_page
    assert popup.get_popup_value("assetTransactionType") == ASSIGN
    assert popup.get_popup_value("assignedEmployeePinNo") == ASSIGNEE_PIN
    assert popup.get_popup_value("assignedEmployee") == ASSIGNEE_NAME
    assert popup.get_popup_value("oldTransactionStatus") == "APPROVED"
    assert popup.get_popup_value("remarks") == SETUP_ASSIGN_NOTE
    assert popup.get_popup_asset_serials() == [serial]

    # Step 3: close without acknowledging; the assignment is still pending
    popup.close_popup()


@pytest.mark.smoke
@pytest.mark.regression
def test_acknowledge_assigned_asset(acknowledgement_page, assigned_asset, assignee_screenshot):
    """
    Asset Assign Acknowledgement: the assigned employee opens Details, verifies the
    Asset Serial Number, clicks Acknowledge, and the asset moves to My Assigned Asset.
    """
    serial = assigned_asset["serial"]

    # Step 1: the assigned employee opens Asset Assign Acknowledgement
    acknowledgement_page.navigate_here()
    pending_before = acknowledgement_page.get_pending_count()
    assert serial not in acknowledgement_page.get_my_assigned_serials(), (
        "The asset should not be in My Assigned Asset before it is acknowledged."
    )
    assignee_screenshot("before acknowledging")

    # Step 2: open Details on the assignment and verify the Asset Serial Number
    acknowledgement_page.open_details_of_row_with_serial(serial)
    assignee_screenshot(f"details of the assignment of {serial}")
    assert acknowledgement_page.get_popup_asset_serials() == [serial], (
        f"Expected the assignment to list asset {serial}."
    )
    assert acknowledgement_page.get_popup_value("assignedEmployeePinNo") == ASSIGNEE_PIN

    # Step 3: click Acknowledge; the success message must be shown
    toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
    assignee_screenshot("acknowledged")
    assert toast == ACKNOWLEDGE_TOAST, f"Expected '{ACKNOWLEDGE_TOAST}' but found '{toast}'."

    # Step 4: the assignment left the pending list
    assert acknowledgement_page.get_pending_count() == pending_before - 1

    # Step 5: the asset now shows in My Assigned Asset, assigned to this employee
    assert serial in acknowledgement_page.get_my_assigned_serials()
    assert f"[{ASSIGNEE_PIN}]" in acknowledgement_page.get_my_assigned_row_text(serial)
