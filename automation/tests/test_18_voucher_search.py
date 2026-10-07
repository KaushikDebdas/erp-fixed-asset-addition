"""
test_18_voucher_search.py: tests for the Voucher Search screen of the
Accounting module (Accounting > Voucher > Voucher Search).

Built from automation/element_catalog/voucher_search.md. The whole file logs in
once and every test reuses that session. These tests only search; the check of
an Asset Expense voucher (search by the Expense ID, then the Preview PDF) is in
the full-flow tests of test_16_asset_expense.py. The last test here checks the
voucher of the APPROVED Accounts expense saved in test_data/saved_assets.json
(the `expenses` fixture, utils/expense_helper.py). The check of an Asset
Registration voucher (search by the Registration Number, then the Preview PDF)
is in test_03_asset_registration_approval_list.py.
"""
import re

import pytest

from test_data.asset_expense_data import ACCOUNTS
from utils.expense_flow import verify_voucher
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
    expected_headers = [
        "Date",
        "Voucher No.",
        "Transaction No",
        "Amount",
        "Particular",
        "Status",
        "Preview",
    ]
    found_headers = voucher_search_page.get_grid_headers()
    assert found_headers == expected_headers, f"Expected grid columns {expected_headers} but found {found_headers}."

    # Step 3: the Voucher Type values
    expected_types = [
        "-Select Voucher Type-",
        "Journal Voucher",
        "Credit Voucher",
        "Debit Voucher",
        "Transfer Voucher",
    ]
    found_types = voucher_search_page.get_voucher_type_options()
    assert found_types == expected_types, f"Expected Voucher Type values {expected_types} but found {found_types}."

    # Step 4: the Module values include Fixed Asset
    module_options = voucher_search_page.get_module_options()
    assert "Fixed Asset" in module_options, f"Expected the Module filter to include 'Fixed Asset' but found {module_options}."


@pytest.mark.regression
def test_voucher_search_accounting_date_is_shown(page, voucher_search_page, take_screenshot):
    """Voucher Search: the page header shows the accounting date the vouchers are dated with."""
    # Step 1: open Voucher Search
    voucher_search_page.navigate_here()
    take_screenshot("voucher search opened")

    # Step 2: the accounting date is a dd/mm/yyyy date
    accounting_date = voucher_search_page.get_accounting_date()
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", accounting_date), (
        f"Expected the accounting date in dd/mm/yyyy format but found '{accounting_date}'."
    )


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
    assert not voucher_search_page.is_voucher_listed("BBDEXP99999999"), (
        "Expected no voucher for Transaction No 'BBDEXP99999999' but a voucher was listed."
    )


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
    assert not voucher_search_page.is_voucher_listed("BBDEXP"), (
        "Expected no voucher for the partial Transaction No 'BBDEXP' but a voucher was listed."
    )
    empty_rows = voucher_search_page.results_table.locator("tbody tr", has_text="No data available in table").count()
    assert empty_rows == 1, f"Expected 1 'No data available in table' row but found {empty_rows}."


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
    voucher_search_page.wait_for_row_or_no_data(voucher_search_page.results_table, "")
    take_screenshot("fixed asset vouchers")
    rows = voucher_search_page.results_table.locator("tbody tr").filter(has_not_text="No data available")
    if rows.count() == 0:
        pytest.skip("There is no Fixed Asset voucher on the accounting date yet.")

    # Step 3: every voucher listed is dated the accounting date (the grid shows d/m/yyyy)
    day, month, year = accounting_date.split("/")
    expected_date = f"{int(day)}/{int(month)}/{year}"
    for i in range(rows.count()):
        found_date = rows.nth(i).locator("td:visible").first.inner_text().strip()
        assert found_date == expected_date, f"Expected voucher row {i + 1} to be dated '{expected_date}' but found '{found_date}'."


@pytest.mark.regression
def test_voucher_search_finds_the_voucher_of_the_saved_expense(
    page, voucher_search_page, expenses, take_screenshot
):
    """Voucher Search: the saved approved expense is found by its Expense ID and its voucher PDF is right."""
    # Step 1: take the saved approved Accounts expense
    record = expenses.get_approved_expense(ACCOUNTS)

    # Step 2: search by its Expense ID and check the row and the Preview PDF
    verify_voucher(voucher_search_page, record["expense_id"], record["expected"], take_screenshot)
