"""
GenerateBarcodePage: Fixed Asset > Asset Profile > Generate Barcode screen.

Pick assets with the row checkboxes, set a Print Quantity per asset (or one
Default Print Quantity for all), and click Generate, which opens a PDF of
barcode labels in a new browser tab. See
`automation/element_catalog/generate_barcode.md`.
"""
import io
import re

from pypdf import PdfReader

from pages.base_page import BasePage
from utils.logger import action_logger, assertion_logger


# Position of a cell in a result row (0-based; the tick box and a hidden ID column come first)
ASSET_SERIAL_COLUMN_INDEX = 3


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

    def get_row_values(self, serial: str) -> dict:
        """Return the cells of the row for this serial: item, sub category, category, project, assign and utilization status."""
        row = self.results_table.locator("tbody tr", has_text=serial)
        cells = [c.strip() for c in row.first.locator("td").all_inner_texts()]
        start = ASSET_SERIAL_COLUMN_INDEX
        return {
            "serial": cells[start],
            "item_name": cells[start + 1],
            "sub_category": cells[start + 2],
            "category": cells[start + 3],
            "project_in_grid": cells[start + 4],
            "assign_status": cells[start + 9],
            "utilization_status": cells[start + 10],
        }

    def verify_row_shows(self, serial: str, expected: dict) -> None:
        """Confirm the row of this serial shows the values in `expected` (see build_asset_profile). Names every difference."""
        found = self.get_row_values(serial)
        assertion_logger.info(f"Verifying the Generate Barcode row of {serial}")
        problems = []
        for name, value in found.items():
            if value != expected[name]:
                problems.append(f"{name}: expected '{expected[name]}' but found '{value}'")
        assert not problems, f"The row of {serial} is not as expected: {problems}"

    def verify_barcode_pdf(self, report_url: str, expected: dict, quantity: int) -> None:
        """
        Fetch the barcode PDF at `report_url` with the logged-in session and
        confirm it is a PDF for this asset: the request asks for this serial and
        quantity, and the label (serial, item name, branch, project) is printed
        once for every copy. Names every difference.
        """
        response = self.page.context.request.get(report_url)
        text = PdfReader(io.BytesIO(response.body())).pages[0].extract_text()
        assertion_logger.info(f"Verifying the barcode PDF of {expected['serial']}")
        problems = []
        if response.status != 200 or "pdf" not in response.headers.get("content-type", ""):
            problems.append(f"expected a PDF with status 200 but found status {response.status}")
        if expected["serial"] not in report_url or f"%22quantity%22:%22{quantity}%22" not in report_url:
            problems.append(f"the request does not ask for serial {expected['serial']} with quantity {quantity}")
        for label, value in [
            ("serial", expected["serial"]),
            ("item name", expected["item_name"]),
            ("branch", expected["branch"]),
            ("project", expected["project_in_grid"]),
        ]:
            if text.count(value) != quantity:
                problems.append(f"{label} '{value}' is printed {text.count(value)} times, expected {quantity}")
        assert not problems, f"The barcode PDF is not as expected: {problems}. PDF text: {text}"
