"""
test_03_asset_registration_approval_list.py: tests for the Asset
Registration Approval List screen (Fixed Asset > Registration > Asset
Registration Approval List), using the 10 AAQ assets that
test_01_asset_registration_aaq.py creates and
test_02_asset_registration_list.py submits.

Built from automation/element_catalog/asset_registration_approval_list.md.
The 8 submitted assets (4 items, Spot Purchase and Gift Item) are approved
here: 6 one by one from their popup, 2 together with ticked rows. The 2 assets
saved as Drafts are not submitted, so they never reach this list. Every asset
is remembered as APPROVED, with its Asset Serial, under AAQ_ASSET_GROUP
(test_data/asset_registration_data.py), so later tests can reuse it:
    registrations.get_approved("land", "gift", AAQ_ASSET_GROUP)
When a test here runs on its own, the `registrations` fixture creates the asset
it needs, so every test can run alone.

The whole file logs in once and every test reuses that session (see the
`page` fixture below).

The tests run top to bottom:
    1. Before approval: each submitted asset is listed with the right data and
       a popup that shows what was entered; Drafts are not listed; the Comment
       box; Status plus number; nothing ticked; select all
    2. The page opens with the right columns, options and defaults
    3. Filters: Status, Registration Type, Project, Vendor, Registration
       Number and Registration Date; Reset; paging
    4. Approve: 6 assets from the popup (with a comment), 2 with ticked rows
    5. After approval: each asset is APPROVED with an approver and a date, its
       popup lists its Asset Serial and has no Approve button; Approve Date filter
    6. The voucher: no voucher exists while a registration is a Draft or PENDING;
       after approval Accounting > Voucher Search finds a voucher for each
       registration number, and its Preview PDF is that registration's voucher

There is no Reject step: the Approval List has no Reject button (checked 2026-10-05).

To run part of the file:
    pytest tests/test_03_asset_registration_approval_list.py -k "gift"
    pytest tests/test_03_asset_registration_approval_list.py -k "land-spot"
"""
import pytest

from test_data.asset_registration_data import (
    AAQ_ASSET_GROUP,
    AAQ_PENDING_GROUP,
    build_asset_data,
    build_registration_voucher,
)
from test_data.toast_messages import (
    APPROVE_SUCCESS_TOAST,
    NOTHING_TICKED_TOAST,
)
from utils.run_context import trace_one_test

# Messages (toasts) the screen shows

# Comment typed when an asset is approved from its popup
APPROVE_COMMENT = "AUTOMATION_TEST approve comment"

# The assets approved from their popup, and the two approved together with ticked rows
POPUP_APPROVED_ROWS = [
    ("furniture", "spot"),
    ("land", "spot"),
    ("building", "spot"),
    ("laptop", "spot"),
    ("furniture", "gift"),
    ("land", "gift"),
]
BULK_APPROVED_ROWS = [
    ("building", "gift"),
    ("laptop", "gift"),
]
SUBMITTED_ROWS = POPUP_APPROVED_ROWS + BULK_APPROVED_ROWS

# Put above a test to run it for every submitted asset, or only for the popup-approved ones
SUBMITTED_ASSETS = pytest.mark.parametrize("item, sub_type", SUBMITTED_ROWS)
POPUP_APPROVED_ASSETS = pytest.mark.parametrize("item, sub_type", POPUP_APPROVED_ROWS)

# The asset the tests share when they only need "a submitted asset" or "an approved asset"
SHARED_ITEM = "furniture"

# Filter option lists the screen offers (no DRAFT: Drafts are not shown here)
STATUS_OPTIONS = ["-Select Status-", "PENDING", "APPROVED", "REJECTED", "SENDBACK"]
REGISTRATION_TYPE_OPTIONS = ["-Select Registration Type-", "MRR", "AAQ", "LEASE"]
RECORDS_PER_PAGE_OPTIONS = ["10", "20", "30", "50", "100"]

