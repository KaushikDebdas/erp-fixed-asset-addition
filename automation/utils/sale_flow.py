"""
sale_flow.py: carries an Asset Sale through its stages, so every Sale test can run
alone or after another.

An asset can be sold while it is IN_USE, as long as it is UNASSIGNED and not in a
pending process; its status is not changed. Each of the four paths sells its own
asset of the pool (test_data/asset_slots.py) for a Sale Value above or below its
Written Down Value, and a sold asset cannot be sold again:

    path       slot           Sale Value      saved with
    profit_a   sale_profit_a  WDV + 5000      Draft   (then Edit from the list, Submit)
    profit_b   sale_profit_b  WDV + 5000      Submit
    loss_a     sale_loss_a    WDV - 5000      Draft   (then Edit from the list, Submit)
    loss_b     sale_loss_b    WDV - 5000      Submit

Stages of a path, in order:
    saved (the Draft or the Submit), submitted (a Draft path only: Edit from the list and Submit)

Example:
    flow = sale.reach("profit_a", "saved")
    sale_id = flow["sale_id"]

The stage handling (`reach`, `record`) comes from `utils/flow_stages.py`.
"""
from utils.flow_stages import FlowStages

SALE_NOTE = "sale"

# Per path: the pool slot, how much the Sale Value is above (+) or below (-) the Written Down Value, how it is saved
PATHS = {
    "profit_a": {"slot": "sale_profit_a", "change": 5000, "save_as": "draft"},
    "profit_b": {"slot": "sale_profit_b", "change": 5000, "save_as": "submit"},
    "loss_a": {"slot": "sale_loss_a", "change": -5000, "save_as": "draft"},
    "loss_b": {"slot": "sale_loss_b", "change": -5000, "save_as": "submit"},
}


class SaleFlow(FlowStages):
    """Does the missing stages of an Asset Sale and remembers what it made."""

    STAGES = {
        "profit_a": ["saved", "submitted"],
        "profit_b": ["saved"],
        "loss_a": ["saved", "submitted"],
        "loss_b": ["saved"],
    }

    def __init__(self, assets, sale_page, list_page, shared: dict):
        """
        `assets` is the asset pool. The two pages are the Asset Sale form and the Asset Sale List,
        in the browser tab of the logged-in user. `shared` is the dictionary shared by the whole
        test run (fixture `shared_sale`).
        """
        super().__init__(shared)
        self.assets = assets
        self.sale_page = sale_page
        self.list_page = list_page

    def use_up(self, path: str) -> None:
        """Give the asset of this path back to the pool: it is sold and cannot be sold again."""
        self.assets.consume(PATHS[path]["slot"])

    def do_saved(self, path: str) -> None:
        """Sell the asset of this path: fill the sale form, Add to Grid, and save it with Draft or Submit."""
        details = PATHS[path]
        asset = self.assets.get(details["slot"])
        serial = asset["serial"]
        self.sale_page.navigate_here()
        self.sale_page.select_project(asset["data"]["project"])
        self.sale_page.select_asset(serial, serial)
        sale_value = self.sale_page.get_written_down_value() + details["change"]
        self.sale_page.enter_sale_value(sale_value)
        self.sale_page.enter_note(SALE_NOTE)
        self.sale_page.add_to_grid()
        self.sale_page.verify_sale_grid_row(serial, sale_value, details["change"])
        status = "DRAFT"
        if details["save_as"] == "draft":
            self.sale_page.draft_and_verify()
        else:
            self.sale_page.submit_and_verify()
            status = "PENDING"
        self.sale_page.verify_grid_is_empty()
        self.list_page.navigate_here()
        self.list_page.filter_by_status(status)
        flow = self.flow(path)
        flow["serial"] = serial
        flow["sale_value"] = sale_value
        flow["sale_id"] = self.list_page.get_newest_write_off_id()
        flow["status"] = status

    def do_submitted(self, path: str) -> None:
        """Open the Draft sale with Edit from the Asset Sale List and Submit it, so it is PENDING."""
        flow = self.flow(path)
        self.list_page.navigate_here()
        self.list_page.filter_by_status("DRAFT")
        self.list_page.open_write_off_for_edit(flow["sale_id"])
        self.sale_page.submit_and_verify()
        self.sale_page.verify_grid_is_empty()
        self.list_page.navigate_here()
        self.list_page.filter_by_status("PENDING")
        self.list_page.verify_status(flow["sale_id"], "PENDING")
        flow["status"] = "PENDING"
