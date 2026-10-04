# Asset Un Assign (Create) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_unassign_page.py` → `AssetUnassignPage` (form screens share `pages/asset_transaction_form_page.py`, grids share `pages/transaction_grid_page.py`); tests in `tests/test_12_asset_unassign.py` |
| Module / menu path | Fixed Asset >> Asset Transaction >> Asset Un Assign |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransaction/showUnAssign` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 |
| Screenshot | `evidence/asset_unassign_initial.png`, `asset_unassign_by_pin.png`, `asset_unassign_pin_search_result.png`, `unassign_filled.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Search By | Radio choice: **Serial** (default, `value=1`) or **Employee Pin** (`value=0`). | `page.locator("#serialWise")`, `page.locator("#employeePinWise")` | "Search By:*" | VERIFIED |
| 2 | Serial search (Serial mode) | Same autocomplete as Asset Assign: type in `#assetSerialId`, click the purple search icon, click the suggestion. Fills the read-only asset and **current assignee** fields (`#assignedEmployeePinNo`, `#assignedEmployeeName`, `#previousAssignStatus` = `ASSIGNED`). | see `asset_assign.md` rows 2-5 | Asset Serial: * | VERIFIED |
| 3 | Employee search (Employee Pin mode) | Autocomplete `#employeeByPinId`; the suggestion reads `<PIN>-<NAME>> <Department>> <Branch>`. Selecting it loads **every asset assigned to that employee** straight into the Asset List grid (3 rows for PIN `00015370`, including two real laptops). Remove unwanted rows with the red trash icon in the Action column before saving. | `page.locator("#employeeByPinId")`, search icon `#employeeByPinId` -> `xpath=following::i[contains(@class,'fa-search')][1]` | employee search box | VERIFIED |
| 4 | Add to Grid / Asset List | Same as Asset Assign (serial mode only). | `#addToGrid`, `#assetDetailsTable` | Add to Grid | VERIFIED |
| 5 | Hand-over person | **Required.** Employee PIN Search (same autocomplete; `#newEmployeePin`, search icon `#myButtonclickforEmployee .btn`) fills `#newEmployeeName2` and `#newEmployeeName`. A name search needs 3+ letters and lists up to 20 matches; a PIN search lists one. | see `asset_assign.md` rows 8-11 | Employee PIN Search:* | VERIFIED |
| 6 | Branch / Project / Date | `#newBranch` (disabled, the user's branch), `#testAbc` (disabled, filled from the asset), `#newAssignDate` (business date, read-only). | ids as listed | Branch Name, Project Name & Number, Assigned Date | VERIFIED |
| 7 | Building / Floor / Room / Note | Optional: `#building` (Head Office, BRAC Gulshan office), `#floor`, `#newLocation`, `#newRemarks`. | ids as listed | Building Name, Floor Number, Room Number, Note/Remarks | VERIFIED |
| 8 | Draft / Submit / Reset | Draft toast `Asset Un-Assign Draft Successfully`; Submit toast `Asset Un-Assign Submit Successfully`. | `#draft`, `#save`, `#resetEditButton` | Draft, Submit, Reset | VERIFIED (Reset not clicked) |

## Notes
- Reach the page by clicking the **Asset Transaction** tab and then the link `Asset Un Assign` (`page.get_by_role("link", name="Asset Un Assign", exact=True)`), after opening the module with `BasePage.open_fixed_asset_module()`. Direct navigation to the hash address is unreliable.
- **Business rule verified:** handing the asset over to the employee who already holds it is refused with the toast `Asset assigned to same employee!` and nothing is saved (the first attempt used PIN `00015370`, the current holder). The hand-over person must be a different employee.
- Full path verified (Serial mode) for test asset `BBDASR00227766`: Draft, Transaction List Details and Edit (values identical), Submit, Approval List Details (values identical), Approve (`Approved successfully`), then the asset's Assign Status is `UNASSIGNED`.
- The hand-over person used in that run was `00295792` (`ABDUL KAYUM TANVIR`), picked from a name search because no ID had been given. The team's chosen hand-over PIN is **`130276`**, which resolves to `00130276` (`Md. Abubokkor Siddik`); use it from now on.
- In the Details/approval popup of an UN ASSIGN, `Organization Branch` shows the **hand-over employee's** branch (here `[BO - HR6328] Aarong Moghbazar Outlet`), while the list row shows `[HO - BDHO] Head Office`, and `Employee Assigned` shows the hand-over person. The `Assigned Before Approval` column of the Assets grid keeps the previous holder (`Sachindra Nath Ghosh[00015370]`).
- Once the Un Assign is Submitted the asset is locked in a pending process (it shows in the Asset In Pending Process List and every Asset Transaction screen answers `No asset found` for it) until the Un Assign is approved.
- Employee Pin mode was explored (suggestion, Asset List loaded) but not run through Draft.
