"""
test_25_asset_single_in_challan.py: tests for Fixed Asset > Single Challan >
Asset Single In-Challan: the approved challan waiting for the receiving side,
and Acknowledge.

Built from automation/element_catalog/asset_single_in_challan.md. Everything is
done by one user (the logged-in TEST_USERNAME, for now). The challans come from
utils/single_challan_flow.py; each test does the earlier stages first when it
runs alone. Acknowledge shows no message that has been confirmed, so the
Status in the list is checked instead.

    pytest tests/test_25_asset_single_in_challan.py
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """The one tab of the logged-in user, used for the whole test: it registers the asset and does every challan step."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.regression
def test_in_challan_is_listed_before_acknowledge(single_in_challan_page, single_challan, take_screenshot):
    """Asset Single In-Challan: the approved challan is listed with an In Challan Number and no Preview yet."""
    # Step 1: find the approved challan on Asset Single In-Challan
    challan_no = single_challan.reach("submit", "approved")["challan_no"]
    single_in_challan_page.navigate_here()
    single_in_challan_page.filter_by_out_challan_no(challan_no)
    take_screenshot("in challan listed")

    # Step 2: APPROVED, an In Challan Number, and no Preview link
    single_in_challan_page.verify_row_status(challan_no, "APPROVED")
    in_challan_no = single_in_challan_page.read_row(challan_no).get("In Challan Number", "")
    assert in_challan_no != "", f"Expected challan {challan_no} to show an In Challan Number but the cell is empty."
    assert not single_in_challan_page.row_has_preview_link(challan_no), "Expected no Preview link before Acknowledge."


@pytest.mark.regression
def test_in_challan_popup_offers_acknowledge(single_in_challan_page, single_challan, take_screenshot):
    """Asset Single In-Challan: the challan popup offers Acknowledge."""
    # Step 1: open the popup of the approved challan
    challan_no = single_challan.reach("submit", "approved")["challan_no"]
    single_in_challan_page.navigate_here()
    single_in_challan_page.filter_by_out_challan_no(challan_no)
    single_in_challan_page.open_popup(challan_no)
    take_screenshot("in challan popup")

    # Step 2: the Acknowledge action is there
    actions = single_in_challan_page.read_popup_actions()
    assert actions == ["Acknowledge"], f"Expected the action ['Acknowledge'] but found {actions}"


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("path", ["submit", "draft"])
def test_in_challan_acknowledge(single_in_challan_page, single_challan, take_screenshot, path):
    """Asset Single In-Challan: Acknowledge changes the status to ACKNOWLEDGED and shows a Preview link."""
    # Step 1: open the popup of the approved challan
    challan_no = single_challan.reach(path, "approved")["challan_no"]
    single_in_challan_page.navigate_here()
    single_in_challan_page.filter_by_out_challan_no(challan_no)
    single_in_challan_page.open_popup(challan_no)

    # Step 2: Acknowledge, close the popup and search again
    single_in_challan_page.acknowledge()
    single_in_challan_page.close_popup_if_open()
    single_in_challan_page.filter_by_out_challan_no(challan_no)
    take_screenshot(f"{path} challan acknowledged")

    # Step 3: ACKNOWLEDGED, with a Preview link (no message was captured for this step)
    single_in_challan_page.verify_row_status(challan_no, "ACKNOWLEDGED")
    single_challan.record(path, "acknowledged")
    assert single_in_challan_page.row_has_preview_link(challan_no), "Expected a Preview link after Acknowledge."
