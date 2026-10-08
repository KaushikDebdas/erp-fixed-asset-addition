"""
test_19_asset_shipment.py: tests for Asset Transfer > Asset Shipment and its Transfer
Challan, up to the submitted challan (same branch, different project).

Built from automation/element_catalog/asset_shipment*.md, asset_gate_pass_generation.md
and projects/fixedasset/e2e-flows/asset-transfer-shipment.md. One user (the logged-in
TEST_USERNAME) does everything for now. The journal voucher check is not part of
these files yet.

One shipment moves through files 19 to 22 in order (see utils/transfer_helper.py):
    test_19  1. The list and the Create Shipment popup
             2. Create the shipment
             3. The challan popup, before anything is saved
             4. Draft the challan and add its serial
             5. Submit the challan
    test_20  6. Approve the challan (Challan Approval List)
             7. Approve the shipment
    test_21  8. Acknowledge on Asset Shipment-In Challan
    test_22  9. Gate Pass

Every test also runs on its own: it does the earlier stages first. Run in file
order, each stage is done once and reused. Do not run a later test before an
earlier one that checks the older state (for example 'Pending') in the same run.
    pytest tests/test_19_asset_shipment.py

The approved asset that is transferred is the slot transfer_a of the asset pool
(`transfer.get_asset()`, utils/transfer_helper.py): it is registered and approved
when the pool has none, and it is used up once its serial is in a challan. The
shipment itself is new in every run.
    pytest "tests/test_19_asset_shipment.py::test_challan_submit"
"""
import pytest

from test_data.asset_shipment_data import build_challan_data, build_shipment_data
from test_data.toast_messages import (
    CHALLAN_DELETED_TOAST,
    CHALLAN_DRAFTED_TOAST,
    CHALLAN_NO_FROM_PROJECT_TOAST,
    CHALLAN_NO_ITEMS_TOAST,
    CHALLAN_NO_TO_PROJECT_TOAST,
    CHALLAN_SERIAL_ADDED_TOAST,
    CHALLAN_SUBMITTED_TOAST,
    SHIPMENT_CREATED_TOAST,
    SHIPMENT_NO_APPROVED_CHALLAN_TOAST,
    SHIPMENT_NO_CHALLAN_TOAST,
)
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """The one tab of the logged-in user, used for the whole test: it registers the asset and does every step."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The list and the Create Shipment popup
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_shipment_list_columns(shipment_page, take_screenshot):
    """Asset Shipment: the list shows the expected columns, in order."""
    # Step 1: open Asset Shipment
    shipment_page.navigate_here()
    take_screenshot("shipment list opened")

    # Step 2: the column headings are as expected (the second is a hidden id column)
    expected = [
        "SL", "", "Shipment No", "Edit", "Shipment Date", "Created By",
        "Creation Date", "Approved By", "Approval Date", "From Branch", "Status", "Preview",
    ]
    found = shipment_page.read_headers()
    assert found == expected, f"Expected the columns {expected} but found {found}."


@pytest.mark.regression
def test_shipment_status_filter_options(shipment_page):
    """Asset Shipment: the Shipment Status filter offers PENDING, APPROVED and REJECTED."""
    # Step 1: open Asset Shipment
    shipment_page.navigate_here()

    # Step 2: read the Shipment Status options
    expected = ["-Select Shipment Status-", "PENDING", "APPROVED", "REJECTED"]
    found = shipment_page.read_status_filter_options()
    assert found == expected, f"Expected the options {expected} but found {found}."


@pytest.mark.regression
def test_shipment_create_popup_defaults(shipment_page, take_screenshot):
    """Asset Shipment: the Create Shipment popup shows AUTO, the branch and today's date."""
    # Step 1: open the Create Shipment popup
    shipment_page.navigate_here()
    shipment_page.open_create_popup()
    take_screenshot("create shipment popup")

    # Step 2: Shipment No is AUTO, From Branch is Head Office, Shipment Date is today
    shipment_page.verify_create_popup_defaults()


@pytest.mark.regression
def test_shipment_create_popup_reset_clears_values(shipment_page, take_screenshot):
    """Asset Shipment: Reset in the Create Shipment popup clears what was typed."""
    # Step 1: open the popup and type the courier details
    shipment_page.navigate_here()
    shipment_page.open_create_popup()
    shipment_page.fill_shipment_form(build_shipment_data())
    take_screenshot("create shipment popup filled")

    # Step 2: click Reset
    shipment_page.reset_create_popup()
    take_screenshot("create shipment popup reset")

    # Step 3: the courier name is empty again
    found = shipment_page.read_edit_popup_values()["courier_name"]
    assert found == "", f"Expected the courier name to be empty after Reset but found '{found}'."


