"""
expense_flow.py: the steps that every Asset Expense flow shares, for both
expense sources (Inventory, Accounts) and both ways of saving (Draft and
then Submit, or Submit straight away).

    create_expense      fill the Create form and save it; returns the stored Expense ID
    submit_draft        open a Draft from the list, check it, and Submit it
    approve_expense     open it in the approval list, check it, Approve, confirm APPROVED
    verify_voucher      find the voucher by the Expense ID and check the Preview PDF

`expected` is what was entered: serial, source, expense_ref, remarks, date_of_entry.
"""
from test_data.asset_expense_data import (
    ACCOUNTS,
    APPROVE_TOAST_START,
    CREDIT_ACCOUNT,
    DEBIT_ACCOUNT,
    DRAFT_TOAST,
    EXPENSE_AMOUNT,
    EXPENSE_AMOUNT_ON_VOUCHER,
    EXPENSE_CATEGORY,
    EXPENSE_ITEM,
    EXPENSE_SUB_CATEGORY,
    INVENTORY,
    SUBMIT_TOAST,
    VENDOR_OPTION,
    VENDOR_SEARCH,
    VOUCHER_CREDIT,
    VOUCHER_DEBIT,
)
from utils.logger import assertion_logger


def fill_expense_form(expense_page, serial: str, source: str, expense_ref: str, remarks: str) -> str:
    """
    Fill the open Create Asset Expense popup in the order the screen needs.
    Returns the Date of Entry (dd/mm/yyyy).
    """
    expense_page.select_asset_by_serial(serial)
    expense_page.enter_amount_and_add_asset(EXPENSE_AMOUNT)
    expense_page.choose_expense_source(source)
    if source == INVENTORY:
        expense_page.select_category_sub_category_and_item(
            EXPENSE_CATEGORY, EXPENSE_SUB_CATEGORY, EXPENSE_ITEM
        )
    expense_page.select_debit_account(DEBIT_ACCOUNT)
    expense_page.select_vendor(VENDOR_SEARCH, VENDOR_OPTION)
    expense_page.enter_expense_ref(expense_ref)
    expense_page.enter_remarks(remarks)
    return expense_page.get_date_of_entry()


def create_expense(expense_page, serial: str, source: str, expense_ref: str, save_as: str, take_screenshot) -> dict:
    """
    Create an expense and save it as a Draft (`save_as="draft"`) or submit it
    straight away (`save_as="submit"`). Checks the toast, then reads the
    generated Expense ID from the list by the random Expense Ref. Returns
    {"expense_id", "date_of_entry", "expected"}.
    """
    remarks = f"AUTOMATION_TEST expense {source}"
    expense_page.navigate_here()
    expense_page.open_create_form()
    date_of_entry = fill_expense_form(expense_page, serial, source, expense_ref, remarks)
    take_screenshot(f"{source} expense form filled")

    if save_as == "draft":
        toast, expected_toast, status = expense_page.draft_and_get_toast(), DRAFT_TOAST, "DRAFT"
    else:
        toast, expected_toast, status = expense_page.submit_and_get_toast(), SUBMIT_TOAST, "PENDING"
    take_screenshot(f"{source} expense saved as {status}")
    assert toast == expected_toast, f"Expected toast '{expected_toast}' but found '{toast}'."
    expense_page.wait_for_popup_to_close()

    # The Expense ID is generated on saving; read it from the list by the random reference
    expense_page.navigate_here()
    expense_page.search(status)
    expense_id = expense_page.get_expense_id_by_ref(expense_ref)
    assert expense_page.get_row_status(expense_id) == status
    return {
        "expense_id": expense_id,
        "date_of_entry": date_of_entry,
        "expected": {
            "serial": serial,
            "source": source,
            "expense_ref": expense_ref,
            "remarks": remarks,
            "date_of_entry": date_of_entry,
        },
    }


def check_saved_values_in_list_popup(expense_page, expected: dict) -> None:
    """Compare the opened Draft (Asset Expense list popup) with what was entered."""
    assertion_logger.info("Verifying the opened expense shows what was entered")
    expense_page.wait_for_saved_selections(expected["source"] == INVENTORY)
    assert expected["serial"] in expense_page.get_asset_grid_serials()
    saved = {
        "Expense Source": (expense_page.get_selected_text("expenseSource"), expected["source"]),
        "Expense Ref.": (expense_page.get_value("expenseRef"), expected["expense_ref"]),
        "Total Expense Amount": (expense_page.get_value("expenseAmount"), EXPENSE_AMOUNT),
        "Remarks": (expense_page.get_value("remarks"), expected["remarks"]),
        "Debit A/C": (expense_page.get_selected_text("debitAccount"), DEBIT_ACCOUNT),
        "Credit A/C": (expense_page.get_selected_text("creditAccount"), CREDIT_ACCOUNT[expected["source"]]),
    }
    if expected["source"] == INVENTORY:
        saved["Category"] = (expense_page.get_selected_text("expenseCategory"), EXPENSE_CATEGORY)
        saved["Sub Category"] = (expense_page.get_selected_text("expenseSubCategory"), EXPENSE_SUB_CATEGORY)
        saved["Item Name"] = (expense_page.get_selected_text("itemName"), EXPENSE_ITEM)
    for field_name, (actual, wanted) in saved.items():
        assert actual == wanted, f"Saved {field_name}: expected '{wanted}' but found '{actual}'."
    assert expense_page.is_vendor_shown("ACE IT"), "The saved vendor ACE IT is not shown."


