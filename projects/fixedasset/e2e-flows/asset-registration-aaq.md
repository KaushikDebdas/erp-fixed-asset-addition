# Flow: Asset Registration by AAQ — Draft to Approved Asset Serial

**Business scenario:** A user registers a newly purchased asset (Spot
Purchase) on the AAQ form, saves it as a Draft, reopens it from the
Asset Registration List and submits it, then reviews and approves it in
the Asset Registration Approval List. A successful approval generates the
**Asset Serial Number**, which is the asset's official identity in the
ERP. Everything runs under **one login** with the same user, because the
staging account can both create and approve, **except the acknowledgement**
(step 18), which the assigned employee does with a second login.

Automated in: `automation/tests/smokesuite_e2e.py`
(`test_asset_registration_aaq_draft_submit_and_approve`, steps 1-31 in the test).
Domain background: `knowledge/erp-fixedasset.md` §2.

| Step | Role/Login | Action | Reference | Data carried forward |
|---|---|---|---|---|
| 1 | ERP External User (`abushoaib.asik`) | Log in once, close the announcement popup if shown | automation-only: login | — |
| 2 | same session | Open Fixed Asset module, then Registration > **Asset Registration by AAQ** | automation-only: navigation | — |
| 3 | same session | Fill the form (Project, Spot Purchase, Purchase Date = Registration Date, Remarks, Vendor, Asset Item, Item Specification, Quantity, Unit Price) and click **Add** | automation-only: create registration | `purchase_date`, `registration_date`, `item_specification` (unique per run) |
| 4 | same session | Click **Draft**; expect toast `Asset registration(AAQ) drafted Successfully!` | automation-only: save as draft | — |
| 5 | same session | Open **Asset Registration List**, filter Status = DRAFT, take the newest row, check Status = DRAFT | automation-only: find the draft | produces `registration_number` |
| 6 | same session | Click the Registration Number link (opens the form as "Update Asset Registration By AAQ"), click **Submit**; expect toast `Asset registration(AAQ) submitted Successfully!` | automation-only: submit from list | consumes `registration_number` |
| 7 | same session | Back in the Asset Registration List, filter Status = PENDING, check the row shows PENDING | automation-only: confirm status | consumes `registration_number` |
| 8 | same session | Open **Asset Registration Approval List**, filter by Registration Number, click the Registration Number link (opens the "Asset Registration View" popup) | automation-only: open for review | consumes `registration_number` |
| 9 | same session | Assert the popup's Registration No equals the number from the list, and every entered value is shown | automation-only: verify details | consumes `registration_number` and the step 3 values |
| 10 | same session | Click **Approve** inside the popup; expect toast `Asset registration approved successfully.` Any other message fails the test | automation-only: approve | consumes `registration_number` |
| 11 | same session | Reopen the registration, open the **Asset Serials** tab, read the serial from the first row, assert it is not empty, and write it to the log | automation-only: capture serial | produces `asset_serial` (e.g. `BBDASR00227761`) |
| 12 | same session | Open **Asset Profile > Generate Barcode**, type the stored `asset_serial` in the Asset Serial box and click **Search** | automation-only: find the asset for barcode | consumes `asset_serial` |
| 13 | same session | Assert the stored `asset_serial` is listed in the results | automation-only: verify the asset is shown | consumes `asset_serial` |
| 14 | same session | Tick the asset's row, set the print quantity to 2 with **Set**, click **Generate**; the barcode PDF opens in a new tab (its address contains `generateAssetBarcodeReport` and `format=PDF`) | automation-only: generate barcode | consumes `asset_serial` |
| 15 | same session | **Asset Assign**: type the stored `asset_serial`, search, pick the suggestion; assert the box starts with the serial and Assigned Status is UNASSIGNED; Add to Grid; search employee PIN `00015370`; add a note; click **Draft**; expect toast `Asset Assign Draft Successfully` | automation-only: assign draft | consumes `asset_serial` |
| 16 | same session | **Transaction List**: open the Draft's **Details**, check the values, click **Edit**, check the form, click **Submit**; expect `Asset Assign Submit Successfully` | automation-only: submit assign | consumes `asset_serial` |
| 17 | same session | **Transaction Approval List**: open **Details**, check the values, **Approve**; expect `Approved successfully`; confirm the row is APPROVED | automation-only: approve assign | consumes `asset_serial` |
| 18 | **assigned employee** (second login, `ASSGN_USER_USERNAME` in `.env`) | **Asset Assign Acknowledgement**: open the screen, note the pending count, **Details** on the row whose asset list holds `asset_serial`, verify the serial, employee and note, click **Acknowledge**; expect toast `Acknowledged successfully`; the pending count drops by one and `asset_serial` appears in **My Assigned Asset** | automation-only: acknowledge assign | consumes `asset_serial` |
| 19 | same session | **Asset Serial Global List**: search `asset_serial`; assert it is listed, Assign Status ASSIGNED, and its popup shows the employee | automation-only: verify ASSIGNED | consumes `asset_serial` |
| 20 | same session | **Asset Internal Movement**: select the serial (Assigned Status must be ASSIGNED), Add to Grid, employee `00015370`, Building `Head Office` and its first floor, note, **Draft**; expect `Asset Internal-Movement Draft Successfully` | automation-only: movement draft | consumes `asset_serial` |
| 21 | same session | Transaction List Details/Edit/**Submit** (`Asset Internal-Movement Submit Successfully`), then Approval List Details/**Approve** (`Approved successfully`) | automation-only: submit and approve movement | consumes `asset_serial` |
| 22 | same session | **Asset Un Assign**: select the serial, Add to Grid, hand over to employee `130276` (`00130276`, a different employee from the holder), note, **Draft**; expect `Asset Un-Assign Draft Successfully` | automation-only: unassign draft | consumes `asset_serial` |
| 23 | same session | Transaction List Details/Edit/**Submit** (`Asset Un-Assign Submit Successfully`), then Approval List Details/**Approve** (`Approved successfully`) | automation-only: submit and approve unassign | consumes `asset_serial` |
| 24 | same session | **Asset Serial Global List**: search `asset_serial`; assert it is listed and Assign Status is UNASSIGNED | automation-only: verify UNASSIGNED | consumes `asset_serial` |
| 25 | same session | **Asset Expense** (source **Inventory**): Create, select `asset_serial`, expense amount `5000` and **Add**, then Expense Source `Inventory`, Category `Furniture`, Sub Category `Wooden Furniture`, Item `Cabinet Table`, Debit A/C `Other Maintenance Expenses[5108010101-07]` (Credit A/C fills in as `Other Inventory`), vendor `ACE IT[P008937]`, a random Expense Ref. (`EXP` + six digits), remarks, then **Draft**; expect toast `Asset expense successfully drafted.`; store the generated **`expense_id`** (`BBDEXP...`) | automation-only: expense draft | consumes `asset_serial`; produces `expense_id` |
| 26 | same session | Open the Draft by `expense_id`, check the saved values, **Submit**; expect `Asset expense successfully submitted.`; the row becomes PENDING | automation-only: submit expense | consumes `expense_id` |
| 27 | same session | **Asset Expense Approval**: find the PENDING row by `expense_id`, check the read-only popup, **Approve**; expect a message starting `Asset Expense approved successfully.`; the row is APPROVED in both lists | automation-only: approve expense | consumes `expense_id` |
| 28 | same session | **Accounting > Voucher > Voucher Search**: same date in Date From and Date To, Transaction Number = `expense_id`, Search; check the row (`Asset Expense Voucher, Reference no: <expense_id>`, 5,000, Approved); **Preview** opens a PDF in a new tab, read with `pypdf`: Journal Voucher, branch `[HO - BDHO] Head Office`, project `015 - Microfinance (Dabi)`, Other Maintenance Expenses Dr. 5,000.00 / Other Inventory Cr. 5,000.00, totals equal, reference = `expense_id` | automation-only: verify voucher | consumes `expense_id` |

**Automation Suitable:** Yes — one repeatable single-role journey whose
every step has a verified locator and an exact expected message.

---
## Order matters
The Internal Movement (step 20) must come **before** the Un Assign (step 22): once an Un Assign is submitted the asset is locked in a pending process and every transaction screen answers `No asset found` for it.
The serial number only exists **after** a successful Approve. The test
reads it in step 11, never earlier. Before approval the Asset Serials
grid is empty ("No data available in table").

## Where to find things
| What | Where |
|---|---|
| Test (full journey) | `automation/tests/smokesuite_e2e.py` |
| One test file per screen | `test_01_asset_registration_aaq.py`, `test_02_asset_registration_list.py`, `test_03_asset_registration_approval_list.py` |
| Page objects | `automation/pages/asset_registration_aaq_page.py`, `..._list_page.py`, `..._approval_list_page.py` |
| Shared test data | `automation/test_data/asset_registration_data.py` |
| Locators and screen notes | `automation/element_catalog/asset_registration_*.md` |
| Run one file | `python -m pytest tests/smokesuite_e2e.py -v` (from the `automation` folder) |
| Report and log | `automation/reports/<date>/<time>/Test_Report_*.html`, `automation/logs/test_run.log` |

## Rules and behaviours learned (verified on staging)
- After login the user lands on the ERP home page, not the module. The
  code opens `/nodef/fixedasset` first, then **clicks** the Registration
  menu (hover does not open it).
- Every menu navigation starts from a freshly loaded module, so each
  screen opens as a clean form.
- Draft needs the same fields as Submit: Purchase Date, Vendor and at
  least one asset line. Toasts seen: `Please Select Purchase Date.`,
  `Please Select a supplier.`, `No Asset in List to perform operation`
  (no full stop).
- A line totalling under 20,000 Taka is rejected:
  `Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka.`
- Toasts fade slowly, so the code waits for the previous toast to clear
  before each Draft, Submit or Approve and then reads the new one.
- The Registration List does not show the number of the Draft just
  saved, so the newest number in the DRAFT filter is used (numbers only
  increase).
- A reopened Draft fills in after the page appears; the code waits for
  the saved Project before clicking Submit.
- In the popup, header fields are input boxes and long text is cut off
  ("...more"), so the check reads input values and compares the first 30
  characters of the Item Specification.
- Grids have a hidden first column (ID), so Status is the 10th cell in
  the Registration List and Asset Serial is the 3rd cell in the Asset
  Serials grid.
- **The project decides whether Approve works.** The test data uses
  `[015] Microfinance (Dabi)`, and Approve succeeds for it. Earlier runs
  with `[C04] Administratiion` and `[801] EHC` were refused with
  `No Area Current Account Code: This branch is not mapped with project`,
  because those projects have no Area Current Account Code mapped for the
  Head Office branch. If another project is used and Approve is refused,
  the test fails on the toast check, which is correct. The asset's
  project in Asset Profile matches the project chosen on the AAQ form.

## Notes for the Automation Engineer
- One browser context per distinct role. This flow has a single role, so
  one tab is used for the whole journey.
- Pass `registration_number` and `asset_serial` as variables between
  steps; never hardcode them.
- Steps execute in the order listed. Do not reorder.
- Each run creates a new registration on staging.

## Why the expense is last
An Asset Expense is not offered for an asset that has a transaction still pending, and a submitted Un Assign locks the asset until it is approved. The expense (rows 25-28) therefore comes after the Un Assign is approved. Only the Inventory source saved as a Draft is in this smoke flow; the Accounts source and the direct-Submit path are covered by the regression tests in `tests/test_16_asset_expense.py`.
