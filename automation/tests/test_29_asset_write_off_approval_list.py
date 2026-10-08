"""
test_29_asset_write_off_approval_list.py: tests for the Asset Write-off
Approval List (Fixed Asset > Asset Disposal > Asset Write-off Approval List).

Built from automation/element_catalog/asset_write_off_approval_list.md. One user
(TEST_USERNAME, who needs the write-off approval permission): writes off a new
DAMAGED asset as Draft, submits it from the Write-off List, then approves it
from the Approval List.

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_29_asset_write_off_approval_list.py -k "approve"
"""
import pytest

from utils.run_context import trace_one_test
from utils.write_off_flow import create_write_off

DRAFT = "DRAFT"
PENDING = "PENDING"
APPROVED = "APPROVED"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_write_off_approval_list_approve_pending_write_off(
    page, registrations, asset_serial_global_list_page, asset_write_off_page, asset_write_off_list_page,
    asset_write_off_approval_list_page, take_screenshot
):
    """Asset Write-off Approval List: a PENDING write-off is approved, which becomes APPROVED."""
    # Step 1: save a write-off for a new DAMAGED asset as Draft
    create_write_off(registrations, asset_serial_global_list_page, asset_write_off_page, "write_off_approval", "draft")

    # Step 2: submit the newest Draft from the Write-off List
    asset_write_off_list_page.navigate_here()
    asset_write_off_list_page.filter_by_status(DRAFT)
    write_off_id = asset_write_off_list_page.get_newest_write_off_id()
    asset_write_off_list_page.open_write_off_for_edit(write_off_id)
    asset_write_off_page.submit_and_verify()
    take_screenshot(f"write-off {write_off_id} submitted")

    # Step 3: open the Approval List and find the PENDING write-off
    asset_write_off_approval_list_page.navigate_here()
    asset_write_off_approval_list_page.filter_by_status(PENDING)
    asset_write_off_approval_list_page.verify_status(write_off_id, PENDING)
    take_screenshot(f"write-off {write_off_id} is PENDING")

    # Step 4: tick it and click Approve
    asset_write_off_approval_list_page.select_write_off(write_off_id)
    asset_write_off_approval_list_page.approve_selected_and_verify()

    # Step 5: the write-off is APPROVED
    asset_write_off_approval_list_page.filter_by_status(APPROVED)
    asset_write_off_approval_list_page.verify_status(write_off_id, APPROVED)
    take_screenshot(f"write-off {write_off_id} is APPROVED")
