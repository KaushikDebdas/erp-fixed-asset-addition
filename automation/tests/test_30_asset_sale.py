"""
test_30_asset_sale.py: tests for the Asset Sale screen (Fixed Asset > Asset
Disposal > Asset Sale): Create with Submit and with Draft, selling above and
below the Written Down Value.

Built from automation/element_catalog/asset_sale.md. The asset sold is one of the
approved assets test_01 creates (see utils/sale_flow.py): UNASSIGNED and IN_USE,
which the sale screen accepts as it is. Each test uses a different asset (they are
not used by the other test files), and a sold asset is removed from the saved
assets, so a later run registers a new one.

The cases (Sale Value compared with the Written Down Value, shown in the grid
as Profit/Loss):
    case 1: Sale Value above it  (+5000, a profit)
    case 2: Sale Value below it  (-5000, a loss)

The whole file logs in once and every test reuses that session.

To run part of the file:
    pytest tests/test_30_asset_sale.py -k "case_2"
"""
import pytest

from utils.run_context import trace_one_test
from utils.sale_flow import create_sale

# Saved status the sale list must show after the save
LIST_STATUS = {"submit": "PENDING", "draft": "DRAFT"}


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize(
    "item, sub_type, sale_change, save_as",
    [
        ("building", "spot", 5000, "submit"),
        ("building", "gift", -5000, "submit"),
        ("laptop", "spot", 5000, "draft"),
        ("laptop", "gift", -5000, "draft"),
    ],
    ids=["case_1_above_wdv_submit", "case_2_below_wdv_submit", "case_1_above_wdv_draft", "case_2_below_wdv_draft"],
)
def test_asset_sale_create(
    page, registrations, asset_sale_page, asset_sale_list_page, take_screenshot, item, sub_type, sale_change, save_as
):
    """Asset Sale: create a sale above or below the Written Down Value and save it with Submit or Draft."""
    # Step 1: sell the approved asset: fill the sale form, Add to Grid and save it
    asset = create_sale(registrations, asset_sale_page, item, sub_type, sale_change, save_as)
    asset_sale_page.verify_grid_is_empty()
    take_screenshot(f"asset {asset['serial']} sold for {int(asset['sale_value'])} ({save_as})")

    # Step 2: the Asset Sale List shows the newest sale with the saved status
    asset_sale_list_page.navigate_here()
    asset_sale_list_page.filter_by_status(LIST_STATUS[save_as])
    sale_id = asset_sale_list_page.get_newest_write_off_id()
    asset_sale_list_page.verify_status(sale_id, LIST_STATUS[save_as])
    take_screenshot(f"sale {sale_id} is {LIST_STATUS[save_as]}")
