"""
test_07_asset_serial_split.py: tests for the Asset Serial Split screen (Fixed
Asset > Asset Profile > Asset Serial Split) and its Asset Split form.

Built from automation/element_catalog/asset_serial_split.md. The asset that is
split is NOT created here: it is the Land asset of the slot split_land, read with
registrations.get_approved_of("split_land") (a new one is created when none exists).
Only that Land asset is ever split. The Furniture asset of the slot usage_a has no
measurement, so it is used only to read the refusal message. The whole file logs in
once and every test reuses that session.

The tests run top to bottom:
    1. The Split screen: search, refusal of an asset with no measurement
    2. The Asset Split form: details, Split Into messages, split lines, percentages
    3. Reset and Back leave the asset unsplit
    4. LAST: the real split is submitted (this uses the Land asset up)

The last test must stay last in the file: after it the Land asset is split, and
its record moves to the SPLIT status (see utils/split_helper.py). Run on its own,
each test creates the Land asset it needs.

To run part of the file:
    pytest tests/test_07_asset_serial_split.py -k "percentage"
"""
import pytest

from test_data.asset_split_data import (
    FIRST_LINE_PERCENTAGE,
    LAND_ACC_DEPRECIATION_TEXT,
    LAND_ITEM_NAME,
    LAND_MEASUREMENT,
    LAND_MEASUREMENT_TEXT,
    LAND_VALUE,
    LAND_VALUE_TEXT,
    SPLIT_INTO,
    SPLIT_REMARKS,
)
from utils.run_context import trace_one_test

# The Land slot that is split, and the Furniture slot (no measurement) used for the refusal message
LAND_SLOT = "split_land"
NO_MEASUREMENT_SLOT = "usage_a"

# Message shown when Split Into is not a whole number from 2 to 100
RANGE_MESSAGE = "Please enter a valid integer number between 2 and 100"

# What the Land asset's details show on the form (field id -> text)
LAND_FORM_FIELDS = {
    "assetName": LAND_ITEM_NAME,
    "measurementFront": LAND_MEASUREMENT_TEXT,
    "netAssetValue": LAND_VALUE_TEXT,
    "accumulatedDepriciation": LAND_ACC_DEPRECIATION_TEXT,
}


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. The Split screen
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_split_search_shows_split_button(page, asset_serial_split_page, registrations, take_screenshot):
    """Asset Serial Split: searching the Land asset's serial lists it with a SPLIT button."""
    # Step 1: get the Land asset
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]

    # Step 2: open Asset Serial Split and search its serial
    asset_serial_split_page.navigate_here()
    asset_serial_split_page.search_by_serial(serial)
    take_screenshot(f"land asset {serial} found")

    # Step 3: the row has a SPLIT button
    asset_serial_split_page.verify_split_button_shown(serial)


@pytest.mark.regression
def test_split_refused_for_asset_without_measurement(
    page, asset_serial_split_page, registrations, take_screenshot
):
    """Asset Serial Split: an asset with no measurement cannot be split, a message says why."""
    # Step 1: get the Furniture asset (it has no measurement) and search its serial
    serial = registrations.get_approved_of(NO_MEASUREMENT_SLOT)["serial"]
    asset_serial_split_page.navigate_here()
    asset_serial_split_page.search_by_serial(serial)
    take_screenshot(f"furniture asset {serial} found")

    # Step 2: click SPLIT; the refusal message is shown and no form opens
    asset_serial_split_page.verify_split_is_refused(serial)
    take_screenshot("split refused without measurement")


# ---------------------------------------------------------------------------
# 2. The Asset Split form
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_split_form_shows_land_details(page, asset_serial_split_page, registrations, take_screenshot):
    """Asset Serial Split: the form opens with the Land asset's details and an empty Split Into box."""
    # Step 1: open the form of the saved Land asset
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]
    asset_serial_split_page.open_split_form_for_serial(serial)
    take_screenshot("asset split form opened")

    # Step 2: the form shows the Land's serial, name, measurement and values
    asset_serial_split_page.verify_form_shows({"assetSerial": serial, **LAND_FORM_FIELDS})

    # Step 3: Split Into is empty and can be typed in
    asset_serial_split_page.verify_split_into_is_empty_and_editable()


@pytest.mark.regression
@pytest.mark.parametrize(
    "split_into, expected_message",
    [
        pytest.param("", "Split into field is mandatory", id="empty"),
        pytest.param("0", RANGE_MESSAGE, id="zero"),
        pytest.param("1", RANGE_MESSAGE, id="one"),
        pytest.param("101", RANGE_MESSAGE, id="one_hundred_and_one"),
    ],
)
def test_split_into_value_is_validated(
    split_into, expected_message, page, asset_serial_split_page, registrations, take_screenshot
):
    """Asset Serial Split: Split Into must be a whole number from 2 to 100."""
    # Step 1: open the form of the saved Land asset
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]
    asset_serial_split_page.open_split_form_for_serial(serial)

    # Step 2: type the value, click Split; the message is shown and no lines are built
    asset_serial_split_page.verify_split_into_message(split_into, expected_message)
    take_screenshot(f"split into '{split_into}' refused")
    asset_serial_split_page.verify_line_count(0)


