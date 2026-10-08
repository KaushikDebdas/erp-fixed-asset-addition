"""
test_30_asset_sale.py: tests for the Asset Sale screen (Fixed Asset > Asset
Disposal > Asset Sale): Create with Submit and with Draft, selling above and
below the Written Down Value.

Built from automation/element_catalog/asset_sale.md. The assets sold are four of the
asset pool (test_data/asset_slots.py, utils/sale_flow.py): UNASSIGNED and IN_USE, which
the sale screen accepts as they are. Each path has its own asset (a sold asset cannot
be sold again), and the pool registers one when the test runs alone.

The cases (Sale Value compared with the Written Down Value, shown in the grid
as Profit/Loss):
    profit: Sale Value above it (+5000, a profit)     loss: Sale Value below it (-5000, a loss)
each saved with Submit and with Draft. The two Drafts are submitted from the Asset Sale
List in test_31, and all four sales are approved there.

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_30_asset_sale.py -k "loss"
"""
import pytest

from utils.run_context import trace_one_test

# Status the sale list must show after the save
LIST_STATUS = {"profit_a": "DRAFT", "profit_b": "PENDING", "loss_a": "DRAFT", "loss_b": "PENDING"}


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize(
    "path",
    ["profit_b", "loss_b", "profit_a", "loss_a"],
    ids=["profit_submit", "loss_submit", "profit_draft", "loss_draft"],
)
def test_asset_sale_create(page, sale, asset_sale_page, asset_sale_list_page, take_screenshot, path):
    """Asset Sale: sell an asset above or below the Written Down Value and save it with Submit or Draft."""
    # Step 1: sell the asset of this path: fill the sale form, Add to Grid and save it
    flow = sale.reach(path, "saved")
    take_screenshot(f"asset {flow['serial']} sold for {int(flow['sale_value'])} ({flow['status']})")

    # Step 2: the Asset Sale List shows the sale with the saved status
    asset_sale_list_page.navigate_here()
    asset_sale_list_page.filter_by_status(LIST_STATUS[path])
    asset_sale_list_page.verify_status(flow["sale_id"], LIST_STATUS[path])
    take_screenshot(f"sale {flow['sale_id']} is {LIST_STATUS[path]}")