# Column headings of the grid, in order (the first is the tick box column)
GRID_COLUMNS = [
    "", "SL", "Registration Number", "Registration Date", "Reference Number",
    "Registration Type", "Branch Name", "Project Name", "Department Name",
    "Created By", "Status", "Approved By", "Approval Date", "Attachment", "Approve",
]


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


# ---------------------------------------------------------------------------
# 1. Before approval
# ---------------------------------------------------------------------------


@pytest.mark.regression
@SUBMITTED_ASSETS
def test_approval_submitted_asset_is_listed(item, sub_type, page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: a submitted asset is listed as PENDING with its project, type AAQ and a tick box."""
    # Step 1: get the submitted asset (created by an earlier test, or created now)
    record = registrations.get_pending(item, sub_type, AAQ_ASSET_GROUP)
    number = record["registration_number"]

    # Step 2: filter the approval list by its Registration Number
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    take_screenshot(f"{sub_type} {item} found in approval list")

    # Step 3: one row with this number, its project, type AAQ and status PENDING, ready to be ticked
    approval_list_page.verify_registration_row(number, record["data"]["project"], "AAQ", "PENDING")
    approval_list_page.verify_row_has_checkbox(number)


@pytest.mark.regression
@SUBMITTED_ASSETS
def test_approval_popup_shows_the_asset_values(item, sub_type, page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the popup shows every value that was entered for the asset."""
    # Step 1: get the submitted asset
    record = registrations.get_pending(item, sub_type, AAQ_ASSET_GROUP)
    number = record["registration_number"]
    data = record["data"]

    # Step 2: open its popup from the approval list
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    take_screenshot(f"popup of {sub_type} {item} registration {number}")

    # Step 3: the popup is for this registration and shows the values that were entered
    approval_list_page.verify_popup_registration_number(number)
    approval_list_page.verify_popup_details([
        number, data["project"], data["remarks"], data["vendor_name"], data["vendor_number"],
        data["grid_item_name"], data["item_specification"][:30], str(data["quantity"]),
        str(data["unit_price"]),
    ])


@pytest.mark.regression
@pytest.mark.parametrize("sub_type", ["spot", "gift"])
def test_approval_asset_serials_are_empty_before_approval(
    sub_type, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: a pending registration has no Asset Serial yet."""
    # Step 1: get a submitted asset
    number = registrations.get_pending("land", sub_type, AAQ_ASSET_GROUP)["registration_number"]

    # Step 2: open its popup and switch to the Asset Serials tab
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    approval_list_page.open_asset_serials_tab()
    take_screenshot(f"{sub_type} asset serials tab before approval")

    # Step 3: no serial number exists yet
    approval_list_page.verify_asset_serials_empty()


@pytest.mark.regression
def test_approval_draft_asset_is_not_listed(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: an asset saved as a Draft is not listed, because it was never submitted."""
    # Step 1: get the asset that stays a Draft (created now when this test runs alone)
    number = registrations.get_draft("desktop", "spot", AAQ_ASSET_GROUP)["registration_number"]

    # Step 2: filter the approval list by its Registration Number
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    take_screenshot("draft registration searched in approval list")

    # Step 3: nothing is listed
    approval_list_page.verify_grid_is_empty()


@pytest.mark.regression
def test_approval_comment_box_keeps_500_characters(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the popup's Comment box keeps at most 500 characters."""
    # Step 1: open the popup of a submitted registration
    number = registrations.get_pending(SHARED_ITEM, "spot", AAQ_ASSET_GROUP)["registration_number"]
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)

    # Step 2: type 600 characters
    approval_list_page.enter_comment("C" * 600)
    take_screenshot("600 characters typed in the comment box")

    # Step 3: only 500 are kept
    approval_list_page.verify_comment_length(500)


@pytest.mark.regression
def test_approval_status_and_number_filters_work_together(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: a PENDING registration is not listed when the Status filter is APPROVED."""
    # Step 1: get a submitted asset
    number = registrations.get_pending(SHARED_ITEM, "spot", AAQ_ASSET_GROUP)["registration_number"]

    # Step 2: filter by its number and by Status APPROVED
    approval_list_page.navigate_here()
    approval_list_page.select_status("APPROVED")
    approval_list_page.filter_by_registration_number(number)
    take_screenshot("pending number with approved status")

    # Step 3: nothing is listed
    approval_list_page.verify_grid_is_empty()


@pytest.mark.regression
def test_approval_filter_by_registration_date(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the Registration From/To Date filters list only that day's registrations."""
    # Step 1: find the Registration Date of a known registration
    number = registrations.get_pending(SHARED_ITEM, "spot", AAQ_ASSET_GROUP)["registration_number"]
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    registration_date = approval_list_page.read_first_value("Registration Date")

    # Step 2: clear the filters and set both dates to that day
    approval_list_page.reset_filters()
    approval_list_page.set_registration_dates(registration_date, registration_date)
    approval_list_page.search()
    take_screenshot(f"approval list filtered by registration date {registration_date}")

    # Step 3: there are rows, and every row shows that Registration Date
    approval_list_page.verify_all_rows_have("Registration Date", registration_date, must_have_rows=True)


@pytest.mark.regression
def test_approval_nothing_ticked_asks_for_a_selection(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: Approve with no row ticked asks for a registration."""
    # Step 1: open the approval list and show the pending registrations
    approval_list_page.navigate_here()
    approval_list_page.filter_by_status("PENDING")

    # Step 2: click Approve without ticking a row
    approval_list_page.approve_ticked_rows()
    take_screenshot("approve with nothing ticked")

    # Step 3: the selection message is shown
    approval_list_page.verify_toast(NOTHING_TICKED_TOAST)


@pytest.mark.regression
def test_approval_select_all_ticks_every_row(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the header tick box ticks every row, and unticking clears them."""
    # Step 1: open the approval list and show the pending registrations
    approval_list_page.navigate_here()
    approval_list_page.filter_by_status("PENDING")

    # Step 2: tick the header box, every row on the page is ticked
    approval_list_page.tick_select_all()
    take_screenshot("select all ticked")
    approval_list_page.verify_all_rows_ticked()

    # Step 3: untick the header box, no row is ticked
    approval_list_page.untick_select_all()
    approval_list_page.verify_no_rows_ticked()


# ---------------------------------------------------------------------------
# 2. The page opens with the right columns, options and defaults
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_approval_grid_columns(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the grid shows the expected columns, in order."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()
    take_screenshot("approval list opened")

    # Step 2: the column headings are as expected
    approval_list_page.verify_headers(GRID_COLUMNS)


@pytest.mark.regression
def test_approval_filter_options(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the Status, Registration Type and Records per page options are as expected."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()

    # Step 2: each dropdown offers the expected values
    approval_list_page.verify_filter_options("Status", STATUS_OPTIONS)
    approval_list_page.verify_filter_options("Registration Type", REGISTRATION_TYPE_OPTIONS)
    approval_list_page.verify_page_size_options(RECORDS_PER_PAGE_OPTIONS)


@pytest.mark.regression
def test_approval_filters_start_empty(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: every filter starts empty, Created By included."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()
    take_screenshot("approval list opened")

    # Step 2: no filter has a value
    approval_list_page.verify_filters_empty(
        ["Status", "Registration Type", "Registration Number", "Created By", "Approved By"]
    )


@pytest.mark.regression
def test_approval_newest_registration_is_first(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: registrations are listed newest first."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()

    # Step 2: the Registration Numbers on the first page go from high to low
    approval_list_page.verify_newest_first()


# ---------------------------------------------------------------------------
# 3. Filters, Reset and paging
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.parametrize("status", ["PENDING", "APPROVED", "REJECTED", "SENDBACK"])
def test_approval_filter_by_status(status, page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by a Status lists only registrations with that Status."""
    # Step 1: open the approval list and filter by the Status
    approval_list_page.navigate_here()
    approval_list_page.filter_by_status(status)
    take_screenshot(f"approval list filtered by {status}")

    # Step 2: every row shows that Status (a Status with no registrations lists nothing)
    approval_list_page.verify_all_rows_have("Status", status)


@pytest.mark.regression
def test_approval_filter_by_registration_type(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by Registration Type AAQ lists only AAQ registrations."""
    # Step 1: open the approval list and filter by the type
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_type("AAQ")
    take_screenshot("approval list filtered by AAQ")

    # Step 2: every row shows that Registration Type
    approval_list_page.verify_all_rows_have("Registration Type", "AAQ")


@pytest.mark.regression
def test_approval_filter_by_project(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by Project lists only registrations of that project."""
    project = build_asset_data(SHARED_ITEM)["project"]

    # Step 1: open the approval list and filter by the project
    approval_list_page.navigate_here()
    approval_list_page.filter_by_project(project)
    take_screenshot("approval list filtered by project")

    # Step 2: there are rows, and every row shows that project
    approval_list_page.verify_all_rows_have("Project Name", project, must_have_rows=True)


@pytest.mark.regression
def test_approval_filter_by_vendor_finds_registrations(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by a Vendor name lists that vendor's registrations."""
    vendor_name = build_asset_data(SHARED_ITEM)["vendor_name"]

    # Step 1: open the approval list and filter by the vendor's name
    approval_list_page.navigate_here()
    approval_list_page.filter_by_vendor(vendor_name)
    take_screenshot("approval list filtered by vendor")

    # Step 2: at least one registration is listed
    approval_list_page.verify_grid_has_rows(f"vendor '{vendor_name}'")


@pytest.mark.regression
def test_approval_filter_by_unknown_vendor_lists_nothing(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: a Vendor name nobody has lists nothing."""
    # Step 1: open the approval list and filter by a vendor that does not exist
    approval_list_page.navigate_here()
    approval_list_page.filter_by_vendor("NO_SUCH_VENDOR_ZZZ")
    take_screenshot("approval list filtered by unknown vendor")

    # Step 2: the grid is empty
    approval_list_page.verify_grid_is_empty()


@pytest.mark.regression
def test_approval_unknown_registration_number_lists_nothing(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: a Registration Number that does not exist lists nothing."""
    # Step 1: open the approval list and filter by a number nobody has
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number("999999999")
    take_screenshot("approval list filtered by unknown registration number")

    # Step 2: the grid is empty
    approval_list_page.verify_grid_is_empty()


@pytest.mark.regression
def test_approval_reset_clears_every_filter(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: Reset empties the filter boxes."""
    # Step 1: open the approval list and fill several filters
    approval_list_page.navigate_here()
    approval_list_page.select_status("PENDING")
    approval_list_page.select_registration_type("AAQ")
    approval_list_page.type_registration_number("757877")
    approval_list_page.type_vendor_name("ACE IT")
    take_screenshot("filters filled")

    # Step 2: click Reset
    approval_list_page.reset_filters()
    take_screenshot("filters reset")

    # Step 3: every filter box is empty
    approval_list_page.verify_filters_empty(["Status", "Registration Type", "Registration Number", "Vendor"])


@pytest.mark.regression
@pytest.mark.parametrize("size", [10, 20, 30, 50, 100])
def test_approval_records_per_page(size, page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: Records per page sets how many rows the grid shows."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()

    # Step 2: choose the page size
    approval_list_page.set_page_size(size)
    take_screenshot(f"{size} records per page")

    # Step 3: the grid shows that many rows, and the line under it agrees
    approval_list_page.verify_rows_per_page(size)


@pytest.mark.regression
def test_approval_second_page_continues_the_list(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the second page shows the next 10 registrations."""
    # Step 1: open the approval list and read the first page
    approval_list_page.navigate_here()
    first_page = approval_list_page.read_column("Registration Number")

    # Step 2: go to page 2
    approval_list_page.go_to_page(2)
    take_screenshot("second page")

    # Step 3: the line under the grid says 11 to 20 and the registrations are different, older ones
    approval_list_page.verify_entries_info_starts_with("Showing 11 to 20 of")
    second_page = approval_list_page.read_column("Registration Number")
    approval_list_page.verify_page_two_is_older(first_page, second_page)


# ---------------------------------------------------------------------------
# 4. Approve (each approval uses up a PENDING asset, so it is remembered as APPROVED)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.regression
@POPUP_APPROVED_ASSETS
def test_approval_approve_asset_from_its_popup(item, sub_type, page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: a pending asset is approved from its popup with a comment, and gets an Asset Serial."""
    # Step 1: get the submitted asset (created by an earlier test, or created now)
    record = registrations.get_pending(item, sub_type, AAQ_ASSET_GROUP)
    number = record["registration_number"]

    # Step 2: open its popup, check it is this registration and type a comment
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    approval_list_page.verify_popup_registration_number(number)
    approval_list_page.enter_comment(APPROVE_COMMENT)
    take_screenshot(f"{sub_type} {item} popup with comment")

    # Step 3: approve it and read the Asset Serial that approval created
    approval_list_page.approve_from_popup_and_verify_success(number)
    serial = approval_list_page.read_asset_serial_of(number)
    take_screenshot(f"{sub_type} {item} approved, serial {serial}")

    # Step 4: it is no longer PENDING; remember it as APPROVED for later tests
    registrations.move_to_approved(record, serial, AAQ_ASSET_GROUP)


@pytest.mark.regression
def test_approval_bulk_approve_ticked_rows(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: two ticked registrations are approved together."""
    # Step 1: get the two submitted assets that are approved together
    first = registrations.get_pending(BULK_APPROVED_ROWS[0][0], BULK_APPROVED_ROWS[0][1], AAQ_ASSET_GROUP)
    second = registrations.get_pending(BULK_APPROVED_ROWS[1][0], BULK_APPROVED_ROWS[1][1], AAQ_ASSET_GROUP)

    # Step 2: show the pending registrations and tick both
    approval_list_page.navigate_here()
    approval_list_page.filter_by_status("PENDING")
    approval_list_page.select_row_checkbox(first["registration_number"])
    approval_list_page.select_row_checkbox(second["registration_number"])
    take_screenshot("two registrations ticked")

    # Step 3: Approve shows the success message
    approval_list_page.approve_ticked_rows()
    take_screenshot("bulk approve done")
    approval_list_page.verify_toast(APPROVE_SUCCESS_TOAST)

    # Step 4: both now show APPROVED; remember them with their Asset Serials
    for record in [first, second]:
        approval_list_page.verify_registration_is_approved(record["registration_number"])
        serial = approval_list_page.read_asset_serial_of(record["registration_number"])
        registrations.move_to_approved(record, serial, AAQ_ASSET_GROUP)


# ---------------------------------------------------------------------------
# 5. After approval
# ---------------------------------------------------------------------------


@pytest.mark.regression
@SUBMITTED_ASSETS
def test_approval_approved_asset_row(item, sub_type, page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: an approved asset shows APPROVED, who approved it and when, and has no tick box."""
    # Step 1: get the approved asset (approved above, or created and approved now)
    number = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)["registration_number"]

    # Step 2: find it in the approval list
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    take_screenshot(f"{sub_type} {item} approved registration {number} in the list")

    # Step 3: the row shows APPROVED, an approver and a dd/mm/yyyy date, and cannot be ticked
    approval_list_page.verify_approved_row(number)


@pytest.mark.regression
@SUBMITTED_ASSETS
def test_approval_asset_serial_is_shown_after_approval(
    item, sub_type, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: an approved registration's popup lists its Asset Serial."""
    # Step 1: get the approved asset and the serial that was recorded when it was approved
    record = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)

    # Step 2: open its popup and switch to the Asset Serials tab
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(record["registration_number"])
    approval_list_page.open_asset_serials_tab()
    take_screenshot(f"{sub_type} {item} asset serials tab after approval")

    # Step 3: the serial is there and is the one approval created
    approval_list_page.verify_asset_serial_shown(record["serial"])


@pytest.mark.regression
def test_approval_approved_popup_has_no_approve_button(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the popup of an approved registration has no Approve button."""
    # Step 1: get an approved registration and open its popup
    number = registrations.get_approved(SHARED_ITEM, "spot", AAQ_ASSET_GROUP)["registration_number"]
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    take_screenshot("popup of an approved registration")

    # Step 2: the Approve button is not shown
    approval_list_page.verify_popup_has_no_approve_button()


@pytest.mark.regression
def test_approval_filter_by_approve_date(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the Approve From/To Date filters list only registrations approved that day."""
    # Step 1: find the Approval Date of an approved registration
    number = registrations.get_approved(SHARED_ITEM, "spot", AAQ_ASSET_GROUP)["registration_number"]
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    approval_date = approval_list_page.read_first_value("Approval Date")

    # Step 2: clear the filters and set both approve dates to that day
    approval_list_page.reset_filters()
    approval_list_page.set_approve_dates(approval_date, approval_date)
    approval_list_page.search()
    take_screenshot(f"approval list filtered by approve date {approval_date}")

    # Step 3: there are rows, and every row shows that Approval Date
    approval_list_page.verify_all_rows_have("Approval Date", approval_date, must_have_rows=True)


# ---------------------------------------------------------------------------
# 6. The voucher each approval creates (Accounting > Voucher Search)
# ---------------------------------------------------------------------------


@pytest.mark.regression
@SUBMITTED_ASSETS
def test_approval_creates_the_registration_voucher(
    item, sub_type, page, registrations, approval_list_page, voucher_search_page, take_screenshot
):
    """Voucher Search: an approved registration has a voucher, and its Preview PDF is that registration's voucher."""
    # Step 1: get the approved asset (approved above, or created and approved now)
    record = registrations.get_approved(item, sub_type, AAQ_ASSET_GROUP)
    number = record["registration_number"]

    # Step 2: read the day it was approved in the approval list; the voucher is dated that day
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    approval_date = approval_list_page.read_first_value("Approval Date")

    # Step 3: in Accounting > Voucher Search, search by the Registration Number as the Transaction No
    voucher_search_page.navigate_here()
    voucher_search_page.search_by_transaction_no(number)
    take_screenshot(f"{sub_type} {item} voucher found for registration {number}")

    # Step 4: the search row and the Preview PDF are this registration's voucher
    expected = build_registration_voucher(record["data"], approval_date)
    voucher_search_page.verify_registration_voucher(number, expected)


@pytest.mark.regression
@pytest.mark.parametrize("status", ["DRAFT", "PENDING"])
@pytest.mark.parametrize("sub_type", ["spot", "gift"])
def test_no_voucher_before_approval(status, sub_type, page, registrations, voucher_search_page, take_screenshot):
    """Voucher Search: a registration that is a Draft or still PENDING has no voucher."""
    # Step 1: get an asset that is not approved (a Draft, or one that stays PENDING)
    if status == "DRAFT":
        record = registrations.get_draft("desktop", sub_type, AAQ_ASSET_GROUP)
    else:
        record = registrations.get_pending("furniture", sub_type, AAQ_PENDING_GROUP)
    number = record["registration_number"]

    # Step 2: in Accounting > Voucher Search, search by its Registration Number as the Transaction No
    voucher_search_page.navigate_here()
    voucher_search_page.search_by_transaction_no(number)
    take_screenshot(f"{sub_type} {status} registration {number} searched in voucher search")

    # Step 3: no voucher was created for it
    voucher_search_page.verify_no_voucher(number)
