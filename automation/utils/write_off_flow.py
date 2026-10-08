"""
write_off_flow.py: carries an Asset Write-off through its stages, so every
Write-off test can run alone or after another.

A write-off only accepts an asset whose Utilization Status is not IN_USE. Each
path takes its asset from the pool (test_data/asset_slots.py), sets it to DAMAGE and
writes it off. The two usage assets that Assign, Movement, Unassign and Expense used
are reused here when they are free; a test run alone registers a new asset.

Two paths, each with its own asset (a written-off asset cannot be used again):
    "draft"  : Draft, then Edit and Submit from the Write-off List, then Approve   (slot write_off_a)
    "submit" : Submit straight from the form                                      (slot write_off_b)

Stages of a path, in order:
    draft path:  drafted, submitted, approved
    submit path: submitted

Example:
    flow = write_off.reach("draft", "submitted")
    write_off_id = flow["write_off_id"]

The stage handling (`reach`, `record`) comes from `utils/flow_stages.py`.
"""
from test_data.asset_registration_data import PROFILE_NAMES_BY_ITEM
from utils.flow_stages import FlowStages

# The notes typed on the Global List popup and on the write-off form
STATUS_NOTE = "AUTOMATION_TEST damaged for write off"
WRITE_OFF_NOTE = "write off"

# The Asset Item Name the write-off grid shows for the Furniture asset
ITEM_NAME = PROFILE_NAMES_BY_ITEM["furniture"][0]

# The pool slot (test_data/asset_slots.py) each path takes its asset from
SLOT_BY_PATH = {"draft": "write_off_a", "submit": "write_off_b"}


class WriteOffFlow(FlowStages):
    """Does the missing stages of an Asset Write-off and remembers what it made."""

    STAGES = {
        "draft": ["drafted", "submitted", "approved"],
        "submit": ["submitted"],
    }

    def __init__(self, assets, global_list_page, write_off_page, list_page, approval_page, shared: dict):
        """
        `assets` is the asset pool. The other four are the page objects of the Global List,
        the Asset Write-off form, the Write-off List and the Write-off Approval List; they work in
        the browser tab of the logged-in user. `shared` is the dictionary shared by the whole test run
        (fixture `shared_write_off`).
        """
        super().__init__(shared)
        self.assets = assets
        self.global_list_page = global_list_page
        self.write_off_page = write_off_page
        self.list_page = list_page
        self.approval_page = approval_page

    def use_up(self, path: str) -> None:
        """Give the asset of this path back to the pool: it is written off and cannot be used again."""
        self.assets.consume(SLOT_BY_PATH[path])

    def fill_write_off_form(self, path: str) -> dict:
        """
        Take the asset of this path, set it to DAMAGE, and fill the Asset Write-off form up to
        Add to Grid (the grid is checked). Returns the asset record.
        """
        asset = self.assets.get(SLOT_BY_PATH[path])
        serial = asset["serial"]
        self.global_list_page.mark_asset_damaged(serial, STATUS_NOTE)
        self.write_off_page.navigate_here()
        self.write_off_page.select_project(asset["data"]["project"])
        self.write_off_page.select_asset(serial, serial)
        self.write_off_page.enter_note(WRITE_OFF_NOTE)
        self.write_off_page.add_to_grid()
        self.write_off_page.verify_grid_row(serial, ITEM_NAME, "DAMAGE", WRITE_OFF_NOTE)
        return asset

    def newest_id_with_status(self, status: str) -> str:
        """Open the Write-off List, filter by this Status and return the Write Off ID of the newest row."""
        self.list_page.navigate_here()
        self.list_page.filter_by_status(status)
        return self.list_page.get_newest_write_off_id()

    # ------------------------------------------------------------------
    # The stages
    # ------------------------------------------------------------------

    def do_drafted(self, path: str) -> None:
        """Write off the asset and save it with Draft."""
        asset = self.fill_write_off_form(path)
        self.write_off_page.draft_and_verify()
        self.write_off_page.verify_grid_is_empty()
        self.flow(path)["serial"] = asset["serial"]
        self.flow(path)["write_off_id"] = self.newest_id_with_status("DRAFT")

    def do_submitted(self, path: str) -> None:
        """Submit the write-off: a Draft is opened with Edit and submitted, otherwise it is submitted straight from the form."""
        flow = self.flow(path)
        if path == "draft":
            self.list_page.navigate_here()
            self.list_page.filter_by_status("DRAFT")
            self.list_page.open_write_off_for_edit(flow["write_off_id"])
            self.write_off_page.submit_and_verify()
            self.write_off_page.verify_grid_is_empty()
        else:
            asset = self.fill_write_off_form(path)
            self.write_off_page.submit_and_verify()
            self.write_off_page.verify_grid_is_empty()
            flow["serial"] = asset["serial"]
            flow["write_off_id"] = self.newest_id_with_status("PENDING")
            self.use_up(path)
        self.list_page.navigate_here()
        self.list_page.filter_by_status("PENDING")
        self.list_page.verify_status(flow["write_off_id"], "PENDING")

    def do_approved(self, path: str) -> None:
        """Approve the write-off from the Approval List and use the asset up."""
        write_off_id = self.flow(path)["write_off_id"]
        self.approval_page.navigate_here()
        self.approval_page.filter_by_status("PENDING")
        self.approval_page.select_write_off(write_off_id)
        self.approval_page.approve_selected_and_verify()
        self.approval_page.filter_by_status("APPROVED")
        self.approval_page.verify_status(write_off_id, "APPROVED")
        self.use_up(path)
