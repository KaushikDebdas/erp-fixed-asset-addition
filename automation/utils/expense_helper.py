"""
expense_helper.py: gives an Asset Expense test the saved Furniture asset and an
APPROVED expense of each source (Inventory, Accounts), so every expense test
file can run alone or after another.

How it works:
    The asset is the saved Furniture asset (item "furniture", sub type "spot",
    owner AAQ_ASSET_GROUP, test_data/saved_assets.json). An expense does not
    change the asset, so its saved record is never changed.

    An approved expense is remembered under the key

        ("furniture", "expense_<source>", "APPROVED", AAQ_ASSET_GROUP)

    and holds "expense_id", "serial" and "expected" (what was entered). A record
    loaded from the saved file is checked once on the Asset Expense Approval
    list; an expense that is not APPROVED there is removed and a new one is
    made (create, Submit, Approve).

Example:
    serial = expenses.get_serial()
    record = expenses.get_approved_expense(INVENTORY)
    expense_id = record["expense_id"]
"""
from test_data.asset_expense_data import (
    EXPENSE_ASSET_ITEM,
    EXPENSE_ASSET_SUB_TYPE,
    new_expense_ref,
)
from test_data.asset_registration_data import AAQ_ASSET_GROUP
from utils.expense_flow import approve_expense, create_expense


def skip_screenshot(description: str) -> None:
    """Take no screenshot: used when the helper makes an expense only to set up a test."""
    return None


class ExpenseHelper:
    """Finds, creates and remembers the saved asset's approved expenses."""

    def __init__(self, registrations, expense_page, expense_approval_page, remembered: dict):
        """
        `registrations` gives the saved Furniture asset. The two page objects
        make a missing expense. `remembered` is the dictionary shared by the
        whole test run.
        """
        self.registrations = registrations
        self.expense_page = expense_page
        self.expense_approval_page = expense_approval_page
        self.remembered = remembered

    def make_key(self, source: str) -> tuple:
        """Return the key the approved expense of this source is remembered under."""
        return (EXPENSE_ASSET_ITEM, f"expense_{source.lower()}", "APPROVED", AAQ_ASSET_GROUP)

    def get_serial(self) -> str:
        """Return the Asset Serial of the saved Furniture asset (a new one is created when none is left)."""
        record = self.registrations.get_approved(EXPENSE_ASSET_ITEM, EXPENSE_ASSET_SUB_TYPE, AAQ_ASSET_GROUP)
        return record["serial"]

    def is_still_valid(self, source: str) -> bool:
        """
        Return True if the remembered expense of this source can be used. A
        record loaded from the saved file is checked once on the Asset Expense
        Approval list; one that is not APPROVED there is removed.
        """
        key = self.make_key(source)
        if key not in self.remembered:
            return False
        if key in self.remembered.trusted:
            return True
        expense_id = self.remembered[key]["expense_id"]
        self.expense_approval_page.navigate_here()
        self.expense_approval_page.find_expense(expense_id, "APPROVED")
        if self.expense_approval_page.get_row_status(expense_id) == "APPROVED":
            self.remembered.trusted.add(key)
            return True
        self.remembered.pop(key, None)
        return False

    def get_approved_expense(self, source: str) -> dict:
        """Return the approved expense of this source, making one (create, Submit, Approve) when none is saved."""
        if not self.is_still_valid(source):
            serial = self.get_serial()
            created = create_expense(
                self.expense_page, serial, source, new_expense_ref(), "submit", skip_screenshot
            )
            approve_expense(
                self.expense_approval_page, self.expense_page,
                created["expense_id"], created["expected"], skip_screenshot,
            )
            self.remember_approved_expense(source, created)
        return self.remembered[self.make_key(source)]

    def remember_approved_expense(self, source: str, created: dict) -> dict:
        """Save an expense that was just approved (the result of `create_expense`) for later tests."""
        self.remembered[self.make_key(source)] = {
            "expense_id": created["expense_id"],
            "serial": created["expected"]["serial"],
            "expected": created["expected"],
        }
        return self.remembered[self.make_key(source)]
