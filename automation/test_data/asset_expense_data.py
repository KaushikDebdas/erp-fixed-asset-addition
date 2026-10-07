"""
asset_expense_data.py: fixed values used by the Asset Expense tests and the
voucher check that follows an approved expense.
"""
from utils.helpers import random_number

# Expense Source choices on the Asset Expense form
INVENTORY = "Inventory"
ACCOUNTS = "Accounts"

# What the Inventory source needs, matched to the test asset (a Cabinet Table)
EXPENSE_CATEGORY = "Furniture"
EXPENSE_SUB_CATEGORY = "Wooden Furniture"
EXPENSE_ITEM = "Cabinet Table"

# Debit account used for both sources (part of its name is enough to find it)
DEBIT_ACCOUNT = "Other Maintenance Expenses[5108010101-07]"

# Credit account that each source fills in by itself
CREDIT_ACCOUNT = {
    INVENTORY: "Other Inventory [1107010401-02]",
    ACCOUNTS: "Supplier Payable-Opex[2101010301-05]",
}

# Vendor/Supplier/Lessor Name, required for both sources
VENDOR_SEARCH = "ACE IT"
VENDOR_OPTION = "ACE IT[P008937]"

# Expense amount in Taka, as it appears on the screens and on the voucher
EXPENSE_AMOUNT = "5000"
EXPENSE_AMOUNT_ON_VOUCHER = "5,000.00"


def new_expense_ref() -> str:
    """Return a random Expense Ref., for example EXP428774 (it must be different every run)."""
    return "EXP" + random_number(6)

# The saved Furniture asset every Asset Expense test uses (see utils/expense_helper.py)
EXPENSE_ASSET_ITEM = "furniture"
EXPENSE_ASSET_SUB_TYPE = "spot"

# The voucher lines expected after approval: (account code, head of accounts)
VOUCHER_DEBIT = ("5108010101-07", "Other Maintenance Expenses")
VOUCHER_CREDIT = {
    INVENTORY: ("1107010401-02", "Other Inventory"),
    ACCOUNTS: ("2101010301-05", "Supplier Payable-Opex"),
}
