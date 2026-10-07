"""
test_09_asset_serial_split_approval_list_new.py: tests for the Asset Serial Split
Approval List screen (Fixed Asset > Asset Profile > Asset Serial Split Approval
List) and its Asset Split View popup.

Built from automation/element_catalog/asset_serial_split_approval_list.md. The
split that is approved is the one of the saved Land asset:
splits.get_pending_split() returns the one test_07_asset_serial_split_new.py
submitted, or splits the saved Land asset now when the test runs on its own
(see utils/split_helper.py). The whole file logs in once and every test reuses
that session.

The tests run top to bottom:
    1. The grid: columns
    2. The PENDING split of the Land asset: its row and its Asset Split View popup
    3. Approve and Reject with nothing ticked
    4. LAST: the pending split is approved (this makes the new asset serials)

The last test must stay last in the file: approving cannot be undone, and it
moves the split record to APPROVED and saves the new Asset Serials. Reject is
never clicked.

To run part of the file:
    pytest tests/test_09_asset_serial_split_approval_list_new.py -k "nothing_ticked"
"""
import pytest

from test_data.asset_split_data import (
    CREATED_BY_NAME,
    LAND_ACC_DEPRECIATION_TEXT,
    LAND_ITEM_NAME,
    LAND_MEASUREMENT_TEXT,
    LAND_VALUE_TEXT,
    SPLIT_GRID_COLUMNS,
    SPLIT_INTO,
)
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The grid
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_split_approval_list_grid_columns(page, asset_split_approval_list_page, take_screenshot):
    """Asset Serial Split Approval List: the grid shows the documented columns."""
    # Step 1: open the Asset Serial Split Approval List and search
    asset_split_approval_list_page.navigate_here()
    asset_split_approval_list_page.search()
    take_screenshot("asset serial split approval list opened")

    # Step 2: the column headings
    asset_split_approval_list_page.verify_grid_headers(SPLIT_GRID_COLUMNS)


# ---------------------------------------------------------------------------
# 2. The PENDING split of the Land asset
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_split_approval_list_shows_the_pending_split(
    page, asset_split_approval_list_page, splits, take_screenshot
):
    """Asset Serial Split Approval List: the pending split of the Land asset is listed, waiting for approval."""
    # Step 1: get the split that is waiting for approval
    split = splits.get_pending_split()

    # Step 2: open the list and search the serial
    asset_split_approval_list_page.navigate_here()
    asset_split_approval_list_page.search_by_serial(split["serial"])
    take_screenshot(f"split of {split['serial']} found")

    # Step 3: the row shows the split as PENDING, with no approver yet
    asset_split_approval_list_page.verify_row_shows(split["serial"], {
        "Asset Split No.": split["split_no"],
        "Asset Group": LAND_ITEM_NAME,
        "Split Into": SPLIT_INTO,
        "Created By": CREATED_BY_NAME,
        "Status": "PENDING",
        "Approved By": "",
        "Approval Date": "",
    })


@pytest.mark.regression
def test_split_approval_list_view_popup(page, asset_split_approval_list_page, splits, take_screenshot):
    """Asset Serial Split Approval List: the Asset Split View popup shows the asset, its WDV and its 2 split lines."""
    # Step 1: get the pending split and find its row
    split = splits.get_pending_split()
    asset_split_approval_list_page.navigate_here()
    asset_split_approval_list_page.search_by_serial(split["serial"])

    # Step 2: click the Asset Split No.
    asset_split_approval_list_page.open_split_view(split["serial"])
    take_screenshot("asset split view popup opened")

    # Step 3: the popup shows the serial, Split Into, written down value and 2 split lines
    asset_split_approval_list_page.verify_popup_shows({
        "assetSerial": split["serial"],
        "splitInto": SPLIT_INTO,
        "measurement": LAND_MEASUREMENT_TEXT,
        "netAssetValue": LAND_VALUE_TEXT,
        "accumulatedDepriciation": LAND_ACC_DEPRECIATION_TEXT,
    }, int(SPLIT_INTO))

    # Step 4: close the popup
    asset_split_approval_list_page.close_split_view()


# ---------------------------------------------------------------------------
# 3. Approve and Reject with nothing ticked
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.parametrize("button_name", ["Approve", "Reject"])
def test_split_approval_list_nothing_ticked(button_name, page, asset_split_approval_list_page, take_screenshot):
    """Asset Serial Split Approval List: Approve or Reject with no row ticked asks to select a split."""
    # Step 1: open the list
    asset_split_approval_list_page.navigate_here()
    take_screenshot("asset serial split approval list opened")

    # Step 2: click the button with nothing ticked; the message asks to select a split
    asset_split_approval_list_page.verify_nothing_ticked_message(button_name)
    take_screenshot(f"{button_name} with nothing ticked")


# ---------------------------------------------------------------------------
# 4. LAST: approve the pending split (cannot be undone)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_approve_split_makes_new_serials(
    page, asset_split_approval_list_page, asset_serial_global_list_page, asset_serial_split_page,
    splits, take_screenshot
):
    """Asset Serial Split Approval List: approving the split makes the new serials and removes the original."""
    # Step 1: get the pending split, open the list and search its serial
    split = splits.get_pending_split()
    asset_split_approval_list_page.navigate_here()
    asset_split_approval_list_page.search_by_serial(split["serial"])

    # Step 2: tick the row and click Approve (Reject is never clicked)
    asset_split_approval_list_page.tick_row(split["serial"])
    take_screenshot("split row ticked")
    toast = asset_split_approval_list_page.click_approve_and_get_toast()
    asset_split_approval_list_page.verify_approve_message(toast)

    # Step 3: the row shows APPROVED, the approver and the approval date
    asset_split_approval_list_page.wait_for_status(split["serial"], "APPROVED")
    take_screenshot("split approved")
    asset_split_approval_list_page.verify_row_is_approved(split["serial"], CREATED_BY_NAME)

    # Step 4: read the new serials and save them in the split record
    approved = splits.remember_approved_split(split)

    # Step 5: each new serial is on the Global List, UNASSIGNED and IN_USE
    asset_serial_global_list_page.navigate_here()
    for new_serial in approved["new_serials"]:
        asset_serial_global_list_page.search_by_serial(new_serial)
        asset_serial_global_list_page.verify_statuses(new_serial, "UNASSIGNED", "IN_USE")
    take_screenshot("new serials on the global list")

    # Step 6: the original serial is gone from the Global List and from the Split screen
    asset_serial_global_list_page.search_by_serial(split["serial"])
    asset_serial_global_list_page.verify_serial_not_listed(split["serial"])
    asset_serial_split_page.navigate_here()
    asset_serial_split_page.search_by_serial(split["serial"])
    asset_serial_split_page.verify_serial_not_listed(split["serial"])
