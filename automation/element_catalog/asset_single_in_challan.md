# Asset Single In-Challan — element catalog

| Field | Value |
|---|---|
| Page class | `pages/single_in_challan_page.py` → `SingleInChallanPage` (inherits `SingleChallanListPage`); tests in `tests/test_25_asset_single_in_challan.py` |
| Module / menu path | Fixed Asset >> Single Challan >> Asset Single In-Challan |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetSingleChallan/showInChallan` |
| Role needed | one user does everything for now (the logged-in `TEST_USERNAME`); Acknowledge worked for it in the test run. Tried by hand in the exploration browser with `abushoaib.asik` and with `00015370`: Acknowledge failed with the toast `Api error - User not found` for both |
| Last explored | 2026-10-08 |

## Elements
The filters (plus Acknowledged By `#acknowledgedBy`), the grid and the challan popup are the ones in `asset_single_out_challan.md`.

| # | Element | Locator | Status |
|---|---|---|---|
| 1 | Acknowledge button (popup; the only action) | `#acknowledge` | VERIFIED (test run: status becomes ACKNOWLEDGED, Preview link appears) |
| 2 | Loading overlay after Acknowledge | `.modalLoader` | as on Asset Shipment In-Challan |

## Notes
- An approved challan is listed here with status APPROVED and an In Challan Number but no Preview; after Acknowledge it is ACKNOWLEDGED with a Preview link and an Acknowledged By.
- Like the shipment In-Challan, no message is checked; the tests search again and read the row Status.
