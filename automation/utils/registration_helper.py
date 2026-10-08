"""
registration_helper.py: gives a test a registration of a chosen asset item in
a chosen status, so one test can reuse what another test created.

How it works:
    A test that creates a registration records it here. A later test asks for
    one with get_draft / get_pending / get_approved. If an earlier test already
    made it, that one is returned. If not (for example the test is run on its
    own), a new one is created right then. So every test can run alone, and a
    full run does not create the same thing twice.

Example:
    record = registrations.get_pending_of("split_land")
    number = record["registration_number"]

The registrations are remembered for the run only (utils/run_registrations.py). The owner
of a record is the asset slot name (test_data/asset_slots.py), and the `*_of(slot)`
methods look an asset up by that name: get_pending_of("sale_profit_a").

A record is a dictionary:
    {"data": <the values entered>, "registration_number": "757877"}
An approved record also has "serial", the Asset Serial Number.
"""
from test_data.asset_registration_data import build_asset_data
from test_data.asset_slots import ASSET_SLOTS
from utils.asset_flow import approve_registration, create_approved_asset


class RegistrationHelper:
    """Finds, creates and remembers registrations for the tests."""

    def __init__(self, aaq_page, registration_list_page, approval_list_page, remembered: dict):
        """
        The three page objects are used to create a registration when none is
        remembered. `remembered` is the dictionary shared by the whole test run.
        """
        self.aaq_page = aaq_page
        self.registration_list_page = registration_list_page
        self.approval_list_page = approval_list_page
        self.remembered = remembered

    def make_key(self, item: str, status: str, sub_type: str, owner: str) -> tuple:
        """
        Return the key a registration is remembered under.
        `owner` is empty for a registration anyone may reuse; give a name (for
        example "bulk") for one that only one test should use.
        """
        return (item, sub_type, status, owner)

    def is_still_valid(self, key: tuple, status: str) -> bool:
        """
        Return True if the remembered registration can be used. A record created
        during this run is up to date. One loaded from the saved file is checked
        once: its Registration Number is searched in the list and its real
        Status must be the remembered one. A record that is out of date is removed.
        """
        if key not in self.remembered:
            return False
        if key in self.remembered.trusted:
            return True
        number = self.remembered[key]["registration_number"]
        self.registration_list_page.navigate_here()
        self.registration_list_page.filter_by_registration_number(number)
        statuses = self.registration_list_page.read_column("Status")
        if statuses == [status]:
            self.remembered.trusted.add(key)
            return True
        self.remembered.pop(key, None)
        return False

    def get_draft(self, item: str, sub_type: str = "spot", owner: str = "") -> dict:
        """Return a DRAFT registration of the item, creating one if none is remembered."""
        key = self.make_key(item, "DRAFT", sub_type, owner)
        if not self.is_still_valid(key, "DRAFT"):
            data = build_asset_data(item, sub_type=sub_type)
            self.aaq_page.navigate_here()
            self.aaq_page.create_draft(data)
            self.remember_draft(data, owner)
        return self.remembered[key]

    def get_pending(self, item: str, sub_type: str = "spot", owner: str = "") -> dict:
        """Return a submitted (PENDING) registration of the item, creating one if none is remembered."""
        key = self.make_key(item, "PENDING", sub_type, owner)
        if not self.is_still_valid(key, "PENDING"):
            data = build_asset_data(item, sub_type=sub_type)
            self.aaq_page.navigate_here()
            self.aaq_page.create_and_submit(data)
            self.remember_pending(data, owner)
        return self.remembered[key]

    def get_approved(self, item: str, sub_type: str = "spot", owner: str = "") -> dict:
        """
        Return an APPROVED registration (with its Asset Serial). When none is remembered, a
        PENDING registration of the same owner is approved now; when there is none either,
        a new asset is registered, submitted and approved.
        """
        key = self.make_key(item, "APPROVED", sub_type, owner)
        if not self.is_still_valid(key, "APPROVED"):
            pending_key = self.make_key(item, "PENDING", sub_type, owner)
            if self.is_still_valid(pending_key, "PENDING"):
                record = self.remembered[pending_key]
                serial = approve_registration(self.approval_list_page, record["registration_number"])
                self.move_to_approved(record, serial, owner)
            else:
                data = build_asset_data(item, sub_type=sub_type)
                created = create_approved_asset(
                    self.aaq_page, self.registration_list_page, self.approval_list_page, data
                )
                self.remembered[key] = {
                    "data": data,
                    "registration_number": created["registration_number"],
                    "serial": created["serial"],
                }
        return self.remembered[key]

    def get_draft_of(self, slot: str) -> dict:
        """Return the DRAFT registration of an asset slot (test_data/asset_slots.py), creating it if none is remembered."""
        return self.get_draft(ASSET_SLOTS[slot]["item"], ASSET_SLOTS[slot]["sub_type"], slot)

    def get_pending_of(self, slot: str) -> dict:
        """Return the PENDING registration of an asset slot, creating it if none is remembered."""
        return self.get_pending(ASSET_SLOTS[slot]["item"], ASSET_SLOTS[slot]["sub_type"], slot)

    def get_approved_of(self, slot: str) -> dict:
        """Return the APPROVED registration of an asset slot, approving or creating it if none is remembered."""
        return self.get_approved(ASSET_SLOTS[slot]["item"], ASSET_SLOTS[slot]["sub_type"], slot)

    def remember_draft(self, data: dict, owner: str = "") -> dict:
        """Record the Draft that was just saved. Its number is the newest DRAFT in the list."""
        return self.remember_from_list(data, "DRAFT", owner)

    def remember_pending(self, data: dict, owner: str = "") -> dict:
        """Record the registration that was just submitted. Its number is the newest PENDING in the list."""
        return self.remember_from_list(data, "PENDING", owner)

    def remember_from_list(self, data: dict, status: str, owner: str) -> dict:
        """Read the newest registration number with this status from the list and record it."""
        self.registration_list_page.navigate_here()
        self.registration_list_page.filter_by_status(status)
        number = self.registration_list_page.get_newest_registration_number()
        key = self.make_key(data["item"], status, data["sub_type"], owner)
        self.remembered[key] = {"data": data, "registration_number": number}
        return self.remembered[key]

    def forget(self, record: dict, status: str, owner: str = "") -> None:
        """Remove a record from its old status, for example after a test approved it."""
        key = self.make_key(record["data"]["item"], status, record["data"]["sub_type"], owner)
        self.remembered.pop(key, None)

    def move_to_approved(self, record: dict, serial: str, owner: str = "") -> None:
        """Record that a PENDING registration was approved, and keep its Asset Serial."""
        self.forget(record, "PENDING", owner)
        key = self.make_key(record["data"]["item"], "APPROVED", record["data"]["sub_type"], owner)
        self.remembered[key] = {**record, "serial": serial}

    def move_draft_to_pending(self, record: dict, owner: str = "") -> None:
        """Record that a DRAFT registration was submitted, so it is now PENDING."""
        self.forget(record, "DRAFT", owner)
        key = self.make_key(record["data"]["item"], "PENDING", record["data"]["sub_type"], owner)
        self.remembered.setdefault(key, record)
