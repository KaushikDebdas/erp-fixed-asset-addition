# Voucher Search (Accounting module) — element catalog

| Field | Value |
|---|---|
| Page class | `pages/voucher_search_page.py` → `VoucherSearchPage`; PDF reader `utils/voucher_pdf.py`; tests: the full flows of `tests/test_16_asset_expense.py`, `test_approval_creates_the_expense_voucher` in `tests/test_17_asset_expense_approval.py` and the registration voucher test in `tests/test_03_asset_registration_approval_list.py` |
| Module / menu path | Accounting >> Voucher >> Voucher Search |
| Entry URL | `https://erpstaging.brac.net/nodef/accounting#!accJournalMaster/showVoucherSearch` (reach via menu click) |
| Role needed | ERP External User (tested with `abushoaib.asik`; Branch shown in the filter is `2`, Head Office) |
| Last explored | 2026-10-04 (used to check the automatic vouchers of two approved Asset Expenses) |
| Screenshot | `evidence/accounting_home.png`, `evidence/voucher_search_initial.png`, `evidence/voucher_search_result.png`, `evidence/voucher_search_fixed_asset.png`, `evidence/voucher_preview_BBDEXP00000001.png` |

## How to reach it
The Accounting module is a separate module of the same site. From any ERP page click the **Accounting** tab in the top bar (it opens in the **same tab**, address `/nodef/accounting`; no new tab). The menu bar then reads: Admin, Party Management, **Voucher**, Bkash Money, Fund Management, Cash Management, ESP, Final Payment, Report. Click `Voucher`, then the link `Voucher Search` (`page.get_by_role("link", name="Voucher Search", exact=True)`).

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Date From / Date To | Read-only date inputs filled through the calendar icons (the first icon is From, the second is To). Pick the day in the calendar: `page.get_by_role("cell", name="20", exact=True).last` while the calendar is open. | `#fromDate`, `#toDate`; icons `page.locator("[class*=date-image-contr]:visible")` | dd/mm/yyyy | VERIFIED |
| 2 | Voucher Type | Select: Journal Voucher, Credit Voucher, Debit Voucher, Transfer Voucher. | `select#voucherType` | "Voucher Type:" | VERIFIED |
| 3 | Transaction Number | Free text; **an exact match** (a partial value such as `BBDEXP` finds nothing). For an Asset Expense it is the **Expense ID**. | `#transactionNo` (placeholder `E.g. LCA0000005 etc.`) | "Transaction Number:" | VERIFIED |
| 4 | Voucher Number | Free text (placeholder `E.g. DV0000217 etc.`). | `#voucherNumber` | "Voucher Number:" | VERIFIED |
| 5 | Module | Select: Human Resources, procurement, Accounts, Fixed Asset, Microfinance. | `select#module` | "Module:" | VERIFIED |
| 6 | Posted Type / Transaction Type | Radio groups: Posted Type (true / false / none), Transaction Type (auto / manual / none). | `input[name=postType]`, `input[name=autoOrManual]` | radio buttons | VERIFIED (not used) |
| 7 | Search | Runs the search. **The grid fills a moment later**: wait for a row or the "No data available in table" row before reading it. | `get_by_role("button", name="Search")` (onclick `dataTableLoad()`) | Search | VERIFIED |
| 8 | Results grid | Columns: Date, Voucher No., Transaction No, Amount, Particular, Status, Preview. | `page.locator("#tableVouchers")` | "Voucher Search List" | VERIFIED |
| 9 | Preview link (row) | Opens the voucher in a **new browser tab**. | `row.locator("td").last.locator("a")` (onclick `setDataVoucherNo('<VIN>_2','<voucherId>')`) | Preview | VERIFIED |

