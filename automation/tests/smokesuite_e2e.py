"""
smokesuite_e2e.py: end-to-end Asset Registration (AAQ) flow, then barcode, assign, internal movement, un assign and an Inventory expense with its voucher.

Covers the "Asset Registration by AAQ -> Asset Registration List -> Asset
Registration Approval List" journey documented in
automation/automation_mapping/asset_registration_e2e.json (the temporary
mapping that this test was built from) and in the matching element catalog
files: asset_registration_aaq.md, asset_registration_list.md,
asset_registration_approval_list.md. After the asset is approved, its Asset
Serial Number is stored and used on Asset Profile > Generate Barcode
(generate_barcode.md). The asset is then taken through Asset Assign, Asset Un
Assign and Asset Internal Movement (asset_assign.md, asset_unassign.md,
asset_internal_movement.md), with the assigned employee acknowledging the
assignment (asset_assign_acknowledgement.md) and the Asset Serial Global List
checked after the assignment and after the un assign. It ends with an Inventory
Asset Expense and its voucher (asset_expense.md, asset_expense_approval.md,
voucher_search.md).

This is a single-role flow: one ERP External User logs in once and carries
out every step, so it uses one browser tab rather than the multi-context
pattern used for multi-role flows.
"""
import pytest

from config.settings import TEST_PASSWORD, TEST_USERNAME
from test_data.asset_transaction_data import (
    ACKNOWLEDGE_TOAST,
    ASSIGN,
    ASSIGNEE_NAME,
    ASSIGNEE_PIN,
    HANDOVER_NAME,
    HANDOVER_PIN,
    HANDOVER_SEARCH,
    MOVE_BUILDING,
    TRANSFER,
    UNASSIGN,
)
from test_data.asset_expense_data import INVENTORY, new_expense_ref
from utils.expense_flow import approve_expense, create_expense, submit_draft, verify_voucher
from utils.helpers import unique_name
from utils.logger import action_logger
from utils.transaction_flow import approve_and_verify, submit_draft_from_list

# Test data used to create the registration. Named here, in one place, so
# later assertions compare against exactly what was entered — never a
# re-typed literal.
TEST_DATA = {
    "project": "[015] Microfinance (Dabi)",
    "remarks": "AUTOMATION_TEST registration note",
    "vendor": "ACE IT[P008937]",
    "vendor_name": "ACE IT",
    "vendor_number": "P008937",
    "asset_item_search": "Furniture",
    "asset_item_selected": "Cabinet Table",
    "item_specification": unique_name("AUTOMATION_TEST-SPEC-FURN"),
    "quantity": 1,
    "unit_price": 25000,
}


