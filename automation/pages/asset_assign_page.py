"""
AssetAssignPage: Asset Assign (Fixed Asset > Asset Transaction > Asset Assign): give an unassigned asset to an employee.

All the fields and actions come from `AssetTransactionFormPage`.
"""
from pages.asset_transaction_form_page import AssetTransactionFormPage


class AssetAssignPage(AssetTransactionFormPage):
    """Page object for the Asset Assign screen."""

    MENU_LINK = "Asset Assign"