def submit_draft(expense_page, expense_id: str, expected: dict, take_screenshot) -> None:
    """Open the Draft by its Expense ID, check the saved values, Submit it, and confirm it is PENDING."""
    expense_page.navigate_here()
    expense_page.search("DRAFT")
    expense_page.open_expense(expense_id)
    take_screenshot(f"draft {expense_id} opened")
    check_saved_values_in_list_popup(expense_page, expected)

    toast = expense_page.submit_and_get_toast()
    take_screenshot(f"draft {expense_id} submitted")
    assert toast == SUBMIT_TOAST, f"Expected toast '{SUBMIT_TOAST}' but found '{toast}'."
    expense_page.wait_for_popup_to_close()

    expense_page.navigate_here()
    expense_page.search("PENDING")
    expense_page.wait_for_row_or_no_data(expense_page.results_table, expense_id)
    assert expense_page.get_row_status(expense_id) == "PENDING"


def approve_expense(expense_approval_page, expense_page, expense_id: str, expected: dict, take_screenshot) -> str:
    """
    Approval list: find the PENDING expense by its stored Expense ID, check the
    read-only popup, Approve it, and confirm it is APPROVED in both lists.
    Returns the approval message.
    """
    expense_approval_page.navigate_here()
    expense_approval_page.find_expense(expense_id, "PENDING")
    expense_approval_page.open_expense(expense_id)
    take_screenshot(f"approval details of {expense_id}")
    assertion_logger.info(f"Verifying the approval popup of {expense_id} shows what was entered")
    approval = expense_approval_page
    assert expected["serial"] in approval.get_popup_asset_serials(), "The expense does not list the test asset."
    shown = {
        "Expense Ref.": (approval.get_popup_value("expenseRef"), expected["expense_ref"]),
        "Total Expense Amount": (approval.get_popup_value("expenseAmount"), EXPENSE_AMOUNT),
        "Remarks": (approval.get_popup_value("remarks"), expected["remarks"]),
        "Date of Entry": (approval.get_popup_value("dateOfEntry"), expected["date_of_entry"]),
        "Debit A/C": (approval.get_popup_selected_text("debitAccount"), DEBIT_ACCOUNT),
        "Credit A/C": (approval.get_popup_selected_text("creditAccount"), CREDIT_ACCOUNT[expected["source"]]),
    }
    for field_name, (actual, wanted) in shown.items():
        assert actual == wanted, f"Approval popup {field_name}: expected '{wanted}' but found '{actual}'."
    assert approval.is_popup_field_read_only("expenseRef"), "The approval popup should be read-only."
    assert approval.are_decision_buttons_visible(), "Approve, Reject and Sendback should all be shown."

    toast = approval.approve_and_get_toast()
    take_screenshot(f"{expense_id} approved")
    assert toast.startswith(APPROVE_TOAST_START), (
        f"Expected the approval message to start with '{APPROVE_TOAST_START}' but found '{toast}'."
    )

    approval.find_expense(expense_id, "APPROVED")
    assert approval.get_row_status(expense_id) == "APPROVED"
    expense_page.navigate_here()
    expense_page.search("APPROVED")
    expense_page.wait_for_row_or_no_data(expense_page.results_table, expense_id)
    assert expense_page.get_row_status(expense_id) == "APPROVED"
    return toast


def verify_voucher(voucher_search_page, expense_id: str, expected: dict, take_screenshot) -> None:
    """
    Accounting > Voucher Search: find the voucher by the Expense ID (Transaction
    Number) on the expense date, then read the Preview PDF and check the header,
    the accounts, the debit and credit amounts, the totals and the reference.
    """
    source = expected["source"]
    voucher_search_page.navigate_here()
    voucher_search_page.set_date_range(expected["date_of_entry"])
    voucher_search_page.search_by_transaction_no(expense_id)
    take_screenshot(f"voucher found for {expense_id}")
    assert voucher_search_page.is_voucher_listed(expense_id), f"No voucher was found for {expense_id}."

    # The search row
    row = voucher_search_page.get_row_values(expense_id)
    assertion_logger.info(f"Verifying the voucher search row of {expense_id}")
    assert row["transaction_no"] == expense_id
    assert row["amount"] == "5,000"
    assert row["particular"] == f"Asset Expense Voucher, Reference no: {expense_id}"
    assert row["status"] == "Approved"

    # The Preview: a PDF opened in a new tab
    voucher = voucher_search_page.read_voucher_preview(expense_id)
    assertion_logger.info(f"Verifying the voucher PDF of {expense_id}")
    assert voucher["pdf_status"] == 200 and "pdf" in voucher["content_type"]
    assert voucher["title"] == "JOURNAL VOUCHER"
    assert "Head Office" in voucher["branch"]
    assert "Microfinance (Dabi)" in voucher["project"]
    assert voucher["voucher_number"] == row["voucher_number"]
    assert voucher["creation_date"] == expected["date_of_entry"]
    assert voucher["posted_date"] == expected["date_of_entry"]
    assert voucher["reference_numbers"] and set(voucher["reference_numbers"]) == {expense_id}

    debit_code, debit_head = VOUCHER_DEBIT
    credit_code, credit_head = VOUCHER_CREDIT[source]
    assert voucher["lines"] == [
        {"account_code": debit_code, "head": debit_head, "debit": EXPENSE_AMOUNT_ON_VOUCHER, "credit": "0.00"},
        {"account_code": credit_code, "head": credit_head, "debit": "0.00", "credit": EXPENSE_AMOUNT_ON_VOUCHER},
    ], f"Unexpected voucher lines: {voucher['lines']}"
    assert voucher["total_debit"] == EXPENSE_AMOUNT_ON_VOUCHER
    assert voucher["total_credit"] == EXPENSE_AMOUNT_ON_VOUCHER
    assert "Five Thousand" in voucher["amount_in_words"]