@pytest.mark.regression
def test_asset_registration_aaq_draft_submit_and_approve(
    page,
    login_page,
    aaq_page,
    registration_list_page,
    approval_list_page,
    generate_barcode_page,
    assign_page,
    unassign_page,
    internal_movement_page,
    transaction_list_page,
    transaction_approval_page,
    asset_serial_global_list_page,
    acknowledgement_page,
    expense_page,
    expense_approval_page,
    voucher_search_page,
    assignee_screenshot,
    take_screenshot,
):
    """
    Asset Registration (AAQ) end-to-end flow: create a registration as a
    Draft, submit it for approval, then review and approve it from the
    Asset Registration Approval List, then generate the barcode for the
    new asset's Asset Serial Number. Approve must show the exact success
    toast; any other message fails the test.

    The same asset is then assigned (Draft, Submit, Approve), acknowledged by
    the assigned employee (a second login) in Asset Assign Acknowledgement, and
    checked in the Asset Serial Global List as ASSIGNED, moved to a new building and
    floor with an Internal Movement (Draft, Submit, Approve), and finally
    unassigned (Draft, Submit, Approve) and checked in the Asset Serial Global
    List as UNASSIGNED. The movement comes before the Un Assign because a
    submitted Un Assign takes the asset out of every transaction screen.

    Last, one Asset Expense of 5000 with the Inventory source is created for the
    same asset: saved as a Draft (its Expense ID is stored), opened and
    submitted, approved with the same user, and its voucher is checked in
    Accounting > Voucher Search. It comes last because an expense is not offered
    for an asset that has a transaction still pending.
    """
    # Step 1: log in and close the announcement popup if it appears
    login_page.wait_for_login_page()
    login_page.login(TEST_USERNAME, TEST_PASSWORD)
    login_page.close_popup_if_present()
    take_screenshot("logged in to ERP")

    # Step 2: navigate to Fixed Asset > Registration > Asset Registration by AAQ
    aaq_page.navigate_here()
    take_screenshot("asset registration by aaq form opened")

    # Step 3: fill the AAQ form with the named test data
    aaq_page.select_project(TEST_DATA["project"])
    aaq_page.choose_spot_purchase()
    purchase_date = aaq_page.set_purchase_date_equal_to_registration_date()
    aaq_page.enter_remarks(TEST_DATA["remarks"])
    aaq_page.select_vendor(TEST_DATA["vendor"])
    aaq_page.select_asset_item(TEST_DATA["asset_item_search"], TEST_DATA["asset_item_selected"])
    aaq_page.enter_item_details(
        TEST_DATA["item_specification"], TEST_DATA["quantity"], TEST_DATA["unit_price"]
    )
    aaq_page.add_asset_line()
    take_screenshot("asset registration form filled")

    # Step 4: Purchase Date must equal Registration Date, confirmed by reading
    # the same auto-filled value back instead of hardcoding two separate dates
    registration_date = aaq_page.read_registration_date()
    assert purchase_date == registration_date, (
        f"Expected Purchase Date to equal Registration Date ({registration_date}) "
        f"but Purchase Date was set to {purchase_date}."
    )

    # Step 5: click Draft and confirm the exact success toast
    aaq_page.draft_and_verify_success()
    take_screenshot("draft saved successfully")

    # Step 6: find the drafted registration in Asset Registration List
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("DRAFT")
    registration_number = registration_list_page.get_newest_registration_number()
    registration_list_page.verify_status(registration_number, "DRAFT")
    take_screenshot(f"registration {registration_number} found as DRAFT")

    # Step 7: reopen the Draft record and submit it for approval
    registration_list_page.open_registration(registration_number)
    aaq_page.submit_and_verify_success()
    take_screenshot("draft submitted for approval")

    # Step 8: confirm the status moved from DRAFT to PENDING
    registration_list_page.navigate_here()
    registration_list_page.filter_by_status("PENDING")
    registration_list_page.verify_status(registration_number, "PENDING")
    take_screenshot(f"registration {registration_number} confirmed as PENDING")

    # Step 9: open the registration in the Approval List by clicking its
    # Registration Number link
    approval_list_page.navigate_here()
    approval_list_page.filter_by_registration_number(registration_number)
    approval_list_page.open_registration_popup(registration_number)
    take_screenshot("asset registration view popup opened")

    # Step 10: the popup is for the registration taken from the Asset
    # Registration List, and every submitted field matches TEST_DATA
    approval_list_page.verify_popup_registration_number(registration_number)
    approval_list_page.verify_popup_details(
        [
            registration_number,
            TEST_DATA["project"],
            registration_date,
            purchase_date,
            TEST_DATA["remarks"],
            TEST_DATA["vendor_name"],
            TEST_DATA["vendor_number"],
            TEST_DATA["asset_item_selected"],
            TEST_DATA["item_specification"][:30],  # the popup truncates long text
            str(TEST_DATA["quantity"]),
            str(TEST_DATA["unit_price"]),
        ]
    )
    take_screenshot("asset registration view popup details verified")

    # Step 11: click Approve inside the popup and confirm the success toast
    approval_list_page.approve_from_popup_and_verify_success(registration_number)
    take_screenshot("registration approved")

    # Step 12: reopen the registration and store the generated Asset Serial
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

    # Step 13: open Asset Profile > Generate Barcode and search the stored
    # Asset Serial Number
    generate_barcode_page.navigate_here()
    generate_barcode_page.search_by_serial(asset_serial)
    take_screenshot(f"generate barcode searched for {asset_serial}")

    # Step 14: the stored Asset Serial Number is shown in the results
    assert generate_barcode_page.is_serial_listed(asset_serial), (
        f"Expected Asset Serial {asset_serial} to be listed on Generate Barcode "
        "after searching for it, but it was not found."
    )

    # Step 15: tick the asset, set the print quantity to 2, and click Generate;
    # the barcode PDF opens in a new tab
    generate_barcode_page.tick_row(asset_serial)
    generate_barcode_page.set_default_quantity(2)
    assert generate_barcode_page.get_row_print_quantity(asset_serial) == "2"
    take_screenshot(f"asset {asset_serial} ticked with quantity 2")
    report_url = generate_barcode_page.generate_and_get_report_url()
    assert "generateAssetBarcodeReport" in report_url
    assert "format=PDF" in report_url

    # Step 16: Asset Assign: fill the form for the registered asset and save
    # it as a Draft
    assign_note = "AUTOMATION_TEST assign note"
    assign_page.navigate_here()
    assign_page.select_asset_by_serial(asset_serial)
    assert assign_page.get_value("assetSerialId").startswith(asset_serial)
    assert assign_page.get_value("previousAssignStatus") == "UNASSIGNED"
    assign_page.add_to_grid()
    assign_page.select_employee(ASSIGNEE_PIN)
    assign_page.enter_note(assign_note)
    assign_date = assign_page.get_transaction_date().replace("-", "/")
    take_screenshot("assign form filled")
    toast = assign_page.draft_and_get_toast()
    take_screenshot("assign draft saved")
    assert toast == "Asset Assign Draft Successfully", f"Unexpected toast: '{toast}'"
    assign_expected = {
        "employee_pin": ASSIGNEE_PIN,
        "employee_name": ASSIGNEE_NAME,
        "note": assign_note,
        "transaction_date": assign_date,
    }

    # Step 17: Transaction List: check the Assign Draft, open Edit, and Submit it
    submit_draft_from_list(
        transaction_list_page, assign_page, ASSIGN, asset_serial, assign_expected,
        "Asset Assign Submit Successfully", take_screenshot,
    )

    # Step 18: Transaction Approval List: check the popup and Approve the assignment
    approve_and_verify(transaction_approval_page, ASSIGN, asset_serial, assign_expected, take_screenshot)

    # Step 19: Asset Assign Acknowledgement: the assigned employee (a second
    # login) opens the screen, verifies the Asset Serial Number in Details, and
    # acknowledges the assignment
    acknowledgement_page.navigate_here()
    pending_before = acknowledgement_page.get_pending_count()
    assert asset_serial not in acknowledgement_page.get_my_assigned_serials(), (
        "The asset should not be in My Assigned Asset before it is acknowledged."
    )
    acknowledgement_page.open_details_of_row_with_serial(asset_serial)
    assignee_screenshot(f"acknowledgement details of {asset_serial}")
    assert acknowledgement_page.get_popup_asset_serials() == [asset_serial]
    assert acknowledgement_page.get_popup_value("assignedEmployeePinNo") == ASSIGNEE_PIN
    assert acknowledgement_page.get_popup_value("assignedEmployee") == ASSIGNEE_NAME
    assert acknowledgement_page.get_popup_value("remarks") == assign_note
    toast = acknowledgement_page.acknowledge_in_popup_and_get_toast()
    assignee_screenshot("assignment acknowledged")
    assert toast == ACKNOWLEDGE_TOAST, f"Expected '{ACKNOWLEDGE_TOAST}' but found '{toast}'."
    assert acknowledgement_page.get_pending_count() == pending_before - 1
    assert asset_serial in acknowledgement_page.get_my_assigned_serials()

    # Step 20: Asset Serial Global List: the asset is listed as ASSIGNED to the employee
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(asset_serial)
    assert asset_serial_global_list_page.is_serial_listed(asset_serial), (
        f"Expected Asset Serial {asset_serial} in the Asset Serial Global List after the assignment."
    )
    assert asset_serial_global_list_page.get_assign_status(asset_serial) == "ASSIGNED"
    asset_serial_global_list_page.open_asset_popup(asset_serial)
    assert asset_serial_global_list_page.get_popup_value("employeePin") == ASSIGNEE_PIN
    assert asset_serial_global_list_page.get_popup_value("assignedEmployee") == ASSIGNEE_NAME
    take_screenshot(f"asset {asset_serial} is assigned")
    asset_serial_global_list_page.close_popup()

    # Step 21: Asset Internal Movement: move the assigned asset (Draft first)
    move_note = "AUTOMATION_TEST internal movement note"
    internal_movement_page.navigate_here()
    internal_movement_page.select_asset_by_serial(asset_serial)
    assert internal_movement_page.get_value("previousAssignStatus") == "ASSIGNED"
    internal_movement_page.add_to_grid()
    internal_movement_page.select_employee(ASSIGNEE_PIN)
    floor = internal_movement_page.select_building_and_first_floor(MOVE_BUILDING)
    internal_movement_page.enter_note(move_note)
    move_date = internal_movement_page.get_transaction_date().replace("-", "/")
    take_screenshot("internal movement form filled")
    toast = internal_movement_page.draft_and_get_toast()
    take_screenshot("internal movement draft saved")
    assert toast == "Asset Internal-Movement Draft Successfully", f"Unexpected toast: '{toast}'"
    move_expected = {
        "employee_pin": ASSIGNEE_PIN,
        "employee_name": ASSIGNEE_NAME,
        "note": move_note,
        "transaction_date": move_date,
        "building": MOVE_BUILDING,
        "floor": floor,
    }

    # Step 22: Transaction List: check the Internal Movement Draft, open Edit, and Submit it
    submit_draft_from_list(
        transaction_list_page, internal_movement_page, TRANSFER, asset_serial, move_expected,
        "Asset Internal-Movement Submit Successfully", take_screenshot,
    )

    # Step 23: Transaction Approval List: check the popup and Approve the movement
    approve_and_verify(transaction_approval_page, TRANSFER, asset_serial, move_expected, take_screenshot)

    # Step 24: Asset Un Assign: create a Draft for the same asset, handing it over to
    # a different employee
    unassign_note = "AUTOMATION_TEST unassign note"
    unassign_page.navigate_here()
    unassign_page.select_asset_by_serial(asset_serial)
    assert unassign_page.get_value("previousAssignStatus") == "ASSIGNED"
    assert unassign_page.get_value("assignedEmployeePinNo") == ASSIGNEE_PIN
    unassign_page.add_to_grid()
    unassign_page.select_employee(HANDOVER_SEARCH)
    assert unassign_page.get_employee_pin() == HANDOVER_PIN
    unassign_page.enter_note(unassign_note)
    unassign_date = unassign_page.get_transaction_date().replace("-", "/")
    take_screenshot("unassign form filled")
    toast = unassign_page.draft_and_get_toast()
    take_screenshot("unassign draft saved")
    assert toast == "Asset Un-Assign Draft Successfully", f"Unexpected toast: '{toast}'"
    unassign_expected = {
        "employee_pin": HANDOVER_PIN,
        "employee_name": HANDOVER_NAME,
        "note": unassign_note,
        "transaction_date": unassign_date,
    }

    # Step 25: Transaction List: check the Un Assign Draft, open Edit, and Submit it
    submit_draft_from_list(
        transaction_list_page, unassign_page, UNASSIGN, asset_serial, unassign_expected,
        "Asset Un-Assign Submit Successfully", take_screenshot,
    )

    # Step 26: Transaction Approval List: check the popup and Approve the Un Assign
    approve_and_verify(transaction_approval_page, UNASSIGN, asset_serial, unassign_expected, take_screenshot)

    # Step 27: Asset Serial Global List: the asset is listed as UNASSIGNED
    asset_serial_global_list_page.navigate_here()
    asset_serial_global_list_page.search_by_serial(asset_serial)
    assert asset_serial_global_list_page.is_serial_listed(asset_serial), (
        f"Expected Asset Serial {asset_serial} in the Asset Serial Global List after the un assign."
    )
    take_screenshot(f"asset {asset_serial} is unassigned")
    assert asset_serial_global_list_page.get_assign_status(asset_serial) == "UNASSIGNED"

    # Step 28: Asset Expense (Inventory source): fill the form for the same asset
    # (expense amount 5000, a random Expense Ref., vendor, Debit A/C) and save it
    # as a Draft. The generated Expense ID is stored.
    expense_ref = new_expense_ref()
    created = create_expense(expense_page, asset_serial, INVENTORY, expense_ref, "draft", take_screenshot)
    expense_id = created["expense_id"]
    expense_expected = created["expected"]
    action_logger.info(f"Stored Expense ID: {expense_id}")
    assert expense_id.startswith("BBDEXP"), f"Unexpected Expense ID '{expense_id}'."

    # Step 29: open the Draft by its Expense ID, check the saved values, and Submit it
    submit_draft(expense_page, expense_id, expense_expected, take_screenshot)

    # Step 30: Asset Expense Approval: find the expense by the stored Expense ID,
    # check the popup, and Approve it with the same user
    approve_expense(expense_approval_page, expense_page, expense_id, expense_expected, take_screenshot)

    # Step 31: Accounting > Voucher > Voucher Search: find the voucher by the
    # Expense ID and check the Preview PDF (accounts, amounts, Dr./Cr., reference)
    verify_voucher(voucher_search_page, expense_id, expense_expected, take_screenshot)
