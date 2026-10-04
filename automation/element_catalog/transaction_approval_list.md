# Transaction Approval List (Assign / Un Assign / Internal Movement) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/transaction_approval_list_page.py` → `TransactionApprovalListPage` (form screens share `pages/asset_transaction_form_page.py`, grids share `pages/transaction_grid_page.py`); tests in `tests/test_14_transaction_approval_list.py` |
| Module / menu path | Fixed Asset >> Asset Transaction >> Transaction Approval List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransaction/showList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 |
| Screenshot | `evidence/transaction_approval_initial.png`, `transaction_approval_searched.png`, `transaction_approval_details_loaded.png`, `transaction_approval_after_approve.png`, `internal_movement_approval_details.png`, `unassign_approval_details.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Filters | Same as the Transaction List: `#assetTransactionType` (ASSIGN, UNASSIGN, TRANSFER), `#fromDate`, `#toDate`, `#createdBy` (**empty here**, unlike the Transaction List), `#assetTransactionStatus` (PENDING, APPROVED, REJECTED, SENDBACK, ACKNOWLEDGED, no DRAFT), `#approvedBy`. | ids as listed | same labels | VERIFIED |
| 2 | Search / Reset | Runs / clears the filter. | `get_by_role("button", name="Search")` (onclick `searchAssetTransaction()`), `#resetUpdate` | Search, Reset | VERIFIED |
| 3 | Results grid | Shows all users' transactions (10 rows per page by default, newest first). Columns: (hidden id), SL, Details, Transaction Type, Transaction Date, Branch, Created By, Approved By, Approval Date, Transaction Status. No Edit column and no checkboxes. | `page.locator("#assetTransactionList")` | Approval List grid | VERIFIED |
| 4 | Details link (row) | Opens the approval popup. | `row.get_by_role("link", name="Details")` | Details | VERIFIED |
| 5 | Comment | Optional text for the decision. | `page.locator(".modal.in #comment")` (placeholder `Leave comment here..`); date `#commentDate` read-only | Comment: | VERIFIED |
| 6 | Approve | Approves the transaction; popup closes. | `page.locator("#btnApproved")` (onclick `approveTransaction()`) | Approve | VERIFIED |
| 7 | Reject | Rejects it. | `page.locator("#btnReject")` (onclick `rejectTransaction()`) | Reject | VERIFIED locator; not clicked |
| 8 | Sendback | Sends it back to the creator. | `page.locator("#btnSendBack")` (onclick `sendBackTransaction()`) | Sendback | VERIFIED locator; not clicked |

## Notes
- Reach the page by clicking the **Asset Transaction** tab and then the link `Transaction Approval List` (`page.get_by_role("link", name="Transaction Approval List", exact=True)`), after opening the module with `BasePage.open_fixed_asset_module()`. Direct navigation to the hash address is unreliable.
- The Details popup is the same read-only popup as in the Transaction List (same ids and Assets grid), plus Comment, Approve, Reject, Sendback and Close.
- Verified for all three types with test asset `BBDASR00227766`: the popup values matched the saved transaction (type, Initiated By, branch, employee name and PIN, transaction date, remarks, status `PENDING`, asset serial and `Assign Status`). **Approve** shows the toast `Approved successfully`, closes the popup, and the row then shows `APPROVED` with Approved By and Approval Date filled in.
- Effects after Approve (checked in Asset Profile): Assign makes the asset `ASSIGNED` to the chosen employee (no acknowledgement step was needed); Internal Movement sets its Building `Head Office` and Floor `12th floor`; Un Assign makes it `UNASSIGNED`.
- The popup of an **APPROVED** transaction has no Comment box and no Approve button; the decision section only appears for PENDING ones.
- The filter drop-downs and the popup both contain an element with id `#assetTransactionType`; match the filter as `select#assetTransactionType`.
- Filter by type and status `PENDING` to find the row: on a busy environment other users' pending items also appear here.
