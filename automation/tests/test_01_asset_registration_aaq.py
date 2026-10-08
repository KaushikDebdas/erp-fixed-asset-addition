"""
test_01_asset_registration_aaq.py: tests for the Asset Registration by AAQ
screen (Fixed Asset > Registration > Asset Registration by AAQ), built around
the planned asset slots (test_data/asset_slots.py) instead of repeating every check for every item.

Built from automation/element_catalog/asset_registration_aaq.md and the
business rules in knowledge/erp-fixedasset.md (§2 Asset Registration).
The whole file logs in once and every test reuses that session (see the
`page` fixture below).

The tests run top to bottom:
    1. Validations, checked once: mandatory fields before Draft or Submit,
       and the amount rules (minimum unit price, Measurement)
    2. The asset slots (Spot Purchase and Gift Item of several items), each created
       as planned in test_data/asset_slots.py and shown with its planned status in
       the Asset Registration List

Opening a Draft from the list and submitting it is tested in
test_02_asset_registration_list.py.

Each asset is remembered under its slot name, so later tests and flows can reuse it:
registrations.get_pending_of("sale_profit_a") here, assets.get("sale_profit_a") later.
There is no Reject step: the Asset Registration Approval List has no Reject
button (checked 2026-10-05).

Every test also runs on its own. To run part of the file:
    pytest tests/test_01_asset_registration_aaq.py -k "gift"
    pytest tests/test_01_asset_registration_aaq.py -k "split_land"
"""
import pytest

from test_data.asset_registration_data import (
    MEASURED_ITEMS,
    build_asset_data,
    build_registration_data,
)
from test_data.asset_slots import ALL_SLOTS
from test_data.toast_messages import (
    MEASUREMENT_TOAST,
    MINIMUM_PRICE_TOAST,
    NO_ASSET_LINE_TOAST,
    PURCHASE_DATE_TOAST,
    VENDOR_TOAST,
)
from utils.run_context import trace_one_test

# Messages (toasts) the screen shows


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. Validations, checked once
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.parametrize("sub_type", ["spot", "gift"])
def test_aaq_mandatory_fields_are_required_before_draft_or_submit(sub_type, page, aaq_page, take_screenshot):
    """
    Asset Registration by AAQ: Draft and Submit both need a Purchase Date, a
    Vendor and at least one asset line, for Spot Purchase and for Gift Item.
    """
    data = build_registration_data(sub_type=sub_type)

    # Step 1: open the form, pick a project and the sub type
    aaq_page.navigate_here()
    aaq_page.select_project(data["project"])
    aaq_page.choose_sub_type(sub_type)

    # Step 2: without a Purchase Date, Draft and Submit are rejected
    aaq_page.verify_draft_and_submit_rejected(PURCHASE_DATE_TOAST)
    take_screenshot("rejected without purchase date")

    # Step 3: with a Purchase Date but no Vendor, Draft and Submit are rejected
    aaq_page.set_purchase_date_equal_to_registration_date()
    aaq_page.verify_draft_and_submit_rejected(VENDOR_TOAST)
    take_screenshot("rejected without vendor")

    # Step 4: with a Vendor but no asset line, Draft and Submit are rejected
    aaq_page.select_vendor(data["vendor"])
    aaq_page.verify_draft_and_submit_rejected(NO_ASSET_LINE_TOAST)
    take_screenshot("rejected without asset line")


@pytest.mark.regression
@pytest.mark.parametrize("sub_type", ["spot", "gift"])
def test_aaq_line_below_minimum_unit_price_is_rejected(sub_type, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a unit price of 19,999 Taka is rejected for Spot Purchase and Gift Item."""
    data = build_asset_data("furniture", quantity=1, unit_price=19999, sub_type=sub_type)

    # Step 1: open the form and fill everything needed to Add a line
    aaq_page.navigate_here()
    aaq_page.fill_form_until_add(data)

    # Step 2: Add is rejected with the minimum-cost message
    toast = aaq_page.click_add_and_get_toast()
    take_screenshot("add rejected below minimum")
    aaq_page.verify_toast_text(toast, MINIMUM_PRICE_TOAST, "click add")


@pytest.mark.regression
def test_aaq_minimum_is_checked_on_unit_price_not_total(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: 2 x 10,000 is rejected, because the 20,000 Taka minimum is on the unit price."""
    data = build_asset_data("furniture", quantity=2, unit_price=10000)

    # Step 1: open the form and fill everything needed to Add a line of 2 x 10,000
    aaq_page.navigate_here()
    aaq_page.fill_form_until_add(data)

    # Step 2: Add is rejected although the line total is 20,000
    toast = aaq_page.click_add_and_get_toast()
    take_screenshot("add rejected, unit price below minimum")
    aaq_page.verify_toast_text(toast, MINIMUM_PRICE_TOAST, "click add")


@pytest.mark.regression
def test_aaq_line_at_exact_minimum_is_accepted(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a line with a unit price of exactly 20,000 Taka is accepted."""
    data = build_asset_data("furniture", quantity=1, unit_price=20000)

    # Step 1: open the form, fill it and add the line
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("line of exactly 20000 added")

    # Step 2: the line is in the grid with a total of 20,000
    line = aaq_page.read_grid_first_line()
    assert line["Total Price(TK)"] == "20000", f"Expected Total Price(TK) '20000' but found grid line: {line}"


@pytest.mark.regression
def test_aaq_land_has_no_minimum_price(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: Land is exempt from the 20,000 Taka minimum unit price."""
    data = build_asset_data("land", quantity=1, unit_price=1)

    # Step 1: open the form and fill it with a unit price of 1 Taka
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("land line of 1 taka added")

    # Step 2: the line is accepted
    line = aaq_page.read_grid_first_line()
    assert line["Unit Price(TK)"] == "1", f"Expected Unit Price(TK) '1' but found grid line: {line}"


@pytest.mark.regression
@MEASURED_ITEMS
def test_aaq_measurement_is_required_for_land_and_building(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a Land or Building line without a Measurement is rejected."""
    data = build_asset_data(item)
    # Leave the Measurement out, so the form must reject the line
    del data["measurement"]

    # Step 1: open the form and fill everything except the Measurement
    aaq_page.navigate_here()
    aaq_page.fill_form_until_add(data)

    # Step 2: Add is rejected with the Measurement message
    toast = aaq_page.click_add_and_get_toast()
    take_screenshot("add rejected without measurement")
    aaq_page.verify_toast_text(toast, MEASUREMENT_TOAST, "click add")


# ---------------------------------------------------------------------------
# 2. The asset slots: each is created as planned and listed with its planned status
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ALL_SLOTS
def test_aaq_slot_asset_created_and_listed(
    slot, item, sub_type, plan, page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration by AAQ: each asset slot is saved as a Draft or submitted as planned, and the list shows that status."""
    # Step 1: create the asset (a Draft, or submitted when the plan says submit)
    if plan == "submit":
        record = registrations.get_pending_of(slot)
        status = "PENDING"
    else:
        record = registrations.get_draft_of(slot)
        status = "DRAFT"
    take_screenshot(f"{slot} created ({plan})")

    # Step 2: the registration number was read from the list, so later tests can find the asset
    assert record["registration_number"], f"No registration number was recorded for slot {slot}."

    # Step 3: find it in the Registration List; its status is the planned one, and the row is this asset's
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(record["registration_number"])
    registration_list_page.verify_status(record["registration_number"], status)
    registration_list_page.verify_column_equals("Project Name", [record["data"]["project"]])
    registration_list_page.verify_column_equals("Registration Type", ["AAQ"])
