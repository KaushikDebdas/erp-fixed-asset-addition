"""
test_16_asset_expense.py: tests for the Asset Expense screen (Fixed Asset >
Asset Expenditure > Asset Expense), for both expense sources.

Built from automation/element_catalog/asset_expense.md,
asset_expense_approval.md and voucher_search.md. The tests use a freshly
approved asset (the `unassigned_asset` fixture in conftest.py). The whole file
logs in once and every test reuses that session.

The four full-flow tests at the end take an expense all the way, for Inventory
and for Accounts, each saved two ways (Draft then Submit, and Submit straight
away):
    create the expense, store its Expense ID, Submit, Approve with the same
    user, then find the voucher in Accounting > Voucher Search by the Expense ID
    and check the voucher PDF.
They each create one approved expense of 5000 and one voucher.
"""
import pytest

from test_data.asset_expense_data import (
    ACCOUNTS,
    CREDIT_ACCOUNT,
    DEBIT_ACCOUNT,
    EXPENSE_AMOUNT,
    INVENTORY,
    VENDOR_REQUIRED_TOAST,
    new_expense_ref,
)
from utils.expense_flow import (
    approve_expense,
    create_expense,
    fill_expense_form,
    submit_draft,
    verify_voucher,
)
from utils.logger import action_logger
from utils.run_context import trace_one_test


@pytest.fixture
def page(logged_in_page, request):
    """Every test in this file reuses the one tab that logged in once."""
    yield from trace_one_test(logged_in_page, request)


@pytest.mark.smoke
@pytest.mark.regression
def test_expense_list_columns_and_status_values(page, expense_page, take_screenshot):
    """Asset Expense: the list has its documented columns and the five statuses."""
    # Step 1: open the Asset Expense list
    expense_page.navigate_here()
    take_screenshot("asset expense list opened")

    # Step 2: the Status filter values
    assert expense_page.get_status_options() == [
        "-Select Status-",
        "PENDING",
        "APPROVED",
        "REJECTED",
        "DRAFT",
        "SENDBACK",
    ]

    # Step 3: the column headings
    assert expense_page.get_grid_headers() == [
        "SL",
        "Expense ID",
        "Entry Date",
        "Expense Amount",
        "Expense Ref.",
        "Status",
        "Created By",
        "Approved By",
        "Approve Date",
        "Note/Remarks",
    ]


@pytest.mark.regression
def test_expense_asset_search_fills_asset_details(
    page, expense_page, unassigned_asset, take_screenshot
):
    """Asset Expense: typing the Asset Serial and picking the suggestion fills the asset details."""
    serial = unassigned_asset["serial"]

    # Step 1: open the Create form
    expense_page.navigate_here()
    expense_page.open_create_form()

    # Step 2: type the serial and pick the suggestion
    expense_page.select_asset_by_serial(serial)
    take_screenshot(f"asset {serial} selected")

    # Step 3: the box holds the serial that was entered, and the details are the asset's own
    assert expense_page.get_value("assetSerialId").startswith(serial)
    assert expense_page.get_value("assetName") == "Cabinet Table"
    assert expense_page.get_value("category") == "Furniture"
    assert expense_page.get_value("subCategory") == "Wooden Furniture"
    assert expense_page.get_value("group") == "Furniture and Fixture"
    assert "Head Office" in expense_page.get_value("currentBranch")
    assert "Microfinance (Dabi)" in expense_page.get_value("currentProjectName")

    # Step 4: close without saving
    expense_page.close_popup()


@pytest.mark.regression
def test_expense_add_asset_fills_the_total(
    page, expense_page, unassigned_asset, take_screenshot
):
    """Asset Expense: the expense amount and Add put the asset in the grid and fill the total."""
    serial = unassigned_asset["serial"]

    # Step 1: select the asset, enter the amount and click Add
    expense_page.navigate_here()
    expense_page.open_create_form()
    expense_page.select_asset_by_serial(serial)
    expense_page.enter_amount_and_add_asset(EXPENSE_AMOUNT)
    take_screenshot("asset added to the expense grid")

    # Step 2: the grid holds the asset and the Total Expense Amount is the amount entered
    assert serial in expense_page.get_asset_grid_serials()
    assert expense_page.get_total_expense_amount() == EXPENSE_AMOUNT

    # Step 3: close without saving
    expense_page.close_popup()


