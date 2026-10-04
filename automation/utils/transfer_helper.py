"""
transfer_helper.py: carries one Asset Shipment through its stages, so one test
can reuse what an earlier test created.

The stages, in order:
    shipment             a saved Shipment (PENDING)
    draft_challan        a Draft Transfer Challan inside it
    serial_added         the asset's serial added to the challan
    challan_submitted    the challan submitted (PENDING)
    challan_approved     the challan approved in the Challan Approval List
    shipment_approved    the shipment approved (Gate Pass generated)
    acknowledged         the challan acknowledged on Asset Shipment-In Challan

How it works:
    A test that does a stage records it with mark_done. A test that needs an
    earlier stage calls reach("<stage>"): every stage that is not done yet is
    done now, in order. So the whole file runs in order, and any single test
    also runs alone.

Example:
    flow = transfer.reach("draft_challan")
    challan_no = flow["challan_no"]

The flow is a dictionary: shipment_no, shipment_data, challan_no, serial,
in_challan_no, plus "done" (the stages finished so far).
"""
from test_data.asset_shipment_data import build_challan_data, build_shipment_data

# The stages in the order they happen
STAGES = [
    "shipment",
    "draft_challan",
    "serial_added",
    "challan_submitted",
    "challan_approved",
    "shipment_approved",
    "acknowledged",
]


