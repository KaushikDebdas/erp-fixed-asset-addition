# Asset Serial Split List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_serial_split_list_page.py` → `AssetSerialSplitListPage`; tests in `tests/test_08_asset_serial_split_list.py` |
| Module / menu path | Fixed Asset >> Asset Profile >> Asset Serial Split List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetProfile/showAssetSplitList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 (read-only: nothing was saved, split, approved or rejected) |
| Screenshot | `evidence/asset_serial_split_list.png` |

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
| 9 | Created By | Employee search; placeholder 'Employee Pin No./Name (Min 3 char...)'. | `page.locator("#createdBy")` | "Created By:" | VERIFIED |
| 10 | Approved By | Same employee search, min 3 characters. | `page.locator("#approvedBy")` | "Approved By:" | VERIFIED |
| 11 | Search button | Runs the filter. | `get_by_role("button", name="Search")` (onclick `showAssetSerialSearch()`) | Search | VERIFIED |
| 12 | Reset button | Clears the filter. | `page.locator("#resetUpdate")` (onclick `resetSearchForm()`) | Reset | VERIFIED |
| 13 | Records per page | 10 / 20 / 30 / 50 / 100. | `page.locator("select[name=assetSplitList_length]")` | Records per page | VERIFIED |
| 14 | Results grid | Columns: Split Id (hidden), SL, Asset Split No., Asset Group, Project Name, Department Name, Asset Serial No., Split Into, Remarks, Created By, Status, Approved By, Approval Date. | `page.locator("#assetSplitList")` | List of splits | VERIFIED |

## Notes
- Reach this page by clicking the **Asset Profile** tab in the Fixed Asset menu bar, then the link `Asset Serial Split List` (`page.get_by_role("link", name="Asset Serial Split List", exact=True)`). Direct `page.goto()` to the hash URL is unreliable (same SPA caveat as the Registration pages). Open the module first (`BasePage.open_fixed_asset_module()`), then click.
- Dropdowns are select2: the real `<select>` (ids above) can be driven with `.select_option()`; the visible `#s2id_autogenN` inputs are generated and their numbers change, so never use them as locators.
- Drop-down option counts are as seen on staging on 2026-10-03.
- **New screen, not in the documents** (they describe only Asset Serial Split and its Approval List). It lists the splits made by the user, with their approval status.
- For the test user the list is empty after Search (`No data available in table`): this user has created no splits.
- The Asset Split No. link should open the same read-only popup as the Approval List (`Asset Split View`); not verified here because the list had no rows.
- Evidence: `evidence/asset_serial_split_list.png`.
