"""
AssetUnassignPage: Asset Un Assign (Fixed Asset > Asset Transaction > Asset Un Assign): take an assigned asset back and record who it is handed over to.

All the fields and actions come from `AssetTransactionFormPage`.
"""
from pages.asset_transaction_form_page import AssetTransactionFormPage


class AssetUnassignPage(AssetTransactionFormPage):
    """Page object for the Asset Un Assign screen."""

    MENU_LINK = "Asset Un Assign"
