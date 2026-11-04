"""
test_34_asset_assign_acknowledgement_extended_assets.py: the Asset Assign
Acknowledgement screen for an assignment that holds a parent asset with
extended assets (CR FAHOV2-643, feature F07 Asset Assign Acknowledgement,
with F01S01 and F02S01).

One assignment is made once per run (`assets_pending_acknowledgement`, about
15 minutes) through HOFIN, HOFA and HOFIN, with the REAL serials read from the
HOFA Global List:
    parent    a new parent asset with three extended assets: the first two are
              active, the third is written off (inactive)
    normal    a new asset with no extended asset
Both are assigned in ONE transaction to the HOFA acknowledger and approved, so
the assignment waits in the Pending Asset Acknowledgement grid.

The screens are used in HOFA (HOFA_URL) by the HOFA acknowledger (HOFA_ACK_USERNAME
and HOFA_ACK_PASSWORD in .env), who is the employee the assets are assigned to.

The tests run top to bottom:
    1. The Details popup while the assignment waits: title and columns, extended assets
       directly below the parent (no SL, indented 4 spaces, no button), SL numbers count
       parents only, an asset with no extended asset, the inactive one not listed, the
       parent's status on the extended rows, the same list when opened again
    2. While it waits, HOFIN refuses an addition to the parent (CR F01S01)
    3. Acknowledge: the parent and its active extended assets are acknowledged together,
       listed in My Assigned Asset and still ASSIGNED

To run part of the file:
    pytest tests/test_34_asset_assign_acknowledgement_extended_assets.py -k "popup or sl_numbers"
"""
import pytest

from pages.asset_assign_acknowledgement_page import AssetAssignAcknowledgementPage
from test_data.asset_transaction_data import ASSIGN, POPUP_ASSET_COLUMNS
from test_data.hofin_asset_data import ADDITION_PARENT_PENDING_MESSAGE, HOFA_ACK_EMPLOYEE_PIN
from test_data.toast_messages import ACKNOWLEDGE_TOAST
from utils.run_context import trace_one_test

# Title of the Details popup (CR F07S01 "Asset Transaction Details (Assign/UnAssign/Internal Movement)")
POPUP_TITLE = "Asset Transaction Details (Assign/UnAssign/Internal Movement)"


@pytest.fixture
def page(hofa_logged_in_page, request):
    """Every test in this file reuses the one HOFA tab that logged in once, as the HOFA acknowledger."""
    assert HOFA_ACK_EMPLOYEE_PIN, "HOFA_ACK_USERNAME must be a numeric login name (the employee PIN) to assign assets to it."
    yield from trace_one_test(hofa_logged_in_page, request)


@pytest.fixture
def acknowledgement_page(page):
    """Asset Assign Acknowledgement in the same HOFA tab: the HOFA acknowledger is the assigned employee."""
    return AssetAssignAcknowledgementPage(page)


# ---------------------------------------------------------------------------
# 1. The Details popup while the assignment waits for acknowledgement
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_details_popup_opens_for_the_assignment(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F07S01): Details of the pending assignment opens the Asset Transaction Details popup with its asset list columns."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details of the pending assignment that holds the parent
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    take_screenshot("details popup of the pending assignment")

    # Step 2: the popup has its title, the ASSIGN type and the asset list columns
    acknowledgement_page.verify_popup_title(POPUP_TITLE)
    found_type = acknowledgement_page.get_popup_value("assetTransactionType")
    assert found_type == ASSIGN, f"Expected Transaction Type {ASSIGN} but found '{found_type}'."
    headers = acknowledgement_page.get_popup_asset_headers()
    assert headers == POPUP_ASSET_COLUMNS, f"Expected columns {POPUP_ASSET_COLUMNS} but found {headers}."
    acknowledgement_page.close_popup()


@pytest.mark.smoke
@pytest.mark.regression
def test_extended_assets_listed_directly_below_parent(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F07S01): the active extended assets are listed directly below their parent, without an SL number, indented 4 spaces, without a button."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details of the pending assignment
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    take_screenshot("extended assets below the parent")

    # Step 2: the two active extended assets follow the parent, in order, with no SL, the indent and no button
    acknowledgement_page.verify_popup_extended_assets_below_parent(assets["parent"], assets["active"])
    acknowledgement_page.close_popup()


@pytest.mark.regression
def test_sl_numbers_count_parent_assets_only(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F07S01): the SL numbers count the assets of the transaction only; extended assets have no SL number."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details of the pending assignment
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    take_screenshot("SL numbers of the details popup")

    # Step 2: parent SL 1, its extended assets no SL, the normal asset SL 2
    expected = {assets["parent"]: "1", assets["active"][0]: "", assets["active"][1]: "", assets["normal"]: "2"}
    acknowledgement_page.verify_popup_sl_numbers(expected)
    acknowledgement_page.close_popup()


