# Asset Registration List — element catalog

| Field | Value |
|---|---|
| Page class | not yet built |
| Module / menu path | Fixed Asset >> Registration >> Asset Registration List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetRegistration/showList` (reach via menu click — see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`) |
| Last explored | 2026-10-03 (session 2 — Draft/Submit verification) |
| Screenshot | `evidence/asset_registration_list_results.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Organization Branch filter | Select2 dropdown, defaults to user's branch | `page.locator("#office")` | "Organization Branch:" | VERIFIED |
| 2 | Registration Type filter | Select2 dropdown (MRR / AAQ / LEASE) | `page.locator("#registrationType")` | "Registration Type:" | VERIFIED |
| 3 | Vendor/Supplier/Lessor Name filter | Free text | `page.get_by_label("Vendor/Supplier/Lessor Name:")` or CSS near label | "Vendor/Supplier/Lessor Name:" | LOCATOR_REQUIRES_REVIEW (id not captured this session; not needed for the happy-path flow, revisit if a filtered search by vendor is required) |
| 4 | Registration Number filter | Free text — key field for finding the just-created item | `page.locator("#registrationId")` | "Registration Number:" | VERIFIED |
| 5 | Created By filter | Employee search box, auto-filled with the logged-in user's name on this page | `page.locator("#createdBy")` | "Created By:" | VERIFIED |
| 6 | Status filter | Select2 dropdown, options confirmed this session: `-Select Status-`, `PENDING`, `APPROVED`, `REJECTED`, `DRAFT`, `SENDBACK`. Underlying native select is `#status`; trigger is a link ("-Select Status-" or the current value) that must be clicked to open the select2 list before clicking the target `option` by accessible name. | `page.locator("#status")` for `.select_option("DRAFT")`, or via UI: `page.get_by_role("link", {name: "-Select Status-"})` then `page.get_by_role("option", {name: "DRAFT"})` | "Status:" | VERIFIED |
| 7 | Search button | Runs the filter | `page.get_by_role("button", {name: " Search"})` | "Search" | VERIFIED |
| 8 | Reset button | Clears filters | `page.get_by_role("button", {name: " Reset"})` | "Reset" | VERIFIED |
| 9 | Results grid | Lists matching registrations | `page.locator("table")` with header `SL, Registration Number, Registration Date, Reference Number, Registration Type, Project Name, Department Name, Created By, Status, Approved By, Approval Date, Attachment` | "Asset Registration List" grid | VERIFIED |
| 10 | Registration Number link (row) | Opens the registration detail; also the unique row identifier. For a **DRAFT** row, clicking this link opens the SAME create/edit form (heading "Update Asset Registration By AAQ") pre-filled, with Draft/Submit/Reset buttons still available — Submit can be clicked directly to move DRAFT -> PENDING. | `page.get_by_role("link", {name: "<registration number>"})`, e.g. `page.locator('a:has-text("757755")')` | Blue clickable number in first data column | VERIFIED |
| 11 | Row Status cell | Shows DRAFT / PENDING / APPROVED / REJECTED / SENDBACK | `page.locator("tr", {hasText: "<registration number>"}).locator("td").nth(8)` (approx. — column order per header row) | "Status" column value | VERIFIED |

## Verified 2026-10-04 (regression suite run on staging)
- Filters and ids: Organization Branch `#office`; Registration Type `#registrationType` (MRR, AAQ, LEASE); Vendor/Supplier/Lessor Name `#supplierName` (free text); MRR Number `#referenceNo`; Registration Number `#registrationId`; Created By `#createdBy`; Approved By `#approvedBy` (both employee search boxes, Min 3 characters); Project Name & Number `#projectId`; Department Name & Number `#receivingDept`; Status `#status`; read-only date filters `#registrationFromDate`, `#registrationToDate`, `#approveFromDate`, `#approveToDate`. This replaces LOCATOR_REQUIRES_REVIEW on row 3.
- Date filters open a bootstrap-datepicker dropdown on the current business month; pick a day with `.datepicker-dropdown:visible td.day:not(.old):not(.new)`.
- Buttons: Search, Reset `#reset`. **Reset empties every filter box, including Created By, and does not run the search again.**
- Grid `#assetRegistrationList` has 13 columns: SL, Registration Number, Registration Date, Reference Number, Registration Type, Branch Name (hidden column), Project Name, Department Name, Created By, Status, Approved By, Approval Date, Attachment. Status is the 10th (index 9). Newest first by default. Clicking a heading does not sort. SL restarts at 1 on each page.
- Paging: Records per page `select[name=assetRegistrationList_length]` (10, 20, 30, 50, 100); line under the grid `.dataTables_info`, e.g. "Showing 1 to 10 of 124 entries"; page buttons `.paginate_button`.
- Created By starts with the logged-in user ("abushoaib.asik-Abu Shoaib Asik"); emptying it lists everyone's registrations (124 -> 13,501 entries).
- The **MRR Number filter is ignored** by Search (same entries with a real, a made-up or no number).
- The Registration Number link of a PENDING row opens the Asset Registration View popup `#commonModal` (tabs Details and Asset Serials), same as the Approval List.

## Notes
- Confirmed end-to-end (session 1): the AAQ item created in `asset_registration_aaq.md` (Registration Number **757754**) appeared in this list immediately after Submit, with Status = PENDING, Created By = "Abu Shoaib Asik".
- Confirmed end-to-end (session 2 — Draft flow): Registration Number **757755** appeared with Status = **DRAFT** immediately after clicking Draft on the AAQ form (Project `[C04] Administratiion`). It was then opened via its Registration Number link, Submitted, and re-confirmed in this list with Status = **PENDING**. Registration Number **757756** (a second Draft, created purely to capture the verbatim Draft toast text) also appeared here with Status = DRAFT and was left as-is.
- The "Created By" filter box is pre-populated with the logged-in user's own name by default on this page — useful for scoping automated searches to just what the test run created.
- Same SPA hash-routing caveat as the AAQ page: reach this page by clicking `Registration` → `Asset Registration List` in the left menu, not via direct `page.goto()` with a hash fragment.
- Grid cell text for a row is reliably read via `document.querySelectorAll('table tbody tr')` + `.textContent` filtered by the known registration number, then `.querySelector('a')` for the link text — more robust than relying on `get_by_role("link", {name: ...})` alone when the table hasn't finished an AJAX repaint.
