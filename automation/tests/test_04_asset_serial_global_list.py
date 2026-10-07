"""
test_04_asset_serial_global_list.py: tests for the Asset Serial Global
List screen (Fixed Asset > Asset Profile > Asset Serial Global List) and its
Asset Profile Details popup, using the 8 approved AAQ assets.

Built from automation/element_catalog/asset_serial_global_list.md and
asset_profile_reference_values.md. The assets are the ones approved by
test_03_asset_registration_approval_list.py; they are remembered, with
their Asset Serial, under AAQ_ASSET_GROUP (test_data/asset_registration_data.py).
When a test here runs on its own, the `registrations` fixture creates and
approves the asset it needs, so every test can run alone.

Every approved asset is checked against its own data: the grid row and the
popup must show its Asset Serial, registration number, item, categories,
project, status and values. The rest of the screen (filters, tabs, the Change
popups) is checked once, on one shared asset.

The whole file logs in once and every test reuses that session.
Nothing is saved: the Update buttons are only clicked with a missing value to
read the validation message, and the popups are closed afterwards.

The tests run top to bottom:
    1. Each approved asset: its grid row and its popup show its own data
    2. Search and filters
    3. The popup: tabs and history
    4. The Change popups: Source Of Fund, Utilization Status, Item, Measurement

To run part of the file:
    pytest tests/test_04_asset_serial_global_list.py -k "land"
"""
import pytest

from test_data.asset_registration_data import (
    AAQ_ASSET_GROUP,
    APPROVED_AAQ_ASSETS,
    build_asset_profile,
)
from test_data.toast_messages import (
    ITEM_SPECIFICATION_TOAST,
    NOTE_TOAST,
    SOURCE_OF_FUND_TOAST,
)
from utils.run_context import trace_one_test

# Messages (toasts) the screen shows

# The asset the tests share when they only need "an approved asset"
SHARED_ITEM = "land"
SHARED_SUB_TYPE = "spot"

# Column headings of the grid, in order
GRID_COLUMNS = [
    "SL", "Asset Serial", "Asset Item Name", "Sub Category", "Category Name",
    "Group Name", "Project Name", "Department", "Assign Status", "Utilization Status",
]

# The tabs of the popup, in order
TAB_NAMES = [
    "Details", "Depreciation History", "Revaluation History", "Transaction History",
    "Expenditure", "Disposal Info", "Attachment",
]

# The tabs that are empty for a new asset
EMPTY_HISTORY_TABS = [
    "Depreciation History", "Revaluation History", "Transaction History", "Expenditure", "Disposal Info",
]

# The values of the Utilization Status drop-down, placeholder first
UTILIZATION_STATUS_OPTIONS = [
    "Select Status", "SPLIT", "IN_USE", "DAMAGE", "STOLEN", "BURNED", "DONATED",
    "OFFLINE_TRANSFER", "UNDER_REPAIR",
]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. Each approved asset: its grid row and its popup show its own data
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
@APPROVED_AAQ_ASSETS
def test_global_list_row_shows_the_asset_data(
    item, sub_type, page, registrations, transactions, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: searching an Asset Serial lists that asset with its own item, categories, project and statuses."""
    # Step 1: get the approved asset (approved by an earlier test, or created and approved now)
    record = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)
    transactions.ensure_unassigned_if_saved_asset(item, sub_type)
    expected = build_asset_profile(record["data"], record["registration_number"], record["serial"])

    # Step 2: open the Asset Serial Global List and search its Asset Serial
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(record["serial"])
    take_screenshot(f"{sub_type} {item} asset {record['serial']} found")

    # Step 3: exactly this asset is listed, and its row shows its own data
    assert asset_serial_global_list_page.is_serial_listed(record["serial"]), (
        f"Expected Asset Serial '{record['serial']}' to be listed after searching it but it was not."
    )
    asset_serial_global_list_page.verify_row_shows(record["serial"], expected)


@pytest.mark.regression
@APPROVED_AAQ_ASSETS
def test_global_list_popup_shows_the_asset_data(
    item, sub_type, page, registrations, transactions, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: the popup shows the asset's registration number, categories, project, measurement and value."""
    # Step 1: get the approved asset
    record = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)
    transactions.ensure_unassigned_if_saved_asset(item, sub_type)
    expected = build_asset_profile(record["data"], record["registration_number"], record["serial"])

    # Step 2: find the asset and open its popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(record["serial"])
    asset_serial_global_list_page.open_asset_popup(record["serial"])
    take_screenshot(f"{sub_type} {item} popup of {record['serial']}")

    # Step 3: the popup shows what was registered and what approval created
    asset_serial_global_list_page.verify_popup_shows(expected)


