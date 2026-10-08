# Asset Sale Approval List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_sale_approval_list_page.py` → `AssetSaleApprovalListPage` (inherits `AssetWriteOffApprovalListPage`); test `tests/test_31_asset_sale_approval_list.py` |
| Module / menu path | Fixed Asset >> Asset Disposal >> Asset Sale Approval List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetDisposalSale/showDisposalSaleScheduleList` |
| Role needed | a user with the disposal approval permission (tested with `00015370`, who created and approved) |
| Last explored | 2026-10-08 |
| Screenshot | `evidence/asset_sale_approval_list.png` |

## Elements
| # | Element | Locator (Playwright) | Status |
|---|---|---|---|
| 1 | Filters and Search | `#office`, `#registrationFromDate`, `#registrationToDate`, `#createdBy`, `#status`, `#approvedBy`, Search button, `#reset` | VERIFIED |
| 2 | Grid | `#assetDisposalSaleScheduleList`; columns: checkbox, SL, Disposal Sale ID, Details, Branch Name, Project Name, Department, bank columns, Disposal Date, Created By, Approved By, Approval Date, Receive Type, Status (cell 16). Only PENDING rows have a checkbox. | VERIFIED |
| 3 | Select all | Checkbox in the grid heading: `#assetDisposalSaleScheduleList thead input[type=checkbox]` | VERIFIED |
| 4 | Approve | `#btnApprove` | VERIFIED |

## Notes
- Select all (2 pending sales) + Approve gave the toast, two lines: `Asset disposal sale approved successfully.` / `Journal and Credit voucher submitted successfully!`; the rows then showed Approved By and Status `APPROVED`.
- Select all approves **every** PENDING sale shown (on a shared staging, also other people's); the test ticks all as the request says.