@pytest.mark.regression
def test_split_into_two_builds_two_lines(page, asset_serial_split_page, registrations, take_screenshot):
    """Asset Serial Split: Split Into 2 builds two split lines."""
    # Step 1: open the form of the saved Land asset
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]
    asset_serial_split_page.open_split_form_for_serial(serial)

    # Step 2: type 2 and click Split
    asset_serial_split_page.build_split_lines(SPLIT_INTO)
    take_screenshot("two split lines built")

    # Step 3: the result grid has two lines
    asset_serial_split_page.verify_line_count(2)


@pytest.mark.regression
def test_percentage_in_line_one_fills_line_two(page, asset_serial_split_page, registrations, take_screenshot):
    """Asset Serial Split: 50 percent in line 1 gives line 2 the other 50 percent, half the measurement and value each."""
    # Step 1: open the form and build two lines
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]
    asset_serial_split_page.open_split_form_for_serial(serial)
    asset_serial_split_page.build_split_lines(SPLIT_INTO)

    # Step 2: type 50 in line 1
    asset_serial_split_page.type_line_percentage(0, FIRST_LINE_PERCENTAGE)
    take_screenshot("50 percent typed in line 1")

    # Step 3: both lines hold half of the measurement and the value
    half_measurement = LAND_MEASUREMENT / 2
    half_value = LAND_VALUE / 2
    asset_serial_split_page.verify_line_values(0, 50, half_measurement, half_value)
    asset_serial_split_page.verify_line_values(1, 50, half_measurement, half_value)

    # Step 4: the totals are the whole asset
    asset_serial_split_page.verify_totals(100, LAND_VALUE, LAND_MEASUREMENT)


@pytest.mark.regression
def test_last_split_line_is_read_only(page, asset_serial_split_page, registrations, take_screenshot):
    """Asset Serial Split: the first line can be edited, the last line only takes the balance."""
    # Step 1: open the form and build two lines
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]
    asset_serial_split_page.open_split_form_for_serial(serial)
    asset_serial_split_page.build_split_lines(SPLIT_INTO)
    take_screenshot("two split lines built")

    # Step 2: line 1 is editable and line 2 (the last) is read-only
    asset_serial_split_page.verify_line_boxes_editable(0, True)
    asset_serial_split_page.verify_line_boxes_editable(1, False)


# ---------------------------------------------------------------------------
# 3. Reset and Back leave the asset unsplit
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_reset_clears_the_typed_split_values(page, asset_serial_split_page, registrations, take_screenshot):
    """Asset Serial Split: Reset sets the typed percentages and the totals back to zero and keeps the split lines."""
    # Step 1: open the form, build two lines and type 50 percent in line 1
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]
    asset_serial_split_page.open_split_form_for_serial(serial)
    asset_serial_split_page.build_split_lines(SPLIT_INTO)
    asset_serial_split_page.type_line_percentage(0, FIRST_LINE_PERCENTAGE)
    take_screenshot("50 percent typed before reset")

    # Step 2: click Reset; both lines and the totals are zero, the two lines and Split Into stay
    asset_serial_split_page.reset_form()
    take_screenshot("form after reset")
    asset_serial_split_page.verify_split_values_are_reset(int(SPLIT_INTO))


@pytest.mark.regression
def test_back_leaves_the_form_without_splitting(page, asset_serial_split_page, registrations, take_screenshot):
    """Asset Serial Split: Back closes the form and the Land asset can still be split."""
    # Step 1: open the form and build two lines
    serial = registrations.get_approved_of(LAND_SLOT)["serial"]
    asset_serial_split_page.open_split_form_for_serial(serial)
    asset_serial_split_page.build_split_lines(SPLIT_INTO)

    # Step 2: click Back; the form closes
    asset_serial_split_page.go_back()
    take_screenshot("back on the split screen")
    asset_serial_split_page.verify_form_closed()

    # Step 3: the Land asset still has its SPLIT button
    asset_serial_split_page.search_by_serial(serial)
    asset_serial_split_page.verify_split_button_shown(serial)


# ---------------------------------------------------------------------------
# 4. LAST: the real split (uses the Land asset up)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
def test_split_land_asset_and_submit(page, asset_serial_split_page, splits, take_screenshot):
    """Asset Serial Split: splitting the Land asset into 2 and submitting sends it for approval (PENDING)."""
    # Step 1: open the form of the saved Land asset
    land = splits.get_land()
    asset_serial_split_page.open_split_form_for_serial(land["serial"])

    # Step 2: type the remarks, build two lines and type 50 percent in line 1
    asset_serial_split_page.type_remarks(SPLIT_REMARKS)
    asset_serial_split_page.build_split_lines(SPLIT_INTO)
    asset_serial_split_page.type_line_percentage(0, FIRST_LINE_PERCENTAGE)
    take_screenshot("split form ready to submit")

    # Step 3: Submit; the success message is shown (when seen) and the Split screen returns
    asset_serial_split_page.submit_split()
    take_screenshot("split submitted")

    # Step 4: the serial is no longer on the Split screen
    asset_serial_split_page.navigate_here()
    asset_serial_split_page.search_by_serial(land["serial"])
    asset_serial_split_page.verify_serial_not_listed(land["serial"])

    # Step 5: the Split List shows a PENDING row; remember the split for the next test files
    splits.remember_submitted_split(land)
