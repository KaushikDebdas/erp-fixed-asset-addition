# Asset Write-off List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_write_off_list_page.py` → `AssetWriteOffListPage` (Edit opens the form in `AssetWriteOffPage`); test `tests/test_28_asset_write_off_list.py`, step reused from `utils/write_off_flow.py` |
| Module / menu path | Fixed Asset >> Asset Disposal >> Asset Write-off List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetWriteOff/showEditWriteOffScheduleList` (reach via menu click) |
| Role needed | ERP External User (tested with `abushoaib.asik`) |
| Last explored | 2026-10-08 |
| Screenshot | `evidence/asset_write_off_list_edit.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Status |
|---|---|---|---|---|
| 1 | Filters | Branch `#office`, From/To date `#registrationFromDate`/`#registrationToDate`, Created By `#createdBy`, Approved By `#approvedBy`, Status `#status` (PENDING, APPROVED, REJECTED, DRAFT, SENDBACK). | ids as listed | VERIFIED (Status only used) |
| 2 | Search / Reset | Runs the filter. | `get_by_role("button", name="Search")`, `#reset` | VERIFIED |
| 3 | Grid | Newest write-off first. Columns: SL, Write Off ID (cell 1), Details, Edit, Branch Name, Project ID, Project Name, Department ID, Department, Disposal Date, Created By, Approved By, Approval Date, Status (cell 13), Dr/Cr Note. | `#assetWriteOffScheduleList` | VERIFIED |
| 4 | Edit | Only on DRAFT rows. Opens the Asset Write-off form with the asset already in the grid (project and Utilization Status filled). | `row.get_by_role("link", name="Edit", exact=True)` | VERIFIED |

## Notes
- Submitting the edited draft shows the toast `Asset write-off submitted successfully`; the screen stays on the form with an empty grid, and the row is PENDING in the list.
- Disposal Date shows the ERP business date (20/09/2026 on staging), not today's date.
