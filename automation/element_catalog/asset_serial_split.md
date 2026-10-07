# Asset Serial Split — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_serial_split_page.py` → `AssetSerialSplitPage`; tests in `tests/test_07_asset_serial_split.py` (old) and `tests/test_07_asset_serial_split.py` (new; helper `utils/split_helper.py`) |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset Serial Split |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showAssetSerialForSplitList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-07 (LIVE: a real split was submitted and approved, split no. 67, see "Live split run" below). First explored 2026-10-03 read-only. |
| Screenshot | `evidence/asset_serial_split.png`, `evidence/asset_serial_split_form.png`, `evidence/split_grid.png`, `evidence/split_after.png` |

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
| 8 | Asset Serial | Free text. NOTE: once the form is opened, a second element with the same id exists (the read-only box of the form), so after opening a form use `page.locator('input[name="assetSerial"]')` for the filter. | `page.locator("#assetSerial")` (before the form is opened) / `page.locator('input[name="assetSerial"]')` | "Asset Serial:" | VERIFIED |
| 9 | Search / Reset | Runs / clears the filter. | `get_by_role("button", name="Search")` (onclick `showAssetSerialSearch()`), `#resetUpdate` | Search, Reset | VERIFIED |
| 10 | Records per page | 10 / 20 / 30 / 50 / 100. | `page.locator("select[name=assetSerialGlobalList_length]")` | Records per page | VERIFIED |
| 11 | Results grid | Columns: Profile ID (hidden), SL, Asset Serial, Asset Item Name, Sub Category, Category Name, Group Name, Project Name, Department Name, Assign Status, Action. Shows 10 rows before a search. | `page.locator("#assetSerialGlobalList")` | List of Global Asset Serial | VERIFIED |
| 12 | SPLIT button (row) | Starts a split for that asset. Rendered `<a href="javascript:;" class="btn btn-success" onclick="getAssetSerialForSplitById('<profileId>', '<assignStatus>', <measurement>)">SPLIT</a>`. | `page.locator("tr", has_text="<asset serial>").locator("a.btn, button", has_text="SPLIT")` (NOT `get_by_role("button")`, it is not exposed as a button) | Green SPLIT button, Action column | VERIFIED |
| 13 | Split Into | Number box on the form, `Split Into *`. | `page.locator("#splitInto")` | Split Into | VERIFIED |
| 14 | Remarks | Textarea on the form. | `page.locator("#remarks")` | Remarks | VERIFIED |
| 15 | Split button | Builds the result grid (does not save). onclick `splitIntoAssets()`. | `page.locator("#splitAsset")` | Split | VERIFIED (live) |
| 16 | Draft button | Saves the split as DRAFT. onclick `saveAssetSplit("DRAFT")`. Appears with the grid. | `page.locator("#save")` | Draft | VERIFIED locator; NOT clicked |
| 17 | Submit button | Saves the split as PENDING for approval. onclick `saveAssetSplit("PENDING")`. | `page.locator("#submit1")` | Submit | VERIFIED (live, clicked once) |
| 18 | Form Reset | Clears the form. onclick `resetForm()`. | `page.locator("#resetEditButton")` | Reset | VERIFIED locator; NOT clicked |
| 19 | Percentage box, line N (N from 0) | Editable on every line except the last; the last line is read-only and takes the balance. | `page.locator("#percentage_0")`, `#percentage_1` (read-only) | Percentage column | VERIFIED (live) |
| 20 | Measurement box, line N | Editable on every line except the last (read-only, balance). | `page.locator("#measurement_0")`, `#measurement_1` | Measurement column | VERIFIED (live) |
| 21 | Grid totals | Footer row `Grand Total:` with ids used by the page script. | `#totalPercentage`, `#totalWrittenDownValue`, `#totalAccDepriciation`, `#totalMeasurement` | Grand Total row | VERIFIED (ids read from the page script) |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset Serial Split` (`page.get_by_role("link", name="Asset Serial Split", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- **Measurement rule confirmed live.** Clicking SPLIT for `BBDASR00227761` (measurement 0) shows a red toast: `Cannot split: Please set a valid measurement above zero.` and no form opens. This confirms the documented prerequisite.
- **Split form verified (2026-10-03)** with the test Land asset `BBDASR00227763` (measurement 12.50). Clicking its SPLIT button opens the form as a page section headed `Asset Split` with a `Back` link (not a popup). Fields: read-only `#projectName`, `#departmentName`, `#group`, `#subCategory`, `#assetSerial`, `#itemSpecification`, `#measurementFront` (Measurement, shows 12.50), `#branchName`, `#category`, `#assetName`, `#netAssetValue` (Asset Written Down Value, 25000.00), `#accumulatedDepriciation` (sic, 0.00); editable `#splitInto` (number, `Split Into *`) and `#remarks` (textarea). Result grid `#assetSerialSplitList`: SL, Asset Item Name, Item Specification, Sub Category, Category Name, Group Name, Measurement Unit, Percentage, Written Down Value, Acc. Depreciation, Measurement, percentageVal, measurementVal.
- Typing a value in Split Into does not fill the result grid; only the Split button builds it.
- Only split a disposable asset such as the test Land asset: a split creates new serial numbers that cannot be undone.

## Live split run (2026-10-07, asset Land `BBDASR00227979`, registration 758131, measurement 12.50, WDV 25000.00, Acc. Dep 0.00)
- **Form values** (read-only boxes): project `Microfinance (Dabi)`, department empty, group/sub category/category/item `Land`, branch `[HO - BDHO] Head Office`, itemSpecification `AUTOMATION_TEST-SPEC-LAND_20261007_091308`, `#measurementFront` 12.50, `#netAssetValue` 25000.00, `#accumulatedDepriciation` 0.00.
- **Split button validation toasts (red, `.toast-message`, nothing saved):**
  - Split Into empty: `Split into field is mandatory`
  - Split Into 0, 1, -3 or 100000: `Please enter a valid integer number between 2 and 100` (valid range is 2 to 100)
  - Remarks empty with Split Into 2: no toast; the grid is still built (remarks is not checked at Split time).
- **Grid after Split with 2** (no toast, no dialog): 2 rows (SL 1, 2), both Asset Item `Land`, Item Specification the same text, Measurement Unit `Decimal`; Percentage, Measurement boxes are empty/0, Written Down Value 0, Acc. Depreciation 0; footer `Grand Total:` 0.00 for each. Line 1 percentage and measurement boxes are editable, the last line is read-only and fills with the balance.
- **Typing a percentage in line 1** (blur) fills the rest: percentage 40 gives line 1 measurement 5.00, WDV 10000, line 2 percentage 60.00, measurement 7.50, WDV 15000; footer totals 100.00 / 25000.00 / 0.00 / 12.50. So the equal-parts rule in the document is not enforced: the user chooses the percentages. Typing a measurement (5) with empty percentage gives line 2 WDV 25000 and total percentage NaN.
- **A percentage with 3 decimals (40.123) is stored as 40.12**; line 2 became 59.88, measurements 5.01 / 7.49, WDV 10030 / 14970 (this is what was actually saved, split no. 67).
- **Buttons after the grid is built:** `Split` `#splitAsset`, `Draft` `#save`, `Submit` `#submit1`, `Reset` `#resetEditButton`. No confirm dialog on Submit.
- **Submit validation messages** (read from the page script `checkValidationSave` and `saveAssetSplit`, client-side, red toast; the first one for the empty percentage was seen to block the save, the others are SOURCE-READ, not seen as toasts): `Percentage value is empty`, `Measurement value is empty`, `Measurement value is not valid` (measurement 0 or less), `Percentage value is not valid` (zero, negative or more than 2 decimals), `Total percentage should be equal to 100`, `Total WrittenDown should be equal to <WDV>`, `Total Accumulated Depreciation should be equal to <value>`, `Total measurement should be equal to <measurement>`, `Your split count and split item not matched` (Split Into changed after the grid was built), `Written down value should not be less than 1`. Remarks empty at Submit: NOT TESTED (no client check exists; the server's reaction is unknown, and the real submit is irreversible).
- **Successful Submit:** POST `/nodef/faAssetProfile/create`, response message `Asset split submitted successfully` (success toast; the toast itself was not caught on screen, the text is from the response). The page returns to the Asset Serial Split list.
- **After Submit (still PENDING):** searching `BBDASR00227979` on this screen gives `No data available in table` (the asset leaves the splittable list). On the Asset Serial Global List the serial is still shown, `UNASSIGNED`, Utilization Status `IN_USE`. Split list row: split no. 67, status PENDING.
- **After approval:** the original `BBDASR00227979` is gone from this screen and from the Global List (search gives `No data available in table`). New serials: `BBDASR00227986` (5.01, WDV 10030) and `BBDASR00227987` (7.49, WDV 14970), both `UNASSIGNED`, `IN_USE`, with `refAssetSerial` = `BBDASR00227979`, a new approved registration 758142 (type AAQ). See the Approval List catalog.
- LOCATOR_REQUIRES_REVIEW: none. The Draft button was never clicked (its result is untested).
- Evidence: `evidence/split_grid.png` (grid after Split), `evidence/split_after.png`.
