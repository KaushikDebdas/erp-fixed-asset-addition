"""
test_02_asset_registration_list.py: tests for the Asset Registration List
screen (Fixed Asset > Registration > Asset Registration List), using the 10 AAQ
assets that test_01_asset_registration_aaq.py creates.

Built from automation/element_catalog/asset_registration_list.md. The 10
assets are remembered under AAQ_ASSET_GROUP (test_data/asset_registration_data.py).
When a test here runs on its own, the `registrations` fixture creates the asset
it needs, so every test can run alone.

The whole file logs in once and every test reuses that session (see the
`page` fixture below).

The tests run top to bottom:
    1. The Drafts planned as "draft_then_submit" are opened from the list and
       submitted, then shown as PENDING
    2. The page opens with the right columns, options and defaults
    3. Filters: Status, Registration Type, Project, Vendor, Registration
       Number, Created By and Registration Date
    4. Reset
    5. Paging
    6. The View popup of a registration

To run part of the file:
    pytest tests/test_02_asset_registration_list.py -k "gift"
    pytest tests/test_02_asset_registration_list.py -k "records_per_page"
"""
import pytest

from config.settings import TEST_USERNAME
from test_data.asset_registration_data import (
    AAQ_ASSET_GROUP,
    DRAFTS_SUBMITTED_FROM_LIST,
    build_registration_data,
)
from test_data.toast_messages import (
    SUBMIT_SUCCESS_TOAST,
)
from utils.run_context import trace_one_test

# Message (toast) the AAQ form shows after a Submit

# The tests that only need "a Draft" or "a submitted asset" all share one of each,
# so run alone this file creates as few registrations as possible (Spot Purchase)
SHARED_DRAFT_ITEM = "desktop"
SHARED_PENDING_ITEM = "land"

# Filter option lists the screen offers
STATUS_OPTIONS = ["-Select Status-", "PENDING", "APPROVED", "REJECTED", "DRAFT", "SENDBACK"]
REGISTRATION_TYPE_OPTIONS = ["-Select Registration Type-", "MRR", "AAQ", "LEASE"]
RECORDS_PER_PAGE_OPTIONS = ["10", "20", "30", "50", "100"]

