"""
test_27_asset_write_off.py: tests for the Asset Write-off screen (Fixed Asset >
Asset Disposal > Asset Write-off): Create as Draft and Create as Submit.

Built from automation/element_catalog/asset_write_off.md. A write-off only
accepts an asset whose Utilization Status is not IN_USE, so each path sets its asset
to DAMAGE and writes it off (see utils/write_off_flow.py). The assets come from the
asset pool (test_data/asset_slots.py): the usage assets that the Assign, Movement,
Unassign and Expense files used, when they are free, otherwise new ones. A written-off
asset cannot be used again, so each path has its own asset.

The whole file logs in once and every test reuses that session.

The tests run top to bottom:
    1. The Draft path (write_off_a): Draft; it is DRAFT in the Write-off List
       (test_28 submits it and test_29 approves it)
    2. The Submit-only path (write_off_b): Submit; it is PENDING in the Write-off List

To run part of the file:
    pytest tests/test_27_asset_write_off.py -k "draft"
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.regression
def test_write_off_create_and_draft(
    page, write_off, asset_write_off_page, asset_write_off_list_page, take_screenshot
):
    """Asset Write-off: write off a DAMAGED asset and save it as Draft; it is listed as DRAFT with an Edit link."""
    # Step 1: write off the asset of the Draft path and save it as Draft
    flow = write_off.reach("draft", "drafted")
    take_screenshot(f"asset {flow['serial']} written off (draft)")

    # Step 2: the Write-off List shows the write-off as DRAFT with an Edit link
    asset_write_off_list_page.navigate_here()
    asset_write_off_list_page.filter_by_status("DRAFT")
    asset_write_off_list_page.verify_status(flow["write_off_id"], "DRAFT")


@pytest.mark.smoke
@pytest.mark.regression
def test_write_off_create_and_submit(
    page, write_off, asset_write_off_page, asset_write_off_list_page, take_screenshot
):
    """Asset Write-off: write off a DAMAGED asset and Submit it straight from the form; it is listed as PENDING."""
    # Step 1: write off the asset of the Submit-only path and Submit it
    flow = write_off.reach("submit", "submitted")
    take_screenshot(f"asset {flow['serial']} written off (submitted)")

    # Step 2: the Write-off List shows the write-off as PENDING
    asset_write_off_list_page.navigate_here()
    asset_write_off_list_page.filter_by_status("PENDING")
    asset_write_off_list_page.verify_status(flow["write_off_id"], "PENDING")
