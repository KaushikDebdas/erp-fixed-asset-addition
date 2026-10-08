"""
test_28_asset_write_off_list.py: tests for the Asset Write-off List screen
(Fixed Asset > Asset Disposal > Asset Write-off List).

Built from automation/element_catalog/asset_write_off_list.md. The write-off is the
Draft of test_27 (utils/write_off_flow.py): the Draft path of the Write-off flow; run
alone, the test makes its own Draft first (a DAMAGED asset written off as Draft).

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_28_asset_write_off_list.py -k "submit"
"""
import pytest

from utils.run_context import trace_one_test
from utils.write_off_flow import ITEM_NAME, WRITE_OFF_NOTE

DRAFT = "DRAFT"
PENDING = "PENDING"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_write_off_list_submit_drafted_write_off(
    page, write_off, asset_write_off_page, asset_write_off_list_page, take_screenshot
):
    """Asset Write-off List: a Draft write-off is opened with Edit and Submitted, then it is PENDING."""
    # Step 1: take the Draft write-off (made by test_27, or made now)
    flow = write_off.reach("draft", "drafted")
    write_off_id = flow["write_off_id"]

    # Step 2: open the list, filter DRAFT; the row is a Draft with an Edit link
    asset_write_off_list_page.navigate_here()
    asset_write_off_list_page.filter_by_status(DRAFT)
    asset_write_off_list_page.verify_status(write_off_id, DRAFT)
    take_screenshot(f"write-off {write_off_id} is DRAFT")

    # Step 3: click Edit, the form shows the drafted asset in the grid
    asset_write_off_list_page.open_write_off_for_edit(write_off_id)
    asset_write_off_page.verify_grid_row(flow["serial"], ITEM_NAME, "DAMAGE", WRITE_OFF_NOTE)
    take_screenshot("draft opened for edit")

    # Step 4: Submit, the success message shows and the grid is empty again
    asset_write_off_page.submit_and_verify()
    asset_write_off_page.verify_grid_is_empty()
    write_off.record("draft", "submitted")

    # Step 5: the list now shows the write-off as PENDING
    asset_write_off_list_page.navigate_here()
    asset_write_off_list_page.filter_by_status(PENDING)
    asset_write_off_list_page.verify_status(write_off_id, PENDING)
    take_screenshot(f"write-off {write_off_id} is PENDING")
