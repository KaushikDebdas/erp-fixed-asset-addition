"""
test_24_asset_single_in_challan.py: tests for Fixed Asset > Single Challan >
Asset Single In-Challan: the approved challan waiting for the receiving side,
and Acknowledge.

Built from automation/element_catalog/asset_single_in_challan.md. Everything is
done by one user (the logged-in ERP_USERNAME, for now). The challans come from
utils/single_challan_flow.py; each test does the earlier stages first when it
runs alone. Acknowledge shows no message that has been confirmed, so the
Status in the list is checked instead.

    pytest tests/test_24_asset_single_in_challan.py
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


# ---------------------------------------------------------------------------
# A Single Challan to another branch: the receiving branch's user (ACK_SHIPMENT_ERP_* in .env)
# The Acknowledge tests click Acknowledge and must end like inside one branch.
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_single_out_challan_different_branch_same_project_receiving_user_sees_the_challan(
    single_challan_other_branch_same_project, ack_single_in_challan_page, take_ack_shipment_screenshot
):
    """Asset Single In-Challan: sent to another branch with the same project, the receiving branch's user finds the approved challan with the branches and projects it was created with."""
    # Step 1: do every stage up to the approved challan, then open the receiving user's Single In-Challan list
    flow = single_challan_other_branch_same_project.reach("submit", "approved")
    challan_no = flow["challan_no"]
    ack_single_in_challan_page.navigate_here()
    ack_single_in_challan_page.filter_by_out_challan_no(challan_no)
    take_ack_shipment_screenshot("challan in the receiving branch list")

    # Step 2: the row shows what the challan was created with
    ack_single_in_challan_page.verify_row_matches_challan(challan_no, flow["challan_data"], flow["sending_branch"])


@pytest.mark.regression
def test_single_out_challan_different_branch_different_project_receiving_user_sees_the_challan(
    single_challan_other_branch_different_project, ack_single_in_challan_page, take_ack_shipment_screenshot
):
    """Asset Single In-Challan: sent to another branch with a different project, the receiving branch's user finds the approved challan with the branches and projects it was created with."""
    # Step 1: do every stage up to the approved challan, then open the receiving user's Single In-Challan list
    flow = single_challan_other_branch_different_project.reach("submit", "approved")
    challan_no = flow["challan_no"]
    ack_single_in_challan_page.navigate_here()
    ack_single_in_challan_page.filter_by_out_challan_no(challan_no)
    take_ack_shipment_screenshot("challan in the receiving branch list")

    # Step 2: the row shows what the challan was created with
    ack_single_in_challan_page.verify_row_matches_challan(challan_no, flow["challan_data"], flow["sending_branch"])


@pytest.mark.regression
def test_single_out_challan_different_branch_same_project_receiving_user_acknowledges_the_challan(
    single_challan_other_branch_same_project, ack_single_in_challan_page, take_ack_shipment_screenshot
):
    """Asset Single In-Challan: sent to another branch with the same project, the receiving branch's user acknowledges the challan, and it ends ACKNOWLEDGED with a Preview link like inside one branch."""
    # Step 1: open the approved challan in the receiving user's list
    flow = single_challan_other_branch_same_project.reach("submit", "approved")
    single_challan_other_branch_same_project.open_challan_to_acknowledge("submit")
    take_ack_shipment_screenshot("challan popup of the receiving user")

    # Step 2: Acknowledge is offered; click it
    actions = ack_single_in_challan_page.read_popup_actions()
    assert actions == ["Acknowledge"], f"Expected the action ['Acknowledge'] but found {actions}"
    message = ack_single_in_challan_page.acknowledge_and_get_message()
    ack_single_in_challan_page.close_popup_if_open()

    # Step 3: search again; the row must show ACKNOWLEDGED (otherwise the failure names the ERP message)
    ack_single_in_challan_page.filter_by_out_challan_no(flow["challan_no"])
    take_ack_shipment_screenshot("challan after Acknowledge")
    ack_single_in_challan_page.verify_acknowledged(flow["challan_no"], message)
    single_challan_other_branch_same_project.record("submit", "acknowledged")


@pytest.mark.regression
def test_single_out_challan_different_branch_different_project_receiving_user_acknowledges_the_challan(
    single_challan_other_branch_different_project, ack_single_in_challan_page, take_ack_shipment_screenshot
):
    """Asset Single In-Challan: sent to another branch with a different project, the receiving branch's user acknowledges the challan, and it ends ACKNOWLEDGED with a Preview link like inside one branch."""
    # Step 1: open the approved challan in the receiving user's list
    flow = single_challan_other_branch_different_project.reach("submit", "approved")
    single_challan_other_branch_different_project.open_challan_to_acknowledge("submit")
    take_ack_shipment_screenshot("challan popup of the receiving user")

    # Step 2: Acknowledge is offered; click it
    actions = ack_single_in_challan_page.read_popup_actions()
    assert actions == ["Acknowledge"], f"Expected the action ['Acknowledge'] but found {actions}"
    message = ack_single_in_challan_page.acknowledge_and_get_message()
    ack_single_in_challan_page.close_popup_if_open()

    # Step 3: search again; the row must show ACKNOWLEDGED (otherwise the failure names the ERP message)
    ack_single_in_challan_page.filter_by_out_challan_no(flow["challan_no"])
    take_ack_shipment_screenshot("challan after Acknowledge")
    ack_single_in_challan_page.verify_acknowledged(flow["challan_no"], message)
    single_challan_other_branch_different_project.record("submit", "acknowledged")
