"""
test_01_asset_registration_aaq.py: tests for the Asset Registration by AAQ
screen (Fixed Asset > Registration > Asset Registration by AAQ).

Built from automation/element_catalog/asset_registration_aaq.md and the
business rules in knowledge/erp-fixedasset.md (§2 Asset Registration).
The whole file logs in once and every test reuses that session (see the
`page` fixture below).

The tests run top to bottom in the order a user works with the screen:
    0. Smoke tests (the original five)
    1. The form opens with the right defaults
    2. Header fields: Note/Remarks and Vendor
    3. The Asset Details block: Asset Item and Measurement
    4. The 20,000 Taka minimum unit price
    5. Adding a line to the grid
    6. Reset and delete
    7. Draft and Submit, for each of the 5 asset items
    8. The saved registrations in the Registration List
    9. Gift Item

Every test also runs on its own. A test that reuses a registration made by an
earlier test creates that registration itself when run alone (see the
`registrations` fixture in conftest.py). To run part of the file:
    pytest tests/test_01_asset_registration_aaq.py -k "land or laptop"
    pytest "tests/test_01_asset_registration_aaq.py::test_aaq_submit_each_asset_item[land]"
"""
import pytest

from test_data.asset_items import ASSET_ITEMS, MEASURED_ITEMS, MINIMUM_PRICE_ITEMS
from test_data.asset_registration_data import build_asset_data, build_registration_data
from utils.run_context import trace_one_test