## Notes
- Typing the Transaction Number with real key presses (`press_sequentially`) was reliable; with only `fill` a search made right after setting the dates once came back empty because the grid had not loaded yet. Always wait for the row.
- A search for `20/09/2026` (the business date, which is the expense's Date of Entry) with Module `Fixed Asset` also lists the vouchers of every asset registration made that day (Transaction No = the registration number, Particular `Furniture and Fixture[4] Registered by AAQ. Asset Item: Cabinet Table`, 25,000).
- **Verified vouchers:** the search row of an approved expense shows `20/9/2026 | <voucher no> | <Expense ID> | 5,000 | Asset Expense Voucher, Reference no: <Expense ID> | Approved | Preview`.

## The Preview (a PDF in a new tab)
- The new tab's address is `https://erpstaging.brac.net/nodef/accJournalMaster/showReportByVoucherNo?format=PDF&voucherNo=<VIN>&organizationBranchId=2&voucherId=<id>`. It is a **PDF viewer**, so the page has no readable text. To read it: take the tab's `url`, close the tab, fetch the same address with the logged-in session (`context.request.get(url)`, status 200, `application/pdf`) and extract the text with **`pypdf`** using `PdfReader(...).pages[0].extract_text(extraction_mode="layout")`. The default extraction order scrambles the columns; layout mode keeps the columns apart.
- **Layout of the voucher:** title `JOURNAL VOUCHER`; branch `[HO - BDHO] Head Office`; `Project: 015 - Microfinance (Dabi)`; `VIN: <voucher no>` with `Creation Date :20/09/2026`; `PVIN: <VIN + 1>` with `Posted Date:20/09/2026`; a table with columns Accounts Code, Heads of Accounts, A/C Sub-Code / MIS Code, Debit, Credit, Particulars; a totals line `Amount (In Word) : Five Thousand  Taka Only   5,000.00   5,000.00`; footer `Prepared By` (the user), `Checked By`, `Approved By` = `Auto Voucher`.
- **Inventory expense (`BBDEXP00000001`, voucher `894315766026145792`):** Debit `5108010101-07 Other Maintenance Expenses` 5,000.00; Credit `1107010401-02 Other Inventory` 5,000.00; Particulars `Asset Expense Voucher, Reference no: BBDEXP00000001` on both lines.
- **Accounts expense (`BBDEXP00000002`, voucher `894316698306678784`):** Debit `5108010101-07 Other Maintenance Expenses` 5,000.00; Credit `2101010301-05 Supplier Payable-Opex` 5,000.00; Particulars `Asset Expense Voucher, Reference no: BBDEXP00000002` on both lines.
- Both agree with the manual: Inventory = Other Maintenance Expenses Dr. / Other Inventory Cr.; Accounts = Other Maintenance Expenses Dr. / Supplier Payable-Opex Cr. (the later manual payment journal, Supplier Payable-Opex Dr. / Cash-Bank Cr., was not part of this check).
- **Quirks found by the automated tests:** (1) The results grid shows its column headings only after a first search. (2) The first cell of every result row is a hidden voucher id; read visible cells only (`td:visible`), so the date is the first visible cell. (3) The Date From / Date To calendars can fail to open if the icon is clicked as soon as the page appears; wait for the page to settle and click the icon again if the calendar does not open, and let each calendar close before opening the next. (4) Open Voucher Search from another module (the page object goes through the Fixed Asset module first) so it is built fresh every time.
- **Automation:** `read_voucher_text` and `parse_voucher` in `utils/voucher_pdf.py` turn the Preview PDF into values (title, branch, project, voucher number, dates, the account lines with debit and credit, totals, amount in words, references). `test_18_voucher_search.py` was removed (2026-10-08). The voucher check of both expense sources is in the full flows of `test_16` and in `test_17`.

## Vouchers of approved Asset Registrations (checked 2026-10-06)
- Searching by the **Registration Number** as the Transaction No finds one voucher per approved registration, with **no date range set**. A search with the Date From / Date To calendars set to the registration's Approval Date (20/09/2026) found some vouchers (building, laptop, Land) but not the furniture ones (758088, 758093), while the same search with no dates found them. So the test searches by number only and checks the date shown on the voucher.
- Search row: `20/9/2026 | <voucher no> | <Registration Number> | 25,000 | <Group>[<id>] Registered by AAQ. Asset Item: <item name> | Approved | Preview`. The Particular groups seen: `Furniture and Fixture[4]` (Cabinet Table), `Land[34359738369]`, `Building[34359738371]`, `Computer/Laptop[34359738377]`.
- Preview PDF (JOURNAL VOUCHER, `[HO - BDHO] Head Office`, `Project: 015 - Microfinance (Dabi)`, Creation and Posted Date = the approval date). Two lines of 25,000.00, debit and credit. The credit line's Particulars end with `Asset Registration by AAQ, Reference no: <Registration Number>`, which ties the voucher to the registration; General Particulars `Asset Registration by AAQ`; Approved By `Auto Voucher`.
- Debit accounts: Furniture `1202010501-01 Furniture and Fixture`, Land `1202010101-01 Land`, Building `1202010201-01 Building`, Laptop `1202010701-01 Computer and IT Equipment`.
- Credit account: **Spot Purchase** `2101010301-06 Supplier Payable-Capex` (as the manual says). **Gift Item** `4202010101-16 Other Income` (verified on staging for all four items; the manual and the flowchart describe only the Spot Purchase voucher).
- Automation: `VoucherSearchPage.verify_registration_voucher` and `build_registration_voucher` (`test_data/asset_registration_data.py`); the 8 tests are `test_approval_creates_the_registration_voucher` in `tests/test_03_asset_registration_approval_list.py`.
- **Before approval there is no voucher** (checked 2026-10-06): a search by the Registration Number of a Draft registration (758092, 758097) or of a registration that is still PENDING (758098, 758099) lists nothing. Test: `test_no_voucher_before_approval` in `tests/test_03_asset_registration_approval_list.py`.
