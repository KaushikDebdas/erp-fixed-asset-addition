# Asset Assign (Create) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_assign_page.py` → `AssetAssignPage` (form screens share `pages/asset_transaction_form_page.py`, grids share `pages/transaction_grid_page.py`); tests in `tests/test_10_asset_assign.py` and `tests/test_10_asset_assign_new.py` (saved Furniture asset, state set by `utils/transaction_helper.py`) |
| Module / menu path | Fixed Asset >> Asset Transaction >> Asset Assign |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransaction/showAssign` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 (full flow through Draft; Submit was NOT clicked) |
| Screenshot | `evidence/asset_assign_initial.png`, `evidence/asset_assign_serial_suggestion.png`, `evidence/asset_assign_serial_searched.png`, `evidence/asset_assign_added_to_grid.png`, `evidence/asset_assign_pin_suggestion.png`, `evidence/asset_assign_pin_searched.png`, `evidence/asset_assign_after_draft.png`, `evidence/asset_transaction_menu.png` |

## Asset Transaction menu (live)
Click the **Asset Transaction** tab, then one of six links: `Asset Assign` (`#!faAssetTransaction/showAssign`), `Asset Un Assign` (`showUnAssign`), `Asset Internal Movement` (`showInternalTransfer`), `Transaction List` (`editList`), `Transaction Approval List` (`showList`), `Asset Assign Acknowledgement` (`showAcknowledgementList`). The last one is not described in the manual.

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Select Project / Select Department (search) | Optional filters that narrow the asset search | `#searchProject`, `#searchDepartment` | "Select Project:", "Select Department:" | VERIFIED (not used) |
| 2 | Asset Serial | **Required.** Autocomplete box (placeholder `Search Asset Serial`). Typing a serial and clicking the search button shows ONE suggestion `<serial>-<Item>><Sub Category>><Category>><Group>`; the screen only fills in after that suggestion is clicked. After the click the box holds the whole suggestion text, not just the serial. | `page.locator("#assetSerialId")` | "Asset Serial: *" | VERIFIED |
| 3 | Serial search button | Small purple icon button right of the box; it is not a normal `<button>` (an `<i class="fa fa-search">` inside `div.btn.btn-xs.purple`). | `page.locator("#assetSerialId").locator("xpath=following::i[contains(@class,'fa-search')][1]")` | magnifier icon | VERIFIED |
| 4 | Serial suggestion | The row to click after searching | `page.locator("ul.ui-autocomplete li:visible", has_text="<serial>")` | suggestion list under the box | VERIFIED |
| 5 | Asset details (read-only, auto-filled) | Filled by selecting the suggestion. Item name, sub category, category, group, branch, project, department, assigned employee PIN and name, assigned date, assigned status, building, floor, room, previous remarks. | `#assetName`, `#subCategoryName`, `#categoryName`, `#groupName`, `#officeName`, `#projectName`, `#departmentName`, `#assignedEmployeePinNo`, `#assignedEmployeeName`, `#assignedDate`, `#previousAssignStatus`, `#buildingName`, `#floorName`, `#roomName`, `#previousRemarks` | "Asset Item Name:*" etc. | VERIFIED |
| 6 | Add to Grid | Moves the searched asset into the Asset List grid and clears the top section. Several assets can be added before Draft/Submit. | `page.locator("#addToGrid")` (onclick `rowAddAssetDetails()`) | "Add to Grid" | VERIFIED |
| 7 | Asset List grid | Holds the added assets. Columns: SL, Asset Serial, Asset Item Name, Branch Name, Project Name, Department Name, Building Name, Floor Number, Room Number, Assigned Employee PIN, Assigned Employee, Assign Status, Utilization Status, Action. | `page.locator("#assetDetailsTable")` | "Asset List" | VERIFIED |
| 8 | Employee PIN Search | **Required.** Autocomplete box (placeholder `Employee Pin No or Name (Min 3 char...)`). Same pattern as the serial box: type, click the search button, click the suggestion `<PIN>-<Employee name>`. | `page.locator("#newEmployeePin")` (hidden id field `#newAssignedPersonId` gets the employee's internal id) | "Employee PIN Search:*" | VERIFIED |
| 9 | Employee search button | Purple icon button right of the box | `page.locator("#myButtonclickforEmployee .btn")` | magnifier icon | VERIFIED |
| 10 | Employee suggestion | The row to click after searching | `page.locator("ul.ui-autocomplete li:visible", has_text="<PIN>")` | suggestion list | VERIFIED |
| 11 | Employee PIN / Employee Name | Read-only, filled by selecting the employee | `#newEmployeeName2` (PIN), `#newEmployeeName` | "Employee PIN: *", "Employee Name: *" | VERIFIED |
| 12 | Branch Name | Always the logged-in user's branch; disabled. Read it to know which branch the user is in (here `Head Office [ BDHO ]`). | `page.locator("#newBranch")` (read the selected option text) | "Branch Name: *" | VERIFIED |
| 13 | Project Name & Number / Department | Disabled; the project is filled from the asset after the employee is selected (here `[015] Microfinance (Dabi)`), the department stays unselected. | `#testAbc`, `#departmentNameNumber` | "Project Name & Number:*", "Department:" | VERIFIED |
| 14 | Assigned Date | Read-only, the business date (here `20-09-2026`). | `#newAssignDate` | "Assigned Date:" | VERIFIED |
| 15 | Building / Floor / Room | Optional location drop-downs; Floor and Room fill after Building. Building options seen: Head Office, BRAC Gulshan office. | `#building`, `#floor`, `#newLocation` | "Building Name:", "Floor Number:", "Room Number:" | VERIFIED (not used) |
| 16 | Branch Location | Free text, optional | `#newBranchLocation` | "Branch Location:" | VERIFIED (not used) |
| 17 | Note/Remarks | Free text for the new assignment | `page.locator("#newRemarks")` | "Note/Remarks:" | VERIFIED |
| 18 | Draft button | Saves the assignment without submitting. Shows the toast `Asset Assign Draft Successfully`, sends `createAssign`, then clears the form and the grid. | `page.locator("#draft")` (onclick `saveAssetTransaction(this.value)`) | "Draft" | VERIFIED |
| 19 | Submit button | Submits for approval | `page.locator("#save")` | "Submit" | VERIFIED locator; not clicked |
| 20 | Reset button | Clears the form | `page.locator("#resetEditButton")` | "Reset" | VERIFIED locator; not clicked |

## Notes
- Reach the page by clicking the **Asset Transaction** tab and then the link `Asset Assign` (`page.get_by_role("link", name="Asset Assign", exact=True)`), after opening the module with `BasePage.open_fixed_asset_module()`. Direct navigation to the hash address is unreliable, as on every other screen.
- Verified end-to-end with the test asset `BBDASR00227766` (Cabinet Table, project `Microfinance (Dabi)`, UNASSIGNED, IN_USE): after selecting its suggestion the screen showed Asset Item Name `Cabinet Table`, Sub Category `Wooden Furniture`, Category `Furniture`, Group `Furniture and Fixture`, Branch `[HO - BDHO] Head Office`, Project `Microfinance (Dabi)`, Assigned Status `UNASSIGNED`. These match the asset, and the box text starts with the serial that was typed, which is the check that the entered serial is the one that came back.
- Employee `00015370` is `Sachindra Nath Ghosh`.
- The search buttons occasionally do not open the suggestion list on the first click; the page object clicks again (up to three times) before failing.
- Only the suggestion click fills the screen: typing the serial or PIN and pressing the search button alone leaves every read-only field empty.
- **Data created by this exploration:** one DRAFT Asset Assign transaction for asset `BBDASR00227766`, assigned to employee `00015370`, note `AUTOMATION_TEST assign note`. It was not submitted. A Draft can be edited or deleted from Transaction List (not opened yet).
