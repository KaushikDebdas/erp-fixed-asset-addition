# Asset Expense (list and Create form) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_expense_page.py` → `AssetExpensePage`; tests in `tests/test_16_asset_expense.py`; shared steps in `utils/expense_flow.py`, data in `test_data/asset_expense_data.py` |
| Module / menu path | Fixed Asset >> Asset Expenditure >> Asset Expense |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetExpense/show` (reach via menu click) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-04 (full flows run for both expense sources: Draft then Submit for Inventory, direct Submit for Accounts) |
| Screenshot | `evidence/asset_expenditure_menu.png`, `asset_expense_initial.png`, `asset_expense_create_form.png`, `asset_expense_inventory_ready.png`, `asset_expense_inventory_after_draft.png`, `asset_expense_draft_opened.png`, `asset_expense_accounts_ready.png` |

## Asset Expenditure menu (live)
Click the **Asset Expenditure** tab, then one of six links: `Asset Expense` (`#!faAssetExpense/show`), `Asset Expense Approval` (`showAssetExpenseApproval`), `Asset Addition From Inventory` (`faAssetAdditionFromInventory/show`), `Asset Addition From Inventory Approval` (`showApprovalList`), `Asset Addition From Vendor` (`faAssetAdditionFromVendor/show`), `Asset Addition From Vendor Approval` (`showAssetAdditionApproval`).

## Elements: the list (what the screen opens with)

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Status filter | Select: `PENDING`, `APPROVED`, `REJECTED`, `DRAFT`, `SENDBACK`. | `select#status` | "Status:" | VERIFIED |
| 2 | Entry From / To Date | Read-only inputs filled through the calendar icons. | `#fromDate`, `#toDate` (the page also holds hidden twins `#entryFromDate`, `#entryToDate`) | "Entry From Date:", "Entry To Date:" | VERIFIED |
| 3 | Search / Reset | Runs / clears the filter. | `get_by_role("button", name="Search")` (onclick `searchAssetExpense()`), `#resetUpdate` | Search, Reset | VERIFIED |
| 4 | Create | Opens the **Expense Detail** form on the same page. It is a link (`<a>`), not a button; other hidden elements share its click handler. | `page.locator("[onclick='resetAssetExpenseForm()']", has_text="Create").locator("visible=true").first` | Create | VERIFIED |
| 5 | Results grid | Columns: SL, Expense ID, Entry Date, Expense Amount, Expense Ref., Status, Created By, Approved By, Approve Date, Note/Remarks. Empty on 2026-10-04 (`No data available in table`). | `page.locator("#editExpenseTable")` | "List of Asset Expense" | VERIFIED |

## Elements: the Create form ("Expense Detail")

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 6 | Asset Serial | **Required.** Autocomplete (placeholder `Search Asset Serial`), expected to work like the Asset Transaction serial box (type, search icon, pick the suggestion). Fills the read-only asset fields. | `#assetSerialId` | "Asset Serial: *" | VERIFIED locator; behaviour not run |
| 7 | Asset details (read-only) | `#assetName`, `#category`, `#subCategory`, `#group`, `#currentBranch` (Branch Name & Number), `#currentProjectName` (Project Name & Number). | ids as listed | "Asset Item Name:", "Asset Category:", ... | VERIFIED locators |
| 8 | Expense Amount (this asset) | Optional amount for the selected asset, used when assets have different amounts. | `#expenseAmountIndividual` | "Expense Amount:" | VERIFIED locator |
| 9 | Add / Reset (asset block) | Adds the asset to the grid below / clears the block. | `#btn-add` (onclick `rowAddAssetDetails()`), `#btn-reset` | Add, Reset | VERIFIED locators |
| 10 | Asset grid | Columns: SL, Asset Serial, Asset Item Name, Asset Sub Category, Asset Category, Asset Group, Branch Name, Project Name, Expense Amount, Action. | `#assetDetailsTable` | asset list | VERIFIED |
| 11 | Date of Entry | **Required**, read-only, the business date (`20/09/2026` on staging). | `#dateOfEntry` | "Date of Entry: *" | VERIFIED |
| 12 | Expense Source | **Required.** Options `Inventory`, `Accounts` (placeholder `Select expense source...`). The manual: Inventory credits Other Inventory; Accounts credits Supplier Payable-Opex and needs a supplier. | `select#expenseSource` | "Expense Source: *" | VERIFIED |
| 13 | Supplier | Supplier select / name box next to the Expense Source (for the Accounts source). | `select#supplierDefault`, `#partyVendorName` | supplier controls | VERIFIED locators; behaviour not run |
| 14 | Category / Sub Category / Item Name | **Required**, dependent selects: category (Agro Ingredients & Accessories, Chemical, Construction Materials, ... Furniture), then sub-category, then item. | `select#expenseCategory`, `select#expenseSubCategory`, `select#itemName` | "Select Category: *", "Select Sub Category: *", "Item Name: *" | VERIFIED locators |
| 15 | Debit A/C, Credit A/C, Debit A/C Sub Code | **Required** selects; options load after the choices above. | `select#debitAccount`, `select#creditAccount`, `select#debitSubAccount` | "Debit A/C: *", "Credit A/C: *", "Debit A/C Sub Code: *" | VERIFIED locators |
| 16 | Total Expense Amount | **Required.** With **Distribute** the total is split evenly across the assets in the grid. | `#expenseAmount`, `#btn-distribute` (onclick `distributeExpenseAmount()`) | "Total Expense Amount: *", Distribute | VERIFIED locators |
| 17 | Expense Ref. | **Required** free text. | `#expenseRef` | "Expense Ref.: *" | VERIFIED locator |
| 18 | Remarks/Note | Optional. | `#remarks` | "Remarks/Note:" | VERIFIED locator |
| 19 | Draft / Submit / Reset / Close | Save as Draft / Submit for approval / clear / leave. Draft and Submit set a hidden `#submitType` to `DRAFT` / `SUBMITTED`. | `#draftExpense`, `#createExpense`, `#reset`, `Close` button | Draft, Submit, Reset, Close | VERIFIED locators; not clicked |