@pytest.mark.regression
def test_shipment_create_popup_can_be_closed(shipment_page, take_screenshot):
    """Asset Shipment: the Create Shipment popup closes with Close."""
    # Step 1: open the popup
    shipment_page.navigate_here()
    shipment_page.open_create_popup()

    # Step 2: close it (the method waits until the popup is gone)
    shipment_page.close_create_popup()
    take_screenshot("create shipment popup closed")


# ---------------------------------------------------------------------------
# 2. Create the shipment
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_shipment_create_saved(shipment_page, transfer, take_screenshot):
    """Asset Shipment: a shipment can be saved, and shows in the list as PENDING."""
    data = build_shipment_data()

    # Step 1: open the Create Shipment popup and fill it
    shipment_page.navigate_here()
    shipment_page.open_create_popup()
    shipment_page.fill_shipment_form(data)
    take_screenshot("shipment form filled")

    # Step 2: Save shows the success message
    toast = shipment_page.save_shipment_and_get_toast()
    shipment_page.verify_toast(toast, SHIPMENT_CREATED_TOAST)
    take_screenshot("shipment saved")

    # Step 3: the newest row is the new shipment, with Status PENDING
    shipment_page.search()
    shipment_no = shipment_page.get_newest_shipment_no()
    shipment_page.verify_row_status(shipment_no, "PENDING")

    # Step 4: remember the shipment for the tests that follow
    transfer.record("shipment", shipment_data=data, shipment_no=shipment_no)


@pytest.mark.regression
def test_shipment_is_listed_without_preview(shipment_page, transfer, take_screenshot):
    """Asset Shipment: a pending shipment is found by its Shipment No and has no Preview yet."""
    # Step 1: get a saved shipment (reused from the test above, or created now)
    shipment_no = transfer.reach("shipment")["shipment_no"]

    # Step 2: find it by its Shipment No
    shipment_page.navigate_here()
    shipment_page.filter_by_shipment_no(shipment_no)
    take_screenshot("shipment found by number")

    # Step 3: Status is PENDING and there is no Preview link
    shipment_page.verify_row_status(shipment_no, "PENDING")
    assert not shipment_page.is_preview_link_shown(shipment_no), "Expected no Preview link for a pending shipment."


@pytest.mark.regression
def test_shipment_edit_popup_shows_saved_values(shipment_page, transfer, take_screenshot):
    """Asset Shipment: Edit opens Update Shipment with the values that were saved."""
    # Step 1: get a saved shipment
    flow = transfer.reach("shipment")

    # Step 2: open its Update Shipment popup
    shipment_page.navigate_here()
    shipment_page.filter_by_shipment_no(flow["shipment_no"])
    shipment_page.open_edit_popup(flow["shipment_no"])
    take_screenshot("update shipment popup")

    # Step 3: the popup shows the saved values
    found = shipment_page.read_edit_popup_values()
    data = flow["shipment_data"]
    assert found["shipment_no"] == flow["shipment_no"], f"Unexpected popup values: {found}"
    assert found["courier_name"] == data["courier_name"], f"Unexpected popup values: {found}"
    assert found["remarks"] == data["remarks"], f"Unexpected popup values: {found}"


@pytest.mark.regression
def test_shipment_details_popup_shows_saved_values(shipment_page, transfer, take_screenshot):
    """Asset Shipment: the Shipment No link opens Shipment Details with the saved values and three tabs."""
    # Step 1: get a saved shipment
    flow = transfer.reach("shipment")

    # Step 2: open its Shipment Details popup
    shipment_page.navigate_here()
    shipment_page.filter_by_shipment_no(flow["shipment_no"])
    shipment_page.open_details(flow["shipment_no"])
    take_screenshot("shipment details popup")

    # Step 3: the saved values, the tabs and the status
    shipment_page.verify_details_values(flow["shipment_data"], flow["shipment_no"])
    tabs = shipment_page.read_details_tab_names()
    assert tabs == ["Details", "Transfer Challans", "Add Serial"], f"Unexpected tabs: {tabs}"
    status = shipment_page.read_details_values()["status"]
    assert status == "PENDING", f"Expected the status PENDING but found '{status}'."


