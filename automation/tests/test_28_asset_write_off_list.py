"""
test_28_asset_write_off_list.py: tests for the Asset Write-off List screen
(Fixed Asset > Asset Disposal > Asset Write-off List).

Built from automation/element_catalog/asset_write_off_list.md. The test makes
its own Draft write-off first (a new approved asset is set to DAMAGE and written
off as Draft, see utils/write_off_flow.py), because a written-off asset cannot
be used again.

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_28_asset_write_off_list.py -k "submit"
"""
import pytest

from utils.run_context import trace_one_test
from utils.write_off_flow import WRITE_OFF_NOTE, create_write_off

DRAFT = "DRAFT"
PENDING = "PENDING"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_write_off_list_submit_drafted_write_off(
    page, registrations, asset_serial_global_list_page, asset_write_off_page, asset_write_off_list_page, take_screenshot
):
    """Asset Write-off List: a Draft write-off is opened with Edit and Submitted, then it is PENDING."""
    # Step 1: save a write-off for a new DAMAGED asset as Draft
    asset = create_write_off(
        registrations, asset_serial_global_list_page, asset_write_off_page, "write_off_list", "draft"
    )

    # Step 2: open the list, filter DRAFT and take the newest write-off
    asset_write_off_list_page.navigate_here()
    asset_write_off_list_page.filter_by_status(DRAFT)
    write_off_id = asset_write_off_list_page.get_newest_write_off_id()
    asset_write_off_list_page.verify_status(write_off_id, DRAFT)
    take_screenshot(f"write-off {write_off_id} is DRAFT")

    # Step 3: click Edit, the form shows the drafted asset in the grid
    asset_write_off_list_page.open_write_off_for_edit(write_off_id)
    asset_write_off_page.verify_grid_row(asset["serial"], asset["item_name"], "DAMAGE", WRITE_OFF_NOTE)
    take_screenshot("draft opened for edit")

    # Step 4: Submit, the success message shows and the grid is empty again
    asset_write_off_page.submit_and_verify()
    asset_write_off_page.verify_grid_is_empty()

    # Step 5: the list now shows the write-off as PENDING
    asset_write_off_list_page.navigate_here()
    asset_write_off_list_page.filter_by_status(PENDING)
    asset_write_off_list_page.verify_status(write_off_id, PENDING)
    take_screenshot(f"write-off {write_off_id} is PENDING")
