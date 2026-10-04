# Transaction List (Assign / Un Assign / Internal Movement) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/transaction_list_page.py` → `TransactionListPage` (form screens share `pages/asset_transaction_form_page.py`, grids share `pages/transaction_grid_page.py`); tests in `tests/test_13_transaction_list.py` |
| Module / menu path | Fixed Asset >> Asset Transaction >> Transaction List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransaction/editList` (reach via menu click, see Notes) |
| Role needed | ERP External User (tested with `abushoaib.asik`, branch Head Office [ BDHO ]) |
| Last explored | 2026-10-03 |
| Screenshot | `evidence/transaction_list_initial.png`, `transaction_list_searched.png`, `transaction_list_details.png`, `transaction_list_edit.png`, `unassign_list_details.png`, `internal_movement_list_details.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Transaction Type | Select. Options `ASSIGN`, `UNASSIGN`, `TRANSFER` (TRANSFER = Internal Movement). | `page.locator("#assetTransactionType")` | "Transaction Type:" | VERIFIED |
| 2 | From Date / To Date | Read-only inputs filled through the calendar icons. | `#fromDate`, `#toDate` | dd/mm/yyyy | VERIFIED |
| 3 | Created By | Employee search box; **prefilled with the logged-in user** (`abushoaib.asik-Abu Shoaib Asik`), so the list shows only that user's transactions until cleared. | `page.locator("#createdBy")` | "Created By:" | VERIFIED |
| 4 | Transaction Status | Select. Options `PENDING`, `APPROVED`, `REJECTED`, `DRAFT`, `SENDBACK`, `ACKNOWLEDGED`. | `page.locator("#assetTransactionStatus")` | "Transaction Status:" | VERIFIED |
| 5 | Approved By | Employee search box, min 3 characters. | `page.locator("#approvedBy")` | "Approved By:" | VERIFIED |
| 6 | Search / Reset | Runs / clears the filter. | `get_by_role("button", name="Search")` (onclick `searchAssetTransaction()`), `#resetUpdate` | Search, Reset | VERIFIED |
| 7 | Results grid | Columns: (hidden transaction id), SL, Details, Edit, Transaction Type, Transaction Date, Branch, Created By, Approved By, Approval Date, Transaction Status. | `page.locator("#assetTransactionList")` | Transaction List grid | VERIFIED |
| 8 | Details link (row) | Opens the read-only **Asset Transaction Details (Assign/UnAssign/Internal Movement)** popup. Present on every row. | `row.get_by_role("link", name="Details")` (onclick `showAssetTransactionDetailsPopup(<id>)`) | Details | VERIFIED |
| 9 | Edit link (row) | Opens the original Assign / Un Assign / Internal Movement form pre-filled. Only DRAFT (and SENDBACK) rows have it. | `row.get_by_role("link", name="Edit")` (onclick `showAssetTransactionForEdit(<id>)`) | Edit | VERIFIED |

## Notes
- Reach the page by clicking the **Asset Transaction** tab and then the link `Transaction List` (`page.get_by_role("link", name="Transaction List", exact=True)`), after opening the module with `BasePage.open_fixed_asset_module()`. Direct navigation to the hash address is unreliable.
- Cell positions: a hidden transaction-id column comes first, so Details is the 3rd cell and the Status is the 10th (index 9).
- **Details popup** (`.modal.in`, title `Asset Transaction Details (Assign/UnAssign/Internal Movement)`): read-only `#assetTransactionType`, `#initiatedBy`, `#branch` (Organization Branch), `#floor`, `#assignedEmployee`, `#assignedEmployeePinNo`, `#assignedDate` (Created Date, the real date), `#transactionDate` (business date), `#oldTransactionStatus`, `#building`, `#room`, `#approvedBy`, `#approvalDate`, `#remarks`. A **List of Assets** grid `#transactionDetailsList` (SL, Asset Serial, Asset Item Name, Sub Category, Category, Project Name, Department Name, Assign Status, Assigned Before Approval, Utilization Status) fills in a few seconds after a spinner (wait for the serial's row, up to about 30 s). The only button is `Close`.
- **Edit** shows the original form with the saved values: for the Assign draft it held Employee PIN `00015370`, name, branch `Head Office [ BDHO ]` and the note exactly as entered; the asset sits in the Asset List grid. Click `Submit` (`#save`) there: toasts `Asset Assign Submit Successfully`, `Asset Internal-Movement Submit Successfully`, `Asset Un-Assign Submit Successfully`. After Submit the row's status becomes PENDING and the Edit link disappears.
- The page shows a loading spinner after Edit and after Details: wait for the values, not a fixed time.
- Evidence of the full path (Assign, Internal Movement, Un Assign) is in the screenshots named in the header.
