"""
test_02_asset_registration_list.py: tests for the Asset Registration List
screen (Fixed Asset > Registration > Asset Registration List).

Built from automation/element_catalog/asset_registration_list.md. The list
only shows registrations that already exist, so the smoke tests first create
one on the AAQ form. The regression tests below get a registration from the
`registrations` fixture (conftest.py), which reuses one an earlier test made
or creates its own when run alone.

Order of the file: 0. smoke, 1. columns/options/defaults, 2. filters,
3. Reset, 4. paging, 5. the View popup for each of the 5 asset items.
"""
import pytest

from config.settings import TEST_USERNAME
from test_data.asset_items import ASSET_ITEMS
from test_data.asset_registration_data import build_registration_data
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_list_shows_new_draft_registration(
    page, aaq_page, registration_list_page, take_screenshot
):
    """Asset Registration List: a saved Draft appears with Status DRAFT."""
    # Step 1: create a Draft registration on the AAQ form
    aaq_page.navigate_here()
    aaq_page.create_draft(build_registration_data())

    # Step 2: open the list and filter by Status DRAFT
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("DRAFT")
    take_screenshot("list filtered by draft status")

    # Step 3: the newest row is the registration just created, with Status DRAFT
    registration_number = registration_list_page.get_newest_registration_number()
    registration_list_page.verify_status(registration_number, "DRAFT")
    take_screenshot(f"registration {registration_number} found as DRAFT")


@pytest.mark.regression
def test_list_filter_by_registration_number(
    page, aaq_page, registration_list_page, take_screenshot
):
    """Asset Registration List: filtering by Registration Number finds exactly that registration."""
    # Step 1: create a Draft registration on the AAQ form
    aaq_page.navigate_here()
    aaq_page.create_draft(build_registration_data())

    # Step 2: find its Registration Number in the list
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("DRAFT")
    registration_number = registration_list_page.get_newest_registration_number()

    # Step 3: search by that Registration Number alone
    registration_list_page.filter_by_registration_number(registration_number)
    take_screenshot(f"list filtered by registration number {registration_number}")

    # Step 4: the registration is listed with Status DRAFT
    assert registration_list_page.is_registration_listed(registration_number), (
        f"Expected Registration {registration_number} to be listed after filtering by its number."
    )
    registration_list_page.verify_status(registration_number, "DRAFT")


@pytest.mark.regression
def test_list_open_draft_and_submit_moves_to_pending(
    page, aaq_page, registration_list_page, take_screenshot
):
    """Asset Registration List: a Draft can be reopened from the list and submitted, moving it to PENDING."""
    # Step 1: create a Draft registration on the AAQ form
    aaq_page.navigate_here()
    aaq_page.create_draft(build_registration_data())

    # Step 2: find the Draft in the list
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("DRAFT")
    registration_number = registration_list_page.get_newest_registration_number()
    registration_list_page.verify_status(registration_number, "DRAFT")

    # Step 3: reopen the Draft from its Registration Number link and submit it
    registration_list_page.open_registration(registration_number)
    take_screenshot(f"draft {registration_number} reopened for update")
    aaq_page.submit_and_verify_success()

    # Step 4: the list now shows the registration as PENDING
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("PENDING")
    registration_list_page.verify_status(registration_number, "PENDING")
    take_screenshot(f"registration {registration_number} confirmed as PENDING")


@pytest.mark.regression
def test_list_submitted_registration_is_pending(
    page, aaq_page, registration_list_page, take_screenshot
):
    """Asset Registration List: a directly submitted registration appears with Status PENDING."""
    # Step 1: create and submit a registration on the AAQ form
    aaq_page.navigate_here()
    aaq_page.create_and_submit(build_registration_data())

    # Step 2: open the list and filter by Status PENDING
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("PENDING")
    take_screenshot("list filtered by pending status")

    # Step 3: the newest row is the registration just submitted, with Status PENDING
    registration_number = registration_list_page.get_newest_registration_number()
    registration_list_page.verify_status(registration_number, "PENDING")


# ---------------------------------------------------------------------------
# 1. The page opens with the right columns, options and defaults
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_list_grid_columns(page, registration_list_page, take_screenshot):
    """Asset Registration List: the grid shows the expected 13 columns, in order."""
    # Step 1: open the list
    registration_list_page.navigate_here()
    take_screenshot("list opened")

    # Step 2: the column headings are as expected
    registration_list_page.verify_headers([
        "SL", "Registration Number", "Registration Date", "Reference Number",
        "Registration Type", "Branch Name", "Project Name", "Department Name",
        "Created By", "Status", "Approved By", "Approval Date", "Attachment",
    ])


@pytest.mark.regression
def test_list_status_filter_options(page, registration_list_page, take_screenshot):
    """Asset Registration List: the Status filter offers PENDING, APPROVED, REJECTED, DRAFT and SENDBACK."""
    # Step 1: open the list
    registration_list_page.navigate_here()

    # Step 2: the Status options are as expected
    registration_list_page.verify_filter_options(
        "Status", ["-Select Status-", "PENDING", "APPROVED", "REJECTED", "DRAFT", "SENDBACK"]
    )


@pytest.mark.regression
def test_list_registration_type_filter_options(page, registration_list_page, take_screenshot):
    """Asset Registration List: the Registration Type filter offers MRR, AAQ and LEASE."""
    # Step 1: open the list
    registration_list_page.navigate_here()

    # Step 2: the Registration Type options are as expected
    registration_list_page.verify_filter_options(
        "Registration Type", ["-Select Registration Type-", "MRR", "AAQ", "LEASE"]
    )


