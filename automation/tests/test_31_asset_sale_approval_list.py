"""
test_31_asset_sale_approval_list.py: tests for the Asset Sale List and the Asset Sale
Approval List (Fixed Asset > Asset Disposal): the two Draft sales are submitted from
the list, then all pending sales are selected and approved.

Built from automation/element_catalog/asset_sale_list.md and
asset_sale_approval_list.md. The four sales are the ones test_30 made (utils/sale_flow.py):
profit and loss, each saved with Draft and with Submit. Run alone, the test makes them
first. The approved sales use their assets up.

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_31_asset_sale_approval_list.py -k "approve"
"""
import pytest

from utils.run_context import trace_one_test

PENDING = "PENDING"
APPROVED = "APPROVED"

# The four sale paths of utils/sale_flow.py
SALE_PATHS = ["profit_a", "profit_b", "loss_a", "loss_b"]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_asset_sale_approval_list_approve_all_pending(
    page, sale, asset_sale_list_page, asset_sale_approval_list_page, take_screenshot
):
    """Asset Sale List and Approval List: the Draft sales are submitted from the list, and select all pending approves the four sales."""
    # Step 1: bring the four sales to PENDING (the Drafts are opened with Edit from the Asset Sale List and submitted)
    sale_ids = []
    for path in SALE_PATHS:
        sale_ids.append(sale.reach(path, "submitted")["sale_id"])
    take_screenshot("the four sales are submitted")

    # Step 2: open the Approval List, filter PENDING and check the four sales are there
    asset_sale_approval_list_page.navigate_here()
    asset_sale_approval_list_page.filter_by_status(PENDING)
    for sale_id in sale_ids:
        asset_sale_approval_list_page.verify_status(sale_id, PENDING)

    # Step 3: select all pending sales and click Approve
    asset_sale_approval_list_page.select_all_pending()
    asset_sale_approval_list_page.approve_selected_and_verify()

    # Step 4: the four sales are APPROVED, and their assets are used up
    asset_sale_approval_list_page.filter_by_status(APPROVED)
    for sale_id in sale_ids:
        asset_sale_approval_list_page.verify_status(sale_id, APPROVED)
    take_screenshot("the four sales are approved")
    for path in SALE_PATHS:
        sale.record(path, "approved")
        sale.use_up(path)
