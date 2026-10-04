# Asset Expense Approval — element catalog

| Field | Value |
|---|---|
| Page class | `pages/asset_expense_approval_page.py` → `AssetExpenseApprovalPage`; tests in `tests/test_16_asset_expense.py` (full flows) and `tests/test_17_asset_expense_approval.py` |
| Module / menu path | Fixed Asset >> Asset Expenditure >> Asset Expense Approval |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetExpense/showAssetExpenseApproval` (reach via menu click) |
| Role needed | ERP External User (tested with `abushoaib.asik`) |
| Last explored | 2026-10-04 (two expenses approved, one per expense source) |
| Screenshot | `evidence/asset_expense_approval_initial.png`, `evidence/asset_expense_approval_searched.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Status filter | Select: `PENDING`, `APPROVED`, `REJECTED`, `SENDBACK` (no DRAFT). | `select#status` | "Status:" | VERIFIED |
| 2 | Entry From / To Date | Read-only inputs with calendar icons. | `#fromDate`, `#toDate` | "Entry From Date:", "Entry To Date:" | VERIFIED |
| 3 | Search / Reset | Runs / clears the filter. | `get_by_role("button", name="Search")` (onclick `searchAssetExpenseApprovalList()`), `#resetUpdate` | Search, Reset | VERIFIED |
| 4 | Results grid | Columns: checkbox, SL, Expense ID, Entry Date, Supplier, Expense Amount, Status, Created By, Approved By, Approve Date. Empty on 2026-10-04. | `page.locator("#editExpenseTable")` | "List of Asset Expense Approval" | VERIFIED |
| 5 | Row checkbox | Selects an expense for the bulk Approve button. | `row.locator("input[type=checkbox]")` (a header checkbox also exists, `input[name=status]`) | checkbox | VERIFIED locator; no rows to try |
| 6 | Approve button | Approves the ticked expenses. | `get_by_role("button", name="Approve")` (onclick `approveAssetExpense()`) | Approve | VERIFIED locator; not clicked |

## Notes (verified)
- **Match the row by the stored Expense ID** (`row = page.locator("#editExpenseTable tbody tr", has_text="<Expense ID>")`): other users' pending expenses can appear in the same list. The grid cells are: checkbox, SL, hidden id, Expense ID link, Entry Date, Supplier, Expense Amount, Expense Ref., ..., Status, Created By, Approved By, Approve Date, Remarks.
- **Expense ID link** opens the same popup as the list, read-only (every field `RO`, matching what was entered: Date of Entry, Total Expense Amount, Expense Ref., Remarks, asset grid), with three decision buttons: **Approve** `#approveBtn` (onclick `approveAssetExpense()`), **Reject** `#rejectBtn` (`rejectAssetExpense('REJECTED')`), **Sendback** `#sendbackBtn` (`rejectAssetExpense('SENDBACK')`), and Close. Reject and Sendback were not clicked.
- **Approve** from the popup: the toast starts `Asset Expense approved successfully.` (for the Inventory expense it continued with a second line `Journal voucher submitted successfully.`), the popup closes, and the row is APPROVED with Approved By and Approve Date filled in, in both this list and the Asset Expense list. Verified for Inventory (`BBDEXP00000001`) and Accounts (`BBDEXP00000002`).
- The page-level Approve (`approveAssetExpense()` with the row checkboxes) is not a normal `<button>`; it was not used. The row checkbox is `input.optionVal`.
- Per the manual, on Approve an automatic journal is posted: Inventory gives Other Maintenance Expenses Dr. / Other Inventory Cr.; Accounts gives Other Maintenance Expenses Dr. / Supplier Payable-Opex Cr., and a manual journal in the Accounting module is needed later to pay the supplier. The journal itself was not inspected; only the toast `Journal voucher submitted successfully.` was seen for Inventory.
- **Timing quirk:** when an expense is opened from this list its Debit A/C and Credit A/C drop-downs fill in a moment after the Expense Ref.; wait for their `selectedIndex` to be above 0 before reading them. The page object does this in `open_expense`.
- **Automation:** `tests/test_17_asset_expense_approval.py` (3 read-only tests: columns and status values, filter by APPROVED, the popup of an approved expense is read-only) and the approval step of the four full flows in `test_16`. Approve is checked by the message starting `Asset Expense approved successfully.`, then the row must read APPROVED in both lists.
