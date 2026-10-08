"""
test_23_asset_single_out_challan.py: tests for Fixed Asset > Single Challan >
Asset Single Out Challan: create a challan with Submit, create one as a Draft
and submit it with Edit, and add the asset serial with Add Serial.

Built from automation/element_catalog/asset_single_out_challan.md. One user (the
logged-in TEST_USERNAME) does everything for now: registers the asset and does
every challan step. Draft and Submit show no message, so the Status in the list
is checked instead.

Two challans move through files 23 to 26 in order (see utils/single_challan_flow.py):
    "submit" path: Create + Submit directly      (its own new approved asset)
    "draft"  path: Create + Draft, Edit, Submit  (its own new approved asset)
Every test also runs on its own: it does the earlier stages first.

    pytest tests/test_23_asset_single_out_challan.py
    pytest tests/test_23_asset_single_out_challan.py -k "add_serial"
"""
import pytest

from utils.run_context import trace_one_test

# Values the challan popup shows (see build_challan_data in test_data/asset_shipment_data.py)
FROM_PROJECT = "[015] Microfinance (Dabi)"
TO_PROJECT = "[060] Progoti"


@pytest.fixture
def page(logged_in_page, request):
    """The one tab of the logged-in user, used for the whole test: it registers the asset and does every challan step."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_out_challan_create_and_submit(single_out_challan_page, single_challan, take_screenshot):
    """Asset Single Out Challan: a challan created with Submit is PENDING and cannot be edited."""
    # Step 1: create the challan and submit it
    challan_no = single_challan.reach("submit", "submitted")["challan_no"]
    single_out_challan_page.navigate_here()
    single_out_challan_page.filter_by_out_challan_no(challan_no)
    take_screenshot("challan submitted")

    # Step 2: the list shows PENDING and no Edit link
    single_out_challan_page.verify_row_status(challan_no, "PENDING")
    assert not single_out_challan_page.row_has_edit_link(challan_no), "Expected no Edit link on a submitted challan."

    # Step 3: the challan popup shows the projects and the status
    single_out_challan_page.open_popup(challan_no)
    single_out_challan_page.verify_popup_values(
        {"Out Challan No": challan_no, "From Project": FROM_PROJECT, "To Project": TO_PROJECT, "Status": "PENDING"}
    )


@pytest.mark.regression
def test_out_challan_create_draft_then_submit(single_out_challan_page, single_challan, take_screenshot):
    """Asset Single Out Challan: a Draft challan has an Edit link; after Edit and Submit it is PENDING."""
    # Step 1: create the challan and save it as Draft; the list shows DRAFT with an Edit link
    challan_no = single_challan.reach("draft", "drafted")["challan_no"]
    single_out_challan_page.navigate_here()
    single_out_challan_page.filter_by_out_challan_no(challan_no)
    single_out_challan_page.verify_row_status(challan_no, "DRAFT")
    assert single_out_challan_page.row_has_edit_link(challan_no), "Expected an Edit link on a Draft challan."
    take_screenshot("challan drafted")

    # Step 2: open the Draft with Edit and submit it
    single_challan.reach("draft", "submitted")

    # Step 3: the list shows PENDING and no Edit link
    single_out_challan_page.navigate_here()
    single_out_challan_page.filter_by_out_challan_no(challan_no)
    single_out_challan_page.verify_row_status(challan_no, "PENDING")
    assert not single_out_challan_page.row_has_edit_link(challan_no), "Expected no Edit link after Submit."
    take_screenshot("draft submitted")


@pytest.mark.regression
@pytest.mark.parametrize("path", ["submit", "draft"])
def test_out_challan_add_serial(single_out_challan_page, single_challan, take_screenshot, path):
    """Asset Single Out Challan: Add Serial puts the asset serial on the challan, shown on its Asset Serials tab."""
    # Step 1: add the serial of the new approved asset to the submitted challan
    flow = single_challan.reach(path, "serial_added")

    # Step 2: open the challan again; its Asset Serials tab lists the serial
    single_out_challan_page.navigate_here()
    single_out_challan_page.filter_by_out_challan_no(flow["challan_no"])
    single_out_challan_page.open_popup(flow["challan_no"])
    serials = single_out_challan_page.read_serials()
    take_screenshot(f"serial added to the {path} challan")
    assert serials == [flow["serial"]], f"Expected the serials {[flow['serial']]} but found {serials}"
