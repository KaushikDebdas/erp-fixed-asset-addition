"""
asset_pool.py: hands out the approved assets of the test suite by slot name, so a
test never creates an asset it does not need and never hardcodes a serial.

How it works:
    assets.get("sale_profit_a")
    - the asset of that slot is already there (the registration tests or an earlier
      flow made it): it is returned as it is;
    - it is not there (the test runs on its own): it is registered, approved and
      remembered right now, then returned.
    So every test can run alone, and a full run never creates the same asset twice.

A slot with `reuse_from` (see test_data/asset_slots.py) first tries the asset of that
other slot. The asset is reused only when its real state allows it: it is UNASSIGNED
(read from the Asset Serial Global List) and in no pending process (read from the
Asset In Pending Process List). Otherwise the slot gets its own new asset.

An asset that a flow uses up (sold, written off, split, in a challan) is given back with
`assets.consume(slot)`, so a later `get` registers a new one.

Example:
    asset = assets.get("write_off_a")
    serial = asset["serial"]
    ... write the asset off ...
    assets.consume("write_off_a")

The record is a dictionary:
    {"slot": "sale_profit_a", "owner": "sale_profit_a", "data": <values entered>,
     "registration_number": "757877", "serial": "BBDASR00228049"}
`owner` is the slot the asset was registered under (it differs from `slot` when a slot reuses an asset).
"""
from test_data.asset_slots import ASSET_SLOTS
from utils.logger import action_logger

UNASSIGNED = "UNASSIGNED"


class AssetPool:
    """Finds, creates, lends and takes back the approved assets of the suite."""

    def __init__(self, registrations, global_list_page, pending_list_page, shared: dict):
        """
        `registrations` registers and approves an asset when none exists (RegistrationHelper).
        The two pages read an asset's real state. `shared` is the dictionary shared by the
        whole test run (fixture `shared_asset_pool`): {"records": {slot: record}, "created": [slots]}.
        """
        self.registrations = registrations
        self.global_list_page = global_list_page
        self.pending_list_page = pending_list_page
        self.records = shared.setdefault("records", {})
        self.created = shared.setdefault("created", [])

    def get(self, slot: str) -> dict:
        """Return the record of the asset of this slot, registering and approving one when it does not exist yet."""
        if slot in self.records:
            return self.records[slot]
        details = ASSET_SLOTS[slot]
        source = details.get("reuse_from", "")
        if source != "" and self.is_free(source):
            action_logger.info(f"Asset pool: slot {slot} reuses the asset of slot {source}")
            self.records[slot] = {**self.records[source], "slot": slot}
            return self.records[slot]
        created = self.registrations.get_approved_of(slot)
        self.records[slot] = {**created, "slot": slot, "owner": slot}
        if slot not in self.created:
            self.created.append(slot)
        action_logger.info(f"Asset pool: slot {slot} has asset {created['serial']} ({len(self.created)} slot assets registered this run)")
        return self.records[slot]

    def is_free(self, slot: str) -> bool:
        """
        Return True when the asset of this slot exists and can be used by another flow: its Assign
        Status is UNASSIGNED and it is in no pending process. False when the slot has no asset yet.
        """
        record = self.records.get(slot)
        if record is None:
            return False
        serial = record["serial"]
        if self.global_list_page.open_and_read_assign_status(serial) != UNASSIGNED:
            action_logger.info(f"Asset pool: asset {serial} of slot {slot} is not UNASSIGNED, so it is not reused")
            return False
        self.pending_list_page.navigate_here()
        self.pending_list_page.search_serial_and_wait_for_result(serial)
        if self.pending_list_page.read_rows_with_serial(serial):
            action_logger.info(f"Asset pool: asset {serial} of slot {slot} is in a pending process, so it is not reused")
            return False
        return True

    def consume(self, slot: str) -> None:
        """Mark the asset of this slot as used up: it is removed from the pool, so the next `get` of any slot that held it registers a new one."""
        record = self.records.get(slot)
        if record is None:
            return
        serial = record["serial"]
        for name in list(self.records):
            if self.records[name]["serial"] == serial:
                self.records.pop(name)
        self.registrations.forget(record, "APPROVED", record["owner"])
        action_logger.info(f"Asset pool: asset {serial} (slot {slot}) is used up")
