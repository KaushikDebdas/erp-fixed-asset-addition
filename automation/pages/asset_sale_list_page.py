"""
AssetSaleListPage: Asset Sale List (Fixed Asset > Asset Disposal > Asset Sale
List). Works like the Asset Write-off List; a DRAFT sale has an Edit link that
opens the Asset Sale form. See `automation/element_catalog/asset_sale_list.md`.
"""
from pages.asset_write_off_list_page import AssetWriteOffListPage


class AssetSaleListPage(AssetWriteOffListPage):
    """Page object for the Asset Sale List screen."""

    MENU_LINK = "Asset Sale List"
    GRID_ID = "#assetDisposalSaleScheduleList"
    STATUS_COLUMN_INDEX = 16
