# Asset Assign Acknowledgement — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_assign_acknowledgement_page.py` → `AssetAssignAcknowledgementPage` (works in the assigned employee's tab, fixture `assignee_logged_in_page`); tests in `tests/test_15_asset_assign_acknowledgement.py` and `tests/test_15_asset_assign_acknowledgement_new.py` (saved Furniture asset, acknowledgement made pending by `utils/transaction_helper.py`) |
| Module / menu path | Fixed Asset >> Asset Transaction >> Asset Assign Acknowledgement |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransaction/showAcknowledgementList` (reach via menu click) |
| Role needed | **The assigned employee**, a different login from the user who creates the assignment. Tested with the second user from `.env` (`ASSIGN_USER_USERNAME`, `ASSIGN_USER_PASSWORD`, read from `config/settings.py`), who is employee `00015370` (Sachindra Nath Ghosh). |
| Last explored | 2026-10-04 (acknowledgement of one test asset was actually performed) |
| Screenshot | `evidence/asset_assign_ack_initial.png`, `asset_assign_ack_details.png`, `asset_assign_ack_details_target.png`, `asset_assign_ack_after_ack.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Pending grid | Approved assignments waiting for the logged-in employee. Columns: checkbox, SL, Transaction Type, Project, Branch, Assigned Employee (`[PIN] NAME`), Assigned By (`[username] name`), Approval Date, Details (plus a per-row `Approve` button, see below). There is **no filter and no Search button** on this screen. | `page.locator("#assetAcknowledgementList")` | "Pending Asset Acknowledgement" | VERIFIED |
| 2 | Row checkbox | Selects an assignment for the header Acknowledge button. Its value is the transaction id. | `row.locator("input.assetCheckbox")` (all share `id="assetTransaction"`, `name="assetTransaction"`) | checkbox, first column | VERIFIED (not used) |
| 3 | Select-all checkbox | Ticks every pending row. **Do not use it on a shared environment: it also ticks assignments made by other people.** | `page.locator("#selectAllCheckbox")` | checkbox in the header | VERIFIED (not used) |
| 4 | Details link (row) | Opens the read-only transaction popup. | `row.get_by_role("link", name="Details")` (onclick `openAssetDetailsModal(<id>)`) | Details | VERIFIED |
| 5 | Per-row Approve button | A small blue button at the end of each row, onclick `singleApprove('<id>', ...)`. Its label is `Approve` but it sits on the acknowledgement list; not clicked. | `row.get_by_role("button", name="Approve")` | Approve | VERIFIED locator; not clicked |
| 6 | Acknowledge button (page) | Acknowledges all ticked rows. | `page.locator("#btnAcknowledgement")` outside the popup (onclick `submit()`) | Acknowledge | VERIFIED locator; not clicked |
| 7 | Details popup | Same read-only popup as the Transaction List (`Asset Transaction Details (Assign/UnAssign/Internal Movement)`): `#assetTransactionType`, `#initiatedBy`, `#branch`, `#assignedEmployee`, `#assignedEmployeePinNo`, `#transactionDate`, `#oldTransactionStatus` (shows `APPROVED`), `#remarks`, `#approvedBy`, `#approvalDate`, and the asset grid `#transactionDetailsList` (SL, Asset Serial, Asset Item Name, Sub Category, Category, Project Name, Department Name, Assign Status, Assigned Before Approval, Utilization Status). The grid fills a few seconds after a spinner. | `page.locator(".modal.in")` | popup | VERIFIED |
| 8 | Acknowledge button (popup) | Acknowledges this one assignment. Shows the toast `Acknowledged successfully`, closes the popup, and removes the row from the Pending grid. | `page.locator(".modal.in #btnAcknowledgement")` (onclick `acknowledgedTransaction()`) | Acknowledge | VERIFIED |
| 9 | My Assigned Asset grid | The assets the employee has acknowledged. Columns: SL, Asset Serial, Asset Item Name, Branch Name, Project Name, Building Name, Floor Name, Room Name, Assigned Employee, Assigned By, Utilization Status. Empty (`No data available in table`) until something is acknowledged. | `page.locator("#afterAssetAcknowledgemenedtList")` (sic) | "My Assigned Asset" | VERIFIED |
| 10 | Records per page | 10 / 20 / 30 / 50 / 100 for each grid. | `select[name=assetAcknowledgementList_length]`, `select[name=afterAssetAcknowledgemenedtList_length]` | Records per page | VERIFIED |

## Notes
- Reach the page with the **assigned employee's** login: open the module with `BasePage.open_fixed_asset_module()`, click the `Asset Transaction` tab, then `page.get_by_role("link", name="Asset Assign Acknowledgement", exact=True)`. The user who created the assignment cannot see these rows.
- **Verified flow** (test asset `BBDASR00227775`): the main user registered and approved an asset, then assigned it to `00015370` and approved the assignment. The assigned user logged in, opened this screen (7 rows pending), clicked **Details** on the row whose asset list held the serial, saw Transaction Type `ASSIGN`, Initiated By `Abu Shoaib Asik`, employee `00015370`, status `APPROVED` and the note, and clicked **Acknowledge** in the popup. Toast: **`Acknowledged successfully`**. Afterwards the Pending grid had 6 rows and My Assigned Asset showed the asset.
- Because nobody had acknowledged earlier assignments, the pending list also held our older test assets and **two real laptops assigned by another person** (`BBDASR00224213`, `BDHO-0099-001685`). Always find the row by the serial inside its Details popup and acknowledge only that one; never use select-all.
- After acknowledgement the transaction **still shows `APPROVED`** in the Transaction List and Transaction Approval List; the `ACKNOWLEDGED` status filter exists but returned no rows. The asset's Asset Profile (Asset Serial Global List) is unchanged by acknowledgement (Assign Status `ASSIGNED`, Assigned Date empty before and after).
- In a pending row the visible cells are: checkbox (0), SL, Transaction Type, Project, Branch, Assigned Employee (5), Assigned By, Approval Date, Details. In My Assigned Asset the Asset Serial is the second visible cell.
- A POST to `faAssetTransaction/showAcknowledgementList` follows the click (the grids reload).
