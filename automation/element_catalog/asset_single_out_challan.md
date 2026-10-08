# Asset Single Out Challan — element catalog

| Field | Value |
|---|---|
| Page class | `pages/single_out_challan_page.py` → `SingleOutChallanPage` (inherits `SingleChallanListPage` in `pages/single_challan_list_page.py`); tests in `tests/test_23_asset_single_out_challan.py`, stages in `utils/single_challan_flow.py` |
| Module / menu path | Fixed Asset >> Single Challan >> Asset Single Out Challan (menu links: Asset Single Out Challan, Asset Single Out Challan Approval List, Asset Single In-Challan, Gate Pass Generation, Asset Receivable List, Asset Returnable List) |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetSingleChallan/show` (reach via menu click) |
| Role needed | one user does everything for now (the logged-in `TEST_USERNAME`); explored with `abushoaib.asik` and `00015370` |
| Last explored | 2026-10-08 |
| Screenshot | `evidence/asset_single_out_challan_create.png`, `evidence/asset_single_out_challan_add_serial.png` |

## Elements — list

| # | Element | Locator (Playwright) | Status |
|---|---|---|---|
| 1 | Filters: Out Challan Number, Challan From/To Date, Return Date From/To, Created By, Approved By, Challan Status (PENDING, APPROVED, REJECTED, ACKNOWLEDGED, SENDBACK) | `#outChallanNumber`, `#challanFromDate`, `#challanToDate`, `#returnDateFrom`, `#returnDateTo`, `#createdBy`, `#approvedBy`, `#assetChallanStatus` | VERIFIED (Out Challan Number and Status used) |
| 2 | Search / Reset | `get_by_role("button", name="Search")`, `#resetUpdate` | VERIFIED |
| 3 | Grid (newest first) | `#challanListTable`, info line `#challanListTable_info`. Columns: (checkbox), SL, (id), Out Challan Number (cell 3), Edit, Status, In Challan Number, Challan Date, Sending Branch, Receiving Branch, From Project, From Department, To Project, To Department, Created By, Approved By, Acknowledged By, Approval Date, Receivable By Date/Status, Preview | VERIFIED |
| 4 | Edit link | Only on a DRAFT row: `row.get_by_role("link", name="Edit", exact=True)`; opens the Edit popup with Update, Submit, Delete | VERIFIED |
| 5 | Create | `page.locator("a.btn", has_text="Create")` (a link with no role name) | VERIFIED |

## Elements — Create / Edit Challan popup `#challanResponsiveSingleChallan`

| # | Element | Locator | Status |
|---|---|---|---|
| 1 | Challan Number (placeholder `AUTO`) | `#challanNumber` | VERIFIED |
| 2 | Sending Branch (pre-filled `Head Office [ BDHO ]`) | `#s2id_office` | VERIFIED |
| 3 | From Project (required) | `#s2id_fromProject` (search box: click `a.select2-choice`, type, click `.select2-result-label`) | VERIFIED |
| 4 | Receiving Branch (required) | `#s2id_destinationBranch` | VERIFIED |
| 5 | To Project (required) | `#s2id_destinationProject` | VERIFIED |
| 6 | Asset Item Name (required); fills `#assetCategory`, `#assetSubCategory`, `#assetGroup`, `#uom` | `#s2id_asset` | VERIFIED |
| 7 | Quantity (required), Challan Note | `#quantity`, `#remarks` | VERIFIED |
| 8 | Add (item line), grid | `#addToAssetItemGrid`, `#assetItemsTable` (SL, Asset Item Name, Sub Category, Category, Measurement Unit, Quantity, Action) | VERIFIED |
| 9 | Draft / Submit / Reset / Update / Delete | `#createChallan`, `#submitChallan`, `#resetChalan`, `#updateChallan`, `#deleteChallan` | VERIFIED (Reset, Update, Delete not clicked) |
| 10 | Not used: Receivable `#isBacked`, Returnable `#isReturn` (with `#challanReturnDate`), Challan Date `#challanDate`, courier boxes | | seen only |

## Elements — challan popup `#singleChallanDetailsModal` and Add Asset Serial popup `#addAssetSerialModal`

| # | Element | Locator | Status |
|---|---|---|---|
| 1 | Read-only fields | `#challanNumberDetails`, `#outChallanDateDetails`, `#inChallanNumberDetails`, `#fromProjectDetails`, `#toProjectDetails`, `#transactionStatusType`, `#fromBranchDetails`, `#toBranchDetails`, `#challanCreatedByDetails`, `#challanApprovalDateDetails`, `#challanApprovedByDetails` | VERIFIED |
| 2 | Tabs Details / Asset Serials; serials grid | `.nav-tabs a`, `#assetSerialTable` (visible columns: SL, Asset Serial, Item Name, Sub Category, Category, Disposal, Transfer to Maintenance) | VERIFIED |
| 3 | Add Serial link (item row) | `popup.get_by_role("link", name="Add Serial")` | VERIFIED |
| 4 | Serial No box, then Add, Save | `#s2id_assetSerialSelect`; Add is a link `#addAssetSerialModal a.btn` (text Add, no href); Save `#saveAssetSerial`; grid `#assetSerialItemAdditionTable` | VERIFIED |
| 5 | Close | `popup.get_by_role("button", name="Close", exact=True)` | VERIFIED |

## Notes
- **Flow verified (2026-10-08):** Create (From Project, Receiving Branch, To Project, item, quantity 1) -> Add -> **Submit**: the popup closes and the challan is **PENDING** at once (no serial needed yet). Then the Out Challan Number link -> Add Serial -> serial -> Add -> Save, toast `Asset serial added successfully`, popup stays on the challan.
- **Draft path:** Draft saves the challan as DRAFT with an Edit link; Edit opens the popup with Update, Submit, Delete; Submit makes it PENDING.
- **No message for Draft or Submit:** no toast appeared, and a DOM watcher saw none either; the tests check the list Status.
- The serial box lists every approved, unassigned asset that fits the item; type the serial to find one.
- The challan stays in the same branch (Head Office), project `[015]` to `[060] Progoti` (the same projects as Asset Shipment).
- Explored with challans OC-79823 (Submit path, serial `BBDASR00227758`, approved) and OC-79824 (Draft, Edit, Submit, left PENDING without a serial).
