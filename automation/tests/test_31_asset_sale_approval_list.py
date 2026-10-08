"""
test_31_asset_sale_approval_list.py: tests for the Asset Sale Approval List
(Fixed Asset > Asset Disposal > Asset Sale Approval List).

Built from automation/element_catalog/asset_sale_approval_list.md. The test
makes its own PENDING sale first (the approved Furniture gift asset that test_01
creates is sold, see utils/sale_flow.py), then selects all pending sales and
approves them.

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_31_asset_sale_approval_list.py -k "approve"
"""
import pytest

from utils.run_context import trace_one_test
from utils.sale_flow import create_sale

PENDING = "PENDING"
APPROVED = "APPROVED"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_asset_sale_approval_list_approve_all_pending(
    page, registrations, asset_sale_page, asset_sale_list_page, asset_sale_approval_list_page, take_screenshot
):
    """Asset Sale Approval List: select all pending sales and approve them, they become APPROVED."""
    # Step 1: submit a sale and find its ID in the Asset Sale List
    create_sale(registrations, asset_sale_page, "furniture", "gift", 5000, "submit")
    asset_sale_list_page.navigate_here()
    asset_sale_list_page.filter_by_status(PENDING)
    sale_id = asset_sale_list_page.get_newest_write_off_id()

    # Step 2: open the Approval List, filter PENDING and check the sale is there
    asset_sale_approval_list_page.navigate_here()
    asset_sale_approval_list_page.filter_by_status(PENDING)
    asset_sale_approval_list_page.verify_status(sale_id, PENDING)
    take_screenshot(f"sale {sale_id} is PENDING")

    # Step 3: select all pending sales and click Approve
    asset_sale_approval_list_page.select_all_pending()
    asset_sale_approval_list_page.approve_selected_and_verify()

    # Step 4: the sale is APPROVED
    asset_sale_approval_list_page.filter_by_status(APPROVED)
    asset_sale_approval_list_page.verify_status(sale_id, APPROVED)
    take_screenshot(f"sale {sale_id} is APPROVED")
