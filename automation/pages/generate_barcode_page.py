"""
GenerateBarcodePage: Fixed Asset > Asset Profile > Generate Barcode screen.

Pick assets with the row checkboxes, set a Print Quantity per asset (or one
Default Print Quantity for all), and click Generate, which opens a PDF of
barcode labels in a new browser tab. See
`automation/element_catalog/generate_barcode.md`.
"""
import re

from pages.base_page import BasePage
from utils.logger import action_logger


class GenerateBarcodePage(BasePage):
    """Page object for the Generate Barcode screen."""

    def __init__(self, page):
        super().__init__(page)
        # Filter and buttons
        self.asset_serial_filter = page.locator("#assetSerial")
        self.search_button = page.get_by_role("button", name="Search")
        # Results grid (same id as the Global List grid, on a different page)
        self.results_table = page.locator("#assetSerialGlobalList")
        # One quantity for every ticked row, applied by the Set button
        self.default_print_quantity_field = page.locator("#defaultPrintValue")
        self.set_button = page.locator("button[name=setDefaultQuantity]")
        self.generate_button = page.locator("#generateBarcode")

    def navigate_here(self) -> None:
        """Open the Generate Barcode screen via the Asset Profile menu."""
        self.open_asset_profile_submenu("Generate Barcode")
        self.wait_until_visible(self.search_button, "Search button")

    def search_by_serial(self, serial: str) -> None:
        """Filter by Asset Serial and wait for the result (or the empty message)."""
        self.type_text(self.asset_serial_filter, serial, "Asset Serial filter")
        self.click(self.search_button, "Search button")
        self.wait_for_grid_refresh()
        self.wait_for_row_or_no_data(self.results_table, serial)

    def is_serial_listed(self, serial: str) -> bool:
        """Return True if a result row for this Asset Serial is shown."""
        return self.results_table.locator("tbody tr", has_text=serial).count() > 0

    def get_grid_headers(self) -> list:
        """Return the visible column headings of the results grid."""
        headers = self.results_table.locator("thead th:visible").all_inner_texts()
        return [h.strip() for h in headers if h.strip()]

    def tick_row(self, serial: str) -> None:
        """Tick the checkbox of the row for this Asset Serial."""
        row = self.results_table.locator("tbody tr", has_text=serial)
        self.click(row.locator("input[type=checkbox]"), f"Row checkbox for {serial}")

    def set_default_quantity(self, quantity: int) -> None:
        """Type the Default Print Quantity and click Set."""
        self.type_text(self.default_print_quantity_field, str(quantity), "Default Print Quantity field")
        self.click(self.set_button, "Set button")

    def get_row_print_quantity(self, serial: str) -> str:
        """Return the Print Quantity shown in the row for this Asset Serial."""
        row = self.results_table.locator("tbody tr", has_text=serial)
        return row.locator("input[name=defaultPrint]").input_value()

    def generate_and_get_report_url(self) -> str:
        """
        Click Generate. The barcode PDF opens in a new browser tab; return
        that tab's address and close the tab. The PDF viewer is not a normal
        page, so only the address can be checked.
        """
        with self.page.context.expect_page() as new_tab_info:
            self.click(self.generate_button, "Generate button")
        report_tab = new_tab_info.value
        report_tab.wait_for_url(re.compile("generateAssetBarcodeReport"), timeout=20000)
        report_url = report_tab.url
        action_logger.info(f"Barcode report opened: {report_url.split('?')[0]}")
        report_tab.close()
        return report_url