@pytest.mark.regression
def test_list_records_per_page_options(page, registration_list_page, take_screenshot):
    """Asset Registration List: Records per page offers 10, 20, 30, 50 and 100."""
    # Step 1: open the list
    registration_list_page.navigate_here()

    # Step 2: the page size options are as expected
    registration_list_page.verify_filter_options("Records per page", ["10", "20", "30", "50", "100"])


@pytest.mark.regression
def test_list_created_by_starts_with_logged_in_user(page, registration_list_page, take_screenshot):
    """Asset Registration List: the Created By filter starts with the logged-in user."""
    # Step 1: open the list
    registration_list_page.navigate_here()
    take_screenshot("list opened")

    # Step 2: the Created By box holds the logged-in user's pin and name
    registration_list_page.verify_created_by_contains(TEST_USERNAME)


@pytest.mark.regression
def test_list_other_filters_start_empty(page, registration_list_page, take_screenshot):
    """Asset Registration List: Status, Registration Type and Registration Number start empty."""
    # Step 1: open the list
    registration_list_page.navigate_here()

    # Step 2: none of those filters has a value
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
# 2. Filters
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.parametrize("status", ["PENDING", "APPROVED", "REJECTED", "DRAFT", "SENDBACK"])
def test_list_filter_by_status(status, page, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by a Status lists only registrations with that Status."""
    # Step 1: open the list and filter by the Status
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status(status)
    take_screenshot(f"list filtered by {status}")

    # Step 2: every row shows that Status (a Status with no registrations lists nothing)
    registration_list_page.verify_all_rows_have("Status", status)


@pytest.mark.regression
@pytest.mark.parametrize("registration_type", ["AAQ", "MRR", "LEASE"])
def test_list_filter_by_registration_type(registration_type, page, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by a Registration Type lists only that type."""
    # Step 1: open the list and filter by the type
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_type(registration_type)
    take_screenshot(f"list filtered by {registration_type}")

    # Step 2: every row shows that Registration Type
    registration_list_page.verify_all_rows_have("Registration Type", registration_type)


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
@pytest.mark.xfail(
    reason="Search ignores the MRR Number filter: the same registrations are listed with a real "
           "MRR number, a made-up one, or none. Needs a product decision.",
    strict=True,
)
def test_list_filter_by_mrr_number(page, registration_list_page, take_screenshot):
    """Asset Registration List: filtering by an MRR Number lists only registrations with that reference."""
    # Step 1: list MRR registrations of every user and pick a Reference Number
    registration_list_page.navigate_here()
    registration_list_page.clear_created_by()
    registration_list_page.filter_by_registration_type("MRR")
    mrr_number = registration_list_page.read_first_filled_value("Reference Number")

    # Step 2: filter by that MRR Number
    registration_list_page.filter_by_mrr_number(mrr_number)
    take_screenshot(f"list filtered by MRR number {mrr_number}")

    # Step 3: every row shows that Reference Number
    registration_list_page.verify_rows_listed_and_all_have("Reference Number", mrr_number)


@pytest.mark.regression
@ASSET_ITEMS
def test_list_filter_by_registration_number_shows_the_registration(
    item, page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration List: filtering by a Registration Number lists exactly that registration."""
    # Step 1: get a submitted registration (reused from an earlier test, or created now)
    record = registrations.get_pending(item)
    data = record["data"]
    number = record["registration_number"]

    # Step 2: filter by its Registration Number
    registration_list_page.navigate_here()
    registration_list_page.filter_by_registration_number(number)
    take_screenshot(f"list filtered by registration number {number}")

    # Step 3: one row, with this number, the project, type AAQ and Status PENDING
    registration_list_page.verify_column_equals("Registration Number", [number])
    registration_list_page.verify_column_equals("Project Name", [data["project"]])
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
    # Step 1: get a submitted registration
    number = registrations.get_pending("furniture")["registration_number"]

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
    number = registrations.get_pending("furniture")["registration_number"]
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


@pytest.mark.regression
def test_list_filter_by_approve_date(page, registration_list_page, take_screenshot):
    """Asset Registration List: the Approve From/To Date filters list only registrations approved that day."""
    # Step 1: find the Approval Date of an approved registration
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("APPROVED")
    approval_date = registration_list_page.read_first_filled_value("Approval Date")
    if approval_date == "":
        pytest.skip("No approved registration with an Approval Date to filter by.")

    # Step 2: clear the filters and set both approve dates to that day
    registration_list_page.reset_filters()
    registration_list_page.set_approve_dates(approval_date, approval_date)
    registration_list_page.search()
    take_screenshot(f"list filtered by approve date {approval_date}")

    # Step 3: every row shows that Approval Date
    registration_list_page.verify_rows_listed_and_all_have("Approval Date", approval_date)


# ---------------------------------------------------------------------------
# 3. Reset
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
# 4. Paging
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
# 5. The View popup, for each of the 5 asset items
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ASSET_ITEMS
def test_list_view_popup_shows_the_registration(
    item, page, registrations, registration_list_page, take_screenshot
):
    """Asset Registration List: a Registration Number opens a popup with every value that was entered."""
    # Step 1: get a submitted registration (reused from an earlier test, or created now)
    record = registrations.get_pending(item)
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
    registration_list_page.close_popup()