## Notes (verified flow)
- **The Create form is a popup** titled `Create Asset Expense` (the page behind it is the list). The **asset serial box has no search button**: typing the serial opens the single suggestion `<serial>-<Item>><Sub Category>><Category>><Group>`; clicking it fills the read-only asset fields (Item Name, Category, Sub Category, Group, Branch `[HO - BDHO] Head Office`, Project). Date of Entry is the business date (`20/09/2026`).
- **Order matters:** type the amount in `#expenseAmountIndividual` and click **Add** first. Add puts the asset in the grid (the amount appears in an input in the grid row) and fills **Total Expense Amount** (`#expenseAmount`, read-only; 5000). Only **after** the asset is in the grid does choosing **Expense Source** load the Credit A/C (`getCreditAccountHead`); choosing the source first leaves Credit A/C empty.
- **Expense Source = Inventory:** Category, Sub Category and Item Name are enabled and required. For the asset used (Cabinet Table) the matching choices are `Furniture`, `Wooden Furniture`, `Cabinet Table`. Credit A/C is filled in automatically as `Other Inventory [1107010401-02]`.
- **Expense Source = Accounts:** Category, Sub Category and Item Name are **disabled** (not needed). Credit A/C is filled in automatically as `Supplier Payable-Opex[2101010301-05]`.
- **Debit A/C** (both sources, required): 84 expense accounts; the documented one is `Other Maintenance Expenses[5108010101-07]`. Debit A/C Sub Code stays hidden for it.
- **Vendor/Supplier/Lessor Name is required for BOTH sources** (the select2 `-Select Party-` link, same widget as on the registration form: click it, type `ACE IT`, click the option `ACE IT[P008937]`). Without it Draft shows the toast `Vendor/Supplier/Lessor Name is required.` and saves nothing.
- **Expense Ref.** is required free text; the tests use `EXP` plus six random digits. Remarks/Note is optional.
- **Draft:** `#draftExpense`. Toast **`Asset expense successfully drafted.`**, the popup closes, and the list shows a new row with status DRAFT. **An Expense ID is generated at this point** (format `BBDEXP00000001`; e.g. `BBDEXP00000001` for ref `EXP428774`). Find the row by the Expense Ref (random per run) and read the ID from the 3rd cell (the cell holds the link `javascript:setDataField('<n>')`).
- **Opening a draft:** click the Expense ID link in the list. The same popup opens with every saved value (asset grid, source, category, sub-category, item, debit and credit accounts, total, ref, remarks, vendor) and Add, Draft, Submit, Reset and Close buttons. **Submit** (`#createExpense`) there shows **`Asset expense successfully submitted.`** (request `faAssetExpense/update`) and the row becomes PENDING.
- **Submit without a draft** (verified with the Accounts source): `#createExpense` straight from the filled form shows the same toast `Asset expense successfully submitted.` (request `faAssetExpense/create`); the new row is PENDING and has its Expense ID (e.g. `BBDEXP00000002`).
- Expense IDs run `BBDEXP00000001`, `BBDEXP00000002`, ... and are the key to store and match on later (the approval list is matched by this ID).
- Test data used: asset `BBDASR00227778` (Cabinet Table, project `[015] Microfinance (Dabi)`), amount 5000, notes `AUTOMATION_TEST expense Inventory` / `AUTOMATION_TEST expense Accounts`.
- **Timing quirks found by the automated tests:** (1) The Create popup's serial search can miss the first typing if the serial is entered the moment the popup opens; the page object types it again (up to three times) until the suggestion shows. (2) After a Draft is reopened, the Sub Category, Item Name and account drop-downs fill in a moment after the rest of the popup, so wait until their `selectedIndex` is above 0 before reading them (`wait_for_saved_selections`).
- **An expense that is still Draft or Pending seems to lock its asset:** after a test left an expense unfinished, the Expense form's serial search no longer offered that asset. Finish (Submit and Approve) an expense before creating another one for the same asset. The automated flows use one asset and complete each expense before starting the next.
- **Automation:** `tests/test_16_asset_expense.py` has 11 tests: the list columns and status values, the asset search, Add and the total, the Inventory fields, the Accounts fields, the required vendor for both sources, and four full flows (Inventory and Accounts, each saved as Draft then Submit and as a direct Submit) that store the Expense ID, approve with the same user, and check the voucher in Voucher Search. All pass (2026-10-04).
