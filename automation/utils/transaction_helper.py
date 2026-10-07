"""
transaction_helper.py: brings the saved Furniture asset into the state an Asset
Transaction test needs (UNASSIGNED, ASSIGNED, a transaction of a given type, or
an acknowledgement waiting), so every test file can run alone or after another.

How it works:
    Only the saved Furniture asset (item "furniture", sub type "spot", owner
    AAQ_ASSET_GROUP, test_data/saved_assets.json) is used for Assign, Internal
    Movement, Un Assign and Acknowledgement. Its saved record is never changed:
    it stays under the APPROVED key. Instead, every method here reads the
    asset's REAL Assign Status from the Asset Serial Global List and does only
    the steps that are missing:

        serial = transactions.ensure_unassigned()    # unassigns it when it is assigned
        serial = transactions.ensure_assigned()      # assigns it when it is unassigned

    When the asset cannot reach the needed state, the method fails with a
    message that says what was expected and what was found.

Example:
    serial = transactions.ensure_assigned()
    internal_movement_page.navigate_here()
"""
from test_data.asset_registration_data import AAQ_ASSET_GROUP
from test_data.asset_transaction_data import (
    ASSIGN,
    ASSIGNED,
    ASSIGNEE_PIN,
    HANDOVER_SEARCH,
    MOVE_BUILDING,
    SETUP_ASSIGN_NOTE,
    SETUP_MOVE_NOTE,
    SETUP_UNASSIGN_NOTE,
    TRANSFER,
    UNASSIGN,
    UNASSIGNED,
)
from utils.asset_flow import assign_and_approve, move_and_approve, unassign_and_approve

# The saved asset every Asset Transaction test uses
ASSET_ITEM = "furniture"
ASSET_SUB_TYPE = "spot"


class TransactionHelper:
    """Reads the real state of the saved Furniture asset and sets up the state a test needs."""

    def __init__(
        self, registrations, assign_page, unassign_page, movement_page, approval_page, global_list_page
    ):
        """
        `registrations` gives the saved Furniture asset. The other five are the
        page objects used to read its status and to make the missing
        transactions. They all work in the main user's browser tab.
        """
        self.registrations = registrations
        self.assign_page = assign_page
        self.unassign_page = unassign_page
        self.movement_page = movement_page
        self.approval_page = approval_page
        self.global_list_page = global_list_page

    # ------------------------------------------------------------------
    # Reading the asset
    # ------------------------------------------------------------------

    def get_serial(self) -> str:
        """Return the Asset Serial of the saved Furniture asset (a new one is created when none is left)."""
        record = self.registrations.get_approved(ASSET_ITEM, ASSET_SUB_TYPE, AAQ_ASSET_GROUP)
        return record["serial"]

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

    def ensure_unassigned(self) -> str:
        """Make sure the asset is UNASSIGNED (unassign it when it is assigned) and return its serial."""
        serial = self.get_serial()
        status = self.read_assign_status(serial)
        if status == ASSIGNED:
            self.unassign(serial)
            status = self.read_assign_status(serial)
        self.require_status(serial, status, UNASSIGNED)
        return serial

    def ensure_assigned(self) -> str:
        """Make sure the asset is ASSIGNED to the test employee (assign it when it is unassigned) and return its serial."""
        serial = self.get_serial()
        status = self.read_assign_status(serial)
        if status == UNASSIGNED:
            self.assign(serial)
            status = self.read_assign_status(serial)
        self.require_status(serial, status, ASSIGNED)
        return serial

    def ensure_acknowledgement_pending(self, acknowledgement_page) -> str:
        """
        Make sure an assignment of the asset waits for acknowledgement in the
        assigned employee's Pending list, and return the serial.
        `acknowledgement_page` works in the assigned employee's tab. An asset
        that is assigned with nothing waiting is unassigned and assigned again.
        """
        serial = self.get_serial()
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

    def ensure_transaction(self, transaction_type: str) -> str:
        """
        Make sure an APPROVED transaction of this type (ASSIGN, TRANSFER or
        UNASSIGN) that lists the asset is on the Transaction Approval List, and
        return the serial. Only a missing transaction is made.
        """
        serial = self.get_serial()
        self.approval_page.navigate_here()
        row_index = self.approval_page.find_row_with_serial(serial, transaction_type, "APPROVED")
        if row_index >= 0:
            self.approval_page.close_popup()
            return serial
        if transaction_type == ASSIGN:
            self.ensure_unassigned()
            self.assign(serial)
        elif transaction_type == TRANSFER:
            self.ensure_assigned()
            self.move(serial)
        elif transaction_type == UNASSIGN:
            self.ensure_assigned()
            self.unassign(serial)
        else:
            raise AssertionError(f"Unknown transaction type '{transaction_type}'.")
        return serial

    # ------------------------------------------------------------------
    # The transactions that change the state
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
