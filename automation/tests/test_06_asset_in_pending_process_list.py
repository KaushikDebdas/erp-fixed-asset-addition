"""
test_06_asset_in_pending_process_list.py: tests for the Asset In Pending
Process List screen (Fixed Asset > Asset Profile > Asset In Pending Process
List), using an approved asset of the asset slots.

Built from automation/element_catalog/asset_in_pending_process_list.md. The
asset is the one approved by test_03_asset_registration_approval_list.py (slot
usage_a); it is remembered, with its Asset Serial, under its slot name. When a
test here runs on its own, the `registrations` fixture creates and approves the
asset it needs, so every test can run alone.

The list shows assets that are in the middle of a process (an assignment, a
transfer, a challan, ...). A freshly approved asset has no process, so it may
not be in it (this file runs before any flow uses the asset). A row that is in the list is checked by searching its
own Asset Serial again. Nothing is changed or saved: the tests only read the
list and download its Excel export.

The whole file logs in once and every test reuses that session.

The tests run top to bottom:
    1. A freshly approved asset is not in the list
    2. The page: columns, search and filters
    3. A row of the list is found again by its own Asset Serial
    4. Export to Excel

To run part of the file:
    pytest tests/test_06_asset_in_pending_process_list.py -k "approved_asset"
"""
import openpyxl
import pytest

from utils.run_context import trace_one_test

# The slot whose asset must not be in a pending process
CHECKED_SLOT = "usage_a"

# Column headings of the grid, in order
GRID_COLUMNS = [
    "SL", "Asset Serial", "From Branch", "To Branch", "From Project", "From Department",
    "To Project", "To Department", "Asset Item Name", "Sub Category", "Category Name",
    "Group Name", "Status", "Pending in Feature", "Created By", "Creation Date", "Aging",
]

# The columns whose value must be the same when a row is searched again by its serial
COLUMNS_THAT_MUST_MATCH = ["Asset Item Name", "Group Name", "Status", "Pending in Feature"]

# The name the downloaded Excel file gets
EXPORT_FILE_NAME = "Asset In Pending Process List.xlsx"


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. A freshly approved asset is not in the list
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_pending_list_does_not_hold_an_approved_asset(
    page, registrations, pending_process_list_page, take_screenshot
):
    """Asset In Pending Process List: a freshly approved asset is in no pending process, so it is not listed."""
    # Step 1: get the approved asset (approved by an earlier test, or created and approved now)
    serial = registrations.get_approved_of(CHECKED_SLOT)["serial"]

    # Step 2: open the list and search its Asset Serial
    pending_process_list_page.navigate_here()
    pending_process_list_page.search_serial_and_wait_for_result(serial)
    take_screenshot(f"asset {serial} searched")

    # Step 3: no row has this serial, because nothing is pending for it
    pending_process_list_page.verify_serial_is_not_pending(serial)


# ---------------------------------------------------------------------------
# 2. The page: columns, search and filters
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_pending_list_columns_and_unknown_serial(page, pending_process_list_page, take_screenshot):
    """Asset In Pending Process List: the grid shows the documented columns, and an unknown Asset Serial shows the empty message."""
    # Step 1: open the Asset In Pending Process List
    pending_process_list_page.navigate_here()
    take_screenshot("asset in pending process list opened")

    # Step 2: the column headings
    found_headers = pending_process_list_page.get_grid_headers()
    assert found_headers == GRID_COLUMNS, f"Expected grid columns {GRID_COLUMNS} but found {found_headers}."

    # Step 3: a well-formed serial that does not exist shows no rows
    pending_process_list_page.search_serial_and_wait_for_result("BBDASR99999999")
    take_screenshot("no data for unknown serial")
    assert not pending_process_list_page.has_data_rows(), (
        "Expected no rows for Asset Serial 'BBDASR99999999' but data rows were shown."
    )


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


# ---------------------------------------------------------------------------
# 3. A row of the list is found again by its own Asset Serial
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_pending_list_row_is_found_again_by_its_serial(page, pending_process_list_page, take_screenshot):
    """Asset In Pending Process List: searching the Asset Serial of a listed row lists that asset with the same data."""
    # Step 1: open the list and take the first row it shows
    pending_process_list_page.navigate_here()
    rows = pending_process_list_page.read_rows()
    if not rows:
        pytest.skip("No asset is in a pending process on this environment right now.")
    first_row = rows[0]
    take_screenshot(f"first row {first_row['Asset Serial']}")

    # Step 2: search its Asset Serial
    pending_process_list_page.search_serial_and_wait_for_result(first_row["Asset Serial"])
    found = pending_process_list_page.read_rows_with_serial(first_row["Asset Serial"])
    take_screenshot(f"asset {first_row['Asset Serial']} searched")

    # Step 3: the asset is listed with the same item, group, status and pending feature
    assert found, f"Expected {first_row['Asset Serial']} to be listed after searching it."
    for column in COLUMNS_THAT_MUST_MATCH:
        assert found[0][column] == first_row[column], (
            f"{column}: the first row showed '{first_row[column]}' but the search found '{found[0][column]}'."
        )


# ---------------------------------------------------------------------------
# 4. Export to Excel
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_pending_list_export_downloads_excel(page, pending_process_list_page, tmp_path, take_screenshot):
    """Asset In Pending Process List: Export downloads an Excel file with the grid's columns."""
    # Step 1: open the list
    pending_process_list_page.navigate_here()
    take_screenshot("asset in pending process list opened")

    # Step 2: click Export and keep the downloaded file
    saved_file = str(tmp_path / "pending_export.xlsx")
    file_name = pending_process_list_page.export_to_file(saved_file)
    assert file_name == EXPORT_FILE_NAME, f"Expected export file name '{EXPORT_FILE_NAME}' but found '{file_name}'."

    # Step 3: the first row of the file holds the same column names as the grid
    sheet = openpyxl.load_workbook(saved_file).active
    header_row = [cell.value for cell in sheet[1]]
    assert header_row == GRID_COLUMNS, f"Expected exported columns {GRID_COLUMNS} but found {header_row}."
