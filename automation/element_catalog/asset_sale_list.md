# Asset Sale List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_sale_list_page.py` → `AssetSaleListPage` (inherits `AssetWriteOffListPage`); used by `tests/test_30_asset_sale.py` and `test_31_asset_sale_approval_list.py` |
| Module / menu path | Fixed Asset >> Asset Disposal >> Asset Sale List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetDisposalSale/showEditDisposalSaleScheduleList` |
| Last explored | 2026-10-08 |

## Elements
Same filters as the Asset Write-off List (`#office`, dates, `#createdBy`, `#status`, `#approvedBy`, Search, `#reset`). Grid `#assetDisposalSaleScheduleList`, columns: SL, Disposal Sale ID (cell 1), Details, Edit, Branch Name, Project Name, Department, Bank Name, Bank Branch Name, Bank Account No, Cheque No, Disposal Date, Created By, Approved By, Approval Date, Receive Type, Status (cell 16). Edit only on DRAFT rows. Status: VERIFIED. Opening a Draft with Edit and submitting it was not run for sales.
