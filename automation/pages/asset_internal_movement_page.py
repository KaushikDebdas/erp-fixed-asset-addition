"""
AssetInternalMovementPage: Asset Internal Movement (Fixed Asset > Asset Transaction > Asset Internal Movement): move an assigned asset to a new building and floor.

All the fields and actions come from `AssetTransactionFormPage`.
"""
from pages.asset_transaction_form_page import AssetTransactionFormPage


class AssetInternalMovementPage(AssetTransactionFormPage):
    """Page object for the Asset Internal Movement screen."""

    MENU_LINK = "Asset Internal Movement"
