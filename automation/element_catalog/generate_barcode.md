# Generate Barcode — element catalog

| Field | Value |
|---|---|
| Page class | `pages/generate_barcode_page.py` → `GenerateBarcodePage`; tests in `tests/test_05_generate_barcode.py` |
| Module / menu path | Fixed Asset >> Asset Profile >> Generate Barcode |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faBarcode/generate` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 (read-only: nothing was saved, split, approved or rejected) |
| Screenshot | `evidence/generate_barcode.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Organization Branch | Select2; 'Head Office [ BDHO ]'. | `page.locator("#office")` | "Organization Branch:" | VERIFIED |
| 2 | Source Of Fund | 290 options; first option text is 'Select Source of Fund' (no dashes, unlike other screens). | `page.locator("#sourceOfFund")` | "Source Of Fund:" | VERIFIED |
| 3 | Asset Serial | Free text. | `page.locator("#assetSerial")` | "Asset Serial:" | VERIFIED |
| 4 | Asset Item Name | Free text. | `page.locator("#assetName")` | "Asset Item Name:" | VERIFIED |
| 5 | MRR Number | Free text. | `page.locator("#referenceNo")` | "MRR Number:" | VERIFIED |
| 6 | Asset Group | 31 options. | `page.locator("#faAssetGroup")` | "Asset Group:" | VERIFIED |
| 7 | Asset Category | 48 options. | `page.locator("#faAssetCategory")` | "Asset Category:" | VERIFIED |
| 8 | Asset Sub Category | 84 options. | `page.locator("#faAssetSubCategory")` | "Asset Sub Category:" | VERIFIED |
| 9 | Registration Date From / To | Read-only date inputs with calendar icons. | `#fromDate`, `#toDate` | Registration Date From: / To: | VERIFIED |
| 10 | Project | 1467 options. | `page.locator("#project")` | "Project:" | VERIFIED |
| 11 | Department | Disabled until a Project is chosen. | `page.locator("#department")` | "Department:" | VERIFIED |
| 12 | Employee PIN | Free text. | `page.locator("#employeePin")` | "Employee PIN:" | VERIFIED |
| 13 | Assign Status | ASSIGNED, UNASSIGNED. | `page.locator("#assetAssignStatus")` | "Assign Status:" | VERIFIED |
| 14 | Asset Status | 9 options (SPLIT, IN_USE, DAMAGE, ...). | `page.locator("#status")` | "Asset Status:" | VERIFIED |
| 15 | Building / Floor / Room | Location filters. | `#building`, `#floor`, `#room` | Building: / Floor: / Room | VERIFIED |
| 16 | Warranty Ends Within | Read-only date input. | `#warrantyEndDate` | Warranty Ends Within: | VERIFIED |
| 17 | Search / Reset | Runs / clears the filter. | `get_by_role("button", name="Search")` (onclick `showAssetSerialSearch()`), `#resetUpdate` | Search, Reset | VERIFIED |
| 18 | Default Print Quantity | Number applied to every row when Set is clicked. Placeholder 'Min: 1, max: 99'. | `#defaultPrintValue` | Default Print Quantity: | VERIFIED |
| 19 | Set button | Copies the default quantity into each row's Print Quantity. | `get_by_role("button", name="Set")` (onclick `changeDefaultPrintQuantity()`) | Set | VERIFIED |
| 20 | Generate button | Builds the barcode preview for the ticked rows. | `page.locator("#generateBarcode")` (onclick `generateBarcodeList()`) | Generate | VERIFIED |
| 21 | Select-all checkbox | Ticks every row on the page. | `page.locator("#select_all")` | Checkbox in the grid header | VERIFIED |
| 22 | Row checkbox + Print Quantity | Per-asset tick and quantity (1-99). | row `input[type=checkbox]` and `input[name=defaultPrint]` scoped to the `tr` of the asset serial | Checkbox and number box per row | VERIFIED |
| 23 | Results grid | Columns: checkbox, Profile ID (hidden), SL, Asset Serial, Asset Item Name, Sub Category, Category Name, Project Name, Department, Branch Name (hidden), Employee Pin (hidden), Assigned Employee (hidden), Asset Assign Status, Status, Print Quantity. Records per page: 10 / 20 / 30 / 40 / 50. | `page.locator("#assetSerialGlobalList")` (same id as the Global List grid, different page) | Asset grid | VERIFIED |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Generate Barcode` (`page.get_by_role("link", name="Generate Barcode", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- **Generate verified** (read-only): search the asset serial, tick the row checkbox, type a quantity in `#defaultPrintValue` and click Set (`page.locator("button[name=setDefaultQuantity]")`; do NOT use `get_by_role("button", name="Set")`, it matches six elements) and the row's `input[name=defaultPrint]` shows that number. Clicking `#generateBarcode` opens a **new browser tab** (`context.pages[-1]`, or `context.expect_page()`) with a PDF report at `faAssetReport/generateAssetBarcodeReport?format=PDF&radPdf=1&otherLabelName=asset_name,branch_name,project_name&download...`. The PDF holds one label per print quantity: BRAC logo, branch, project, asset item name, barcode and asset serial. The PDF viewer is not a normal page, so assert on the tab's URL and take a screenshot rather than reading text. No write request is sent. Evidence: `evidence/generate_barcode_preview.png`.
- Differences from the Global List filters: no Registration Type, Employee Name, AAQ Type or Disposal Type filters; the status filter is labelled 'Asset Status' and the dropdown placeholders have no dashes.
- The grid shows 10 rows before any search.
- Evidence: `evidence/generate_barcode.png`.
