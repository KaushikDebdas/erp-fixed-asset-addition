"""
transaction_helper.py: brings an asset of the pool into the state an Asset
Transaction test needs (UNASSIGNED, ASSIGNED, or an acknowledgement waiting),
so every test file can run alone or after another.

How it works:
    The assets are the two usage assets of the asset pool (utils/asset_pool.py,
    test_data/asset_slots.py): usage_a (the Draft + Submit path) and usage_b (the
    Submit-only path). Every method here reads the asset's REAL Assign Status from
    the Asset Serial Global List and does only the steps that are missing:

        serial = transactions.ensure_unassigned()            # usage_a, unassigns it when it is assigned
        serial = transactions.ensure_assigned("usage_b")     # assigns usage_b when it is unassigned

    In a full run the files run in the order assign, acknowledge, movement,
    unassign, so each one finds the state it needs and nothing is made behind a
    test's back. Run alone, a test makes the missing steps first.
    When the asset cannot reach the needed state, the method fails with a
    message that says what was expected and what was found.

Example:
    serial = transactions.ensure_assigned()
    internal_movement_page.navigate_here()
"""
from test_data.asset_transaction_data import (
    ASSIGNED,
    ASSIGNEE_PIN,
    HANDOVER_SEARCH,
    MOVE_BUILDING,
    SETUP_ASSIGN_NOTE,
    SETUP_MOVE_NOTE,
    SETUP_UNASSIGN_NOTE,
    UNASSIGNED,
)
from utils.asset_flow import assign_and_approve, move_and_approve, unassign_and_approve

# The slots (test_data/asset_slots.py) of the two assets the transaction tests use
USAGE_A = "usage_a"
USAGE_B = "usage_b"


class TransactionHelper:
    """Reads the real state of a usage asset and sets up the state a test needs."""

    def __init__(
        self, assets, assign_page, unassign_page, movement_page, approval_page, global_list_page
    ):
        """
        `assets` is the asset pool that gives the asset of a slot. The other five are
        the page objects used to read its status and to make the missing
        transactions. They all work in the main user's browser tab.
        """
        self.assets = assets
        self.assign_page = assign_page
        self.unassign_page = unassign_page
        self.movement_page = movement_page
        self.approval_page = approval_page
        self.global_list_page = global_list_page

    # ------------------------------------------------------------------
    # Reading the asset
    # ------------------------------------------------------------------

    def get_serial(self, slot: str = USAGE_A) -> str:
        """Return the Asset Serial of the asset of this slot (a new one is created when the pool has none)."""
        return self.assets.get(slot)["serial"]

    def read_assign_status(self, serial: str) -> str:
        """Return the asset's real Assign Status (ASSIGNED or UNASSIGNED) from the Global List."""
        return self.global_list_page.open_and_read_assign_status(serial)

    def read_profile_row(self, serial: str) -> dict:
        """Return the asset's Global List row (item, sub category, category, group, statuses)."""
        self.global_list_page.navigate_here()
        self.global_list_page.search_by_serial(serial)
        return self.global_list_page.get_row_values(serial)

    def require_status(self, serial: str, found: str, wanted: str) -> None:
        """Fail with a clear message when the asset's Assign Status is not the one a test needs."""
        assert found == wanted, (
            f"Asset {serial} should be {wanted} but its Assign Status is '{found}' "
            f"(the transaction that should have changed it did not)."
        )

    # ------------------------------------------------------------------
    # The states
    # ------------------------------------------------------------------

    def ensure_unassigned(self, slot: str = USAGE_A) -> str:
        """Make sure the asset is UNASSIGNED (unassign it when it is assigned) and return its serial."""
        serial = self.get_serial(slot)
        status = self.read_assign_status(serial)
        if status == ASSIGNED:
            self.unassign(serial)
            status = self.read_assign_status(serial)
        self.require_status(serial, status, UNASSIGNED)
        return serial

    def ensure_assigned(self, slot: str = USAGE_A) -> str:
        """Make sure the asset is ASSIGNED to the test employee (assign it when it is unassigned) and return its serial."""
        serial = self.get_serial(slot)
        status = self.read_assign_status(serial)
        if status == UNASSIGNED:
            self.assign(serial)
            status = self.read_assign_status(serial)
        self.require_status(serial, status, ASSIGNED)
        return serial

    def ensure_acknowledgement_pending(self, acknowledgement_page, slot: str = USAGE_A) -> str:
        """
        Make sure an assignment of the asset waits for acknowledgement in the
        assigned employee's Pending list, and return the serial.
        `acknowledgement_page` works in the assigned employee's tab. An asset
        that is assigned with nothing waiting is unassigned and assigned again.
        """
        serial = self.get_serial(slot)
        status = self.read_assign_status(serial)
        if status == ASSIGNED:
            acknowledgement_page.navigate_here()
            if acknowledgement_page.has_pending_for_serial(serial):
                return serial
            self.unassign(serial)
        self.assign(serial)
        acknowledgement_page.navigate_here()
        assert acknowledgement_page.has_pending_for_serial(serial), (
            f"Asset {serial} was assigned but no acknowledgement for it is waiting for employee {ASSIGNEE_PIN}."
        )
        return serial

    # ------------------------------------------------------------------
    # The transactions that change the state (each one submits straight from the form and approves)
    # ------------------------------------------------------------------

    def assign(self, serial: str) -> None:
        """Assign the asset to the test employee and approve it."""
        assign_and_approve(self.assign_page, self.approval_page, serial, ASSIGNEE_PIN, SETUP_ASSIGN_NOTE)

    def unassign(self, serial: str) -> None:
        """Hand the asset over to the hand-over employee and approve it, so the asset is UNASSIGNED."""
        unassign_and_approve(self.unassign_page, self.approval_page, serial, HANDOVER_SEARCH, SETUP_UNASSIGN_NOTE)

    def move(self, serial: str) -> None:
        """Move the asset to the movement building and approve it."""
        move_and_approve(
            self.movement_page, self.approval_page, serial, ASSIGNEE_PIN, MOVE_BUILDING, SETUP_MOVE_NOTE
        )