class TransferHelper:
    """Does and remembers the stages of one Asset Shipment for the tests."""

    def __init__(self, registrations, shipment_page, challan_page,
                 challan_approval_page, in_challan_page, remembered: dict):
        """
        `registrations` gives the approved asset whose serial is transferred.
        The page objects all work on the second user's browser tab.
        `remembered` is the dictionary shared by the whole test run.
        """
        self.registrations = registrations
        self.shipment_page = shipment_page
        self.challan_page = challan_page
        self.challan_approval_page = challan_approval_page
        self.in_challan_page = in_challan_page
        self.remembered = remembered

    def flow(self) -> dict:
        """Return the remembered flow dictionary, creating an empty one the first time."""
        if "flow" not in self.remembered:
            self.remembered["flow"] = {"done": []}
        return self.remembered["flow"]

    def is_done(self, stage: str) -> bool:
        """Return True when the stage has been done in this run."""
        return stage in self.flow()["done"]

    def mark_done(self, stage: str) -> None:
        """Record that a stage has been done."""
        if stage not in self.flow()["done"]:
            self.flow()["done"].append(stage)

    def record(self, stage: str, shipment_data: dict = None, shipment_no: str = "",
               challan_no: str = "", serial: str = "") -> None:
        """
        Record that a test did `stage`, with the values it produced. Does nothing
        when the stage is already done, so a test can never overwrite a later stage.
        """
        if self.is_done(stage):
            return
        flow = self.flow()
        if shipment_data is not None:
            flow["shipment_data"] = shipment_data
        if shipment_no != "":
            flow["shipment_no"] = shipment_no
        if challan_no != "":
            flow["challan_no"] = challan_no
        if serial != "":
            flow["serial"] = serial
        self.mark_done(stage)

    def reach(self, stage: str) -> dict:
        """
        Do every stage up to and including `stage` that is not done yet, and
        return the flow dictionary.
        """
        for name in STAGES:
            if not self.is_done(name):
                self.do_stage(name)
            if name == stage:
                break
        return self.flow()

    def do_stage(self, stage: str) -> None:
        """Do one stage now, with page actions, and record it."""
        if stage == "shipment":
            self.create_shipment()
        elif stage == "draft_challan":
            self.create_draft_challan()
        elif stage == "serial_added":
            self.add_serial()
        elif stage == "challan_submitted":
            self.submit_challan()
        elif stage == "challan_approved":
            self.approve_challan()
        elif stage == "shipment_approved":
            self.approve_shipment()
        elif stage == "acknowledged":
            self.acknowledge()
        self.mark_done(stage)

    # ------------------------------------------------------------------
    # Shared steps
    # ------------------------------------------------------------------

    def open_challan_tab(self) -> None:
        """Open the saved shipment's Details popup and switch to its Transfer Challans tab."""
        self.shipment_page.navigate_here()
        self.shipment_page.filter_by_shipment_no(self.flow()["shipment_no"])
        self.shipment_page.open_details(self.flow()["shipment_no"])
        self.challan_page.open_transfer_challans_tab()

    def fill_challan_form(self, challan_data: dict) -> None:
        """Fill the open Create Challan popup (projects, branch, note, the asset item and its quantity) and add the line."""
        self.challan_page.choose_from_project(challan_data["from_project"])
        self.challan_page.choose_receiving_branch(challan_data["receiving_branch"])
        self.challan_page.choose_to_project(challan_data["to_project"])
        self.challan_page.enter_note(challan_data["note"])
        self.challan_page.choose_asset_item(challan_data["item_search"], challan_data["item_name"])
        self.challan_page.enter_quantity(challan_data["quantity"])
        self.challan_page.add_item_line()

    # ------------------------------------------------------------------
    # The stages
    # ------------------------------------------------------------------

    def create_shipment(self) -> None:
        """Create and save a shipment, and remember its Shipment No."""
        data = build_shipment_data()
        self.shipment_page.navigate_here()
        self.shipment_page.open_create_popup()
        self.shipment_page.fill_shipment_form(data)
        toast = self.shipment_page.save_shipment_and_get_toast()
        self.shipment_page.verify_toast(toast, ["Asset Shipment Initiated Successfuly"])
        self.shipment_page.search()
        self.flow()["shipment_data"] = data
        self.flow()["shipment_no"] = self.shipment_page.get_newest_shipment_no()

    def create_draft_challan(self) -> None:
        """Create a Draft challan inside the shipment, and remember its Out Challan No."""
        self.open_challan_tab()
        self.challan_page.click_create_challan()
        self.fill_challan_form(build_challan_data())
        toast = self.challan_page.draft_and_get_toast()
        self.challan_page.verify_toast(toast, ["Challan drafted successfully"])
        self.flow()["challan_no"] = self.challan_page.get_newest_challan_no()

    def create_extra_draft_challan(self) -> str:
        """Create a second Draft challan in the shipment and return its Out Challan No (a test deletes it)."""
        self.open_challan_tab()
        numbers_before = self.challan_page.read_challan_numbers()
        self.challan_page.click_create_challan()
        self.fill_challan_form(build_challan_data())
        toast = self.challan_page.draft_and_get_toast()
        self.challan_page.verify_toast(toast, ["Challan drafted successfully"])
        return self.challan_page.find_new_challan_no(numbers_before)

    def add_serial(self) -> None:
        """Add the serial of a freshly approved asset to the challan, and remember the serial."""
        asset = self.registrations.get_approved("furniture", owner="transfer")
        self.open_challan_tab()
        self.challan_page.open_challan_details(self.flow()["challan_no"])
        self.challan_page.click_add_serial_link()
        self.challan_page.choose_serial(asset["serial"])
        self.challan_page.add_serial_to_popup_grid()
        toast = self.challan_page.save_serial_and_get_toast()
        self.challan_page.verify_toast(toast, ["Asset serial added Successfuly"])
        self.flow()["serial"] = asset["serial"]

    def submit_challan(self) -> None:
        """Submit the Draft challan from its Update Challan popup."""
        self.open_challan_tab()
        self.challan_page.open_update_challan(self.flow()["challan_no"])
        toast = self.challan_page.submit_update_challan_and_get_toast()
        self.challan_page.verify_toast(toast, ["Challan submitted successfully"])

    def approve_challan(self) -> None:
        """Approve the challan in the Asset Shipment Challan Approval List."""
        challan_no = self.flow()["challan_no"]
        self.challan_approval_page.navigate_here()
        self.challan_approval_page.filter_by_out_challan_no(challan_no)
        self.challan_approval_page.open_popup(challan_no)
        self.challan_approval_page.enter_comment("AUTOMATION_TEST approve challan")
        toast = self.challan_approval_page.approve_and_get_toast()
        self.challan_approval_page.verify_toast(toast, "Challan approved successfully.")

    def approve_shipment(self) -> None:
        """Approve the shipment from its Details popup, and remember the In Challan No."""
        shipment_no = self.flow()["shipment_no"]
        self.shipment_page.navigate_here()
        self.shipment_page.filter_by_shipment_no(shipment_no)
        self.shipment_page.open_details(shipment_no)
        toast = self.shipment_page.approve_shipment_and_get_toast()
        self.shipment_page.verify_toast(
            toast, ["Shipment approved successfully", "Gate pass generated successfully"]
        )
        self.in_challan_page.navigate_here()
        self.in_challan_page.filter_by_out_challan_no(self.flow()["challan_no"])
        row = self.in_challan_page.read_row(self.flow()["challan_no"])
        self.flow()["in_challan_no"] = row["In Challan No"]

    def acknowledge(self) -> None:
        """Acknowledge the challan on Asset Shipment-In Challan and check it is ACKNOWLEDGED."""
        challan_no = self.flow()["challan_no"]
        self.in_challan_page.navigate_here()
        self.in_challan_page.filter_by_out_challan_no(challan_no)
        self.in_challan_page.open_popup(challan_no)
        self.in_challan_page.acknowledge()
        self.in_challan_page.close_popup_if_open()
        self.in_challan_page.filter_by_out_challan_no(challan_no)
        self.in_challan_page.verify_row_status(challan_no, "ACKNOWLEDGED")
