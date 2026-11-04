# Asset Serial Global List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_serial_global_list_page.py` → `AssetSerialGlobalListPage`; tests in `tests/test_04_asset_serial_global_list.py` (AAQ assets) and `tests/test_32_asset_serial_global_list_hofin_assets.py` (HOFIN assets, CR FAHOV2-643 F01) |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset Serial Global List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showAssetSerialGlobalList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 (read-only: nothing was saved, split, approved or rejected) |
| Screenshot | `evidence/asset_serial_global_list.png`, `evidence/asset_serial_global_list_detail.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Organization Branch | Select2; only 'Head Office [ BDHO ]' for this user. | `page.locator("#office")` | "Organization Branch:" | VERIFIED |
| 2 | Asset Serial | Free text; partial match. Fastest way to find one asset. | `page.locator('input[name="assetSerial"]')` (the popup also has an `#assetSerial`) | "Asset Serial:" | VERIFIED |
| 3 | Asset Item Name | Free text. | `page.locator("#assetName")` | "Asset Item Name:" | VERIFIED |
| 4 | Registration Type | Options: MRR, AAQ, LEASE, BOOKING. | `page.locator("#assetRegistrationType")` | "Registration Type:" | VERIFIED |
| 5 | MRR Number | Free text. | `page.locator("#referenceNo")` | "MRR Number:" | VERIFIED |
| 6 | Asset Group | 31 options. | `page.locator("#faAssetGroup")` | "Asset Group:" | VERIFIED |
| 7 | Asset Category | 48 options. | `page.locator("#faAssetCategory")` | "Asset Category:" | VERIFIED |
| 8 | Asset Sub Category | 84 options. | `page.locator("#faAssetSubCategory")` | "Asset Sub Category:" | VERIFIED |
| 9 | Registration Date From / To | Date range; read-only inputs filled through the calendar icon. | `#registrationDateFrom`, `#registrationDateTo` | dd/mm/yyyy | VERIFIED |
| 10 | Asset Utilization Status | 9 options incl. SPLIT, IN_USE, DAMAGE, STOLEN, BURNED, DONATED, OFFLINE_TRANSFER. | `page.locator("#status")` | "Asset Utilization Status:" | VERIFIED |
| 11 | Project | 1467 options. | `page.locator("#project")` | "Project:" | VERIFIED |
| 12 | Department | Disabled until a Project is chosen. | `page.locator("#department")` | "Department:" | VERIFIED |
| 13 | Source Of Fund | 290 options. | `page.locator("#sourceOfFund")` | "Source Of Fund:" | VERIFIED |
| 14 | Employee PIN / Employee Name | Free text. | `#employeePin`, `#employeeName` | Employee PIN: / Employee Name: | VERIFIED |
| 15 | AAQ Type | Spot Purchase, Gift Item. | `page.locator("#assetAAQType")` | "AAQ Type:" | VERIFIED |
| 16 | Assign Status | ASSIGNED, UNASSIGNED. | `page.locator("#assetAssignStatus")` | "Assign Status:" | VERIFIED |
| 17 | Building / Floor / Room | Location filters; Floor and Room fill after Building. | `#building`, `#floor`, `#room` | Building Name: / Floor Number: / Room Number: | VERIFIED |
| 18 | Warranty Ends Within | Read-only date input with calendar icon. | `#warrantyEndDate` | Warranty Ends Within: | VERIFIED |
| 19 | Asset Disposal Type | WRITE_OFF, SALE, AUCTION, SPLIT. | `page.locator("#disposalType")` | "Asset Disposal Type:" | VERIFIED |
| 20 | Search button | Runs the filter. | `page.get_by_role("button", name="Search")` (onclick `showAssetSerialSearch()`) | Search | VERIFIED |
| 21 | Reset button | Clears filters. | `page.locator("#resetUpdate")` | Reset | VERIFIED |
| 22 | Records per page | 10 / 20 / 30 / 50 / 100. | `page.locator("select[name=assetSerialGlobalList_length]")` | Records per page | VERIFIED |
| 23 | Results grid | Lists assets. Columns: Profile ID (hidden), SL, Asset Serial, Asset Item Name, Sub Category, Category Name, Group Name, Project Name, Department, Assign Status, Utilization Status. Shows 10 rows even before a search. | `page.locator("#assetSerialGlobalList")` | List of Global Asset Serial | VERIFIED |
| 24 | Asset Serial link (row) | Opens the **Asset Profile Details** popup (see below). | `page.get_by_role("link", name="<asset serial>")` | Blue serial in the Asset Serial column | VERIFIED |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset Serial Global List` (`page.get_by_role("link", name="Asset Serial Global List", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- Verified with `BBDASR00227761` (the serial produced by the Asset Registration e2e flow): searching it returns exactly one row, `Cabinet Table / Wooden Furniture / Furniture / Furniture and Fixture`, Assign Status UNASSIGNED, Utilization Status IN_USE.
- The asset's Project here, `[015] Microfinance (Dabi)`, is the project chosen on the AAQ form for that run (the test data uses Dabi), so the two screens agree.

## Popup: "Asset Profile Details" (click an Asset Serial link)
- Container: the open Bootstrap modal (`.modal.in`); title `Asset Profile Details`. Buttons: `Update` (`#updateProfileDetails`), `Close`.
- Seven tabs (`a[data-toggle=tab]`): `Details` (`#tab_details`), `Depreciation History` (`#tab_dep_history`), `Revaluation History` (`#tab_rev_history`), `Transaction History` (`#tab_transfer_history`), `Expenditure` (`#tab_expenditure`), `Disposal Info` (`#tab_disposal_info`), `Attachment` (`#tab_attachment`).
- **Details tab, read-only fields** (all `input`, ids as listed): `#assetSerial`, `#refAssetSerial` (Reference Asset), `#assetName`, `#subCategory`, `#category`, `#group`, `#branchName`, `#branchCode`, `#projectName`, `#projectCode`, `#department`, `#sourceOfFundName`, `#utilizationStatusName`, `#assignUnassignStatus`, `#revaluationApplicability` (Excluded From Depreciation), `#disposalType1`, `#disposalDate`, `#employeePin`, `#assignedEmployee`, `#assignedDate`, `#roomNo`, `#floorNo`, `#buildingName`, `#newBranch`, `#unitPrice`, `#totalAdditionRegistered`, `#totalExpenseRegistered`, `#netAssetValue` (WDV), `#totalDepCalculated`, `#currentDepreciation`, `#remainingLife`, `#lastDepDt`, `#lastDepdate`, `#depreciationModel`, `#referenceNo` (labelled Depreciation Method), `#depreciationFrequency`, `#depAccountCode`, `#depAccCode`, `#associatedAccountCode`, `#measurementUnit`, `#measurement`, `#itemSpecification`, `#itemImeiSlNo`, `#assetLife`, `#assetTaxLife`, `#salvageValue`, `#depreciationRate`, `#registrationDate`, `#purchaseDate`, `#registrationNumber`, `#regType`, `#aaqType`, `#requisitionNumber`, `#mrrNumber`, `#mrrDate`, `#challanNumber`, `#challanReceivedDate`, `#orderNumber`, `#orderDate`, `#warrantyEndDate`, `#leaseIdentificationNo`, `#leaseRepaymentType`, `#leaseRepaymentAmount`, `#leaseInterestsRate`, `#leaseEndDate`, `#supplierName`, `#supplierNumber`, `#supplierContactNumber`, `#supplierAddress`.
- **Editable controls** (Details tab): `Change` buttons `#sourceOfFundChange`, `#statusChange` (Asset Utilization Status), `#enableMeasurement` (Measurement), `#itemChange` (Item); file input `#attachedFile` with `Reset Image` (`#deleteImage`); `Note` textarea `#remarks`; `Update` saves. The manual lists only Utilization Status, Attach File and Note, but it is out of date: the live screen with its four Change buttons is the accurate one.
- **What each Change button opens** (explored read-only: popups closed with Close, Update never clicked, no write request sent). Source Of Fund, Utilization Status and Item each open the same small stacked popup (`#changeStatus`, title `Update`) on top of the profile popup, so the profile popup cannot be clicked until it is closed:
  - `#sourceOfFundChange`: select `#newSourceOfFund` (`-Select Source of Fund-` + 290), Update `#updateAssetSourceOfFund` (`updateAssetSourceOfFundFunc()`).
  - `#statusChange`: select `#updateStatus` (Select Status, SPLIT, IN_USE, DAMAGE, STOLEN, BURNED, DONATED, OFFLINE_TRANSFER, UNDER_REPAIR; current value preselected), mandatory textarea `#updateNote`, Update `#updateAssetBtn` (`updateAssetProfileStatus()`).
  - `#itemChange`: text input `#newItemSpecification` (New Item Specification/IMEI/SL No., mandatory), Update `#updateItemSpecification` (`updateItemSpecificationFunc()`).
  - Each popup also has Reset (`#cancel`, `resetStatus()`) and Close (`resetStatus()`).
  - `#enableMeasurement` opens no popup: it hides itself, makes `#measurement` editable (value `0.00` for the new asset) and shows a separate Update button `#setMeasurement`. The Measurement unit (`#measurementUnit`) follows the item: Land shows `Decimal` (Land asset `BBDASR00227457`: measurement blank), Desktop Computer and Cabinet Table show `Pcs`.
  - Business rules (confirmed by the team, Update buttons not clicked): Source Of Fund Update only saves after an option is selected; the Utilization Status Note is mandatory so the reason for a change is recorded; Item Change replaces the specification/IMEI/serial text; Measurement can be set to make an asset splittable or changed if one already exists.
  - Full value lists for the Source Of Fund (289) and Utilization Status (8) drop-downs: `asset_profile_reference_values.md`.
  - **Missing-value checks verified** on the test Land asset `BBDASR00227763` (nothing saved, no request sent): `#updateAssetSourceOfFund` with no option gives toast `Please select a Source Of Fund.`; `#updateAssetBtn` with an empty `#updateNote` gives `Please add a note.`; `#updateItemSpecification` with an empty `#newItemSpecification` gives `Please select a Item Specification/IMEI/SL No.` (wording as on screen). The popups stay open after these messages. Evidence: `evidence/profile_sof_update_empty.png`, `profile_status_update_empty_note.png`, `profile_item_update_empty.png`.
  - **Measurement carried from registration:** the test Land asset registered with Measurement 12.5 shows `#measurement` = `12.50`, `#measurementUnit` = `Decimal` here. Evidence: `evidence/asset_profile_land_with_measurement.png`.
  - Caution: `#assetName` and `#measurement` exist twice on this page (filter box and popup). Scope popup locators with `#commonModal`, e.g. `page.locator("#commonModal #measurement")`.
  - Close a Change popup with its Close button, then the profile popup with its own Close.
- **Grids on the other tabs** (all empty for the new asset, "No data available in table"):
  - Depreciation History: SL, Asset Serial, Asset Item Name, Category, Purchase Price, Depreciation Amount, WDV, Period.
  - Revaluation History: SL, Asset Serial, Asset Purchase Price(TK), Revaluation Date, Revaluation Amount(TK), Type Of Net Carrying, Difference LRA and CRA(TK).
  - Transaction History: SL, Asset Serial, Transaction Type, Transaction Date, New Assign Status, New Assigned Person, Building, Floor, Room, New Project, New Utilization Status, Transaction Status, Approved By, Approval Date, Created By, Remarks.
  - Expenditure (grid `#assetExpenditureList` in `#tab_expenditure`; read on staging 2026-10-15 after two approved Asset Expenses, VERIFIED): SL, Asset Serial, Inventory Asset Item Name, Inventory Asset Sub Category, Inventory Asset Category, Expenditure Type, Expense/Addition Amount, Reference Number, Supplier Name, Status, Source/Group, Credit Account, Debit Account, Inventory Name, Date of Entry, Remarks. One row per expense.
    - Inventory expense: `Expense | 5000 | EXP420736 | Jewel and Brothers | APPROVED | Inventory | Other Inventory [1107010401-02] | Other Maintenance Expenses[5108010101-07] | | 21/09/2026 | AUTOMATION_TEST expense Inventory`.
    - Accounts expense: `Expense | 5000 | EXP650673 | Jewel and Brothers | APPROVED | Accounts | Supplier Payable-Opex[2101010301-05] | Other Maintenance Expenses[5108010101-07] | | 21/09/2026 | AUTOMATION_TEST expense Accounts`.
    - Expenditure Type is `Expense`; Source/Group is the Expense Source (`Inventory` or `Accounts`); Date of Entry is dd/mm/yyyy; Credit and Debit Account include the account code in brackets; Inventory Name is empty.
    - The three `Inventory Asset ...` columns show `1 | 1 | 1` for the Inventory expense and `0 | 0 | 0` for the Accounts expense (the ERP shows ids or flags there, not names), so they are not compared.
    - The serial link must be searched with `input[name="assetSerial"]`: while the popup is open a second read-only `#assetSerial` exists.
    - Evidence: `evidence/global_list_expenditure_tab_inventory.png`.
  - Addition History, 2026-11-04 (env42 HOFA, as the HOFA acknowledger, VERIFIED by `tests/test_32_asset_serial_global_list_hofin_assets.py`):
    - The tab is shown for **every parent asset**, also one with no addition; then its grid is empty and the entries text is `Showing 0 to 0 of 0 entries` (this replaces the 2026-11-01 note below that it shows only for a parent with additions).
    - Records per page box: `#tab_addition_history` → `get_by_label("Records per page")` (a `<select name="assetAdditionHistoryList_length">` inside its label): options 10, 20, 50, 100; 10 chosen.
    - Entries text: `#tab_addition_history` → `get_by_role("status")` (`#assetAdditionHistoryList_info`), e.g. `Showing 1 to 2 of 2 entries`.
    - Asset Serial link of a row: `#assetAdditionHistoryList` → `get_by_role("link", name="<extended serial>", exact=True)` (`onclick="showChildAssetProfileDetailsPopupId(<id>)"`). It loads the extended asset into the SAME popup `#commonModal` (no second modal); Close then shows the parent's popup again (`#assetSerial` back to the parent), so the CR's "closing returns to the previous popup" holds.
    - Row values for an addition of 25000: `Addition Amount 25000`, `Addition Date` = the business date dd/mm/yyyy (same as the parent's `#registrationDate` on that day), `Reference Number JV.../26`, `Item Name Sofa Set`, `Acc. Depreciation 0`, **`WDV 24999`** while the extended asset's own popup shows `#netAssetValue` 25000.00 (seen again for 20000 → 19999). Recorded as a CR deviation.
    - Popup fields used to check a HOFIN asset: `#itemSpecification` (typed in HOFIN), `#unitPrice` (Purchase Price), `#totalAdditionRegistered` (stays 0.00 on a parent after additions), `#netAssetValue`, `#totalDepCalculated`, `#remainingLife`, `#registrationDate`, `#branchName` (`[HO - BDHO] Head Office`), `#regType` (`MRR` for a HOFIN registration). A parent has no `#parentAssetSerial` element at all.
    - Transaction History tab: the grid is the first `table` inside `#tab_transfer_history` (read by heading: `Transaction Type`, `Transaction Status`, `New Assign Status`, ...). VERIFIED 2026-11-04 on BBDASR00227790 (`ASSIGN | APPROVED | ASSIGNED`) and by `test_32` on an auto-assigned extended asset.
    - Utilization Status Change on a parent whose addition is acknowledged but not approved answers `Cannot Change Status, BBDASR00227787 is pending in Asset Addition From HOFIN`.
  - Addition History (grid `#assetAdditionHistoryList` in `#tab_addition_history`; read on env42 HOFA 2026-11-01, VERIFIED): shown ONLY for a parent asset that has additions, between Expenditure and Disposal Info. Columns: SL, Asset Serial, Addition Amount, Addition Date, Reference Number, Item Name, Acc. Depreciation, WDV, Impairment Status, Impairment ID. Example row of parent `BBDASR00227752`: `1 | BBDASR00227752-1 | 25000 | 13/09/2026 | JV09005680/26 | Sofa Set | 0 | 24999 | |`.
  - Parent and extended assets (FAHOV2-643, read on env42 HOFA 2026-11-01, VERIFIED): an extended asset is a separate row of the grid with serial `<parent serial>-1`, `-2`, ... and the parent's item. Its popup shows the parent in `#commonModal #parentAssetSerial` (label "Parent Asset") and has no Addition History tab. `#refAssetSerial` (label "Reference Asset") stays empty for both.
  - Grid order: before any search the grid lists the newest asset first (highest hidden Profile ID); the column headings cannot be sorted (`sorting_disabled`). `read_newest_parent_serial()` takes the first row of the item whose serial has no `-N` ending.
  - Filter box: use `input[name="assetSerial"]`. After a popup is closed its read-only `#assetSerial` stays in the page, so `#assetSerial` alone matches two elements.
  - Disposal Info: SL, Disposal Type, Asset Serial, Accumulated Depreciated, Written down Value, Auction/Sale Value, Base Value, Auction Start Date, Auction End Date, Approval Status, Disposal Status, Disposal Date.
  - Attachment: shows `File :` and `No Attachment` when none is attached.
- Evidence: `evidence/asset_serial_global_list.png`, `evidence/asset_serial_global_list_detail.png`.
