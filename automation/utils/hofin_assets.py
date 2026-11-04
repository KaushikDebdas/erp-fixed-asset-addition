"""
hofin_assets.py: registers assets through HOFIN > HOFA > HOFIN and returns the
REAL asset serials the system generated, so a test never hardcodes a serial.

This is the HOFIN counterpart of the AAQ registration (utils/registration_helper.py).
Both stay in the suite side by side: a test asks for `registrations` / `assets`
for an AAQ asset, and for `hofin_assets` for a HOFIN asset.

Two kinds of asset:
    normal asset     a new parent asset with no extended asset
                         record = hofin_assets.get_normal_asset()
                         record["serial"]                     e.g. "BBDASR00227759"
    parent + extended a new parent asset with extended assets added to it
                         pair = hofin_assets.get_parent_with_extended()
                         pair["parent"]                       e.g. "BBDASR00227760"
                         pair["extended"]                     e.g. ["BBDASR00227760-1", "BBDASR00227760-2"]

How the real serial is found:
    Each registration types its own Item Specification (AUTO-SPEC_<date>_<time>).
    After the HOFIN approval, the newest parent assets of the item are opened in
    the HOFA Asset Serial Global List until that Item Specification is found.
    An extended asset's serial is read from its parent's Addition History tab:
    it is the one serial that was not there before the addition.

`get_normal_asset` and `get_parent_with_extended` make the asset once per run
(a few minutes each) and return the same record to every later test. The
`register_*` methods always make a new one.
"""
from test_data import hofin_asset_data as data
from utils.helpers import unique_name
from utils.logger import action_logger

# Key of the run's records (fixture `hofin_asset_records`) for the shared normal asset and pair
NORMAL_KEY = "normal"
PAIR_KEY = "parent_with_extended"


class HofinAssets:
    """Registers HOFIN assets, finds their real serials and remembers them for the run."""

    def __init__(self, hofin_flow, records: dict):
        """
        `hofin_flow` runs the three roles (utils/hofin_flow.py). `records` is the
        dictionary shared by the whole test run (fixture `hofin_asset_records`).
        """
        self.flow = hofin_flow
        self.records = records

    # ---- once per run ---------------------------------------------------------

    def get_normal_asset(self) -> dict:
        """Return the run's normal HOFIN asset (no extended asset), registering it on first use."""
        if NORMAL_KEY not in self.records:
            self.records[NORMAL_KEY] = self.register_normal_asset()
        return self.records[NORMAL_KEY]

    def get_parent_with_extended(self, extension_count: int = data.GLOBAL_LIST_EXTENDED_COUNT) -> dict:
        """Return the run's parent asset with `extension_count` extended assets, making it on first use."""
        if PAIR_KEY not in self.records:
            self.records[PAIR_KEY] = self.register_parent_with_extended(extension_count)
        return self.records[PAIR_KEY]

    # ---- always new ------------------------------------------------------------

    def register_normal_asset(self) -> dict:
        """
        Register a new asset through the three roles and return its record:
            {"serial": ..., "transaction_no": ..., "item_specification": ...,
             "details": {popup field: text} as the asset was right after registration}
        """
        specification = unique_name(data.ITEM_SPECIFICATION)
        transaction_no = self.flow.create_bill(unique_name("REG"), "", specification)
        self.flow.acknowledge(transaction_no)
        self.flow.approve(transaction_no)
        global_list = self.flow.open_hofa_global_list()
        serial = global_list.find_newest_parent_by_specification(data.ASSET_ITEM_NAME, specification)
        details = global_list.read_popup_fields(serial, data.PARENT_UNCHANGED_FIELDS)
        self.flow.close_all()
        action_logger.info(f"HOFIN asset registered: {serial} (bill {transaction_no})")
        return {
            "serial": serial,
            "transaction_no": transaction_no,
            "item_specification": specification,
            "details": details,
        }

    def add_extended_asset(self, parent_serial: str, known_extended: list) -> dict:
        """
        Add one extended asset to the parent through the three roles and return
        {"serial": the new extended serial, "transaction_no": ...}. `known_extended` are
        the parent's extended serials before this addition.
        """
        transaction_no = self.flow.add_extended_asset(parent_serial, unique_name(data.ITEM_SPECIFICATION))
        new_serial = self.read_new_extended_serial(parent_serial, known_extended)
        action_logger.info(f"Extended asset {new_serial} added to {parent_serial} (bill {transaction_no})")
        return {"serial": new_serial, "transaction_no": transaction_no}

    def register_parent_with_extended(self, extension_count: int) -> dict:
        """
        Register a new parent asset and add `extension_count` extended assets to it. Returns
            {"parent": serial, "extended": [serials in the order added],
             "transaction_nos": [the bills of the additions], "parent_details": the parent's
             popup fields from before the additions, "item_specification": the parent's}
        """
        parent = self.register_normal_asset()
        pair = {
            "parent": parent["serial"],
            "extended": [],
            "transaction_nos": [],
            "parent_details": parent["details"],
            "item_specification": parent["item_specification"],
        }
        for number in range(extension_count):
            added = self.add_extended_asset(pair["parent"], pair["extended"])
            pair["extended"].append(added["serial"])
            pair["transaction_nos"].append(added["transaction_no"])
        return pair

    # ---- reading the result -------------------------------------------------------

    def read_new_extended_serial(self, parent_serial: str, known_extended: list) -> str:
        """
        Open the parent's Addition History in HOFA and return the one extended serial that
        is not in `known_extended`. Fails when there is not exactly one new serial.
        """
        global_list = self.flow.open_hofa_global_list()
        listed = global_list.read_addition_history_serials(parent_serial)
        self.flow.close_all()
        new_serials = [serial for serial in listed if serial not in known_extended]
        assert len(new_serials) == 1, (
            f"After one addition to {parent_serial} its Addition History should have one new extended "
            f"asset, but the new serials are {new_serials} (all listed: {listed})."
        )
        return new_serials[0]

    def remember_new_extended(self, pair: dict, serial: str) -> None:
        """Add an extended serial that a test made itself (stage by stage) to the pair's record."""
        pair["extended"].append(serial)
