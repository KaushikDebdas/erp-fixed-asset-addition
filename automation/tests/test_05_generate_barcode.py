"""
test_05_generate_barcode.py: tests for the Generate Barcode screen (Fixed
Asset > Asset Profile > Generate Barcode).

Built from automation/element_catalog/generate_barcode.md. The tests use one
approved asset, the Land slot (split_land) approved by
test_03_asset_registration_approval_list.py and remembered, with its Asset
Serial, under its slot name. When a test here runs on its own, the
`registrations` fixture creates and approves the asset it needs, so every test
can run alone.

The whole file logs in once and every test reuses that session. Generate only
clicks the button: the barcode report is not opened or checked.

The tests run top to bottom:
    1. Print Quantity: a listed asset starts with 1
    2. Generate: an approved asset is ticked, Set copies the Default Print Quantity into its
       row, and it is sent to Generate

To run part of the file:
    pytest tests/test_05_generate_barcode.py -k "generate"
"""
import pytest

from utils.run_context import trace_one_test

# The asset the tests share when they only need "an approved asset" (the Land slot)
SHARED_SLOT = "split_land"

# The quantity asked for before Generate (Set copies it into the ticked row)
LABEL_QUANTITY = 2


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. Print Quantity starts at 1
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_barcode_print_quantity_starts_at_one(page, registrations, generate_barcode_page, take_screenshot):
    """Generate Barcode: a listed asset starts with a Print Quantity of 1."""
    serial = registrations.get_approved_of(SHARED_SLOT)["serial"]

    # Step 1: find the asset
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    take_screenshot("asset found")

    # Step 2: its Print Quantity is 1
    found_quantity = generate_barcode_page.get_row_print_quantity(serial)
    assert found_quantity == "1", f"Expected Print Quantity '1' for {serial} but found '{found_quantity}'."


# ---------------------------------------------------------------------------
# 2. Set the quantity and Generate
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_barcode_generate_for_the_asset(page, registrations, generate_barcode_page, take_screenshot):
    """Generate Barcode: an approved asset can be ticked, Set copies a quantity into its row, and it is sent to Generate."""
    # Step 1: get the shared approved asset (one asset is enough for Generate)
    serial = registrations.get_approved_of(SHARED_SLOT)["serial"]

    # Step 2: find the asset, tick its row and ask for the label copies
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    generate_barcode_page.tick_row(serial)
    generate_barcode_page.set_default_quantity(LABEL_QUANTITY)
    take_screenshot(f"asset ticked with quantity {LABEL_QUANTITY}")

    # Step 3: Set copied the quantity into the ticked row
    found_quantity = generate_barcode_page.get_row_print_quantity(serial)
    assert found_quantity == str(LABEL_QUANTITY), (
        f"Expected Print Quantity '{LABEL_QUANTITY}' for {serial} but found '{found_quantity}'."
    )

    # Step 4: click Generate (the barcode report itself is not checked)
    generate_barcode_page.click_generate()
    take_screenshot("generate clicked")