@pytest.mark.regression
def test_shipment_approve_without_challan_is_refused(shipment_page, transfer, take_screenshot):
    """Asset Shipment: Approve with no challan is refused."""
    # Step 1: open the Shipment Details of a shipment that has no challan yet
    shipment_no = transfer.reach("shipment")["shipment_no"]
    shipment_page.navigate_here()
    shipment_page.filter_by_shipment_no(shipment_no)
    shipment_page.open_details(shipment_no)

    # Step 2: click Approve
    toast = shipment_page.approve_shipment_and_get_toast()
    take_screenshot("approve refused without a challan")

    # Step 3: the message asks for a challan
    shipment_page.verify_toast(toast, SHIPMENT_NO_CHALLAN_TOAST)


# ---------------------------------------------------------------------------
# 3. The challan popup, before anything is saved
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_challan_popup_defaults(challan_page, transfer, take_screenshot):
    """Transfer Challan: the Create Challan popup shows AUTO and the sending branch."""
    # Step 1: open the Create Challan popup of the saved shipment
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    take_screenshot("create challan popup")

    # Step 2: Out Challan No is AUTO and the Sending Branch is Head Office
    found = challan_page.read_challan_popup_defaults()
    assert found["out_challan_no"] == "AUTO", f"Expected Out Challan No 'AUTO' but found {found}"
    assert "BDHO" in found["sending_branch"], f"Expected the Sending Branch to contain 'BDHO' but found {found}"


@pytest.mark.regression
def test_challan_item_fills_classification(challan_page, transfer, take_screenshot):
    """Transfer Challan: picking the asset item fills its Category, Sub Category, Group and Unit."""
    # Step 1: open the Create Challan popup and pick the asset item
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    data = build_challan_data()
    challan_page.choose_asset_item(data["item_search"], data["item_name"])
    take_screenshot("asset item picked")

    # Step 2: the read-only boxes are filled in
    found = challan_page.read_item_classification()
    assert found["category"] == "Furniture", f"Unexpected classification: {found}"
    assert found["sub_category"] == "Wooden Furniture", f"Unexpected classification: {found}"
    assert found["unit"] == "Pcs", f"Unexpected classification: {found}"


@pytest.mark.regression
def test_challan_add_without_from_project_is_refused(challan_page, transfer, take_screenshot):
    """Transfer Challan: Add is refused while no From Project is chosen."""
    # Step 1: open the popup and pick only the asset item and quantity
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    data = build_challan_data()
    challan_page.choose_asset_item(data["item_search"], data["item_name"])
    challan_page.enter_quantity(data["quantity"])

    # Step 2: click Add
    toast = challan_page.click_add_and_get_toast()
    take_screenshot("add refused without a from project")

    # Step 3: the message asks for the From Project
    challan_page.verify_toast(toast, CHALLAN_NO_FROM_PROJECT_TOAST)


@pytest.mark.regression
def test_challan_add_without_to_project_is_refused(challan_page, transfer, take_screenshot):
    """Transfer Challan: Add is refused while no To Project is chosen."""
    # Step 1: open the popup and pick the From Project, branch, asset item and quantity (not the To Project)
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    data = build_challan_data()
    challan_page.choose_from_project(data["from_project"])
    challan_page.choose_receiving_branch(data["receiving_branch"])
    challan_page.choose_asset_item(data["item_search"], data["item_name"])
    challan_page.enter_quantity(data["quantity"])

    # Step 2: click Add
    toast = challan_page.click_add_and_get_toast()
    take_screenshot("add refused without a to project")

    # Step 3: the message asks for the To Project
    challan_page.verify_toast(toast, CHALLAN_NO_TO_PROJECT_TOAST)


@pytest.mark.regression
def test_challan_draft_without_item_is_refused(challan_page, transfer, take_screenshot):
    """Transfer Challan: Draft is refused while no asset line was added."""
    # Step 1: open the popup and pick the projects and branch, but add no line
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    data = build_challan_data()
    challan_page.choose_from_project(data["from_project"])
    challan_page.choose_receiving_branch(data["receiving_branch"])
    challan_page.choose_to_project(data["to_project"])

    # Step 2: click Draft
    toast = challan_page.draft_and_get_toast()
    take_screenshot("draft refused without an item")

    # Step 3: the message says there is no item
    challan_page.verify_toast(toast, CHALLAN_NO_ITEMS_TOAST)


@pytest.mark.regression
def test_challan_added_line_shows_in_grid(challan_page, transfer, take_screenshot):
    """Transfer Challan: an added asset line appears in the grid."""
    # Step 1: fill the popup and add the line
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    transfer.fill_challan_form(build_challan_data())
    take_screenshot("line added")

    # Step 2: the grid shows the item and its quantity
    lines = challan_page.read_item_lines()
    assert len(lines) == 1, f"Expected one line in the grid but found {lines}"
    assert lines[0]["Asset Item Name"] == "Cabinet Table", f"Unexpected line: {lines[0]}"
    assert lines[0]["Quantity"] == "1", f"Unexpected line: {lines[0]}"


