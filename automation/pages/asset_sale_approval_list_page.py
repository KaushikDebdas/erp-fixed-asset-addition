"""
AssetSaleApprovalListPage: Asset Sale Approval List (Fixed Asset > Asset
Disposal > Asset Sale Approval List). Works like the Asset Write-off Approval
List: tick PENDING sales (or all of them) and click Approve. See
`automation/element_catalog/asset_sale_approval_list.md`.
"""
from pages.asset_write_off_approval_list_page import AssetWriteOffApprovalListPage
from test_data.toast_messages import SALE_APPROVE_TOAST


class AssetSaleApprovalListPage(AssetWriteOffApprovalListPage):
    """Page object for the Asset Sale Approval List screen."""

    MENU_LINK = "Asset Sale Approval List"
    GRID_ID = "#assetDisposalSaleScheduleList"
    STATUS_COLUMN_INDEX = 16
    APPROVE_TOAST = SALE_APPROVE_TOAST
