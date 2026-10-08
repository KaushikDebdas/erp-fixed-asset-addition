"""
test_29_asset_write_off_approval_list.py: tests for the Asset Write-off
Approval List (Fixed Asset > Asset Disposal > Asset Write-off Approval List).

Built from automation/element_catalog/asset_write_off_approval_list.md. One user
(TEST_USERNAME, who needs the write-off approval permission). The write-off is the
one test_27 drafted and test_28 submitted (utils/write_off_flow.py); run alone, the
test makes the earlier stages first. The approved write-off uses its asset up.

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_29_asset_write_off_approval_list.py -k "approve"
"""
import pytest

from utils.run_context import trace_one_test

PENDING = "PENDING"
APPROVED = "APPROVED"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_write_off_approval_list_approve_pending_write_off(
    page, write_off, asset_write_off_approval_list_page, take_screenshot
):
    """Asset Write-off Approval List: a PENDING write-off is approved, which becomes APPROVED."""
    # Step 1: take the PENDING write-off (drafted and submitted by test_27 and test_28, or made now)
    write_off_id = write_off.reach("draft", "submitted")["write_off_id"]

    # Step 2: open the Approval List and find the PENDING write-off
    asset_write_off_approval_list_page.navigate_here()
    asset_write_off_approval_list_page.filter_by_status(PENDING)
    asset_write_off_approval_list_page.verify_status(write_off_id, PENDING)
    take_screenshot(f"write-off {write_off_id} is PENDING")

    # Step 3: tick it and click Approve
    asset_write_off_approval_list_page.select_write_off(write_off_id)
    asset_write_off_approval_list_page.approve_selected_and_verify()

    # Step 4: the write-off is APPROVED, and its asset is used up
    asset_write_off_approval_list_page.filter_by_status(APPROVED)
    asset_write_off_approval_list_page.verify_status(write_off_id, APPROVED)
    take_screenshot(f"write-off {write_off_id} is APPROVED")
    write_off.record("draft", "approved")
    write_off.use_up("draft")
