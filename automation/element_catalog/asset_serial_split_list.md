# Asset Serial Split List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_serial_split_list_page.py` → `AssetSerialSplitListPage`; tests in `tests/test_08_asset_serial_split_list.py` (old) and `tests/test_08_asset_serial_split_list_new.py` (new; popup class `pages/asset_split_view_popup.py`) |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset Serial Split List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showAssetSplitList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-07 (live, with split no. 67 PENDING and then APPROVED). First explored 2026-10-03 read-only. |
| Screenshot | `evidence/asset_serial_split_list.png`, `evidence/split_list67.png`, `evidence/split_list_appr.png`, `evidence/split_view67.png` |

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
| 8 | Asset Serial | Free text. After the Asset Split View popup has been opened a second element with id `assetSerial` exists (the popup's read-only box), so `#assetSerial` then matches two elements. | `page.locator('input[name="assetSerial"]')` (safe in every state); `#assetSerial` only before a popup is opened | "Asset Serial:" | VERIFIED |
| 9 | Created By | Employee search; placeholder 'Employee Pin No./Name (Min 3 char...)'. The autocomplete is NOT triggered by typing (script has `minLength: 3000`): type 3+ characters, then click the small magnifier icon next to the box; one suggestion appears (`abushoaib.asik-Abu Shoaib Asik`), click it. | box `page.locator("#createdBy")`; icon `page.locator("#createdBy").locator("xpath=ancestor::div[contains(@class,'form-group')][1]").locator("i.fa-search")`; suggestion `page.locator("ul.ui-autocomplete li:visible").first` | "Created By:" | VERIFIED (typing, icon click and suggestion tested; the filtered Search was run once) |
| 10 | Approved By | Same employee search and icon, min 3 characters. | `page.locator("#approvedBy")` | "Approved By:" | VERIFIED locator; filter not run |
| 11 | Search button | Runs the filter. | `get_by_role("button", name="Search")` (onclick `showAssetSerialSearch()`) | Search | VERIFIED |
| 12 | Reset button | Clears the filter boxes (Created By and Asset Serial become empty) and reloads the grid. | `page.locator("#resetUpdate")` (onclick `resetSearchForm()`) | Reset | VERIFIED (live) |
| 13 | Records per page | 10 / 20 / 30 / 50 / 100. | `page.locator("select[name=assetSplitList_length]")` | Records per page | VERIFIED |
| 14 | Results grid | Columns: Split Id (hidden), SL, Asset Split No., Asset Group, Project Name, Department Name, Asset Serial No., Split Into, Remarks, Created By, Status, Approved By, Approval Date. | `page.locator("#assetSplitList")` | List of splits | VERIFIED |
| 15 | Asset Split No. link (row) | Opens the read-only `Asset Split View` popup. `<a href="javascript:;" onclick="assetSplitDetails('67')">67</a>`. | `page.locator("#assetSplitList tbody tr", has_text="<serial>").locator("a")` | Blue split number | VERIFIED (live) |
| 16 | Entries line | Text under the grid. | `page.locator("#assetSplitList_info")` | "Showing 1 to 1 of 1 entries" | VERIFIED |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset Serial Split List` (`page.get_by_role("link", name="Asset Serial Split List", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- **New screen, not in the documents.** It lists the splits made by the user, with their approval status.
- On 2026-10-03 this user had no splits. On 2026-10-07 the unfiltered list shows exactly 1 entry, the split created in the live run.

## Live run (2026-10-07), split of Land `BBDASR00227979`
- Row after Submit: `1 | 67 | Land | [015] Microfinance (Dabi) | (department empty) | BBDASR00227979 | 2 | AUTOMATION_TEST split note | Abu Shoaib Asik | PENDING | (Approved By empty) | (Approval Date empty)`.
- Row after approval: same, with Status `APPROVED`, Approved By `Abu Shoaib Asik`, Approval Date `20/09/2026` (the ERP accounting/business date, not the calendar date).
- **Asset Split View popup** (click `67`): modal `.modal.in`, title `Asset Split View`, `Close` button. Read-only values: project `Microfinance (Dabi)`, group `Land`, assetSerial `BBDASR00227979`, itemSpecification `AUTOMATION_TEST-SPEC-LAND_20261007_091308`, `#measurement` 12.50, `#splitInto` 2, branch `[HO - BDHO] Head Office`, category `Land`, assetName `Land`, `#netAssetValue` 25000.00, `#accumulatedDepriciation` 0.00, `#remarks` `AUTOMATION_TEST split note`. Grid `#assetSerialSplitList` lines: `1 | Land | spec | Land | Land | Land | Decimal | 40.12 | 10030 | 0 | 5.01` and `2 | ... | Decimal | 59.88 | 14970 | 0 | 7.49`; `Grand Total: 100 | 25000.00 | 0.00 | 12.50`. The popup does NOT list the new serial numbers.
- Created By filter: icon click gave the one suggestion; Search by Created By returned the row; Reset emptied Created By and Asset Serial and the grid showed `Showing 1 to 1 of 1 entries`.
- LOCATOR_REQUIRES_REVIEW: none. Approved By filter not exercised with a search.
- Evidence: `evidence/asset_serial_split_list.png`, `evidence/split_list67.png` (PENDING), `evidence/split_list_appr.png` (APPROVED), `evidence/split_view67.png` (popup).
