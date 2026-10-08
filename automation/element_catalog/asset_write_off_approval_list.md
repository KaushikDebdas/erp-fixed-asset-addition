# Asset Write-off Approval List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_write_off_approval_list_page.py` → `AssetWriteOffApprovalListPage`; test `tests/test_29_asset_write_off_approval_list.py` |
| Module / menu path | Fixed Asset >> Asset Disposal >> Asset Write-off Approval List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetWriteOff/showWriteOffScheduleList` (reach via menu click) |
| Role needed | a user with the write-off approval permission; the creator can approve their own write-off (explored and tested as user `00015370`, Sachindra Nath Ghosh; `abushoaib.asik` lacked the permission) |
| Last explored | 2026-10-08 |
| Screenshot | `evidence/asset_write_off_approval_list.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Status |
|---|---|---|---|---|
| 1 | Filters | Same as the Write-off List: `#office`, `#registrationFromDate`, `#registrationToDate`, `#createdBy`, `#approvedBy`, `#status`; Search button, `#reset`. | ids as listed | VERIFIED (seen) |
| 2 | Grid | `#assetWriteOffScheduleList`. Columns: checkbox, SL, Details, Write Off ID, Branch Name, Project Name, Department, Disposal Date, Created By, Approved By, Approval Date, Status, Dr/Cr Note. Lists every status; only PENDING rows have a checkbox. | `#assetWriteOffScheduleList` | VERIFIED |
| 3 | Row checkbox / select all | `input#assetWriteOffSchedule` (value 1) per PENDING row; the header has a select-all checkbox. | `row.locator("input[type=checkbox]")` | VERIFIED |
| 4 | Approve | Bottom button, approves the ticked rows. | `#btnApprove` | VERIFIED |
| 5 | Details popup | `#commonModal`: "Asset Write Off Details" with the asset grid (Asset Serial, Item Name, Purchase Price, Written Down Value, Accumulated Depreciation, Addition, Status, Asset Assign Status, Disposal Type), `#comment`, `#commentDate`, and buttons `#btnForApprove`, `#btnForReject`, `#btnForSendBack`, Close. | `#commonModal`, ids as listed | VERIFIED (seen) |

## Notes
- **Approve verified** (write-off 24480, grid checkbox + `#btnApprove`): toast, two lines, `Asset write-off approved successfully.` / `Journal voucher submitted successfully!`; the row then shows Approved By `SACHINDRA NATH GHOSH`, Approval Date and Status `APPROVED`. The Details popup `#btnForApprove` was not run successfully (only tried while blocked).
- **Earlier failure:** with `abushoaib.asik` both Approve buttons (grid and popup) gave the toast `Api error - User not found` and the write-off stayed PENDING; that account has a permission problem. With a user that has the permission, the same click worked, and the same user can create, submit and approve.
- `test_22` runs it all with one login: Draft, submit from the list, approve (1 passed).
- Earlier APPROVED rows were approved by other users (for example write-off 24416 by `MD FOKHRUL ISLAM`).
