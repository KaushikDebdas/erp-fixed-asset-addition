"""
test_08_asset_serial_split_list.py: tests for the Asset Serial Split List
screen (Fixed Asset > Asset Profile > Asset Serial Split List).

Built from automation/element_catalog/asset_serial_split_list.md. The whole
file logs in once and every test reuses that session. The tests only read the
list; they change nothing.
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_split_list_grid_columns(page, asset_split_list_page, take_screenshot):
    """Asset Serial Split List: the grid shows the documented columns."""
    # Step 1: open the Asset Serial Split List
    asset_split_list_page.navigate_here()
    take_screenshot("asset serial split list opened")

    # Step 2: the column headings
    assert asset_split_list_page.get_grid_headers() == [
        "SL",
        "Asset Split No.",
        "Asset Group",
        "Project Name",
        "Department Name",
        "Asset Serial No.",
        "Split Into",
        "Remarks",
        "Created By",
        "Status",
        "Approved By",
        "Approval Date",
    ]


@pytest.mark.regression
def test_split_list_unknown_serial_shows_no_data(
    page, asset_split_list_page, take_screenshot
):
    """Asset Serial Split List: an Asset Serial that was never split shows the empty message."""
    # Step 1: open the list and search a serial that cannot exist
    asset_split_list_page.navigate_here()
    asset_split_list_page.search_by_serial("NOSUCHSERIAL000")
    take_screenshot("no data for unknown serial")

    # Step 2: the grid shows the empty message
    assert "No data available in table" in asset_split_list_page.get_grid_text()


@pytest.mark.regression
def test_split_list_new_asset_has_no_split(
    page, asset_split_list_page, profile_assets, take_screenshot
):
    """Asset Serial Split List: a freshly approved asset that was not split is not listed."""
    serial = profile_assets["land"]["serial"]

    # Step 1: search for the new asset
    asset_split_list_page.navigate_here()
    asset_split_list_page.search_by_serial(serial)
    take_screenshot(f"search for {serial}")

    # Step 2: no split exists for it
    assert "No data available in table" in asset_split_list_page.get_grid_text()
