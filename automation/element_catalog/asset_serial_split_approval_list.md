# Asset Serial Split Approval List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_serial_split_approval_list_page.py` → `AssetSerialSplitApprovalListPage`; tests in `tests/test_09_asset_serial_split_approval_list.py` (old) and `tests/test_09_asset_serial_split_approval_list.py` (new; popup class `pages/asset_split_view_popup.py`) |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset Serial Split Approval List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showAssetSplitApprovalList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]; the same user can approve a split it created) |
| Last explored | 2026-10-07 (live: split no. 67 was approved). First explored 2026-10-03 read-only. |
| Screenshot | `evidence/asset_serial_split_approval_list.png`, `evidence/asset_serial_split_approval_view.png`, `evidence/split_appr_view.png`, `evidence/split_appr_tick.png`, `evidence/split_appr_toast.png`, `evidence/split_global.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Organization Branch | Select2; 'Head Office [ BDHO ]'. | `page.locator("#office")` | "Organization Branch:" | VERIFIED |
| 2 | Project | 1467 options. | `page.locator("#project")` | "Project:" | VERIFIED |
| 3 | Department | Disabled until a Project is chosen. | `page.locator("#department")` | "Department:" | VERIFIED |
| 4 | Asset Group | 31 options. | `page.locator("#faAssetGroup")` | "Asset Group:" | VERIFIED |
| 5 | Asset Category | 48 options. | `page.locator("#faAssetCategory")` | "Asset Category:" | VERIFIED |
| 6 | Asset Sub Category | 84 options. | `page.locator("#faAssetSubCategory")` | "Asset Sub Category:" | VERIFIED |
| 7 | Asset Item Name | A drop-down here (1081 options), unlike the free-text box on the Global List. | `page.locator("#assetName")` | "Asset Item Name:" | VERIFIED |
| 8 | Asset Serial | Free text. After a popup has been opened, `#assetSerial` matches two elements. | `page.locator('input[name="assetSerial"]')` | "Asset Serial:" | VERIFIED |
| 9 | Created By | Employee search, min 3 characters, needs the magnifier icon (see the Split List catalog). | `page.locator("#createdBy")` | "Created By:" | VERIFIED |
| 10 | Approved By | Employee search, min 3 characters. | `page.locator("#approvedBy")` | "Approved By:" | VERIFIED |
| 11 | Search / Reset (filter) | Runs / clears the filter. | `get_by_role("button", name="Search")`, `page.locator("#resetUpdate")` | Search, Reset | VERIFIED |
| 12 | Row checkbox | Selects a split request. REAL attributes: `<input type="checkbox" name="assetSplitApproval" id="assetSplitApproval" onclick="toggleDselect(this)" value="1">`. The earlier note `input[name=post]` was WRONG for rows: `name=post` is the header select-all box only. | `page.locator("#assetSplitList tbody tr", has_text="<serial>").locator("input[name=assetSplitApproval]")` | Checkbox, first column | VERIFIED (live, `.check()` works) |
| 13 | Header select-all | Ticks every row. onclick `toggle(this)`. | `page.locator("#assetSplitList thead input[name=post]")` | Header checkbox | VERIFIED locator; not clicked |
| 14 | Approve button (grid) | Approves the ticked splits (onclick `submit();`). The id `btnApprove` is DUPLICATED: the Asset Split View popup holds a second `#btnApprove` (onclick `approveAssetSplit()`), so `#btnApprove` fails with a strict-mode error once the popup markup exists. | `page.locator('button[onclick="submit();"]')` (or `get_by_role("button", name="Approve")` scoped away from `#approveButtonDetails`) | Approve | VERIFIED (live, clicked) |
| 15 | Reject button (grid) | Rejects the ticked splits (onclick `reject()`). Same duplicated-id caveat (`#btnReject` also exists in the popup, onclick `rejectAssetSplit("REJECTED")`). | `page.locator('button[onclick="reject();"]')` (onclick text read from the earlier note, not re-read; check before use) | Reject | VERIFIED locator by earlier note; not clicked with a row ticked |
| 16 | Reset button (bottom) | Clears the ticked rows (onclick `resetAssetSplitListTable()`). | `page.locator("#resetEditButton")` | Reset | VERIFIED |
| 17 | Results grid | Columns: checkbox, SL, Asset Split No., Asset Group, Project Name, Department Name, Asset Serial No., Split Into, Remarks, Created By, Status, Approved By, Approval Date, (hidden). | `page.locator("#assetSplitList")` | List of splits | VERIFIED |
| 18 | Asset Split No. link (row) | Opens the **Asset Split View** popup (read-only). | `page.locator("#assetSplitList tbody tr", has_text="<serial>").locator("a")` | Blue split number | VERIFIED |
| 19 | Popup Approve / Reject | Inside `#approveButtonDetails` of the Asset Split View popup. | `page.locator("#approveButtonDetails #btnApprove")`, `#approveButtonDetails #btnReject` | Approve, Reject (popup) | VERIFIED locator; NOT clicked (popup shown with the Close button) |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset Serial Split Approval List` (`page.get_by_role("link", name="Asset Serial Split Approval List", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- Three older APPROVED splits exist on staging (created and approved by MD. TANVIR ALAM): split 27 (Computer/Laptop, `BDHO-0099-000536`, into 20, approved 24/02/2026), split 26 (Land, `BDHO-0099-000073`, into 2, 30/11/2025), split 17 (Computer/Laptop, `BDHO-0099-001180`, into 2, 14/08/2025). Approved rows still appear here.
- Asset serials on those older splits use the format `BDHO-0099-000536`; newly registered assets use `BBDASR...`.

## Popup: "Asset Split View" (click an Asset Split No.)
- Container: open modal (`.modal.in`); title `Asset Split View`. Button: `Close`.
- Read-only fields: `#projectName`, `#departmentName`, `#group`, `#subCategory`, `#assetSerial`, `#itemSpecification`, `#measurement`, `#splitInto` (number, labelled 'Split Into: *'), `#branchName`, `#category`, `#assetName`, `#netAssetValue` (Asset Written Down Value), `#accumulatedDepriciation` (sic), `#remarks` (textarea, disabled).
- Grid `#assetSerialSplitList`: SL, Asset Item Name, Item Specification, Sub Category, Category Name, Group Name, Measurement Unit, Percentage, Written Down Value, Acc. Depreciation, Measurement. Split 27 holds 20 lines of 5 percent; split 67 holds the user-chosen 40.12 and 59.88 percent (see the Split catalog).
- Evidence: `evidence/asset_serial_split_approval_list.png`, `evidence/asset_serial_split_approval_view.png`, `evidence/split_appr_view.png`.

## Live run (2026-10-07), approving split 67 (Land `BBDASR00227979`)
- Search by serial `BBDASR00227979` shows 1 row: `1 | 67 | Land | [015] Microfinance (Dabi) | | BBDASR00227979 | 2 | AUTOMATION_TEST split note | Abu Shoaib Asik | PENDING | | `.
- **Nothing ticked, Approve clicked:** blue info toast `You have to select a split first`. **Nothing ticked, Reject clicked:** the same text `You have to select a split first`. No dialog in either case.
- **Approve flow:** tick the row checkbox, click the grid Approve button. There is NO confirm dialog and NO comment box. The request is GET `/nodef/faAssetProfile/approveAssetSplit?...assetSplitInfo.assetSplitInfo[0].id=67`; response message `Asset Split approved successfully.` (success toast text from the response; the toast itself faded before it could be read from the screen). Within about 3 seconds the row shows Status `APPROVED`, Approved By `Abu Shoaib Asik`, Approval Date `20/09/2026` (business date); the row stays in the list.
- **What the approval generated:** a new APPROVED Asset Registration `758142` (type AAQ, same supplier ACE IT, purchase date 20/09/2026) with two new asset profiles, both `UNASSIGNED`, `IN_USE`, `refAssetSerial` = `BBDASR00227979`: serial `BBDASR00227986` (measurement 5.01, current value 10030.00) and serial `BBDASR00227987` (measurement 7.49, current value 14970.00). Both found on the Asset Serial Global List (utilization IN_USE, assign UNASSIGNED). The original `BBDASR00227979` is no longer found on the Global List or on the Asset Serial Split screen (`No data available in table`).
- Reject was NOT run (the asset is needed approved).
- LOCATOR_REQUIRES_REVIEW: none; the grid Reject locator (row 15) must be confirmed against the page source before use.
