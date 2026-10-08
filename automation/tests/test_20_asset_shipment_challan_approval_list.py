"""
test_20_asset_shipment_challan_approval_list.py: Asset Transfer > Asset Shipment
Challan Approval List (the pending challan, its popup, Show Serial, Approve) and
the approval of the shipment itself, which follows the approved challan.

Built from automation/element_catalog/asset_shipment*.md, asset_gate_pass_generation.md
and projects/fixedasset/e2e-flows/asset-transfer-shipment.md. One user (the logged-in
TEST_USERNAME) does everything for now. The shipment moves through files 19 to 22 in
order (see utils/transfer_helper.py); every test also runs on its own: it does the
earlier stages first.

    pytest tests/test_20_asset_shipment_challan_approval_list.py
"""
import pytest

from test_data.toast_messages import CHALLAN_APPROVED_TOAST, SHIPMENT_APPROVED_TOAST
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """The one tab of the logged-in user, used for the whole test: it registers the asset and does every step."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 6. Approve the challan
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_approval_list_shows_the_pending_challan(challan_approval_page, transfer, take_screenshot):
    """Challan Approval List: a submitted challan is listed as PENDING with its projects."""
    # Step 1: find the submitted challan in the approval list
    flow = transfer.reach("challan_submitted")
    challan_approval_page.navigate_here()
    challan_approval_page.filter_by_out_challan_no(flow["challan_no"])
    take_screenshot("challan in the approval list")

    # Step 2: Status PENDING, the shipment and the projects
    challan_approval_page.verify_row_status(flow["challan_no"], "PENDING")
    row = challan_approval_page.read_row(flow["challan_no"])
    assert row["Shipment Number"] == flow["shipment_no"], f"Unexpected row: {row}"
    assert row["To Project"] == "[060] Progoti", f"Unexpected row: {row}"


@pytest.mark.regression
def test_approval_popup_offers_approve_reject_sendback(challan_approval_page, transfer, take_screenshot):
    """Challan Approval List: the challan popup offers Approve, Reject and Sendback."""
    # Step 1: open the popup of the pending challan
    flow = transfer.reach("challan_submitted")
    challan_approval_page.navigate_here()
    challan_approval_page.filter_by_out_challan_no(flow["challan_no"])
    challan_approval_page.open_popup(flow["challan_no"])
    take_screenshot("approval popup")

    # Step 2: the three actions are there
    challan_approval_page.verify_popup_actions(["Approve", "Reject", "Sendback"])


@pytest.mark.regression
def test_approval_show_serial_lists_the_serial(challan_approval_page, transfer, take_screenshot):
    """Challan Approval List: Show Serial lists the serial added to the challan."""
    # Step 1: open the popup and click Show Serial
    flow = transfer.reach("challan_submitted")
    challan_approval_page.navigate_here()
    challan_approval_page.filter_by_out_challan_no(flow["challan_no"])
    challan_approval_page.open_popup(flow["challan_no"])
    challan_approval_page.click_show_serial()
    take_screenshot("show serial popup")

    # Step 2: the serial is listed
    challan_approval_page.verify_shown_serials(flow["serial"])
    challan_approval_page.close_show_serial_popup()


@pytest.mark.regression
def test_challan_approve(challan_approval_page, transfer, take_screenshot):
    """Challan Approval List: a pending challan can be approved with a comment."""
    # Step 1: open the popup of the pending challan and type a comment
    flow = transfer.reach("challan_submitted")
    challan_approval_page.navigate_here()
    challan_approval_page.filter_by_out_challan_no(flow["challan_no"])
    challan_approval_page.open_popup(flow["challan_no"])
    challan_approval_page.enter_comment("AUTOMATION_TEST approve challan")

    # Step 2: Approve shows the success message
    toast = challan_approval_page.approve_and_get_toast()
    challan_approval_page.verify_toast(toast, CHALLAN_APPROVED_TOAST)
    take_screenshot("challan approved")

    # Step 3: the row is APPROVED and now has a Preview link
    challan_approval_page.filter_by_out_challan_no(flow["challan_no"])
    challan_approval_page.verify_row_status(flow["challan_no"], "APPROVED")
    transfer.record("challan_approved")
    assert challan_approval_page.row_has_preview_link(flow["challan_no"]), "Expected a Preview link after approval."


# ---------------------------------------------------------------------------
# 7. Approve the shipment
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_shipment_approve(shipment_page, transfer, take_screenshot):
    """Asset Shipment: with an approved challan the shipment can be approved; a Gate Pass is generated."""
    # Step 1: open the shipment that has an approved challan
    shipment_no = transfer.reach("challan_approved")["shipment_no"]
    shipment_page.navigate_here()
    shipment_page.filter_by_shipment_no(shipment_no)
    shipment_page.open_details(shipment_no)

    # Step 2: Approve shows both messages
    toast = shipment_page.approve_shipment_and_get_toast()
    shipment_page.verify_toast(toast, SHIPMENT_APPROVED_TOAST)
    take_screenshot("shipment approved")

    # Step 3: the shipment is APPROVED and has a Preview link (remembered as soon as it is APPROVED)
    shipment_page.filter_by_shipment_no(shipment_no)
    shipment_page.verify_row_status(shipment_no, "APPROVED")
    transfer.record("shipment_approved")
    assert shipment_page.is_preview_link_shown(shipment_no), "Expected a Preview link after approval."
