"""
single_challan_flow.py: carries one Asset Single Challan through its stages, so
every Single Challan test can run alone or after another.

Two challans (two paths) move through the files in order, each with its own new
approved asset (a challan uses its asset up):
    "draft"  : Create + Draft, then Edit and Submit from the list
    "submit" : Create + Submit directly

Stages of a path, in order:
    drafted (draft path only), submitted, serial_added, approved, acknowledged

Example:
    flow = single_challan.reach("submit", "serial_added")
    challan_no = flow["challan_no"]

`reach` does every stage that is not done yet, up to the one asked for, and
remembers it. A test that does a stage itself calls `record` so the stage is
not done twice.
"""
from test_data.asset_shipment_data import build_challan_data
from utils.logger import action_logger

# Stages of each path, in order
STAGES = {
    "draft": ["drafted", "submitted", "serial_added", "approved", "acknowledged"],
    "submit": ["submitted", "serial_added", "approved", "acknowledged"],
}

# Status the challan list must show once a stage is done
STAGE_STATUS = {
    "drafted": "DRAFT",
    "submitted": "PENDING",
    "approved": "APPROVED",
    "acknowledged": "ACKNOWLEDGED",
}


class SingleChallanFlow:
    """Does the missing stages of a Single Challan and remembers what it made."""

    def __init__(self, registrations, out_challan_page, approval_page, in_challan_page, shared: dict):
        """
        `registrations` gives each challan its new approved asset. The three pages
        work in the browser tab of the logged-in user (the same user does everything). `shared` is the dictionary shared
        by the whole test run (fixture `shared_single_challan`).
        """
        self.registrations = registrations
        self.out_challan_page = out_challan_page
        self.approval_page = approval_page
        self.in_challan_page = in_challan_page
        self.shared = shared

    def flow(self, path: str) -> dict:
        """Return the remembered flow of this path ("draft" or "submit"), made empty on first use."""
        return self.shared.setdefault(path, {"done": []})

    def is_done(self, path: str, stage: str) -> bool:
        """Return True when this stage of this path was already done."""
        return stage in self.flow(path)["done"]

    def record(self, path: str, stage: str) -> None:
        """Remember that a test did this stage itself (nothing happens when it is already remembered)."""
        if not self.is_done(path, stage):
            self.flow(path)["done"].append(stage)

    def get_serial(self, path: str) -> str:
        """Return the Asset Serial of the new approved asset this path uses (it is registered and approved now when it does not exist yet)."""
        owner = f"single_challan_{path}"
        return self.registrations.get_approved("furniture", "spot", owner)["serial"]

    def reach(self, path: str, stage: str) -> dict:
        """Do every stage of `path` up to and including `stage` that is not done yet. Returns the flow dictionary."""
        for name in STAGES[path]:
            if not self.is_done(path, name):
                action_logger.info(f"Single challan ({path}): doing stage {name}")
                getattr(self, "do_" + name)(path)
                self.record(path, name)
            if name == stage:
                break
        return self.flow(path)

    # ------------------------------------------------------------------
    # The stages
    # ------------------------------------------------------------------

    def create_challan(self, button: str) -> str:
        """Create a challan with Draft or Submit (`button` is "draft" or "submit") and return its Out Challan Number."""
        page = self.out_challan_page
        page.navigate_here()
        page.click_create()
        page.fill_challan_form(build_challan_data())
        if button == "draft":
            page.draft()
        else:
            page.submit()
        page.search()
        return page.get_newest_out_challan_no()

    def do_drafted(self, path: str) -> None:
        """Create the challan and save it with Draft."""
        challan_no = self.create_challan("draft")
        self.out_challan_page.verify_row_status(challan_no, "DRAFT")
        self.flow(path)["challan_no"] = challan_no

    def do_submitted(self, path: str) -> None:
        """Submit the challan: a Draft is opened with Edit and submitted, otherwise it is created with Submit."""
        page = self.out_challan_page
        if path == "draft":
            challan_no = self.flow(path)["challan_no"]
            page.navigate_here()
            page.filter_by_out_challan_no(challan_no)
            page.open_draft_for_edit(challan_no)
            page.submit()
            page.search()
        else:
            challan_no = self.create_challan("submit")
            self.flow(path)["challan_no"] = challan_no
        page.verify_row_status(challan_no, "PENDING")

    def do_serial_added(self, path: str) -> None:
        """Open the challan from its Out Challan Number and add the serial of the path's new approved asset."""
        page = self.out_challan_page
        challan_no = self.flow(path)["challan_no"]
        serial = self.get_serial(path)
        page.navigate_here()
        page.filter_by_out_challan_no(challan_no)
        page.open_popup(challan_no)
        page.add_serial(serial)
        self.flow(path)["serial"] = serial

    def do_approved(self, path: str) -> None:
        """Approve the challan from the Approval List with a comment."""
        page = self.approval_page
        challan_no = self.flow(path)["challan_no"]
        page.navigate_here()
        page.filter_by_out_challan_no(challan_no)
        page.open_popup(challan_no)
        page.enter_comment("Approved by automation")
        page.approve_and_verify()
        page.filter_by_out_challan_no(challan_no)
        page.verify_row_status(challan_no, "APPROVED")

    def do_acknowledged(self, path: str) -> None:
        """Acknowledge the approved challan on Asset Single In-Challan."""
        page = self.in_challan_page
        challan_no = self.flow(path)["challan_no"]
        page.navigate_here()
        page.filter_by_out_challan_no(challan_no)
        page.open_popup(challan_no)
        page.acknowledge()
        page.close_popup_if_open()
        page.filter_by_out_challan_no(challan_no)
        page.verify_row_status(challan_no, "ACKNOWLEDGED")
