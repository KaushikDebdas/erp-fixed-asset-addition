"""
test_32_asset_serial_global_list_hofin_assets.py: the HOFA Asset Serial Global List
for assets registered in HOFIN (CR FAHOV2-643, F01S01 and F01S02).

The assets are made by the `hofin_assets` helper (utils/hofin_assets.py) through
HOFIN creator > HOFA acknowledger > HOFIN approver, and their REAL serials are
read back from the Global List; no serial is written in this file:
    hofin_normal_asset           a new parent asset with no extended asset
    hofin_parent_with_extended   a new parent asset with two extended assets
                                 ("<parent>-1", "<parent>-2")
Each is made once per run (a few minutes each). The AAQ assets of test_04 are not
touched: both registrations live side by side.

The screens are checked as the HOFA acknowledger (HOFA_ACK_USERNAME in .env).

The tests run top to bottom. Groups 3 and 4 change the parent asset (one more
extended asset, then a DAMAGE status), so they come last:
    1. The normal asset: its row, its popup, an empty Addition History, no Parent Asset field
    2. The parent with extended assets: separate serials, their popups, the parent unchanged,
       the Addition History grid, records per page, the link to the extended asset, the
       parent-only search in HOFIN
    3. A new addition is listed only after HOFA acknowledges and HOFIN approves it
    4. Utilization Status: an extended asset changes alone; the parent's change is copied

To run part of the file:
    pytest tests/test_32_asset_serial_global_list_hofin_assets.py -k "normal or addition_history"
"""
import pytest

from test_data import hofin_asset_data as data
from utils.helpers import unique_name
from utils.run_context import trace_one_test


@pytest.fixture
def page(hofa_logged_in_page, request):
    """Every test in this file reuses the one HOFA tab that logged in once, as the HOFA acknowledger."""
    yield from trace_one_test(hofa_logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. A normal asset registered in HOFIN
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_hofin_asset_is_listed_with_its_data(page, asset_serial_global_list_page, hofin_normal_asset, take_screenshot):
    """Asset Serial Global List (CR F01S01): an asset registered through HOFIN > HOFA > HOFIN is listed with its item, classification, project and statuses."""
    serial = hofin_normal_asset["serial"]

    # Step 1: search the serial that was captured when the asset was registered
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot(f"HOFIN asset {serial} found")

    # Step 2: the row shows the values of the HOFIN asset
    asset_serial_global_list_page.verify_row_shows(serial, {**data.PROFILE_ROW, "serial": serial})


@pytest.mark.regression
def test_hofin_asset_popup_shows_its_data(page, asset_serial_global_list_page, hofin_normal_asset, take_screenshot):
    """Asset Profile Details (CR F01S01): the popup of a HOFIN asset shows its item, branch, project, price, value and statuses."""
    serial = hofin_normal_asset["serial"]

    # Step 1: open the popup of the asset
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    take_screenshot("asset profile details popup")

    # Step 2: the popup shows the asset's own values, with the Item Specification typed in HOFIN
    expected = {**data.PROFILE_POPUP, "assetSerial": serial, "itemSpecification": hofin_normal_asset["item_specification"]}
    asset_serial_global_list_page.verify_popup_fields(expected)
    asset_serial_global_list_page.close_popup()


@pytest.mark.regression
def test_hofin_asset_without_addition_has_empty_addition_history(
    page, asset_serial_global_list_page, hofin_normal_asset, take_screenshot
):
    """Asset Profile Details (CR F01S02): every parent asset has the Addition History tab, empty when nothing was added, and no Parent Asset field."""
    serial = hofin_normal_asset["serial"]

    # Step 1: open the popup of the asset
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)

    # Step 2: a parent asset has no Parent Asset field
    asset_serial_global_list_page.verify_popup_field_not_shown(data.PARENT_ASSET_FIELD, "only an extended asset has a Parent Asset")

    # Step 3: the Addition History tab is there, and it is empty
    asset_serial_global_list_page.verify_tab_shown("Addition History", True)
    asset_serial_global_list_page.get_tab_text("Addition History")
    take_screenshot("empty addition history")
    asset_serial_global_list_page.verify_addition_history_empty()
    asset_serial_global_list_page.close_popup()


