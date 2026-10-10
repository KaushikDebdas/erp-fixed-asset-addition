# Approve Transaction list (HOFIN) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/hofin_approval_page.py` → `HofinApprovalPage` |
| Module / menu path | HOFIN > Approval > Approval |
| Entry URL | `https://hofin42.erp.bracits.net/brac/workflow-transaction/list`; a bill opens at `/brac/vendor/vendor-bill-payable/workflow/<id>` |
| Role needed | HOFIN approver |
| Last explored | 2026-10-10 |
| Screenshot | passed test screenshots `05_*_waiting_for_approval.png`, `06_*_approved.png` |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Approval menu | opens the menu | `locator("a", has_text="Approval").first` | link | VERIFIED |
| 2 | Approval | the list | `locator('a[href="/brac/workflow-transaction/list"]')` | link | VERIFIED |
| 3 | Feature | required filter, option `Vendor Bill Payable-Vendor` (type `bill`) | `locator("#feature input")` | ng-select | VERIFIED |
| 4 | Status | filter: SUBMITTED, REVIEWED, RECOMMENDED, APPROVED, REJECTED, SENT BACK, PAID/RECEIVED | `locator("#status input")` | ng-select | VERIFIED |
| 5 | Transaction Number | filter | `get_by_placeholder("Transaction Number")` | text box | VERIFIED |
| 6 | Search | runs the filter | `locator("a.btn-search")` | link, not a button | VERIFIED |
| 7 | Action | opens the bill | row `.get_by_role("button", name="Action")` | button | VERIFIED |
| 8 | Approve | approves | `locator("button.btn-info").filter(has_text="Approve")` | button; `get_by_role(name="Approve")` does not find it | VERIFIED |
| 9 | SendBack, Preview, Back | other buttons of the bill screen | not used | buttons | seen |

Grid columns: Feature Name, Trans. No, Trans. Date, Payment Type, Amount, Performed By, Action Date, Status, Money Receipt, FA Acknowledge, Preview, Activity, Particular.

## Notes
- Without the Feature filter the search finds nothing. A bill waiting for approval shows Status SUBMITTED and FA Acknowledge `Yes` once HOFA has acknowledged it.
- After Approve the page returns to this list. No toast was seen. The row is listed with Status APPROVED when the list is opened again (reload) and searched with Status APPROVED; searching again on the same page can still show "No data available!".
- The approver is a different login from the creator (a different HOFIN user).
