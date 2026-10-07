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


def unassign_and_approve(unassign_page, approval_list_page, serial: str, handover_search: str, note: str) -> None:
    """
    Take an assigned asset back, handing it over to the employee found by
    `handover_search`, and approve it, so the asset ends up UNASSIGNED. Used to
    prepare test data: it submits straight from the Asset Un Assign form.
    """
    unassign_page.navigate_here()
    unassign_page.select_asset_by_serial(serial)
    unassign_page.add_to_grid()
    unassign_page.select_employee(handover_search)
    unassign_page.enter_note(note)
    toast = unassign_page.submit_and_get_toast()
    unassign_page.verify_toast_text(toast, "Asset Un-Assign Submit Successfully", "Submit on Asset Un Assign")

    approval_list_page.navigate_here()
    toast = approval_list_page.approve_transaction_for_serial("UNASSIGN", serial)
    approval_list_page.verify_toast_text(toast, "Approved successfully", "Approve of the UNASSIGN transaction")
    action_logger.info(f"Asset {serial} is now unassigned")


def move_and_approve(
    movement_page, approval_list_page, serial: str, employee_pin: str, building: str, note: str
) -> None:
    """
    Move an assigned asset to a building (and its first floor) and approve the
    movement. Used to prepare test data: it submits straight from the Asset
    Internal Movement form.
    """
    movement_page.navigate_here()
    movement_page.select_asset_by_serial(serial)
    movement_page.add_to_grid()
    movement_page.select_employee(employee_pin)
    movement_page.select_building_and_first_floor(building)
    movement_page.enter_note(note)
    toast = movement_page.submit_and_get_toast()
    movement_page.verify_toast_text(
        toast, "Asset Internal-Movement Submit Successfully", "Submit on Asset Internal Movement"
    )

    approval_list_page.navigate_here()
    toast = approval_list_page.approve_transaction_for_serial("TRANSFER", serial)
    approval_list_page.verify_toast_text(toast, "Approved successfully", "Approve of the TRANSFER transaction")
    action_logger.info(f"Asset {serial} is now moved to {building}")