# ---------------------------------------------------------------------------
# 2. A parent asset with extended assets
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_each_addition_is_a_separate_listed_asset(
    page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot
):
    """Asset Serial Global List (CR F01S01): each addition is a standalone asset '<parent serial>-1', '-2', ..., with a unique serial, found on its own."""
    pair = hofin_parent_with_extended

    # Step 1: the extended serials are the parent's serial plus -1, -2 in the order added
    asset_serial_global_list_page.verify_extended_serial_format(pair["parent"], pair["extended"])

    # Step 2: each extended asset is found on its own, UNASSIGNED and IN_USE
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_listed_on_their_own(pair["extended"], "UNASSIGNED", "IN_USE")
    take_screenshot(f"extended asset {pair['extended'][-1]} found")

    # Step 3: the parent is still listed as a parent asset of its own
    asset_serial_global_list_page.verify_listed_on_their_own([pair["parent"]], "UNASSIGNED", "IN_USE")


@pytest.mark.regression
def test_extended_asset_popup_shows_its_parent(page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot):
    """Asset Profile Details (CR F01S02): an extended asset shows its parent in the Parent Asset field and has no Addition History tab."""
    pair = hofin_parent_with_extended

    # Step 1: every extended asset's popup names the parent and has no Addition History tab
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_extended_asset_popups(pair["extended"], pair["parent"])

    # Step 2: the first extended asset has its own item, price and value
    asset_serial_global_list_page.search_by_serial(pair["extended"][0])
    asset_serial_global_list_page.open_asset_popup(pair["extended"][0])
    take_screenshot("extended asset popup")
    asset_serial_global_list_page.verify_popup_fields({**data.PROFILE_POPUP, data.PARENT_ASSET_FIELD: pair["parent"]})
    asset_serial_global_list_page.close_popup()


@pytest.mark.regression
def test_parent_is_not_changed_by_the_additions(page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot):
    """Asset Serial Global List (CR F01S01): additions do not change the parent: purchase value, WDV, remaining life and the other values stay as they were."""
    pair = hofin_parent_with_extended

    # Step 1: read the parent's values now, after the additions
    asset_serial_global_list_page.navigate_here()
    after = asset_serial_global_list_page.read_popup_fields(pair["parent"], data.PARENT_UNCHANGED_FIELDS)
    take_screenshot("parent after the additions")

    # Step 2: they are the values read right after the parent was registered
    assert after == pair["parent_details"], (
        f"The parent {pair['parent']} changed after the additions. "
        f"Before: {pair['parent_details']} After: {after}"
    )


@pytest.mark.smoke
@pytest.mark.regression
def test_addition_history_lists_every_extended_asset(
    page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot
):
    """Addition History (CR F01S02): the parent's tab lists each extended asset with its Asset Serial, Addition Amount, Addition Date, Reference Number, Item Name, Acc. Depreciation and WDV."""
    pair = hofin_parent_with_extended

    # Step 1: open the parent's Addition History tab
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.open_addition_history(pair["parent"])
    take_screenshot("addition history of the parent")

    # Step 2: the grid has the CR's columns (and the two impairment columns of the screen)
    headings = asset_serial_global_list_page.read_addition_history_headings()
    assert headings == data.ADDITION_HISTORY_HEADINGS, f"Expected columns {data.ADDITION_HISTORY_HEADINGS} but found {headings}."

    # Step 3: one row per extended asset, with the price, the business date, the item and a JV number
    expected = {
        "Addition Amount": data.UNIT_PRICE,
        "Addition Date": pair["parent_details"]["registrationDate"],
        "Item Name": data.ASSET_ITEM_NAME,
    }
    asset_serial_global_list_page.verify_addition_history_rows(pair["extended"], expected, data.REFERENCE_NUMBER_PREFIX)
    asset_serial_global_list_page.close_popup()