@pytest.mark.regression
def test_asset_without_extended_assets_has_no_rows_below_it(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F07S01): an asset with no extended asset is listed as before, with no indented rows below it."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details of the pending assignment
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["normal"])
    take_screenshot("asset without extended assets")

    # Step 2: no extended row follows the normal asset
    acknowledgement_page.verify_popup_extended_assets_below_parent(assets["normal"], [])
    acknowledgement_page.close_popup()


@pytest.mark.regression
def test_inactive_extended_asset_is_not_listed(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F07S01): only active extended assets are listed; the written-off extended asset is not."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details of the pending assignment
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    take_screenshot("inactive extended asset not listed")

    # Step 2: the written-off extended asset is not in the popup
    acknowledgement_page.verify_popup_does_not_list(assets["inactive"])
    acknowledgement_page.close_popup()


@pytest.mark.regression
def test_extended_assets_show_the_parents_assign_status(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F02S01, F07S01): the extended assets are part of the same assignment and show the parent's Assign Status and item."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details of the pending assignment
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    take_screenshot("status of the extended assets")

    # Step 2: the extended rows show the parent's Assign Status and Asset Item Name
    acknowledgement_page.verify_popup_same_status_as_parent(assets["parent"], assets["active"], "Assign Status")
    acknowledgement_page.verify_popup_same_status_as_parent(assets["parent"], assets["active"], "Asset Item Name")
    acknowledgement_page.close_popup()


@pytest.mark.regression
def test_details_popup_is_the_same_when_opened_again(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F07S01): closing and opening Details again shows the same asset list, without duplicate rows."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details, read the asset list and close it
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    first = acknowledgement_page.read_popup_asset_rows()
    acknowledgement_page.close_popup()

    # Step 2: open it again: the same rows, in the same order
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    take_screenshot("details popup opened again")
    second = acknowledgement_page.read_popup_asset_rows()
    acknowledgement_page.close_popup()
    assert second == first, f"The Details popup changed when opened again. First: {first} Second: {second}"


# ---------------------------------------------------------------------------
# 2. While the assignment waits: no addition to the parent (CR F01S01)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_hofin_addition_is_refused_while_acknowledgement_waits(hofin_flow, assets_pending_acknowledgement):
    """HOFIN Vendor Bill Payable (CR F01S01): an addition to a parent whose assignment waits for acknowledgement is refused with the CR message."""
    parent = assets_pending_acknowledgement["parent"]
    expected = ADDITION_PARENT_PENDING_MESSAGE.format(parent)

    # Step 1: the HOFIN creator fills an addition bill for the parent and clicks Submit
    message = hofin_flow.submit_addition_and_read_refusal(parent)

    # Step 2: HOFIN refuses it with the CR message instead of submitting the bill
    assert message != "", f"The addition to {parent} was submitted, but the parent's assignment still waits for acknowledgement."
    assert expected in message, f"Expected the message '{expected}' but HOFIN showed '{message}'."


# ---------------------------------------------------------------------------
# 3. Acknowledge the assignment
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_acknowledge_parent_with_extended_assets(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F02S01, F07S01): acknowledging the assignment from its Details popup acknowledges it once; it leaves the pending grid."""
    assets = assets_pending_acknowledgement

    # Step 1: open Details of the pending assignment and acknowledge it
    acknowledgement_page.navigate_here()
    acknowledgement_page.open_details_of_row_with_serial(assets["parent"])
    toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
    take_screenshot("assignment acknowledged")
    acknowledgement_page.verify_toast_contains(toast, ACKNOWLEDGE_TOAST, "Acknowledge of the assignment")

    # Step 2: no pending acknowledgement for the parent is left
    acknowledgement_page.navigate_here()
    assert not acknowledgement_page.has_pending_for_serial(assets["parent"]), (
        f"The assignment of {assets['parent']} is still waiting for acknowledgement after it was acknowledged."
    )


@pytest.mark.regression
def test_my_assigned_asset_lists_parent_and_active_extended_assets(acknowledgement_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Assign Acknowledgement (CR F02S01): My Assigned Asset lists the parent, its active extended assets and the normal asset, not the written-off one."""
    assets = assets_pending_acknowledgement

    # Step 1: My Assigned Asset lists every active asset of the assignment
    acknowledgement_page.verify_my_assets_include([assets["parent"]] + assets["active"] + [assets["normal"]])
    take_screenshot("my assigned asset")

    # Step 2: the written-off extended asset is not listed
    acknowledgement_page.verify_my_assets_exclude(assets["inactive"])


@pytest.mark.regression
def test_acknowledged_assets_stay_assigned(page, asset_serial_global_list_page, assets_pending_acknowledgement, take_screenshot):
    """Asset Serial Global List (CR F01S02, F02S01): after the acknowledgement the parent, its active extended assets and the normal asset are all ASSIGNED."""
    assets = assets_pending_acknowledgement

    # Step 1: read every asset of the assignment in the Global List
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_all_assigned([assets["parent"]] + assets["active"] + [assets["normal"]])
    take_screenshot("acknowledged assets are assigned")
