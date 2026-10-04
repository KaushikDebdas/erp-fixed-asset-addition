# Asset Serial Split — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_serial_split_page.py` → `AssetSerialSplitPage`; tests in `tests/test_07_asset_serial_split.py` |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset Serial Split |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showAssetSerialForSplitList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 (read-only: nothing was saved, split, approved or rejected) |
| Screenshot | `evidence/asset_serial_split.png`, `evidence/asset_serial_split_form.png` |

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
| 9 | Search / Reset | Runs / clears the filter. | `get_by_role("button", name="Search")` (onclick `showAssetSerialSearch()`), `#resetUpdate` | Search, Reset | VERIFIED |
| 10 | Records per page | 10 / 20 / 30 / 50 / 100. | `page.locator("select[name=assetSerialGlobalList_length]")` | Records per page | VERIFIED |
| 11 | Results grid | Columns: Profile ID (hidden), SL, Asset Serial, Asset Item Name, Sub Category, Category Name, Group Name, Project Name, Department Name, Assign Status, Action. Shows 10 rows before a search. | `page.locator("#assetSerialGlobalList")` | List of Global Asset Serial | VERIFIED |
| 12 | SPLIT button (row) | Starts a split for that asset. Rendered with onclick `getAssetSerialForSplitById('<profileId>', '<assignStatus>', <measurement>)`. | `page.locator("tr", has_text="<asset serial>").locator("a.btn, button", has_text="SPLIT")` (NOT `get_by_role("button")`, it is not exposed as a button) | Green SPLIT button, Action column | VERIFIED |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset Serial Split` (`page.get_by_role("link", name="Asset Serial Split", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- **Measurement rule confirmed live.** Clicking SPLIT for `BBDASR00227761` (measurement 0) shows a red toast: `Cannot split: Please set a valid measurement above zero.` and no form opens. This confirms the documented prerequisite.
- **Split form verified (2026-10-03)** with the test Land asset `BBDASR00227763` (measurement 12.50). Clicking its SPLIT button opens the form as a page section headed `Asset Split` with a `Back` link (not a popup). Fields: read-only `#projectName`, `#departmentName`, `#group`, `#subCategory`, `#assetSerial`, `#itemSpecification`, `#measurementFront` (Measurement, shows 12.50), `#branchName`, `#category`, `#assetName`, `#netAssetValue` (Asset Written Down Value, 25000.00), `#accumulatedDepriciation` (sic, 0.00); editable `#splitInto` (number, `Split Into *`) and `#remarks` (textarea). Button `Split` = `#splitAsset` (`splitIntoAssets()`). Result grid `#assetSerialSplitList`: SL, Asset Item Name, Item Specification, Sub Category, Category Name, Group Name, Measurement Unit, Percentage, Written Down Value, Acc. Depreciation, Measurement, percentageVal, measurementVal. All form elements: VERIFIED.
- Typing a value in Split Into (Tab or key presses) does **not** fill the result grid ("No data available in table") and sends no request, so the grid is built by the Split button. **The Split button was not clicked**: it would split the asset and create new serials (cannot be undone). Status of the split submit and its success message: `LOCATOR_REQUIRES_REVIEW`.
- The same test asset can be used for the split run if the team wants it: Land `BBDASR00227763`, registration `757793`.
- Only split a disposable asset such as the test Land asset above: a split creates new serial numbers that cannot be undone.
- Evidence: `evidence/asset_serial_split.png`, `evidence/asset_serial_split_form.png` (the measurement error toast), `evidence/asset_serial_split_form_open.png` (the form for the Land asset), `evidence/asset_serial_split_preview_2.png`.
