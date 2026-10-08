"""
expense_helper.py: gives an Asset Expense test a usage asset and an APPROVED
expense of each source (Inventory, Accounts), so every expense test file can run
alone or after another.

How it works:
    The assets are the two usage assets of the asset pool (utils/asset_pool.py,
    test_data/asset_slots.py): the Inventory expense uses usage_a (the Draft +
    Submit path) and the Accounts expense uses usage_b (the Submit-only path). An
    expense does not change the asset, so the assets stay usable afterwards.

    An approved expense is remembered for the run under the key

        ("furniture", "expense_<source>", "APPROVED", "expenses")

    and holds "expense_id", "serial" and "expected" (what was entered). When none is
    remembered, one is made (create, Submit, Approve).

Example:
    serial = expenses.get_serial()
    record = expenses.get_approved_expense(INVENTORY)
    expense_id = record["expense_id"]
"""
from test_data.asset_expense_data import (
    ACCOUNTS,
    EXPENSE_ASSET_ITEM,
    INVENTORY,
    new_expense_ref,
)
from utils.expense_flow import approve_expense, create_expense

# The key owner the approved expenses are remembered under
EXPENSE_OWNER = "expenses"

# The pool slot each expense source uses
SLOT_BY_SOURCE = {INVENTORY: "usage_a", ACCOUNTS: "usage_b"}


def skip_screenshot(description: str) -> None:
    """Take no screenshot: used when the helper makes an expense only to set up a test."""
    return None


class ExpenseHelper:
    """Finds, creates and remembers the approved expenses of the usage assets."""

    def __init__(self, assets, expense_page, expense_approval_page, remembered: dict):
        """
        `assets` is the asset pool that gives the asset of a slot. The two page
        objects make a missing expense. `remembered` is the dictionary shared by the
        whole test run.
        """
        self.assets = assets
        self.expense_page = expense_page
        self.expense_approval_page = expense_approval_page
        self.remembered = remembered

    def make_key(self, source: str) -> tuple:
        """Return the key the approved expense of this source is remembered under."""
        return (EXPENSE_ASSET_ITEM, f"expense_{source.lower()}", "APPROVED", EXPENSE_OWNER)

    def get_serial(self, slot: str = "usage_a") -> str:
        """Return the Asset Serial of the asset of this slot (a new one is created when the pool has none)."""
        return self.assets.get(slot)["serial"]

    def is_still_valid(self, source: str) -> bool:
        """Return True if an expense of this source was approved earlier in this run."""
        return self.make_key(source) in self.remembered

    def get_approved_expense(self, source: str) -> dict:
        """Return the approved expense of this source, making one (create, Submit, Approve) when none is remembered."""
        if not self.is_still_valid(source):
            serial = self.get_serial(SLOT_BY_SOURCE[source])
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
        """Remember an expense that was just approved (the result of `create_expense`) for later tests."""
        self.remembered[self.make_key(source)] = {
            "expense_id": created["expense_id"],
            "serial": created["expected"]["serial"],
            "expected": created["expected"],
        }
        return self.remembered[self.make_key(source)]
