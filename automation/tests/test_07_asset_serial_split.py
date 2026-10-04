"""
test_07_asset_serial_split.py: tests for the Asset Serial Split screen (Fixed
Asset > Asset Profile > Asset Serial Split) and its Asset Split form.

Built from automation/element_catalog/asset_serial_split.md. The tests use two
freshly approved assets (see the `profile_assets` fixture in conftest.py): a
Land asset with a Measurement, and a plain asset without one. The whole file
logs in once and every test reuses that session.

The Split button is never clicked: splitting creates new asset serials that
cannot be undone.
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_split_search_shows_split_button(
    page, asset_serial_split_page, profile_assets, take_screenshot
):
    """Asset Serial Split: searching an Asset Serial lists the asset with a SPLIT button."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open Asset Serial Split
    asset_serial_split_page.navigate_here()

    # Step 2: search by the Asset Serial
    asset_serial_split_page.search_by_serial(serial)
    take_screenshot(f"asset {serial} found")

    # Step 3: the row has a SPLIT button
    assert asset_serial_split_page.has_split_button(serial)


@pytest.mark.regression
def test_split_grid_columns(page, asset_serial_split_page, take_screenshot):
    """Asset Serial Split: the results grid shows the documented columns."""
    # Step 1: open Asset Serial Split
    asset_serial_split_page.navigate_here()
    take_screenshot("asset serial split opened")

    # Step 2: the column headings
    assert asset_serial_split_page.get_grid_headers() == [
        "SL",
        "Asset Serial",
        "Asset Item Name",
        "Sub Category",
        "Category Name",
        "Group Name",
        "Project Name",
        "Department Name",
        "Assign Status",
        "Action",
    ]


@pytest.mark.regression
def test_split_refused_without_measurement(
    page, asset_serial_split_page, profile_assets, take_screenshot
):
    """Asset Serial Split: an asset with no Measurement cannot be split."""
    serial = profile_assets["plain"]["serial"]

    # Step 1: find the asset that has no measurement
    asset_serial_split_page.navigate_here()
    asset_serial_split_page.search_by_serial(serial)

    # Step 2: click SPLIT; a message says a measurement above zero is needed
    toast = asset_serial_split_page.click_split_and_get_toast(serial)
    take_screenshot("split refused without measurement")
    assert toast == "Cannot split: Please set a valid measurement above zero.", (
        f"Unexpected toast: '{toast}'"
    )


@pytest.mark.regression
def test_split_form_opens_for_asset_with_measurement(
    page, asset_serial_split_page, profile_assets, take_screenshot
):
    """Asset Serial Split: an asset with a Measurement opens the Asset Split form showing its details."""
    serial = profile_assets["land"]["serial"]

    # Step 1: find the Land asset and click SPLIT
    asset_serial_split_page.navigate_here()
    asset_serial_split_page.search_by_serial(serial)
    asset_serial_split_page.open_split_form(serial)
    take_screenshot("asset split form opened")

    # Step 2: the form shows the asset's details, read-only
    form = asset_serial_split_page
    assert form.get_form_value("assetSerial") == serial
    assert form.get_form_value("assetName") == "Land"
    assert form.get_form_value("measurementFront") == "12.50"
    assert form.get_form_value("netAssetValue") == "25000.00"
    assert form.get_form_value("accumulatedDepriciation") == "0.00"

    # Step 3: Split Into is empty and can be typed in, and the Split button is there
    assert form.is_split_into_editable()
    assert form.get_split_into_value() == ""
    assert form.is_split_button_visible()

    # Step 4: the result grid has its documented columns
    assert form.get_result_grid_headers() == [
        "SL",
        "Asset Item Name",
        "Item Specification",
        "Sub Category",
        "Category Name",
        "Group Name",
        "Measurement Unit",
        "Percentage",
        "Written Down Value",
        "Acc. Depreciation",
        "Measurement",
    ]

    # Step 5: leave the form without splitting
    form.go_back()