# Column headings of the grid, in order
GRID_COLUMNS = [
    "SL", "Registration Number", "Registration Date", "Reference Number",
    "Registration Type", "Branch Name", "Project Name", "Department Name",
    "Created By", "Status", "Approved By", "Approval Date", "Attachment",
]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. Drafts are opened from the list and submitted
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
@DRAFTS_SUBMITTED_FROM_LIST
def test_list_draft_is_opened_and_submitted(
    item, sub_type, plan, page, aaq_page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration List: a Draft opened from its Registration Number link can be submitted."""
    # Step 1: get the Draft (created by test_01_asset_registration_aaq, or created now)
    draft = registrations.get_draft(item, sub_type, AAQ_ASSET_GROUP)

    # Step 2: find the Draft in the list; its status is DRAFT
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(draft["registration_number"])
    registration_list_page.verify_status(draft["registration_number"], "DRAFT")

    # Step 3: open it from its Registration Number link and submit it
    registration_list_page.open_registration(draft["registration_number"])
    take_screenshot(f"{sub_type} {item} draft opened from list")

    # Step 4: the form shows this Draft's own values
    aaq_page.verify_form_shows_registration(draft["data"])

    # Step 5: submit it and confirm the success message
    toast = aaq_page.click_submit_and_get_toast()
    take_screenshot(f"{sub_type} {item} draft submitted")
    aaq_page.verify_toast_text(toast, SUBMIT_SUCCESS_TOAST, "click submit")

    # Step 6: it is no longer a Draft; remember it as a submitted asset
    registrations.move_draft_to_pending(draft, AAQ_ASSET_GROUP)


@pytest.mark.regression
@DRAFTS_SUBMITTED_FROM_LIST
def test_list_submitted_draft_is_shown_as_pending(
    item, sub_type, plan, page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration List: a Draft that was submitted from the list now has status PENDING."""
    # Step 1: get the submitted asset (a new submitted one is created when this test runs alone)
    record = registrations.get_pending(item, sub_type, AAQ_ASSET_GROUP)

    # Step 2: find it in the list
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(record["registration_number"])
    take_screenshot(f"{sub_type} {item} found in list")

    # Step 3: its status is PENDING, and the row is this asset's (project and type)
    registration_list_page.verify_status(record["registration_number"], "PENDING")
    registration_list_page.verify_column_equals("Project Name", [record["data"]["project"]])
    registration_list_page.verify_column_equals("Registration Type", ["AAQ"])


# ---------------------------------------------------------------------------
# 2. The page opens with the right columns, options and defaults
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_list_grid_columns(page, registration_list_page, take_screenshot):
    """Asset Registration List: the grid shows the expected 13 columns, in order."""
    # Step 1: open the list
    registration_list_page.navigate_here()
    take_screenshot("list opened")

    # Step 2: the column headings are as expected
    registration_list_page.verify_headers(GRID_COLUMNS)


@pytest.mark.regression
def test_list_filter_options(page, registration_list_page, take_screenshot):
    """Asset Registration List: the Status, Registration Type and Records per page options are as expected."""
    # Step 1: open the list
    registration_list_page.navigate_here()

    # Step 2: each dropdown offers the expected values
    registration_list_page.verify_filter_options("Status", STATUS_OPTIONS)
    registration_list_page.verify_filter_options("Registration Type", REGISTRATION_TYPE_OPTIONS)
    registration_list_page.verify_filter_options("Records per page", RECORDS_PER_PAGE_OPTIONS)


@pytest.mark.regression
def test_list_starts_with_the_right_defaults(page, registration_list_page, take_screenshot):
    """Asset Registration List: Created By starts with the logged-in user and the other filters start empty."""
    # Step 1: open the list
    registration_list_page.navigate_here()
    take_screenshot("list opened")

    # Step 2: the Created By box holds the logged-in user's pin and name
    registration_list_page.verify_created_by_contains(TEST_USERNAME)

    # Step 3: Status, Registration Type and Registration Number are empty
    registration_list_page.verify_filters_are_empty(["Status", "Registration Type", "Registration Number"])


@pytest.mark.regression
def test_list_newest_registration_is_first(page, registration_list_page, take_screenshot):
    """Asset Registration List: registrations are listed newest first."""
    # Step 1: open the list
    registration_list_page.navigate_here()
    take_screenshot("list opened")

    # Step 2: the Registration Numbers on the first page go from high to low
    registration_list_page.verify_newest_first()


# ---------------------------------------------------------------------------
# 3. Filters
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_list_status_draft_lists_the_draft_asset(page, registrations, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by DRAFT lists only Drafts, including the Draft asset that was left as a Draft."""
    # Step 1: get the asset that stays a Draft (created now when this test runs alone)
    draft = registrations.get_draft(SHARED_DRAFT_ITEM, "spot", AAQ_ASSET_GROUP)

    # Step 2: open the list and filter by Status DRAFT
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("DRAFT")
    take_screenshot("list filtered by DRAFT")

    # Step 3: every row is a Draft, and the Draft asset is listed
    registration_list_page.verify_all_rows_have("Status", "DRAFT")
    assert registration_list_page.is_registration_listed(draft["registration_number"]), (
        f"Expected Registration {draft['registration_number']} in the DRAFT list."
    )


@pytest.mark.regression
def test_list_status_pending_lists_the_submitted_asset(page, registrations, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by PENDING lists only PENDING rows, including a submitted asset."""
    # Step 1: get a submitted asset (created now when this test runs alone)
    submitted = registrations.get_pending(SHARED_PENDING_ITEM, "spot", AAQ_ASSET_GROUP)

    # Step 2: open the list and filter by Status PENDING
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("PENDING")
    take_screenshot("list filtered by PENDING")

    # Step 3: every row is PENDING, and the submitted asset is listed
    registration_list_page.verify_all_rows_have("Status", "PENDING")
    assert registration_list_page.is_registration_listed(submitted["registration_number"]), (
        f"Expected Registration {submitted['registration_number']} in the PENDING list."
    )


@pytest.mark.regression
def test_list_filter_by_registration_type(page, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by Registration Type AAQ lists only AAQ registrations."""
    # Step 1: open the list and filter by the type
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_type("AAQ")
    take_screenshot("list filtered by AAQ")

    # Step 2: every row shows that Registration Type
    registration_list_page.verify_all_rows_have("Registration Type", "AAQ")


@pytest.mark.regression
def test_list_filter_by_project(page, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by Project lists only registrations of that project."""
    project = build_registration_data()["project"]

    # Step 1: open the list and filter by the project
    registration_list_page.navigate_here()
    registration_list_page.filter_by_project(project)
    take_screenshot("list filtered by project")

    # Step 2: there are rows, and every row shows that project
    registration_list_page.verify_rows_listed_and_all_have("Project Name", project)


@pytest.mark.regression
def test_list_filter_by_vendor_finds_registrations(page, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by a Vendor name lists that vendor's registrations."""
    vendor_name = build_registration_data()["vendor_name"]

    # Step 1: open the list and filter by the vendor's name
    registration_list_page.navigate_here()
    registration_list_page.filter_by_vendor(vendor_name)
    take_screenshot("list filtered by vendor")

    # Step 2: at least one registration is listed
    registration_list_page.verify_grid_has_rows(f"registrations for vendor '{vendor_name}'")


@pytest.mark.regression
def test_list_filter_by_unknown_vendor_lists_nothing(page, registration_list_page, take_screenshot):
    """Asset Registration List: a Vendor name nobody has lists nothing."""
    # Step 1: open the list and filter by a vendor that does not exist
    registration_list_page.navigate_here()
    registration_list_page.filter_by_vendor("NO_SUCH_VENDOR_ZZZ")
    take_screenshot("list filtered by unknown vendor")

    # Step 2: the grid is empty
    registration_list_page.verify_grid_is_empty("vendor NO_SUCH_VENDOR_ZZZ")


@pytest.mark.regression
def test_list_filter_by_registration_number_shows_the_registration(
    page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration List: filtering by a Registration Number lists exactly that registration."""
    # Step 1: get a submitted asset (created now when this test runs alone)
    record = registrations.get_pending(SHARED_PENDING_ITEM, "spot", AAQ_ASSET_GROUP)
    number = record["registration_number"]

    # Step 2: filter by its Registration Number
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(number)
    take_screenshot(f"list filtered by registration number {number}")

    # Step 3: one row, with this number, the project, type AAQ and Status PENDING
    registration_list_page.verify_column_equals("Registration Number", [number])
    registration_list_page.verify_column_equals("Project Name", [record["data"]["project"]])
    registration_list_page.verify_column_equals("Registration Type", ["AAQ"])
    registration_list_page.verify_column_equals("Status", ["PENDING"])


@pytest.mark.regression
def test_list_unknown_registration_number_lists_nothing(page, registration_list_page, take_screenshot):
    """Asset Registration List: a Registration Number that does not exist lists nothing."""
    # Step 1: open the list and filter by a number nobody has
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number("999999999")
    take_screenshot("list filtered by unknown registration number")

    # Step 2: the grid is empty
    registration_list_page.verify_grid_is_empty("Registration Number 999999999")


@pytest.mark.regression
def test_list_status_and_number_filters_work_together(page, registrations, registration_list_page, take_screenshot):
    """Asset Registration List: a PENDING registration is not listed when the Status filter is DRAFT."""
    # Step 1: get a submitted asset
    number = registrations.get_pending(SHARED_PENDING_ITEM, "spot", AAQ_ASSET_GROUP)["registration_number"]

    # Step 2: filter by its number and by Status DRAFT
    registration_list_page.navigate_here()
    registration_list_page.select_status("DRAFT")
    registration_list_page.filter_by_registration_number(number)
    take_screenshot("pending number with draft status")

    # Step 3: nothing is listed
    registration_list_page.verify_grid_is_empty(f"PENDING Registration Number {number} with Status DRAFT")


@pytest.mark.regression
def test_list_clearing_created_by_lists_other_users_too(page, registration_list_page, take_screenshot):
    """Asset Registration List: emptying Created By lists registrations made by everyone."""
    # Step 1: open the list and count the logged-in user's registrations
    registration_list_page.navigate_here()
    registration_list_page.search()
    own_total = registration_list_page.read_total_entries()
    take_screenshot("own registrations")

    # Step 2: empty Created By and search again
    registration_list_page.clear_created_by()
    registration_list_page.search()
    take_screenshot("everyone's registrations")

    # Step 3: more registrations are listed
    registration_list_page.verify_total_entries_above(own_total)


@pytest.mark.regression
def test_list_filter_by_registration_date(page, registrations, registration_list_page, take_screenshot):
    """Asset Registration List: the Registration From/To Date filters list only that day's registrations."""
    # Step 1: find the Registration Date of a known registration
    number = registrations.get_pending(SHARED_PENDING_ITEM, "spot", AAQ_ASSET_GROUP)["registration_number"]
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(number)
    registration_date = registration_list_page.read_first_value("Registration Date")

    # Step 2: clear the filters and set both dates to that day
    registration_list_page.reset_filters()
    registration_list_page.set_registration_dates(registration_date, registration_date)
    registration_list_page.search()
    take_screenshot(f"list filtered by registration date {registration_date}")

    # Step 3: every row shows that Registration Date
    registration_list_page.verify_rows_listed_and_all_have("Registration Date", registration_date)


# ---------------------------------------------------------------------------
# 4. Reset
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_list_reset_clears_every_filter(page, registration_list_page, take_screenshot):
    """Asset Registration List: Reset empties the filter boxes, Created By included."""
    # Step 1: open the list and fill several filters
    registration_list_page.navigate_here()
    registration_list_page.select_status("DRAFT")
    registration_list_page.select_registration_type("AAQ")
    registration_list_page.type_registration_number("757877")
    registration_list_page.type_vendor("ACE IT")
    take_screenshot("filters filled")

    # Step 2: click Reset
    registration_list_page.reset_filters()
    take_screenshot("filters reset")

    # Step 3: every filter box is empty
    registration_list_page.verify_filters_are_empty(
        ["Status", "Registration Type", "Registration Number", "Vendor", "Created By"]
    )


# ---------------------------------------------------------------------------
# 5. Paging
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.parametrize("size", [10, 20, 30, 50, 100])
def test_list_records_per_page(size, page, registration_list_page, take_screenshot):
    """Asset Registration List: Records per page sets how many rows the grid shows."""
    # Step 1: open the list, with Created By emptied so there are many registrations
    registration_list_page.navigate_here()
    registration_list_page.clear_created_by()
    registration_list_page.search()

    # Step 2: choose the page size
    registration_list_page.set_page_size(size)
    take_screenshot(f"{size} records per page")

    # Step 3: the grid shows that many rows, and the line under it agrees
    registration_list_page.verify_rows_per_page(size)


@pytest.mark.regression
def test_list_second_page_continues_the_list(page, registration_list_page, take_screenshot):
    """Asset Registration List: the second page shows the next 10 registrations."""
    # Step 1: open the list, with Created By emptied so there are many registrations
    registration_list_page.navigate_here()
    registration_list_page.clear_created_by()
    registration_list_page.search()
    first_page = registration_list_page.read_column("Registration Number")

    # Step 2: go to page 2
    registration_list_page.go_to_page(2)
    take_screenshot("second page")

    # Step 3: the line under the grid says 11 to 20 and the registrations are different, older ones
    registration_list_page.verify_second_page_continues(first_page)


# ---------------------------------------------------------------------------
# 6. The View popup
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_list_view_popup_shows_the_registration(page, registrations, registration_list_page, take_screenshot):
    """Asset Registration List: a Registration Number opens a popup with every value that was entered."""
    # Step 1: get a submitted asset (created now when this test runs alone)
    record = registrations.get_pending(SHARED_PENDING_ITEM, "spot", AAQ_ASSET_GROUP)
    data = record["data"]
    number = record["registration_number"]

    # Step 2: find it in the list and open its popup
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(number)
    registration_list_page.open_registration_popup(number)
    take_screenshot(f"popup of registration {number}")

    # Step 3: the popup shows the values that were entered (it shortens a long specification)
    registration_list_page.verify_popup_contains([
        number, data["project"], data["remarks"], data["vendor_name"], data["vendor_number"],
        data["grid_item_name"], data["item_specification"][:30], str(data["quantity"]),
        str(data["unit_price"]),
    ])
