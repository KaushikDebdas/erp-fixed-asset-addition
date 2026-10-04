"""
asset_flow.py: one reusable step used by the Asset Profile tests.

The Asset Profile screens only show assets that already exist, so the
tests first need an approved asset. `create_approved_asset` registers one on
the AAQ form, submits it, approves it from the Approval List, and returns
its Registration Number and Asset Serial Number.
"""
from utils.logger import action_logger


def create_approved_asset(aaq_page, registration_list_page, approval_list_page, data: dict) -> dict:
    """
    Register, submit and approve one asset. Returns
    {"registration_number": ..., "serial": ...}.
    """
    # Register and submit on the AAQ form
    aaq_page.navigate_here()
    aaq_page.create_and_submit(data)

    # Find the new registration (the newest PENDING one)
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("PENDING")
    registration_number = registration_list_page.get_newest_registration_number()

    # Open it from the Approval List and approve it from the popup
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    approval_list_page.open_registration_popup(registration_number)
    approval_list_page.approve_from_popup_and_verify_success(registration_number)

    # Approval creates the Asset Serial Number
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    approval_list_page.open_registration_popup(registration_number)
    approval_list_page.open_asset_serials_tab()
    serial = approval_list_page.get_generated_asset_serial()
    action_logger.info(f"Created asset {serial} from registration {registration_number}")
    return {"registration_number": registration_number, "serial": serial}


def assign_and_approve(assign_page, approval_list_page, serial: str, employee_pin: str, note: str) -> None:
    """
    Assign an unassigned asset to an employee and approve the assignment, so
    the asset ends up ASSIGNED. Used to prepare test data: it submits
    straight from the Asset Assign form and approves from the Approval List.
    """
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(serial)
    assign_page.add_to_grid()
    assign_page.select_employee(employee_pin)
    assign_page.enter_note(note)
    toast = assign_page.submit_and_get_toast()
    assert toast == "Asset Assign Submit Successfully", f"Unexpected toast: '{toast}'"

    approval_list_page.navigate_here()
    toast = approval_list_page.approve_transaction_for_serial("ASSIGN", serial)
    assert toast == "Approved successfully", f"Unexpected toast: '{toast}'"
    action_logger.info(f"Asset {serial} is now assigned to employee {employee_pin}")
