"""
test_24_asset_single_out_challan_approval_list.py: tests for Fixed Asset > Single
Challan > Asset Single Out Challan Approval List: the pending challan and its
actions, and approving it (which also generates the gate pass).

Built from automation/element_catalog/asset_single_out_challan_approval_list.md.
Everything is done by one user (the logged-in TEST_USERNAME, for now). The challans come from
utils/single_challan_flow.py; each test does the earlier stages first when it
runs alone.

    pytest tests/test_24_asset_single_out_challan_approval_list.py
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """The one tab of the logged-in user, used for the whole test: it registers the asset and does every challan step."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.regression
def test_approval_list_shows_the_pending_challan(
    single_out_challan_approval_list_page, single_challan, take_screenshot
):
    """Asset Single Out Challan Approval List: the submitted challan is PENDING and its popup offers Approve, Reject and Sendback."""
    # Step 1: find the pending challan in the Approval List
    challan_no = single_challan.reach("submit", "serial_added")["challan_no"]
    single_out_challan_approval_list_page.navigate_here()
    single_out_challan_approval_list_page.filter_by_out_challan_no(challan_no)
    single_out_challan_approval_list_page.verify_row_status(challan_no, "PENDING")
    take_screenshot("pending challan listed")

    # Step 2: open its popup; the three actions are there
    single_out_challan_approval_list_page.open_popup(challan_no)
    actions = single_out_challan_approval_list_page.read_popup_actions()
    assert actions == ["Approve", "Reject", "Sendback"], f"Expected the actions ['Approve', 'Reject', 'Sendback'] but found {actions}"


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("path", ["submit", "draft"])
def test_approval_list_approve_challan(
    single_out_challan_approval_list_page, single_challan, take_screenshot, path
):
    """Asset Single Out Challan Approval List: Approve with a comment makes the challan APPROVED and generates the gate pass."""
    # Step 1: open the pending challan from the Approval List
    flow = single_challan.reach(path, "serial_added")
    challan_no = flow["challan_no"]
    single_out_challan_approval_list_page.navigate_here()
    single_out_challan_approval_list_page.filter_by_out_challan_no(challan_no)
    single_out_challan_approval_list_page.open_popup(challan_no)

    # Step 2: type a comment and Approve; both messages show
    single_out_challan_approval_list_page.enter_comment("Approved by automation")
    single_out_challan_approval_list_page.approve_and_verify()
    take_screenshot(f"{path} challan approved")

    # Step 3: the challan is APPROVED (remembered as soon as it is APPROVED) and has a Preview link
    single_out_challan_approval_list_page.filter_by_out_challan_no(challan_no)
    single_out_challan_approval_list_page.verify_row_status(challan_no, "APPROVED")
    single_challan.record(path, "approved")
    assert single_out_challan_approval_list_page.row_has_preview_link(challan_no), "Expected a Preview link after approval."
