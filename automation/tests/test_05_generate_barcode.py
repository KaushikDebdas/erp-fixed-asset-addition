"""
test_05_generate_barcode.py: tests for the Generate Barcode screen (Fixed
Asset > Asset Profile > Generate Barcode).

Built from automation/element_catalog/generate_barcode.md. The tests use a
freshly approved asset (see the `profile_assets` fixture in conftest.py). The
whole file logs in once and every test reuses that session. Nothing is
printed or saved: the barcode PDF is only opened and its address checked.
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_barcode_search_by_serial(page, generate_barcode_page, profile_assets, take_screenshot):
    """Generate Barcode: searching an Asset Serial lists the asset."""
    serial = profile_assets["land"]["serial"]

    # Step 1: open Generate Barcode
    generate_barcode_page.navigate_here()

    # Step 2: search by the Asset Serial
    generate_barcode_page.search_by_serial(serial)
    take_screenshot(f"asset {serial} found")

    # Step 3: the asset is listed
    assert generate_barcode_page.is_serial_listed(serial)


@pytest.mark.regression
def test_barcode_grid_columns(page, generate_barcode_page, take_screenshot):
    """Generate Barcode: the results grid shows the documented columns."""
    # Step 1: open Generate Barcode
    generate_barcode_page.navigate_here()
    take_screenshot("generate barcode opened")

    # Step 2: the column headings
    assert generate_barcode_page.get_grid_headers() == [
        "SL",
        "Asset Serial",
        "Asset Item Name",
        "Sub Category",
        "Category Name",
        "Project Name",
        "Department",
        "Asset Assign Status",
        "Status",
        "Print Quantity",
    ]


@pytest.mark.regression
def test_barcode_set_default_quantity(page, generate_barcode_page, profile_assets, take_screenshot):
    """Generate Barcode: Set copies the Default Print Quantity into the ticked row."""
    serial = profile_assets["land"]["serial"]

    # Step 1: find the asset and tick its row
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    generate_barcode_page.tick_row(serial)

    # Step 2: set a default quantity of 3
    generate_barcode_page.set_default_quantity(3)
    take_screenshot("default print quantity set")

    # Step 3: the row's Print Quantity shows 3
    assert generate_barcode_page.get_row_print_quantity(serial) == "3"


@pytest.mark.regression
def test_barcode_generate_opens_pdf_report(
    page, generate_barcode_page, profile_assets, take_screenshot
):
    """Generate Barcode: Generate opens the barcode PDF report in a new tab."""
    serial = profile_assets["land"]["serial"]

    # Step 1: find the asset, tick its row and set a quantity of 2
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    generate_barcode_page.tick_row(serial)
    generate_barcode_page.set_default_quantity(2)
    take_screenshot("asset ticked with quantity 2")

    # Step 2: click Generate; a new tab opens with the PDF barcode report
    report_url = generate_barcode_page.generate_and_get_report_url()
    assert "generateAssetBarcodeReport" in report_url
    assert "format=PDF" in report_url
