"""
test_15_asset_assign_acknowledgement.py: tests for the Asset Assign
Acknowledgement screen (Fixed Asset > Asset Transaction > Asset Assign
Acknowledgement).

Built from automation/element_catalog/asset_assign_acknowledgement.md. The asset
is NOT created here: it is the saved Furniture asset, read with
registrations.get_approved("furniture", "spot", AAQ_ASSET_GROUP)
(test_data/saved_assets.json). Its saved record is never changed.

Two logins are involved:
    - the main user (TEST_USERNAME) assigns the asset to the test employee and
      approves the assignment, only when no acknowledgement is waiting yet
      (`transactions.ensure_acknowledgement_pending(...)`, utils/transaction_helper.py).
      This file's `page` is the main user's tab.
    - the ASSIGNED employee (ASSIGN_USER_USERNAME / ASSIGN_USER_PASSWORD in .env)
      works in a second browser tab (the `assignee_logged_in_page` fixture),
      opens the Asset Assign Acknowledgement screen and acknowledges it.

The assigned employee's pending list can hold other people's assignments as well,
so the test finds its own row by the serial inside the Details popup and
acknowledges only that row. Acknowledging does not change the asset: the last
test reads its real Assign Status afterwards and it is still ASSIGNED.

The tests run top to bottom:
    1. The screen: columns and the Acknowledge button
    2. The pending rows and the Details popup
    3. LAST: acknowledge (this uses up the waiting acknowledgement)

To run part of the file:
    pytest tests/test_15_asset_assign_acknowledgement.py -k "details"
"""
import pytest

from test_data.asset_transaction_data import (
    ASSIGNED,
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    NOTE_PREFIX,
)
from test_data.toast_messages import (
    ACKNOWLEDGE_TOAST,
)
from utils.run_context import trace_one_test

# Column headings of the Pending Asset Acknowledgement grid
PENDING_COLUMNS = [
    "SL", "Transaction Type", "Project", "Branch", "Assigned Employee",
    "Assigned By", "Approval Date", "Details",
]

# Column headings of the My Assigned Asset grid
MY_ASSET_COLUMNS = [
    "SL", "Asset Serial", "Asset Item Name", "Branch Name", "Project Name", "Building Name",
    "Floor Name", "Room Name", "Assigned Employee", "Assigned By", "Utilization Status",
]


@pytest.fixture
def page(logged_in_page, request):
    """The main user's tab, logged in once; it makes the assignment this file acknowledges."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The screen
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_acknowledgement_screen_layout(acknowledgement_page, assignee_screenshot):
    """Asset Assign Acknowledgement: the screen shows the pending grid, My Assigned Asset and the Acknowledge button."""
    # Step 1: the assigned employee opens Asset Assign Acknowledgement
    acknowledgement_page.navigate_here()
    assignee_screenshot("asset assign acknowledgement opened")

    # Step 2: both grids have their documented columns
    acknowledgement_page.verify_pending_headers(PENDING_COLUMNS)
    acknowledgement_page.verify_my_assets_headers(MY_ASSET_COLUMNS)

    # Step 3: the Acknowledge button is on the screen
    acknowledgement_page.verify_acknowledge_button_shown()


# ---------------------------------------------------------------------------
# 2. The pending rows and the Details popup
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_pending_rows_belong_to_the_logged_in_employee(
    page, acknowledgement_page, transactions, assignee_screenshot
):
    """Asset Assign Acknowledgement: every pending row is an assignment to the employee who is logged in."""
    # Step 1: make sure an acknowledgement of the saved asset is waiting
    transactions.ensure_acknowledgement_pending(acknowledgement_page)

    # Step 2: open the screen as the assigned employee
    acknowledgement_page.navigate_here()
    assignee_screenshot("pending assignments")

    # Step 3: there are pending rows and every one names this employee
    acknowledgement_page.verify_pending_rows_belong_to(ASSIGNEE_PIN)


@pytest.mark.regression
def test_details_popup_shows_the_assignment(page, acknowledgement_page, transactions, assignee_screenshot):
    """Asset Assign Acknowledgement: Details shows the approved assignment and the assigned asset's serial."""
    # Step 1: make sure an acknowledgement of the saved asset is waiting
    serial = transactions.ensure_acknowledgement_pending(acknowledgement_page)

    # Step 2: open the screen and the Details of the row that holds the saved asset
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(serial)
    assignee_screenshot(f"details of the assignment of {serial}")

    # Step 3: the popup shows the approved ASSIGN transaction of this asset for this employee
    acknowledgement_page.verify_popup_shows_assignment(serial, ASSIGNEE_PIN, ASSIGNEE_NAME, NOTE_PREFIX)

    # Step 4: close without acknowledging
    acknowledgement_page.close_popup()


# ---------------------------------------------------------------------------
# 3. LAST: acknowledge (uses up the waiting acknowledgement)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_acknowledge_assigned_asset(
    page, acknowledgement_page, asset_serial_global_list_page, transactions,
    take_screenshot, assignee_screenshot
):
    """Asset Assign Acknowledgement: the employee opens Details, verifies the serial, clicks Acknowledge, and the asset moves to My Assigned Asset."""
    # Step 1: make sure an acknowledgement of the saved asset is waiting, then open the screen
    serial = transactions.ensure_acknowledgement_pending(acknowledgement_page)
    acknowledgement_page.navigate_here()
    pending_before = acknowledgement_page.get_pending_count()
    assignee_screenshot("before acknowledging")

    # Step 2: open Details on the assignment and verify the Asset Serial Number
    acknowledgement_page.open_details_of_row_with_serial(serial)
    assignee_screenshot(f"details of the assignment of {serial}")
    acknowledgement_page.verify_popup_shows_assignment(serial, ASSIGNEE_PIN, ASSIGNEE_NAME, NOTE_PREFIX)

    # Step 3: click Acknowledge; the success message must be shown
    toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
    assignee_screenshot("acknowledged")
    acknowledgement_page.verify_toast_text(toast, ACKNOWLEDGE_TOAST, "Acknowledge")

    # Step 4: one pending row less, and the asset is in My Assigned Asset
    acknowledgement_page.verify_acknowledged(serial, pending_before, ASSIGNEE_PIN)

    # Step 5: the asset's real status is unchanged: still ASSIGNED
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("asset still assigned")
    asset_serial_global_list_page.verify_assign_status(serial, ASSIGNED)