@pytest.mark.regression
def test_challan_line_can_be_removed_and_added_again(challan_page, transfer, take_screenshot):
    """Transfer Challan: a line can be removed, and the same item can be added again."""
    # Step 1: add a line, then remove it
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    transfer.fill_challan_form(build_challan_data())
    challan_page.remove_first_item_line()
    challan_page.verify_item_grid_is_empty()
    take_screenshot("line removed")

    # Step 2: pick the item and add it again
    data = build_challan_data()
    challan_page.choose_asset_item(data["item_search"], data["item_name"])
    challan_page.enter_quantity(data["quantity"])
    challan_page.add_item_line()
    take_screenshot("line added again")

    # Step 3: the grid has one line again
    lines = challan_page.read_item_lines()
    assert len(lines) == 1, f"Expected one line in the grid but found {lines}"


# ---------------------------------------------------------------------------
# 4. Draft the challan and add its serial
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_challan_draft_saved(challan_page, transfer, take_screenshot):
    """Transfer Challan: a challan can be saved as a Draft; it gets an Out Challan No."""
    # Step 1: open the Create Challan popup of the saved shipment and fill it
    transfer.reach("shipment")
    transfer.open_challan_tab()
    challan_page.click_create_challan()
    transfer.fill_challan_form(build_challan_data())
    take_screenshot("challan form filled")

    # Step 2: Draft shows the success message
    toast = challan_page.draft_and_get_toast()
    challan_page.verify_toast(toast, CHALLAN_DRAFTED_TOAST)
    take_screenshot("challan drafted")

    # Step 3: the new challan is listed as DRAFT, with no serial yet
    challan_no = challan_page.get_newest_challan_no()
    challan_page.verify_challan_status(challan_no, "DRAFT")
    challan_page.verify_all_serial_added(challan_no, "No")
    transfer.record("draft_challan", challan_no=challan_no)


@pytest.mark.regression
def test_challan_details_popup_shows_the_challan(challan_page, transfer, take_screenshot):
    """Transfer Challan: the Out Challan No opens Challan Details with the projects and three tabs."""
    # Step 1: get a Draft challan and open its details
    challan_no = transfer.reach("draft_challan")["challan_no"]
    transfer.open_challan_tab()
    challan_page.open_challan_details(challan_no)
    take_screenshot("challan details popup")

    # Step 2: the projects and the status
    found = challan_page.read_challan_details_values()
    assert found["from_project"] == "[015] Microfinance (Dabi)", f"Unexpected details: {found}"
    assert found["to_project"] == "[060] Progoti", f"Unexpected details: {found}"
    assert found["status"] == "DRAFT", f"Unexpected details: {found}"

    # Step 3: the tabs
    tabs = challan_page.read_challan_details_tab_names()
    assert tabs == ["Details", "Asset Serials", "Posted Accounts"], f"Unexpected tabs: {tabs}"


@pytest.mark.regression
def test_challan_add_serial_popup_fills_details(challan_page, transfer, take_screenshot):
    """Transfer Challan: picking a serial fills the item name, quantity, sub category and category."""
    # Step 1: open the Add Serial popup of a Draft challan
    challan_no = transfer.reach("draft_challan")["challan_no"]
    asset = transfer.get_asset()
    transfer.open_challan_tab()
    challan_page.open_challan_details(challan_no)
    challan_page.click_add_serial_link()

    # Step 2: pick the serial
    challan_page.choose_serial(asset["serial"])
    take_screenshot("serial picked")

    # Step 3: the item details are filled in
    found = challan_page.read_serial_popup_values()
    assert found["item_name"] == "Cabinet Table", f"Unexpected serial details: {found}"
    assert found["category"] == "Furniture", f"Unexpected serial details: {found}"


@pytest.mark.regression
def test_challan_serial_saved(challan_page, transfer, take_screenshot):
    """Transfer Challan: a serial can be added and saved; the challan then shows All Serial Added."""
    # Step 1: get a Draft challan and an approved asset
    challan_no = transfer.reach("draft_challan")["challan_no"]
    asset = transfer.get_asset()
    transfer.open_challan_tab()
    challan_page.open_challan_details(challan_no)

    # Step 2: add the serial and save
    challan_page.click_add_serial_link()
    challan_page.choose_serial(asset["serial"])
    challan_page.add_serial_to_popup_grid()
    take_screenshot("serial added to the popup grid")
    toast = challan_page.save_serial_and_get_toast()
    challan_page.verify_toast(toast, CHALLAN_SERIAL_ADDED_TOAST)

    # Step 3: remember it; the Asset Serials tab shows the serial
    transfer.record("serial_added", serial=asset["serial"])
    serials = challan_page.read_asset_serials_tab()
    assert serials == [asset["serial"]], f"Expected the serial {asset['serial']} but the tab shows {serials}"


