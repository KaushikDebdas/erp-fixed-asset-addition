"""
test_04_asset_serial_global_list.py: tests for the Asset Serial Global List
screen (Fixed Asset > Asset Profile > Asset Serial Global List) and its
Asset Profile Details popup.

Built from automation/element_catalog/asset_serial_global_list.md and
asset_profile_reference_values.md. The tests use a freshly approved Land
asset (see the `profile_assets` fixture in conftest.py). The whole file
logs in once and every test reuses that session.

Nothing is saved: the Update buttons are only clicked with a missing value to
read the validation message, and the popups are closed afterwards.
"""
import pytest

from utils.run_context import trace_one_test

TAB_NAMES = [
    "Details",
    "Depreciation History",
    "Revaluation History",
    "Transaction History",
    "Expenditure",
    "Disposal Info",
    "Attachment",
]
UTILIZATION_STATUS_OPTIONS = [
    "Select Status",
    "SPLIT",
    "IN_USE",
    "DAMAGE",
    "STOLEN",
    "BURNED",
    "DONATED",
    "OFFLINE_TRANSFER",
    "UNDER_REPAIR",
]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_global_list_search_by_serial(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: searching an Asset Serial finds the asset with its statuses."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the Asset Serial Global List
    asset_serial_global_list_page.navigate_here()

    # Step 2: search by the Asset Serial
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot(f"asset {serial} found")

    # Step 3: the asset is listed, in use and not assigned to anyone
    assert asset_serial_global_list_page.is_serial_listed(serial)
    assert asset_serial_global_list_page.get_utilization_status(serial) == "IN_USE"
    assert asset_serial_global_list_page.get_assign_status(serial) == "UNASSIGNED"


@pytest.mark.regression
def test_global_list_grid_columns(page, asset_serial_global_list_page, take_screenshot):
    """Asset Serial Global List: the results grid shows the documented columns."""
    # Step 1: open the Asset Serial Global List
    asset_serial_global_list_page.navigate_here()
    take_screenshot("asset serial global list opened")

    # Step 2: the column headings
    assert asset_serial_global_list_page.get_grid_headers() == [
        "SL",
        "Asset Serial",
        "Asset Item Name",
        "Sub Category",
        "Category Name",
        "Group Name",
        "Project Name",
        "Department",
        "Assign Status",
        "Utilization Status",
    ]


@pytest.mark.regression
def test_global_list_filter_by_utilization_status(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: the Utilization Status filter keeps only matching assets."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the list and filter by the status the asset really has
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.filter_by_utilization_status("IN_USE")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by IN_USE")
    assert asset_serial_global_list_page.is_serial_listed(serial)

    # Step 2: filter by a status the asset does not have
    asset_serial_global_list_page.filter_by_utilization_status("DAMAGE")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by DAMAGE")
    assert not asset_serial_global_list_page.is_serial_listed(serial)


@pytest.mark.regression
def test_global_list_filter_by_assign_status(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: the Assign Status filter keeps only matching assets."""
    serial = profile_assets["land"]["serial"]

    # Step 1: the new asset is UNASSIGNED, so it shows under UNASSIGNED
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.filter_by_assign_status("UNASSIGNED")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by UNASSIGNED")
    assert asset_serial_global_list_page.is_serial_listed(serial)

    # Step 2: and it does not show under ASSIGNED
    asset_serial_global_list_page.filter_by_assign_status("ASSIGNED")
    asset_serial_global_list_page.search_by_serial(serial)
    take_screenshot("filtered by ASSIGNED")
    assert not asset_serial_global_list_page.is_serial_listed(serial)


@pytest.mark.smoke
@pytest.mark.regression
def test_global_list_popup_details(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: the popup shows the details entered at registration, including the Measurement."""
    asset = profile_assets["land"]

    # Step 1: find the asset and open its popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(asset["serial"])
    asset_serial_global_list_page.open_asset_popup(asset["serial"])
    take_screenshot("asset profile details popup opened")

    # Step 2: the details match what was registered
    popup = asset_serial_global_list_page
    assert popup.get_popup_value("assetSerial") == asset["serial"]
    assert popup.get_popup_value("registrationNumber") == asset["registration_number"]
    assert popup.get_popup_value("assetName") == "Land"
    assert popup.get_popup_value("projectName") == "Microfinance (Dabi)"
    assert popup.get_popup_value("utilizationStatusName") == "IN_USE"
    assert popup.get_popup_value("measurement") == "12.50"
    assert popup.get_popup_value("measurementUnit") == "Decimal"
    assert popup.get_popup_value("netAssetValue") == "25000.00"


@pytest.mark.regression
def test_global_list_popup_tabs(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: the popup has seven tabs and a new asset has no history yet."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the asset popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)

    # Step 2: the seven tabs, in order
    assert asset_serial_global_list_page.get_tab_names() == TAB_NAMES

    # Step 3: a new asset has no depreciation, revaluation, transaction, expenditure or disposal history
    for tab_name in [
        "Depreciation History",
        "Revaluation History",
        "Transaction History",
        "Expenditure",
        "Disposal Info",
    ]:
        tab_text = asset_serial_global_list_page.get_tab_text(tab_name)
        assert "No data available in table" in tab_text, f"{tab_name} tab text: {tab_text}"
    take_screenshot("history tabs checked")

    # Step 4: and no attachment
    assert "No Attachment" in asset_serial_global_list_page.get_tab_text("Attachment")


@pytest.mark.regression
def test_global_list_source_of_fund_values(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: the Source Of Fund Change popup offers the list of funds."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the asset popup and click Change next to Source Of Fund
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_source_of_fund_change()
    take_screenshot("source of fund change popup")

    # Step 2: the drop-down starts with its placeholder and holds the funds
    options = asset_serial_global_list_page.get_source_of_fund_options()
    assert options[0] == "-Select Source of Fund-"
    assert "Dutch Embassy" in options
    assert "BRAC" in options
    assert len(options) > 100, f"Expected the full list of funds but found {len(options)} values."

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_source_of_fund_requires_selection(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: Update in the Source Of Fund popup is refused until a fund is selected."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the Source Of Fund popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_source_of_fund_change()

    # Step 2: Update with nothing selected shows a message and saves nothing
    toast = asset_serial_global_list_page.click_source_of_fund_update_and_get_toast()
    take_screenshot("source of fund update refused")
    assert toast == "Please select a Source Of Fund.", f"Unexpected toast: '{toast}'"

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_utilization_status_values(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: the Utilization Status Change popup offers the eight statuses."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the asset popup and click Change next to Asset Utilization Status
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_status_change()
    take_screenshot("utilization status change popup")

    # Step 2: the drop-down holds the eight statuses and starts on the asset's current one
    assert asset_serial_global_list_page.get_status_options() == UTILIZATION_STATUS_OPTIONS
    assert asset_serial_global_list_page.get_selected_status() == "IN_USE"

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_status_change_requires_note(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: a Utilization Status change is refused without a Note."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the Utilization Status popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_status_change()

    # Step 2: Update with an empty Note shows a message and saves nothing
    toast = asset_serial_global_list_page.click_status_update_with_empty_note_and_get_toast()
    take_screenshot("status update refused without note")
    assert toast == "Please add a note.", f"Unexpected toast: '{toast}'"

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_item_change_requires_specification(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: an Item change is refused without a new Specification/IMEI/SL No."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the Item popup
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    asset_serial_global_list_page.open_item_change()

    # Step 2: Update with an empty box shows a message and saves nothing
    toast = asset_serial_global_list_page.click_item_update_with_empty_specification_and_get_toast()
    take_screenshot("item update refused without specification")
    assert toast == "Please select a Item Specification/IMEI/SL No.", f"Unexpected toast: '{toast}'"

    # Step 3: close without saving
    asset_serial_global_list_page.close_change_popup()


@pytest.mark.regression
def test_global_list_measurement_change_unlocks_field(
    page, asset_serial_global_list_page, profile_assets, take_screenshot
):
    """Asset Serial Global List: Change next to Measurement makes the box editable and shows Update."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open the asset popup; Measurement is read-only at first
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(serial)
    asset_serial_global_list_page.open_asset_popup(serial)
    assert not asset_serial_global_list_page.is_measurement_editable()

    # Step 2: click Change; the box becomes editable and keeps its value
    asset_serial_global_list_page.unlock_measurement()
    take_screenshot("measurement unlocked")
    assert asset_serial_global_list_page.is_measurement_editable()
    assert asset_serial_global_list_page.get_popup_value("measurement") == "12.50"

    # Step 3: close the popup without saving
    asset_serial_global_list_page.close_popup()
