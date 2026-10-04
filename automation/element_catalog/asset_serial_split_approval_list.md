# Asset Serial Split Approval List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_serial_split_approval_list_page.py` → `AssetSerialSplitApprovalListPage`; tests in `tests/test_09_asset_serial_split_approval_list.py` |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset Serial Split Approval List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showAssetSplitApprovalList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 (read-only: nothing was saved, split, approved or rejected) |
| Screenshot | `evidence/asset_serial_split_approval_list.png`, `evidence/asset_serial_split_approval_view.png` |

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
| 8 | Asset Serial | Free text. | `page.locator("#assetSerial")` | "Asset Serial:" | VERIFIED |
| 9 | Created By | Employee search, min 3 characters. | `page.locator("#createdBy")` | "Created By:" | VERIFIED |
| 10 | Approved By | Employee search, min 3 characters. | `page.locator("#approvedBy")` | "Approved By:" | VERIFIED |
| 11 | Search / Reset (filter) | Runs / clears the filter. | `get_by_role("button", name="Search")`, `page.locator("#resetUpdate")` | Search, Reset | VERIFIED |
| 12 | Row checkbox | Selects a split request for bulk Approve / Reject. | row `input[name=post]` scoped to the `tr` of the split number | Checkbox, first column | VERIFIED |
| 13 | Approve button | Approves the ticked splits (onclick `submit()`). Generates the new asset serials. | `page.locator("#btnApprove")` | Approve | VERIFIED locator; not clicked |
| 14 | Reject button | Rejects the ticked splits (onclick `reject()`). | `page.locator("#btnReject")` | Reject | VERIFIED locator; not clicked |
| 15 | Reset button (bottom) | Clears the ticked rows (onclick `resetAssetSplitListTable()`). | `page.locator("#resetEditButton")` | Reset | VERIFIED |
| 16 | Results grid | Columns: checkbox, SL, Asset Split No., Asset Group, Project Name, Department Name, Asset Serial No., Split Into, Remarks, Created By, Status, Approved By, Approval Date, (hidden). | `page.locator("#assetSplitList")` | List of splits | VERIFIED |
| 17 | Asset Split No. link (row) | Opens the **Asset Split View** popup (read-only). | `page.locator("#assetSplitList tbody tr a").first` or by link text | Blue split number | VERIFIED |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset Serial Split Approval List` (`page.get_by_role("link", name="Asset Serial Split Approval List", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- The list already holds three **APPROVED** splits (created and approved by the same user, MD. TANVIR ALAM): split 27 (Computer/Laptop, asset `BDHO-0099-000536`, split into 20, approved 24/02/2026), split 26 (Land, `BDHO-0099-000073`, split into 2, 30/11/2025), split 17 (Computer/Laptop, `BDHO-0099-001180`, split into 2, 14/08/2025). Approved rows still appear here.
- No PENDING split exists on staging, so **Approve and Reject were not run**.
- Asset serials on this screen use the older format `BDHO-0099-000536`; the newly registered asset uses `BBDASR00227761`.

## Popup: "Asset Split View" (click an Asset Split No.)
- Container: open modal (`.modal.in`); title `Asset Split View`. Button: `Close`.
- Read-only fields: `#projectName`, `#departmentName`, `#group`, `#subCategory`, `#assetSerial`, `#itemSpecification`, `#measurement`, `#splitInto` (number, labelled 'Split Into: *'), `#branchName`, `#category`, `#assetName`, `#netAssetValue` (Asset Written Down Value), `#accumulatedDepriciation` (sic, spelled this way in the page), `#remarks` (textarea, disabled).
- Grid `#assetSerialSplitList`: SL, Asset Item Name, Item Specification, Sub Category, Category Name, Group Name, Measurement Unit, Percentage, Written Down Value, Acc. Depreciation, Measurement, percentageVal. For split 27 it holds 20 equal lines of 5 percent each, which matches the documented rule that Split Into divides the value into equal parts.
- Evidence: `evidence/asset_serial_split_approval_list.png`, `evidence/asset_serial_split_approval_view.png`.
