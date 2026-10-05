"""
test_03_asset_registration_approval_list.py: tests for the Asset
Registration Approval List screen (Fixed Asset > Registration > Asset
Registration Approval List).

Built from automation/element_catalog/asset_registration_approval_list.md.
The approval list only shows submitted registrations, so the smoke tests
first create and submit one on the AAQ form. The regression tests below
reuse a registration an earlier test made (see the `registrations` fixture
in conftest.py) or create their own when run alone.

Order of the file: 0. smoke, 1. columns/options/defaults, 2. filters,
3. Reset, 4. paging, 5. the View popup, 6. Approve. Approving uses up a
PENDING registration, so those tests tell `registrations` that it is now
APPROVED.
"""
import pytest

from test_data.asset_registration_data import ASSET_ITEMS, build_asset_data, build_registration_data
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


def submit_new_registration(aaq_page, registration_list_page, data) -> str:
    """
    Submit a new registration on the AAQ form and return its Registration
    Number (read from the list, because the AAQ form does not show the
    number it just created).
    """
    aaq_page.navigate_here()
    aaq_page.create_and_submit(data)

    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("PENDING")
    return registration_list_page.get_newest_registration_number()


@pytest.mark.smoke
@pytest.mark.regression
def test_approval_list_shows_submitted_registration(
    page, aaq_page, registration_list_page, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: a submitted registration can be found by its Registration Number."""
    # Step 1: submit a new registration
    registration_number = submit_new_registration(
        aaq_page, registration_list_page, build_registration_data()
    )

    # Step 2: open the approval list and filter by that Registration Number
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    take_screenshot(f"approval list filtered by registration {registration_number}")

    # Step 3: the registration is listed and ready to be selected
    approval_list_page.select_row_checkbox(registration_number)
    take_screenshot(f"registration {registration_number} row selected")


@pytest.mark.regression
def test_approval_list_popup_shows_entered_details(
    page, aaq_page, registration_list_page, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: the View popup shows every value entered on the AAQ form."""
    data = build_registration_data()

    # Step 1: submit a new registration
    registration_number = submit_new_registration(
        aaq_page, registration_list_page, data
    )

    # Step 2: open the registration's View popup from the approval list
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    approval_list_page.open_registration_popup(registration_number)
    take_screenshot("asset registration view popup opened")

    # Step 3: every entered value appears in the popup
    approval_list_page.verify_popup_details(
        [
            registration_number,
            data["project"],
            data["remarks"],
            data["vendor_name"],
            data["vendor_number"],
            data["asset_item_selected"],
            data["item_specification"][:30],  # the popup truncates long text
            str(data["quantity"]),
            str(data["unit_price"]),
        ]
    )
    take_screenshot("asset registration view popup details verified")


@pytest.mark.regression
def test_approval_list_asset_serials_empty_before_approval(
    page, aaq_page, registration_list_page, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: the Asset Serials tab is empty until the registration is approved."""
    # Step 1: submit a new registration
    registration_number = submit_new_registration(
        aaq_page, registration_list_page, build_registration_data()
    )

    # Step 2: open the View popup and switch to the Asset Serials tab
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    approval_list_page.open_registration_popup(registration_number)
    approval_list_page.open_asset_serials_tab()
    take_screenshot("asset serials tab before approval")

    # Step 3: no serial number exists yet
    serials_text = approval_list_page.get_asset_serials_text()
    assert "No data available in table" in serials_text, (
        f"Expected an empty Asset Serials grid before approval but found: {serials_text}"
    )


@pytest.mark.regression
def test_approval_list_approve_registration(
    page, aaq_page, registration_list_page, approval_list_page, take_screenshot
):
    """
    Asset Registration Approval List: approving a pending registration
    generates an Asset Serial Number.
    """
    # Step 1: submit a new registration
    registration_number = submit_new_registration(
        aaq_page, registration_list_page, build_registration_data()
    )

    # Step 2: open the registration from the approval list by clicking its
    # Registration Number link
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    approval_list_page.open_registration_popup(registration_number)
    take_screenshot("asset registration view popup opened")

    # Step 3: the popup is for the registration taken from the Asset
    # Registration List
    approval_list_page.verify_popup_registration_number(registration_number)

    # Step 4: click Approve inside the popup and confirm the success toast
    approval_list_page.approve_from_popup_and_verify_success(registration_number)
    take_screenshot("registration approved")

    # Step 5: reopen the registration and store the generated Asset Serial
    # Number from the Asset Serials tab (it is written to the log)
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    approval_list_page.open_registration_popup(registration_number)
    approval_list_page.open_asset_serials_tab()
    asset_serial = approval_list_page.get_generated_asset_serial()
    assert asset_serial, (
        "Expected a generated Asset Serial Number on the Asset Serials tab "
        "after a successful Approve, but none was found."
    )
    take_screenshot(f"asset serial {asset_serial} generated")


# ---------------------------------------------------------------------------
# 1. The page opens with the right columns, options and defaults
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_approval_grid_columns(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the grid shows the expected columns, in order."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()
    take_screenshot("approval list opened")

    # Step 2: the column headings are as expected (the first is the tick box column)
    approval_list_page.verify_headers(
        [
            "", "SL", "Registration Number", "Registration Date", "Reference Number",
            "Registration Type", "Branch Name", "Project Name", "Department Name",
            "Created By", "Status", "Approved By", "Approval Date", "Attachment", "Approve",
        ]
    )


@pytest.mark.regression
def test_approval_status_filter_options(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the Status filter offers PENDING, APPROVED, REJECTED and SENDBACK (no DRAFT)."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()

    # Step 2: the Status options are as expected
    approval_list_page.verify_filter_options(
        "Status", ["-Select Status-", "PENDING", "APPROVED", "REJECTED", "SENDBACK"]
    )


@pytest.mark.regression
def test_approval_registration_type_filter_options(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the Registration Type filter offers MRR, AAQ and LEASE."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()

    # Step 2: the Registration Type options are as expected
    approval_list_page.verify_filter_options(
        "Registration Type", ["-Select Registration Type-", "MRR", "AAQ", "LEASE"]
    )


@pytest.mark.regression
def test_approval_records_per_page_options(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: Records per page offers 10, 20, 30, 50 and 100."""
    # Step 1: open the approval list
    approval_list_page.navigate_here()

    # Step 2: the page size options are as expected
    approval_list_page.verify_page_size_options(["10", "20", "30", "50", "100"])


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
# 2. Filters
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
@pytest.mark.parametrize("registration_type", ["AAQ", "MRR", "LEASE"])
def test_approval_filter_by_registration_type(registration_type, page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by a Registration Type lists only that type."""
    # Step 1: open the approval list and filter by the type
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_type(registration_type)
    take_screenshot(f"approval list filtered by {registration_type}")

    # Step 2: every row shows that Registration Type
    approval_list_page.verify_all_rows_have("Registration Type", registration_type)


@pytest.mark.regression
def test_approval_filter_by_project(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by Project lists only registrations of that project."""
    project = build_asset_data("furniture")["project"]

    # Step 1: open the approval list and filter by the project
    approval_list_page.navigate_here()
    approval_list_page.filter_by_project(project)
    take_screenshot("approval list filtered by project")

    # Step 2: there are rows, and every row shows that project
    approval_list_page.verify_all_rows_have("Project Name", project, must_have_rows=True)


@pytest.mark.regression
def test_approval_filter_by_vendor_finds_registrations(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by a Vendor name lists that vendor's registrations."""
    vendor_name = build_asset_data("furniture")["vendor_name"]

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
@pytest.mark.xfail(
    reason="Search ignores the MRR Number filter on the Registration List; this checks whether the "
           "Approval List does too. Needs a product decision.",
    strict=True,
)
def test_approval_filter_by_mrr_number(page, approval_list_page, take_screenshot):
    """Asset Registration Approval List: filtering by an MRR Number lists only registrations with that reference."""
    # Step 1: list MRR registrations and pick a Reference Number
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_type("MRR")
    mrr_number = approval_list_page.read_first_reference_number()

    # Step 2: filter by that MRR Number
    approval_list_page.filter_by_mrr_number(mrr_number)
    take_screenshot(f"approval list filtered by MRR number {mrr_number}")

    # Step 3: every row shows that Reference Number
    approval_list_page.verify_all_rows_have("Reference Number", mrr_number, must_have_rows=True)


@pytest.mark.regression
@ASSET_ITEMS
def test_approval_filter_by_registration_number_shows_the_registration(
    item, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: filtering by a Registration Number lists exactly that registration."""
    # Step 1: get a submitted registration (reused from an earlier test, or created now)
    record = registrations.get_pending(item)
    number = record["registration_number"]

    # Step 2: filter by its Registration Number
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    take_screenshot(f"approval list filtered by registration number {number}")

    # Step 3: one row, with this number, the project, type AAQ and Status PENDING, ready to be ticked
    approval_list_page.verify_registration_row(number, record["data"]["project"], "AAQ", "PENDING")
    approval_list_page.verify_row_has_checkbox(number)


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
def test_approval_status_and_number_filters_work_together(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: a PENDING registration is not listed when the Status filter is APPROVED."""
    # Step 1: get a submitted registration
    number = registrations.get_pending("furniture")["registration_number"]

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
    number = registrations.get_pending("furniture")["registration_number"]
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
def test_approval_filter_by_approve_date(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the Approve From/To Date filters list only registrations approved that day."""
    # Step 1: find the Approval Date of an approved registration
    number = registrations.get_approved("furniture")["registration_number"]
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
# 3. Reset
# ---------------------------------------------------------------------------


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
    approval_list_page.verify_filters_empty(
        ["Status", "Registration Type", "Registration Number", "Vendor"]
    )


# ---------------------------------------------------------------------------
# 4. Paging
# ---------------------------------------------------------------------------


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
# 5. The View popup, for each of the 5 asset items
# ---------------------------------------------------------------------------


@pytest.mark.regression
@ASSET_ITEMS
def test_approval_popup_shows_the_registration(
    item, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: the popup shows every value that was entered."""
    # Step 1: get a submitted registration (reused from an earlier test, or created now)
    record = registrations.get_pending(item)
    number = record["registration_number"]
    data = record["data"]

    # Step 2: open its popup from the approval list
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    take_screenshot(f"popup of registration {number}")

    # Step 3: the popup shows the values that were entered (it shortens a long specification)
    approval_list_page.verify_popup_registration_number(number)
    approval_list_page.verify_popup_details(
        [
            number, data["project"], data["remarks"], data["vendor_name"], data["vendor_number"],
            data["grid_item_name"], data["item_specification"][:30], str(data["quantity"]), str(data["unit_price"]),
        ]
    )


@pytest.mark.regression
@ASSET_ITEMS
def test_approval_asset_serials_are_empty_before_approval(
    item, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: a pending registration has no Asset Serial yet."""
    # Step 1: get a submitted registration (reused from an earlier test, or created now)
    number = registrations.get_pending(item)["registration_number"]

    # Step 2: open its popup and switch to the Asset Serials tab
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    approval_list_page.open_asset_serials_tab()
    take_screenshot("asset serials tab before approval")

    # Step 3: no serial number exists yet
    approval_list_page.verify_asset_serials_empty()


@pytest.mark.regression
def test_approval_comment_box_keeps_500_characters(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the popup's Comment box keeps at most 500 characters."""
    # Step 1: open the popup of a submitted registration
    number = registrations.get_pending("furniture")["registration_number"]
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)

    # Step 2: type 600 characters
    approval_list_page.enter_comment("C" * 600)
    take_screenshot("600 characters typed in the comment box")

    # Step 3: only 500 are kept
    approval_list_page.verify_comment_length(500)


# ---------------------------------------------------------------------------
# 6. Approve
#    These use up a PENDING registration, so each one tells `registrations`
#    about it for the tests that follow.
# ---------------------------------------------------------------------------


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
    approval_list_page.verify_toast("You have to select a Registration first")


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


@pytest.mark.regression
@ASSET_ITEMS
def test_approval_approve_each_asset_item(
    item, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: a pending registration of each asset item can be approved from its popup."""
    # Step 1: get a submitted registration (reused from an earlier test, or created now)
    record = registrations.get_pending(item)
    number = record["registration_number"]

    # Step 2: open its popup and approve it
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    take_screenshot("popup opened")
    approval_list_page.approve_from_popup_and_verify_success(number)
    take_screenshot("registration approved")

    # Step 3: read the Asset Serial that approval created
    serial = approval_list_page.read_asset_serial_of(number)
    take_screenshot(f"asset serial {serial} generated")

    # Step 4: it is no longer PENDING; remember it as APPROVED for later tests
    registrations.move_to_approved(record, serial)


@pytest.mark.regression
@ASSET_ITEMS
def test_approval_approved_registration_row(
    item, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: an approved registration shows APPROVED, who approved it and when, and has no tick box."""
    # Step 1: get an approved registration (reused from the Approve test, or created now)
    number = registrations.get_approved(item)["registration_number"]

    # Step 2: find it in the approval list
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(number)
    take_screenshot(f"approved registration {number} in the list")

    # Step 3: the row shows APPROVED, an approver and a dd/mm/yyyy date, and cannot be ticked
    approval_list_page.verify_approved_row(number)


@pytest.mark.regression
@ASSET_ITEMS
def test_approval_asset_serial_is_shown_after_approval(
    item, page, registrations, approval_list_page, take_screenshot
):
    """Asset Registration Approval List: an approved registration's popup lists its Asset Serial."""
    # Step 1: get an approved registration (reused from the Approve test, or created now)
    record = registrations.get_approved(item)
    number = record["registration_number"]

    # Step 2: open its popup and switch to the Asset Serials tab
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    approval_list_page.open_asset_serials_tab()
    take_screenshot("asset serials tab after approval")

    # Step 3: the serial is there, looks like BBDASR00227761 and is the one approval created
    approval_list_page.verify_asset_serial_shown(record["serial"])


@pytest.mark.regression
def test_approval_approved_popup_has_no_approve_button(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: the popup of an approved registration has no Approve button."""
    # Step 1: get an approved registration and open its popup
    number = registrations.get_approved("furniture")["registration_number"]
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    take_screenshot("popup of an approved registration")

    # Step 2: the Approve button is not shown
    approval_list_page.verify_popup_has_no_approve_button()


@pytest.mark.regression
def test_approval_approve_with_a_comment(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: a registration can be approved with a comment."""
    # Step 1: get a submitted registration of its own, so no other test needs it
    record = registrations.get_pending("furniture", owner="comment")
    number = record["registration_number"]

    # Step 2: open its popup, type a comment and approve
    approval_list_page.navigate_here()
    approval_list_page.open_registration_popup_by_number(number)
    approval_list_page.enter_comment("AUTOMATION_TEST approve comment")
    take_screenshot("comment typed")
    approval_list_page.approve_from_popup_and_verify_success(number)
    take_screenshot("approved with a comment")

    # Step 3: it is no longer PENDING
    registrations.forget(record, "PENDING", owner="comment")


@pytest.mark.regression
def test_approval_bulk_approve_ticked_rows(page, registrations, approval_list_page, take_screenshot):
    """Asset Registration Approval List: two ticked registrations are approved together."""
    # Step 1: get two submitted registrations of their own, so no other test needs them
    first = registrations.get_pending("furniture", owner="bulk")
    second = registrations.get_pending("land", owner="bulk")
    first_number = first["registration_number"]
    second_number = second["registration_number"]

    # Step 2: show the pending registrations (the newest are first) and tick both
    approval_list_page.navigate_here()
    approval_list_page.filter_by_status("PENDING")
    approval_list_page.select_row_checkbox(first_number)
    approval_list_page.select_row_checkbox(second_number)
    take_screenshot("two registrations ticked")

    # Step 3: Approve shows the success toast
    approval_list_page.approve_ticked_rows()
    take_screenshot("bulk approve done")
    approval_list_page.verify_toast("Asset registration approved successfully.")
    registrations.forget(first, "PENDING", owner="bulk")
    registrations.forget(second, "PENDING", owner="bulk")

    # Step 4: both now show APPROVED
    approval_list_page.verify_registration_is_approved(first_number)
    approval_list_page.verify_registration_is_approved(second_number)
