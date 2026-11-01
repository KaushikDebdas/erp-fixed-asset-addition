"""
test_20_asset_shipment_in_challan.py: Asset Transfer > Asset Shipment-In Challan:
the approved challan waiting to be acknowledged, and Acknowledge. Acknowledge shows
no message that has been confirmed, so the Status in the list is checked instead.

Built from automation/element_catalog/asset_shipment*.md, asset_gate_pass_generation.md
and projects/fixedasset/e2e-flows/asset-transfer-shipment.md. One user (the logged-in
ERP_USERNAME) does everything for now. The shipment moves through files 18 to 21 in
order (see utils/transfer_helper.py); every test also runs on its own: it does the
earlier stages first.

    pytest tests/test_20_asset_shipment_in_challan.py
"""
import pytest

from utils.run_context import trace_one_test


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


# ---------------------------------------------------------------------------
# 9. A shipment to another branch: the receiving branch's user (ACK_SHIPMENT_ERP_* in .env)
#    The Acknowledge tests click Acknowledge and must end like inside one branch.
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_different_branch_same_project_receiving_user_sees_the_challan(
    transfer_other_branch_same_project, ack_in_challan_page, take_ack_shipment_screenshot
):
    """Shipment-In Challan: sent to another branch with the same project, the receiving branch's user finds the approved challan with the branches and projects it was created with."""
    # Step 1: do every stage up to the approved shipment, then open the receiving user's In-Challan list
    flow = transfer_other_branch_same_project.reach("shipment_approved")
    challan_no = flow["challan_no"]
    ack_in_challan_page.navigate_here()
    ack_in_challan_page.filter_by_out_challan_no(challan_no)
    take_ack_shipment_screenshot("challan in the receiving branch list")

    # Step 2: the row shows what the challan was created with
    ack_in_challan_page.verify_row_matches_challan(challan_no, flow["challan_data"], flow["sending_branch"])


@pytest.mark.regression
def test_different_branch_different_project_receiving_user_sees_the_challan(
    transfer_other_branch_different_project, ack_in_challan_page, take_ack_shipment_screenshot
):
    """Shipment-In Challan: sent to another branch with a different project, the receiving branch's user finds the approved challan with the branches and projects it was created with."""
    # Step 1: do every stage up to the approved shipment, then open the receiving user's In-Challan list
    flow = transfer_other_branch_different_project.reach("shipment_approved")
    challan_no = flow["challan_no"]
    ack_in_challan_page.navigate_here()
    ack_in_challan_page.filter_by_out_challan_no(challan_no)
    take_ack_shipment_screenshot("challan in the receiving branch list")

    # Step 2: the row shows what the challan was created with
    ack_in_challan_page.verify_row_matches_challan(challan_no, flow["challan_data"], flow["sending_branch"])


@pytest.mark.regression
def test_different_branch_same_project_receiving_user_acknowledges_the_challan(
    transfer_other_branch_same_project, ack_in_challan_page, take_ack_shipment_screenshot
):
    """Shipment-In Challan: sent to another branch with the same project, the receiving branch's user acknowledges the challan, and it ends ACKNOWLEDGED with a Preview link like inside one branch."""
    # Step 1: open the approved challan in the receiving user's list
    flow = transfer_other_branch_same_project.reach("shipment_approved")
    transfer_other_branch_same_project.open_challan_to_acknowledge()
    take_ack_shipment_screenshot("challan popup of the receiving user")

    # Step 2: Acknowledge is offered; click it
    actions = ack_in_challan_page.read_popup_actions()
    assert actions == ["Acknowledge"], f"Expected the action ['Acknowledge'] but found {actions}"
    message = ack_in_challan_page.acknowledge_and_get_message()
    ack_in_challan_page.close_popup_if_open()

    # Step 3: search again; the row must show ACKNOWLEDGED (otherwise the failure names the ERP message)
    ack_in_challan_page.filter_by_out_challan_no(flow["challan_no"])
    take_ack_shipment_screenshot("challan after Acknowledge")
    ack_in_challan_page.verify_acknowledged(flow["challan_no"], message)
    transfer_other_branch_same_project.record("acknowledged")


@pytest.mark.regression
def test_different_branch_different_project_receiving_user_acknowledges_the_challan(
    transfer_other_branch_different_project, ack_in_challan_page, take_ack_shipment_screenshot
):
    """Shipment-In Challan: sent to another branch with a different project, the receiving branch's user acknowledges the challan, and it ends ACKNOWLEDGED with a Preview link like inside one branch."""
    # Step 1: open the approved challan in the receiving user's list
    flow = transfer_other_branch_different_project.reach("shipment_approved")
    transfer_other_branch_different_project.open_challan_to_acknowledge()
    take_ack_shipment_screenshot("challan popup of the receiving user")

    # Step 2: Acknowledge is offered; click it
    actions = ack_in_challan_page.read_popup_actions()
    assert actions == ["Acknowledge"], f"Expected the action ['Acknowledge'] but found {actions}"
    message = ack_in_challan_page.acknowledge_and_get_message()
    ack_in_challan_page.close_popup_if_open()

    # Step 3: search again; the row must show ACKNOWLEDGED (otherwise the failure names the ERP message)
    ack_in_challan_page.filter_by_out_challan_no(flow["challan_no"])
    take_ack_shipment_screenshot("challan after Acknowledge")
    ack_in_challan_page.verify_acknowledged(flow["challan_no"], message)
    transfer_other_branch_different_project.record("acknowledged")