@pytest.mark.regression
def test_expense_source_inventory_needs_item_and_fills_credit(
    page, expense_page, unassigned_asset, take_screenshot
):
    """Asset Expense: with Inventory the Category chain is open and Credit A/C is Other Inventory."""
    # Step 1: add the asset, then choose the Inventory source
    expense_page.navigate_here()
    expense_page.open_create_form()
    expense_page.select_asset_by_serial(unassigned_asset["serial"])
    expense_page.enter_amount_and_add_asset(EXPENSE_AMOUNT)
    expense_page.choose_expense_source(INVENTORY)
    take_screenshot("inventory source chosen")

    # Step 2: Category, Sub Category and Item Name can be chosen, and Credit A/C was filled in
    assert expense_page.is_category_chain_enabled()
    assert expense_page.get_credit_account() == CREDIT_ACCOUNT[INVENTORY]

    # Step 3: close without saving
    expense_page.close_popup()


@pytest.mark.regression
def test_expense_source_accounts_disables_item_and_fills_credit(
    page, expense_page, unassigned_asset, take_screenshot
):
    """Asset Expense: with Accounts the Category chain is disabled and Credit A/C is Supplier Payable-Opex."""
    # Step 1: add the asset, then choose the Accounts source
    expense_page.navigate_here()
    expense_page.open_create_form()
    expense_page.select_asset_by_serial(unassigned_asset["serial"])
    expense_page.enter_amount_and_add_asset(EXPENSE_AMOUNT)
    expense_page.choose_expense_source(ACCOUNTS)
    take_screenshot("accounts source chosen")

    # Step 2: Category, Sub Category and Item Name are disabled, and Credit A/C was filled in
    assert not expense_page.is_category_chain_enabled()
    assert expense_page.get_credit_account() == CREDIT_ACCOUNT[ACCOUNTS]

    # Step 3: close without saving
    expense_page.close_popup()


@pytest.mark.regression
@pytest.mark.parametrize("source", [INVENTORY, ACCOUNTS])
def test_expense_requires_vendor_for_both_sources(
    page, expense_page, unassigned_asset, source, take_screenshot
):
    """Asset Expense: Draft without a Vendor/Supplier/Lessor Name is refused, for either source."""
    # Step 1: fill everything except the vendor
    expense_page.navigate_here()
    expense_page.open_create_form()
    expense_page.select_asset_by_serial(unassigned_asset["serial"])
    expense_page.enter_amount_and_add_asset(EXPENSE_AMOUNT)
    expense_page.choose_expense_source(source)
    if source == INVENTORY:
        expense_page.select_category_sub_category_and_item("Furniture", "Wooden Furniture", "Cabinet Table")
    expense_page.select_debit_account(DEBIT_ACCOUNT)
    expense_page.enter_expense_ref(new_expense_ref())

    # Step 2: click Draft; the message asks for the vendor and nothing is saved
    toast = expense_page.draft_and_get_toast()
    take_screenshot("draft refused without vendor")
    assert toast == VENDOR_REQUIRED_TOAST, f"Unexpected toast: '{toast}'"
    assert expense_page.popup.is_visible(), "The form should stay open when the save is refused."

    # Step 3: close without saving
    expense_page.close_popup()


@pytest.mark.regression
@pytest.mark.parametrize("save_as", ["draft", "submit"])
@pytest.mark.parametrize("source", [INVENTORY, ACCOUNTS])
def test_expense_full_flow_with_voucher(
    page, expense_page, expense_approval_page, voucher_search_page,
    unassigned_asset, source, save_as, take_screenshot
):
    """
    Asset Expense: create (Draft or direct Submit), store the Expense ID, Submit,
    Approve with the same user, then check the voucher in Voucher Search.
    """
    serial = unassigned_asset["serial"]
    expense_ref = new_expense_ref()

    # Step 1: create the expense and store its generated Expense ID
    created = create_expense(expense_page, serial, source, expense_ref, save_as, take_screenshot)
    expense_id = created["expense_id"]
    expected = created["expected"]
    action_logger.info(f"Stored Expense ID: {expense_id} ({source}, saved as {save_as})")
    assert expense_id.startswith("BBDEXP"), f"Unexpected Expense ID '{expense_id}'."

    # Step 2: a Draft is opened from the list, checked, and submitted
    if save_as == "draft":
        submit_draft(expense_page, expense_id, expected, take_screenshot)

    # Step 3: approve it with the same user, matched by the stored Expense ID
    approve_expense(expense_approval_page, expense_page, expense_id, expected, take_screenshot)

    # Step 4: the journal: find the voucher by the Expense ID and check its PDF
    verify_voucher(voucher_search_page, expense_id, expected, take_screenshot)
