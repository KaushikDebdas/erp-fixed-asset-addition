# Asset In Pending Process List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_in_pending_process_list_page.py` → `AssetInPendingProcessListPage`; tests in `tests/test_06_asset_in_pending_process_list.py` |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset In Pending Process List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showPendingAssetList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 (read-only: nothing was saved, split, approved or rejected) |
| Screenshot | `evidence/asset_in_pending_process_list.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Asset Serial | Free text. | `page.locator("#assetSerial")` | "Asset Serial:" | VERIFIED |
| 2 | Asset Item Name | Free text. | `page.locator("#assetName")` | "Asset Item Name:" | VERIFIED |
| 3 | Pending Feature | Free text; the screen name the asset is pending in (e.g. 'Asset Assign'). | `page.locator("#pendingFeature")` | "Pending Feature:" | VERIFIED |
| 4 | Status | Options: PENDING, APPROVED, DRAFT, SENDBACK. | `page.locator("#assetStatus")` | "Status:" | VERIFIED |
| 5 | Search button | Runs the filter. | `get_by_role("button", name="Search")` (onclick `searchAssetFromPendingList()`) | Search | VERIFIED |
| 6 | Reset button | Clears the filter. | `page.locator("#resetUpdate")` | Reset | VERIFIED |
| 7 | Export button | Downloads the pending list as Excel. **Not in the documents.** | `page.locator("#exportBtn")` (onclick `downloadExcelOfPendingList()`) | Export | VERIFIED |
| 8 | Records per page | 10 / 20 / 30 / 50 / 100. | `page.locator("select[name=pendingAssetTable_length]")` | Records per page | VERIFIED |
| 9 | Results grid | Columns: SL, (hidden), Asset Serial, From Branch, To Branch, From Project, From Department, To Project, To Department, Asset Item Name, Sub Category, Category Name, Group Name, Status, Pending in Feature, Created By, Creation Date, Aging. Shows 8 rows before any search on staging. | `page.locator("#pendingAssetTable")` | Asset in Pending Process grid | VERIFIED |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset In Pending Process List` (`page.get_by_role("link", name="Asset In Pending Process List", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- The live grid has more columns than the manual lists (From/To Branch, From/To Project and Department, Created By, Creation Date, Aging).
- A search for text that is not shaped like a serial (e.g. `NOSUCHSERIAL000`) is ignored and the unfiltered list comes back; a well-formed serial that is not pending (e.g. `BBDASR99999999`) returns `No data available in table`. Tests use the well-formed form.
- **Export verified**: clicking `#exportBtn` downloads `Asset In Pending Process List.xlsx` (use `page.expect_download()`). One sheet, header row plus one row per grid row, 17 columns: SL, Asset Serial, From Branch, To Branch, From Project, From Department, To Project, To Department, Asset Item Name, Sub Category, Category Name, Group Name, Status, Pending in Feature, Created By, Creation Date, Aging. It held 8 data rows, matching the grid. Rows seen: `Pending in Feature` = `Asset Single In-Challan`, Status APPROVED, Aging in days.
- Evidence: `evidence/asset_in_pending_process_list.png`.
- **First load race (2026-10-06):** the list fills its first rows a moment after the page appears. A search or an Export started before that is overwritten by the first load: the grid then shows the unfiltered list while the serial typed in the box is not applied. Wait for the first row before searching or exporting (`AssetInPendingProcessListPage.navigate_here` does).
- **Empty result:** a serial with no pending process can show the "No data available in table" row several seconds after Search.
- **Export (2026-10-06):** on one run Export started no download within 30 seconds. `test_pending_list_export_downloads_excel` in `test_06_asset_in_pending_process_list.py` fails with that message; not yet explained.
