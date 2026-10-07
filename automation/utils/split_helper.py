"""
split_helper.py: gives a test the saved Land asset's split in a chosen state
(PENDING or APPROVED), so every split test can run alone or after another.

How it works:
    Only the saved Land asset (item "land", sub type "spot", owner
    AAQ_ASSET_GROUP) is ever split. Once it is split it is used up, so its
    record moves from the APPROVED registration key to a SPLIT key:

        ("land", "spot", "SPLIT", AAQ_ASSET_GROUP)

    The SPLIT record holds the Land's old fields plus:
        "split_no":     the Asset Split No., e.g. "67"
        "split_status": "PENDING", then "APPROVED"
        "new_serials":  the new Asset Serials (only after approval)

    get_pending_split() returns the record of a split waiting for approval, and
    performs the split first when there is none. get_approved_split() approves a
    pending split when needed. When no Land asset is left, the registration
    helper creates a new one (see utils/registration_helper.py).

Example:
    record = splits.get_pending_split()
    serial = record["serial"]

The SPLIT record is saved in test_data/saved_assets.json with the other AAQ
assets (see utils/saved_registrations.py).
"""
from test_data.asset_registration_data import AAQ_ASSET_GROUP
from test_data.asset_split_data import (
    FIRST_LINE_PERCENTAGE,
    SPLIT_INTO,
    SPLIT_REMARKS,
)

# The registration key of the Land asset that may be split
LAND_ITEM = "land"
LAND_SUB_TYPE = "spot"

# The key the Land asset is remembered under after it was split
SPLIT_KEY = (LAND_ITEM, LAND_SUB_TYPE, "SPLIT", AAQ_ASSET_GROUP)


class SplitHelper:
    """Finds, performs and remembers the split of the saved Land asset."""

    def __init__(self, registrations, split_page, split_list_page, split_approval_page, remembered: dict):
        """
        `registrations` is the RegistrationHelper (it gives the Land asset and
        the registration pages). The other three are the split page objects.
        `remembered` is the dictionary shared by the whole test run.
        """
        self.registrations = registrations
        self.split_page = split_page
        self.split_list_page = split_list_page
        self.split_approval_page = split_approval_page
        self.remembered = remembered

    def get_land(self) -> dict:
        """
        Return the approved Land asset that may be split. A Land asset that
        already has a split on the Split List (waiting for approval or approved)
        is used up: it is forgotten and a new Land asset is created.
        """
        land = self.registrations.get_approved(LAND_ITEM, LAND_SUB_TYPE, AAQ_ASSET_GROUP)
        if ("split_list_checked", land["serial"]) not in self.remembered.trusted:
            if self.is_on_split_list(land["serial"]):
                self.registrations.forget(land, "APPROVED", AAQ_ASSET_GROUP)
                land = self.registrations.get_approved(LAND_ITEM, LAND_SUB_TYPE, AAQ_ASSET_GROUP)
            self.remembered.trusted.add(("split_list_checked", land["serial"]))
        return land

    def is_on_split_list(self, serial: str) -> bool:
        """Return True if the Split List already has a split (any status) for this Asset Serial."""
        self.split_list_page.navigate_here()
        self.split_list_page.search_by_serial(serial)
        return self.split_list_page.results_table.locator("tbody tr", has_text=serial).count() > 0

    def is_still_valid(self, status: str) -> bool:
        """
        Return True if the remembered split has this status. A record loaded
        from the saved file is checked once on the Split List; a record whose
        real status differs is removed.
        """
        record = self.remembered.get(SPLIT_KEY)
        if record is None or record["split_status"] != status:
            return False
        if SPLIT_KEY in self.remembered.trusted:
            return True
        self.split_list_page.navigate_here()
        self.split_list_page.search_by_serial(record["serial"])
        if self.split_list_page.get_row_status(record["serial"]) == status:
            self.remembered.trusted.add(SPLIT_KEY)
            return True
        self.remembered.pop(SPLIT_KEY, None)
        return False

    def get_pending_split(self) -> dict:
        """Return the record of a split waiting for approval, performing the split when none is remembered."""
        if not self.is_still_valid("PENDING"):
            land = self.get_land()
            self.split_page.fill_and_submit_split(land["serial"], SPLIT_INTO, SPLIT_REMARKS, FIRST_LINE_PERCENTAGE)
            self.remember_submitted_split(land)
        return self.remembered[SPLIT_KEY]

    def get_approved_split(self) -> dict:
        """Return the record of an approved split (with its new serials), approving a pending split when needed."""
        if not self.is_still_valid("APPROVED"):
            record = self.get_pending_split()
            self.split_approval_page.navigate_here()
            self.split_approval_page.approve_split(record["serial"])
            self.remember_approved_split(record)
        return self.remembered[SPLIT_KEY]

    def remember_submitted_split(self, land: dict) -> dict:
        """
        Record that the Land asset was split and is waiting for approval. The
        Split List must show a PENDING row for it; its Asset Split No. is kept.
        The Land asset is used up, so it is removed from the APPROVED records.
        """
        serial = land["serial"]
        self.split_list_page.navigate_here()
        self.split_list_page.search_by_serial(serial)
        self.split_list_page.verify_row_status(serial, "PENDING")
        split_no = self.split_list_page.get_split_number(serial)
        self.registrations.forget(land, "APPROVED", AAQ_ASSET_GROUP)
        self.remembered[SPLIT_KEY] = {**land, "split_no": split_no, "split_status": "PENDING"}
        return self.remembered[SPLIT_KEY]

    def remember_approved_split(self, record: dict) -> dict:
        """Record that the split was approved and keep the new Asset Serials it made."""
        new_serials = self.read_new_serials(record)
        self.remembered[SPLIT_KEY] = {**record, "split_status": "APPROVED", "new_serials": new_serials}
        return self.remembered[SPLIT_KEY]

    def read_new_serials(self, record: dict) -> list:
        """
        Return the new Asset Serials made by an approved split. Approval
        creates a new APPROVED registration with one asset serial per split
        line: it is the newest APPROVED registration, and its Asset Serials
        tab lists the serials.
        """
        registration_list = self.registrations.registration_list_page
        approval_list = self.registrations.approval_list_page
        registration_list.navigate_here()
        registration_list.filter_by_status("APPROVED")
        number = registration_list.get_newest_registration_number()
        approval_list.navigate_here()
        approval_list.filter_by_registration_number(number)
        approval_list.open_registration_popup(number)
        approval_list.open_asset_serials_tab()
        serials = approval_list.get_all_generated_asset_serials()
        assert len(serials) == int(SPLIT_INTO), (
            f"Expected {SPLIT_INTO} new Asset Serials on registration {number} (made by the split of "
            f"{record['serial']}) but found {len(serials)}: {serials}"
        )
        assert record["serial"] not in serials, (
            f"Registration {number} lists the split asset {record['serial']} itself, so it is not the split's new registration."
        )
        return serials
