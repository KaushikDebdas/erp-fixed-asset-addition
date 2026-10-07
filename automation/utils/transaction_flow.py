"""
transaction_flow.py: the checks that every Asset Transaction type (Assign,
Un Assign, Internal Movement) goes through after its Draft is saved.

    Transaction List: open the Draft's Details and compare it with what was
    entered, open Edit and compare the form, then Submit.
    Approval List: open the transaction's Details, compare it again, then
    Approve and confirm it is now APPROVED.

`expected` holds what was entered on the form:
    employee_pin, employee_name, note, transaction_date (dd/mm/yyyy), and
    optionally building and floor.
"""
from test_data.asset_transaction_data import USER_BRANCH
from utils.logger import assertion_logger

APPROVE_TOAST = "Approved successfully"


def build_expected(
    employee_pin: str, employee_name: str, note: str, transaction_date: str,
    building: str = "", floor: str = ""
) -> dict:
    """
    Return the `expected` dictionary the checks below compare with. Give
    `building` and `floor` only for an Internal Movement.

    Example:
        expected = build_expected(ASSIGNEE_PIN, ASSIGNEE_NAME, NOTE, transaction_date)
    """
    expected = {
        "employee_pin": employee_pin,
        "employee_name": employee_name,
        "note": note,
        "transaction_date": transaction_date,
    }
    if building != "":
        expected["building"] = building
        expected["floor"] = floor
    return expected


def check_popup_matches(grid_page, transaction_type: str, status: str, expected: dict) -> None:
    """Compare the open Details popup with what was entered on the form."""
    assertion_logger.info(f"Verifying {transaction_type} Details popup shows status {status}")
    popup_values = {
        "assetTransactionType": transaction_type,
        "oldTransactionStatus": status,
        "assignedEmployeePinNo": expected["employee_pin"],
        "assignedEmployee": expected["employee_name"],
        "remarks": expected["note"],
        "transactionDate": expected["transaction_date"],
    }
    if "building" in expected:
        popup_values["building"] = expected["building"]
        popup_values["floor"] = expected["floor"]
    for field_id, expected_value in popup_values.items():
        actual_value = grid_page.get_popup_value(field_id)
        assert actual_value == expected_value, (
            f"Details popup field '{field_id}': expected '{expected_value}' but found '{actual_value}'."
        )


def submit_draft_from_list(
    list_page, form_page, transaction_type: str, serial: str, expected: dict,
    submit_toast: str, take_screenshot
) -> None:
    """
    Transaction List: find the Draft that lists `serial`, check its Details,
    open Edit, check the form shows what was entered, and Submit.
    """
    list_page.navigate_here()
    row_index = list_page.open_details_of_row_with_serial(serial, transaction_type, "DRAFT")
    take_screenshot(f"{transaction_type} draft details")
    check_popup_matches(list_page, transaction_type, "DRAFT", expected)
    list_page.close_popup()

    assert list_page.has_edit_link(row_index), "A Draft row should have an Edit link."
    list_page.click_edit_of_row(row_index)
    take_screenshot(f"{transaction_type} draft edit form")
    assertion_logger.info(f"Verifying the Edit form of the {transaction_type} Draft")
    assert form_page.get_employee_pin() == expected["employee_pin"]
    assert form_page.get_employee_name() == expected["employee_name"]
    assert form_page.get_value("newRemarks") == expected["note"]
    assert form_page.get_branch_name() == USER_BRANCH

    toast = form_page.submit_and_get_toast()
    take_screenshot(f"{transaction_type} submitted")
    assert toast == submit_toast, f"Expected Submit toast '{submit_toast}' but found '{toast}'."


def approve_and_verify(approval_page, transaction_type: str, serial: str, expected: dict, take_screenshot) -> None:
    """
    Approval List: find the PENDING transaction that lists `serial`, check its
    Details, Approve it, and confirm it is now APPROVED.
    """
    approval_page.navigate_here()
    approval_page.open_details_of_row_with_serial(serial, transaction_type, "PENDING")
    take_screenshot(f"{transaction_type} approval details")
    check_popup_matches(approval_page, transaction_type, "PENDING", expected)
    assert approval_page.are_decision_buttons_visible(), "Approve, Reject and Sendback should all be shown."

    approval_page.enter_comment("AUTOMATION_TEST approve comment")
    toast = approval_page.approve_and_get_toast()
    take_screenshot(f"{transaction_type} approved")
    assert toast == APPROVE_TOAST, f"Expected Approve toast '{APPROVE_TOAST}' but found '{toast}'."

    # The transaction is now APPROVED, with an approver and an approval date
    approval_page.open_details_of_row_with_serial(serial, transaction_type, "APPROVED")
    check_popup_matches(approval_page, transaction_type, "APPROVED", expected)
    assert approval_page.get_popup_value("approvedBy"), "Approved By should be filled after approval."
    assert approval_page.get_popup_value("approvalDate"), "Approval Date should be filled after approval."
    approval_page.close_popup()