# ---------------------------------------------------------------------------
# 2. Search and filters
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_global_list_grid_columns(page, asset_serial_global_list_page, take_screenshot):
    """Asset Serial Global List: the results grid shows the documented columns."""
    # Step 1: open the Asset Serial Global List
    asset_serial_global_list_page.navigate_here()
    take_screenshot("asset serial global list opened")

    # Step 2: the column headings
    found_headers = asset_serial_global_list_page.get_grid_headers()
    assert found_headers == GRID_COLUMNS, f"Expected grid columns {GRID_COLUMNS} but found {found_headers}."


@pytest.mark.regression
def test_global_list_unknown_serial_lists_nothing(page, asset_serial_global_list_page, take_screenshot):
    """Asset Serial Global List: an Asset Serial that does not exist lists no asset."""
    # Step 1: open the list and search a well-formed serial that does not exist
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial("BBDASR99999999")
    take_screenshot("unknown serial searched")

    # Step 2: it is not listed
    assert not asset_serial_global_list_page.is_serial_listed("BBDASR99999999"), (
        "Expected Asset Serial 'BBDASR99999999' not to be listed but it was."
    )


@pytest.mark.regression
def test_global_list_filter_by_utilization_status(
    page, registrations, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: the Utilization Status filter keeps only matching assets."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: filter by the status the asset really has (IN_USE); it is listed
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.filter_by_utilization_status("IN_USE")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by IN_USE")
    assert asset_serial_global_list_page.is_serial_listed(serial), (
        f"Expected Asset Serial '{serial}' to be listed under Utilization Status IN_USE but it was not."
    )

    # Step 2: filter by a status it does not have (DAMAGE); it is not listed
    asset_serial_global_list_page.filter_by_utilization_status("DAMAGE")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by DAMAGE")
    assert not asset_serial_global_list_page.is_serial_listed(serial), (
        f"Expected Asset Serial '{serial}' not to be listed under Utilization Status DAMAGE but it was."
    )


@pytest.mark.regression
def test_global_list_filter_by_assign_status(
    page, registrations, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: the Assign Status filter keeps only matching assets."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: the asset is UNASSIGNED, so it shows under UNASSIGNED
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.filter_by_assign_status("UNASSIGNED")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by UNASSIGNED")
    assert asset_serial_global_list_page.is_serial_listed(serial), (
        f"Expected Asset Serial '{serial}' to be listed under Assign Status UNASSIGNED but it was not."
    )

    # Step 2: and it does not show under ASSIGNED
    asset_serial_global_list_page.filter_by_assign_status("ASSIGNED")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by ASSIGNED")
    assert not asset_serial_global_list_page.is_serial_listed(serial), (
        f"Expected Asset Serial '{serial}' not to be listed under Assign Status ASSIGNED but it was."
    )


# ---------------------------------------------------------------------------
# 3. The popup: tabs and history
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_global_list_popup_tabs(page, registrations, asset_serial_global_list_page, take_screenshot):
    """Asset Serial Global List: the popup has seven tabs and a new asset has no history yet."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: open the asset popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)

    # Step 2: the seven tabs, in order
    found_tabs = asset_serial_global_list_page.get_tab_names()
    assert found_tabs == TAB_NAMES, f"Expected popup tabs {TAB_NAMES} but found {found_tabs}."

    # Step 3: a new asset has no depreciation, revaluation, transaction, expenditure or disposal history
    for tab_name in EMPTY_HISTORY_TABS:
        tab_text = asset_serial_global_list_page.get_tab_text(tab_name)
        assert "No data available in table" in tab_text, f"{tab_name} tab text: {tab_text}"
    take_screenshot("history tabs checked")

    # Step 4: and no attachment
    attachment_text = asset_serial_global_list_page.get_tab_text("Attachment")
    assert "No Attachment" in attachment_text, f"Expected the Attachment tab to say 'No Attachment' but it showed '{attachment_text}'."


# ---------------------------------------------------------------------------
# 4. The Change popups (nothing is saved)
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_global_list_source_of_fund_values(page, registrations, asset_serial_global_list_page, take_screenshot):
    """Asset Serial Global List: the Source Of Fund Change popup offers the list of funds."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: open the asset popup and click Change next to Source Of Fund
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_source_of_fund_change()
    take_screenshot("source of fund change popup")

    # Step 2: the drop-down starts with its placeholder and holds the funds
    options = asset_serial_global_list_page.get_source_of_fund_options()
    assert options[0] == "-Select Source of Fund-", (
        f"Expected the first Source of Fund value to be '-Select Source of Fund-' but found '{options[0]}'."
    )
    assert "Dutch Embassy" in options, f"Expected 'Dutch Embassy' in the Source of Fund list but it was not found among {len(options)} values."
    assert "BRAC" in options, f"Expected 'BRAC' in the Source of Fund list but it was not found among {len(options)} values."
    assert len(options) > 100, f"Expected the full list of funds but found {len(options)} values."

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_source_of_fund_requires_selection(
    page, registrations, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: Update in the Source Of Fund popup is refused until a fund is selected."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: open the Source Of Fund popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_source_of_fund_change()

    # Step 2: Update with nothing selected shows a message and saves nothing
    toast = asset_serial_global_list_page.click_source_of_fund_update_and_get_toast()
    take_screenshot("source of fund update refused")
    asset_serial_global_list_page.verify_toast_text(toast, SOURCE_OF_FUND_TOAST, "click source of fund update")

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_utilization_status_values(
    page, registrations, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: the Utilization Status Change popup offers the eight statuses."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: open the asset popup and click Change next to Asset Utilization Status
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_status_change()
    take_screenshot("utilization status change popup")

    # Step 2: the drop-down holds the eight statuses and starts on the asset's current one
    found_options = asset_serial_global_list_page.get_status_options()
    assert found_options == UTILIZATION_STATUS_OPTIONS, (
        f"Expected Utilization Status values {UTILIZATION_STATUS_OPTIONS} but found {found_options}."
    )
    selected_status = asset_serial_global_list_page.get_selected_status()
    assert selected_status == "IN_USE", f"Expected the selected Utilization Status 'IN_USE' but found '{selected_status}'."

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_status_change_requires_note(
    page, registrations, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: a Utilization Status change is refused without a Note."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: open the Utilization Status popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_status_change()

    # Step 2: Update with an empty Note shows a message and saves nothing
    toast = asset_serial_global_list_page.click_status_update_with_empty_note_and_get_toast()
    take_screenshot("status update refused without note")
    asset_serial_global_list_page.verify_toast_text(toast, NOTE_TOAST, "click status update with empty note")

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_item_change_requires_specification(
    page, registrations, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: an Item change is refused without a new Specification/IMEI/SL No."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: open the Item popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_item_change()

    # Step 2: Update with an empty box shows a message and saves nothing
    toast = asset_serial_global_list_page.click_item_update_with_empty_specification_and_get_toast()
    take_screenshot("item update refused without specification")
    asset_serial_global_list_page.verify_toast_text(toast, ITEM_SPECIFICATION_TOAST, "click item update with empty specification")

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_measurement_change_unlocks_field(
    page, registrations, asset_serial_global_list_page, take_screenshot
):
    """Asset Serial Global List: Change next to Measurement makes the box editable and keeps its value."""
    record = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)
    expected = build_asset_profile(record["data"], record["registration_number"], record["serial"])

    # Step 1: open the asset popup; Measurement is read-only at first
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(record["serial"])
    asset_serial_global_list_page.open_asset_popup(record["serial"])
    assert not asset_serial_global_list_page.is_measurement_editable(), (
        "Expected the Measurement box to be read-only when the popup opens but it was editable."
    )

    # Step 2: click Change; the box becomes editable and keeps the registered value
    asset_serial_global_list_page.unlock_measurement()
    take_screenshot("measurement unlocked")
    assert asset_serial_global_list_page.is_measurement_editable(), (
        "Expected the Measurement box to be editable after clicking Change but it was read-only."
    )
    found_measurement = asset_serial_global_list_page.get_popup_value("measurement")
    assert found_measurement == expected["measurement"], (
        f"Expected Measurement '{expected['measurement']}' but found '{found_measurement}'."
    )
