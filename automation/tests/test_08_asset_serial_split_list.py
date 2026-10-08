"""
test_08_asset_serial_split_list.py: tests for the Asset Serial Split List
screen (Fixed Asset > Asset Profile > Asset Serial Split List).

Built from automation/element_catalog/asset_serial_split_list.md. The split
that is listed is the one of the saved Land asset, waiting for approval:
splits.get_pending_split() returns the one test_07_asset_serial_split.py
submitted, or splits the saved Land asset now when the test runs on its own
(see utils/split_helper.py). The tests only read the list and open its popup;
they change nothing. The whole file logs in once and every test reuses that
session.

The tests run top to bottom:
    1. The grid: columns, an unknown serial
    2. The PENDING split of the Land asset: its row and its Asset Split View popup
    3. The filters: Created By, Reset, Records per page

To run part of the file:
    pytest tests/test_08_asset_serial_split_list.py -k "created_by"
"""
import pytest

from test_data.asset_split_data import (
    LAND_ACC_DEPRECIATION_TEXT,
    LAND_ITEM_NAME,
    LAND_MEASUREMENT_TEXT,
    LAND_VALUE_TEXT,
    SPLIT_GRID_COLUMNS,
    SPLIT_INTO,
    SPLIT_REMARKS,
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
def test_split_list_grid_columns(page, asset_split_list_page, take_screenshot):
    """Asset Serial Split List: the grid shows the documented columns."""
    # Step 1: open the Asset Serial Split List
    asset_split_list_page.navigate_here()
    take_screenshot("asset serial split list opened")

    # Step 2: the column headings
    asset_split_list_page.verify_grid_headers(SPLIT_GRID_COLUMNS)


@pytest.mark.regression
def test_split_list_unknown_serial_shows_no_data(page, asset_split_list_page, take_screenshot):
    """Asset Serial Split List: an Asset Serial that was never split shows the empty message."""
    # Step 1: open the list and search a serial that cannot exist
    asset_split_list_page.navigate_here()
    asset_split_list_page.search_by_serial("NOSUCHSERIAL000")
    take_screenshot("no data for unknown serial")

    # Step 2: the grid shows the empty message
    asset_split_list_page.verify_grid_is_empty("serial NOSUCHSERIAL000")


# ---------------------------------------------------------------------------
# 2. The PENDING split of the Land asset
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_split_list_shows_the_pending_split(page, asset_split_list_page, splits, current_user, take_screenshot):
    """Asset Serial Split List: searching the split Land asset's serial lists its PENDING split."""
    # Step 1: get the split that is waiting for approval
    split = splits.get_pending_split()

    # Step 2: open the list and search the serial
    asset_split_list_page.navigate_here()
    asset_split_list_page.search_by_serial(split["serial"])
    take_screenshot(f"split of {split['serial']} found")

    # Step 3: the row shows the split, who made it, and no approver yet
    asset_split_list_page.verify_row_shows(split["serial"], {
        "Asset Split No.": split["split_no"],
        "Asset Group": LAND_ITEM_NAME,
        "Asset Serial No.": split["serial"],
        "Split Into": SPLIT_INTO,
        "Remarks": SPLIT_REMARKS,
        "Created By": current_user["name"],
        "Status": "PENDING",
        "Approved By": "",
        "Approval Date": "",
    })


@pytest.mark.regression
def test_split_number_opens_the_split_view_popup(page, asset_split_list_page, splits, take_screenshot):
    """Asset Serial Split List: the Asset Split No. opens the Asset Split View popup with the split's details."""
    # Step 1: get the pending split and find its row
    split = splits.get_pending_split()
    asset_split_list_page.navigate_here()
    asset_split_list_page.search_by_serial(split["serial"])

    # Step 2: click the Asset Split No.
    asset_split_list_page.open_split_view(split["serial"])
    take_screenshot("asset split view popup opened")

    # Step 3: the popup shows the asset and its 2 split lines
    asset_split_list_page.verify_popup_shows({
        "assetSerial": split["serial"],
        "assetName": LAND_ITEM_NAME,
        "splitInto": SPLIT_INTO,
        "measurement": LAND_MEASUREMENT_TEXT,
        "netAssetValue": LAND_VALUE_TEXT,
        "accumulatedDepriciation": LAND_ACC_DEPRECIATION_TEXT,
        "remarks": SPLIT_REMARKS,
    }, int(SPLIT_INTO))

    # Step 4: close the popup
    asset_split_list_page.close_popup()
