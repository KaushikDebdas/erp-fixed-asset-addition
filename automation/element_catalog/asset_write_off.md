# Asset Write-off (Create) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_write_off_page.py` → `AssetWriteOffPage` (the DAMAGE step uses `AssetSerialGlobalListPage.find_unassigned_in_use_asset` and `mark_asset_damaged`); tests in `tests/test_27_asset_write_off.py` |
| Module / menu path | Fixed Asset >> Asset Disposal >> Asset Write-off (the link is spelled with a hyphen) |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetWriteOff/show` (reach via menu click) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-08 |
| Screenshot | `evidence/asset_write_off_initial.png`, `evidence/asset_write_off_grid_added.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Branch | Select, pre-filled with the user's branch. | `#office` | Head Office [ BDHO ] | VERIFIED (not changed) |
| 2 | Project | Choose the project; the Asset Serial box then lists only that project's assets. | `page.locator("#project")`, `select_option(label="[015] Microfinance (Dabi)")` | -Select Project- | VERIFIED |
| 3 | Department | Disabled select. | `#department` | -Select Department- | VERIFIED (not used) |
| 4 | Asset Serial | Search drop-down: click `#s2id_asset .select2-choice`, type 3+ letters of the **item name** (for example `cabinet`), click the result `<SERIAL>-> <Item>-> <Sub Category>-> <Category>-> <Group>`. Shows "Please enter 3 or more characters" below 3 letters and "No matches found" when no asset of the project has a status other than IN_USE. | `#s2id_asset .select2-choice`, `.select2-drop-active input.select2-input`, `.select2-drop-active .select2-results li` | Asset Serial | VERIFIED |
| 5 | Auto-filled fields | Read-only after a pick: `#assetName`, `#assetSubCategory`, `#assetCategory`, `#assetGroup`, `#unitPrice` (25000), `#addition` (0), `#depreciatedValue` (0), `#writtenDownValue` (25000). | ids as listed | Asset Item Name, Sub Category, ... | VERIFIED |
| 6 | Utilization Status | Disabled select, filled with the asset's status (`DAMAGE`); it is the write-off reason. | `#disposalType` | -Utilization Status- | VERIFIED |
| 7 | Note | Text area, "Maximum 200 characters". | `#remarks` | Note | VERIFIED |
| 8 | Add to Grid / grid | Adds the asset to the grid. Columns: SL, Profile ID, Asset Serial, Asset Item Name, Asset Project Id, Project Name, Unit Price(TK.), Addition, Accumulated Depreciation, Written Down Value, Utilization Status, Note/Remarks, Action. No toast is shown. | `#addToGrid`, `#assetDetailsTable` | Add to Grid | VERIFIED |
| 9 | Draft / Submit / Reset | Draft toast `Asset write-off drafted successfully`; Submit toast `Asset write-off submitted successfully`. After either the grid shows "No data available in table" and the project is cleared. | `#draft`, `#save`, `#resetEditButton` | Draft, Submit, Reset | VERIFIED (Reset not clicked) |

## Preparing the asset (Asset Serial Global List)
- The asset must be UNASSIGNED. Open its serial in the Asset Serial Global List, click `#statusChange` (Change next to Asset Utilization Status), choose `DAMAGE` in `#updateStatus`, type a note in `#updateNote`, click `#updateAssetBtn`. Toast: `Asset profile status updated successfully.`
- The Utilization Status filter offers SPLIT, IN_USE, DAMAGE, STOLEN, BURNED, DONATED, OFFLINE_TRANSFER, UNDER_REPAIR.

## Notes
- Before any asset is set to DAMAGE (or another status) the Asset Serial box finds nothing, even for `BBD` or `generator`.
- No Generator asset was on staging (item search for "generator" found none), so Cabinet Table `BBDASR00228056` (Submit) and Laptop `BBDASR00228048` (Draft) were explored by hand; the tests pick the newest UNASSIGNED / IN_USE asset of `[015] Microfinance (Dabi)` themselves.
- The Write-off List (`Asset Disposal >> Asset Write-off List`, grid `#assetWriteOffScheduleList`) has filters Branch (`#office`), From/To date, Created By, Status (`#status`), Approved By and columns SL, Write Off ID, Details, Edit, Branch Name, Project ID, Project Name, Department ID, Department, Disposal Date, Created By, Approved By, Approval Date, Status, Dr/Cr Note. Seen only; not automated yet.
- At 1280 x 720 the top menu works (Asset Disposal opens its list of links on a click).