@pytest.mark.regression
def test_addition_history_depreciation_and_wdv_are_the_extended_assets(
    page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot
):
    """Addition History (CR F01S02): Acc. Depreciation and WDV of a row are the extended asset's own Accumulated Depreciation and Net Book Value/WDV."""
    pair = hofin_parent_with_extended
    extended = pair["extended"][0]

    # Step 1: read the extended asset's own values from its popup
    asset_serial_global_list_page.navigate_here()
    own = asset_serial_global_list_page.read_popup_fields(extended, ["totalDepCalculated", "netAssetValue"])

    # Step 2: read its row in the parent's Addition History
    row = asset_serial_global_list_page.read_addition_history_row(pair["parent"], extended)
    take_screenshot("addition history row read")

    # Step 3: the row shows the same Accumulated Depreciation and WDV as the asset itself
    assert float(row["Acc. Depreciation"]) == float(own["totalDepCalculated"]), (
        f"Acc. Depreciation of {extended} in the Addition History is {row['Acc. Depreciation']} but its popup shows {own['totalDepCalculated']}."
    )
    assert float(row["WDV"]) == float(own["netAssetValue"]), (
        f"WDV of {extended} in the Addition History is {row['WDV']} but its popup shows Net Book Value/WDV {own['netAssetValue']}."
    )


@pytest.mark.regression
def test_addition_history_records_per_page_and_entries(
    page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot
):
    """Addition History (CR F01S02): Records per page offers 10, 20, 50 and 100 with 10 chosen, and the entries text shows the range of rows."""
    pair = hofin_parent_with_extended
    count = len(pair["extended"])

    # Step 1: open the parent's Addition History tab
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.open_addition_history(pair["parent"])
    take_screenshot("records per page and entries")

    # Step 2: the Records per page choices, and the one chosen
    options = asset_serial_global_list_page.get_records_per_page_options()
    assert options == data.RECORDS_PER_PAGE_OPTIONS, f"Expected Records per page {data.RECORDS_PER_PAGE_OPTIONS} but found {options}."
    selected = asset_serial_global_list_page.get_selected_records_per_page()
    assert selected == data.DEFAULT_RECORDS_PER_PAGE, f"Expected {data.DEFAULT_RECORDS_PER_PAGE} records per page but {selected} is chosen."

    # Step 3: the entries text counts the extended assets
    entries = asset_serial_global_list_page.get_addition_history_entries_text()
    assert entries == f"Showing 1 to {count} of {count} entries", f"Unexpected entries text: '{entries}'"
    asset_serial_global_list_page.close_popup()


@pytest.mark.regression
def test_addition_history_serial_opens_the_extended_asset(
    page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot
):
    """Addition History (CR F01S02): the Asset Serial link opens the extended asset's popup over the parent's; closing it shows the parent's popup again."""
    pair = hofin_parent_with_extended

    # Step 1: open the parent's Addition History and click the first extended serial
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.open_addition_history(pair["parent"])
    asset_serial_global_list_page.open_extended_from_addition_history(pair["extended"][0])
    take_screenshot("extended asset opened from the addition history")

    # Step 2: closing the extended asset's popup shows the parent's popup again
    asset_serial_global_list_page.close_popup_back_to(pair["parent"])
    take_screenshot("back on the parent popup")
    asset_serial_global_list_page.close_popup()


