"""
test_22_asset_gate_pass_generation_transfer.py: Asset Transfer > Gate Pass
Generation: the acknowledged challan is listed and its Preview opens the gate pass
as a PDF.

Built from automation/element_catalog/asset_shipment*.md, asset_gate_pass_generation.md
and projects/fixedasset/e2e-flows/asset-transfer-shipment.md. One user (the logged-in
TEST_USERNAME) does everything for now. The shipment moves through files 19 to 22 in
order (see utils/transfer_helper.py); every test also runs on its own: it does the
earlier stages first.

    pytest tests/test_22_asset_gate_pass_generation_transfer.py
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
# 9. Gate Pass
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_gate_pass_lists_the_acknowledged_challan(gate_pass_page, transfer, take_screenshot):
    """Gate Pass Generation: the acknowledged challan is listed with ACKNOWLEDGED."""
    # Step 1: find the challan on Gate Pass Generation
    challan_no = transfer.reach("acknowledged")["challan_no"]
    gate_pass_page.navigate_here()
    gate_pass_page.filter_by_out_challan_no(challan_no)
    take_screenshot("gate pass listed")

    # Step 2: its Status is ACKNOWLEDGED
    row = gate_pass_page.read_row(challan_no)
    assert row["Status"] == "ACKNOWLEDGED", f"Expected the Status ACKNOWLEDGED but found row {row}"


@pytest.mark.regression
def test_gate_pass_preview_is_a_pdf(gate_pass_page, transfer, take_screenshot):
    """Gate Pass Generation: Preview opens the Gate Pass report as a PDF."""
    # Step 1: find the challan on Gate Pass Generation
    challan_no = transfer.reach("acknowledged")["challan_no"]
    gate_pass_page.navigate_here()
    gate_pass_page.filter_by_out_challan_no(challan_no)

    # Step 2: click Preview; the report opens in a new tab
    preview = gate_pass_page.read_preview(challan_no)
    take_screenshot("gate pass previewed")

    # Step 3: the report is a PDF from the gate pass report
    gate_pass_page.verify_preview_is_pdf(preview, challan_no)
