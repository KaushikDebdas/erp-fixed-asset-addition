# Vendor Bill Payable (HOFIN) and its Fixed Asset Details popup — element catalog

| Field | Value |
|---|---|
| Page class | `pages/vendor_bill_payable_page.py` → `VendorBillPayablePage` (login: `pages/hofin_login_page.py` → `HofinLoginPage`) |
| Module / menu path | HOFIN > Vendor > Payable Journal > + Create |
| Entry URL | `https://hofin42.erp.bracits.net/` (sign in), then `/brac/vendor/vendor-bill-payable/add/:payableCreate`; after Add the bill is `/brac/vendor/vendor-bill-payable/edit/<id>`; after Submit `/brac/vendor/vendor-bill-payable/view/<id>` |
| Role needed | HOFIN creator |
| Last explored | 2026-10-10 |
| Screenshot | `evidence/` not saved this time; the passed test screenshots (`reports/<date>/<time>/screenshots/passed/test_asset_*_hofin_hofa_hofin/`) show the popup and the submitted bill |

## Elements

| # | Element | What it is for | Locator (Playwright) | Seen in the page as | Status |
|---|---|---|---|---|---|
| 1 | Sign-in email | HOFIN login | `get_by_placeholder("Your email address")` | placeholder | VERIFIED |
| 2 | Sign-in password | HOFIN login | `get_by_placeholder("Password")` | placeholder | VERIFIED |
| 3 | Login button | submit credentials | `get_by_role("button", name="Login")` | button | VERIFIED |
| 4 | Vendor menu | opens the Vendor menu | `get_by_role("link", name="Vendor")` | link | VERIFIED |
| 5 | Payable Journal | list of bills | `locator('a[href="/brac/vendor/pending-bill-payable-list"]')` | link | VERIFIED |
| 6 | + Create | opens the empty form | `get_by_role("link", name="+ Create")` | link | VERIFIED |
| 7 | Transaction No. | filled when the allocation is added (`VP########`) | `locator("#transactionNo")` | read-only text box | VERIFIED |
| 8 | Date | the business date (read-only); the Bill Date must equal it | `locator("#transactionDate")` | read-only text box `13-09-2026` | VERIFIED |
| 9 | Vendor | supplier | `locator("#vendor input")` (type `SU0006`, option `SU000634 -3DEVs`) | ng-select | VERIFIED |
| 10 | Purchase Method | method | `locator("#purchaseMethod input")` | ng-select, 11 options | VERIFIED |
| 11 | Bill/Invoice No. | bill number, new on every run | `get_by_role("textbox", name="Bill/Invoice No.: *")` | text box | VERIFIED |
| 12 | Bill Date | read-only box that opens a calendar | `locator("#billDate")` | `dd-mm-yyyy` | VERIFIED |
| 13 | Calendar | pick the day | `bs-datepicker-navigation-view button.previous`, `button.current` (first = month, second = year), `bs-days-calendar-view td[role="gridcell"]:not(.is-other-month) span` | ngx-bootstrap date picker | VERIFIED |
| 14 | Total Bill Amount | bill total | `get_by_role("textbox", name="Total Bill Amount: *")` | text box | VERIFIED |
| 15 | Bank Account | bank | `locator("#bankAccount input")` (type `Gulshan`) | ng-select | VERIFIED |
| 16 | Project | allocation project | `locator("#project input")` (type `015`) | ng-select | VERIFIED |
| 17 | A/C Code | allocation account | `locator("#chartOfAccount input")` (type `Furn`; filled only after a project is chosen) | ng-select | VERIFIED |
| 18 | Purpose | allocation purpose | `locator("#purpose input")` | ng-select | VERIFIED |
| 19 | Allocation Amount | amount (20000 or more for a fixed asset A/C code) | `get_by_role("textbox", name="Amount: *", exact=True)` | text box | VERIFIED |
| 20 | Add (allocation) | saves the bill, shows the Transaction No. and "Fixed Asset Details" | `locator("text=Bill Allocation Details").locator('xpath=following::*[normalize-space(text())="Add"][1]')` | link-button | VERIFIED |
| 21 | Fixed Asset Details | opens the popup | `get_by_text("Fixed Asset Details", exact=True)` | link | VERIFIED |
| 22 | Popup | container | `locator("app-vendor-fixed-asset-modal")` | Angular component, not a `<dialog>` | VERIFIED |
| 23 | Bill Allocation (popup) | one auto-filled option; narrows the parent list | `#budgetAllocation input` | ng-select | VERIFIED |
| 24 | Fixed Asset Addition | tick for an addition | `#isFixedAssetAddition` | check box (no label link) | VERIFIED |
| 25 | Fixed Asset Serial No | parent asset search (shows parent serials only) | `#fixedAssetProfile input`; selected value `#fixedAssetProfile .ng-value-label`; search answer `**listForFixedAssetProfile**search=<serial>&**` | ng-select, server search | VERIFIED |
| 26 | Source Of Fund | fund | `#sourceOfFund input` (first option `USAD`) | ng-select | VERIFIED |
| 27 | Quantity, Unit Price | amounts (auto-set to 1 when addition is ticked) | `#quantity`, `#unitPrice` | text boxes, need key presses | VERIFIED |
| 28 | Asset Item Name | item | `#assetItemName input` (type `Sofa`, option `171798695282-Sofa Set`) | ng-select | VERIFIED |
| 29 | Item Specification | free text | `get_by_placeholder("Eg. XYZ-4523453")` | text box, needs key presses | VERIFIED |
| 30 | Add (popup) | adds the item to the popup list | `app-vendor-fixed-asset-modal a.btn-add` | link-button | VERIFIED |
| 31 | Item row | FAA column `YES` (addition) or `NO` (registration), then the parent serial | `table tbody tr` with the item name; the list also has a "Total" row | row | VERIFIED |
| 32 | Confirm / Yes | confirms; question "Do you want to continue?" | `get_by_role("button", name="Confirm")`, `get_by_role("button", name="Yes")` | buttons | VERIFIED |
| 33 | Submit | submits the bill | `get_by_text("Submit", exact=True)` | link-button | VERIFIED |

## Notes
- Amount, specification, unit price and quantity boxes only work with real key presses (`press_sequentially`); a plain fill leaves "Amount In Words" empty and Add does nothing.
- Add of the Bill Allocation does nothing while the Bill Date is empty ("Bill Date is Required").
- Pressing Escape in the popup closes the whole popup.
- Confirm shows the toast "Transaction drafted!". The success of Submit is checked by the screen changing to `/vendor-bill-payable/view/<id>`; the text "Transaction Submitted Successfully" was not seen in the 2026-10-10 exploration.
- Submit opens a new HOFA tab on the pending registration (`hoAssetPendingId`); the test does not use it.
- HOFIN is slow to open the first time (up to a minute).
- An addition's HOFA row shows a journal voucher number (`JV…`) in the Transaction No. column and the bill number in Payable No.; a registration shows the bill number in Transaction No.