@pytest.mark.regression
def test_shipment_add_serial_tab_shows_the_serial(shipment_page, transfer, take_screenshot):
    """Asset Shipment: the Add Serial tab of the shipment lists the challan's serial."""
    # Step 1: get a challan with a serial and open the shipment details
    flow = transfer.reach("serial_added")
    shipment_page.navigate_here()
    shipment_page.filter_by_shipment_no(flow["shipment_no"])
    shipment_page.open_details(flow["shipment_no"])

    # Step 2: the Add Serial tab lists the serial
    serials = shipment_page.read_add_serial_tab_serials()
    take_screenshot("add serial tab")
    assert serials == [flow["serial"]], f"Expected the serial {flow['serial']} but the tab shows {serials}"


@pytest.mark.regression
def test_challan_list_shows_all_serial_added(challan_page, transfer, take_screenshot):
    """Transfer Challan: after the serial is saved the challan list shows All Serial Added = Yes."""
    # Step 1: get a challan with a serial and open the Transfer Challans tab
    challan_no = transfer.reach("serial_added")["challan_no"]
    transfer.open_challan_tab()
    take_screenshot("transfer challans tab")

    # Step 2: All Serial Added is Yes
    challan_page.verify_all_serial_added(challan_no, "Yes")


@pytest.mark.regression
def test_shipment_approve_with_draft_challan_is_refused(shipment_page, transfer, take_screenshot):
    """Asset Shipment: Approve is refused while the challan is still a Draft."""
    # Step 1: open the shipment that has a Draft challan with a serial
    shipment_no = transfer.reach("serial_added")["shipment_no"]
    shipment_page.navigate_here()
    shipment_page.filter_by_shipment_no(shipment_no)
    shipment_page.open_details(shipment_no)

    # Step 2: click Approve
    toast = shipment_page.approve_shipment_and_get_toast()
    take_screenshot("approve refused with a draft challan")

    # Step 3: the message asks for an approved challan
    shipment_page.verify_toast(toast, SHIPMENT_NO_APPROVED_CHALLAN_TOAST)


@pytest.mark.regression
def test_challan_update_popup_fixed_fields_are_read_only(challan_page, transfer, take_screenshot):
    """Transfer Challan: in Update Challan the branches, projects and date cannot be changed."""
    # Step 1: open the Update Challan popup of the Draft challan
    challan_no = transfer.reach("serial_added")["challan_no"]
    transfer.open_challan_tab()
    challan_page.open_update_challan(challan_no)
    take_screenshot("update challan popup")

    # Step 2: the fixed fields are read-only
    challan_page.verify_update_popup_read_only()


@pytest.mark.regression
def test_extra_draft_challan_can_be_deleted(challan_page, transfer, take_screenshot):
    """Transfer Challan: a Draft challan can be deleted from Update Challan."""
    # Step 1: add a second Draft challan to the shipment
    transfer.reach("serial_added")
    extra_challan_no = transfer.create_extra_draft_challan()

    # Step 2: open its Update Challan popup and click Delete
    transfer.open_challan_tab()
    challan_page.open_update_challan(extra_challan_no)
    toast = challan_page.delete_update_challan_and_get_toast()
    take_screenshot("extra challan deleted")

    # Step 3: the delete message is shown
    challan_page.verify_toast(toast, CHALLAN_DELETED_TOAST)


# ---------------------------------------------------------------------------
# 5. Submit the challan
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_challan_submit(challan_page, transfer, take_screenshot):
    """Transfer Challan: a Draft challan can be submitted from Update Challan; it becomes PENDING."""
    # Step 1: open the Update Challan popup of the Draft challan with a serial
    challan_no = transfer.reach("serial_added")["challan_no"]
    transfer.open_challan_tab()
    challan_page.open_update_challan(challan_no)

    # Step 2: Submit shows the success message
    toast = challan_page.submit_update_challan_and_get_toast()
    challan_page.verify_toast(toast, CHALLAN_SUBMITTED_TOAST)
    take_screenshot("challan submitted")

    # Step 3: the challan is PENDING
    transfer.open_challan_tab()
    challan_page.verify_challan_status(challan_no, "PENDING")
    transfer.record("challan_submitted")
