"""
test_26_asset_gate_pass_generation_challan.py: tests for Fixed Asset > Single
Challan > Gate Pass Generation: the acknowledged single challan is listed and
its Preview opens the gate pass as a PDF.

Built from automation/element_catalog/asset_single_challan_gate_pass.md. Everything
is done by one user (the logged-in TEST_USERNAME, for now). The challans come from
utils/single_challan_flow.py; each test does the earlier stages first when it
runs alone.

    pytest tests/test_26_asset_gate_pass_generation_challan.py
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """The one tab of the logged-in user, used for the whole test: it registers the asset and does every challan step."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.regression
@pytest.mark.parametrize("path", ["submit", "draft"])
def test_gate_pass_lists_the_acknowledged_challan(single_gate_pass_page, single_challan, take_screenshot, path):
    """Gate Pass Generation (Single Challan): the acknowledged challan is listed with ACKNOWLEDGED."""
    # Step 1: find the challan on Gate Pass Generation
    challan_no = single_challan.reach(path, "acknowledged")["challan_no"]
    single_gate_pass_page.navigate_here()
    single_gate_pass_page.filter_by_out_challan_no(challan_no)
    take_screenshot(f"{path} challan on gate pass list")

    # Step 2: its Status is ACKNOWLEDGED
    row = single_gate_pass_page.read_row(challan_no)
    assert row["Status"] == "ACKNOWLEDGED", f"Expected the Status ACKNOWLEDGED but found row {row}"


"""
@pytest.mark.smoke
@pytest.mark.regression
def test_gate_pass_preview_is_a_pdf(single_gate_pass_page, single_challan, take_screenshot):
    # Gate Pass Generation (Single Challan): Preview opens the Gate Pass report as a PDF.
    # Step 1: find the challan on Gate Pass Generation
    challan_no = single_challan.reach("submit", "acknowledged")["challan_no"]
    single_gate_pass_page.navigate_here()
    single_gate_pass_page.filter_by_out_challan_no(challan_no)

    # Step 2: click Preview; the report opens in a new tab
    preview = single_gate_pass_page.read_preview(challan_no)
    take_screenshot("gate pass previewed")

    # Step 3: the report is a PDF from the gate pass report
    single_gate_pass_page.verify_preview_is_pdf(preview, challan_no)

"""