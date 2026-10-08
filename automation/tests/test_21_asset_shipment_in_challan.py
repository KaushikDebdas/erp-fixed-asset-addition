"""
test_21_asset_shipment_in_challan.py: Asset Transfer > Asset Shipment-In Challan:
the approved challan waiting to be acknowledged, and Acknowledge. Acknowledge shows
no message that has been confirmed, so the Status in the list is checked instead.

Built from automation/element_catalog/asset_shipment*.md, asset_gate_pass_generation.md
and projects/fixedasset/e2e-flows/asset-transfer-shipment.md. One user (the logged-in
TEST_USERNAME) does everything for now. The shipment moves through files 19 to 22 in
order (see utils/transfer_helper.py); every test also runs on its own: it does the
earlier stages first.

    pytest tests/test_21_asset_shipment_in_challan.py
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def transfer(saved_transfer):
    """The shipment stages, with the transferred asset saved in the JSON file."""
    return saved_transfer


@pytest.fixture
def page(logged_in_page, request):
    """The one tab of the logged-in user, used for the whole test: it registers the asset and does every step."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 8. Acknowledge on Asset Shipment-In Challan
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_in_challan_is_listed_before_acknowledge(in_challan_page, transfer, take_screenshot):
    """Shipment-In Challan: the approved challan is listed with an In Challan No and no Preview yet."""
    # Step 1: find the challan on Asset Shipment-In Challan
    challan_no = transfer.reach("shipment_approved")["challan_no"]
    in_challan_page.navigate_here()
    in_challan_page.filter_by_out_challan_no(challan_no)
    take_screenshot("in challan listed")

    # Step 2: APPROVED, an In Challan No, and no Preview link
    in_challan_page.verify_row_status(challan_no, "APPROVED")
    in_challan_page.verify_in_challan_no_filled(challan_no)
    assert not in_challan_page.row_has_preview_link(challan_no), "Expected no Preview link before Acknowledge."


@pytest.mark.regression
def test_in_challan_popup_offers_acknowledge(in_challan_page, transfer, take_screenshot):
    """Shipment-In Challan: the challan popup offers Acknowledge."""
    # Step 1: open the popup of the approved challan
    challan_no = transfer.reach("shipment_approved")["challan_no"]
    in_challan_page.navigate_here()
    in_challan_page.filter_by_out_challan_no(challan_no)
    in_challan_page.open_popup(challan_no)
    take_screenshot("in challan popup")

    # Step 2: the Acknowledge action is there
    actions = in_challan_page.read_popup_actions()
    assert actions == ["Acknowledge"], f"Expected the action ['Acknowledge'] but found {actions}"


@pytest.mark.regression
def test_in_challan_acknowledge(in_challan_page, transfer, take_screenshot):
    """Shipment-In Challan: Acknowledge changes the status to ACKNOWLEDGED and shows a Preview link."""
    # Step 1: open the popup of the approved challan
    challan_no = transfer.reach("shipment_approved")["challan_no"]
    in_challan_page.navigate_here()
    in_challan_page.filter_by_out_challan_no(challan_no)
    in_challan_page.open_popup(challan_no)

    # Step 2: Acknowledge, close the popup and search again
    in_challan_page.acknowledge()
    in_challan_page.close_popup_if_open()
    in_challan_page.filter_by_out_challan_no(challan_no)
    take_screenshot("challan acknowledged")

    # Step 3: ACKNOWLEDGED, with a Preview link (no message was captured for this step)
    in_challan_page.verify_row_status(challan_no, "ACKNOWLEDGED")
    transfer.record("acknowledged")
    assert in_challan_page.row_has_preview_link(challan_no), "Expected a Preview link after Acknowledge."
