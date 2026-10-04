"""
test_06_asset_in_pending_process_list.py: tests for the Asset In Pending
Process List screen (Fixed Asset > Asset Profile > Asset In Pending Process
List).

Built from automation/element_catalog/asset_in_pending_process_list.md. The
whole file logs in once and every test reuses that session. The tests only
read the list and download its Excel export; they change nothing.
"""
import openpyxl
import pytest

from utils.run_context import trace_one_test

GRID_COLUMNS = [
    "SL",
    "Asset Serial",
    "From Branch",
    "To Branch",
    "From Project",
    "From Department",
    "To Project",
    "To Department",
    "Asset Item Name",
    "Sub Category",
    "Category Name",
    "Group Name",
    "Status",
    "Pending in Feature",
    "Created By",
    "Creation Date",
    "Aging",
]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_pending_list_grid_columns(page, pending_process_list_page, take_screenshot):
    """Asset In Pending Process List: the grid shows the documented columns."""
    # Step 1: open the Asset In Pending Process List
    pending_process_list_page.navigate_here()
    take_screenshot("asset in pending process list opened")

    # Step 2: the column headings
    assert pending_process_list_page.get_grid_headers() == GRID_COLUMNS


@pytest.mark.regression
def test_pending_list_unknown_serial_shows_no_data(
    page, pending_process_list_page, take_screenshot
):
    """Asset In Pending Process List: an Asset Serial that is not pending shows the empty message."""
    # Step 1: open the list and search a well-formed serial that does not exist
    pending_process_list_page.navigate_here()
    pending_process_list_page.search_by_serial("BBDASR99999999")
    take_screenshot("no data for unknown serial")

    # Step 2: no rows are shown
    assert not pending_process_list_page.has_data_rows()


@pytest.mark.regression
def test_pending_list_new_approved_asset_is_not_pending(
    page, pending_process_list_page, profile_assets, take_screenshot
):
    """Asset In Pending Process List: a freshly approved asset is not in any pending process."""
    serial = profile_assets["land"]["serial"]

    # Step 1: search for the new asset
    pending_process_list_page.navigate_here()
    pending_process_list_page.search_by_serial(serial)
    take_screenshot(f"search for {serial}")

    # Step 2: it is not listed, because nothing is pending for it
    assert not pending_process_list_page.has_data_rows()


@pytest.mark.regression
def test_pending_list_status_filter(page, pending_process_list_page, take_screenshot):
    """Asset In Pending Process List: the Status filter keeps only rows with that Status."""
    # Step 1: open the list and filter by Status APPROVED
    pending_process_list_page.navigate_here()
    pending_process_list_page.filter_by_status("APPROVED")
    take_screenshot("filtered by approved status")
    if not pending_process_list_page.has_data_rows():
        pytest.skip("No pending rows with Status APPROVED on this environment right now.")

    # Step 2: every row shown has that Status
    statuses = pending_process_list_page.get_visible_statuses()
    assert statuses, "Expected at least one row."
    assert set(statuses) == {"APPROVED"}, f"Found other statuses: {set(statuses)}"


@pytest.mark.regression
def test_pending_list_export_downloads_excel(
    page, pending_process_list_page, tmp_path, take_screenshot
):
    """Asset In Pending Process List: Export downloads an Excel file with the grid's columns."""
    # Step 1: open the list
    pending_process_list_page.navigate_here()
    take_screenshot("asset in pending process list opened")

    # Step 2: click Export and keep the downloaded file
    saved_file = str(tmp_path / "pending_export.xlsx")
    file_name = pending_process_list_page.export_to_file(saved_file)
    assert file_name == "Asset In Pending Process List.xlsx"

    # Step 3: the first row of the file holds the same column names as the grid
    sheet = openpyxl.load_workbook(saved_file).active
    header_row = [cell.value for cell in sheet[1]]
    assert header_row == GRID_COLUMNS