@pytest.mark.regression
def test_hofin_addition_search_offers_parent_assets_only(hofin_flow, hofin_parent_with_extended):
    """HOFIN Fixed Asset Details (CR F01S01): the Fixed Asset Serial No search of an addition offers the parent, never an extended asset."""
    pair = hofin_parent_with_extended
    extended = pair["extended"][0]

    # Step 1: in HOFIN, search the parent's serial and then an extended serial (the bill is not submitted)
    options = hofin_flow.read_addition_search_options([pair["parent"], extended])

    # Step 2: the parent is offered, without its extended assets
    assert pair["parent"] in options[pair["parent"]], f"Searching {pair['parent']} should offer it but offers {options[pair['parent']]}."
    assert extended not in options[pair["parent"]], f"Searching {pair['parent']} should not offer {extended}: {options[pair['parent']]}"

    # Step 3: an extended asset cannot be chosen as the parent of an addition
    assert extended not in options[extended], f"Searching {extended} should offer no extended asset but offers {options[extended]}."


# ---------------------------------------------------------------------------
# 3. A new addition, stage by stage (adds one more extended asset to the parent)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_addition_is_listed_only_after_acknowledge_and_approve(
    page, asset_serial_global_list_page, hofin_flow, hofin_assets, hofin_parent_with_extended, take_screenshot
):
    """Asset Serial Global List (CR F01S02 pre-condition): a new addition is not listed while it waits for HOFA acknowledgement or HOFIN approval, and is listed after the approval."""
    pair = hofin_parent_with_extended
    next_serial = f"{pair['parent']}-{len(pair['extended']) + 1}"

    # Step 1: the HOFIN creator submits an addition to the parent
    transaction_no = hofin_flow.create_bill(unique_name("ADD"), pair["parent"], unique_name(data.ITEM_SPECIFICATION))

    # Step 2: waiting for the HOFA acknowledgement, the new serial is not listed
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(next_serial)
    asset_serial_global_list_page.verify_serial_not_listed(next_serial)

    # Step 3: acknowledged in HOFA, waiting for the HOFIN approval, it is still not listed
    # (the acknowledger's log-out also ends this tab's session; opening the menu signs in again)
    hofin_flow.acknowledge(transaction_no)
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(next_serial)
    asset_serial_global_list_page.verify_serial_not_listed(next_serial)

    # Step 4: approved in HOFIN, it is listed as a new extended asset
    hofin_flow.approve(transaction_no)
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(next_serial)
    take_screenshot(f"new extended asset {next_serial} listed after approval")
    asset_serial_global_list_page.verify_statuses(next_serial, "UNASSIGNED", "IN_USE")
    hofin_assets.remember_new_extended(pair, next_serial)


# ---------------------------------------------------------------------------
# 4. Utilization Status of a parent and its extended assets (sets DAMAGE)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_extended_asset_utilization_status_changes_alone(
    page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot
):
    """Asset Profile Details (CR F01S02): an extended asset's Utilization Status can be changed on its own; the parent and the other extended assets keep theirs."""
    pair = hofin_parent_with_extended
    changed = pair["extended"][-1]

    # Step 1: set the last extended asset to DAMAGE
    asset_serial_global_list_page.change_utilization_status(changed, data.DAMAGE, data.STATUS_NOTE)

    # Step 2: only that extended asset is DAMAGE
    expected = {pair["parent"]: "IN_USE", pair["extended"][0]: "IN_USE", changed: data.DAMAGE}
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_utilization_statuses(expected)
    take_screenshot("only the extended asset is damaged")


@pytest.mark.regression
def test_parent_utilization_status_is_copied_to_extended_assets(
    page, asset_serial_global_list_page, hofin_parent_with_extended, take_screenshot
):
    """Asset Profile Details (CR F01S02): changing the parent's Utilization Status sets the same status on all its extended assets."""
    pair = hofin_parent_with_extended

    # Step 1: set the parent to DAMAGE
    asset_serial_global_list_page.change_utilization_status(pair["parent"], data.DAMAGE, data.STATUS_NOTE)

    # Step 2: the parent and every extended asset are DAMAGE
    expected = {pair["parent"]: data.DAMAGE}
    for serial in pair["extended"]:
        expected[serial] = data.DAMAGE
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.verify_utilization_statuses(expected)
    take_screenshot("parent and extended assets damaged")
