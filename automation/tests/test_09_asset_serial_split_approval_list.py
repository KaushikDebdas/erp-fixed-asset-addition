"""
test_09_asset_serial_split_approval_list.py: tests for the Asset Serial Split
Approval List screen (Fixed Asset > Asset Profile > Asset Serial Split
Approval List) and its Asset Split View popup.

Built from automation/element_catalog/asset_serial_split_approval_list.md. The
whole file logs in once and every test reuses that session. The tests only
read the list and open the view popup. Approve and Reject are never clicked:
they would change real split requests.
"""
import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_split_approval_list_grid_columns(page, asset_split_approval_list_page, take_screenshot):
    """Asset Serial Split Approval List: the grid shows the documented columns."""
    # Step 1: open the Asset Serial Split Approval List and search
    asset_split_approval_list_page.navigate_here()
    asset_split_approval_list_page.search()
    take_screenshot("asset serial split approval list opened")

    # Step 2: the column headings
    assert asset_split_approval_list_page.get_grid_headers() == [
        "SL",
        "Asset Split No.",
        "Asset Group",
        "Project Name",
        "Department Name",
        "Asset Serial No.",
        "Split Into",
        "Remarks",
        "Created By",
        "Status",
        "Approved By",
        "Approval Date",
    ]


@pytest.mark.regression
def test_split_approval_list_has_approve_and_reject_buttons(
    page, asset_split_approval_list_page, take_screenshot
):
    """Asset Serial Split Approval List: the Approve and Reject buttons are on the page."""
    # Step 1: open the list
    asset_split_approval_list_page.navigate_here()
    take_screenshot("asset serial split approval list opened")

    # Step 2: both buttons are shown (they are not clicked)
    assert asset_split_approval_list_page.approve_button.is_visible()
    assert asset_split_approval_list_page.reject_button.is_visible()


@pytest.mark.regression
def test_split_approval_list_view_popup(page, asset_split_approval_list_page, take_screenshot):
    """Asset Serial Split Approval List: a split's View popup shows the same asset and its split lines."""
    # Step 1: open the list and search
    asset_split_approval_list_page.navigate_here()
    asset_split_approval_list_page.search()
    if not asset_split_approval_list_page.has_data_rows():
        pytest.skip("There is no split request on this environment right now.")
    list_page = asset_split_approval_list_page
    serial_in_list = list_page.get_first_row_asset_serial()

    # Step 2: open the first split's View popup
    list_page.open_first_row_popup()
    take_screenshot("asset split view popup opened")
    assert list_page.get_popup_title() == "Asset Split View"

    # Step 3: the popup is for the same asset as the list row
    assert list_page.get_popup_value("assetSerial") == serial_in_list

    # Step 4: Split Into matches the number of split lines shown
    split_into = int(list_page.get_popup_value("splitInto"))
    assert list_page.get_popup_split_line_count() == split_into, (
        f"Split Into is {split_into} but the popup lists "
        f"{list_page.get_popup_split_line_count()} split lines."
    )

    # Step 5: close the popup
    list_page.close_popup()
