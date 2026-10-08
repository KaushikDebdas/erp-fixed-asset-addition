# Asset Sale (Create) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_sale_page.py` → `AssetSalePage` (inherits `AssetWriteOffPage`); tests in `tests/test_30_asset_sale.py`, step in `utils/sale_flow.py` |
| Module / menu path | Fixed Asset >> Asset Disposal >> Asset Sale |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetDisposalSale/show` (reach via menu click) |
| Role needed | a user with the disposal permission (explored and tested with `00015370`) |
| Last explored | 2026-10-08 |
| Screenshot | `evidence/asset_sale_initial.png` |

## Elements
The form is the same as Asset Write-off (see `asset_write_off.md`) with these differences.

| # | Element | What it is for | Locator (Playwright) | Status |
|---|---|---|---|---|
| 1 | Project | `#project`, choose `[015] Microfinance (Dabi)`. | `page.locator("#project")` | VERIFIED |
| 2 | Asset Serial | Search drop-down `#s2id_asset .select2-choice`; type the **exact serial** (or item name), click the result. It offers IN_USE assets that are UNASSIGNED and in no pending process (an asset in a pending Asset Split or a Draft/Pending write-off or sale gives "No matches found"). | `.select2-drop-active input.select2-input`, `.select2-drop-active .select2-results li` | VERIFIED |
| 3 | Auto-filled fields | `#assetName`, `#assetSubCategory`, `#assetCategory`, `#assetGroup`, `#disposalType` (the asset's status, `IN_USE`), `#unitPrice`, `#addition`, `#depreciatedValue`, `#writtenDownValue` (25000 for the AAQ test assets). | ids as listed | VERIFIED |
| 4 | Sale Value | Required. | `#saleValue` | VERIFIED |
| 5 | Note | `#remarks`. | `#remarks` | VERIFIED |
| 6 | Add to Grid / grid | Grid columns: SL, Profile ID, Asset Serial, Asset Item Name, Asset Project Id, Asset Project Name, Unit Price, Addition, Accumulated Depreciation, Written Down Value, **Sale Value**, Note/Remarks, **Profit/Loss**, Action. Profit/Loss = Sale Value − Written Down Value (`5000.00` when sold above, `-5000.00` below). No toast. | `#addToGrid`, `#assetDetailsTable` | VERIFIED |
| 7 | Draft / Submit / Reset | Toasts `Asset sale drafted successfully` and `Asset sale submitted successfully`; the grid and project are then cleared. | `#draft`, `#save`, `#resetEditButton` | VERIFIED (Reset not clicked) |

## Notes
- The screen has **no Receive Type (Cash/Bank) choice** (the PDF describes one); the Sale List shows Receive Type `BANK` for every sale.
- **No status change is needed:** the sale was created with assets still IN_USE (a Cabinet Table, tried in the form). Marking the asset DAMAGE first also works but is not required. An asset must be UNASSIGNED.
- The first sale explored: case 1 Building `BBDASR00228049` sold for 30000 (WDV 25000, profit 5000.00) and case 2 Land `BBDASR00228047` for 20000 (loss -5000.00), both Submitted; two Drafts (Cabinet Table, Laptop) saved the same way. These assets were first set to DAMAGE by hand, which turned out not to be needed.
- The Draft and Pending sales keep the asset in the Asset In Pending Process List (Pending in Feature `Asset Disposal Sale`).
