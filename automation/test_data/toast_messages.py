"""
toast_messages.py: every toast (pop-up) message the Fixed Asset screens show,
in one place, grouped by screen. Tests, page classes and helpers import the
text from here and never type a message themselves.

A toast with more than one line is a list with one entry per line, in the
order the screen shows them. Check a toast with
`BasePage.verify_toast_text(actual, expected, action)` (pages/base_page.py).
"""

# ---------------------------------------------------------------------------
# Asset Registration (AAQ), Registration List, Approval List
# ---------------------------------------------------------------------------
PURCHASE_DATE_TOAST = "Please Select Purchase Date."
VENDOR_TOAST = "Please Select a supplier."
NO_ASSET_LINE_TOAST = "No Asset in List to perform operation"
MINIMUM_PRICE_TOAST = "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka."
MEASUREMENT_TOAST = "Measurement must be greater than zero for this asset group"
SUBMIT_SUCCESS_TOAST = "Asset registration(AAQ) submitted Successfully!"
NOTHING_TICKED_TOAST = "You have to select a Registration first"
APPROVE_SUCCESS_TOAST = "Asset registration approved successfully."

# ---------------------------------------------------------------------------
# Asset Serial Global List (the Change popups)
# ---------------------------------------------------------------------------
SOURCE_OF_FUND_TOAST = "Please select a Source Of Fund."
NOTE_TOAST = "Please add a note."
ITEM_SPECIFICATION_TOAST = "Please select a Item Specification/IMEI/SL No."
STATUS_UPDATED_TOAST = "Asset profile status updated successfully."

# ---------------------------------------------------------------------------
# Asset Serial Split, Split List, Split Approval List
# ---------------------------------------------------------------------------
SPLIT_REFUSED_MESSAGE = "Cannot split: Please set a valid measurement above zero."
SPLIT_SUBMITTED_MESSAGE = "Asset split submitted successfully"
SPLIT_NOTHING_TICKED_MESSAGE = "You have to select a split first"
SPLIT_APPROVED_MESSAGE = "Asset Split approved successfully"

# ---------------------------------------------------------------------------
# Asset Assign, Internal Movement, Un Assign, Transaction Approval, Acknowledgement
# ---------------------------------------------------------------------------
ASSIGN_DRAFT_TOAST = "Asset Assign Draft Successfully"
ASSIGN_SUBMIT_TOAST = "Asset Assign Submit Successfully"
MOVEMENT_DRAFT_TOAST = "Asset Internal-Movement Draft Successfully"
MOVEMENT_SUBMIT_TOAST = "Asset Internal-Movement Submit Successfully"
UNASSIGN_DRAFT_TOAST = "Asset Un-Assign Draft Successfully"
UNASSIGN_SUBMIT_TOAST = "Asset Un-Assign Submit Successfully"
UNASSIGN_SAME_EMPLOYEE_TOAST = "Asset assigned to same employee!"
TRANSACTION_APPROVE_TOAST = "Approved successfully"
# Shown when an extended asset's serial (<parent>-1) is searched in Asset Assign (CR FAHOV2-643)
ASSET_NOT_FOUND_TOAST = "No asset found"
ACKNOWLEDGE_TOAST = "Acknowledged successfully"

# ---------------------------------------------------------------------------
# Asset Expense and Expense Approval
# ---------------------------------------------------------------------------
EXPENSE_DRAFT_TOAST = "Asset expense successfully drafted."
EXPENSE_SUBMIT_TOAST = "Asset expense successfully submitted."
EXPENSE_APPROVE_TOAST_START = "Asset Expense approved successfully."
EXPENSE_VENDOR_REQUIRED_TOAST = "Vendor/Supplier/Lessor Name is required."

# ---------------------------------------------------------------------------
# Asset Shipment, Transfer Challan, Challan Approval, Gate Pass
# ---------------------------------------------------------------------------
SHIPMENT_CREATED_TOAST = ["Asset Shipment Initiated Successfuly"]
SHIPMENT_NO_CHALLAN_TOAST = ["Please add at least one challan"]
SHIPMENT_NO_APPROVED_CHALLAN_TOAST = ["Approve at least one challan"]
SHIPMENT_APPROVED_TOAST = ["Shipment approved successfully", "Gate pass generated successfully"]
CHALLAN_NO_FROM_PROJECT_TOAST = ["Please select from project"]
CHALLAN_NO_TO_PROJECT_TOAST = ["Please select to project"]
CHALLAN_NO_ITEMS_TOAST = ["No Items in Challan to perform operation"]
CHALLAN_DRAFTED_TOAST = ["Challan drafted successfully"]
CHALLAN_SERIAL_ADDED_TOAST = ["Asset serial added Successfuly"]
CHALLAN_DELETED_TOAST = ["Challan deleted successfuly"]
CHALLAN_SUBMITTED_TOAST = ["Challan submitted successfully"]
CHALLAN_APPROVED_TOAST = "Challan approved successfully."

# ---------------------------------------------------------------------------
# Asset Write-off
# ---------------------------------------------------------------------------
WRITE_OFF_DRAFT_TOAST = "Asset write-off drafted successfully"
WRITE_OFF_SUBMIT_TOAST = "Asset write-off submitted successfully"
WRITE_OFF_APPROVE_TOAST = ["Asset write-off approved successfully.", "Journal voucher submitted successfully!"]

# ---------------------------------------------------------------------------
# Asset Sale
# ---------------------------------------------------------------------------
SALE_DRAFT_TOAST = "Asset sale drafted successfully"
SALE_SUBMIT_TOAST = "Asset sale submitted successfully"
SALE_APPROVE_TOAST = ["Asset disposal sale approved successfully.", "Journal and Credit voucher submitted successfully!"]

# ---------------------------------------------------------------------------
# Single Challan: Out Challan, Approval List (Draft and Submit show no message)
# ---------------------------------------------------------------------------
SINGLE_CHALLAN_SERIAL_ADDED_TOAST = "Asset serial added successfully"
SINGLE_CHALLAN_APPROVE_TOAST = ["Challan approved successfully.", "Gate pass generated successfully"]

