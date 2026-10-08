"""
test_27_asset_write_off.py: tests for the Asset Write-off screen (Fixed Asset >
Asset Disposal > Asset Write-off): Create as Submit and Create as Draft.

Built from automation/element_catalog/asset_write_off.md. A write-off only
accepts an asset whose Utilization Status is not IN_USE, so each test registers
and approves its own new Furniture asset (like test_01), sets it to DAMAGE and
writes it off (see utils/write_off_flow.py). A written-off asset cannot be used
again, so every test has its own asset.

The whole file logs in once and every test reuses that session.

The tests run top to bottom:
    1. Create a write-off and Submit it
    2. Create a write-off and save it as Draft

To run part of the file:
    pytest tests/test_27_asset_write_off.py -k "draft"
"""
import pytest

from utils.run_context import trace_one_test
from utils.write_off_flow import create_write_off


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_write_off_create_and_submit(
    page, registrations, asset_serial_global_list_page, asset_write_off_page, take_screenshot
):
    """Asset Write-off: create a write-off for a DAMAGED asset and Submit it."""
    # Step 1: write off a new DAMAGED asset and Submit it
    asset = create_write_off(
        registrations, asset_serial_global_list_page, asset_write_off_page, "write_off_submit", "submit"
    )
    take_screenshot(f"asset {asset['serial']} written off (submitted)")

    # Step 2: the grid is empty again after the save
    asset_write_off_page.verify_grid_is_empty()


@pytest.mark.regression
def test_write_off_create_and_draft(
    page, registrations, asset_serial_global_list_page, asset_write_off_page, take_screenshot
):
    """Asset Write-off: create a write-off for a DAMAGED asset and save it as Draft."""
    # Step 1: write off a new DAMAGED asset and save it as Draft
    asset = create_write_off(
        registrations, asset_serial_global_list_page, asset_write_off_page, "write_off_draft", "draft"
    )
    take_screenshot(f"asset {asset['serial']} written off (draft)")

    # Step 2: the grid is empty again after the save
    asset_write_off_page.verify_grid_is_empty()
