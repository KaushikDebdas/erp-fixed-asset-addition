"""
test_18_voucher_search.py: tests for the Voucher Search screen of the
Accounting module (Accounting > Voucher > Voucher Search).

Built from automation/element_catalog/voucher_search.md. The whole file logs in
once and every test reuses that session. These tests only search; the check of
an Asset Expense voucher (search by the Expense ID, then the Preview PDF) is in
the full-flow tests of test_16_asset_expense.py.
"""
import re

import pytest

from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_voucher_search_columns_and_filter_values(page, voucher_search_page, take_screenshot):
    """Voucher Search: the grid has its documented columns, and the Voucher Type and Module filters their values."""
    # Step 1: open Voucher Search through the Accounting module and search once
    # (the results grid only shows its headings after a search)
    voucher_search_page.navigate_here()
    voucher_search_page.search_by_transaction_no("BBDEXP99999999")
    take_screenshot("voucher search opened")

    # Step 2: the column headings
    assert voucher_search_page.get_grid_headers() == [
        "Date",
        "Voucher No.",
        "Transaction No",
        "Amount",
        "Particular",
        "Status",
        "Preview",
    ]

    # Step 3: the Voucher Type values
    assert voucher_search_page.get_voucher_type_options() == [
        "-Select Voucher Type-",
        "Journal Voucher",
        "Credit Voucher",
        "Debit Voucher",
        "Transfer Voucher",
    ]

    # Step 4: the Module values include Fixed Asset
    assert "Fixed Asset" in voucher_search_page.get_module_options()


@pytest.mark.regression
def test_voucher_search_accounting_date_is_shown(page, voucher_search_page, take_screenshot):
    """Voucher Search: the page header shows the accounting date the vouchers are dated with."""
    # Step 1: open Voucher Search
    voucher_search_page.navigate_here()
    take_screenshot("voucher search opened")

    # Step 2: the accounting date is a dd/mm/yyyy date
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", voucher_search_page.get_accounting_date())


@pytest.mark.regression
def test_voucher_search_unknown_transaction_number_finds_nothing(
    page, voucher_search_page, take_screenshot
):
    """Voucher Search: a Transaction Number that does not exist lists no voucher."""
    # Step 1: open Voucher Search and search for a number that cannot exist
    voucher_search_page.navigate_here()
    voucher_search_page.search_by_transaction_no("BBDEXP99999999")
    take_screenshot("no voucher for an unknown number")

    # Step 2: no voucher is listed
    assert not voucher_search_page.is_voucher_listed("BBDEXP99999999")


@pytest.mark.regression
def test_voucher_search_transaction_number_must_match_exactly(
    page, voucher_search_page, take_screenshot
):
    """Voucher Search: only the whole Transaction Number finds a voucher, a part of it finds nothing."""
    # Step 1: open Voucher Search and search with just the start of an Expense ID
    voucher_search_page.navigate_here()
    voucher_search_page.search_by_transaction_no("BBDEXP")
    take_screenshot("partial number")

    # Step 2: nothing is listed
    assert not voucher_search_page.is_voucher_listed("BBDEXP")
    assert voucher_search_page.results_table.locator("tbody tr", has_text="No data available in table").count() == 1


@pytest.mark.regression
def test_voucher_search_fixed_asset_module_on_the_accounting_date(
    page, voucher_search_page, take_screenshot
):
    """Voucher Search: Module Fixed Asset on the accounting date lists vouchers dated that day."""
    # Step 1: open Voucher Search and set both dates to the accounting date
    voucher_search_page.navigate_here()
    accounting_date = voucher_search_page.get_accounting_date()
    voucher_search_page.set_date_range(accounting_date)

    # Step 2: choose the Fixed Asset module and search
    voucher_search_page.choose_module("Fixed Asset")
    voucher_search_page.click(voucher_search_page.search_button, "Search button")
    voucher_search_page.wait_for_grid_refresh()
    take_screenshot("fixed asset vouchers")
    rows = voucher_search_page.results_table.locator("tbody tr").filter(has_not_text="No data available")
    if rows.count() == 0:
        pytest.skip("There is no Fixed Asset voucher on the accounting date yet.")

    # Step 3: every voucher listed is dated the accounting date (the grid shows d/m/yyyy)
    day, month, year = accounting_date.split("/")
    expected_date = f"{int(day)}/{int(month)}/{year}"
    for i in range(rows.count()):
        assert rows.nth(i).locator("td:visible").first.inner_text().strip() == expected_date
