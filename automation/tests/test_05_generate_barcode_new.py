"""
test_05_generate_barcode_new.py: tests for the Generate Barcode screen (Fixed
Asset > Asset Profile > Generate Barcode), using the 8 approved AAQ assets.

Built from automation/element_catalog/generate_barcode.md. The assets are the
ones approved by test_03_asset_registration_approval_list_new.py; they are
remembered, with their Asset Serial, under AAQ_ASSET_GROUP
(test_data/asset_registration_data.py). When a test here runs on its own, the
`registrations` fixture creates and approves the asset it needs, so every test
can run alone.

Every approved asset is checked against its own data: its row must show its
Asset Serial, item, categories, project and statuses. The barcode PDF is
fetched and read, so the test sees that it is the label of the right asset,
printed once for every copy asked for.

The whole file logs in once and every test reuses that session. Nothing is
printed or saved.

The tests run top to bottom:
    1. Each approved asset: its row shows its own data
    2. The page: columns and search
    3. Print Quantity: Set copies the Default Print Quantity into a ticked row
    4. Generate: the barcode PDF is the label of the right asset

To run part of the file:
    pytest tests/test_05_generate_barcode_new.py -k "land"
"""
import pytest

from test_data.asset_registration_data import (
    AAQ_ASSET_GROUP,
    APPROVED_AAQ_ASSETS,
    build_asset_profile,
)
from utils.run_context import trace_one_test

# The asset the tests share when they only need "an approved asset"
SHARED_ITEM = "land"
SHARED_SUB_TYPE = "spot"

# Column headings of the grid, in order
GRID_COLUMNS = [
    "SL", "Asset Serial", "Asset Item Name", "Sub Category", "Category Name",
    "Project Name", "Department", "Asset Assign Status", "Status", "Print Quantity",
]

# Print Quantity that Set copies into the ticked row, and the number of labels Generate must print
DEFAULT_QUANTITY = 3
LABEL_QUANTITY = 2


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. Each approved asset: its row shows its own data
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
@APPROVED_AAQ_ASSETS
def test_barcode_row_shows_the_asset_data(
    item, sub_type, page, registrations, generate_barcode_page, take_screenshot
):
    """Generate Barcode: searching an Asset Serial lists that asset with its own item, categories, project and statuses."""
    # Step 1: get the approved asset (approved by an earlier test, or created and approved now)
    record = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)
    expected = build_asset_profile(record["data"], record["registration_number"], record["serial"])

    # Step 2: open Generate Barcode and search its Asset Serial
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(record["serial"])
    take_screenshot(f"{sub_type} {item} asset {record['serial']} found")

    # Step 3: exactly this asset is listed, and its row shows its own data
    assert generate_barcode_page.is_serial_listed(record["serial"])
    generate_barcode_page.verify_row_shows(record["serial"], expected)


# ---------------------------------------------------------------------------
# 2. The page: columns and search
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_barcode_grid_columns(page, generate_barcode_page, take_screenshot):
    """Generate Barcode: the results grid shows the documented columns."""
    # Step 1: open Generate Barcode
    generate_barcode_page.navigate_here()
    take_screenshot("generate barcode opened")

    # Step 2: the column headings
    assert generate_barcode_page.get_grid_headers() == GRID_COLUMNS


@pytest.mark.regression
def test_barcode_unknown_serial_lists_nothing(page, generate_barcode_page, take_screenshot):
    """Generate Barcode: an Asset Serial that does not exist lists no asset."""
    # Step 1: open the screen and search a well-formed serial that does not exist
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial("BBDASR99999999")
    take_screenshot("unknown serial searched")

    # Step 2: it is not listed
    assert not generate_barcode_page.is_serial_listed("BBDASR99999999")


# ---------------------------------------------------------------------------
# 3. Print Quantity
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_barcode_print_quantity_starts_at_one(page, registrations, generate_barcode_page, take_screenshot):
    """Generate Barcode: a listed asset starts with a Print Quantity of 1."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: find the asset
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    take_screenshot("asset found")

    # Step 2: its Print Quantity is 1
    assert generate_barcode_page.get_row_print_quantity(serial) == "1"


@pytest.mark.regression
def test_barcode_set_default_quantity(page, registrations, generate_barcode_page, take_screenshot):
    """Generate Barcode: Set copies the Default Print Quantity into the ticked row."""
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: find the asset and tick its row
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    generate_barcode_page.tick_row(serial)

    # Step 2: set a default quantity
    generate_barcode_page.set_default_quantity(DEFAULT_QUANTITY)
    take_screenshot("default print quantity set")

    # Step 3: the row's Print Quantity shows it
    assert generate_barcode_page.get_row_print_quantity(serial) == str(DEFAULT_QUANTITY)


# ---------------------------------------------------------------------------
# 4. Generate
# ---------------------------------------------------------------------------


@pytest.mark.regression
@APPROVED_AAQ_ASSETS
def test_barcode_generate_prints_the_label_of_the_asset(
    item, sub_type, page, registrations, generate_barcode_page, take_screenshot
):
    """Generate Barcode: Generate opens a PDF with the asset's own label, printed once for every copy."""
    # Step 1: get the approved asset
    record = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)
    expected = build_asset_profile(record["data"], record["registration_number"], record["serial"])

    # Step 2: find the asset, tick its row and ask for the label copies
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(record["serial"])
    generate_barcode_page.tick_row(record["serial"])
    generate_barcode_page.set_default_quantity(LABEL_QUANTITY)
    take_screenshot(f"{sub_type} {item} asset ticked with quantity {LABEL_QUANTITY}")

    # Step 3: Generate opens a PDF report in a new tab
    report_url = generate_barcode_page.generate_and_get_report_url()
    assert "generateAssetBarcodeReport" in report_url
    assert "format=PDF" in report_url

    # Step 4: the PDF is this asset's label (serial, item, branch, project), once for every copy
    generate_barcode_page.verify_barcode_pdf(report_url, expected, LABEL_QUANTITY)
