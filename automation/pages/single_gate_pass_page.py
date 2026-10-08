"""
SingleGatePassPage: Gate Pass Generation under Fixed Asset > Single Challan.

Lists the approved and acknowledged single challans with a Preview link that
opens the gate pass as a PDF in a new tab. It works like the Asset Transfer
gate pass screen (`GatePassPage`); only the menu and the Out Challan filter are
different. See `automation/element_catalog/asset_single_challan_gate_pass.md`.
"""
from pages.gate_pass_page import MENU_LINK_NAME, GatePassPage


class SingleGatePassPage(GatePassPage):
    """Page object for the Single Challan Gate Pass Generation screen."""

    def __init__(self, page):
        super().__init__(page)
        # Out Challan Number filter (free text)
        self.out_challan_filter = page.locator("#outChallanNumber")

    def navigate_here(self) -> None:
        """Open Gate Pass Generation via the Single Challan menu."""
        self.open_single_challan_submenu(MENU_LINK_NAME)
        self.wait_until_visible(self.search_button, "Search button")
