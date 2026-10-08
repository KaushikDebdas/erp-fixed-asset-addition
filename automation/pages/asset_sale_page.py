"""
AssetSalePage: Asset Sale (Fixed Asset > Asset Disposal > Asset Sale).

The form is the Asset Write-off form (`AssetWriteOffPage`) plus a Sale Value
box. The grid also shows the Profit/Loss: Sale Value minus Written Down Value.
See `automation/element_catalog/asset_sale.md`.
"""
from pages.asset_write_off_page import AssetWriteOffPage
from test_data.toast_messages import SALE_DRAFT_TOAST, SALE_SUBMIT_TOAST
from utils.logger import assertion_logger


class AssetSalePage(AssetWriteOffPage):
    """Page object for the Asset Sale screen."""

    MENU_LINK = "Asset Sale"
    DRAFT_TOAST = SALE_DRAFT_TOAST
    SUBMIT_TOAST = SALE_SUBMIT_TOAST

    def __init__(self, page):
        super().__init__(page)
        # Price the asset is sold for (required)
        self.sale_value_field = page.locator("#saleValue")

    def enter_sale_value(self, sale_value: float) -> None:
        """Type the Sale Value."""
        self.type_text(self.sale_value_field, str(int(sale_value)), "Sale Value field")

    def verify_sale_grid_row(self, serial: str, sale_value: float, profit_loss: float) -> None:
        """Confirm the grid row of this serial shows the Sale Value and the Profit/Loss (for example 5000.00 or -5000.00)."""
        assertion_logger.info(f"Verifying the sale grid row of {serial}")
        cells = self.get_grid_row_values(serial)
        expected = {"sale value": str(int(sale_value)), "profit/loss": f"{profit_loss:.2f}"}
        problems = []
        for name, value in expected.items():
            if value not in cells:
                problems.append(f"{name} '{value}' is not in the row {cells}")
        assert not problems, f"The sale grid row of {serial} is not as expected: {problems}"
