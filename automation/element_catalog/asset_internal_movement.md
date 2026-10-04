# Asset Internal Movement (Create) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_internal_movement_page.py` → `AssetInternalMovementPage` (form screens share `pages/asset_transaction_form_page.py`, grids share `pages/transaction_grid_page.py`); tests in `tests/test_11_asset_internal_movement.py` |
| Module / menu path | Fixed Asset >> Asset Transaction >> Asset Internal Movement |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransaction/showInternalTransfer` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 |
| Screenshot | `evidence/asset_internal_movement_initial.png`, `asset_internal_movement_by_pin.png`, `asset_internal_movement_pin_search_result.png`, `internal_movement_draft_empty.png`, `internal_movement_filled.png`, `internal_movement_after_draft.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Search By | Radio choice **Serial** (default) or **Employee Pin**, exactly as on Un Assign. | `#serialWise`, `#employeePinWise` | "Search By:*" | VERIFIED |
| 2 | Serial / Employee Pin search | Same autocompletes and behaviour as Un Assign: serial fills the asset and current assignee (`#previousAssignStatus` must be `ASSIGNED`); Employee Pin mode loads all of that employee's assets into the grid. | see `asset_unassign.md` | Asset Serial: * / employee search | VERIFIED |
| 3 | Internal Movement To: Employee | **Required** (inline message `This field is required` if empty). Same autocomplete (`#newEmployeePin`, `#myButtonclickforEmployee .btn`); fills `#newEmployeeName2`, `#newEmployeeName`. | see `asset_assign.md` | Employee PIN Search:* | VERIFIED |
| 4 | Branch / Project / Date | `#newBranch` (disabled, the user's branch), `#testAbc` (disabled, from the asset), `#newAssignDate` (read-only business date). | ids as listed | Branch Name, Project Name & Number, Assigned Date | VERIFIED |
| 5 | Building / Floor / Room | Where the asset moves. `#building` options: Head Office, BRAC Gulshan office. Floors for Head Office: 12th floor, 7th floor, 6th floor, 17th floor, 8th Floor. The 12th floor has no rooms (`#newLocation` stays at `-Select Room-`). `#newBranchLocation` is a select (`-Select Branch-`). | `#building`, `#floor`, `#newLocation`, `#newBranchLocation` | Building Name, Floor Number, Room Number, Branch Location | VERIFIED |
| 6 | Note/Remarks | Optional. | `#newRemarks` | Note/Remarks: | VERIFIED |
| 7 | Draft / Submit / Reset | Draft toast `Asset Internal-Movement Draft Successfully`; Submit toast `Asset Internal-Movement Submit Successfully`. Draft with the employee empty shows only the inline required message and no toast. | `#draft`, `#save`, `#resetEditButton` | Draft, Submit, Reset | VERIFIED (Reset not clicked) |

## Notes
- Reach the page by clicking the **Asset Transaction** tab and then the link `Asset Internal Movement` (`page.get_by_role("link", name="Asset Internal Movement", exact=True)`), after opening the module with `BasePage.open_fixed_asset_module()`. Direct navigation to the hash address is unreliable.
- Section headings seen on the screen: `Asset List` and **`Internal Movement To`**.
- An asset with a transaction still pending (for example a submitted Un Assign) is not offered here at all: the serial search shows the toast `No asset found`. Do the movement before any Un Assign.
- The asset must already be `ASSIGNED` (the screen shows the current assignee after selecting it).
- Full path verified (Serial mode) for test asset `BBDASR00227766`: Draft, Transaction List (type `TRANSFER`) Details and Edit (values identical), Submit, Approval List Details (values identical), Approve (`Approved successfully`). In Asset Profile the asset then shows Building `Head Office` and Floor `12th floor`, still `ASSIGNED` to `00015370`.
- In the Edit view the floor drop-down comes back at `-Select Floor-` although the saved floor is `12th floor` in the Details popup; the building is kept. Re-pick the floor before submitting if it matters.
- Employee Pin mode was explored (suggestion, Asset List loaded) but not run through Draft.
