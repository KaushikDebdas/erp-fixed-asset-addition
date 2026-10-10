# Asset Registration Pending/Review List (HOFA) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_registration_pending_review_page.py` → `AssetRegistrationPendingReviewPage` |
| Module / menu path | HOFA > Fixed Asset > Registration > Asset Registration Pending/Review List |
| Entry URL | `https://env42.erp.bracits.net/nodef/fixedasset#!faAssetRegistration/hoFixedAssetRegistrationPendingReviewList` |
| Role needed | HOFA acknowledger |
| Last explored | 2026-10-10 |
| Screenshot | passed test screenshots `03_*_pending_in_hofa.png`, `04_*_acknowledged.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Payable Number | filter; takes the Transaction No. of the bill | `get_by_placeholder("Enter Payable Number(Min 3 char...)")` | text box | VERIFIED |
| 2 | Search | runs the filter | `get_by_role("button", name="Search")` | button | VERIFIED |
| 3 | Row | the request | `locator("table tbody tr", has_text=<transaction no>)` | row | VERIFIED |
| 4 | View | opens the request | row `.get_by_text("View", exact=True)` | link | VERIFIED |
| 5 | Acknowledge | acknowledges | `get_by_role("button", name="Acknowledge")` | button | VERIFIED |
| 6 | Toast | success | `.toast-message`: "Asset registration acknowledged successfully." | toast | VERIFIED |

Grid columns: (checkbox), SL, Asset Pending Number, Transaction No, Payable No, Ref. MRR No, Vendor/Supplier/Lessor, Registration Type, Submitted By, Acknowledged By, Status, Payable Posting Date, Attachment, Action. Status filter options: PENDING, ACKNOWLEDGED, APPROVED. Registration Type filter: MRR, AAQ.

## Notes
- A new HOFIN bill is listed as PENDING with Registration Type `AAQ`. After the HOFIN approval the status is APPROVED.
- After Acknowledge the list reloads without the filter and shows other rows too, so the row is always found by Transaction No., never as "the first row".
- HOFIN and HOFA must be connected and on the same business date, otherwise the request is not listed.
