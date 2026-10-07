"""
test_05_generate_barcode.py: tests for the Generate Barcode screen (Fixed
Asset > Asset Profile > Generate Barcode).

Built from automation/element_catalog/generate_barcode.md. The tests use one
approved asset, the shared Land asset approved by
test_03_asset_registration_approval_list.py and remembered, with its Asset
Serial, under AAQ_ASSET_GROUP (test_data/asset_registration_data.py). When a
test here runs on its own, the `registrations` fixture creates and approves the
asset it needs, so every test can run alone.

The whole file logs in once and every test reuses that session. Generate only
clicks the button: the barcode report is not opened or checked.

The tests run top to bottom:
    1. Print Quantity: a listed asset starts with 1
    2. Print Quantity: Set copies the Default Print Quantity into a ticked row
    3. Generate: an approved asset is ticked, given a quantity and sent to Generate

To run part of the file:
    pytest tests/test_05_generate_barcode.py -k "generate"
"""
import pytest

from test_data.asset_registration_data import AAQ_ASSET_GROUP
from utils.run_context import trace_one_test

# The asset the tests share when they only need "an approved asset"
SHARED_ITEM = "land"
SHARED_SUB_TYPE = "spot"

# Print Quantity that Set copies into the ticked row, and the quantity asked for before Generate
DEFAULT_QUANTITY = 3
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
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 1: find the asset
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    take_screenshot("asset found")

    # Step 2: its Print Quantity is 1
    found_quantity = generate_barcode_page.get_row_print_quantity(serial)
    assert found_quantity == "1", f"Expected Print Quantity '1' for {serial} but found '{found_quantity}'."


# ---------------------------------------------------------------------------
# 2. Print Quantity: Set
# ---------------------------------------------------------------------------


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
    found_quantity = generate_barcode_page.get_row_print_quantity(serial)
    assert found_quantity == str(DEFAULT_QUANTITY), (
        f"Expected Print Quantity '{DEFAULT_QUANTITY}' for {serial} but found '{found_quantity}'."
    )


# ---------------------------------------------------------------------------
# 3. Generate
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_barcode_generate_for_the_asset(page, registrations, generate_barcode_page, take_screenshot):
    """Generate Barcode: an approved asset can be ticked, given a quantity and sent to Generate."""
    # Step 1: get the shared approved asset (one asset is enough for Generate)
    serial = registrations.get_approved(SHARED_ITEM, SHARED_SUB_TYPE, AAQ_ASSET_GROUP)["serial"]

    # Step 2: find the asset, tick its row and ask for the label copies
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(serial)
    generate_barcode_page.tick_row(serial)
    generate_barcode_page.set_default_quantity(LABEL_QUANTITY)
    take_screenshot(f"asset ticked with quantity {LABEL_QUANTITY}")

    # Step 3: click Generate (the barcode report itself is not checked)
    generate_barcode_page.click_generate()
    take_screenshot("generate clicked")