MINIMUM_PRICE_TOAST = "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka."


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 0. Smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_aaq_draft_registration(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a completed form can be saved as a Draft."""
    data = build_registration_data()

    # Step 1: open the Asset Registration by AAQ form
    aaq_page.navigate_here()
    take_screenshot("asset registration by aaq form opened")

    # Step 2: fill the form and add one asset line
    aaq_page.fill_registration_form(data)
    take_screenshot("asset registration form filled")

    # Step 3: click Draft and confirm the exact success toast
    aaq_page.draft_and_verify_success()
    take_screenshot("draft saved successfully")


@pytest.mark.smoke
@pytest.mark.regression
def test_aaq_submit_registration(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a completed form can be submitted for approval."""
    data = build_registration_data()

    # Step 1: open the Asset Registration by AAQ form
    aaq_page.navigate_here()

    # Step 2: fill the form and add one asset line
    aaq_page.fill_registration_form(data)
    take_screenshot("asset registration form filled")

    # Step 3: click Submit and confirm the exact success toast
    aaq_page.submit_and_verify_success()
    take_screenshot("registration submitted successfully")


@pytest.mark.regression
def test_aaq_purchase_date_equals_registration_date(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: Purchase Date can be set equal to the auto-filled Registration Date."""
    data = build_registration_data()

    # Step 1: open the form and pick a project so the Registration Date shows
    aaq_page.navigate_here()
    aaq_page.select_project(data["project"])

    # Step 2: set Purchase Date through the calendar pop-up
    purchase_date = aaq_page.set_purchase_date_equal_to_registration_date()
    take_screenshot("purchase date set")

    # Step 3: both dates must show the identical value
    registration_date = aaq_page.read_registration_date()
    assert purchase_date == registration_date, (
        f"Expected Purchase Date to equal Registration Date ({registration_date}) "
        f"but Purchase Date was set to {purchase_date}."
    )


@pytest.mark.regression
def test_aaq_draft_required_field_validations(page, aaq_page, take_screenshot):
    """
    Asset Registration by AAQ: Draft needs the same required fields as
    Submit — Purchase Date, Vendor and at least one Asset Details line.
    """
    data = build_registration_data()

    # Step 1: open the form, pick a project and the Spot Purchase type
    aaq_page.navigate_here()
    aaq_page.select_project(data["project"])
    aaq_page.choose_spot_purchase()

    # Step 2: Draft without a Purchase Date is rejected
    toast = aaq_page.click_draft_and_get_toast()
    take_screenshot("draft rejected without purchase date")
    assert toast == "Please Select Purchase Date.", f"Unexpected toast: '{toast}'"

    # Step 3: with a Purchase Date but no Vendor, Draft is rejected
    aaq_page.set_purchase_date_equal_to_registration_date()
    toast = aaq_page.click_draft_and_get_toast()
    take_screenshot("draft rejected without vendor")
    assert toast == "Please Select a supplier.", f"Unexpected toast: '{toast}'"

    # Step 4: with a Vendor but no asset line in the grid, Draft is rejected
    aaq_page.select_vendor(data["vendor"])
    toast = aaq_page.click_draft_and_get_toast()
    take_screenshot("draft rejected without asset line")
    assert toast == "No Asset in List to perform operation", f"Unexpected toast: '{toast}'"


@pytest.mark.regression
def test_aaq_minimum_line_total_rule(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: an asset line totalling under 20,000 Taka cannot be added."""
    # A unit price below the 20,000 Taka minimum
    data = build_registration_data(quantity=1, unit_price=19999)

    # Step 1: open the form and fill everything needed to Add a line
    aaq_page.navigate_here()
    aaq_page.select_project(data["project"])
    aaq_page.choose_spot_purchase()
    aaq_page.set_purchase_date_equal_to_registration_date()
    aaq_page.select_vendor(data["vendor"])
    aaq_page.select_asset_item(data["asset_item_search"], data["asset_item_selected"])

    # Step 2: enter the below-minimum unit price and click Add
    aaq_page.enter_item_details(data["item_specification"], data["quantity"], data["unit_price"])
    toast = aaq_page.click_add_and_get_toast()
    take_screenshot("add rejected below minimum total")

    # Step 3: the line is rejected with the minimum-cost message
    expected = "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka."
    assert toast == expected, f"Expected toast '{expected}' but found '{toast}'."


# ---------------------------------------------------------------------------
# 1. The form opens with the right defaults
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_aaq_registration_type_is_aaq(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: the Registration Type shows AAQ."""
    # Step 1: open the form
    aaq_page.navigate_here()
    take_screenshot("form opened")

    # Step 2: the read-only Registration Type is AAQ
    registration_type = aaq_page.read_registration_type()
    assert registration_type == "AAQ", f"Expected Registration Type 'AAQ' but found '{registration_type}'."


@pytest.mark.regression
def test_aaq_registration_date_is_prefilled(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: the Registration Date is filled in once a project is chosen."""
    data = build_registration_data()

    # Step 1: open the form and pick a project
    aaq_page.navigate_here()
    aaq_page.select_project(data["project"])
    take_screenshot("project picked")

    # Step 2: the Registration Date is a dd/mm/yyyy date
    aaq_page.verify_registration_date_format()


@pytest.mark.regression
def test_aaq_gift_item_and_spot_purchase_are_exclusive(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: Spot Purchase and Gift Item cannot both be selected."""
    # Step 1: open the form and choose Spot Purchase
    aaq_page.navigate_here()
    aaq_page.choose_spot_purchase()
    aaq_page.verify_sub_type_selected("spot")

    # Step 2: choose Gift Item, which switches Spot Purchase off
    aaq_page.choose_gift_item()
    take_screenshot("gift item chosen")
    aaq_page.verify_sub_type_selected("gift")


# ---------------------------------------------------------------------------
# 2. Header fields: Note/Remarks and Vendor
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_aaq_remarks_keeps_what_is_typed(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a short Note/Remarks is kept exactly as typed."""
    # Step 1: open the form and type a note
    aaq_page.navigate_here()
    aaq_page.enter_remarks("AUTOMATION_TEST remarks check")
    take_screenshot("remarks typed")

    # Step 2: the box shows the same text
    remarks = aaq_page.read_remarks()
    assert remarks == "AUTOMATION_TEST remarks check", (
        f"Expected the Note/Remarks box to show 'AUTOMATION_TEST remarks check' but found '{remarks}'."
    )


@pytest.mark.regression
@pytest.mark.xfail(
    reason="The Note/Remarks placeholder and the knowledge file say 100 characters, "
           "but the box accepts 200. Needs a product decision.",
    strict=True,
)
def test_aaq_remarks_accepts_100_characters(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: Note/Remarks accepts at most 100 characters."""
    # Step 1: open the form and type 150 characters
    aaq_page.navigate_here()
    aaq_page.enter_remarks("R" * 150)
    take_screenshot("150 characters typed")

    # Step 2: only 100 characters are kept
    remarks = aaq_page.read_remarks()
    assert len(remarks) == 100, f"Expected 100 characters to be kept but found {len(remarks)}."


@pytest.mark.regression
def test_aaq_vendor_selection_fills_details(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: picking a Vendor fills its Ref. Number and Address."""
    data = build_registration_data()

    # Step 1: open the form and pick the vendor
    aaq_page.navigate_here()
    aaq_page.select_vendor(data["vendor"])
    take_screenshot("vendor picked")

    # Step 2: the Ref. Number matches the vendor and the Address is filled
    details = aaq_page.read_vendor_details()
    assert details["number"] == data["vendor_number"], (
        f"Expected Vendor Ref. Number '{data['vendor_number']}' but found '{details['number']}'."
    )
    assert details["address"] != "", "Expected the Vendor Address to be filled in but it was empty."


# ---------------------------------------------------------------------------
# 3. The Asset Details block: Asset Item and Measurement
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_item_selection_fills_classification(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: picking an Asset Item fills its Category, Sub Category, Group and Unit."""
    data = build_asset_data(item)

    # Step 1: open the form and pick the Asset Item
    aaq_page.navigate_here()
    aaq_page.select_asset_item(data["asset_item_search"], data["asset_item_selected"])
    take_screenshot("asset item picked")

    # Step 2: every read-only classification box is filled in
    aaq_page.verify_item_classification_filled()


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
    expected = "Measurement must be greater than zero for this asset group"
    assert toast == expected, f"Expected toast '{expected}' but found '{toast}'."


# ---------------------------------------------------------------------------
# 4. The 20,000 Taka minimum unit price
# ---------------------------------------------------------------------------


@pytest.mark.regression
@MINIMUM_PRICE_ITEMS
def test_aaq_line_below_minimum_is_rejected(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a unit price of 19,999 Taka is rejected."""
    data = build_asset_data(item, quantity=1, unit_price=19999)

    # Step 1: open the form and fill everything needed to Add a line
    aaq_page.navigate_here()
    aaq_page.fill_form_until_add(data)

    # Step 2: Add is rejected with the minimum-cost message
    toast = aaq_page.click_add_and_get_toast()
    take_screenshot("add rejected below minimum")
    assert toast == MINIMUM_PRICE_TOAST, f"Expected toast '{MINIMUM_PRICE_TOAST}' but found '{toast}'."


@pytest.mark.regression
@MINIMUM_PRICE_ITEMS
def test_aaq_minimum_is_checked_on_unit_price_not_total(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: 2 x 10,000 is rejected, because the 20,000 Taka minimum is on the unit price."""
    data = build_asset_data(item, quantity=2, unit_price=10000)

    # Step 1: open the form and fill everything needed to Add a line of 2 x 10,000
    aaq_page.navigate_here()
    aaq_page.fill_form_until_add(data)

    # Step 2: Add is rejected although the line total is 20,000
    toast = aaq_page.click_add_and_get_toast()
    take_screenshot("add rejected, unit price below minimum")
    assert toast == MINIMUM_PRICE_TOAST, f"Expected toast '{MINIMUM_PRICE_TOAST}' but found '{toast}'."


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_line_at_exact_minimum_is_accepted(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a line totalling exactly 20,000 Taka is accepted."""
    data = build_asset_data(item, quantity=1, unit_price=20000)

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


# ---------------------------------------------------------------------------
# 5. Adding a line to the grid
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_add_line_shows_in_grid(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: an added asset line appears in the Asset Details grid."""
    data = build_asset_data(item)

    # Step 1: open the form, fill it and add the asset line
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("asset line added")

    # Step 2: the grid line shows the item, its specification (the grid shortens
    # a long one), the quantity and the unit price
    line = aaq_page.read_grid_first_line()
    specification_start = data["item_specification"][:25]
    assert line["Asset Item Name"] == data["grid_item_name"], (
        f"Expected Asset Item Name '{data['grid_item_name']}' but found grid line: {line}"
    )
    assert line["Item Specification"].startswith(specification_start), (
        f"Expected Item Specification starting '{specification_start}' but found grid line: {line}"
    )
    assert line["Quantity"] == "1", f"Expected Quantity '1' but found grid line: {line}"
    assert line["Unit Price(TK)"] == "25000", f"Expected Unit Price(TK) '25000' but found grid line: {line}"


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_grid_grand_total(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: the grid's Grand Total equals Quantity x Unit Price."""
    data = build_asset_data(item, quantity=2, unit_price=25000)

    # Step 1: open the form, fill it and add a line of 2 x 25,000
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("line of 2 x 25000 added")

    # Step 2: the line's Total Price and the Grand Total row both show 50,000
    line = aaq_page.read_grid_first_line()
    assert line["Total Price(TK)"] == "50000", f"Expected Total Price(TK) '50000' but found grid line: {line}"
    grid_text = aaq_page.read_asset_grid_text()
    assert "50,000" in grid_text, f"Expected a Grand Total of 50,000 but the grid shows: {grid_text}"


@pytest.mark.regression
@MEASURED_ITEMS
def test_aaq_measurement_shown_in_grid(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: the Measurement typed for an item is shown in the grid."""
    data = build_asset_data(item, measurement="30")

    # Step 1: open the form, fill it with a Measurement and add the line
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("line with measurement added")

    # Step 2: the grid line shows the Measurement and its unit
    line = aaq_page.read_grid_first_line()
    assert line["Measurement"] == "30", f"Expected Measurement '30' but found grid line: {line}"
    assert line["Measurement Unit"] != "", f"Expected a Measurement Unit but found grid line: {line}"


# ---------------------------------------------------------------------------
# 6. Reset and delete
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_reset_clears_asset_details_block(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: the Reset beside Add clears the Asset Details block."""
    data = build_asset_data(item)

    # Step 1: open the form and fill the Asset Details block without adding it
    aaq_page.navigate_here()
    aaq_page.fill_form_until_add(data)
    take_screenshot("asset details block filled")

    # Step 2: click the Reset beside Add
    aaq_page.reset_asset_details()
    take_screenshot("asset details block reset")

    # Step 3: the typed values are cleared
    aaq_page.verify_asset_block_cleared()


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_form_reset_clears_the_form(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: the footer Reset clears the typed note and the added lines."""
    data = build_asset_data(item)

    # Step 1: open the form, fill it and add the asset line
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    aaq_page.read_grid_first_line()
    take_screenshot("form filled and line added")

    # Step 2: click the footer Reset
    aaq_page.reset_form()
    take_screenshot("form reset")

    # Step 3: the note and the grid are empty
    remarks = aaq_page.read_remarks()
    assert remarks == "", f"Expected Note/Remarks to be cleared but found '{remarks}'."
    aaq_page.wait_until_grid_is_empty()


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_delete_removes_grid_line(item, page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: the trash button removes an added line from the grid."""
    data = build_asset_data(item)

    # Step 1: open the form, fill it and add the asset line
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    aaq_page.read_grid_first_line()
    take_screenshot("line added")

    # Step 2: delete the line
    aaq_page.delete_first_grid_line()
    take_screenshot("line deleted")

    # Step 3: the grid is empty again
    aaq_page.wait_until_grid_is_empty()


# ---------------------------------------------------------------------------
# 7. Draft and Submit, for each of the 5 asset items
#    These tests record what they create so section 8 can reuse it.
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_draft_each_asset_item(item, page, aaq_page, take_screenshot, registrations):
    """Asset Registration by AAQ: a registration for each asset item can be saved as a Draft."""
    data = build_asset_data(item)

    # Step 1: open the form and fill it
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("registration form filled")

    # Step 2: click Draft and confirm the exact success toast
    aaq_page.draft_and_verify_success()
    take_screenshot("draft saved successfully")

    # Step 3: remember the Draft so later tests can reuse it
    registrations.remember_draft(data)


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_submit_each_asset_item(item, page, aaq_page, take_screenshot, registrations):
    """Asset Registration by AAQ: a registration for each asset item can be submitted."""
    data = build_asset_data(item)

    # Step 1: open the form and fill it
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("registration form filled")

    # Step 2: click Submit and confirm the exact success toast
    aaq_page.submit_and_verify_success()
    take_screenshot("registration submitted successfully")

    # Step 3: remember the submitted registration so later tests can reuse it
    registrations.remember_pending(data)


# ---------------------------------------------------------------------------
# 8. The saved registrations in the Registration List
#    These reuse a registration from section 7. Run on their own, they create
#    the registration themselves.
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_draft_is_listed_as_draft(item, page, registrations, registration_list_page, take_screenshot):
    """Asset Registration by AAQ: a saved Draft appears in the Registration List with status DRAFT."""
    # Step 1: get a Draft registration (reused from the Draft test, or created now)
    draft = registrations.get_draft(item)

    # Step 2: open the list and find it
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(draft["registration_number"])
    take_screenshot("draft found in list")

    # Step 3: its status is DRAFT
    registration_list_page.verify_status(draft["registration_number"], "DRAFT")


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_submitted_is_listed_as_pending(item, page, registrations, registration_list_page, take_screenshot):
    """Asset Registration by AAQ: a submitted registration appears in the Registration List as PENDING."""
    # Step 1: get a submitted registration (reused from the Submit test, or created now)
    submitted = registrations.get_pending(item)

    # Step 2: open the list and find it
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(submitted["registration_number"])
    take_screenshot("submitted registration found in list")

    # Step 3: its status is PENDING
    registration_list_page.verify_status(submitted["registration_number"], "PENDING")


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_draft_can_be_submitted_from_list(
    item, page, aaq_page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration by AAQ: a Draft opened from the list can be submitted without re-entering anything."""
    # Step 1: get a Draft registration (reused from the Draft test, or created now)
    draft = registrations.get_draft(item)

    # Step 2: open it from the Registration List and submit it
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(draft["registration_number"])
    registration_list_page.open_registration(draft["registration_number"])
    take_screenshot("draft opened from list")
    aaq_page.submit_and_verify_success()
    take_screenshot("draft submitted")

    # Step 3: it is no longer a Draft; keep it as the submitted registration for this item
    registrations.move_draft_to_pending(draft)


# ---------------------------------------------------------------------------
# 9. Gift Item: the same form with the Gift Item sub-type
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_aaq_gift_item_required_field_validations(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: Draft with Gift Item needs a Purchase Date, a Vendor and an asset line."""
    data = build_registration_data(sub_type="gift")

    # Step 1: open the form, pick a project and the Gift Item type
    aaq_page.navigate_here()
    aaq_page.select_project(data["project"])
    aaq_page.choose_sub_type(data["sub_type"])

    # Step 2: Draft without a Purchase Date is rejected
    toast = aaq_page.click_draft_and_get_toast()
    take_screenshot("gift draft rejected without purchase date")
    assert toast == "Please Select Purchase Date.", f"Unexpected toast: '{toast}'"

    # Step 3: with a Purchase Date but no Vendor, Draft is rejected
    aaq_page.set_purchase_date_equal_to_registration_date()
    toast = aaq_page.click_draft_and_get_toast()
    take_screenshot("gift draft rejected without vendor")
    assert toast == "Please Select a supplier.", f"Unexpected toast: '{toast}'"

    # Step 4: with a Vendor but no asset line, Draft is rejected
    aaq_page.select_vendor(data["vendor"])
    toast = aaq_page.click_draft_and_get_toast()
    take_screenshot("gift draft rejected without asset line")
    assert toast == "No Asset in List to perform operation", f"Unexpected toast: '{toast}'"


@pytest.mark.regression
def test_aaq_gift_item_minimum_unit_price(page, aaq_page, take_screenshot):
    """Asset Registration by AAQ: a Gift Item line with a unit price of 19,999 Taka is rejected."""
    data = build_registration_data(sub_type="gift", quantity=1, unit_price=19999)

    # Step 1: open the form and fill everything needed to Add a line
    aaq_page.navigate_here()
    aaq_page.fill_form_until_add(data)

    # Step 2: Add is rejected with the minimum-cost message
    toast = aaq_page.click_add_and_get_toast()
    take_screenshot("gift add rejected below minimum")
    assert toast == MINIMUM_PRICE_TOAST, f"Expected toast '{MINIMUM_PRICE_TOAST}' but found '{toast}'."


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_gift_item_draft_each_asset_item(item, page, aaq_page, take_screenshot, registrations):
    """Asset Registration by AAQ: a Gift Item registration for each asset item can be saved as a Draft."""
    data = build_asset_data(item, sub_type="gift")

    # Step 1: open the form and fill it with Gift Item selected
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("gift item form filled")

    # Step 2: click Draft and confirm the exact success toast
    aaq_page.draft_and_verify_success()
    take_screenshot("gift item draft saved successfully")

    # Step 3: remember the Draft so later tests can reuse it
    registrations.remember_draft(data)


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_gift_item_submit_each_asset_item(item, page, aaq_page, take_screenshot, registrations):
    """Asset Registration by AAQ: a Gift Item registration for each asset item can be submitted."""
    data = build_asset_data(item, sub_type="gift")

    # Step 1: open the form and fill it with Gift Item selected
    aaq_page.navigate_here()
    aaq_page.fill_registration_form(data)
    take_screenshot("gift item form filled")

    # Step 2: click Submit and confirm the exact success toast
    aaq_page.submit_and_verify_success()
    take_screenshot("gift item submitted successfully")

    # Step 3: remember the submitted registration so later tests can reuse it
    registrations.remember_pending(data)


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_gift_item_draft_is_listed_as_draft(item, page, registrations, registration_list_page, take_screenshot):
    """Asset Registration by AAQ: a saved Gift Item Draft appears in the Registration List with status DRAFT."""
    # Step 1: get a Gift Item Draft (reused from the Draft test, or created now)
    draft = registrations.get_draft(item, sub_type="gift")

    # Step 2: open the list and find it
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(draft["registration_number"])
    take_screenshot("gift item draft found in list")

    # Step 3: its status is DRAFT
    registration_list_page.verify_status(draft["registration_number"], "DRAFT")


@pytest.mark.regression
@ASSET_ITEMS
def test_aaq_gift_item_submitted_is_listed_as_pending(
    item, page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration by AAQ: a submitted Gift Item registration appears in the Registration List as PENDING."""
    # Step 1: get a submitted Gift Item registration (reused from the Submit test, or created now)
    submitted = registrations.get_pending(item, sub_type="gift")

    # Step 2: open the list and find it
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(submitted["registration_number"])
    take_screenshot("gift item registration found in list")

    # Step 3: its status is PENDING
    registration_list_page.verify_status(submitted["registration_number"], "PENDING")
