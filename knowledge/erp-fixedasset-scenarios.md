# ERP Fixed Asset — Scenario Guide for Test-Case Writing

| Field | Value |
|---|---|
| Domain / sub-domain | Finance / Fixed Asset (BRAC ERP, staging) |
| Purpose | Fully worked, business-language scenarios (precondition, steps, test data, expected result) for the screens that the automation covers: Registration, Asset Profile and Split, Asset Transaction, Asset Expense and voucher checking, Asset Transfer and Single Challan, Write-off and Sale. **It does not need the automation code to be read or even present.** |
| Scope limit | **This guide does NOT cover every screen.** It has no scenarios for Setup, Offline Assets Receive and Offline Transfer, Addition from Inventory and Vendor, Depreciation, the 13 Reports, Receivable and Returnable lists, Auction, or the Dashboard. For those, and for the rules behind every screen, use the screen sheets in §16 of `knowledge/erp-fixedasset.md` (its coverage map shows which screens have a worked scenario here). |
| Companion | `knowledge/erp-fixedasset.md` — the domain knowledge file: business rules, history, and one test-case reference sheet per screen (§16). Start there; use this guide for step wording on the covered screens. |
| First version | 2026-10-09. Built from the working automation (`test_01` to `test_31`) and its catalogs; nothing was run to write it. |

**Basis tags on every scenario**
- `VERIFIED (test_xx)` — a working automated test performs exactly this. Steps and messages are real.
- `OBSERVED (catalog)` — seen on the live screen during exploration, not part of a test.
- `DERIVED (not yet run)` — a sensible extension of a verified rule (a boundary, a negative variant). Steps follow the verified pattern, but the result was never seen. Confirm on the screen before trusting an exact message.

**Secrets:** logins, PINs and personal names are never written. Use `<ERP Username> / <ERP Password>` and role words.

---

## How to use this guide (when a CR arrives)

0. **First check the coverage map at the top of `knowledge/erp-fixedasset.md`.** If the screen has no scenarios here, write from its §16 sheet instead.
1. **Read the CR and underline the changes.** For each one write: *which screen, which field/rule/status/message, what it was, what it becomes.*
2. **Find the area** in the index below, then read its sections 1 to 3 (what it is, starting states, rules).
3. **Pick the scenarios the change touches** from section 4 — copy their Steps, change the data or expected result that the CR changed. Use section 5 of the area ("When a CR changes something — what to re-check") to find the neighbours that can break.
4. **Add new scenarios only for what is new.** Follow the same layout (Precondition, Steps, Test data, Expected).
5. **Check the journeys** (Part J below) if the change crosses screens, e.g. a new field on registration that later shows on the voucher or the profile.
6. **Put open points to the BA** — each area ends with questions the automation never answered.
7. **Format** the final rows with the `test-case-writing` standard (11 columns, Positive / Negative / Edge Case / Business / Out of Scope). The mapping is below.

### Area index
| Area | Prefix | Use it when the CR touches |
|---|---|---|
| Asset Registration (AAQ) | REG | creating, drafting, submitting, approving registrations; the serial number; the first voucher |
| Asset Profile | PRF, SPL | finding an asset by serial, profile changes, barcode, pending list, splitting an asset |
| Asset Transaction | TRX | assign, acknowledge, move, un-assign |
| Asset Expense and voucher checking | EXP | repair/maintenance expense; how to verify any voucher |
| Asset Transfer and Single Challan | TRF, SCH | moving assets between branches or projects |
| Asset Disposal | WOF, SAL | write-off and sale |
| Journeys across areas | JRN | changes that cross more than one screen |

### How a scenario maps to a test-case row (11-column standard)
| Scenario part | Test-case column |
|---|---|
| Prefix letter P / N / E / B | Test Case Type: Positive / Negative / Edge Case / Business |
| Title ("Verify …") | Name (one behaviour per row, max 255 characters) |
| Precondition | Precondition (numbered) |
| Steps | Steps (numbered, literal control names) |
| Test data | Test Data (login placeholder plus the values that drive this row) |
| Expected ("System should …") | Expected Result |
| the area's name, e.g. `Fixed Asset/Registration/Asset Registration by AAQ` | Folder (same value for Positive, Negative, Edge, Business rows of one screen) |
| — | Actual Result: "Works as expected"; Priority: High; Status: Approved |
| Basis: DERIVED | In the automation columns: Automation Suitable = No until the screen has been checked |

---

## Worked example — from a CR to test cases

**Mock CR (for illustration only):** "On Asset Registration by AAQ, the **Warranty End Date** becomes mandatory for **Laptop** and **Desktop Computer** items. It must not be earlier than the Purchase Date. Draft is also blocked without it."

**Step 1 — what changes.** Screen: Asset Registration by AAQ. New rule on an existing optional field (Warranty End Date). New validation (not before Purchase Date). Applies to two item groups. Applies to Draft and Submit.

**Step 2 — which existing scenarios are the base.** From the Registration area: the mandatory-field scenarios (the Purchase Date / Vendor / empty-grid messages, which show that Draft and Submit give the same message), the 20,000 Taka and Measurement scenarios (they show how item-specific rules are tested), Draft-then-reopen-and-Submit, and the voucher after approval.

**Step 3 — new rows (derived from those patterns).**

| Type | Name | Steps in short | Expected |
|---|---|---|---|
| Positive | Verify a Laptop registration is saved as Draft when Warranty End Date is on or after the Purchase Date | Open Asset Registration by AAQ → select Project, Spot Purchase, Purchase Date, Vendor → choose Laptop item, specification, quantity 1, unit price 25000 → set Warranty End Date later than Purchase Date → Add → Draft | System should show "Asset registration(AAQ) drafted Successfully!" and list the registration as DRAFT |
| Negative | Verify Submit is blocked when a Laptop line has no Warranty End Date | same, leave Warranty End Date empty → Submit | System should show a validation message for Warranty End Date (exact text to be confirmed) and not create the registration |
| Negative | Verify Draft is also blocked without Warranty End Date for a Desktop Computer | as above with Desktop Computer → Draft | same validation, nothing saved |
| Edge Case | Verify Warranty End Date equal to the Purchase Date is accepted | Warranty End Date = Purchase Date → Add → Submit | System should accept (boundary) |
| Negative | Verify Warranty End Date one day before the Purchase Date is rejected | date − 1 day → Add | System should show a validation message (exact text to be confirmed) |
| Positive (regression) | Verify Furniture still saves without Warranty End Date | Furniture line, no date → Submit | System should show "Asset registration(AAQ) submitted Successfully!" |
| Business | Verify the approved Laptop's voucher is unchanged | approve, then search the Registration Number in Voucher Search | Debit 1202010701-01 Computer and IT Equipment, credit per sub type, amount = quantity × unit price |
| Edge Case | Verify a Draft saved earlier without the date is blocked on Submit | open the old Draft from the list → Submit | System should show the validation message |

**What made this fast:** the messages, the Draft/Submit pattern, the voucher accounts and the "reopen a Draft" step were already known. Only the new rule and its boundary needed thinking. The "exact text to be confirmed" rows are the points to ask the developer or BA.

---

## Journeys across areas (JRN)

These are the stories where one result feeds the next screen. Use them for end-to-end rows and for impact checks.

**JRN-01 — A purchase becomes a usable asset.** Register (Spot or Gift) → Submit → PENDING → approve → Asset Serial is generated, voucher is posted → Asset Serial Global List shows it UNASSIGNED / IN_USE. *Check:* nothing is in the Pending Process List for a fresh asset.
Areas: REG, PRF.

**JRN-02 — Hand an asset to an employee and take it back.** Approved asset → Assign (Draft or Submit) → approve → asset ASSIGNED → assignee acknowledges (asset stays ASSIGNED) → Internal Movement (new building and floor, asset stays ASSIGNED) → Un-Assign to a different employee → approve → UNASSIGNED. *Order matters:* do the movement before Un-Assign; a submitted Un-Assign locks the asset.
Areas: TRX, PRF.

**JRN-03 — Spend on an asset.** Approved asset → Asset Expense (Inventory or Accounts source) → Submit → approve → expense voucher posted (Dr Other Maintenance Expenses, Cr Other Inventory or Supplier Payable-Opex) → find it in Voucher Search by Expense ID.
Areas: EXP.

**JRN-04 — Split a large asset.** Approved Land with a Measurement → Asset Serial Split (Split Into 2, percentages) → Submit → PENDING → approve → original serial disappears, new serials appear UNASSIGNED / IN_USE under a new approved registration. *Irreversible.*
Areas: SPL, PRF.

**JRN-05 — Move an asset to another project.** Approved asset → Shipment → challan (Draft) → add the asset serial → Submit → challan approval → shipment approval (gate pass generated) → In-Challan acknowledge → Gate Pass shows ACKNOWLEDGED. Single Challan is the same idea for one challan without a shipment.
Areas: TRF, SCH.

**JRN-06 — End of life.** Unassigned asset → either set to DAMAGE and write it off (Draft or Submit → approve) or sell it above/below the Written Down Value (Draft or Submit → approve). The asset cannot be used again.
Areas: WOF, SAL.

**JRN-07 — One asset, many stops (the order the suite uses).** Register → approve → Assign → Acknowledge → Internal Movement → Un-Assign → Expense → Write-off. Split, Transfer and Sale each use their own asset because they consume it.

**What to re-check when a CR changes a shared thing:**
| Changed thing | Re-check |
|---|---|
| Asset Serial format or generation | JRN-01, every screen that searches by serial |
| Assign Status or Utilization Status values | JRN-02, write-off and sale candidate lists, Global List filters |
| Project / area-code mapping | registration approval, shipment and challan projects |
| Voucher accounts or amounts | Registration, Expense, Write-off/Sale approval messages, Voucher Search |
| An approval screen's buttons or rules | all approval screens: popup approve, ticked-row approve, nothing ticked, select-all |
| A toast text | every scenario quoting it (search the text in this file) |

---

**Read before trusting the voucher scenarios.** The project CHANGELOG records that the voucher-content checks are known to fail or were not run after the last refactor, and the registration voucher PDF check is switched off in `test_03`. Treat the Debit/Credit accounts and amounts in the voucher scenarios as *what the system is expected to post*, and confirm them on the screen before using them as pass/fail criteria. Approve/Reject beyond "Approve" is untested everywhere: Reject and Send Back are open questions in every area.

**How a scenario is written (so you can edit it):** every scenario stands alone. It has its own numbered Precondition, one action per Step (screen, field label and value), a Test data list with every value used, and numbered Expected results. No scenario says "as above" or points to another scenario, so you can change one value or add a step without touching any other scenario. Values read from the system during the run are written in angle brackets, such as <Asset Serial>, <Registration Number> and <Out Challan No>.

**How these scenarios were checked:** every on-screen label, option text and example value was taken from, or compared with, the automation's element catalogs, test data and tests. Where a label, message or value could not be confirmed anywhere, the scenario says "(to be confirmed)" instead of guessing. A `VERIFIED (test_xx)` tag means that test performs these steps. A few example values (for instance free-text notes and comments, and an invalid PIN used in a negative scenario) are chosen for the scenario and are not taken from a test; they are ordinary data you can change.

---

## Areas


### Asset Registration (AAQ) — create, draft, submit, approve, list, voucher

**1. What this area is, in plain words**
- This is where a new fixed asset enters the system. A user fills the form "Asset Registration by AAQ" for something that was bought (Spot Purchase) or received free (Gift Item).
- The user saves it as a Draft (can be finished later) or Submits it. A Submitted registration has status PENDING.
- An approver opens the Asset Registration Approval List and approves it, one at a time from a popup or several at once by ticking rows. The same user account can create and approve.
- Approval gives the asset its Asset Serial number(s) and creates an automatic Journal Voucher (accounting entry). Before approval there is no serial and no voucher.
- There is no Reject or Sendback action on the screens; REJECTED and SENDBACK exist only as filter options.
- After approval the asset is UNASSIGNED and IN_USE. It then feeds every later flow: Assign, Transfer, Split, Expense, Write-off, Sale.

**2. Before you test: getting the right starting state**

| State needed | Why | How to get it (short human steps) |
|---|---|---|
| Logged in, Fixed Asset module open | Every scenario starts here | Open the ERP site, sign in with `<ERP Username> / <ERP Password>`. If an announcement banner appears, click the dark area outside it to close it. Open the Fixed Asset module. Check the "Registration" menu is visible. |
| A project that can be approved | Some projects fail at approval | Use project "[015] Microfinance (Dabi)". |
| A DRAFT registration | List, reopen and "not in Approval List" scenarios | Registration > Asset Registration by AAQ, fill the form, click Add, click Draft. Then find the number in Asset Registration List (Status DRAFT, Search, top row). |
| A PENDING registration | Approval scenarios, "no voucher yet" | Click the menu 'Registration', then the link 'Asset Registration by AAQ'. Fill the form (Project '[015] Microfinance (Dabi)', radio 'Spot Purchase', Purchase Date, Vendor 'ACE IT[P008937]', item 'Cabinet Table', Item Specification, Quantity 1, Unit Price 25000, Note), click 'Add', then click 'Submit' (toast "Asset registration(AAQ) submitted Successfully!"). Then open the link 'Asset Registration List', choose Status PENDING, click 'Search'; the newest Registration Number is in the top row. |
| An APPROVED registration | Serial and voucher scenarios | Approve a PENDING one in Asset Registration Approval List. Note the Registration Number and the Asset Serial from the popup tab "Asset Serials". |
| Several PENDING registrations | Bulk approval, header tick box | Submit two or three registrations, note their numbers. |
| Fixed test values | Same values give comparable results | Vendor "ACE IT[P008937]"; Quantity 1; Unit Price 25000; Item Specification any unique text; Note/Remarks any text. |

The form does not show the new Registration Number after Draft or Submit. Always read it from Asset Registration List. Each approval, submission and draft creates permanent data on staging.

**3. Rules and what to test for each**

| Rule (plain words) | Where it applies | Pass example | Fail / boundary examples to test |
|---|---|---|---|
| Fields are checked in this order: Purchase Date, then Vendor, then at least one asset line. The same message appears for Draft and for Submit. | Draft and Submit buttons, Spot Purchase and Gift Item | Date set, vendor set, one line in Asset Details | No date: "Please Select Purchase Date." No vendor: "Please Select a supplier." No line: "No Asset in List to perform operation" |
| Purchase Date must equal Registration Date. | Form | Pick the day equal to Registration Date in the calendar | Other dates (calendar is the only way to enter a date; behaviour for other days not confirmed) |
| Unit price per unit must be at least 20,000 Taka. The rule is on unit price, not on the total. | Add button; Furniture, Building, Laptop, Desktop | 20000 x 1 | 19999 x 1; 10000 x 2 (total 20,000 but unit price low); 20001; 19999.99 |
| Land is exempt from the 20,000 rule. | Add button, Land | Unit price 1, Measurement 12.5 | none for price |
| Land and Building need Measurement greater than zero. | Add button | Land with 12.5; Building with 15.5 | Blank; 0; negative number (exact message for 0 and negative to be confirmed) |
| Other items (Furniture, Laptop, Desktop) do not need Measurement. | Add button | Furniture with Measurement blank | none |
| Sub type is Spot Purchase or Gift Item. Fields and rules are the same for both. | Form | Either radio | Accounting credit side differs (see voucher) |
| Item pick fills Category, Sub Category, Group, Depreciation Rate and Measurement Unit by itself. | Form | Pick "Cabinet Table"; fields fill in about 3 seconds | Pick another item and check the fields change |
| Draft appears in Registration List only; Submit puts the registration in both lists. | Lists | Draft: status DRAFT, absent from Approval List | |
| Approval gives status APPROVED, Approved By, Approval Date, serial(s), and one voucher. | Approval List | See scenarios | |
| Approval comment holds at most 500 characters. | Approval popup | 500 characters | 600 typed: only 500 kept |
| Approve with nothing ticked is refused. | Approval List page-level Approve | | "You have to select a Registration first" |
| Approval fails for projects not mapped to the branch's current account code. | Approval | Project "[015] Microfinance (Dabi)" | Projects "[801] EHC", "[C04] Administratiion" |

**4. Scenario catalogue**

#### Positive

**REG-P01 — Verify a Spot Purchase furniture registration can be saved as Draft**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the registration form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Read the field 'Registration Date' and check that it is already filled with a date (dd/mm/yyyy).
  4. Click the radio button 'Spot Purchase'.
  5. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  6. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  7. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  8. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until 'Asset Category', 'Asset Sub Category', 'Asset Group', 'Depreciation Rate(%)' and 'Measurement Unit' are filled.
  9. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  10. In the field 'Quantity' type 1.
  11. In the field 'Unit Price(TK.)' type 25000.
  12. Click the button 'Add' and wait about 2 seconds for the line to appear in the 'Asset Details' grid.
  13. Click the button 'Draft'.
  14. Wait for the toast message to appear and read it.
  15. Click the menu 'Registration', then the link 'Asset Registration List'.
  16. In the filter 'Status' choose 'DRAFT' and click the button 'Search'.
  17. In the grid, read the cells 'Registration Number' and 'Status' of the top row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Status filter = DRAFT
- Expected:
  1. System should show the toast "Asset registration(AAQ) drafted Successfully!".
  2. System should clear the form and return to a blank Create form.
  3. System should show the new registration in the Asset Registration List with the 'Status' cell DRAFT in the top row.
- Basis: VERIFIED (test_01)
- Check also:
  1. After step 6, read the fields 'Vendor/Supplier/Lessor Ref. Number' and 'Vendor/Supplier/Lessor Address': System should fill both (the Ref. Number shows the vendor number).
  2. After step 12, read the 'Asset Details' grid: System should show 'Total Price(TK)' 25000 on the line and Grand Total 25000.

**REG-P02 — Verify a Gift Item furniture registration can be saved as Draft**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the registration form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Read the field 'Registration Date' and check that it is already filled with a date (dd/mm/yyyy).
  4. Click the radio button 'Gift Item'.
  5. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  6. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  7. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  8. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  9. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  10. In the field 'Quantity' type 1.
  11. In the field 'Unit Price(TK.)' type 25000.
  12. Click the button 'Add' and wait about 2 seconds for the line to appear in the 'Asset Details' grid.
  13. Click the button 'Draft'.
  14. Wait for the toast message to appear and read it.
  15. Click the menu 'Registration', then the link 'Asset Registration List'.
  16. In the filter 'Status' choose 'DRAFT' and click the button 'Search'.
  17. In the grid, read the cells 'Registration Number' and 'Status' of the top row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Gift Item
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Status filter = DRAFT
- Expected:
  1. System should show the toast "Asset registration(AAQ) drafted Successfully!".
  2. System should clear the form.
  3. System should show the new registration in the Asset Registration List with the 'Status' cell DRAFT in the top row.
- Basis: VERIFIED (test_01)
- Check also:
  1. Open the new Draft (click its Registration Number link) and read the radio buttons: System should show 'Gift Item' selected, not 'Spot Purchase'.

**REG-P03 — Verify a Spot Purchase registration can be submitted directly**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the registration form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Read the field 'Registration Date' and check that it is already filled with a date (dd/mm/yyyy).
  4. Click the radio button 'Spot Purchase'.
  5. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  6. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  7. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  8. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  9. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  10. In the field 'Quantity' type 1.
  11. In the field 'Unit Price(TK.)' type 25000.
  12. Click the button 'Add' and wait about 2 seconds for the line to appear in the 'Asset Details' grid.
  13. Click the button 'Submit'.
  14. Wait for the toast message to appear and read it. Look at the form and check whether a Registration Number is shown.
  15. Click the menu 'Registration', then the link 'Asset Registration List'.
  16. In the filter 'Status' choose 'PENDING' and click the button 'Search'.
  17. In the grid, read the cells 'Registration Number' and 'Status' of the top row (the newest number is at the top).
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Status filter = PENDING
- Expected:
  1. System should show the toast "Asset registration(AAQ) submitted Successfully!".
  2. System should not show the new Registration Number on the form.
  3. System should show in the Asset Registration List a top row with 'Status' PENDING (this is the new registration; its number is <Registration Number>).
- Basis: VERIFIED (test_01, test_02)
- Check also:
  1. In the Asset Registration List, read the top row cells 'Created By' and 'Registration Type': System should show the logged-in user and AAQ.

**REG-P04 — Verify a Gift Item registration can be submitted directly**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the registration form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Read the field 'Registration Date' and check that it is already filled with a date (dd/mm/yyyy).
  4. Click the radio button 'Gift Item'.
  5. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  6. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  7. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  8. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  9. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  10. In the field 'Quantity' type 1.
  11. In the field 'Unit Price(TK.)' type 25000.
  12. Click the button 'Add' and wait about 2 seconds for the line to appear in the 'Asset Details' grid.
  13. Click the button 'Submit'.
  14. Wait for the toast message to appear and read it.
  15. Click the menu 'Registration', then the link 'Asset Registration List'.
  16. In the filter 'Status' choose 'PENDING' and click the button 'Search'.
  17. In the grid, read the cells 'Registration Number' and 'Status' of the top row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Gift Item
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Status filter = PENDING
- Expected:
  1. System should show the toast "Asset registration(AAQ) submitted Successfully!".
  2. System should show in the Asset Registration List a top row with 'Status' PENDING.
- Basis: VERIFIED (test_01)
- Check also:
  1. Click the Registration Number link of the top row to open the popup 'Asset Registration View': System should show 'Gift Item' as the selected sub type.

**REG-P05 — Verify a Land registration is accepted with a very low unit price**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the registration form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Land' and click the option 'Land-> Land-> Land-> Land'. Wait about 3 seconds until the category fields are filled.
  8. Read the field 'Measurement Unit'.
  9. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-LAND-001'.
  10. In the field 'Quantity' type 1.
  11. In the field 'Unit Price(TK.)' type 1.
  12. In the field 'Measurement' type 12.5.
  13. Click the button 'Add' and wait about 2 seconds.
  14. Read the toast messages (if any) and read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Land-> Land-> Land-> Land
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-LAND-001
  - Quantity = 1
  - Unit Price(TK.) = 1
  - Measurement = 12.5
- Expected:
  1. System should add one line to the 'Asset Details' grid with 'Unit Price(TK)' 1.
  2. System should not show the minimum-price message "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka."
- Basis: VERIFIED (test_01)
- Check also:
  1. At step 8 the field 'Measurement Unit' should show Decimal.
  2. In the grid line read the column 'Measurement': System should show 12.5.

**REG-P06 — Verify a Building registration with Measurement is accepted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the registration form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Building' and click the option 'Building-> Building-> Building-> Building'. Wait about 3 seconds until the category fields are filled.
  8. Read the field 'Measurement Unit'.
  9. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-BUILDING-001'.
  10. In the field 'Quantity' type 1.
  11. In the field 'Unit Price(TK.)' type 25000.
  12. In the field 'Measurement' type 15.5.
  13. Click the button 'Add' and wait about 2 seconds for the line to appear in the 'Asset Details' grid.
  14. Click the button 'Submit'.
  15. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Building-> Building-> Building-> Building
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-BUILDING-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Measurement = 15.5
- Expected:
  1. System should add the line to the 'Asset Details' grid.
  2. System should then show the toast "Asset registration(AAQ) submitted Successfully!".
- Basis: VERIFIED (test_01; Building assets are also registered this way for the sale flows)
- Check also:
  1. At step 8 the field 'Measurement Unit' should show SFT.
  2. In the grid line read the column 'Measurement': System should show 15.5.

**REG-P07 — Verify Laptop and Desktop registrations are accepted at the minimum unit price**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the registration form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Laptop' and click the option 'Laptop-> Laptop-> Laptop-> Computer/Laptop'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-LAPTOP-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 20000.
  11. Click the button 'Add' and wait about 2 seconds. Read the 'Asset Details' grid line: column 'Total Price(TK)'.
  12. Click the button 'Reset' at the bottom of the form (the one beside 'Draft' and 'Submit') to get a fresh form.
  13. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  14. Click the radio button 'Spot Purchase'.
  15. Click the calendar icon beside 'Purchase Date', then click the day that is equal to the 'Registration Date'.
  16. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  17. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  18. In 'Asset Item Name' click '-Select Item-', type 'Desktop Computer' and click the option 'Desktop Computer-> Computer-> Computer-> Computer/Laptop' (the option that starts with 'Desktop Computer', not 'All In One Desktop Computer'). Wait about 3 seconds.
  19. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-DESKTOP-001'.
  20. In the field 'Quantity' type 1.
  21. In the field 'Unit Price(TK.)' type 20000.
  22. Click the button 'Add' and wait about 2 seconds. Read the 'Asset Details' grid line: column 'Total Price(TK)'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name 1 = Laptop-> Laptop-> Laptop-> Computer/Laptop
  - Item Specification/IMEI/SL 1 = AUTOMATION_TEST-SPEC-LAPTOP-001
  - Asset Item Name 2 = Desktop Computer-> Computer-> Computer-> Computer/Laptop
  - Item Specification/IMEI/SL 2 = AUTOMATION_TEST-SPEC-DESKTOP-001
  - Quantity = 1 (both)
  - Unit Price(TK.) = 20000 (both)
- Expected:
  1. System should add the Laptop line with 'Total Price(TK)' 20000 and no minimum-price message.
  2. System should add the Desktop Computer line with 'Total Price(TK)' 20000 and no minimum-price message.
- Basis: VERIFIED (test_01 for the 20000 boundary on furniture; laptop and desktop registered in test_02 and later flows); laptop and desktop at exactly 20000: DERIVED (not yet run)
- Check also:
  1. After step 11 read the Grand Total: System should show 20000.

**REG-P08 — Verify a Draft can be reopened and submitted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A DRAFT Spot Purchase registration exists in the Asset Registration List, saved with project '[015] Microfinance (Dabi)', Note/Remarks 'AUTOMATION_TEST registration note', vendor 'ACE IT[P008937]', one line 'Cabinet Table' with Item Specification 'AUTOMATION_TEST-SPEC-FURN-001', Quantity 1, Unit Price(TK.) 25000. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. In the filter 'Registration Number' type <Registration Number>.
  3. Click the button 'Search'.
  4. In the grid, check that exactly one row is shown and read its 'Status' cell.
  5. Click the Registration Number link in that row.
  6. Read the heading of the form and check which buttons are present.
  7. Read the sub type radio buttons, the 'Project Name & Number', the 'Note/Remarks', the vendor number, and the line in the 'Asset Details' grid (item name, first 30 characters of the specification, quantity, unit price).
  8. Click the button 'Submit'.
  9. Wait for the toast message to appear and read it.
  10. Click the menu 'Registration', then the link 'Asset Registration List'.
  11. In the filter 'Registration Number' type <Registration Number> and click the button 'Search'.
  12. Read the 'Status' cell and count the rows.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number> (the Draft number)
  - Saved values to compare = Spot Purchase; [015] Microfinance (Dabi); AUTOMATION_TEST registration note; ACE IT[P008937] (number P008937); Cabinet Table; AUTOMATION_TEST-SPEC-FURN-001; Quantity 1; Unit Price 25000
- Expected:
  1. System should show one row with 'Status' DRAFT at step 4.
  2. System should show the form heading "Update Asset Registration By AAQ" with the buttons 'Draft', 'Submit' and 'Reset'.
  3. System should show the saved values unchanged (sub type Spot Purchase, project, remarks, vendor, line).
  4. System should show the toast "Asset registration(AAQ) submitted Successfully!".
  5. System should show the same <Registration Number> in one row with 'Status' PENDING.
- Basis: VERIFIED (test_02)
- Check also:
  1. At step 12 count the rows for <Registration Number>: System should show exactly one row (the Draft did not create a second registration).

**REG-P09 — Verify a PENDING registration is approved from its popup with a comment**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A PENDING Spot Purchase registration exists (project '[015] Microfinance (Dabi)', vendor 'ACE IT[P008937]', one line 'Cabinet Table', Quantity 1, Unit Price(TK.) 25000, Item Specification 'AUTOMATION_TEST-SPEC-FURN-001'). Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number>.
  3. Click the button 'Search'.
  4. In the grid, read the cells of the row: 'Status', 'Project Name', 'Registration Type', and check that a tick box is present in the first column.
  5. Click the Registration Number link in that row.
  6. Wait for the popup 'Asset Registration View' to open. Read 'Registration No.' and the entered details (project, vendor, line).
  7. In the 'Comment' box of the popup type 'Approved by test'.
  8. Click the button 'Approve' in the popup.
  9. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number>
  - Comment = Approved by test
- Expected:
  1. System should show one row with 'Status' PENDING, 'Project Name' [015] Microfinance (Dabi), 'Registration Type' AAQ and a tick box.
  2. System should show the popup 'Asset Registration View' with 'Registration No.' equal to <Registration Number> and the details entered at registration.
  3. System should show the toast "Asset registration approved successfully."
- Basis: VERIFIED (test_03)
- Check also:
  1. Click the button 'Search' again for <Registration Number> and read the 'Status' cell: System should show APPROVED.

**REG-P10 — Verify an approved registration shows approver, date and no tick box**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A registration has just been approved from its popup with the comment 'Approved by test'. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number>.
  3. Click the button 'Search'.
  4. In the grid, read the cells 'Status', 'Approved By' and 'Approval Date' of the row, and check whether the first column has a tick box.
  5. Click the Registration Number link and look at the popup for an 'Approve' button.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number>
- Expected:
  1. System should show 'Status' APPROVED.
  2. System should show 'Approved By' filled.
  3. System should show 'Approval Date' in the format dd/mm/yyyy.
  4. System should show no tick box on the row.
  5. System should show no 'Approve' button in the popup (only 'Close').
- Basis: VERIFIED (test_03)
- Check also:
  1. In the popup, read the 'Comment' box: System should show it empty for an approved registration.

**REG-P11 — Verify an Asset Serial is generated on approval**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. An APPROVED registration with one Furniture line 'Cabinet Table', Quantity 1, exists. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number> and click the button 'Search'.
  3. Click the Registration Number link in the row.
  4. In the popup 'Asset Registration View' click the tab 'Asset Serials'.
  5. In the grid 'Registered Asset Serials' read the first row: column 'Asset Serial' (written below as <Asset Serial>) and the other columns.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number>
  - Quantity = 1
- Expected:
  1. System should show exactly one row in 'Registered Asset Serials'.
  2. System should show an 'Asset Serial' that starts with letters followed by digits (pattern example BBDASR followed by digits, such as BBDASR00227761).
  3. System should show 'Asset Item Name' Cabinet Table in that row.
- Basis: VERIFIED (test_03)
- Check also:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then the link 'Asset Serial Global List', search <Asset Serial>: System should find the serial.
  2. Open the Asset Serials tab of a registration that is still PENDING: System should show no serial ("No data available in table").

**REG-P12 — Verify several registrations are approved together using ticked rows**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. Two PENDING Spot Purchase furniture registrations exist (project '[015] Microfinance (Dabi)', 'Cabinet Table', Quantity 1, Unit Price(TK.) 25000). Their numbers are known (written below as <Registration Number 1> and <Registration Number 2>).
  4. Optionally a third PENDING registration exists and is NOT to be approved (written below as <Registration Number 3>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Status' choose 'PENDING' and click the button 'Search'.
  3. In the grid, tick the tick box of the row <Registration Number 1>.
  4. In the grid, tick the tick box of the row <Registration Number 2>.
  5. Do not tick the row <Registration Number 3>.
  6. Click the button 'Approve' at the bottom of the page (not the 'Approve' button of a row and not the one inside a popup).
  7. Wait for the toast message to appear and read it.
  8. In the filter 'Registration Number' type <Registration Number 1>, clear 'Status', click 'Search', read the 'Status' cell. Click the number link, open the tab 'Asset Serials' and read the first row.
  9. Repeat the same reading for <Registration Number 2>.
  10. Search <Registration Number 3> and read its 'Status' cell.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status filter = PENDING
  - Rows ticked = <Registration Number 1>, <Registration Number 2>
  - Row not ticked = <Registration Number 3>
- Expected:
  1. System should show the toast "Asset registration approved successfully."
  2. System should show 'Status' APPROVED for <Registration Number 1> and <Registration Number 2>.
  3. System should show one separate Asset Serial in the tab 'Asset Serials' of each approved registration (the two serials differ).
  4. System should keep <Registration Number 3> at 'Status' PENDING.
- Basis: VERIFIED (test_03)
- Check also:
  1. Only ticked rows are approved: the unticked PENDING row <Registration Number 3> stays PENDING (step 10).

**REG-P13 — Verify the header tick box ticks and unticks all rows**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. At least three PENDING registrations exist, so that the Approval List shows several rows with a tick box.
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Status' choose 'PENDING' and click the button 'Search'.
  3. Click the tick box in the header of the grid (first column heading).
  4. Look at the tick box of every row and note whether it is ticked.
  5. Click the tick box in the header of the grid again.
  6. Look at the tick box of every row and note whether it is ticked.
  7. Do not click the button 'Approve'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status filter = PENDING
- Expected:
  1. System should tick every row that has a tick box after the first click.
  2. System should clear every row after the second click.
- Basis: VERIFIED (test_03)
- Check also:
  1. After step 6 click the button 'Reset' of the page and check that no row is approved: read the 'Status' of the rows, all still PENDING. (Do not click 'Approve' while rows are ticked, because it approves every ticked row.)

#### Negative

**REG-N01 — Verify the first mandatory message when Purchase Date is missing (Spot Purchase)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Leave 'Purchase Date', 'Vendor/Supplier/Lessor Name' and the 'Asset Details' grid empty.
  5. Click the button 'Draft'.
  6. Wait for the toast message to appear, read it, and wait until it has disappeared.
  7. Click the button 'Submit'.
  8. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = (not set)
  - Vendor/Supplier/Lessor Name = (not set)
  - Asset line = (none)
- Expected:
  1. System should show the toast "Please Select Purchase Date." after clicking 'Draft'.
  2. System should show the toast "Please Select Purchase Date." after clicking 'Submit'.
  3. System should save nothing (the form stays open and filled as it was).
- Basis: VERIFIED (test_01)
- Check also:
  1. Open the menu 'Registration', then 'Asset Registration List', choose 'Status' DRAFT and PENDING in turn and click 'Search': System should show no new row created by this test.

**REG-N02 — Verify the same Purchase Date message for Gift Item**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Gift Item'.
  4. Leave 'Purchase Date', 'Vendor/Supplier/Lessor Name' and the 'Asset Details' grid empty.
  5. Click the button 'Draft'.
  6. Wait for the toast message to appear, read it, and wait until it has disappeared.
  7. Click the button 'Submit'.
  8. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Gift Item
  - Purchase Date = (not set)
  - Vendor/Supplier/Lessor Name = (not set)
  - Asset line = (none)
- Expected:
  1. System should show the toast "Please Select Purchase Date." after clicking 'Draft'.
  2. System should show the toast "Please Select Purchase Date." after clicking 'Submit'.
- Basis: VERIFIED (test_01)

**REG-N03 — Verify the vendor message comes second (Spot Purchase and Gift Item)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. Leave 'Vendor/Supplier/Lessor Name' on '-Select Party-' and the 'Asset Details' grid empty.
  6. Click the button 'Draft'. Wait for the toast message to appear, read it, and wait until it has disappeared.
  7. Click the button 'Submit'. Wait for the toast message to appear and read it.
  8. Click the radio button 'Gift Item'.
  9. Check that 'Purchase Date' is still set to the day of the 'Registration Date'; if it is empty, set it again as in step 4.
  10. Click the button 'Draft'. Wait for the toast message to appear, read it, and wait until it has disappeared.
  11. Click the button 'Submit'. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase, then Gift Item
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = (not set)
  - Asset line = (none)
- Expected:
  1. System should show the toast "Please Select a supplier." after 'Draft' with Spot Purchase.
  2. System should show the toast "Please Select a supplier." after 'Submit' with Spot Purchase.
  3. System should show the toast "Please Select a supplier." after 'Draft' with Gift Item.
  4. System should show the toast "Please Select a supplier." after 'Submit' with Gift Item.
- Basis: VERIFIED (test_01)

**REG-N04 — Verify the no-line message comes third (Spot Purchase and Gift Item)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. Do not add any line to the 'Asset Details' grid.
  7. Click the button 'Draft'. Wait for the toast message to appear, read it, and wait until it has disappeared.
  8. Click the button 'Submit'. Wait for the toast message to appear and read it.
  9. Click the radio button 'Gift Item'.
  10. Check that 'Purchase Date' and the vendor 'ACE IT[P008937]' are still set; if one is empty, set it again as in steps 4 and 5.
  11. Click the button 'Draft'. Wait for the toast message to appear, read it, and wait until it has disappeared.
  12. Click the button 'Submit'. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase, then Gift Item
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Asset line = (none)
- Expected:
  1. System should show the toast "No Asset in List to perform operation" after 'Draft' with Spot Purchase.
  2. System should show the toast "No Asset in List to perform operation" after 'Submit' with Spot Purchase.
  3. System should show the toast "No Asset in List to perform operation" after 'Draft' with Gift Item.
  4. System should show the toast "No Asset in List to perform operation" after 'Submit' with Gift Item.
- Basis: VERIFIED (test_01)

**REG-N05 — Verify unit price 19999 is refused for Furniture (Spot and Gift)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 19999.
  11. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
  12. Click the radio button 'Gift Item'.
  13. Check that the item fields are still filled (Cabinet Table, specification, Quantity 1, Unit Price(TK.) 19999); if not, fill them again as in steps 7 to 10.
  14. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase, then Gift Item
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 19999
- Expected:
  1. System should show the toast "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka." for Spot Purchase.
  2. System should show the same toast for Gift Item.
  3. System should add no line to the 'Asset Details' grid in either case.
- Basis: VERIFIED (test_01)

**REG-N06 — Verify the 20,000 rule uses unit price, not the total**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  9. In the field 'Quantity' type 2.
  10. In the field 'Unit Price(TK.)' type 10000.
  11. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 2
  - Unit Price(TK.) = 10000 (total 20,000)
- Expected:
  1. System should show the toast "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka."
  2. System should add no line to the 'Asset Details' grid.
- Basis: VERIFIED (test_01)
- Check also:
  1. Change 'Quantity' to 3 and 'Unit Price(TK.)' to 20000 and click 'Add': System should add the line (unit price meets the minimum).

**REG-N07 — Verify Land without Measurement is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Land' and click the option 'Land-> Land-> Land-> Land'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-LAND-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 25000.
  11. Leave the field 'Measurement' blank.
  12. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Land-> Land-> Land-> Land
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-LAND-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Measurement = (blank)
- Expected:
  1. System should show the toast "Measurement must be greater than zero for this asset group".
  2. System should add no line to the 'Asset Details' grid.
- Basis: VERIFIED (test_01)

**REG-N08 — Verify Building without Measurement is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Building' and click the option 'Building-> Building-> Building-> Building'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-BUILDING-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 25000.
  11. Leave the field 'Measurement' blank.
  12. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Building-> Building-> Building-> Building
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-BUILDING-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Measurement = (blank)
- Expected:
  1. System should show the toast "Measurement must be greater than zero for this asset group".
  2. System should add no line to the 'Asset Details' grid.
- Basis: VERIFIED (test_01)

**REG-N09 — Verify Land with Measurement 0 is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Land' and click the option 'Land-> Land-> Land-> Land'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-LAND-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 25000.
  11. In the field 'Measurement' type 0.
  12. Click the button 'Add'. Wait for the toast message to appear and read its exact text, then read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Land-> Land-> Land-> Land
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-LAND-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
  - Measurement = 0
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should add no line to the 'Asset Details' grid.
- Basis: DERIVED (not yet run)

**REG-N10 — Verify approving with nothing ticked is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. At least one PENDING registration exists, so the Approval List with Status PENDING shows rows.
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Status' choose 'PENDING' and click the button 'Search'.
  3. Check that no tick box in the grid is ticked.
  4. Click the button 'Approve' at the bottom of the page.
  5. Wait for the toast message to appear and read it.
  6. Click 'Search' again and read the 'Status' cell of the top row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status filter = PENDING
  - Rows ticked = none
- Expected:
  1. System should show the toast "You have to select a Registration first".
  2. System should approve nothing (the top row 'Status' is still PENDING).
- Basis: VERIFIED (test_03)

**REG-N11 — Verify approval fails for a project not mapped to the branch**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A PENDING Spot Purchase registration exists that was created with project '[801] EHC' (vendor 'ACE IT[P008937]', 'Cabinet Table', Quantity 1, Unit Price(TK.) 25000). Its number is known (written below as <Registration Number>). Project '[C04] Administratiion' behaves the same way and may be used in a second run.
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number> and click the button 'Search'.
  3. Click the Registration Number link in the row to open the popup 'Asset Registration View'.
  4. Click the button 'Approve' in the popup.
  5. Wait for the toast message to appear and read it.
  6. In the popup click the tab 'Asset Serials' and read the grid.
  7. Close the popup, click 'Search' again and read the 'Status' cell.
  8. Click the menu 'Accounting' tab, then 'Voucher', then 'Voucher Search'; in 'Transaction Number' type <Registration Number> and click 'Search'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number>
  - Project Name & Number = [801] EHC
- Expected:
  1. System should show the message "No Area Current Account Code: This branch is not mapped with project : [801] EHC" (the project name written in the message is the project of the registration).
  2. System should keep 'Status' PENDING.
  3. System should show no serial in the tab 'Asset Serials' ("No data available in table").
  4. System should list no voucher for <Registration Number>.
- Basis: OBSERVED (catalog, approval list notes, not part of a regular run)
- Check also:
  1. Approve a PENDING registration created with project '[015] Microfinance (Dabi)' in the same way: System should show "Asset registration approved successfully." (the problem is per project, not per branch).

**REG-N12 — Verify a Draft is not in the Approval List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A DRAFT registration exists. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number>.
  3. Click the button 'Search'.
  4. Read the grid.
  5. Click the dropdown 'Status' and read the list of options.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number> (a Draft)
- Expected:
  1. System should show "No data available in table".
  2. System should offer the 'Status' options PENDING, APPROVED, REJECTED, SENDBACK and no option DRAFT.
- Basis: VERIFIED (test_03)

**REG-N13 — Verify a PENDING number is not listed when Status APPROVED is chosen**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A PENDING registration exists. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number>.
  3. In the filter 'Status' choose 'APPROVED'.
  4. Click the button 'Search'.
  5. Read the grid.
  6. In the filter 'Status' choose 'PENDING' and click 'Search'.
  7. Read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number> (PENDING)
  - Status filter = APPROVED, then PENDING
- Expected:
  1. System should show "No data available in table" with Status APPROVED.
  2. System should show one row for <Registration Number> with 'Status' PENDING when Status PENDING is chosen.
- Basis: VERIFIED (test_03)

**REG-N14 — Verify Draft cannot be saved with a vendor but no line after a valid date (order of messages with line present but date missing)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Do not set 'Purchase Date'. The Add step below must still be possible; if 'Add' refuses because the date is missing, note the toast and stop (the line then cannot be added without a date).
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 25000.
  11. Click the button 'Add' and read the toast message and the 'Asset Details' grid.
  12. Click the button 'Draft'. Wait for the toast message to appear, read it, and wait until it has disappeared.
  13. Click the button 'Submit'. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = (not set)
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
- Expected:
  1. System should show a validation message about Purchase Date on 'Draft' (expected "Please Select Purchase Date." because the date is checked first; to be confirmed with a line present).
  2. System should show the same validation message on 'Submit'.
  3. System should save nothing.
- Basis: DERIVED (not yet run)

**REG-N15 — Verify a unit price of 19999.99 is refused for a non-Land item**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 19999.99.
  11. Click the button 'Add'. Wait for the toast message to appear and read its exact text, then read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 19999.99
- Expected:
  1. System should refuse the line with a validation message (exact text to be confirmed; likely "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka.").
  2. System should add no line to the 'Asset Details' grid.
- Basis: DERIVED (not yet run)

#### Edge Case

**REG-E01 — Verify exactly 20000 per unit is accepted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  9. In the field 'Quantity' type 1.
  10. In the field 'Unit Price(TK.)' type 20000.
  11. Click the button 'Add' and wait about 2 seconds.
  12. Read the toast messages (if any) and read the line in the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 20000
- Expected:
  1. System should add the line to the 'Asset Details' grid with 'Total Price(TK)' 20000.
  2. System should not show the message "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka."
- Basis: VERIFIED (test_01)
- Check also:
  1. Read the Grand Total under the grid: System should show 20000.

**REG-E02 — Verify 20001 per unit is accepted and the Grand Total is right**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds until the category fields are filled.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  9. In the field 'Quantity' type 3.
  10. In the field 'Unit Price(TK.)' type 20001.
  11. Click the button 'Add' and wait about 2 seconds.
  12. Read the line in the 'Asset Details' grid: column 'Total Price(TK)', and read the Grand Total.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 3
  - Unit Price(TK.) = 20001
- Expected:
  1. System should add the line to the 'Asset Details' grid.
  2. System should show 'Total Price(TK)' 60003.
  3. System should show Grand Total 60003.
- Basis: DERIVED (not yet run)

**REG-E03 — Verify the 20,000 boundary for Building, Laptop and Desktop**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. Building, below the limit: in 'Asset Item Name' click '-Select Item-', type 'Building' and click the option 'Building-> Building-> Building-> Building'. Wait about 3 seconds.
  8. In 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-BUILDING-001', in 'Quantity' type 1, in 'Unit Price(TK.)' type 19999, in 'Measurement' type 15.5.
  9. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
  10. Building, at the limit: in 'Unit Price(TK.)' type 20000 (replace 19999) and click the button 'Add'. Read the toast messages (if any) and the 'Asset Details' grid.
  11. Click the button 'Reset' beside 'Add' to clear the item block.
  12. Laptop, below the limit: in 'Asset Item Name' click '-Select Item-', type 'Laptop' and click the option 'Laptop-> Laptop-> Laptop-> Computer/Laptop'. Wait about 3 seconds.
  13. In 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-LAPTOP-001', in 'Quantity' type 1, in 'Unit Price(TK.)' type 19999.
  14. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
  15. Laptop, at the limit: in 'Unit Price(TK.)' type 20000 (replace 19999) and click the button 'Add'. Read the toast messages (if any) and the 'Asset Details' grid.
  16. Click the button 'Reset' beside 'Add' to clear the item block.
  17. Desktop, below the limit: in 'Asset Item Name' click '-Select Item-', type 'Desktop Computer' and click the option 'Desktop Computer-> Computer-> Computer-> Computer/Laptop' (not 'All In One Desktop Computer'). Wait about 3 seconds.
  18. In 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-DESKTOP-001', in 'Quantity' type 1, in 'Unit Price(TK.)' type 19999.
  19. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
  20. Desktop, at the limit: in 'Unit Price(TK.)' type 20000 (replace 19999) and click the button 'Add'. Read the toast messages (if any) and the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Building = Building-> Building-> Building-> Building; AUTOMATION_TEST-SPEC-BUILDING-001; Measurement 15.5
  - Laptop = Laptop-> Laptop-> Laptop-> Computer/Laptop; AUTOMATION_TEST-SPEC-LAPTOP-001
  - Desktop = Desktop Computer-> Computer-> Computer-> Computer/Laptop; AUTOMATION_TEST-SPEC-DESKTOP-001
  - Quantity = 1 (all)
  - Unit Price(TK.) = 19999, then 20000 (each item)
- Expected:
  1. System should show "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka." for Building, Laptop and Desktop at 19999, and add no line.
  2. System should add a line with 'Total Price(TK)' 20000 for each of Building, Laptop and Desktop at 20000.
- Basis: VERIFIED for Furniture (test_01); other items DERIVED (not yet run). The project notes record the rule as enforced for Furniture, Building, Laptop and Desktop.

**REG-E04 — Verify Land accepts unit price 1 while Furniture with the same price is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Land' and click the option 'Land-> Land-> Land-> Land'. Wait about 3 seconds.
  8. In 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-LAND-001', in 'Quantity' type 1, in 'Unit Price(TK.)' type 1, in 'Measurement' type 12.5.
  9. Click the button 'Add'. Read the toast messages (if any) and the 'Asset Details' grid.
  10. Click the bottom 'Reset' (beside 'Draft' and 'Submit') to get a fresh form.
  11. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)', click the radio button 'Spot Purchase', set 'Purchase Date' to the day equal to 'Registration Date', and in 'Vendor/Supplier/Lessor Name' choose 'ACE IT[P008937]' as in steps 4 and 5.
  12. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds.
  13. In 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001', in 'Quantity' type 1, in 'Unit Price(TK.)' type 1.
  14. Click the button 'Add'. Wait for the toast message to appear and read it, then read the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Land = Land-> Land-> Land-> Land; AUTOMATION_TEST-SPEC-LAND-001; Measurement 12.5
  - Furniture = Cabinet Table; AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 1 (both)
- Expected:
  1. System should add the Land line with 'Unit Price(TK)' 1.
  2. System should refuse the Furniture line with "Total Unit Price/Cost of Fixed Asset cannot be lower than 20000 Taka." and add no line.
- Basis: VERIFIED (test_01)

**REG-E05 — Verify the approval Comment keeps only 500 characters**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A PENDING registration exists. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number> and click the button 'Search'.
  3. Click the Registration Number link to open the popup 'Asset Registration View'.
  4. In the 'Comment' box (placeholder 'Leave comment here... Maximum 500 characters') type or paste a text of 600 characters (for example the letter 'a' repeated 600 times).
  5. Read the text now in the 'Comment' box and count its characters.
  6. Do not click 'Approve' (click 'Close' to leave the popup).
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number>
  - Comment = 600 characters ('a' repeated 600 times)
- Expected:
  1. System should keep only 500 characters in the 'Comment' box.
- Basis: VERIFIED (test_03)
- Check also:
  1. In a popup of a PENDING registration, type exactly 500 characters in 'Comment' and click 'Approve': System should show "Asset registration approved successfully."
  2. Approve another PENDING registration with an empty 'Comment': System should also show "Asset registration approved successfully." (the comment is optional).

**REG-E06 — Verify approval works with an empty Comment**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A PENDING registration with project '[015] Microfinance (Dabi)' exists. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. In the filter 'Registration Number' type <Registration Number> and click the button 'Search'.
  3. Click the Registration Number link to open the popup 'Asset Registration View'.
  4. Leave the 'Comment' box empty.
  5. Click the button 'Approve' in the popup.
  6. Wait for the toast message to appear and read it.
  7. Click 'Search' again and read the 'Status' cell of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number>
  - Comment = (empty)
- Expected:
  1. System should show the toast "Asset registration approved successfully."
  2. System should show 'Status' APPROVED for <Registration Number>.
- Basis: DERIVED (not yet run)

**REG-E07 — Verify a Quantity above 1 creates the matching number of serials**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds.
  8. In the field 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001'.
  9. In the field 'Quantity' type 3.
  10. In the field 'Unit Price(TK.)' type 25000.
  11. Click the button 'Add' and wait about 2 seconds.
  12. Click the button 'Submit' and wait for the toast message.
  13. Click the menu 'Registration', then the link 'Asset Registration List'. In the filter 'Status' choose 'PENDING', click 'Search' and read the 'Registration Number' of the top row (written below as <Registration Number>).
  14. Click the menu 'Registration', then the link 'Asset Registration Approval List'. In 'Registration Number' type <Registration Number> and click 'Search'.
  15. Click the Registration Number link to open the popup, type nothing in 'Comment' and click the button 'Approve'. Wait for the toast message.
  16. Click 'Search' again, click the Registration Number link and click the tab 'Asset Serials'.
  17. Count the rows of the grid 'Registered Asset Serials' and read the column 'Asset Serial' of each.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 3
  - Unit Price(TK.) = 25000
- Expected:
  1. System should list serials for the registration in the tab 'Asset Serials' (number of serials expected to equal Quantity 3; to be confirmed).
  2. System should show each serial different from the others.
- Basis: DERIVED (not yet run)

**REG-E08 — Verify Delete and Reset in the form**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds.
  8. In 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001', in 'Quantity' type 1, in 'Unit Price(TK.)' type 25000.
  9. Click the button 'Add' and wait about 2 seconds for the line to appear in the 'Asset Details' grid.
  10. Click the delete (trash) button at the end of the line. Read the grid.
  11. Fill the item block again (Cabinet Table, 'AUTOMATION_TEST-SPEC-FURN-001', Quantity 1, Unit Price(TK.) 25000) and click 'Add' again. Wait for the line.
  12. Fill the item block once more (Cabinet Table, 'AUTOMATION_TEST-SPEC-FURN-002', Quantity 2, Unit Price(TK.) 30000) without clicking 'Add', then click the 'Reset' button beside 'Add'. Read the item fields and the grid.
  13. Click the 'Reset' button at the bottom of the form (beside 'Draft' and 'Submit'). Read all fields of the form and the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001 (second fill: AUTOMATION_TEST-SPEC-FURN-002)
  - Quantity = 1 (second fill: 2)
  - Unit Price(TK.) = 25000 (second fill: 30000)
- Expected:
  1. System should remove the line on delete; the grid shows "No data available in table".
  2. System should show the line again after the second 'Add'.
  3. System should clear the item block (item, specification, quantity, unit price) on the 'Reset' beside 'Add' and keep the line already in the grid.
  4. System should clear the whole form on the bottom 'Reset'.
- Basis: OBSERVED (catalog)

**REG-E09 — Verify a long specification is shortened in the grid and popup**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds.
  8. In the field 'Item Specification/IMEI/SL' type a 50-character text: 'AUTOMATION_TEST-SPEC-LONG-0123456789-0123456789-AB'.
  9. In the field 'Quantity' type 1, and in 'Unit Price(TK.)' type 25000.
  10. Click the button 'Add' and wait about 2 seconds. In the 'Asset Details' grid read the column 'Item Specification'.
  11. Click the button 'Submit' and wait for the toast message.
  12. Click the menu 'Registration', then the link 'Asset Registration List'. In the filter 'Status' choose 'PENDING', click 'Search', and click the Registration Number link of the top row.
  13. In the popup 'Asset Registration View' read the 'Item Specification' of the line in the 'Asset Details' grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-LONG-0123456789-0123456789-AB (50 characters)
  - Quantity = 1
  - Unit Price(TK.) = 25000
- Expected:
  1. System should show in the form grid the first 30 characters of the specification (AUTOMATION_TEST-SPEC-LONG-0123) followed by "...more".
  2. System should show the same first 30 characters followed by "...more" in the popup.
- Basis: OBSERVED (catalog)

#### Business

**REG-B01 — Verify Registration List filters return matching rows only**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. The logged-in user has registrations of type AAQ in several statuses (DRAFT, PENDING, APPROVED) with project '[015] Microfinance (Dabi)' and vendor 'ACE IT[P008937]'. One of their numbers is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. In the filter 'Status' choose 'PENDING' and click the button 'Search'. Read the 'Status' cell of every row.
  3. Click the button 'Reset'. In the filter 'Created By' type the logged-in user's name and choose it from the suggestions (needed again because Reset empties it).
  4. In the filter 'Registration Type' choose 'AAQ' and click 'Search'. Read the 'Registration Type' cell of every row.
  5. Click 'Reset' and set 'Created By' again. In the filter 'Project Name & Number' choose '[015] Microfinance (Dabi)' and click 'Search'. Read the 'Project Name' cell of every row.
  6. Click 'Reset' and set 'Created By' again. In the filter 'Vendor/Supplier/Lessor Name' type 'ACE IT' and click 'Search'. Read the rows.
  7. Click 'Reset' and set 'Created By' again. In the filter 'Registration Number' type <Registration Number> and click 'Search'. Read the rows.
  8. Click 'Reset' and set 'Created By' again. Click 'Registration From Date', pick today's day in the calendar; click 'Registration To Date', pick today's day; click 'Search'. Read the 'Registration Date' cell of every row.
  9. Read the column headings of the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status = PENDING
  - Registration Type = AAQ
  - Project Name & Number = [015] Microfinance (Dabi)
  - Vendor/Supplier/Lessor Name = ACE IT
  - Registration Number = <Registration Number>
  - Registration From Date = today; Registration To Date = today
- Expected:
  1. System should show only rows with 'Status' PENDING for the Status filter.
  2. System should show only rows with 'Registration Type' AAQ for the type filter.
  3. System should show only rows with 'Project Name' [015] Microfinance (Dabi) for the project filter.
  4. System should show only rows of registrations of vendor 'ACE IT' for the vendor filter.
  5. System should show exactly one row, <Registration Number>, for the number filter.
  6. System should show only rows whose 'Registration Date' is today for the date filter.
- Basis: VERIFIED (test_02)
- Check also:
  1. Read the grid headings: System should show 13 columns: SL, Registration Number, Registration Date, Reference Number, Registration Type, Branch Name, Project Name, Department Name, Created By, Status, Approved By, Approval Date, Attachment (Branch Name may be hidden on screen).

**REG-B02 — Verify unknown vendor or unknown number shows an empty grid**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. In the filter 'Vendor/Supplier/Lessor Name' type 'NO_SUCH_VENDOR_XYZ'.
  3. Click the button 'Search' and read the grid.
  4. Click the button 'Reset'.
  5. In the filter 'Registration Number' type 999999999.
  6. Click the button 'Search' and read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Vendor/Supplier/Lessor Name = NO_SUCH_VENDOR_XYZ
  - Registration Number = 999999999
- Expected:
  1. System should show "No data available in table" for the unknown vendor.
  2. System should show "No data available in table" for Registration Number 999999999.
- Basis: VERIFIED (test_02)

**REG-B03 — Verify Status and number filters combine as AND**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A PENDING registration exists. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. In the filter 'Status' choose 'DRAFT'.
  3. In the filter 'Registration Number' type <Registration Number>.
  4. Click the button 'Search' and read the grid.
  5. In the filter 'Status' choose 'PENDING' and click 'Search' and read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number> (PENDING)
  - Status = DRAFT, then PENDING
- Expected:
  1. System should list nothing ("No data available in table") for Status DRAFT with the PENDING number.
  2. System should list one row for <Registration Number> with 'Status' PENDING when Status PENDING is chosen.
- Basis: VERIFIED (test_02)

**REG-B04 — Verify Created By limits the list to own records**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. Read the filter 'Created By' and check that it is pre-filled with the logged-in user.
  3. Click the button 'Search'.
  4. Read the text under the grid "Showing 1 to N of ... entries" and note the total (written below as <Own Total>).
  5. Clear the filter 'Created By' (delete its text).
  6. Click the button 'Search'.
  7. Read the text under the grid again and note the total (written below as <All Total>).
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Created By = (pre-filled with the logged-in user), then empty
- Expected:
  1. System should pre-fill 'Created By' with the logged-in user.
  2. System should show a larger total with 'Created By' cleared (<All Total> is greater than <Own Total>; at catalog time 124 own versus 13,501 for everyone).
- Basis: VERIFIED (test_02)

**REG-B05 — Verify Reset empties all filters and does not search**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A registration of the logged-in user exists. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. In the filter 'Status' choose 'PENDING'.
  3. In the filter 'Registration Number' type <Registration Number>.
  4. Click the button 'Search' and read the grid (the grid shows the filtered result).
  5. Click the button 'Reset'.
  6. Read every filter box ('Status', 'Registration Number', 'Created By', 'Vendor/Supplier/Lessor Name', 'Project Name & Number').
  7. Read the grid without clicking 'Search'.
  8. Click the button 'Search' and read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status = PENDING
  - Registration Number = <Registration Number>
- Expected:
  1. System should empty all filter boxes, including 'Created By'.
  2. System should not refresh the grid after Reset (it still shows the result of step 4).
  3. System should refresh the grid only after 'Search' is clicked (rows of all users are listed, as 'Created By' is empty).
- Basis: VERIFIED (test_02)

**REG-B06 — Verify Records per page and paging**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. The logged-in user has more than 20 registrations (the Asset Registration List with 'Created By' pre-filled shows more than 20 entries).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. Click the button 'Search'.
  3. In the dropdown 'Records per page' choose 10. Count the rows and read the text under the grid.
  4. In the dropdown 'Records per page' choose 100. Count the rows and read the text under the grid.
  5. In the dropdown 'Records per page' choose 10 again.
  6. Read the 'Registration Number' of the first and last row and the 'SL' of the first row.
  7. Click the page button '2' under the grid.
  8. Read the text under the grid, the 'SL' of the first row and the 'Registration Number' of the first row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Records per page = 10 and 100 (available options 10, 20, 30, 50, 100)
  - Page = 2
- Expected:
  1. System should show 10 rows and the text "Showing 1 to 10 of ..." with page size 10.
  2. System should show up to 100 rows with page size 100.
  3. System should show "Showing 11 to 20 of" on page 2.
  4. System should show on page 2 older registrations (lower Registration Numbers than on page 1).
  5. System should restart 'SL' at 1 on every page.
  6. System should list the newest Registration Number first on page 1.
- Basis: VERIFIED (test_02)

**REG-B07 — Verify the View popup of a PENDING registration from the Registration List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. A PENDING Spot Purchase registration exists (project '[015] Microfinance (Dabi)', Note/Remarks 'AUTOMATION_TEST registration note', vendor 'ACE IT[P008937]', one line 'Cabinet Table', Item Specification 'AUTOMATION_TEST-SPEC-FURN-001', Quantity 1, Unit Price(TK.) 25000). Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration List'.
  2. In the filter 'Registration Number' type <Registration Number>.
  3. Click the button 'Search'.
  4. Click the Registration Number link in the row.
  5. In the popup 'Asset Registration View' (tab 'Details') read: Registration No., Project Name, Note/Remarks, Vendor/Supplier/Lessor Name, Vendor/Supplier/Lessor Number, and in the 'Asset Details' grid the Asset Item Name, Item Specification, Quantity and Unit Price(TK).
  6. Click the tab 'Asset Serials' and read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Number = <Registration Number>
- Expected:
  1. System should show the popup 'Asset Registration View' with Registration No. equal to <Registration Number>.
  2. System should show Project Name Microfinance (Dabi), Note/Remarks 'AUTOMATION_TEST registration note', vendor name 'ACE IT' and vendor number 'P008937'.
  3. System should show the line: Asset Item Name Cabinet Table, the first 30 characters of the specification (followed by "...more" if longer), Quantity 1, Unit Price(TK) 25000.
  4. System should show no serial in the tab 'Asset Serials' ("No data available in table").
- Basis: VERIFIED (test_02, test_03)

**REG-B08 — Verify Approval List filters, Approve Date range and statuses**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. At least one registration was approved today. Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration Approval List'.
  2. Read the filter 'Created By' (it starts empty on this page).
  3. Click the 'Approve From Date' filter and in the calendar (it opens on the current business month) click today's day.
  4. Click the 'Approve To Date' filter and in the calendar click today's day.
  5. Click the button 'Search' and read the grid.
  6. Click the button 'Reset'.
  7. In the filter 'Status' choose 'PENDING', click 'Search', and read the 'Status' cell of every row.
  8. In the filter 'Status' choose 'APPROVED', click 'Search', and read the 'Status' cell of every row.
  9. In the filter 'Status' choose 'REJECTED', click 'Search', and read the grid.
  10. In the filter 'Status' choose 'SENDBACK', click 'Search', and read the grid.
  11. Click the dropdown 'Status' and read the list of options.
  12. Read the column headings of the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Approve From Date = today; Approve To Date = today
  - Status = PENDING, APPROVED, REJECTED, SENDBACK
- Expected:
  1. System should show 'Created By' empty at the start.
  2. System should list the registrations approved today (including <Registration Number>) for the date range.
  3. System should list only rows with 'Status' PENDING for PENDING, and only APPROVED for APPROVED.
  4. System should list only REJECTED rows or an empty grid for REJECTED, and only SENDBACK rows or an empty grid for SENDBACK.
  5. System should offer the options PENDING, APPROVED, REJECTED, SENDBACK and not DRAFT.
- Basis: VERIFIED (test_03)
- Check also:
  1. Read the grid headings: System should show a tick box column, SL, then Registration Number, Registration Date, Reference Number, Registration Type, Project Name, Department Name, Created By, Status, Approved By, Approval Date, Attachment, plus an Approve column (Branch Name and the Approve column may be hidden on screen).

**REG-B09 — Verify no voucher exists before approval**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A DRAFT registration exists (number written below as <Draft Number>).
  4. A PENDING registration exists (number written below as <Pending Number>).
- Steps:
  1. Click the tab 'Accounting' in the top bar (it opens in the same browser tab).
  2. Click the menu 'Voucher', then click the link 'Voucher Search'.
  3. In the field 'Transaction Number' type <Draft Number>.
  4. Click the button 'Search' and wait for the grid to load. Read the grid.
  5. Clear the field 'Transaction Number' and type <Pending Number>.
  6. Click the button 'Search' and wait for the grid to load. Read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Number = <Draft Number>, then <Pending Number>
  - Date From / Date To = (left empty)
- Expected:
  1. System should list no voucher for <Draft Number> ("No data available in table").
  2. System should list no voucher for <Pending Number> ("No data available in table").
- Basis: VERIFIED (test_03)

**REG-B10 — Verify a voucher is created after approval**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Spot Purchase registration exists with project '[015] Microfinance (Dabi)', one line 'Cabinet Table' (Furniture), Quantity 1, Unit Price(TK.) 25000. Its number is known (written below as <Registration Number>) and its Approval Date is known (written below as <Approval Date>).
- Steps:
  1. Click the tab 'Accounting' in the top bar (it opens in the same browser tab).
  2. Click the menu 'Voucher', then click the link 'Voucher Search'.
  3. In the field 'Transaction Number' type <Registration Number> (the exact number). Leave 'Date From' and 'Date To' empty.
  4. Click the button 'Search' and wait for the grid to load.
  5. Read the row: columns Date, Voucher No., Transaction No, Amount, Particular, Status.
  6. Click 'Preview' on the row (it opens a new browser tab with the voucher as a PDF) and read the voucher: title, branch, Project, the account lines with Debit and Credit, the Particulars, and 'Approved By'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Number = <Registration Number>
  - Expected amount = 25000 (Quantity 1 x Unit Price 25000)
- Expected:
  1. System should show exactly one row for <Registration Number>.
  2. System should show Date equal to <Approval Date>, a Voucher No., Transaction No equal to <Registration Number>, Amount 25,000, Status Approved.
  3. System should show a Particular like "Furniture and Fixture ... Registered by AAQ. Asset Item: Cabinet Table".
  4. System should show in the PDF the title JOURNAL VOUCHER, branch "[HO - BDHO] Head Office" and Project "015 - Microfinance (Dabi)".
  5. System should show one debit line and one credit line, each 25,000.00.
  6. System should show credit Particulars ending "Asset Registration by AAQ, Reference no: <Registration Number>".
  7. System should show "Approved By" = "Auto Voucher".
- Basis: VERIFIED (test_03 row found; PDF content recorded in the catalog)
- Check also:
  1. Compare the Amount with Quantity x Unit Price of the registration: System should show equal values (25,000).

**REG-B11 — Verify debit account per item type (Spot Purchase)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Four APPROVED Spot Purchase registrations exist (project '[015] Microfinance (Dabi)', vendor 'ACE IT[P008937]', Quantity 1, Unit Price(TK.) 25000): one with Furniture 'Cabinet Table' (<Furniture Number>), one with 'Land' and Measurement 12.5 (<Land Number>), one with 'Building' and Measurement 15.5 (<Building Number>), one with 'Laptop' (<Laptop Number>).
  4. Optionally an APPROVED Spot Purchase registration with 'Desktop Computer' exists (<Desktop Number>).
- Steps:
  1. Click the tab 'Accounting' in the top bar, then the menu 'Voucher', then the link 'Voucher Search'.
  2. In the field 'Transaction Number' type <Furniture Number>, click 'Search', wait for the grid, click 'Preview' on the row, and read the debit and credit lines in the voucher PDF (account code, head of accounts, amount).
  3. Close the PDF tab. In 'Transaction Number' type <Land Number>, click 'Search', click 'Preview', and read the debit and credit lines.
  4. Close the PDF tab. In 'Transaction Number' type <Building Number>, click 'Search', click 'Preview', and read the debit and credit lines.
  5. Close the PDF tab. In 'Transaction Number' type <Laptop Number>, click 'Search', click 'Preview', and read the debit and credit lines.
  6. Optionally close the PDF tab, type <Desktop Number> in 'Transaction Number', click 'Search', click 'Preview', and read the lines.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Number = <Furniture Number>, <Land Number>, <Building Number>, <Laptop Number>, <Desktop Number>
  - Amount per voucher = 25,000.00
- Expected:
  1. System should debit 1202010501-01 Furniture and Fixture for Furniture.
  2. System should debit 1202010101-01 Land for Land.
  3. System should debit 1202010201-01 Building for Building.
  4. System should debit 1202010701-01 Computer and IT Equipment for Laptop.
  5. System should credit 2101010301-06 Supplier Payable-Capex on all vouchers.
  6. Desktop Computer (if tested): System should debit Computer and IT Equipment, expected same as Laptop (DERIVED, to be confirmed).
- Basis: OBSERVED (catalog voucher notes); Desktop debit account DERIVED (not yet run, expected same as Laptop, Computer and IT Equipment)

**REG-B12 — Verify credit account for Gift Item differs from Spot Purchase**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Gift Item registration exists (project '[015] Microfinance (Dabi)', vendor 'ACE IT[P008937]', 'Cabinet Table' Furniture, Quantity 1, Unit Price(TK.) 25000). Its number is known (written below as <Registration Number>).
- Steps:
  1. Click the tab 'Accounting' in the top bar, then the menu 'Voucher', then the link 'Voucher Search'.
  2. In the field 'Transaction Number' type <Registration Number>.
  3. Click the button 'Search' and wait for the grid to load.
  4. Click 'Preview' on the row and read the debit and credit lines in the voucher PDF (account code, head of accounts, amount).
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Number = <Registration Number>
  - Sub type = Gift Item (furniture)
- Expected:
  1. System should credit 4202010101-16 Other Income (not 2101010301-06 Supplier Payable-Capex).
  2. System should debit 1202010501-01 Furniture and Fixture (the same item account as for Spot Purchase).
  3. System should show 25,000.00 on both lines.
- Basis: OBSERVED (catalog voucher notes)

**REG-B13 — Verify an approved asset is UNASSIGNED and IN_USE in Asset Profile**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED registration exists (Furniture 'Cabinet Table', Quantity 1, Unit Price(TK.) 25000; a second one with 'Land', Measurement 12.5, Unit Price(TK.) 25000 may be used for the measurement check). The Asset Serial from the tab 'Asset Serials' is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Global List'.
  2. In the filter for the asset serial type <Asset Serial> (filter label to be confirmed).
  3. Click the button 'Search'.
  4. In the row read the columns 'Assign Status', 'Utilization Status' and 'Net Asset Value', and the Measurement with its unit.
  5. Repeat steps 2 to 4 for the Land serial (written below as <Land Serial>), if available.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>, and <Land Serial>
- Expected:
  1. System should show Assign Status UNASSIGNED.
  2. System should show Utilization Status IN_USE.
  3. System should show Net Asset Value 25000.00 (Quantity x Unit Price, 2 decimals).
  4. For the Land serial System should show the Measurement 12.50 with unit Decimal (2 decimals).
- Basis: OBSERVED (the automation builds these values for later flows)

**REG-B14 — Verify the same user can create and approve**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same account is used for creating and for approving.
  2. The Fixed Asset module is open and the menu 'Registration' is visible.
  3. No form is open yet (the form is opened in the steps below).
- Steps:
  1. Click the menu 'Registration' in the Fixed Asset module, then click the link 'Asset Registration by AAQ'.
  2. In the dropdown 'Project Name & Number' choose '[015] Microfinance (Dabi)'.
  3. Click the radio button 'Spot Purchase'.
  4. Click the calendar icon beside 'Purchase Date', then in the calendar click the day that is equal to the 'Registration Date'.
  5. In 'Vendor/Supplier/Lessor Name' click '-Select Party-', type 'ACE IT' and click the option 'ACE IT[P008937]'.
  6. In the field 'Note/Remarks' type 'AUTOMATION_TEST registration note'.
  7. In 'Asset Item Name' click '-Select Item-', type 'Furniture' and click the option 'Cabinet Table-> Wooden Furniture-> Furniture-> Furniture and Fixture'. Wait about 3 seconds.
  8. In 'Item Specification/IMEI/SL' type 'AUTOMATION_TEST-SPEC-FURN-001', in 'Quantity' type 1, in 'Unit Price(TK.)' type 25000.
  9. Click the button 'Add' and wait about 2 seconds, then click the button 'Submit' and wait for the toast message.
  10. Click the menu 'Registration', then the link 'Asset Registration List'. In the filter 'Status' choose 'PENDING', click 'Search' and read the 'Registration Number' of the top row (written below as <Registration Number>).
  11. Click the menu 'Registration', then the link 'Asset Registration Approval List'. In 'Registration Number' type <Registration Number> and click 'Search'.
  12. Click the Registration Number link, then click the button 'Approve' in the popup (leave 'Comment' empty).
  13. Wait for the toast message to appear and read it.
  14. Click 'Search' again and read the 'Status' and 'Approved By' cells.
- Test data:
  - Login = <ERP Username> / <ERP Password> (same account for all steps)
  - Project Name & Number = [015] Microfinance (Dabi)
  - Sub type = Spot Purchase
  - Purchase Date = same day as Registration Date
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Note/Remarks = AUTOMATION_TEST registration note
  - Asset Item Name = Cabinet Table (Furniture)
  - Item Specification/IMEI/SL = AUTOMATION_TEST-SPEC-FURN-001
  - Quantity = 1
  - Unit Price(TK.) = 25000
- Expected:
  1. System should show the toast "Asset registration(AAQ) submitted Successfully!" after Submit.
  2. System should allow the approval and show the toast "Asset registration approved successfully."
  3. System should show 'Status' APPROVED and 'Approved By' filled.
- Basis: OBSERVED (catalog)
- Check also:
  1. Approval by a different user and an approval limit by amount are not covered by this scenario (open questions for the business analyst); no extra check is possible with one account.

**5. When a CR changes something here — what to re-check**
- A field is added or changed on the AAQ form: REG-P01 to P07, REG-N01 to N04 (order of mandatory messages), REG-E08, REG-E09, and the popup check in REG-P08 and REG-B07.
- The unit price limit (20,000) or the Land exemption changes: REG-N05, N06, N15, REG-E01 to E04, REG-P05.
- The Measurement rule changes: REG-N07 to N09, REG-P05, REG-P06.
- A new item type or group is added: REG-P07 pattern, REG-E03, REG-B11 (new debit account), REG-B13.
- A mandatory-field message text changes: REG-N01 to N04, N05 to N08, N10, N11 (update the exact quotes).
- Approval logic changes (new status, Reject or Sendback added, multi-level approval): REG-P09 to P13, REG-N10, N11, REG-B08, REG-B14. Add new scenarios for the new action.
- Serial numbering changes: REG-P11, REG-E07, REG-B13.
- Voucher or account mapping changes: REG-B09 to B12.
- List columns, filters or paging change: REG-B01 to B08.
- Project mapping or branch setup changes: REG-N11 and the choice of project in every scenario.

**6. Questions to ask the BA**
- Can a Draft be edited (changed vendor, line, quantity) before Submit? Only reopen and submit unchanged was tested.
- Is Note/Remarks mandatory? It is typed in every test but never tested empty. The placeholder says "Maximum 100 characters" while the field accepts 200.
- What is the exact rule for Purchase Date versus Registration Date, and can another date be used?
- What are the Source Of Fund values and does the choice change the accounting? Does Warranty End Date have any effect or validation?
- What are the depreciation rate values per item type, and does the rate show on any later screen?
- Is the number of serials always equal to Quantity? Is the serial pattern fixed?
- Should Reject and Sendback exist? What is the intended path for a wrong registration after Submit?
- Should approval by a different user, and an approval limit by amount, be tested?
- Which projects are meant to be approvable? What should the user do when "This branch is not mapped with project" appears?
- MRR and LEASE registration types appear in the list filter. Is there a creation flow for them?
- The MRR Number filter does nothing in the Registration List; is that a known defect?
- What do the Attachment column and the Branch and Department filters do?
- What is the exact message for Measurement 0 or a negative Measurement?

---

### Asset Profile — Global List, Barcode, Pending Process List, Asset Serial Split

Prefixes: PRF = Asset Serial Global List, Generate Barcode, Asset In Pending Process List. SPL = Asset Serial Split, Split List, Split Approval List.
Menu for all screens: Fixed Asset > Asset Profile > (screen name). Always click through the menu; typing the address directly does not work reliably.

**1. What this area is, in plain words**
- Asset Profile is where a user looks at assets that already exist (registered and approved). It does not create assets.
- Asset Serial Global List shows every asset by Asset Serial. A user can filter, open an "Asset Profile Details" popup with 7 tabs, and change four things: Source Of Fund, Utilization Status, Item, Measurement.
- Generate Barcode lets the user tick assets, choose how many labels per asset (Print Quantity) and produce a barcode label PDF.
- Asset In Pending Process List shows assets that are stuck in an open process (assign, transfer, challan and so on) and which feature they are pending in. It can be exported to Excel.
- Asset Serial Split cuts one asset that has a Measurement (for example Land) into 2 to 100 new assets. The split goes PENDING in Asset Serial Split List, then an approver approves it in Asset Serial Split Approval List.
- After approval the original serial is gone and one new Asset Serial exists per split line. Before this area: Asset Registration and its approval. After this area: the new serials can be assigned, transferred and so on.

**2. Before you test: getting the right starting state**

| State needed | Why | How to get it (short human steps) |
|---|---|---|
| An APPROVED, UNASSIGNED furniture asset (no measurement) | Global List checks, Barcode, Pending list absence, split refusal | Register furniture (Fixed Asset > Registration > Asset Registration by AAQ), Submit, approve it in Asset Registration Approval List, note the Asset Serial from the Asset Serials tab |
| An APPROVED Land asset (Measurement 12.5, unit price 25000, quantity 1) | Split flow. Value 25000.00 is the Written Down Value | Click the menu 'Registration', then the link 'Asset Registration by AAQ'. Fill the form (Project '[015] Microfinance (Dabi)', radio 'Spot Purchase', Purchase Date, Vendor 'ACE IT[P008937]', search 'Land' and pick the Land item, Item Specification, Quantity 1, Unit Price 25000, Measurement 12.5), click 'Add' and 'Submit'. Open 'Asset Registration Approval List', filter the new Registration Number, open it, click 'Approve', and read the Asset Serial on the tab 'Asset Serials'. Use a fresh Land for each full split run, because a split uses the asset up |
| An APPROVED Building asset (Measurement 15.5) | Check Measurement and unit on the profile | Register and approve exactly as for the Land asset above, but search 'Building', pick the Building item and type Measurement 15.5 |
| A PENDING split | Split List and Split Approval List checks | Open the menu 'Asset Profile', then the link 'Asset Serial Split'. In 'Asset Serial' type the Land serial, click 'Search', click the green 'SPLIT' button of the row. Type Remarks 'AUTOMATION_TEST split note', type 2 in 'Split Into', click 'Split', type 50 in the percentage of line 1 and press Tab, then click 'Submit' |
| An APPROVED split | New serials checks | Open the menu 'Asset Profile', then the link 'Asset Serial Split Approval List'. Search the split serial, tick the checkbox of its row and click the button 'Approve'. The row shows Status APPROVED |
| A user who can open the Approval List | Approve step | Log in as the approver role |
| An asset that is inside an open process (optional) | Pending list with rows, Status filter, Export | Start an assign or transfer for an asset and leave it unfinished |

**3. Rules and what to test for each**

| Rule (plain words) | Where it applies | Pass example | Fail / boundary examples to test |
|---|---|---|---|
| Serial filter finds the exact asset | Global List, Barcode, Pending list | Asset Serial of a real asset lists one row | Well-formed unknown serial BBDASR99999999 gives "No data available in table"; partial serial |
| Pending list ignores text that does not look like a serial | Pending list | BBDASR99999999 gives no data | NOSUCHSERIAL000 returns the normal unfiltered list |
| Utilization Status and Assign Status filters narrow the list | Global List | IN_USE and UNASSIGNED list a new asset | DAMAGE or ASSIGNED must not list it |
| Source Of Fund must be chosen to save | Source Of Fund Change popup | Choose "BRAC" and Update | Update with nothing chosen gives "Please select a Source Of Fund." |
| Utilization Status change needs a Note | Utilization Status Change popup | Choose DAMAGE, type Note, Update gives "Asset profile status updated successfully." | Empty Note gives "Please add a note." |
| Item change needs a specification | Item Change popup | Enter Item Specification/IMEI/SL No. | Empty gives "Please select a Item Specification/IMEI/SL No." |
| Measurement is read-only until Change is clicked | Global List popup | Click Change, box becomes editable | Box editable before Change |
| Print Quantity is 1 to 99 (default 1) | Generate Barcode | 2 | 0, 100, empty (exact behaviour to be confirmed) |
| Split Into is a whole number from 2 to 100 | Asset Serial Split form | 2, 3, 100 | empty, 0, 1, 101, -3, 100000, 2.5 |
| Only an asset with Measurement above zero can be split | Asset Serial Split | Land (12.50) | Furniture gives "Cannot split: Please set a valid measurement above zero." |
| Last split line is read-only and takes the balance | Split form | Line 1 = 50 gives line 2 = 50 | Typing in the last line is not possible |
| Percentage keeps 2 decimals | Split form | 40 | 40.123 is stored as 40.12 |
| Lines need not be equal | Split form | 40 / 60 | (The old manual says equal parts; the live screen allows any percentage) |
| Totals must equal 100 percent, the asset measurement, Written Down Value and Accumulated Depreciation; each line value at least 1 | Submit | 50 / 50 | Empty or invalid percentage and measurement values (messages listed in section 4) |
| Approve or Reject needs at least one ticked row | Split Approval List | One row ticked | None ticked gives "You have to select a split first" |
| Approve and Submit are irreversible | Split and Approval | - | There is no confirm box. Use only fresh test assets |

**4. Scenario catalogue**

#### Positive

**PRF-P01 — Verify an approved asset is found by Asset Serial on the Global List with correct row data**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened from the ERP home page.
  3. An APPROVED, UNASSIGNED Furniture asset exists. It was registered through 'Asset Registration by AAQ' with Project Name & Number '[015] Microfinance (Dabi)', Asset Item Name 'Cabinet Table', Quantity 1, Unit Price(TK.) 25000, and approved in 'Asset Registration Approval List'.
  4. Its Asset Serial is known (written below as <Asset Serial>), read from the 'Asset Serials' tab of the approved registration.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' and the grid 'List of Global Asset Serial' are visible.
  4. In the field 'Asset Serial:' type <Asset Serial>.
  5. Click the button 'Search'.
  6. Wait for the grid to reload.
  7. In the grid, read the number of rows shown.
  8. In the row, read the cells under the columns 'Asset Serial', 'Asset Item Name', 'Sub Category', 'Category Name', 'Group Name', 'Project Name', 'Assign Status' and 'Utilization Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Asset Item Name (registered) = Cabinet Table
  - Project Name & Number (registered) = [015] Microfinance (Dabi)
- Expected:
  1. System should list exactly one row, and its 'Asset Serial' is <Asset Serial>.
  2. System should show 'Asset Item Name' = "Cabinet Table".
  3. System should show 'Sub Category' = "Wooden Furniture", 'Category Name' = "Furniture" and 'Group Name' = "Furniture and Fixture".
  4. System should show 'Project Name' = the project used at registration ("[015] Microfinance (Dabi)").
  5. System should show 'Assign Status' = "UNASSIGNED".
  6. System should show 'Utilization Status' = "IN_USE".
- Basis: VERIFIED (test_04)
- Check also: In step 8, compare the 'Project Name' text in the row with the Project Name & Number chosen at registration ('[015] Microfinance (Dabi)'); the text must name the same project even if the layout differs from the popup.

**PRF-P02 — Verify the Asset Profile Details popup shows the asset data (Furniture, Land, Building)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED Furniture asset exists: Asset Item Name 'Cabinet Table', Project '[015] Microfinance (Dabi)', Quantity 1, Unit Price(TK.) 25000, no Measurement. Its Asset Serial is <Furniture Serial> and its Registration Number is <Furniture Registration Number>.
  4. An APPROVED Land asset exists: Asset Item Name 'Land', Project '[015] Microfinance (Dabi)', Quantity 1, Unit Price(TK.) 25000, Measurement 12.5. Its Asset Serial is <Land Serial> and its Registration Number is <Land Registration Number>.
  5. An APPROVED Building asset exists: Asset Item Name 'Building', Project '[015] Microfinance (Dabi)', Quantity 1, Unit Price(TK.) 25000, Measurement 15.5. Its Asset Serial is <Building Serial> and its Registration Number is <Building Registration Number>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Furniture Serial>.
  5. Click the button 'Search'.
  6. Wait for the grid to reload.
  7. In the grid, click the blue link <Furniture Serial> in the column 'Asset Serial'.
  8. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  9. Read the fields 'Asset Serial', 'Registration Number', 'Item', 'Sub Category', 'Category', 'Group', 'Project', 'Utilization Status', 'Measurement', 'Measurement Unit' and 'Net Asset Value'.
  10. Click the button 'Close' of the popup.
  11. In the field 'Asset Serial:' delete the text and type <Land Serial>.
  12. Click the button 'Search' and wait for the grid to reload.
  13. In the grid, click the blue link <Land Serial> in the column 'Asset Serial'.
  14. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  15. Read the fields 'Asset Serial', 'Registration Number', 'Item', 'Sub Category', 'Category', 'Group', 'Project', 'Utilization Status', 'Measurement', 'Measurement Unit' and 'Net Asset Value'.
  16. Click the button 'Close' of the popup.
  17. In the field 'Asset Serial:' delete the text and type <Building Serial>.
  18. Click the button 'Search' and wait for the grid to reload.
  19. In the grid, click the blue link <Building Serial> in the column 'Asset Serial'.
  20. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  21. Read the fields 'Asset Serial', 'Registration Number', 'Item', 'Sub Category', 'Category', 'Group', 'Project', 'Utilization Status', 'Measurement', 'Measurement Unit' and 'Net Asset Value'.
  22. Click the button 'Close' of the popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Furniture Serial = <Furniture Serial>, Registration Number = <Furniture Registration Number>, Item = Cabinet Table, Measurement = none
  - Land Serial = <Land Serial>, Registration Number = <Land Registration Number>, Item = Land, Measurement = 12.5
  - Building Serial = <Building Serial>, Registration Number = <Building Registration Number>, Item = Building, Measurement = 15.5
  - Quantity = 1, Unit Price(TK.) = 25000 for all three
- Expected:
  1. For each of the three assets, System should open the popup titled "Asset Profile Details".
  2. For each asset, the popup should show 'Asset Serial' = that asset's serial and 'Registration Number' = the registration that created it.
  3. For each asset, the popup should show 'Item', 'Sub Category', 'Category' and 'Group' as registered (Furniture: "Cabinet Table", "Wooden Furniture", "Furniture", "Furniture and Fixture"; Land: "Land" for all four; Building: "Building" for all four).
  4. For each asset, the popup should show 'Project' = the registered project ("Microfinance (Dabi)") and 'Utilization Status' = "IN_USE".
  5. System should show 'Measurement' = "0.00" for the Furniture asset, "12.50" for the Land asset and "15.50" for the Building asset.
  6. System should show 'Measurement Unit' = "Pcs" for Furniture and "Decimal" for Land. For Building it should show "SFT" (the automation test data expects SFT).
  7. System should show 'Net Asset Value' = "25000.00" for each asset (Quantity 1 x Unit Price 25000, 2 decimals).
- Basis: VERIFIED (test_04)
- Check also: After step 22, with the popup of the Land asset open, confirm the 'Measurement' box is read-only (cannot be typed in) before any 'Change' button is clicked.

**PRF-P03 — Verify the Global List column headings**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' and the grid 'List of Global Asset Serial' are visible (the grid shows 10 rows before any search).
  4. Read the visible column headings of the grid from left to right.
- Test data:
  - Login = <ERP Username> / <ERP Password>
- Expected:
  1. System should show these 10 columns in this order: "SL", "Asset Serial", "Asset Item Name", "Sub Category", "Category Name", "Group Name", "Project Name", "Department", "Assign Status", "Utilization Status".
  2. System should show no other visible column heading.
- Basis: VERIFIED (test_04)
- Check also: Open the drop-down 'Records per page' under the grid and read its options. Expected: 10, 20, 30, 50 and 100.

**PRF-P04 — Verify the Utilization Status filter**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. A newly approved asset exists with Utilization Status 'IN_USE' (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the drop-down 'Asset Utilization Status:' choose 'IN_USE'.
  5. In the field 'Asset Serial:' type <Asset Serial>.
  6. Click the button 'Search'.
  7. Wait for the grid to reload and read the 'Asset Serial' column.
  8. In the drop-down 'Asset Utilization Status:' choose 'DAMAGE'.
  9. Check that the grid still shows the result of step 7 (choosing a status does not search by itself).
  10. Click the button 'Search'.
  11. Wait for the grid to reload and read the 'Asset Serial' column and the empty-state text.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Asset Utilization Status = IN_USE, then DAMAGE
- Expected:
  1. After step 7, System should list the asset <Asset Serial>.
  2. After step 9, System should not change the grid until 'Search' is clicked.
  3. After step 11, System should not list <Asset Serial>; the grid should show "No data available in table".
- Basis: VERIFIED (test_04)
- Check also: Click the button 'Reset', then repeat steps 5 to 7 with the drop-down left unselected. Expected: the asset is listed again.

**PRF-P05 — Verify the Assign Status filter**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. A newly approved asset exists with Assign Status 'UNASSIGNED' (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the drop-down 'Assign Status:' choose 'UNASSIGNED'.
  5. In the field 'Asset Serial:' type <Asset Serial>.
  6. Click the button 'Search'.
  7. Wait for the grid to reload and read the 'Asset Serial' column.
  8. In the drop-down 'Assign Status:' choose 'ASSIGNED'.
  9. Click the button 'Search'.
  10. Wait for the grid to reload and read the 'Asset Serial' column and the empty-state text.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Assign Status = UNASSIGNED, then ASSIGNED
- Expected:
  1. After step 7, System should list the asset <Asset Serial> with 'Assign Status' = "UNASSIGNED".
  2. After step 10, System should not list <Asset Serial>; the grid should show "No data available in table".
- Basis: VERIFIED (test_04)
- Check also: In the drop-down 'Assign Status:' read all options. Expected: exactly 'ASSIGNED' and 'UNASSIGNED' besides the placeholder.

**PRF-P06 — Verify the seven tabs of the profile popup and their empty content for a new asset**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. A newly approved asset exists that has never been assigned, transferred, depreciated, revalued, expensed or disposed (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open.
  8. Read the names of all tabs from left to right.
  9. Click the tab 'Depreciation History' and read its grid.
  10. Click the tab 'Revaluation History' and read its grid.
  11. Click the tab 'Transaction History' and read its grid.
  12. Click the tab 'Expenditure' and read its grid.
  13. Click the tab 'Disposal Info' and read its grid.
  14. Click the tab 'Attachment' and read its text.
  15. Click the button 'Close' of the popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show these 7 tabs in this order: "Details", "Depreciation History", "Revaluation History", "Transaction History", "Expenditure", "Disposal Info", "Attachment".
  2. The tab 'Depreciation History' should show "No data available in table".
  3. The tab 'Revaluation History' should show "No data available in table".
  4. The tab 'Transaction History' should show "No data available in table".
  5. The tab 'Expenditure' should show "No data available in table".
  6. The tab 'Disposal Info' should show "No data available in table".
  7. The tab 'Attachment' should show "No Attachment".
- Basis: VERIFIED (test_04)
- Check also: In steps 9 to 13 read the column headings of each empty grid. Expected: Depreciation History = SL, Asset Serial, Asset Item Name, Category, Purchase Price, Depreciation Amount, WDV, Period; Transaction History starts with SL, Asset Serial, Transaction Type, Transaction Date.

**PRF-P07 — Verify the Source Of Fund Change drop-down values**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An approved asset exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Click the button 'Change' next to the field 'Source Of Fund'.
  9. Wait for the small popup titled 'Update' to open on top of the profile popup.
  10. Open the drop-down 'New Source Of Fund' and read all its options.
  11. Count the options after the first one.
  12. Click the button 'Close' of the small popup (do not click 'Update').
  13. Click the button 'Close' of the profile popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Source Of Fund = none chosen
- Expected:
  1. System should open the small popup 'Update' with the drop-down 'New Source Of Fund'.
  2. The first option should be "-Select Source of Fund-".
  3. The list should contain the option "Dutch Embassy".
  4. The list should contain the option "BRAC".
  5. The list should hold more than 100 values (289 seen after the first option).
  6. Nothing is saved: after closing both popups the asset's Source Of Fund is unchanged.
- Basis: VERIFIED (test_04)
- Check also: Re-open the profile popup of the same asset and read the field 'Source Of Fund'. Expected: it shows the same value as before step 8.

**PRF-P08 — Verify the Utilization Status Change drop-down values and preselection**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. A newly approved asset exists with Utilization Status 'IN_USE' (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Click the button 'Change' next to the field 'Asset Utilization Status'.
  9. Wait for the small popup titled 'Update' to open.
  10. Read which option is currently selected in the status drop-down.
  11. Open the status drop-down and read all its options in order.
  12. Click the button 'Close' of the small popup (do not click 'Update').
  13. Click the button 'Close' of the profile popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Note = empty (nothing typed)
- Expected:
  1. System should list these options in this order: "Select Status", "SPLIT", "IN_USE", "DAMAGE", "STOLEN", "BURNED", "DONATED", "OFFLINE_TRANSFER", "UNDER_REPAIR".
  2. System should have "IN_USE" preselected.
  3. Nothing is saved after closing the popups.
- Basis: VERIFIED (test_04)
- Check also: In the small popup, check that a text box 'Note' is present and empty, and that the buttons 'Update', 'Reset' and 'Close' are shown.

**PRF-P09 — Verify Utilization Status can be changed to DAMAGE with a Note**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. A spare APPROVED asset with Utilization Status 'IN_USE' exists that is not needed by any other test (this scenario changes the asset). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Click the button 'Change' next to the field 'Asset Utilization Status'.
  9. Wait for the small popup titled 'Update' to open.
  10. In the status drop-down choose 'DAMAGE'.
  11. In the text box 'Note' type "AUTOMATION_TEST damaged for write off".
  12. Click the button 'Update' of the small popup.
  13. Wait for the toast message to appear and read it.
  14. Close the popups.
  15. On the Global List, in the drop-down 'Asset Utilization Status:' choose 'DAMAGE'.
  16. In the field 'Asset Serial:' type <Asset Serial>.
  17. Click the button 'Search' and wait for the grid to reload.
  18. In the grid, read the cell under the column 'Utilization Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Asset Utilization Status (new) = DAMAGE
  - Note = AUTOMATION_TEST damaged for write off
- Expected:
  1. System should show the success message "Asset profile status updated successfully."
  2. After step 17, System should list the asset <Asset Serial> under the filter DAMAGE.
  3. System should show 'Utilization Status' = "DAMAGE" in its row.
- Basis: OBSERVED (catalog; the change is used as a setup step by other flows)
- Check also: Open the profile popup of the asset again and read the field 'Asset Utilization Status'. Expected: "DAMAGE". The asset may not be usable for later transactions after this.

**PRF-P10 — Verify Measurement becomes editable only after Change**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED Land asset exists, registered with Measurement 12.5, Quantity 1, Unit Price(TK.) 25000, Project '[015] Microfinance (Dabi)'. Its Asset Serial is <Land Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Land Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Land Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Click inside the field 'Measurement' and try to type 5.
  9. Read the value in the field 'Measurement'.
  10. Click the button 'Change' next to the field 'Measurement'.
  11. Look at the screen for any new popup.
  12. Click inside the field 'Measurement' and read its value; check it can be edited.
  13. Look for a separate button 'Update' next to the Measurement field.
  14. Do not click 'Update'. Click the button 'Close' of the profile popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Land Serial = <Land Serial>
  - Measurement (registered) = 12.5
- Expected:
  1. Before 'Change', System should keep the field 'Measurement' read-only and showing "12.50"; typing 5 should have no effect.
  2. After 'Change', System should make the field 'Measurement' editable.
  3. System should keep the registered value "12.50" in the field.
  4. System should show a separate 'Update' button next to the Measurement field.
  5. System should open no other popup after 'Change'.
  6. Nothing is saved after closing the popup.
- Basis: VERIFIED (test_04)
- Check also: Re-open the popup of the same Land asset and read 'Measurement'. Expected: still "12.50" and read-only again.

**PRF-P11 — Verify Generate Barcode shows default Print Quantity 1**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED asset exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Generate Barcode'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial>.
  5. Click the button 'Search'.
  6. Wait for the grid to reload.
  7. In the grid, read the number in the column 'Print Quantity' of the row of <Asset Serial>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should list the asset <Asset Serial> in the grid.
  2. System should show 'Print Quantity' = "1" in its row.
- Basis: VERIFIED (test_05)
- Check also: Read the column headings of the grid. Expected visible columns: SL, Asset Serial, Asset Item Name, Sub Category, Category Name, Project Name, Department, Asset Assign Status, Status, Print Quantity (plus a tick box column).

**PRF-P12 — Verify Print Quantity can be set for a ticked row and a barcode PDF is generated**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED asset exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
  4. The browser allows a new tab to open.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Generate Barcode'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial>.
  5. Click the button 'Search' and wait for the grid to reload.
  6. In the grid, tick the check box in the row of <Asset Serial>.
  7. Read the hint inside the field 'Default Print Quantity:'.
  8. In the field 'Default Print Quantity:' type 2.
  9. Click the button 'Set'.
  10. In the grid, read the number in the column 'Print Quantity' of the row of <Asset Serial>.
  11. Click the button 'Generate'.
  12. Wait for a new browser tab to open and read the address of the new tab.
  13. Look at the content of the PDF in the new tab.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Default Print Quantity = 2
- Expected:
  1. System should show the hint "Min: 1, max: 99" in the field 'Default Print Quantity:'.
  2. After 'Set', System should show 'Print Quantity' = "2" in the row.
  3. After 'Generate', System should open a new browser tab with the barcode PDF; its address contains "generateAssetBarcodeReport".
  4. The PDF should hold one label per print quantity (2 labels), each with the BRAC logo, branch, project, item, barcode and serial.
- Basis: VERIFIED (test_05 for quantity and the new tab; PDF content only OBSERVED in catalog)
- Check also: Close the PDF tab and return to the Generate Barcode tab. Expected: the row is still ticked and still shows Print Quantity "2".

**PRF-P13 — Verify a freshly approved asset is NOT in the Asset In Pending Process List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. A freshly APPROVED Furniture asset exists (Asset Item Name 'Cabinet Table', Project '[015] Microfinance (Dabi)', Quantity 1, Unit Price(TK.) 25000) that is in no open process (not assigned, not transferred, not in a challan). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset In Pending Process List'.
  3. Wait until the button 'Search' is visible.
  4. Wait for the first rows of the grid to load.
  5. In the field 'Asset Serial:' type <Asset Serial>.
  6. Click the button 'Search'.
  7. Wait for the grid to reload; the empty-state row can take several seconds.
  8. Read the 'Asset Serial' column of the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show no row with the Asset Serial <Asset Serial>.
  2. The grid should show "No data available in table".
- Basis: VERIFIED (test_06)
- Check also: Open 'Asset Serial Global List', search <Asset Serial> and read 'Assign Status'. Expected: "UNASSIGNED", which matches the asset being in no process.

**PRF-P14 — Verify the Pending list column headings**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset In Pending Process List'.
  3. Wait until the button 'Search' is visible.
  4. Wait for the first rows of the grid to load.
  5. Read the visible column headings of the grid from left to right.
- Test data:
  - Login = <ERP Username> / <ERP Password>
- Expected:
  1. System should show these 17 columns in this order: "SL", "Asset Serial", "From Branch", "To Branch", "From Project", "From Department", "To Project", "To Department", "Asset Item Name", "Sub Category", "Category Name", "Group Name", "Status", "Pending in Feature", "Created By", "Creation Date", "Aging".
- Basis: VERIFIED (test_06)
- Check also: Read the filter labels above the grid. Expected: 'Asset Serial:', 'Asset Item Name:', 'Pending Feature:' and 'Status:', with the buttons 'Search', 'Reset' and 'Export'.

**PRF-P15 — Verify the Pending list Status filter**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. At least one asset with Status 'APPROVED' is in a pending process (for example an asset shown with 'Pending in Feature' = 'Asset Single In-Challan'). If no such row exists, do not run this scenario.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset In Pending Process List'.
  3. Wait until the button 'Search' is visible.
  4. Wait for the first rows of the grid to load.
  5. In the drop-down 'Status:' choose 'APPROVED'.
  6. Click the button 'Search'.
  7. Wait for the grid to reload.
  8. Read the cell under the column 'Status' of every row shown.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status = APPROVED (options in the drop-down: PENDING, APPROVED, DRAFT, SENDBACK)
- Expected:
  1. System should show at least one row.
  2. System should show "APPROVED" in the column 'Status' of every row shown.
- Basis: VERIFIED (test_06)
- Check also: Repeat steps 5 to 8 once each with 'PENDING', 'DRAFT' and 'SENDBACK' (DERIVED). Expected: every row shown has the chosen Status, or the grid shows "No data available in table" when no asset has that Status.

**PRF-P16 — Verify a Pending list row is found again by its own serial**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. The Asset In Pending Process List holds at least one row (an asset is inside an open process).
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset In Pending Process List'.
  3. Wait until the button 'Search' is visible.
  4. Wait for the first rows of the grid to load.
  5. In the first row, read and write down the cells under 'Asset Serial' (written below as <Pending Serial>), 'Asset Item Name', 'Group Name', 'Status' and 'Pending in Feature'.
  6. In the field 'Asset Serial:' type <Pending Serial>.
  7. Click the button 'Search'.
  8. Wait for the grid to reload.
  9. In the row of <Pending Serial>, read the cells under 'Asset Serial', 'Asset Item Name', 'Group Name', 'Status' and 'Pending in Feature'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Pending Serial> (read in step 5)
- Expected:
  1. System should list the row for <Pending Serial>.
  2. System should show the same 'Asset Item Name' as in step 5.
  3. System should show the same 'Group Name' as in step 5.
  4. System should show the same 'Status' as in step 5.
  5. System should show the same 'Pending in Feature' as in step 5.
- Basis: VERIFIED (test_06)
- Check also: Click the button 'Reset' and read the grid. Expected: the unfiltered list returns and the field 'Asset Serial:' is empty.

**PRF-P17 — Verify Export of the Pending list to Excel**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. Microsoft Excel (or another spreadsheet program) is available to open the downloaded file.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset In Pending Process List'.
  3. Wait until the button 'Search' is visible.
  4. Wait for the first rows of the grid to load.
  5. Read the total number of rows of the grid (the text under the grid, 'Showing ... of ... entries').
  6. Click the button 'Export'.
  7. Wait for the file download to finish and read the file name.
  8. Open the downloaded file.
  9. Read the first row of the sheet.
  10. Count the data rows below the first row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Filters = none (grid unfiltered)
- Expected:
  1. System should download a file named "Asset In Pending Process List.xlsx".
  2. The first row of the sheet should hold these 17 names: "SL", "Asset Serial", "From Branch", "To Branch", "From Project", "From Department", "To Project", "To Department", "Asset Item Name", "Sub Category", "Category Name", "Group Name", "Status", "Pending in Feature", "Created By", "Creation Date", "Aging".
  3. The sheet should hold one data row per grid row (the count of step 10 equals the count of step 5).
- Basis: VERIFIED (test_06)
- Check also: One earlier run saw no download within 30 seconds. If the download is slow, note how many seconds it took and whether it finished after waiting longer.

#### Negative

**PRF-N01 — Verify an unknown but well-formed serial gives an empty Global List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. No asset has the Asset Serial BBDASR99999999.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type BBDASR99999999.
  5. Click the button 'Search'.
  6. Wait for the grid to reload.
  7. Read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = BBDASR99999999
- Expected:
  1. System should show no asset row.
  2. System should show "No data available in table".
- Basis: VERIFIED (test_04)
- Check also: In the field 'Asset Serial:' type a partial serial of a real asset (for example the first 10 characters of <Asset Serial> of any approved asset) and click 'Search'. Expected: the real asset is listed, because the filter matches part of a serial.

**PRF-N02 — Verify Source Of Fund Update with nothing selected is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED asset exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Click the button 'Change' next to the field 'Source Of Fund'.
  9. Wait for the small popup titled 'Update' to open.
  10. Leave the drop-down 'New Source Of Fund' on "-Select Source of Fund-".
  11. Click the button 'Update' of the small popup.
  12. Wait for the toast message to appear and read it.
  13. Look at the screen to check whether the small popup is still open.
  14. Click the button 'Close' of the small popup, then the button 'Close' of the profile popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - New Source Of Fund = "-Select Source of Fund-" (nothing chosen)
- Expected:
  1. System should show the error message "Please select a Source Of Fund."
  2. System should keep the small popup 'Update' open.
  3. System should save nothing: after closing, the field 'Source Of Fund' of the asset is unchanged.
- Basis: VERIFIED (test_04)
- Check also: In the same small popup choose the option "BRAC" in 'New Source Of Fund' and click 'Reset'. Expected: the drop-down goes back to "-Select Source of Fund-" and nothing is saved.

**PRF-N03 — Verify Utilization Status Update with an empty Note is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED asset with Utilization Status 'IN_USE' exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Click the button 'Change' next to the field 'Asset Utilization Status'.
  9. Wait for the small popup titled 'Update' to open.
  10. In the status drop-down choose 'DAMAGE'.
  11. Leave the text box 'Note' empty.
  12. Click the button 'Update' of the small popup.
  13. Wait for the toast message to appear and read it.
  14. Click the button 'Close' of the small popup, then the button 'Close' of the profile popup.
  15. Read the field 'Asset Utilization Status' of the asset on the Global List row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Asset Utilization Status (new) = DAMAGE
  - Note = empty
- Expected:
  1. System should show the error message "Please add a note."
  2. System should save nothing: 'Utilization Status' of the asset in the grid is still "IN_USE".
- Basis: VERIFIED (test_04)
- Check also: Type a Note consisting only of spaces and click 'Update'. Expected: record what the system does (exact behaviour to be confirmed).

**PRF-N04 — Verify Item Update without an Item Specification is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED asset exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Read the current value of the field 'Item Specification' (written below as <Old Specification>).
  9. Click the button 'Change' next to the field 'Item'.
  10. Wait for the small popup titled 'Update' to open.
  11. Leave the field 'New Item Specification/IMEI/SL No.' empty.
  12. Click the button 'Update' of the small popup.
  13. Wait for the toast message to appear and read it.
  14. Click the button 'Close' of the small popup, then the button 'Close' of the profile popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - New Item Specification/IMEI/SL No. = empty
- Expected:
  1. System should show the error message "Please select a Item Specification/IMEI/SL No." (wording exactly as on screen).
  2. System should save nothing: after re-opening the popup the 'Item Specification' still equals <Old Specification>.
- Basis: VERIFIED (test_04)
- Check also: Re-open the profile popup of the same asset and read the field 'Item Specification'. Expected: the value is <Old Specification>.

**PRF-N05 — Verify Utilization Status Update with the placeholder status and a Note**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED asset with Utilization Status 'IN_USE' exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  7. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  8. Click the button 'Change' next to the field 'Asset Utilization Status'.
  9. Wait for the small popup titled 'Update' to open.
  10. In the status drop-down choose 'Select Status'.
  11. In the text box 'Note' type "Test".
  12. Click the button 'Update' of the small popup.
  13. Wait for the toast message to appear and read it.
  14. Click the button 'Close' of the small popup, then the button 'Close' of the profile popup.
  15. Read the cell under 'Utilization Status' of the asset on the Global List.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Asset Utilization Status (new) = Select Status
  - Note = Test
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should save nothing: 'Utilization Status' of the asset is still "IN_USE".
- Basis: DERIVED (not yet run)
- Check also: Repeat steps 8 to 13 with the current status 'IN_USE' chosen again and Note "Test". Record whether the system accepts a change to the same status (behaviour to be confirmed).

**PRF-N06 — Verify a malformed serial typed in the Pending Process List search returns the unfiltered list**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. No asset has the Asset Serial BBDASR99999999.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset In Pending Process List'.
  3. Wait until the button 'Search' is visible.
  4. Wait for the first rows of the grid to load and note how many rows and which serials are shown (the unfiltered list).
  5. In the field 'Asset Serial:' type NOSUCHSERIAL000.
  6. Click the button 'Search'.
  7. Wait for the grid to reload and read the rows shown.
  8. In the field 'Asset Serial:' delete the text and type BBDASR99999999.
  9. Click the button 'Search'.
  10. Wait up to several seconds for the grid to reload and read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (first search) = NOSUCHSERIAL000
  - Asset Serial (second search) = BBDASR99999999
- Expected:
  1. After step 7, System should not treat NOSUCHSERIAL000 as a serial and should return the normal unfiltered list (the same rows as in step 4).
  2. After step 10, System should show "No data available in table" (it may take several seconds).
- Basis: OBSERVED (catalog)
- Check also: In step 10 wait at least 10 seconds before concluding the grid is not empty, and note how long the empty-state text took to appear.

**SPL-N01 — Verify SPLIT is refused for an asset without Measurement**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists (Measurement 0, no measurement). Its Asset Serial is known (written below as <Furniture Serial>).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Furniture Serial>.
  3. Click the button 'Search'.
  4. In the row of <Furniture Serial> click the green button 'SPLIT'.
  5. Wait for the red message to appear and read it.
  6. Look at the screen for an 'Asset Split' form.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Furniture Serial>
- Expected:
  1. System should show the red message "Cannot split: Please set a valid measurement above zero."
  2. System should not open the 'Asset Split' form.
- Basis: VERIFIED (test_07)
- Check also: Search <Furniture Serial> on 'Asset Serial Split List'. Expected: "No data available in table" (nothing was created).

**SPL-N02 — Verify Split Into cannot be empty**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. Leave the field 'Split Into' empty.
  5. Click the button 'Split'.
  6. Wait for the red message and read it.
  7. Look at the form for result lines.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = (empty)
- Expected:
  1. System should show the red message "Split into field is mandatory".
  2. System should build no split lines.
- Basis: VERIFIED (test_07)
- Check also: Leave 'Split Into' empty and type nothing in 'Remarks' either, click 'Split'. Expected: the same red message (the empty Remarks adds no second message).

**SPL-N03 — Verify Split Into values outside 2 to 100 are refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 0.
  5. Click the button 'Split', read the red message and look for result lines.
  6. In the field 'Split Into' replace the value with 1.
  7. Click the button 'Split', read the red message and look for result lines.
  8. In the field 'Split Into' replace the value with 101.
  9. Click the button 'Split', read the red message and look for result lines.
  10. In the field 'Split Into' replace the value with -3.
  11. Click the button 'Split', read the red message and look for result lines.
  12. In the field 'Split Into' replace the value with 100000.
  13. Click the button 'Split', read the red message and look for result lines.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 0, 1, 101, -3, 100000 (one after the other)
- Expected:
  1. For 0, System should show the red message "Please enter a valid integer number between 2 and 100".
  2. For 1, System should show the red message "Please enter a valid integer number between 2 and 100".
  3. For 101, System should show the red message "Please enter a valid integer number between 2 and 100".
  4. For -3, System should show the red message "Please enter a valid integer number between 2 and 100".
  5. For 100000, System should show the red message "Please enter a valid integer number between 2 and 100".
  6. In every case System should build no split lines.
- Basis: VERIFIED (test_07 for 0, 1, 101; catalog for -3 and 100000)
- Check also: After the last refusal type 2 in 'Split Into' and click 'Split'. Expected: 2 split lines are built (the form recovers from the errors).

**SPL-N04 — Verify Split Into with a decimal or text value is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2.5.
  5. Click the button 'Split', read the message and look for result lines.
  6. In the field 'Split Into' remove the value and type abc (note whether the box accepts letters at all).
  7. Click the button 'Split', read the message and look for result lines.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2.5, then abc
- Expected:
  1. For 2.5, System should show a validation message (exact text to be confirmed) and build no lines.
  2. For abc, System should show a validation message (exact text to be confirmed) or keep the box empty, and build no lines.
- Basis: DERIVED (not yet run)
- Check also: Record whether the message is the same as "Please enter a valid integer number between 2 and 100" or "Split into field is mandatory".

**SPL-N05 — Verify Submit is refused when line percentage is empty**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>. It is disposable.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Remarks' type AUTOMATION_TEST split note.
  5. In the field 'Split Into' type 2, click the button 'Split'.
  6. Do not type anything in the 'Percentage' boxes.
  7. Click the button 'Submit'.
  8. Wait for the message and read it.
  9. Search <Land Serial> on 'Asset Serial Split List'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Remarks = AUTOMATION_TEST split note
  - Split Into = 2
  - Percentage (both lines) = (empty)
- Expected:
  1. System should show a validation message. Source text suggests "Percentage value is empty" (seen in source only, not seen on screen).
  2. System should create no split ("No data available in table" on Asset Serial Split List).
- Basis: DERIVED (not yet run)
- Check also: Other Submit messages in the source: "Measurement value is empty", "Measurement value is not valid", "Percentage value is not valid", "Total percentage should be equal to 100", "Total measurement should be equal to <measurement>", "Written down value should not be less than 1". Confirm each on screen before using them as expected results. Try one: type 0 in the 'Percentage' box of line 1, press Tab, click 'Submit' and record the message.

**SPL-N06 — Verify Approve with no row ticked is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> as the approver.
  2. The Fixed Asset module is open.
  3. The Asset Serial Split Approval List has at least one row (no row is ticked).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split Approval List'.
  2. Make sure no checkbox in the grid is ticked.
  3. Click the button 'Approve'.
  4. Wait for the message and read it.
  5. Look at the screen for a dialog.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Rows ticked = none
- Expected:
  1. System should show the info message "You have to select a split first".
  2. System should open no dialog.
  3. System should change no 'Status' in the grid.
- Basis: VERIFIED (test_09)
- Check also: Click the 'Search' button (with no filter) and read the 'Status' of the top row. Expected: unchanged.

**SPL-N07 — Verify Reject with no row ticked is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> as the approver.
  2. The Fixed Asset module is open.
  3. The Asset Serial Split Approval List has at least one row (no row is ticked).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split Approval List'.
  2. Make sure no checkbox in the grid is ticked.
  3. Click the button 'Reject'.
  4. Wait for the message and read it.
  5. Look at the screen for a dialog.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Rows ticked = none
- Expected:
  1. System should show "You have to select a split first".
  2. System should open no dialog.
  3. System should change no 'Status' in the grid.
- Basis: OBSERVED (catalog)
- Check also: Tick the header checkbox (select all) and untick it again, then click 'Reject'. Expected: the same message "You have to select a split first" (do not leave any row ticked when clicking 'Reject' on real data).

**SPL-N08 — Verify an unknown serial on Split List gives an empty grid**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split List'.
  2. In the field 'Asset Serial' type NOSUCHSERIAL000.
  3. Click the button 'Search'.
  4. Read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = NOSUCHSERIAL000
- Expected:
  1. System should show "No data available in table".
- Basis: VERIFIED (test_08)
- Check also: Click the button 'Reset'. Expected: 'Asset Serial' is emptied and the grid reloads with the normal list.

#### Edge Case

**PRF-E01 — Verify Print Quantity limits 1 to 99 on Generate Barcode**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. An APPROVED asset exists (for example the Land asset registered with Project '[015] Microfinance (Dabi)', Measurement 12.5, Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Generate Barcode'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial>.
  5. Click the button 'Search' and wait for the grid to reload.
  6. In the grid, tick the check box in the row of <Asset Serial>.
  7. In the field 'Default Print Quantity:' type 0.
  8. Click the button 'Set'.
  9. Read any message shown and read the 'Print Quantity' of the row.
  10. In the field 'Default Print Quantity:' delete the text and type 100.
  11. Click the button 'Set'.
  12. Read any message shown and read the 'Print Quantity' of the row.
  13. In the field 'Default Print Quantity:' delete the text so it is empty.
  14. Click the button 'Set'.
  15. Read any message shown and read the 'Print Quantity' of the row.
  16. In the field 'Default Print Quantity:' type 1.
  17. Click the button 'Set'.
  18. Read any message shown and read the 'Print Quantity' of the row.
  19. In the field 'Default Print Quantity:' delete the text and type 99.
  20. Click the button 'Set'.
  21. Read any message shown and read the 'Print Quantity' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Default Print Quantity = 0, 100, empty (invalid) and 1, 99 (boundaries, valid)
- Expected:
  1. For 1, System should accept the value and show 'Print Quantity' = "1" in the row.
  2. For 99, System should accept the value and show 'Print Quantity' = "99" in the row.
  3. For 0, System should refuse the value with a validation message (exact text to be confirmed) and not set the row to 0.
  4. For 100, System should refuse the value with a validation message (exact text to be confirmed) and not set the row to 100.
  5. For empty, System should refuse the value with a validation message (exact text to be confirmed).
- Basis: DERIVED (not yet run)
- Check also: In the row, type 100 directly in the 'Print Quantity' box and click 'Generate'. Record whether a PDF opens or a message is shown (behaviour to be confirmed).

**PRF-E02 — Verify Generate with no row ticked**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. The browser is showing no other open barcode PDF tab.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Generate Barcode'.
  3. Wait until the button 'Search' is visible.
  4. Check that no row check box in the grid is ticked (and the header check box is not ticked).
  5. Click the button 'Generate'.
  6. Wait for the toast message to appear and read it.
  7. Look at the browser tabs.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Ticked rows = none
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should open no PDF tab.
- Basis: DERIVED (not yet run)
- Check also: Tick the header check box (select all), then untick it again, and click 'Generate'. Expected: the same validation message as in step 6 and still no PDF tab.

**SPL-E01 — Verify Split Into boundary values 2 and 100 are accepted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2.
  5. Click the button 'Split' and count the lines of the result grid.
  6. Click the link 'Back'.
  7. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  8. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  9. In the field 'Split Into' type 100.
  10. Click the button 'Split' and count the lines of the result grid.
  11. Try to type a value in the 'Percentage' box of line 100.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2, then 100
- Expected:
  1. With 2 System should build 2 split lines (verified).
  2. With 100 System should build 100 split lines.
  3. System should show no red message in either case.
- Basis: VERIFIED (test_07) for 2; DERIVED (not yet run) for 100
- Check also: The last line (line 100) is still read-only. Expected: it cannot be typed in and takes the balance.

**SPL-E02 — Verify typing Split Into alone does not build the lines**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split. Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2.
  5. Do not click the button 'Split'. Press the Tab key and wait 3 seconds.
  6. Look at the form below the field.
  7. Click the button 'Split'.
  8. Look at the form again.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
- Expected:
  1. System should show no split lines before 'Split' is clicked.
  2. System should show 2 split lines after 'Split' is clicked.
- Basis: OBSERVED (catalog)
- Check also: The buttons 'Draft' and 'Submit' appear only with the grid. Expected: they are not shown before 'Split' is clicked.

**SPL-E03 — Verify Percentage with 3 decimals is rounded to 2**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2, click the button 'Split'.
  5. In the 'Percentage' box of line 1 type 40.123.
  6. Press the Tab key.
  7. Read 'Percentage', 'Measurement' and 'Written Down Value' of line 1 and line 2.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
  - Percentage (line 1) = 40.123
- Expected:
  1. System should show line 1 Percentage 40.12.
  2. System should show line 2 Percentage 59.88.
  3. System should show Measurement 5.01 (line 1) and 7.49 (line 2).
  4. System should show Written Down Value 10030 (line 1) and 14970 (line 2).
- Basis: OBSERVED (catalog)
- Check also: Read the 'Grand Total:' row. Expected: 100 / 25000.00 / 12.50 for Percentage / Written Down Value / Measurement.

**SPL-E04 — Verify the last line is read-only**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2, click the button 'Split'.
  5. Click into the 'Percentage' box of line 1 and type 50.
  6. Click into the 'Measurement' box of line 1 and check that it can be edited.
  7. Click into the 'Percentage' box of line 2 and try to type 10.
  8. Click into the 'Measurement' box of line 2 and try to type 10.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
  - Percentage (line 1) = 50
  - Value tried in line 2 = 10
- Expected:
  1. System should let the user edit 'Percentage' and 'Measurement' of line 1.
  2. System should keep 'Percentage' of line 2 (the last line) read-only; nothing can be typed.
  3. System should keep 'Measurement' of line 2 (the last line) read-only; nothing can be typed.
- Basis: VERIFIED (test_07)
- Check also: After step 8 read line 2. Expected: it still shows the balance (50 / 6.25).

**SPL-E05 — Verify unequal split percentages are allowed**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2, click the button 'Split'.
  5. In the 'Percentage' box of line 1 type 40.
  6. Press the Tab key.
  7. Read 'Percentage', 'Measurement' and 'Written Down Value' of line 1 and line 2.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
  - Percentage (line 1) = 40
- Expected:
  1. System should show line 1: Percentage 40, Measurement 5.00, Written Down Value 10000.
  2. System should show line 2: Percentage 60, Measurement 7.50, Written Down Value 15000.
  3. System should accept the unequal split without any message (the split need not be equal).
- Basis: OBSERVED (catalog)
- Check also: Read the 'Grand Total:' row. Expected: 100 / 25000 / 12.5.

**SPL-E06 — Verify a percentage of 100 or more in line 1 is handled**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2, click the button 'Split'.
  5. In the 'Percentage' box of line 1 type 100 and press the Tab key. Read the toast (if any), and 'Percentage', 'Measurement' and 'Written Down Value' of both lines.
  6. In the 'Percentage' box of line 1 type 101 and press the Tab key. Read the toast (if any) and both lines again.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
  - Percentage (line 1) = 100, then 101
- Expected:
  1. System should show a validation message or a refusal for 100 and for 101 (exact behaviour to be confirmed).
  2. System should not make line 2 negative.
  3. The Written Down Value of each line should be at least 1 before Submit.
- Basis: DERIVED (not yet run)
- Check also: Do not click 'Submit' with these values. If tried, record the message (the source suggests "Written down value should not be less than 1").

#### Business

**PRF-B01 — Verify Project value format differs between grid and popup**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module can be opened.
  3. A newly APPROVED asset exists that was registered with Project Name & Number '[015] Microfinance (Dabi)' (for example the Furniture asset 'Cabinet Table', Quantity 1, Unit Price(TK.) 25000). Its Asset Serial is <Asset Serial>.
- Steps:
  1. Open the Fixed Asset module.
  2. Click the text 'Asset Profile' in the module menu bar, then click the link 'Asset Serial Global List'.
  3. Wait until the button 'Search' is visible.
  4. In the field 'Asset Serial:' type <Asset Serial> and click the button 'Search'.
  5. Wait for the grid to reload.
  6. In the grid, read the cell under the column 'Project Name' of the row of <Asset Serial> (written below as <Grid Project>).
  7. In the grid, click the blue link <Asset Serial> in the column 'Asset Serial'.
  8. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  9. Read the field 'Project' (written below as <Popup Project>).
  10. Click the button 'Close' of the popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Project (registered) = [015] Microfinance (Dabi)
- Expected:
  1. System should show in the grid a 'Project Name' that identifies the registered project (seen: "[015] Microfinance (Dabi)").
  2. System should show in the popup a 'Project' that identifies the same project (seen: "Microfinance (Dabi)").
  3. The text format may differ between <Grid Project> and <Popup Project>; both must name the registered project.
- Basis: OBSERVED (catalog)
- Check also: Open the 'Generate Barcode' screen, search <Asset Serial> and read the column 'Project Name'. Expected: it names the same project.

**SPL-B01 — Verify the split form shows the asset details**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split: Measurement 12.50, quantity 1, unit price 25000 (Written Down Value 25000.00, Accumulated Depreciation 0.00). Its Asset Serial is known (written below as <Land Serial>).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>.
  3. Click the button 'Search'.
  4. In the grid, look at the row of <Land Serial> and read the 'Action' column: a green button 'SPLIT' should be there.
  5. Click the green button 'SPLIT' in that row.
  6. Wait for the section headed 'Asset Split' (with a 'Back' link) to appear.
  7. Read the fields 'Asset Serial', 'Asset Item Name', 'Measurement', 'Asset Written Down Value' and 'Accumulated Depreciation'.
  8. Look at the field 'Split Into' and try to type in it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. System should show a green button 'SPLIT' in the row of <Land Serial>.
  2. System should open the 'Asset Split' form with a 'Back' link.
  3. System should show Asset Serial = <Land Serial>.
  4. System should show Asset Item = "Land".
  5. System should show Measurement = "12.50".
  6. System should show Asset Written Down Value = "25000.00".
  7. System should show Accumulated Depreciation = "0.00".
  8. System should show the field 'Split Into' empty and editable.
- Basis: VERIFIED (test_07)
- Check also: In the same pass read 'Project', 'Branch' and 'Item Specification' on the form. Expected: they show the values entered when the Land was registered, and these boxes cannot be edited.

**SPL-B02 — Verify 2 lines are built and the last percentage auto-fills**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split: Measurement 12.50, Written Down Value 25000.00, Accumulated Depreciation 0.00. Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>.
  3. Click the button 'Search'.
  4. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  5. In the field 'Split Into' type 2.
  6. Click the button 'Split'.
  7. In the result grid read the number of lines and the 'Percentage' and 'Measurement' of each line.
  8. In the 'Percentage' box of line 1 type 50.
  9. Press the Tab key.
  10. Read 'Percentage', 'Measurement' and 'Written Down Value' of line 1 and line 2, and the 'Grand Total:' row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
  - Percentage (line 1) = 50
- Expected:
  1. After clicking 'Split', System should show a result grid with 2 lines.
  2. System should show 'Percentage' and 'Measurement' of both lines empty until typed.
  3. After Tab, System should show line 1: Percentage 50, Measurement 6.25, Written Down Value 12500.
  4. After Tab, System should show line 2: Percentage 50, Measurement 6.25, Written Down Value 12500.
  5. System should show 'Grand Total:' Percentage 100, Written Down Value 25000, Measurement 12.5.
- Basis: VERIFIED (test_07)
- Check also: Click into the 'Percentage' box of line 2. Expected: it is read-only and cannot be typed in.

**SPL-B03 — Verify Reset clears the typed values but keeps the lines**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2.
  5. Click the button 'Split'.
  6. In the 'Percentage' box of line 1 type 50 and press the Tab key.
  7. Read that line 1 shows 50 / 6.25 / 12500 and the 'Grand Total:' row shows 100 / 25000 / 12.5.
  8. Click the button 'Reset' on the form.
  9. Read 'Percentage', 'Measurement' and 'Written Down Value' of both lines, the 'Grand Total:' row and the field 'Split Into'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
  - Percentage (line 1) = 50
- Expected:
  1. Before Reset, System should show line 1 Percentage 50, Measurement 6.25, Written Down Value 12500.
  2. After Reset, System should set Percentage, Measurement and Written Down Value of both lines to 0.
  3. After Reset, System should set the 'Grand Total:' values to 0.
  4. After Reset, System should still show the 2 lines.
  5. After Reset, System should still show 2 in the field 'Split Into'.
- Basis: VERIFIED (test_07)
- Check also: After Reset type 50 in the 'Percentage' box of line 1 and press Tab. Expected: line 1 shows 50 / 6.25 / 12500 and line 2 shows Percentage 50, so the lines still calculate after Reset.

**SPL-B04 — Verify Back closes the form without a split**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split. Its Asset Serial is <Land Serial>.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Split Into' type 2.
  5. Click the button 'Split' and wait until 2 lines show in the result grid.
  6. Click the link 'Back'.
  7. Look at the screen.
  8. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  9. Read the 'Action' column of the row of <Land Serial>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Split Into = 2
- Expected:
  1. System should close the 'Asset Split' form and show the search screen again.
  2. System should list <Land Serial> again after the search.
  3. System should still show the green button 'SPLIT' in that row.
  4. System should not have created any split (nothing is saved).
- Basis: VERIFIED (test_07)
- Check also: Open the menu link 'Asset Serial Split List' and search <Land Serial>. Expected: "No data available in table".

**SPL-B05 — Verify the PENDING row on Asset Serial Split List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> (the same user who submitted the split).
  2. The Fixed Asset module is open.
  3. A PENDING split exists for a Land with Asset Serial <Land Serial>: Split Into 2, Remarks "AUTOMATION_TEST split note", line 1 = 50.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split List'.
  2. Read the column headings of the grid.
  3. In the field 'Asset Serial' type <Land Serial>.
  4. Click the button 'Search'.
  5. Read every cell of the row shown, including the columns 'Asset Split No.', 'Asset Group', 'Asset Serial No.', 'Split Into', 'Remarks', 'Created By', 'Status', 'Approved By' and 'Approval Date'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Remarks (expected in row) = AUTOMATION_TEST split note
- Expected:
  1. System should show these columns in order: SL, Asset Split No., Asset Group, Project Name, Department Name, Asset Serial No., Split Into, Remarks, Created By, Status, Approved By, Approval Date.
  2. System should show one row with an 'Asset Split No.' number.
  3. System should show 'Asset Group' = "Land".
  4. System should show 'Asset Serial No.' = <Land Serial>.
  5. System should show 'Split Into' = 2.
  6. System should show 'Remarks' = "AUTOMATION_TEST split note".
  7. System should show 'Created By' = the user who submitted the split.
  8. System should show 'Status' = "PENDING".
  9. System should show 'Approved By' and 'Approval Date' empty.
- Basis: VERIFIED (test_08)
- Check also: Read the line under the grid. Expected: "Showing 1 to 1 of 1 entries" for the serial filter.

**SPL-B06 — Verify the Asset Split View popup from Split List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A PENDING split exists for a Land with Asset Serial <Land Serial>: Measurement 12.50, Net Asset Value 25000.00, Split Into 2, Remarks "AUTOMATION_TEST split note", line 1 = 50.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split List'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row shown, click the blue number link under 'Asset Split No.'.
  4. Wait for the popup 'Asset Split View'.
  5. Read the fields Asset Serial, Asset Item Name, Split Into, Measurement, Asset Written Down Value, Accumulated Depreciation and Remarks.
  6. Read the lines of the grid in the popup, and look whether new Asset Serials are listed anywhere in the popup.
  7. Click the button 'Close'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. System should open the popup titled "Asset Split View".
  2. System should show Asset Serial = <Land Serial> and Asset Item Name = "Land".
  3. System should show Split Into = 2.
  4. System should show Measurement = "12.50".
  5. System should show Asset Written Down Value (Net Asset Value) = "25000.00".
  6. System should show Accumulated Depreciation = "0.00".
  7. System should show Remarks = "AUTOMATION_TEST split note".
  8. System should show 2 split lines.
  9. System should not list any new Asset Serial yet.
  10. System should close the popup after 'Close'.
- Basis: VERIFIED (test_08)
- Check also: Read the 'Grand Total:' row of the popup grid. Expected: Percentage 100, Written Down Value 25000.00, Measurement 12.50.

**SPL-B07 — Verify Split List filters Created By, Reset and Records per page**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. The Asset Serial Split List contains several rows, at least one created by a known user (written below as <Creator Name>).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split List'.
  2. In the field 'Created By' type the first 3 or more letters of <Creator Name>.
  3. Click the small magnifier icon next to the 'Created By' box and wait for the suggestion to appear.
  4. Click the suggestion.
  5. Click the button 'Search'.
  6. In the grid read the column 'Created By' of every row.
  7. Click the button 'Reset'.
  8. Read the fields 'Asset Serial' and 'Created By' and the number of rows in the grid.
  9. In 'Records per page' choose 10 and count the rows shown; then choose 20, 30, 50 and 100 in turn and count the rows each time.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Created By (typed) = first 3 or more letters of <Creator Name>
  - Records per page = 10, 20, 30, 50, 100
- Expected:
  1. System should show suggestions only after the magnifier icon is clicked.
  2. System should list only rows whose 'Created By' is <Creator Name> after 'Search'.
  3. System should empty 'Asset Serial' and 'Created By' after 'Reset'.
  4. System should reload the full grid after 'Reset'.
  5. System should show at most 10, 20, 30, 50, 100 rows for the chosen page sizes.
- Basis: OBSERVED (catalog; the matching automated test is not confirmed)
- Check also: The 'Approved By' filter was never run. Type 3 or more letters of an approver name in 'Approved By', click the magnifier icon, pick the suggestion and click 'Search'. Expected: only rows approved by that user show (not yet seen).

**SPL-B08 — Verify the Split Approval List shows the PENDING split**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> as a user who can open the Split Approval List (the approver).
  2. The Fixed Asset module is open.
  3. A PENDING split exists for a Land with Asset Serial <Land Serial> (Split Into 2, created by <Creator Name>).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split Approval List'.
  2. Click the button 'Search' (with no filter) and read the column headings of the grid.
  3. In the field 'Asset Serial' type <Land Serial>.
  4. Click the button 'Search'.
  5. Read every cell of the row shown.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. System should show 12 headings in order: SL, Asset Split No., Asset Group, Project Name, Department Name, Asset Serial No., Split Into, Remarks, Created By, Status, Approved By, Approval Date (the checkbox column has no heading).
  2. System should show a row for <Land Serial> with an 'Asset Split No.'.
  3. System should show 'Asset Group' = "Land" and 'Split Into' = 2.
  4. System should show 'Created By' = <Creator Name>.
  5. System should show 'Status' = "PENDING".
  6. System should show 'Approved By' and 'Approval Date' empty.
- Basis: VERIFIED (test_09)
- Check also: Click the 'Reset' button below the grid. Expected: ticked rows are cleared (no checkbox ticked).

**SPL-B09 — Verify the Asset Split View popup from the Approval List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> as the approver.
  2. The Fixed Asset module is open.
  3. A PENDING split exists for a Land with Asset Serial <Land Serial>: Measurement 12.50, Written Down Value 25000.00, Accumulated Depreciation 0.00, Split Into 2.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split Approval List'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row shown, click the blue number link under 'Asset Split No.'.
  4. Wait for the popup 'Asset Split View'.
  5. Read the fields Asset Serial, Split Into, Measurement, Asset Written Down Value and Accumulated Depreciation, and count the lines of the grid.
  6. Click the button 'Close'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. System should open the popup titled "Asset Split View".
  2. System should show Asset Serial = <Land Serial>.
  3. System should show Split Into = 2.
  4. System should show Measurement = "12.50".
  5. System should show Written Down Value = "25000.00".
  6. System should show Accumulated Depreciation = "0.00".
  7. System should show 2 split lines.
  8. System should close the popup after 'Close'.
- Basis: VERIFIED (test_09)
- Check also: Read the popup buttons. Expected: besides 'Close' the popup also holds 'Approve' and 'Reject' buttons (do not click them).

**SPL-B10 — Verify approval creates one new serial per split line**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A Land with Asset Serial <Land Serial> (Measurement 12.50, Written Down Value 25000.00) has an APPROVED split of 2 lines, made with Percentage 40.123 typed in line 1 (stored as 40.12; line 2 = 59.88).
- Steps:
  1. Open the Asset Registration Approval List (menu path to be confirmed; it is under the menu 'Registration' of the Fixed Asset module).
  2. In the filter 'Registration Type' choose "AAQ" and in 'Status' choose "APPROVED", then click the button 'Search'.
  3. In the grid take the top (newest) row and click its 'Registration Number' link (written below as <New Registration Number>).
  4. In the popup 'Asset Registration View' click the tab 'Asset Serials'.
  5. Read the 'Asset Serial' column of the grid 'Registered Asset Serials' (written below as <New Serial 1> and <New Serial 2>).
  6. Close the popup.
  7. Click the menu 'Asset Profile', then the link 'Asset Serial Global List'.
  8. In the field 'Asset Serial' type <New Serial 1> and click the button 'Search'. Read 'Assign Status' and 'Utilization Status'.
  9. In the field 'Asset Serial' type <New Serial 2> and click the button 'Search'. Read 'Assign Status' and 'Utilization Status'.
  10. Click the Asset Serial link of each new serial and read the field 'Measurement' on the tab 'Details' (and the reference asset serial, if shown).
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Registration Type (filter) = AAQ
  - Status (filter) = APPROVED
  - Asset Serial (filter) = <New Serial 1>, then <New Serial 2>
- Expected:
  1. System should show a new registration of 'Registration Type' "AAQ" with Status "APPROVED".
  2. System should show 2 new serials on the tab 'Asset Serials' (one per split line).
  3. System should show that neither new serial equals <Land Serial>.
  4. System should list each new serial on the Asset Serial Global List with 'Assign Status' "UNASSIGNED" and 'Utilization Status' "IN_USE".
  5. System should show <Land Serial> as the reference asset of each new serial.
  6. System should show Measurement 5.01 for one serial and 7.49 for the other.
- Basis: VERIFIED (test_09)
- Check also: Read the current value of each new serial. Expected: 10030.00 and 14970.00 (sum 25000.00).

**SPL-B11 — Verify the original serial is gone after approval**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A Land with Asset Serial <Land Serial> has an APPROVED split.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Global List'.
  2. In the field 'Asset Serial' type <Land Serial>.
  3. Click the button 'Search' and read the grid.
  4. Click the menu 'Asset Profile', then the link 'Asset Serial Split'.
  5. In the field 'Asset Serial' type <Land Serial>.
  6. Click the button 'Search' and read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. System should show "No data available in table" on the Asset Serial Global List.
  2. System should show "No data available in table" on the Asset Serial Split screen.
- Basis: VERIFIED (test_09)
- Check also: Open 'Asset Serial Split List' and search <Land Serial>. Expected: the row still shows with Status "APPROVED".

**SPL-B12 — Verify the original serial remains on the Global List while the split is only PENDING**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A Land with Asset Serial <Land Serial> has a split in Status "PENDING" (submitted, not yet approved).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Global List'.
  2. In the field 'Asset Serial' type <Land Serial>.
  3. Click the button 'Search' and read the grid.
  4. Click the menu 'Asset Profile', then the link 'Asset Serial Split'.
  5. In the field 'Asset Serial' type <Land Serial>.
  6. Click the button 'Search' and read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. System should list <Land Serial> on the Asset Serial Global List with 'Assign Status' "UNASSIGNED" and 'Utilization Status' "IN_USE".
  2. System should show "No data available in table" on the Asset Serial Split screen.
- Basis: OBSERVED (project notes, status table)
- Check also: Open 'Asset Serial Split List' and search <Land Serial>. Expected: the row shows Status "PENDING".

**SPL-B13 — Verify the irreversible warning is respected in the test plan**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A "used-up" Land with Asset Serial <Used Land Serial> exists: its split was already submitted (Status "PENDING" or "APPROVED"). There is no undo for a submitted or approved split, so only a disposable test Land may be used.
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Used Land Serial>.
  3. Click the button 'Search'.
  4. Read the grid and look for a green button 'SPLIT'.
  5. Look on the screen for any button or link that could undo or cancel the earlier split.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Used Land Serial>
- Expected:
  1. System should show "No data available in table" for <Used Land Serial>, so no button 'SPLIT' is available.
  2. System should offer no undo or cancel for a submitted split on this screen.
- Basis: DERIVED (not yet run)
- Check also: Open 'Asset Serial Split List' and search <Used Land Serial>. Expected: the earlier split row is still listed with its Status.

**SPL-B14 — Verify a new split serial can be used in a later process**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A Land split is APPROVED and produced new serials; one of them is written below as <New Serial 1> (UNASSIGNED, IN_USE).
- Steps:
  1. Click the menu 'Asset Transaction' in the Fixed Asset module, then click the link 'Asset Assign'.
  2. In the field 'Asset Serial' type <New Serial 1>.
  3. Click the search button next to the box and wait for the suggestion to appear.
  4. Click the suggestion.
  5. Read the screen (the asset details and the 'Asset List' grid, if the asset is added).
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <New Serial 1>
- Expected:
  1. System should show one suggestion for <New Serial 1> (format serial, item, sub category, category, group).
  2. System should accept <New Serial 1> as an asset with 'Assign Status' "UNASSIGNED".
  3. System should show no error message.
- Basis: DERIVED (not yet run)
- Check also: Do not save the assignment. Search <New Serial 1> on the 'Asset Serial Global List' afterwards. Expected: 'Assign Status' is still "UNASSIGNED".

**SPL-B15 — Verify Reject on a PENDING split**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> as the approver.
  2. The Fixed Asset module is open.
  3. A Land with Asset Serial <Land Serial> has a split in Status "PENDING". This is a disposable test Land (the action may be irreversible).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split Approval List'.
  2. In the field 'Asset Serial' type <Land Serial>.
  3. Click the button 'Search'.
  4. Tick the checkbox in the first column of the row shown.
  5. Click the button 'Reject'.
  6. Wait for a toast message and read it (note whether a dialog or comment box opens).
  7. Read the cell under the column 'Status' of the row.
  8. Click the menu 'Asset Profile', then the link 'Asset Serial Global List', type <Land Serial> in 'Asset Serial' and click 'Search'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. Result is not known (success text and final status to be confirmed). Record the message, the dialog (if any) and the 'Status' value shown.
  2. System should still list the original serial <Land Serial> on the Asset Serial Global List.
- Basis: DERIVED (not yet run)
- Check also: Search <Land Serial> on the 'Asset Serial Split' screen. Record whether a green button 'SPLIT' shows again (not yet known).

**SPL-B16 — Verify Draft on the split form**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>. It is disposable (Draft may use it up).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. In the field 'Remarks' type AUTOMATION_TEST split note.
  5. In the field 'Split Into' type 2, click the button 'Split'.
  6. In the 'Percentage' box of line 1 type 50 and press the Tab key.
  7. Click the button 'Draft'.
  8. Wait for a toast message and read it.
  9. Open 'Asset Serial Split List' and search <Land Serial>; read the 'Status' cell of the row, if any.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Remarks = AUTOMATION_TEST split note
  - Split Into = 2
  - Percentage (line 1) = 50
- Expected:
  1. The status DRAFT is expected from the button name, but the screen behaviour and message are not yet known (to be confirmed). Record the message and where the screen goes.
  2. Record whether a row with Status "DRAFT" shows on the Split List.
- Basis: DERIVED (not yet run)
- Check also: Search <Land Serial> on the 'Asset Serial Split' screen. Record whether a green button 'SPLIT' still shows.

**SPL-B17 — Verify Submit without Remarks**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Land asset exists that has never been split (Measurement 12.50, Written Down Value 25000.00). Its Asset Serial is <Land Serial>. It is disposable (Submit is irreversible).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>, click the button 'Search'.
  3. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  4. Leave the field 'Remarks' empty.
  5. In the field 'Split Into' type 2, click the button 'Split'.
  6. In the 'Percentage' box of line 1 type 50 and press the Tab key.
  7. Click the button 'Submit' (no confirm box appears).
  8. Wait for a toast message and read it.
  9. Open 'Asset Serial Split List' and search <Land Serial>; read the 'Status' and 'Remarks' of the row, if any.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Remarks = (empty)
  - Split Into = 2
  - Percentage (line 1) = 50
- Expected:
  1. Not known whether Remarks is required. Record what the system does (message text, or "Asset split submitted successfully").
  2. If it is accepted, record that the Split List row has Status "PENDING" with empty 'Remarks'.
- Basis: DERIVED (not yet run)
- Check also: When the Split Into box has 2 and Remarks is empty, click 'Split' only. Expected: the grid is built and no toast shows (Remarks is not checked at Split time).

**SPL-B18 — Verify Submit creates a PENDING split (irreversible)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A fresh APPROVED Land asset that has never been split exists: Measurement 12.50, quantity 1, unit price 25000 (Written Down Value 25000.00, Accumulated Depreciation 0.00). Its Asset Serial is <Land Serial>. It is a disposable test asset (Submit has no confirm box and cannot be undone).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split'.
  2. In the field 'Asset Serial' type <Land Serial>.
  3. Click the button 'Search'.
  4. In the row of <Land Serial> click the green button 'SPLIT'. Wait for the 'Asset Split' form.
  5. In the field 'Remarks' type AUTOMATION_TEST split note.
  6. In the field 'Split Into' type 2.
  7. Click the button 'Split'.
  8. In the 'Percentage' box of line 1 type 50.
  9. Press the Tab key.
  10. Click the button 'Submit' (no confirm box appears).
  11. Wait for the toast message and read it (it may fade quickly).
  12. In the field 'Asset Serial' type <Land Serial> and click the button 'Search'.
  13. Click the menu 'Asset Profile', then the link 'Asset Serial Split List'.
  14. In the field 'Asset Serial' type <Land Serial> and click the button 'Search'. Read the cell under 'Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
  - Remarks = AUTOMATION_TEST split note
  - Split Into = 2
  - Percentage (line 1) = 50
- Expected:
  1. System should show the success message "Asset split submitted successfully".
  2. System should return to the list screen of Asset Serial Split.
  3. System should show "No data available in table" when <Land Serial> is searched on Asset Serial Split.
  4. System should show a row for <Land Serial> on Asset Serial Split List with 'Status' "PENDING".
- Basis: VERIFIED (test_07)
- Check also: Open 'Asset Serial Global List' and search <Land Serial>. Expected: the original serial is still listed ("UNASSIGNED", "IN_USE") until approval.

**SPL-B19 — Verify Approve sets the split to APPROVED (irreversible)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> as the approver.
  2. The Fixed Asset module is open.
  3. A split in Status "PENDING" exists for the Land with Asset Serial <Land Serial> (Split Into 2, line 1 = 50). It is a disposable test asset (Approve has no confirm box and cannot be undone).
- Steps:
  1. Click the menu 'Asset Profile' in the Fixed Asset module, then click the link 'Asset Serial Split Approval List'.
  2. In the field 'Asset Serial' type <Land Serial>.
  3. Click the button 'Search'.
  4. Tick the checkbox in the first column of the row shown.
  5. Click the button 'Approve' (no confirm box and no comment box appear).
  6. Wait for the toast message and read it (it may fade quickly).
  7. Within about 3 seconds read the cells under 'Status', 'Approved By' and 'Approval Date' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial (filter) = <Land Serial>
- Expected:
  1. System should show the success message "Asset split approved successfully" (it may fade, and may show a trailing full stop).
  2. System should show 'Status' = "APPROVED" within about 3 seconds.
  3. System should show 'Approved By' = the name of the approver.
  4. System should show 'Approval Date' in the format dd/mm/yyyy (the ERP business date, not always today).
  5. System should keep the row in the list.
- Basis: VERIFIED (test_09)
- Check also: Click the menu 'Asset Profile', then 'Asset Serial Global List', and search <Land Serial>. Expected: "No data available in table".

**5. When a CR changes something here — what to re-check**
- A field is added or changed on the Asset Profile Details popup or a Change popup: PRF-P02, PRF-P06 to PRF-P10, PRF-N02 to PRF-N05.
- A new filter or a new column on Global List, Barcode or Pending list: PRF-P01, PRF-P03, PRF-P04, PRF-P05, PRF-P11, PRF-P14, PRF-P15, PRF-P17.
- A Utilization Status value is added or removed: PRF-P04, PRF-P08, PRF-P09, PRF-N05.
- The Print Quantity limit changes: PRF-P11, PRF-P12, PRF-E01.
- The Split Into limit (2 to 100) changes: SPL-N02, SPL-N03, SPL-N04, SPL-E01.
- Split percentage or rounding rule changes (for example equal parts forced): SPL-B02, SPL-B03, SPL-E03, SPL-E04, SPL-E05, SPL-E06.
- The status flow or approval rule of a split changes (for example a comment box or confirm box): SPL-B18, SPL-B05, SPL-B08, SPL-B19, SPL-B15, SPL-B16.
- Which assets are splittable changes: SPL-N01, SPL-B01, SPL-B13.
- A message text changes: scenarios that quote it, mainly PRF-N02 to PRF-N04, SPL-N01 to SPL-N03, SPL-N06, SPL-B18, SPL-B19.
- What approval creates (new serials, registration type): SPL-B10, SPL-B11, SPL-B14.
- A column is added to the Split List or Pending list: PRF-P14, PRF-P17, SPL-B05, SPL-B08.

**6. Questions to ask the BA**
- What happens when Reject is clicked on a split: final status, message, and does the original asset return to normal use?
- What does Draft do on the split form, and can a Draft be opened again?
- Is Remarks mandatory when submitting a split?
- Should splits be in equal parts (the old manual says so) or any percentage (the live screen allows this)?
- Is there any limit on the Written Down Value of a single split line beyond "at least 1"?
- What are the exact on-screen messages for Submit errors (empty or invalid percentage, wrong totals)?
- What happens to an asset with a Utilization Status other than IN_USE (for example DAMAGE) when a split is requested?
- Why did one Export run on the Pending list not download in 30 seconds? Is there a size limit or delay?
- Which Print Quantity validation applies for 0, 100 or empty, and what message?
- Which process opens a row in the Pending list and when does the row leave it?
- Does the Approved By filter on Split List work as the Created By filter does?
- Can a split be applied to an asset that is already ASSIGNED or has depreciation?

---

### Asset Transaction — Assign, Acknowledge, Internal Movement, Un-Assign

**1. What this area is, in plain words**

An approved asset starts life UNASSIGNED. An assigner gives it to an employee on the Asset Assign screen. After an approver approves, the asset becomes ASSIGNED to that employee. The employee can then confirm receipt on the Asset Assign Acknowledgement screen. This confirmation does not change the asset.

While the asset is ASSIGNED, it can be moved to a new building and floor on Asset Internal Movement. The list screens call this type TRANSFER. When the asset is taken back, Asset Un Assign records a hand-over employee and the asset becomes UNASSIGNED again.

Every type has two ways to be created. In the Draft path the user clicks Draft, then opens Transaction List, clicks Edit and Submits. In the Submit-only path the user clicks Submit straight from the form. Both end in the Transaction Approval List, where an approver approves.

Before this area: the asset is registered and approved. After this area: the asset can go on to Asset Expense and Write-off.

**2. Before you test: getting the right starting state**

| State needed | Why | How to get it in short human steps |
|---|---|---|
| An APPROVED, UNASSIGNED furniture asset (note the Asset Serial) | Needed for every Asset Assign scenario | Register furniture (Registration > Asset Registration by AAQ), Submit, approve it in Asset Registration Approval List. Open Asset Serial Global List, search the serial and check Assign Status = UNASSIGNED. |
| A second UNASSIGNED asset | Needed to test the Submit-only path separately from the Draft path | Same steps as above, with a second registration. |
| An ASSIGNED asset (note the serial and the holder) | Needed for Internal Movement, Un Assign and the "ASSIGNED" checks | Take an UNASSIGNED asset, assign it to the test employee (Submit, then Approve in Transaction Approval List). Check Global List shows ASSIGNED. |
| An approved ASSIGN waiting for acknowledgement | Needed for the Acknowledgement scenarios | Assign the asset to the employee who will log in for the test. Approve it. Do not acknowledge it yet. |
| Two different employees | Needed for the hand-over rule on Un Assign | One employee is the assignee (current holder). The other is the hand-over employee. Both must be findable by Employee PIN. |
| Login as an assigner and as an approver | Creating and approving are separate steps | Use `<ERP Username> / <ERP Password>` for each role. In the test environment the logged-in user may also be the assignee. Confirm with the BA (see section 6). |
| At least one Transaction List row of each type and status (DRAFT, PENDING, APPROVED) | Needed for list filter scenarios | Create them through the scenarios above. If no rows exist, filter checks cannot be done. |

Tip: Keep one asset for the "Draft path" and a second for the "Submit-only path". Run the flows in this order: Assign, Acknowledge, Internal Movement, Un Assign.

**3. Rules and what to test for each**

| Rule (plain words) | Where it applies | Pass example | Fail / boundary examples to test |
|---|---|---|---|
| Only an UNASSIGNED asset can be assigned | Asset Assign | An UNASSIGNED asset is found by serial and loads | An ASSIGNED asset should not be offered for Assign (exact behaviour to be confirmed) |
| Only an ASSIGNED asset can be moved or un-assigned | Internal Movement, Un Assign | The ASSIGNED asset loads and shows its holder | An UNASSIGNED asset should not be offered (to be confirmed) |
| Asset details are read-only and auto-filled from the asset | All three forms | Item, Sub Category, Category, Group, Project and Previous Assign Status fill after choosing the serial | Typing in these fields has no effect |
| The serial must be chosen from the suggestion list | All three forms | Type serial, click the search icon, click the suggestion | Typing a serial only, without clicking the suggestion, does not fill the form |
| An employee is required | Assign (assignee), Un Assign (hand-over), Internal Movement (Internal Movement To) | Employee PIN and Employee Name filled | Click Draft with no employee: "This field is required", nothing saved |
| The hand-over employee must differ from the current holder | Un Assign | A different employee is accepted | The current holder: "Asset assigned to same employee!" |
| Branch Name is fixed to the logged-in user's branch | All three forms | Head Office [ BDHO ] shown and not editable | Typing in it is not possible |
| Transaction date is a read-only business date | All three forms | Shown dd-mm-yyyy on the form, dd/mm/yyyy in the Details popup | Editing is not possible |
| Building and Floor choose the new location | Internal Movement | Building Head Office, then the first floor | Floor stays empty until a Building is chosen. Whether Submit without Building and Floor is blocked is not known. |
| Draft makes an editable row; Submit makes it PENDING and not editable | Transaction List | DRAFT row has an Edit link; after Submit it shows PENDING and no Edit | APPROVED and PENDING rows have no Edit link |
| A submitted-but-unapproved transaction locks the asset | All transaction screens | After Submit, the asset is in a pending process | Searching its serial on another transaction screen shows "No asset found" |
| Order of work: Internal Movement before Un Assign | Un Assign | Move first, then un-assign | A submitted Un Assign locks the asset, so a movement cannot be started until it is decided |
| Approve changes the asset | Approval List | Assign approved: ASSIGNED. Movement approved: stays ASSIGNED with new Building and Floor. Un Assign approved: UNASSIGNED | Before Approve the asset does not change |
| Acknowledgement is not needed for ASSIGNED | Acknowledgement | The asset is ASSIGNED right after Approve | Acknowledging does not change the asset (still ASSIGNED) |
| A user acknowledges only own pending rows | Acknowledgement | Own rows only in the Pending grid | Never tick the select-all box: it also ticks other people's assignments |
| An approved transaction cannot be decided again | Approval List | No Comment box and no Approve button | Looking for Approve on an APPROVED row finds none |
| Search by Employee Pin loads all of that employee's assets | Internal Movement, Un Assign | All assets of that employee appear in the Asset List | Unwanted rows must be removed before saving |

**4. Scenario catalogue**

#### Positive

**TRX-P01 — Verify the Asset Assign form shows the asset details after choosing the serial**
- Precondition:
  1. The user (assigner) is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available on the home page.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists, and its Asset Serial is known (written below as <Asset Serial>).
  4. In 'Asset Serial Global List' this asset shows Item 'Cabinet Table', Sub Category 'Wooden Furniture', Category 'Furniture', Group 'Furniture and Fixture', Project '[015] Microfinance (Dabi)' and Assign Status 'UNASSIGNED'.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon on the right of the 'Asset Serial' box.
  6. Wait for the suggestion list to appear under the box (one suggestion starting with <Asset Serial>).
  7. Click that suggestion.
  8. Read the fields 'Asset Item Name', 'Sub Category', 'Category', 'Group', 'Project' and 'Previous Assign Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expected item = Cabinet Table / Wooden Furniture / Furniture / Furniture and Fixture / Microfinance (Dabi)
- Expected:
  1. System should show 'Cabinet Table' in 'Asset Item Name'.
  2. System should show 'Wooden Furniture' in 'Sub Category'.
  3. System should show 'Furniture' in 'Category'.
  4. System should show 'Furniture and Fixture' in 'Group'.
  5. System should show 'Microfinance (Dabi)' in 'Project'.
  6. System should show 'UNASSIGNED' in 'Previous Assign Status'.
  7. All values should match the row of the asset in 'Asset Serial Global List'.
- Basis: VERIFIED (test_10)
- Check also: Click into 'Asset Item Name' and try to type "abc". Expected: the text is not accepted (the field is read-only).

**TRX-P02 — Verify the auto-filled asset fields on Asset Assign are read-only**
- Precondition:
  1. The user (assigner) is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists and its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon on the right of the 'Asset Serial' box.
  6. Click the suggestion that starts with <Asset Serial>.
  7. Wait until 'Asset Item Name' shows 'Cabinet Table'.
  8. Click into 'Asset Item Name' and try to type "abc".
  9. Click into 'Sub Category' and try to type "abc".
  10. Click into 'Category' and try to type "abc".
  11. Click into 'Group' and try to type "abc".
  12. Click into 'Project' and try to type "abc".
  13. Click into 'Previous Assign Status' and try to type "abc".
  14. Read the content of each of the six fields again.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Text tried in each field = abc
- Expected:
  1. System should not accept the typed text "abc" in 'Asset Item Name'.
  2. System should not accept the typed text in 'Sub Category'.
  3. System should not accept the typed text in 'Category'.
  4. System should not accept the typed text in 'Group'.
  5. System should not accept the typed text in 'Project'.
  6. System should not accept the typed text in 'Previous Assign Status'.
  7. All six fields should still show their auto-filled values (for example 'Cabinet Table' and 'UNASSIGNED').
- Basis: VERIFIED (test_10)
- Check also: Read the field 'Branch Name' and try to type in it. Expected: it shows 'Head Office [ BDHO ]' and cannot be edited.

**TRX-P03 — Verify Add to Grid moves the asset into the Asset List on Asset Assign**
- Precondition:
  1. The user (assigner) is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists and its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon on the right of the 'Asset Serial' box.
  6. Click the suggestion that starts with <Asset Serial>.
  7. Wait until 'Asset Item Name' shows 'Cabinet Table'.
  8. Click the button 'Add to Grid'.
  9. Look at the grid 'Asset List': read the columns 'Asset Serial' and 'Assign Status' of the new row.
  10. Look at the top section of the form: read the field 'Asset Item Name'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should add one row to the grid 'Asset List'.
  2. System should show <Asset Serial> under the column 'Asset Serial' of that row.
  3. System should show 'UNASSIGNED' under the column 'Assign Status' of that row.
  4. System should clear the top asset section (the field 'Asset Item Name' should be empty).
- Basis: VERIFIED (test_10)
- Check also: Read the row's 'Asset Item Name' cell. Expected: 'Cabinet Table'.

**TRX-P04 — Verify the assignee can be found by Employee PIN on Asset Assign**
- Precondition:
  1. The user (assigner) is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists and its Asset Serial is known (<Asset Serial>).
  4. The assignee (the employee who will receive the asset) is known and has an Employee PIN (written below as <Assignee PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon, then click the suggestion that starts with <Asset Serial>.
  6. Click the button 'Add to Grid' and check that the serial appears in the grid 'Asset List'.
  7. In the field 'Employee PIN Search' type the assignee's Employee PIN (see Test data).
  8. Click the small purple search icon on the right of the 'Employee PIN Search' box.
  9. Wait for the suggestion list (one suggestion in the form '<PIN>-<Employee name>').
  10. Click that suggestion.
  11. Read the fields 'Employee PIN', 'Employee Name' and 'Branch Name'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Assignee PIN>
- Expected:
  1. System should show one suggestion for the typed PIN.
  2. System should fill the field 'Employee PIN' with the assignee's PIN.
  3. System should fill the field 'Employee Name' with the assignee's name.
  4. System should show 'Head Office [ BDHO ]' in the field 'Branch Name' (the logged-in user's branch).
- Basis: VERIFIED (test_10)
- Check also: Try to type in 'Employee Name'. Expected: the text is not accepted (read-only).

**TRX-P05 — Verify Assign through the Draft path (Draft, Edit, Submit, Approve)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as the assigner and as the approver.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists and its Asset Serial is known (<Asset Serial>).
  4. The assignee is known and has an Employee PIN (<Assignee PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion that starts with <Asset Serial>.
  5. Click the button 'Add to Grid' and check that the serial is in the grid 'Asset List'.
  6. In the field 'Employee PIN Search' type the assignee's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In the field 'Note/Remarks' type "Assign note".
  8. Read the field 'Assigned Date' and note it (written below as <Assigned Date>, format dd-mm-yyyy).
  9. Click the button 'Draft'.
  10. Wait for the toast message to appear and read it.
  11. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  12. In 'Transaction Type' choose 'ASSIGN'. In 'Transaction Status' choose 'DRAFT'. Click the button 'Search'.
  13. In the grid, find the newest row whose asset list holds <Asset Serial>: click the link 'Details' on that row.
  14. Wait for the asset list in the popup to load, then read 'Transaction Type', 'Transaction Status', the employee PIN and name, the remarks and the transaction date.
  15. Click the button 'Close'.
  16. Click the link 'Edit' on the same row.
  17. Wait for the form to load and read 'Employee PIN', 'Employee Name', 'Note/Remarks' and 'Branch Name'.
  18. Click the button 'Submit'.
  19. Wait for the toast message to appear and read it. Then read the 'Transaction Status' of the row and check whether it has an 'Edit' link.
  20. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  21. In 'Transaction Type' choose 'ASSIGN'. In 'Transaction Status' choose 'PENDING'. Click the button 'Search'.
  22. Click the link 'Details' on the row whose asset list holds <Asset Serial>.
  23. Read the popup values and the buttons shown at the bottom.
  24. In the field 'Comment' type "Approved".
  25. Click the button 'Approve'.
  26. Wait for the toast message to appear and read it.
  27. In 'Transaction Status' choose 'APPROVED', click 'Search', then click 'Details' on the row holding <Asset Serial>.
  28. Read 'Transaction Status', 'Approved By' and 'Approval Date'. Click 'Close'.
  29. Click the menu 'Asset Serial Global List' (Fixed Asset), search for <Asset Serial>, and open the asset popup.
  30. Read 'Assign Status' and the assigned employee PIN and name.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Assignee PIN>
  - Note/Remarks = Assign note
  - Comment (approval) = Approved
  - Assigned Date = <Assigned Date> (read from the form)
  - Filters = Transaction Type 'ASSIGN'; Transaction Status 'DRAFT', then 'PENDING', then 'APPROVED'
- Expected:
  1. System should show the toast "Asset Assign Draft Successfully" at step 10.
  2. The Details popup of step 14 should show Transaction Type 'ASSIGN', status 'DRAFT', the assignee's PIN and name, remarks "Assign note" and the date <Assigned Date> in the format dd/mm/yyyy.
  3. The form opened by 'Edit' should show the assignee's PIN, name, the note "Assign note" and Branch Name 'Head Office [ BDHO ]' as saved.
  4. System should show the toast "Asset Assign Submit Successfully" at step 19.
  5. The row should then show status 'PENDING' and no 'Edit' link.
  6. The popup at step 23 should show the same values as before, status 'PENDING', and the Comment box with the buttons 'Approve', 'Reject' and 'Sendback'.
  7. System should show the toast "Approved successfully" at step 26 and close the popup.
  8. At step 28 the row should show status 'APPROVED' with 'Approved By' and 'Approval Date' filled.
  9. At step 30 the asset should show Assign Status 'ASSIGNED' with the assignee's PIN and name.
- Basis: VERIFIED (test_10)
- Check also: Compare the values in the Details popup (step 14) with what was typed on the form. Expected: they are identical.

**TRX-P06 — Verify Assign through the Submit-only path**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as the assigner and as the approver.
  2. The module 'Fixed Asset' is available.
  3. A second APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists and its Asset Serial is known (<Second Asset Serial>).
  4. The assignee is known and has an Employee PIN (<Assignee PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Second Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In the field 'Employee PIN Search' type the assignee's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In the field 'Note/Remarks' type "Assign note".
  8. Click the button 'Submit'.
  9. Wait for the toast message to appear and read it.
  10. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  11. In 'Transaction Type' choose 'ASSIGN'. In 'Transaction Status' choose 'PENDING'. Click the button 'Search'.
  12. Click the link 'Details' on the row whose asset list holds <Second Asset Serial>.
  13. Click the button 'Approve'.
  14. Wait for the toast message to appear and read it.
  15. Open 'Asset Serial Global List', search <Second Asset Serial> and open the asset popup.
  16. Read 'Assign Status' and the assigned employee.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Second Asset Serial>
  - Employee PIN Search = <Assignee PIN>
  - Note/Remarks = Assign note
- Expected:
  1. System should show the toast "Asset Assign Submit Successfully" at step 9.
  2. System should show the toast "Approved successfully" at step 14.
  3. System should show Assign Status 'ASSIGNED' for the asset.
  4. The asset popup should show the assignee's PIN and name.
- Basis: VERIFIED (test_10)
- Check also: In 'Transaction List' filter 'ASSIGN' and 'APPROVED'. Expected: the new row has status 'APPROVED' and no 'Edit' link.

**TRX-P07 — Verify the Acknowledgement screen layout**
- Precondition:
  1. The assignee (the employee an asset was assigned to) is logged into the ERP with <ERP Username> / <ERP Password> (the assignee's own login).
  2. The module 'Fixed Asset' is available.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign Acknowledgement'.
  3. Wait for the page to load completely.
  4. Read the heading and the column headers of the first grid.
  5. Read the heading and the column headers of the second grid.
  6. Look for an 'Acknowledge' button on the page.
  7. Look for any filter fields and a 'Search' button.
- Test data:
  - Login = <ERP Username> / <ERP Password> (assignee)
- Expected:
  1. System should show a grid titled 'Pending Asset Acknowledgement' with the columns 'SL', 'Transaction Type', 'Project', 'Branch', 'Assigned Employee', 'Assigned By', 'Approval Date' and 'Details'.
  2. System should show a grid titled 'My Assigned Asset' with the columns 'SL', 'Asset Serial', 'Asset Item Name', 'Branch Name', 'Project Name', 'Building Name', 'Floor Name', 'Room Name', 'Assigned Employee', 'Assigned By' and 'Utilization Status'.
  3. System should show a button 'Acknowledge' on the page.
  4. System should show no filter fields and no 'Search' button.
- Basis: VERIFIED (test_11)
- Check also: Open the 'Records per page' drop-down of the first grid. Expected: the options 10, 20, 30, 50, 100 are offered and 10 is selected by default.

**TRX-P08 — Verify the Pending list shows only the logged-in employee's assignments**
- Precondition:
  1. The assignee is logged into the ERP with <ERP Username> / <ERP Password> (the assignee's own login).
  2. At least one APPROVED Assign to this assignee is waiting and has not been acknowledged.
  3. The assignee's Employee PIN is known (<Assignee PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign Acknowledgement'.
  3. Wait for the page to load completely.
  4. In the grid 'Pending Asset Acknowledgement' count the rows.
  5. In each row read the cell under the column 'Assigned Employee'.
- Test data:
  - Login = <ERP Username> / <ERP Password> (assignee)
  - Assigned Employee expected = [<Assignee PIN>]
- Expected:
  1. System should show at least one row in 'Pending Asset Acknowledgement'.
  2. Every 'Assigned Employee' cell should contain the assignee's PIN in the form '[<Assignee PIN>] NAME'.
- Basis: VERIFIED (test_11)
- Check also: Read the column 'Assigned By' of the first row. Expected: it shows the assigner in the form '[username] name'.

**TRX-P09 — Verify the Details popup on the Acknowledgement screen**
- Precondition:
  1. The assignee is logged into the ERP with <ERP Username> / <ERP Password> (the assignee's own login).
  2. An APPROVED Assign of the asset <Asset Serial> to this assignee is waiting for acknowledgement, with the note "Assign note".
  3. The assignee's Employee PIN is known (<Assignee PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign Acknowledgement'.
  3. Wait for the page to load completely.
  4. In the grid 'Pending Asset Acknowledgement' click the link 'Details' on the first row.
  5. Wait for the asset list in the popup to load and read the 'Asset Serial' cell. If it is not <Asset Serial>, click 'Close' and repeat from step 4 on the next row until the popup holds <Asset Serial>.
  6. Read 'Transaction Type', 'Transaction Status', the employee PIN and name, and the remarks.
  7. Count the rows of the asset list in the popup.
  8. Note the total N in the line 'Showing x to y of N entries' under the pending grid (before the popup, or after closing).
  9. Click the button 'Close' (do not click 'Acknowledge').
  10. Read the total N again.
- Test data:
  - Login = <ERP Username> / <ERP Password> (assignee)
  - Asset Serial = <Asset Serial>
  - Remarks expected = Assign note
- Expected:
  1. System should show Transaction Type 'ASSIGN' and status 'APPROVED'.
  2. System should show the assignee's PIN <Assignee PIN> and name.
  3. System should show the remarks "Assign note".
  4. The asset list in the popup should hold exactly one row, with <Asset Serial>.
  5. After 'Close' the popup should be closed and the total N should be unchanged.
- Basis: VERIFIED (test_11)
- Check also: Read the field 'Approval Date' in the popup. Expected: it is filled.

**TRX-P10 — Verify an assigned asset can be acknowledged and the asset stays ASSIGNED**
- Precondition:
  1. The assignee is logged into the ERP with <ERP Username> / <ERP Password> (the assignee's own login).
  2. An APPROVED Assign of the asset <Asset Serial> to this assignee is waiting for acknowledgement.
  3. The assignee's Employee PIN is known (<Assignee PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign Acknowledgement'.
  3. Wait for the page to load completely.
  4. Read the total N in the line 'Showing x to y of N entries' under 'Pending Asset Acknowledgement'.
  5. Click the link 'Details' on the row whose popup asset list holds <Asset Serial> (open rows one by one and close with 'Close' until it matches).
  6. In the popup check the cell 'Asset Serial'.
  7. Click the button 'Acknowledge' in the popup (do not tick the select-all checkbox).
  8. Wait for the toast message to appear and read it.
  9. Read the total N of 'Pending Asset Acknowledgement' again.
  10. In the grid 'My Assigned Asset' find the row with <Asset Serial> and read its 'Assigned Employee' cell.
  11. Open 'Asset Serial Global List' (Fixed Asset), search <Asset Serial> and read 'Assign Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password> (assignee)
  - Asset Serial = <Asset Serial>
  - N = total entries read at step 4
- Expected:
  1. System should show the toast "Acknowledged successfully" and close the popup.
  2. The pending total should be N-1.
  3. The grid 'My Assigned Asset' should contain <Asset Serial>.
  4. The 'Assigned Employee' cell of that row should contain [<Assignee PIN>].
  5. 'Asset Serial Global List' should still show Assign Status 'ASSIGNED'.
- Basis: VERIFIED (test_11)
- Check also: Do not use the select-all checkbox at any point (it ticks other people's assignments). In 'Transaction List' the ASSIGN row should still show status 'APPROVED'.

**TRX-P11 — Verify Internal Movement loads an assigned asset with its current holder**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED Furniture asset 'Cabinet Table' exists; its Asset Serial is known (<Asset Serial>) and its holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon on the right of the 'Asset Serial' box.
  6. Click the suggestion that starts with <Asset Serial>.
  7. Read the fields 'Asset Item Name', 'Previous Assign Status', and the assigned employee PIN and name.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show 'Cabinet Table' in 'Asset Item Name'.
  2. System should show 'ASSIGNED' in 'Previous Assign Status'.
  3. System should show the current holder's PIN <Assignee PIN> and name in the assigned employee fields.
- Basis: VERIFIED (test_12)
- Check also: Read the field 'Search By'. Expected: the option 'Serial' is selected by default.

**TRX-P12 — Verify Search By offers Serial and Employee Pin on Internal Movement**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset <Asset Serial> exists; its holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. Look at the radio options of 'Search By' and note which one is selected.
  5. Click the radio 'Employee Pin'.
  6. In the employee search box type the holder's Employee PIN (see Test data).
  7. Click the small purple search icon on the right of the box.
  8. Click the suggestion that appears.
  9. Wait for the grid 'Asset List' to fill and read the 'Asset Serial' column of every row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Employee PIN = <Assignee PIN>
  - Asset Serial expected in the list = <Asset Serial>
- Expected:
  1. System should show both options 'Serial' and 'Employee Pin' in 'Search By'.
  2. 'Serial' should be selected by default and 'Employee Pin' should not be selected.
  3. After step 8 the grid 'Asset List' should load every asset assigned to that employee.
  4. The list should include <Asset Serial>.
- Basis: VERIFIED (test_12)
- Check also: Each loaded row has a trash icon in the column 'Action'. Click one icon on an unwanted row and check that only that row disappears.

**TRX-P13 — Verify Internal Movement through the Draft path**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as the creator and as the approver.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED Furniture asset 'Cabinet Table' exists; its Asset Serial is known (<Asset Serial>) and its holder has the Employee PIN <Assignee PIN>.
  4. The Building 'Head Office' has at least one floor.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. Under 'Internal Movement To', in 'Employee PIN Search' type the employee's PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In 'Building Name' choose 'Head Office'.
  8. In 'Floor Number' choose the first floor in the list (note its name, written below as <Floor>).
  9. In 'Note/Remarks' type "Movement note".
  10. Click the button 'Draft'.
  11. Wait for the toast message to appear and read it.
  12. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  13. In 'Transaction Type' choose 'TRANSFER'. In 'Transaction Status' choose 'DRAFT'. Click 'Search'.
  14. Click the link 'Details' on the row whose asset list holds <Asset Serial>.
  15. Read 'Transaction Type', 'Transaction Status', employee, remarks, date, Building and Floor. Click 'Close'.
  16. Click the link 'Edit' on the same row.
  17. If 'Floor Number' shows '-Select Floor-', choose <Floor> again.
  18. Click the button 'Submit'.
  19. Wait for the toast message to appear and read it.
  20. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  21. In 'Transaction Type' choose 'TRANSFER'. In 'Transaction Status' choose 'PENDING'. Click 'Search'.
  22. Click 'Details' on the row holding <Asset Serial>, then click the button 'Approve'.
  23. Wait for the toast message to appear and read it.
  24. In 'Transaction Status' choose 'APPROVED', click 'Search', click 'Details' on the row holding <Asset Serial>, and read 'Approved By' and 'Approval Date'. Click 'Close'.
  25. Open 'Asset Serial Global List', search <Asset Serial>, open the asset popup and read 'Assign Status', Building and Floor.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Internal Movement To, Employee PIN Search = <Assignee PIN>
  - Building Name = Head Office
  - Floor Number = <Floor> (first floor of Head Office)
  - Note/Remarks = Movement note
- Expected:
  1. System should show the toast "Asset Internal-Movement Draft Successfully" at step 11.
  2. The Details popup at step 15 should show Transaction Type 'TRANSFER', status 'DRAFT', the employee, the note "Movement note", the date, Building 'Head Office' and Floor <Floor> as entered.
  3. System should show the toast "Asset Internal-Movement Submit Successfully" at step 19.
  4. System should show the toast "Approved successfully" at step 23.
  5. At step 24 the row should show 'Approved By' and 'Approval Date' filled.
  6. 'Asset Serial Global List' should show Assign Status 'ASSIGNED', Building 'Head Office' and Floor <Floor>.
- Basis: VERIFIED (test_12)
- Check also: Look at the 'Floor Number' drop-down right after 'Edit'. It may reopen at '-Select Floor-' while the Building stays 'Head Office'.

**TRX-P14 — Verify Internal Movement through the Submit-only path**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as the creator and as the approver.
  2. The module 'Fixed Asset' is available.
  3. A second ASSIGNED Furniture asset 'Cabinet Table' exists; its Asset Serial is known (<Second Asset Serial>) and its holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Second Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. Under 'Internal Movement To', in 'Employee PIN Search' type the employee's PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In 'Building Name' choose 'Head Office'.
  8. In 'Floor Number' choose the first floor in the list.
  9. In 'Note/Remarks' type "Movement note".
  10. Click the button 'Submit'.
  11. Wait for the toast message to appear and read it.
  12. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  13. In 'Transaction Type' choose 'TRANSFER'. In 'Transaction Status' choose 'PENDING'. Click 'Search'.
  14. Click 'Details' on the row holding <Second Asset Serial>, then click the button 'Approve'.
  15. Wait for the toast message to appear and read it.
  16. Open 'Asset Serial Global List', search <Second Asset Serial>, open the asset popup and read 'Assign Status' and Building.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Second Asset Serial>
  - Internal Movement To, Employee PIN Search = <Assignee PIN>
  - Building Name = Head Office
  - Floor Number = first floor of Head Office
  - Note/Remarks = Movement note
- Expected:
  1. System should show the toast "Asset Internal-Movement Submit Successfully" at step 11.
  2. System should show the toast "Approved successfully" at step 15.
  3. The asset should stay 'ASSIGNED'.
  4. The asset popup should show Building 'Head Office'.
- Basis: VERIFIED (test_12)
- Check also: In 'Transaction List' filter 'TRANSFER' and 'APPROVED'. Expected: the row has no 'Edit' link.

**TRX-P15 — Verify Un Assign loads an assigned asset with its current holder**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>) and its holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Un Assign'.
  3. Wait for the page to load completely.
  4. Check that the option 'Serial' of 'Search By' is selected.
  5. In the field 'Asset Serial' type <Asset Serial>.
  6. Click the small purple search icon on the right of the 'Asset Serial' box.
  7. Click the suggestion that starts with <Asset Serial>.
  8. Read 'Previous Assign Status' and the current assignee's PIN and name.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show 'ASSIGNED' in 'Previous Assign Status'.
  2. System should show the PIN <Assignee PIN> and the name of the current assignee.
- Basis: VERIFIED (test_13)
- Check also: Try to type in 'Previous Assign Status'. Expected: the text is not accepted (read-only).

**TRX-P16 — Verify Un Assign through the Draft path**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as the creator and as the approver.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>) and its current holder has the Employee PIN <Assignee PIN>.
  4. A hand-over employee exists who is a different person from the current holder; the hand-over employee's PIN is known (<Hand-over PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Un Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In the field 'Employee PIN Search' type the hand-over employee's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. Read 'Employee PIN' and 'Employee Name'.
  8. In 'Note/Remarks' type "Unassign note".
  9. Click the button 'Draft'.
  10. Wait for the toast message to appear and read it.
  11. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  12. In 'Transaction Type' choose 'UNASSIGN'. In 'Transaction Status' choose 'DRAFT'. Click 'Search'.
  13. Click the link 'Details' on the row whose asset list holds <Asset Serial>. Read the values and click 'Close'.
  14. Click the link 'Edit' on the same row, then click the button 'Submit'.
  15. Wait for the toast message to appear and read it.
  16. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  17. In 'Transaction Type' choose 'UNASSIGN'. In 'Transaction Status' choose 'PENDING'. Click 'Search'.
  18. Click 'Details' on the row holding <Asset Serial>, then click the button 'Approve'.
  19. Wait for the toast message to appear and read it.
  20. In 'Transaction Status' choose 'APPROVED', click 'Search', and read 'Transaction Status', 'Approved By' and 'Approval Date' of the row.
  21. Open 'Asset Serial Global List', search <Asset Serial> and read 'Assign Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search (hand-over employee) = <Hand-over PIN>
  - Note/Remarks = Unassign note
- Expected:
  1. System should fill 'Employee PIN' and 'Employee Name' with the hand-over employee's PIN and name at step 7.
  2. System should show the toast "Asset Un-Assign Draft Successfully" at step 10.
  3. System should show the toast "Asset Un-Assign Submit Successfully" at step 15.
  4. System should show the toast "Approved successfully" at step 19.
  5. The row should show status 'APPROVED' with 'Approved By' and 'Approval Date' filled.
  6. 'Asset Serial Global List' should show Assign Status 'UNASSIGNED'.
- Basis: VERIFIED (test_13)
- Check also: In the Details popup of step 13 compare the note "Unassign note" and the hand-over employee with what was typed. Expected: they are identical.

**TRX-P17 — Verify Un Assign through the Submit-only path**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as the creator and as the approver.
  2. The module 'Fixed Asset' is available.
  3. A second ASSIGNED asset exists; its Asset Serial is known (<Second Asset Serial>) and its current holder is a different person from the hand-over employee (<Hand-over PIN>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Un Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Second Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In the field 'Employee PIN Search' type the hand-over employee's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In 'Note/Remarks' type "Unassign note".
  8. Click the button 'Submit'.
  9. Wait for the toast message to appear and read it.
  10. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  11. In 'Transaction Type' choose 'UNASSIGN'. In 'Transaction Status' choose 'PENDING'. Click 'Search'.
  12. Click 'Details' on the row holding <Second Asset Serial>, then click the button 'Approve'.
  13. Wait for the toast message to appear and read it.
  14. Open 'Asset Serial Global List', search <Second Asset Serial> and read 'Assign Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Second Asset Serial>
  - Employee PIN Search (hand-over employee) = <Hand-over PIN>
  - Note/Remarks = Unassign note
- Expected:
  1. System should show the toast "Asset Un-Assign Submit Successfully" at step 9.
  2. System should show the toast "Approved successfully" at step 13.
  3. 'Asset Serial Global List' should show Assign Status 'UNASSIGNED'.
- Basis: VERIFIED (test_13)
- Check also: In 'Transaction List' filter 'UNASSIGN' and 'APPROVED'. Expected: the row has no 'Edit' link.

**TRX-P18 — Verify the Transaction List columns and filter options**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. Read the column headers of the result grid.
  5. Open the drop-down 'Transaction Type' and read all options.
  6. Open the drop-down 'Transaction Status' and read all options.
  7. Read the content of the field 'Created By'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
- Expected:
  1. System should show the columns 'SL', 'Details', 'Edit', 'Transaction Type', 'Transaction Date', 'Branch', 'Created By', 'Approved By', 'Approval Date' and 'Transaction Status'.
  2. 'Transaction Type' should offer '-Select Transaction Type-', 'ASSIGN', 'UNASSIGN', 'TRANSFER'.
  3. 'Transaction Status' should offer '-Select Transaction Status-', 'PENDING', 'APPROVED', 'REJECTED', 'DRAFT', 'SENDBACK', 'ACKNOWLEDGED'.
  4. 'Created By' should be pre-filled with the logged-in user.
- Basis: VERIFIED (test_14)
- Check also: Look for the filters 'From Date', 'To Date' and 'Approved By', and the buttons 'Search' and 'Reset'. Expected: all are present.

**TRX-P19 — Verify Transaction List filters by type and by status**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. The user has created transactions of type ASSIGN, UNASSIGN and TRANSFER, and at least one transaction of each type has status APPROVED.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Type' choose 'ASSIGN' and click 'Search'. Read the 'Transaction Type' cell of every row.
  5. Click 'Reset'. In 'Transaction Type' choose 'UNASSIGN' and click 'Search'. Read the 'Transaction Type' cell of every row.
  6. Click 'Reset'. In 'Transaction Type' choose 'TRANSFER' and click 'Search'. Read the 'Transaction Type' cell of every row.
  7. Click 'Reset'. In 'Transaction Status' choose 'APPROVED' and click 'Search'. Read the 'Transaction Status' cell of every row.
  8. Click the link 'Details' on the first row.
  9. Wait for the asset list to load; read 'Transaction Type', the column headers of the asset list and the buttons shown.
  10. Try to type in any field of the popup.
  11. Click 'Close'.
  12. Look at the 'Edit' column of the first row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Type = ASSIGN, then UNASSIGN, then TRANSFER
  - Transaction Status = APPROVED
- Expected:
  1. System should show only rows of the chosen type for each type filter.
  2. System should show only rows with status 'APPROVED' for the status filter.
  3. The Details popup should be read-only and its 'Transaction Type' should equal the row's type.
  4. The asset list in the popup should have the columns 'SL', 'Asset Serial', 'Asset Item Name', 'Sub Category', 'Category', 'Project Name', 'Department Name', 'Assign Status', 'Assigned Before Approval', 'Utilization Status'.
  5. The popup should have only the button 'Close'.
  6. The APPROVED row should have no 'Edit' link.
- Basis: VERIFIED (test_14)
- Check also: Click 'Reset' and read 'Created By'. Expected: the filters are cleared; 'Created By' may return to the logged-in user (to be confirmed).

**TRX-P20 — Verify Transaction Approval List columns and filter options**
- Precondition:
  1. The approver is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. Transactions of type ASSIGN, UNASSIGN and TRANSFER exist, and at least one transaction is APPROVED.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  3. Wait for the page to load completely.
  4. Read the column headers of the result grid.
  5. Open the drop-down 'Transaction Type' and read all options.
  6. Open the drop-down 'Transaction Status' and read all options.
  7. Choose 'ASSIGN' in 'Transaction Type', click 'Search', read the 'Transaction Type' cell of every row.
  8. Click 'Reset'. Repeat with 'UNASSIGN' and then with 'TRANSFER'.
  9. Click 'Reset'. Choose 'APPROVED' in 'Transaction Status', click 'Search', read the 'Transaction Status' cell of every row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Type = ASSIGN, UNASSIGN, TRANSFER
  - Transaction Status = APPROVED
- Expected:
  1. System should show the columns 'SL', 'Details', 'Transaction Type', 'Transaction Date', 'Branch', 'Created By', 'Approved By', 'Approval Date', 'Transaction Status' and no 'Edit' column.
  2. 'Transaction Type' should offer 'ASSIGN', 'UNASSIGN', 'TRANSFER'.
  3. 'Transaction Status' should offer 'PENDING', 'APPROVED', 'REJECTED', 'SENDBACK', 'ACKNOWLEDGED' and no 'DRAFT'.
  4. Every filtered row should match the filter that was chosen.
- Basis: VERIFIED (test_15)
- Check also: Read the filter 'Created By'. Expected: it is empty on this screen (unlike Transaction List).

**TRX-P21 — Verify an APPROVED transaction has no Comment box and no Approve button**
- Precondition:
  1. The approver is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. At least one transaction with status APPROVED exists.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Status' choose 'APPROVED' and click 'Search'.
  5. Read the 'Transaction Type' cell of the first row.
  6. Click the link 'Details' on the first row.
  7. Wait for the asset list in the popup to load.
  8. Read 'Transaction Type' and 'Transaction Status' in the popup.
  9. Look for the 'Comment' box and the buttons 'Approve', 'Reject' and 'Sendback'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Status = APPROVED
- Expected:
  1. System should show 'Transaction Type' equal to the type in the row.
  2. System should show 'Transaction Status' 'APPROVED'.
  3. System should show no 'Comment' box.
  4. System should show no 'Approve' button.
- Basis: VERIFIED (test_15)
- Check also: Read the buttons at the bottom of the popup. Expected: only 'Close'.

**TRX-P22 — Verify the approval popup of a PENDING transaction shows the decision controls**
- Precondition:
  1. The approver is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. At least one transaction with status PENDING exists.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Status' choose 'PENDING' and click 'Search'.
  5. Click the link 'Details' on the first row.
  6. Wait for the asset list in the popup to load.
  7. Read the placeholder text of the 'Comment' box.
  8. Look for the buttons 'Approve', 'Reject' and 'Sendback'. Do not click them.
  9. Click the button 'Close'.
  10. Read 'Transaction Status' of the same row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Status = PENDING
- Expected:
  1. System should show the 'Comment' box with the placeholder "Leave comment here..".
  2. System should show the buttons 'Approve', 'Reject' and 'Sendback'.
  3. After 'Close' the row should still show status 'PENDING'.
- Basis: VERIFIED (test_10)
- Check also: Reject and Sendback have never been clicked in any run (see the BA questions); do not click them.

#### Negative

**TRX-N01 — Verify Draft on Asset Assign without an employee is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid' and check that the serial is in 'Asset List'.
  6. Leave 'Employee PIN Search' empty.
  7. Click the button 'Draft'.
  8. Read the message next to the employee field and check whether a toast message appears.
  9. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  10. In 'Transaction Type' choose 'ASSIGN', in 'Transaction Status' choose 'DRAFT', click 'Search' and look for a new row holding <Asset Serial>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = (empty)
- Expected:
  1. System should show "This field is required" next to the employee field.
  2. System should show no success toast.
  3. System should save nothing: no new DRAFT row for <Asset Serial> in 'Transaction List'.
- Basis: VERIFIED (test_10)
- Check also: Read the toast area after the click. Expected: no toast message appears.

**TRX-N02 — Verify Submit on Asset Assign without an employee is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid' and check that the serial is in 'Asset List'.
  6. Leave 'Employee PIN Search' empty.
  7. Click the button 'Submit'.
  8. Read any message next to the employee field or in a toast.
  9. Open 'Transaction Approval List', choose 'ASSIGN' and 'PENDING', click 'Search' and look for a row holding <Asset Serial>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = (empty)
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should create no PENDING transaction for <Asset Serial>.
- Basis: DERIVED (not yet run)
- Check also: Open 'Asset Serial Global List' and search <Asset Serial>. Expected: Assign Status is still 'UNASSIGNED'.

**TRX-N03 — Verify Un Assign to the same employee is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>) and its current holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Un Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In 'Employee PIN Search' type the current holder's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. Click the button 'Draft'.
  8. Wait for the toast message to appear and read it.
  9. Click the tab 'Asset Transaction', then click the link 'Transaction List', choose 'UNASSIGN' and 'DRAFT' and click 'Search'; look for a new row holding <Asset Serial>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Assignee PIN> (the current holder)
- Expected:
  1. System should show the error toast "Asset assigned to same employee!".
  2. System should save nothing: no new DRAFT row for <Asset Serial>.
- Basis: VERIFIED (test_13)
- Check also: Open 'Asset Serial Global List' and search <Asset Serial>. Expected: Assign Status is still 'ASSIGNED'.

**TRX-N04 — Verify Submit on Un Assign to the same employee is also refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>) and its current holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Un Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In 'Employee PIN Search' type the current holder's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. Click the button 'Submit'.
  8. Wait for the toast message to appear and read it.
  9. Open 'Transaction Approval List', choose 'UNASSIGN' and 'PENDING', click 'Search' and look for a row holding <Asset Serial>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Assignee PIN> (the current holder)
- Expected:
  1. System should refuse the Submit.
  2. System should create no PENDING transaction for <Asset Serial>.
  3. The message is expected to be "Asset assigned to same employee!" (to be confirmed for Submit).
- Basis: DERIVED (not yet run)
- Check also: Search <Asset Serial> on 'Asset Internal Movement'. Expected: the asset loads (it is not locked).

**TRX-N05 — Verify a locked asset cannot be found on other transaction screens**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
  4. An Un Assign for this asset has been submitted (status PENDING) and not yet approved.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon on the right of the 'Asset Serial' box.
  6. Wait for the toast message to appear and read it.
  7. Look at the suggestion list.
  8. Open the menu 'Asset In Pending Process List' in the Fixed Asset module and look for <Asset Serial>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show the toast "No asset found".
  2. System should offer no suggestion.
  3. The asset <Asset Serial> should be listed in 'Asset In Pending Process List'.
- Basis: VERIFIED (catalog notes in the Un Assign and Internal Movement screens)
- Check also: Repeat steps 4 to 6 on 'Asset Un Assign' and on 'Asset Assign'. Expected: the same toast "No asset found".

**TRX-N06 — Verify Internal Movement is not possible after Un Assign is submitted (ordering rule)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as the creator and as the approver.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
  4. An Un Assign for this asset has been submitted (status PENDING) to a hand-over employee (<Hand-over PIN>) and not approved.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial> and click the small purple search icon.
  5. Wait for the toast message and read it; check that no suggestion is offered.
  6. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  7. Choose 'UNASSIGN' and 'PENDING', click 'Search', click 'Details' on the row holding <Asset Serial> and click 'Approve'.
  8. Wait for the toast message and read it.
  9. Open 'Asset Internal Movement' again, type <Asset Serial> in 'Asset Serial' and click the small purple search icon.
  10. Wait for the toast message and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Hand-over employee PIN = <Hand-over PIN>
- Expected:
  1. System should show "No asset found" at step 5 and let no movement be created.
  2. System should show the toast "Approved successfully" at step 8.
  3. After the Un Assign is approved the asset is 'UNASSIGNED' and also cannot be moved (step 10 should again not offer the asset; exact message to be confirmed).
- Basis: VERIFIED (catalog notes)
- Check also: Open 'Asset Serial Global List' and search <Asset Serial>. Expected: Assign Status 'UNASSIGNED' after step 8.

**TRX-N07 — Verify an UNASSIGNED asset cannot be un-assigned**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Un Assign'.
  3. Wait for the page to load completely.
  4. Check that the option 'Serial' of 'Search By' is selected.
  5. In the field 'Asset Serial' type <Asset Serial>.
  6. Click the small purple search icon on the right of the 'Asset Serial' box.
  7. Wait for a suggestion list or a toast message and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should not offer the asset for Un Assign (exact message to be confirmed).
  2. The form fields 'Asset Item Name' and 'Previous Assign Status' should stay empty.
- Basis: DERIVED (not yet run)
- Check also: Click the button 'Add to Grid'. Expected: no row is added to 'Asset List'.

**TRX-N08 — Verify an ASSIGNED asset cannot be assigned again**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon on the right of the 'Asset Serial' box.
  6. Wait for a suggestion list or a toast message and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should not offer the asset for Assign (exact message to be confirmed).
  2. The form fields 'Asset Item Name' and 'Previous Assign Status' should stay empty.
- Basis: DERIVED (not yet run)
- Check also: Click the button 'Add to Grid'. Expected: no row is added to 'Asset List'.

**TRX-N09 — Verify an UNASSIGNED asset cannot be moved**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Click the small purple search icon on the right of the 'Asset Serial' box.
  6. Wait for a suggestion list or a toast message and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should not offer the asset for Internal Movement (exact message to be confirmed).
  2. The form fields 'Asset Item Name' and 'Previous Assign Status' should stay empty.
- Basis: DERIVED (not yet run)
- Check also: Click the button 'Add to Grid'. Expected: no row is added to 'Asset List'.

**TRX-N10 — Verify a typed serial without clicking the suggestion does not fill the form**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Do not click the search icon and do not click any suggestion.
  6. Read the fields 'Asset Item Name' and 'Previous Assign Status'.
  7. Click the button 'Add to Grid'.
  8. Read any message shown and look at the grid 'Asset List'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should leave 'Asset Item Name' and 'Previous Assign Status' empty.
  2. System should not add the asset to 'Asset List'.
  3. A validation message should appear (exact text to be confirmed).
- Basis: DERIVED (not yet run)
- Check also: Click the search icon and then the suggestion. Expected: the fields fill and 'Add to Grid' now adds a row.

**TRX-N11 — Verify Add to Grid with no asset chosen does not add a row**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. Leave the field 'Asset Serial' empty.
  5. Click the button 'Add to Grid'.
  6. Read any message shown and look at the grid 'Asset List'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = (empty)
- Expected:
  1. System should add no row to 'Asset List'.
  2. A validation message should appear (exact text to be confirmed).
- Basis: DERIVED (not yet run)
- Check also: Click the button 'Draft' with the grid empty. Expected: nothing is saved and no success toast appears.

**TRX-N12 — Verify an employee name search shorter than 3 characters gives no suggestions**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
  4. The assignee's name is known; its first two letters are used below (written as <Two letters of name>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In the field 'Employee PIN Search' type <Two letters of name>.
  7. Click the small purple search icon on the right of the 'Employee PIN Search' box.
  8. Wait and look at the suggestion list and any message.
  9. Type one more letter of the name so that the text has 3 characters and click the search icon again.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Two letters of name>, then three letters of the same name
- Expected:
  1. System should show no suggestions for 2 characters (the rule is 3 or more characters for a name search).
  2. A message may appear (exact text to be confirmed).
  3. 'Employee PIN' and 'Employee Name' should stay empty.
  4. For 3 characters, suggestions should appear.
- Basis: DERIVED (not yet run)
- Check also: Click 'Draft' with no employee chosen. Expected: "This field is required".

**TRX-N13 — Verify an employee PIN that does not exist gives no match**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In the field 'Employee PIN Search' type 99999999.
  7. Click the small purple search icon on the right of the 'Employee PIN Search' box.
  8. Wait and look at the suggestion list.
  9. Read the fields 'Employee PIN' and 'Employee Name'.
  10. Click the button 'Draft'.
  11. Read the message next to the employee field.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = 99999999 (a made-up PIN that does not exist)
- Expected:
  1. System should show no suggestion.
  2. System should leave 'Employee PIN' and 'Employee Name' empty.
  3. System should show "This field is required" after 'Draft' and save nothing.
- Basis: DERIVED (not yet run)
- Check also: Open 'Transaction List', choose 'ASSIGN' and 'DRAFT', click 'Search'. Expected: no new row for <Asset Serial>.

**TRX-N14 — Verify the Pending list does not show another employee's assignment**
- Precondition:
  1. Two employees, A and B, each have an APPROVED Assign waiting for acknowledgement.
  2. The asset assigned to B has the Asset Serial <Serial Assigned To B>.
  3. Employee A is logged into the ERP with <ERP Username> / <ERP Password> (employee A's own login).
  4. The module 'Fixed Asset' is available.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign Acknowledgement'.
  3. Wait for the page to load completely.
  4. In the grid 'Pending Asset Acknowledgement' read the 'Assigned Employee' cell of every row (switch 'Records per page' to 100 if there are more than 10 rows).
  5. Click the link 'Details' on each row and look for <Serial Assigned To B> in the asset list of the popup; click 'Close' after each.
- Test data:
  - Login = <ERP Username> / <ERP Password> (employee A)
  - Serial = <Serial Assigned To B>
- Expected:
  1. System should show only rows whose 'Assigned Employee' is employee A.
  2. System should not show the asset <Serial Assigned To B> in any popup of A's Pending list.
- Basis: DERIVED (not yet run)
- Check also: Log in as the assigner who created the assignment and open the same screen. The catalog says the creator does not see these rows; confirm whether the list is shared (BA question).

**TRX-N15 — Verify a PENDING row has no Edit link and a DRAFT row has one**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. The user has created at least one transaction with status DRAFT and one with status PENDING.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Status' choose 'DRAFT' and click 'Search'. Look at the column 'Edit' of every row.
  5. Click 'Reset'. In 'Transaction Status' choose 'PENDING' and click 'Search'. Look at the column 'Edit' of every row.
  6. Click 'Reset'. In 'Transaction Status' choose 'APPROVED' and click 'Search'. Look at the column 'Edit' of every row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Status = DRAFT, then PENDING, then APPROVED
- Expected:
  1. System should show a link 'Edit' on every DRAFT row.
  2. System should show no 'Edit' link on PENDING rows.
  3. System should show no 'Edit' link on APPROVED rows.
- Basis: VERIFIED (test_10, test_14)
- Check also: Click 'Edit' on a DRAFT row. Expected: the original form opens with the saved values.

**TRX-N16 — Verify a Draft is not applied to the asset before approval**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset exists; its Asset Serial is known (<Asset Serial>).
  4. The assignee has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In 'Employee PIN Search' type the assignee's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In 'Note/Remarks' type "Draft check".
  8. Click the button 'Draft' and wait for the toast message.
  9. Open 'Asset Serial Global List' in the Fixed Asset module, search <Asset Serial> and read 'Assign Status'.
  10. Open 'Transaction List', choose 'ASSIGN' and 'DRAFT', click 'Search', click 'Edit' on the row holding <Asset Serial> and click 'Submit'; wait for the toast.
  11. Open 'Asset Serial Global List' again, search <Asset Serial> and read 'Assign Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Assignee PIN>
  - Note/Remarks = Draft check
- Expected:
  1. System should show the toast "Asset Assign Draft Successfully" at step 8.
  2. System should show Assign Status 'UNASSIGNED' at step 9.
  3. System should show the toast "Asset Assign Submit Successfully" at step 10.
  4. System should still show Assign Status 'UNASSIGNED' at step 11 while the transaction is PENDING.
- Basis: DERIVED (not yet run)
- Check also: Open 'Asset Assign' and search <Asset Serial> after step 10. Expected: "No asset found" (the asset is locked by the pending transaction).

#### Edge Case

**TRX-E01 — Verify two or more assets can be added to the grid in one transaction**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as creator and approver.
  2. The module 'Fixed Asset' is available.
  3. Two APPROVED, UNASSIGNED assets exist; their Asset Serials are <Asset Serial> and <Second Asset Serial>.
  4. The assignee has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In the field 'Asset Serial' type <Second Asset Serial>, click the small purple search icon, then click the suggestion.
  7. Click the button 'Add to Grid'.
  8. Read the 'Asset Serial' column of 'Asset List'.
  9. In 'Employee PIN Search' type the assignee's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  10. Click the button 'Submit' and read the toast message.
  11. Open 'Transaction Approval List', choose 'ASSIGN' and 'PENDING', click 'Search', click 'Details' on the row holding both serials and click 'Approve'.
  12. Read the toast message.
  13. Open 'Asset Serial Global List' and read 'Assign Status' of both serials.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Second Asset Serial = <Second Asset Serial>
  - Employee PIN Search = <Assignee PIN>
- Expected:
  1. System should list both serials in 'Asset List' (two rows).
  2. Whether both assets become 'ASSIGNED' is to be confirmed.
- Basis: DERIVED (not yet run)
- Check also: Click the trash icon of one row in 'Asset List' before step 9. Expected: only that row disappears.

**TRX-E02 — Verify the same asset added to the grid twice**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. One APPROVED, UNASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In the field 'Asset Serial' type <Asset Serial> again, click the small purple search icon, then click the suggestion.
  7. Click the button 'Add to Grid'.
  8. Read any message and count the rows of 'Asset List'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial> (both times)
- Expected:
  1. System should show a validation message or add no second row (exact behaviour to be confirmed).
  2. 'Asset List' should not hold <Asset Serial> twice.
- Basis: DERIVED (not yet run)
- Check also: Click 'Draft' with an employee chosen. Expected (to be confirmed): only one asset is saved.

**TRX-E03 — Verify Un Assign with Search By Employee Pin loads all of that employee's assets**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An employee holds the test asset <Asset Serial> and possibly other assets; the employee's PIN is <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Un Assign'.
  3. Wait for the page to load completely.
  4. In 'Search By' click the radio 'Employee Pin'.
  5. In the employee search box type the holder's Employee PIN (see Test data).
  6. Click the small purple search icon, then click the suggestion (in the form '<PIN>-<NAME>> <Department>> <Branch>').
  7. Wait for 'Asset List' to fill and read the 'Asset Serial' column.
  8. Click the red trash icon in the column 'Action' of every row except the row of <Asset Serial>.
  9. Read 'Asset List' again.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Employee PIN = <Assignee PIN>
  - Asset Serial to keep = <Asset Serial>
- Expected:
  1. System should load every asset of that employee into 'Asset List'.
  2. Rows should disappear when their trash icon is clicked.
  3. After step 8 only <Asset Serial> should remain.
  4. This mode was not run to Draft, so the save step is not yet verified.
- Basis: DERIVED (not yet run)
- Check also: Real assets of that employee must not be un-assigned by mistake; do not click 'Draft' or 'Submit' unless only the test asset remains.

**TRX-E04 — Verify Internal Movement Floor list depends on the Building**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. Open the drop-down 'Floor Number' before choosing a Building and read its options.
  7. In 'Building Name' choose 'Head Office'.
  8. Open the drop-down 'Floor Number' and read its options.
  9. Choose the floor '12th floor' and open the drop-down 'Room Number'.
  10. In 'Building Name' choose 'BRAC Gulshan office'.
  11. Open the drop-down 'Floor Number' and read its options.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Building Name = Head Office, then BRAC Gulshan office
  - Floor Number = 12th floor
- Expected:
  1. System should show no floors before a Building is chosen.
  2. For 'Head Office' System should offer the floors 12th floor, 7th floor, 6th floor, 17th floor, 8th Floor.
  3. The '12th floor' should have no rooms ('Room Number' stays '-Select Room-').
  4. For 'BRAC Gulshan office' System should offer the floors of that building (list to be confirmed).
- Basis: OBSERVED (catalog)
- Check also: Read the drop-down 'Branch Location'. Expected: it shows '-Select Branch-'.

**TRX-E05 — Verify Internal Movement Submit without Building and Floor**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>) and its holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In the field 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. Under 'Internal Movement To', in 'Employee PIN Search' type the employee's PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. Leave 'Building Name' and 'Floor Number' unchosen.
  8. Click the button 'Submit'.
  9. Wait for the toast message or a validation message and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Internal Movement To, Employee PIN Search = <Assignee PIN>
  - Building Name = (not chosen); Floor Number = (not chosen)
- Expected:
  1. System should either block the Submit with a validation message or accept it. Exact behaviour and text to be confirmed.
- Basis: DERIVED (not yet run)
- Check also: Open 'Transaction List' and filter 'TRANSFER' and 'PENDING'. Record whether a row exists for <Asset Serial>.

**TRX-E06 — Verify Edit of an Internal Movement draft keeps the Building but resets the Floor**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. A DRAFT Internal Movement exists for the asset <Asset Serial>, saved with the employee <Assignee PIN>, Building 'Head Office', a floor (written <Floor>) and the note "Movement note".
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Type' choose 'TRANSFER'. In 'Transaction Status' choose 'DRAFT'. Click 'Search'.
  5. Click the link 'Details' on the row holding <Asset Serial>; read the Floor; click 'Close'.
  6. Click the link 'Edit' on the same row.
  7. Wait for the form to load.
  8. Read 'Employee PIN', 'Employee Name', 'Note/Remarks', 'Building Name' and 'Floor Number'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Type = TRANSFER; Transaction Status = DRAFT
  - Saved values = employee <Assignee PIN>, Building Head Office, Floor <Floor>, note "Movement note"
- Expected:
  1. System should show the saved employee PIN and name.
  2. System should show the note "Movement note".
  3. System should keep 'Building Name' at 'Head Office'.
  4. System should show 'Floor Number' as '-Select Floor-' although the Details popup shows <Floor>.
  5. The user must choose the floor again if it matters.
- Basis: VERIFIED (test_12)
- Check also: Choose <Floor> again in 'Floor Number' and click 'Submit'. Expected: the toast "Asset Internal-Movement Submit Successfully".

**TRX-E07 — Verify the Details popup of an Un Assign transaction**
- Precondition:
  1. The approver is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED Un Assign exists for the asset <Asset Serial>, previously held by the employee <Assignee PIN>, handed over to the hand-over employee <Hand-over PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Type' choose 'UNASSIGN'. In 'Transaction Status' choose 'APPROVED'. Click 'Search'.
  5. Read the cell 'Branch' of the row holding the Un Assign of <Asset Serial>.
  6. Click the link 'Details' on that row.
  7. Wait for the asset list to load.
  8. Read 'Organization Branch' in the popup.
  9. In the asset list of the popup read the cell under 'Assigned Before Approval'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Type = UNASSIGN; Transaction Status = APPROVED
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show in the popup the 'Organization Branch' of the hand-over employee.
  2. The list row should show the creator's branch (for example 'Head Office [ BDHO ]').
  3. The column 'Assigned Before Approval' should show the previous holder (name and [<Assignee PIN>]).
- Basis: OBSERVED (catalog)
- Check also: Read the field showing the employee in the popup. Expected: it is the hand-over employee.

**TRX-E08 — Verify the Pending count on Acknowledgement uses the total entries line**
- Precondition:
  1. The assignee is logged into the ERP with <ERP Username> / <ERP Password> (the assignee's own login).
  2. The module 'Fixed Asset' is available.
  3. More than 10 APPROVED Assign rows are pending for this assignee (if not available, record the test as not executable).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign Acknowledgement'.
  3. Wait for the page to load completely.
  4. Read the line 'Showing x to y of N entries' under 'Pending Asset Acknowledgement' and count the rows shown.
  5. In 'Records per page' of that grid choose 20 and read the line again.
  6. Choose 50 and read the line again.
  7. Choose 100 and read the line again.
  8. Choose 10 and read the line again.
- Test data:
  - Login = <ERP Username> / <ERP Password> (assignee)
  - Records per page = 10, 20, 50, 100 (the options are 10, 20, 30, 50, 100)
- Expected:
  1. System should show 10 rows per page by default.
  2. The value N in 'of N entries' should stay the same for every page size.
  3. The number of rows shown should follow the page size (up to N).
- Basis: OBSERVED (catalog)
- Check also: Do the same on the grid 'My Assigned Asset'. Expected: N is unchanged by page size there too.

**TRX-E09 — Verify the From Date and To Date filters on Transaction List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. The user has transactions on at least two different dates (written <Date 1> and <Date 2>, with <Date 1> earlier).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. Click the calendar icon of 'From Date' and pick <Date 2> (the inputs are read-only, so use the calendar).
  5. Click the calendar icon of 'To Date' and pick <Date 2>.
  6. Click the button 'Search'.
  7. Read the 'Transaction Date' of every row.
  8. Click 'Reset', set 'From Date' = <Date 1> and 'To Date' = <Date 1>, click 'Search' and read the 'Transaction Date' of every row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - From Date / To Date = <Date 2>, then <Date 1> (a range that includes some rows and excludes others)
- Expected:
  1. System should show only rows with a 'Transaction Date' inside the range.
  2. Boundary dates are expected to be included (to be confirmed).
- Basis: DERIVED (not yet run)
- Check also: Set 'To Date' earlier than 'From Date' and click 'Search'. Expected: no rows or a message (behaviour to be confirmed).

**TRX-E10 — Verify the Approved By filter needs 3 or more characters**
- Precondition:
  1. The approver is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. APPROVED transactions exist; the approver's name is known (first letters written <First 3 letters of name>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  3. Wait for the page to load completely.
  4. In the field 'Approved By' type the first 2 letters of the approver's name.
  5. Wait and look for a suggestion list.
  6. Add the third letter (text = <First 3 letters of name>).
  7. Wait and look for a suggestion list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Approved By = 2 letters, then <First 3 letters of name>
- Expected:
  1. System should give no suggestion for 2 characters.
  2. System should give suggestions for 3 or more characters.
- Basis: DERIVED (not yet run)
- Check also: Click a suggestion, choose 'APPROVED' and click 'Search'. Expected: rows approved by that person.

**TRX-E11 — Verify the filter Reset clears the filters**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. A filter is applied on Transaction List.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Type' choose 'ASSIGN'.
  5. In 'Transaction Status' choose 'APPROVED'.
  6. Click the button 'Search'.
  7. Click the button 'Reset'.
  8. Read 'Transaction Type', 'Transaction Status' and 'Created By'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Type = ASSIGN; Transaction Status = APPROVED
- Expected:
  1. System should clear 'Transaction Type' to '-Select Transaction Type-'.
  2. System should clear 'Transaction Status' to '-Select Transaction Status-'.
  3. 'Created By' should return to the logged-in user (to be confirmed).
- Basis: DERIVED (not yet run)
- Check also: Click 'Search' after Reset. Expected: the unfiltered list of the user's transactions appears.

**TRX-E12 — Verify an empty grid message**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. No transaction with status ACKNOWLEDGED exists (earlier observation).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Status' choose 'ACKNOWLEDGED'.
  5. Click the button 'Search'.
  6. Read the message in the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Status = ACKNOWLEDGED
- Expected:
  1. System should show "No data available in table".
- Basis: OBSERVED (catalog)
- Check also: Repeat on 'Transaction Approval List'. Expected: the same message.

#### Business

**TRX-B01 — Verify approving an Assign makes the asset ASSIGNED without acknowledgement**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as creator and approver.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset exists; its Asset Serial is known (<Asset Serial>).
  4. The assignee (Employee PIN <Assignee PIN>) will not acknowledge during this test.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'.
  3. Wait for the page to load completely.
  4. In 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. In 'Employee PIN Search' type the assignee's Employee PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In 'Note/Remarks' type "Assign note".
  8. Click the button 'Submit' and wait for the toast message.
  9. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  10. Choose 'ASSIGN' and 'PENDING', click 'Search', click 'Details' on the row holding <Asset Serial> and click 'Approve'.
  11. Wait for the toast message.
  12. Open 'Asset Serial Global List', search <Asset Serial> and read 'Assign Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Assignee PIN>
  - Note/Remarks = Assign note
- Expected:
  1. System should show the toast "Asset Assign Submit Successfully" at step 8.
  2. System should show the toast "Approved successfully" at step 11.
  3. System should show Assign Status 'ASSIGNED' before any acknowledgement.
- Basis: VERIFIED (catalog notes)
- Check also: Open 'Asset Assign Acknowledgement' with the assignee's login. Expected: the assignment still waits in 'Pending Asset Acknowledgement'.

**TRX-B02 — Verify acknowledging does not change the asset and does not change the transaction status**
- Precondition:
  1. The assignee is logged into the ERP with <ERP Username> / <ERP Password> (the assignee's own login) and has just acknowledged the approved Assign of the asset <Asset Serial>.
  2. The module 'Fixed Asset' is available.
  3. The user who created the assignment can log in to check the Transaction List.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Open 'Asset Serial Global List', search <Asset Serial> and read 'Assign Status'.
  3. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  4. In 'Transaction Type' choose 'ASSIGN' and click 'Search'.
  5. Find the row holding <Asset Serial> (use 'Details') and read its 'Transaction Status'.
  6. Click 'Reset'. In 'Transaction Status' choose 'ACKNOWLEDGED' and click 'Search'.
  7. Read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Transaction Type = ASSIGN; Transaction Status = ACKNOWLEDGED
- Expected:
  1. System should show Assign Status 'ASSIGNED'.
  2. The transaction should still show status 'APPROVED'.
  3. The 'ACKNOWLEDGED' filter returned no rows in earlier observations ("No data available in table").
- Basis: OBSERVED (catalog)
- Check also: Read 'Assigned Date' in the asset popup. Expected: it is empty before and after acknowledgement.

**TRX-B03 — Verify an approved Internal Movement keeps the asset ASSIGNED and updates the location**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as creator and approver.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>) and its holder has the Employee PIN <Assignee PIN>.
  4. The current Building and Floor of the asset are known from the asset popup in 'Asset Serial Global List' (written <Old Building> / <Old Floor>).
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  3. Wait for the page to load completely.
  4. In 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  5. Click the button 'Add to Grid'.
  6. Under 'Internal Movement To', in 'Employee PIN Search' type the employee's PIN (see Test data), click the small purple search icon, then click the suggestion.
  7. In 'Building Name' choose 'Head Office' (a different building or floor from <Old Building> / <Old Floor>).
  8. In 'Floor Number' choose a floor different from <Old Floor> (written <New Floor>).
  9. Click the button 'Submit' and wait for the toast message.
  10. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  11. Choose 'TRANSFER' and 'PENDING', click 'Search', click 'Details' on the row holding <Asset Serial> and click 'Approve'.
  12. Wait for the toast message.
  13. Open 'Asset Serial Global List', search <Asset Serial>, open the asset popup and read 'Assign Status', Building and Floor.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Internal Movement To, Employee PIN Search = <Assignee PIN>
  - Building Name = Head Office
  - Floor Number = <New Floor>
- Expected:
  1. System should show the toast "Asset Internal-Movement Submit Successfully" at step 9 and "Approved successfully" at step 12.
  2. System should show Assign Status 'ASSIGNED'.
  3. System should show the new Building 'Head Office' and the new Floor <New Floor> in the popup.
- Basis: VERIFIED (test_12)
- Check also: Read the assigned employee in the popup. Expected: the same holder as before.

**TRX-B04 — Verify the full life cycle UNASSIGNED to ASSIGNED to UNASSIGNED**
- Precondition:
  1. The creator/approver is logged into the ERP with <ERP Username> / <ERP Password>; the assignee can log in with their own <ERP Username> / <ERP Password> to acknowledge.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED, UNASSIGNED Furniture asset exists; its Asset Serial is known (<Asset Serial>).
  4. The assignee has the Employee PIN <Assignee PIN>; a different hand-over employee has the PIN <Hand-over PIN>.
- Steps:
  1. Open 'Asset Serial Global List', search <Asset Serial> and read 'Assign Status'.
  2. Click the tab 'Asset Transaction', then click the link 'Asset Assign'. Type <Asset Serial> in 'Asset Serial', click the search icon, click the suggestion, click 'Add to Grid', type the assignee's PIN in 'Employee PIN Search', click the search icon, click the suggestion, type "Assign note" in 'Note/Remarks' and click 'Submit'.
  3. In 'Transaction Approval List' choose 'ASSIGN' and 'PENDING', click 'Search', click 'Details' on the row with <Asset Serial> and click 'Approve'. Read 'Assign Status' in 'Asset Serial Global List'.
  4. Log in as the assignee. Open 'Asset Assign Acknowledgement', click 'Details' on the row whose asset list holds <Asset Serial> and click 'Acknowledge'. Read 'Assign Status' again.
  5. Log in again as the creator/approver. Open 'Asset Internal Movement', type <Asset Serial>, click the search icon, click the suggestion, click 'Add to Grid', type the assignee's PIN in 'Employee PIN Search' under 'Internal Movement To', click the search icon, click the suggestion, choose 'Head Office' in 'Building Name', choose the first floor in 'Floor Number', and click 'Submit'.
  6. In 'Transaction Approval List' choose 'TRANSFER' and 'PENDING', click 'Search', click 'Details' on the row with <Asset Serial> and click 'Approve'. Read 'Assign Status', Building and Floor in 'Asset Serial Global List'.
  7. Open 'Asset Un Assign', type <Asset Serial> in 'Asset Serial', click the search icon, click the suggestion, click 'Add to Grid', type the hand-over employee's PIN in 'Employee PIN Search', click the search icon, click the suggestion, type "Unassign note" in 'Note/Remarks' and click 'Submit'.
  8. In 'Transaction Approval List' choose 'UNASSIGN' and 'PENDING', click 'Search', click 'Details' on the row with <Asset Serial> and click 'Approve'.
  9. Read 'Assign Status' in 'Asset Serial Global List'.
- Test data:
  - Login = <ERP Username> / <ERP Password> (creator/approver and assignee)
  - Asset Serial = <Asset Serial>
  - Employee PIN Search = <Assignee PIN>, then <Hand-over PIN>
  - Note/Remarks = Assign note, Unassign note
  - Building Name = Head Office; Floor Number = first floor
- Expected:
  1. System should show 'UNASSIGNED' at step 1.
  2. System should show 'ASSIGNED' at step 3.
  3. System should show "Acknowledged successfully" at step 4 and 'ASSIGNED' after it.
  4. System should show 'ASSIGNED' with Building 'Head Office' and the chosen floor at step 6.
  5. System should show "Approved successfully" for each approval.
  6. System should show 'UNASSIGNED' at step 9.
  7. The asset should then be ready for Asset Expense and Write-off.
- Basis: VERIFIED (test_10, test_11, test_12, test_13)
- Check also: In 'Transaction List' filter 'APPROVED' and check that the ASSIGN, TRANSFER and UNASSIGN rows of the asset exist, each without an 'Edit' link.

**TRX-B05 — Verify a PENDING transaction locks the asset and the lock is released on Approve**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password> and can act as creator and approver.
  2. The module 'Fixed Asset' is available.
  3. An ASSIGNED asset exists; its Asset Serial is known (<Asset Serial>) and its holder has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the tab 'Asset Transaction', then click the link 'Asset Internal Movement'.
  2. In 'Asset Serial' type <Asset Serial>, click the small purple search icon, then click the suggestion.
  3. Click 'Add to Grid'.
  4. Under 'Internal Movement To', in 'Employee PIN Search' type the employee's PIN (see Test data), click the search icon, then click the suggestion.
  5. In 'Building Name' choose 'Head Office' and in 'Floor Number' choose the first floor.
  6. Click the button 'Submit' and read the toast message.
  7. Open the menu 'Asset In Pending Process List' in the Fixed Asset module and look for <Asset Serial>.
  8. Open 'Asset Un Assign', type <Asset Serial> in 'Asset Serial' and click the small purple search icon. Read the toast message.
  9. Open 'Transaction Approval List', choose 'TRANSFER' and 'PENDING', click 'Search', click 'Details' on the row with <Asset Serial> and click 'Approve'. Read the toast message.
  10. Open 'Asset Un Assign' again, type <Asset Serial> in 'Asset Serial', click the search icon and read the result.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Internal Movement To, Employee PIN Search = <Assignee PIN>
  - Building Name = Head Office; Floor Number = first floor
- Expected:
  1. System should show the toast "Asset Internal-Movement Submit Successfully" at step 6.
  2. System should list the asset in 'Asset In Pending Process List' at step 7.
  3. System should show "No asset found" at step 8.
  4. System should show "Approved successfully" at step 9.
  5. After step 9 the asset should load (a suggestion appears) on 'Asset Un Assign' at step 10.
- Basis: DERIVED (not yet run)
- Check also: Behaviour on Reject and Sendback is not known; do not click them, only note the question for the BA.

**TRX-B06 — Verify Created By and visibility between Transaction List and Approval List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. Transactions created by at least two different users exist.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction List'.
  3. Wait for the page to load completely.
  4. Click 'Search' without changing the filters and read the 'Created By' cell of every row.
  5. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  6. Wait for the page to load completely and click 'Search'.
  7. Read the 'Created By' cell of every row, the order of the rows and the number of rows per page.
- Test data:
  - Login = <ERP Username> / <ERP Password>
- Expected:
  1. System should show on 'Transaction List' only the logged-in user's own transactions.
  2. System should show on 'Transaction Approval List' the transactions of everyone, newest first.
  3. System should show 10 rows per page on 'Transaction Approval List'.
- Basis: VERIFIED (test_14, test_15)
- Check also: Read 'Created By' filter on both screens. Expected: pre-filled on 'Transaction List', empty on 'Transaction Approval List'.

**TRX-B07 — Verify the hand-over employee is recorded on an approved Un Assign**
- Precondition:
  1. The approver is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED Un Assign exists for the asset <Asset Serial>, with the hand-over employee <Hand-over PIN> and the note "Unassign note".
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Click the tab 'Asset Transaction', then click the link 'Transaction Approval List'.
  3. Wait for the page to load completely.
  4. In 'Transaction Type' choose 'UNASSIGN'. In 'Transaction Status' choose 'APPROVED'. Click 'Search'.
  5. Click the link 'Details' on the row holding <Asset Serial>.
  6. Wait for the asset list to load and read 'Transaction Type', 'Transaction Status', the employee PIN and name, the remarks, the date, 'Approved By' and 'Approval Date'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Transaction Type = UNASSIGN; Transaction Status = APPROVED
  - Hand-over employee PIN = <Hand-over PIN>; remarks = Unassign note
- Expected:
  1. System should show Transaction Type 'UNASSIGN' and status 'APPROVED'.
  2. System should show the hand-over employee's PIN <Hand-over PIN> and name.
  3. System should show the remarks "Unassign note" and the transaction date.
  4. System should show 'Approved By' and 'Approval Date' filled.
- Basis: VERIFIED (test_13)
- Check also: Read that no 'Comment' box and no 'Approve' button are shown (approved transaction).

**TRX-B08 — Verify the Assigned Date on the asset profile after an approved Assign**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The module 'Fixed Asset' is available.
  3. An APPROVED Assign exists for the asset <Asset Serial>; the assignee has the Employee PIN <Assignee PIN>.
- Steps:
  1. Click the module 'Fixed Asset'.
  2. Open 'Asset Serial Global List'.
  3. Search for <Asset Serial>.
  4. Open the asset popup of the row.
  5. Read the assigned employee PIN and name.
  6. Read the field 'Assigned Date'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show the assigned employee PIN <Assignee PIN> and name.
  2. The 'Assigned Date' on the profile is not set by the Assign (as observed; it stays empty).
- Basis: OBSERVED (catalog)
- Check also: This may be a gap; ask the BA whether 'Assigned Date' should be set on approval.

**5. When a CR changes something here — what to re-check**

- If a field is added or changed on the Assign, Internal Movement or Un Assign form: re-run TRX-P01 to P04, TRX-P13, TRX-E04 and TRX-N10 to N13. Check the Details popup (TRX-P05, TRX-P19).
- If the employee rule changes (required, search length, hand-over rule): TRX-N01, N02, N03, N04, N12, N13, TRX-P16.
- If the Building, Floor or Room rule changes: TRX-P13, TRX-P14, TRX-E04, TRX-E05, TRX-E06, TRX-B03.
- If a status or approval rule changes (new status, Reject or Sendback made active): TRX-P05, TRX-P22, TRX-P21, TRX-N15, TRX-B05, TRX-E12 and the status filter checks (TRX-P18, TRX-P19, TRX-P20).
- If the asset lock rule or the ordering rule changes: TRX-N05, TRX-N06, TRX-B05, TRX-B04.
- If the Acknowledgement logic changes (who sees which rows, status after acknowledging): TRX-P07 to P10, TRX-N14, TRX-B02, TRX-E08.
- If a message text changes: the scenarios quoting that message, namely TRX-P05, P06, P10, P13, P14, P16, P17, TRX-N01, N03, N05. Update the quoted text.
- If a list column or filter changes: TRX-P18, P19, P20, TRX-E09, E10, E11.
- If multi-asset transactions are enabled or restricted: TRX-E01, TRX-E02, TRX-E03.
- If the asset status model changes (UNASSIGNED / ASSIGNED): all of TRX-B01 to B05 and TRX-P05, P06, P13 to P17.

**6. Questions to ask the BA**

- Is Building and Floor mandatory on Internal Movement? What happens on Submit without them?
- Can one transaction hold several assets (Assign, Un Assign, Internal Movement)? What happens to each? Only single assets have been tested.
- What happens on Reject and Sendback? What toast texts appear, does the asset lock release, and who can Edit a SENDBACK row? These have never been clicked.
- Which login acknowledges: the assigned employee's own login only, or can the assigner see and acknowledge those rows too? Earlier notes disagree.
- What should the system say when a user searches an asset in the wrong state (ASSIGNED asset on Assign, UNASSIGNED asset on Un Assign or Internal Movement)? The automation never tried this.
- Should the Assigned Date on the asset profile be set when an Assign is approved? It was not set in observation.
- Why does the ACKNOWLEDGED status filter return no rows? Is the status ever used?
- Is an Un Assign to the same employee also refused on Submit, or only on Draft?
- Employee Pin mode of Un Assign and Internal Movement: what happens to the other assets of the employee when saved? Not run through Draft.
- Can an acknowledged assignment be un-assigned or moved without any extra step? Can acknowledgement be undone?
- Is Reset on the forms expected to clear the grid and employee?

---

### Asset Expense and Voucher verification

**1. What this area is, in plain words**

An Asset Expense records money spent on an existing asset that does NOT extend its life, for example a routine repair. A user picks the asset, enters the amount, says where the cost comes from (Inventory = spare parts taken from stock; Accounts = an outside bill or service), picks the expense account, the vendor and a reference, then saves it as Draft or submits it. The system gives the expense an Expense ID (BBDEXPnnnnnnnn). An approver then approves it in Asset Expense Approval. On approval the system posts a journal voucher by itself (approved by "Auto Voucher"). The voucher can be found in the Accounting module (Voucher Search) and opened as a PDF. The expense does not change the asset itself (status, assignment, value stay as they were). Before this: the asset must already be registered and approved. After this: for the Accounts source only, someone must post a manual payment journal in Accounting (Supplier Payable-Opex Dr / Cash-Bank Cr); that payment is outside what has been tested.

**2. Before you test: getting the right starting state**

| State needed | Why | How to get it in short human steps |
|---|---|---|
| An APPROVED asset (a furniture item such as a Cabinet Table works well) with no Draft or Pending expense on it | The expense form searches by Asset Serial; an asset with an open (Draft or Pending) expense seems to be locked from the serial search | Register furniture (Registration > Asset Registration by AAQ), Submit, approve it in Asset Registration Approval List, note the Asset Serial. Use a different asset for each expense you want to keep open at the same time |
| A vendor available in the Vendor/Supplier/Lessor list | Vendor is required for both sources | Use a known vendor, for example search "ACE IT" and pick "ACE IT[P008937]" |
| A PENDING expense | To test approval | Create an expense and click Submit (or save Draft, reopen it and Submit). Note the Expense ID from the Asset Expense list |
| An APPROVED expense | To test the voucher | Open Fixed Asset > Asset Expenditure > Asset Expense Approval, filter Status = PENDING, click the Expense ID, click Approve. Note the Expense ID and the Date of Entry |
| A DRAFT expense | To test reopen and Submit | Create an expense, click Draft, note the Expense ID |
| Access to both the Fixed Asset module and the Accounting module | Voucher Search is in Accounting | The same login worked for both. The same user created and approved the expense in the tests (no second login). Whether approval by another user is required by policy is not known |

Standard test values used so far: Expense Amount 5000; Debit A/C "Other Maintenance Expenses[5108010101-07]"; Expense Ref. "EXP" plus 6 digits; Remarks "AUTOMATION_TEST expense Inventory" (or Accounts).

**3. Rules and what to test for each**

| Rule (plain words) | Where it applies | Pass example | Fail / boundary examples to test |
|---|---|---|---|
| Add the asset to the grid before choosing Expense Source | Create Asset Expense popup | Type serial, pick suggestion, enter 5000, click Add, then choose Source: Credit A/C fills | Choose Source before clicking Add: Credit A/C stays empty |
| Inventory source enables the Category chain and sets Credit A/C = Other Inventory [1107010401-02] | Create popup | Source = Inventory: Category, Sub Category, Item Name enabled; Category Furniture, Sub Category Wooden Furniture, Item Name Cabinet Table | Leave the chain empty and save (message not recorded); pick a chain that does not match the asset |
| Accounts source disables the Category chain and sets Credit A/C = Supplier Payable-Opex[2101010301-05] | Create popup | Source = Accounts: three drop-downs disabled | Switch Inventory to Accounts and back: Credit A/C must follow the source each time |
| Vendor/Supplier/Lessor Name is required for both sources | Draft and Submit | Vendor "ACE IT[P008937]" chosen: save succeeds | No vendor, either source: error "Vendor/Supplier/Lessor Name is required." and nothing is saved |
| Debit A/C is chosen by hand | Create popup | "Other Maintenance Expenses[5108010101-07]" | Left unselected (message not recorded) |
| Expense Ref. is required free text | Create popup | EXP123456 | Blank (message not recorded) |
| Expense ID is created when the expense is saved, for Draft and for Submit | Asset Expense list | New ID like BBDEXP00000001 shown, status DRAFT or PENDING | Two expenses must never get the same ID |
| Draft can be reopened (click Expense ID) and then Submitted | Asset Expense list | Reopened form shows all saved values; Submit gives PENDING | Values lost or changed after reopening |
| Only PENDING expenses can be approved; approval gives APPROVED in both lists | Approval list, Expense list | Approve: row APPROVED in both lists | Draft expense must not appear in the Approval list |
| Approval posts an automatic voucher with Dr Other Maintenance Expenses and Cr depending on source | Voucher Search | Inventory: Cr Other Inventory; Accounts: Cr Supplier Payable-Opex; both 5,000.00 | Wrong Cr account for the source; totals not equal |
| No voucher should exist before approval | Voucher Search | Draft or Pending Expense ID: "No data available in table" (DERIVED for expenses) | A voucher row found for a Draft or Pending expense |
| Voucher Search by Transaction Number is an exact match | Voucher Search | Full Expense ID finds the row | Partial text such as "BBDEXP" finds nothing |
| Date range on Voucher Search | Voucher Search | Date From and To both set to the expense Date of Entry finds the expense voucher | Range that excludes the entry date finds nothing (DERIVED) |

**4. Scenario catalogue**

#### Positive

**EXP-P01 — Verify asset details fill in after choosing the Asset Serial**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' (Category Furniture, Sub Category Wooden Furniture, Group Furniture and Fixture, Branch Head Office, Project [015] Microfinance (Dabi)) exists. It has no Draft or Pending expense. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Wait for the list 'List of Asset Expense' to load.
  3. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  4. In the field 'Asset Serial' type <Asset Serial>.
  5. Wait for the suggestion to appear (it reads <Asset Serial>-Cabinet Table>Wooden Furniture>Furniture>Furniture and Fixture) and click it.
  6. Read the read-only fields 'Asset Item Name', 'Asset Category', 'Asset Sub Category', 'Asset Group', 'Branch Name & Number' and 'Project Name & Number'.
  7. Read the field 'Date of Entry' and try to type in it.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Asset Item Name = Cabinet Table
  - Asset Category = Furniture
  - Asset Sub Category = Wooden Furniture
  - Asset Group = Furniture and Fixture
- Expected:
  1. System should fill 'Asset Item Name' with "Cabinet Table".
  2. System should fill 'Asset Category' with "Furniture" and 'Asset Sub Category' with "Wooden Furniture".
  3. System should fill 'Asset Group' with "Furniture and Fixture".
  4. System should fill 'Branch Name & Number' with a value containing "Head Office" and 'Project Name & Number' with a value containing "Microfinance (Dabi)".
  5. System should show all six fields as read-only (they cannot be typed in).
  6. System should show the 'Asset Serial' box holding the serial that was chosen (it starts with <Asset Serial>).
- Basis: VERIFIED (test_16)
- Check also: Click in the field 'Date of Entry' and try to type a date. System should show the business date and not accept typing (the field is read-only).

**EXP-P02 — Verify Add puts the asset in the grid and fills Total Expense Amount**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' (next to the asset details) type 5000.
  5. Click the button 'Add'.
  6. Read the asset grid below the Add button: the column 'Asset Serial' and the amount in the column 'Expense Amount'.
  7. Read the field 'Total Expense Amount'.
  8. Click the button 'Close' (nothing is saved).
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
- Expected:
  1. System should show one row in the asset grid with 'Asset Serial' = <Asset Serial> and 'Asset Item Name' = "Cabinet Table".
  2. System should show 5000 as the amount of that row in the column 'Expense Amount'.
  3. System should show 'Total Expense Amount' = 5000.
- Basis: VERIFIED (test_16)

**EXP-P03 — Verify Inventory source enables the Category chain and fills Credit A/C**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid.
  6. In 'Expense Source' choose 'Inventory'.
  7. Read the field 'Credit A/C'.
  8. Check that the drop-downs 'Select Category', 'Select Sub Category' and 'Item Name' can be used.
  9. In 'Select Category' choose 'Furniture'.
  10. In 'Select Sub Category' choose 'Wooden Furniture'.
  11. In 'Item Name' choose 'Cabinet Table'.
  12. Click the button 'Close' (nothing is saved).
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Inventory
  - Select Category = Furniture
  - Select Sub Category = Wooden Furniture
  - Item Name = Cabinet Table
- Expected:
  1. System should enable 'Select Category', 'Select Sub Category' and 'Item Name'.
  2. System should fill 'Credit A/C' with "Other Inventory [1107010401-02]".
  3. System should accept the choices Furniture, Wooden Furniture and Cabinet Table (they match the asset).
- Basis: VERIFIED (test_16)
- Check also: After step 6, read 'Credit A/C' once more after choosing the Category chain. System should still show "Other Inventory [1107010401-02]".

**EXP-P04 — Verify Accounts source disables the Category chain and fills Credit A/C**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid.
  6. In 'Expense Source' choose 'Accounts'.
  7. Read the field 'Credit A/C'.
  8. Check the drop-downs 'Select Category', 'Select Sub Category' and 'Item Name'.
  9. Click the button 'Close' (nothing is saved).
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Accounts
- Expected:
  1. System should disable 'Select Category', 'Select Sub Category' and 'Item Name'.
  2. System should fill 'Credit A/C' with "Supplier Payable-Opex[2101010301-05]".
- Basis: VERIFIED (test_16)

**EXP-P05 — Verify an Inventory expense can be saved as Draft and gets an Expense ID**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
  4. The vendor 'ACE IT[P008937]' is available in the Vendor/Supplier/Lessor list.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid and 'Total Expense Amount' shows 5000.
  6. In 'Expense Source' choose 'Inventory'.
  7. In 'Select Category' choose 'Furniture'.
  8. In 'Select Sub Category' choose 'Wooden Furniture'.
  9. In 'Item Name' choose 'Cabinet Table'.
  10. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  11. Check that 'Credit A/C' shows 'Other Inventory [1107010401-02]'.
  12. Click the link '-Select Party-' under 'Vendor/Supplier/Lessor Name', type ACE IT in the search box and click the option 'ACE IT[P008937]'.
  13. In the field 'Expense Ref.' type <Expense Ref.>.
  14. In the field 'Remarks/Note' type AUTOMATION_TEST expense Inventory.
  15. Click the button 'Draft'.
  16. Wait for the toast message to appear and read it.
  17. In the Asset Expense list, in 'Status' choose 'DRAFT', then click the button 'Search'.
  18. In the grid, find the row whose column 'Expense Ref.' is <Expense Ref.> and read the columns 'Expense ID' and 'Status'.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Inventory
  - Select Category = Furniture
  - Select Sub Category = Wooden Furniture
  - Item Name = Cabinet Table
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937] (search text: ACE IT)
  - Expense Ref. = <Expense Ref.> (EXP followed by 6 digits, for example EXP428774)
  - Remarks/Note = AUTOMATION_TEST expense Inventory
  - Status filter = DRAFT
- Expected:
  1. System should show the toast "Asset expense successfully drafted."
  2. System should close the popup.
  3. System should list a row with 'Status' = DRAFT and the matching 'Expense Ref.'.
  4. System should show a new 'Expense ID' of the form BBDEXPnnnnnnnn (for example BBDEXP00000001) in that row.
- Basis: VERIFIED (test_16)
- Check also: Write down the Expense ID as <Expense ID>. It is the key to find this expense later in the Approval list and in Voucher Search.

**EXP-P06 — Verify a Draft reopens with all saved values and can be Submitted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A DRAFT Inventory expense exists for the asset 'Cabinet Table' (Asset Serial <Asset Serial>), with Expense Amount 5000, Debit A/C 'Other Maintenance Expenses[5108010101-07]', Category chain Furniture / Wooden Furniture / Cabinet Table, vendor 'ACE IT[P008937]', Expense Ref. <Expense Ref.> and Remarks 'AUTOMATION_TEST expense Inventory'. Its Expense ID is known (<Expense ID>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. In 'Status' choose 'DRAFT', then click the button 'Search'.
  3. In the grid, click the link in the column 'Expense ID' of the row with <Expense ID>. The popup opens.
  4. Wait until the Sub Category, Item Name and account drop-downs are filled.
  5. Read the asset grid, 'Expense Source', 'Expense Ref.', 'Total Expense Amount', 'Remarks/Note', 'Debit A/C', 'Credit A/C', 'Select Category', 'Select Sub Category', 'Item Name' and 'Vendor/Supplier/Lessor Name'.
  6. Click the button 'Submit'.
  7. Wait for the toast message to appear and read it.
  8. In the Asset Expense list, in 'Status' choose 'PENDING', then click the button 'Search'.
  9. In the grid find the row with <Expense ID> and read the columns 'Expense ID' and 'Status'.
- Test data:
  - <ERP Username> / <ERP Password>
  - Expense ID = <Expense ID>
  - Asset Serial = <Asset Serial>
  - Expense Source = Inventory
  - Expense Ref. = <Expense Ref.>
  - Total Expense Amount = 5000
  - Remarks/Note = AUTOMATION_TEST expense Inventory
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Credit A/C = Other Inventory [1107010401-02]
  - Select Category / Select Sub Category / Item Name = Furniture / Wooden Furniture / Cabinet Table
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Status filter = DRAFT, then PENDING
- Expected:
  1. System should show the saved asset (<Asset Serial>) in the asset grid.
  2. System should show 'Expense Source' = Inventory, 'Total Expense Amount' = 5000 and the saved 'Expense Ref.' and 'Remarks/Note'.
  3. System should show 'Debit A/C' = "Other Maintenance Expenses[5108010101-07]" and 'Credit A/C' = "Other Inventory [1107010401-02]".
  4. System should show the Category chain Furniture / Wooden Furniture / Cabinet Table and the vendor "ACE IT".
  5. System should show the toast "Asset expense successfully submitted."
  6. System should list the row <Expense ID> with 'Status' = PENDING.
- Basis: VERIFIED (test_16)
- Check also: Compare the Expense ID before and after Submit. System should show the same <Expense ID> (it does not change between DRAFT and PENDING).

**EXP-P07 — Verify an Accounts expense can be Submitted directly**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
  4. The vendor 'ACE IT[P008937]' is available in the Vendor/Supplier/Lessor list.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid.
  6. In 'Expense Source' choose 'Accounts'.
  7. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  8. Check that 'Credit A/C' shows 'Supplier Payable-Opex[2101010301-05]'.
  9. Click the link '-Select Party-' under 'Vendor/Supplier/Lessor Name', type ACE IT and click the option 'ACE IT[P008937]'.
  10. In the field 'Expense Ref.' type <Expense Ref.>.
  11. In the field 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  12. Click the button 'Submit'.
  13. Wait for the toast message to appear and read it.
  14. In the Asset Expense list, in 'Status' choose 'PENDING', then click the button 'Search'.
  15. Find the row whose 'Expense Ref.' is <Expense Ref.> and read 'Expense ID' and 'Status'.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Accounts
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937] (search text: ACE IT)
  - Expense Ref. = <Expense Ref.> (EXP followed by 6 digits)
  - Remarks/Note = AUTOMATION_TEST expense Accounts
  - Status filter = PENDING
- Expected:
  1. System should show the toast "Asset expense successfully submitted."
  2. System should close the popup.
  3. System should list the expense with 'Status' = PENDING and a new 'Expense ID' of the form BBDEXPnnnnnnnn.
- Basis: VERIFIED (test_16)

**EXP-P08 — Verify an Inventory expense can be Submitted directly**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
  4. The vendor 'ACE IT[P008937]' is available in the Vendor/Supplier/Lessor list.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid.
  6. In 'Expense Source' choose 'Inventory'.
  7. In 'Select Category' choose 'Furniture'.
  8. In 'Select Sub Category' choose 'Wooden Furniture'.
  9. In 'Item Name' choose 'Cabinet Table'.
  10. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  11. Click the link '-Select Party-' under 'Vendor/Supplier/Lessor Name', type ACE IT and click the option 'ACE IT[P008937]'.
  12. In the field 'Expense Ref.' type <Expense Ref.>.
  13. In the field 'Remarks/Note' type AUTOMATION_TEST expense Inventory.
  14. Click the button 'Submit'.
  15. Wait for the toast message to appear and read it.
  16. In the Asset Expense list, in 'Status' choose 'PENDING', then click the button 'Search'.
  17. Find the row whose 'Expense Ref.' is <Expense Ref.> and read 'Expense ID' and 'Status'.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Inventory
  - Select Category = Furniture
  - Select Sub Category = Wooden Furniture
  - Item Name = Cabinet Table
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937] (search text: ACE IT)
  - Expense Ref. = <Expense Ref.> (EXP followed by 6 digits)
  - Remarks/Note = AUTOMATION_TEST expense Inventory
- Expected:
  1. System should show the toast "Asset expense successfully submitted."
  2. System should close the popup.
  3. System should list the row with 'Status' = PENDING and a new 'Expense ID' of the form BBDEXPnnnnnnnn.
- Basis: DERIVED (not yet run)
- Check also: Repeat with 'Expense Source' = 'Accounts' saved first with 'Draft' and then reopened and submitted (the fourth combination). System should show "Asset expense successfully drafted." and then "Asset expense successfully submitted." and the row PENDING.

**EXP-P09 — Verify a PENDING expense appears in the Approval list and opens read-only**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A PENDING expense exists for the asset 'Cabinet Table' with Expense Amount 5000, Expense Ref. <Expense Ref.>, Remarks 'AUTOMATION_TEST expense Inventory', Debit A/C 'Other Maintenance Expenses[5108010101-07]' and Credit A/C 'Other Inventory [1107010401-02]'. Its Expense ID is known (<Expense ID>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense Approval'.
  2. In 'Status' choose 'PENDING', then click the button 'Search'.
  3. In the grid find the row with <Expense ID>.
  4. Click the link in the column 'Expense ID' of that row. A popup opens.
  5. Wait until the 'Debit A/C' and 'Credit A/C' drop-downs are filled.
  6. Read 'Expense Ref.', 'Total Expense Amount', 'Remarks/Note', 'Date of Entry', 'Debit A/C', 'Credit A/C' and the asset grid.
  7. Try to type in 'Expense Ref.' and 'Remarks/Note'.
  8. Read the buttons at the bottom of the popup.
- Test data:
  - <ERP Username> / <ERP Password>
  - Status filter = PENDING
  - Expense ID = <Expense ID>
  - Expense Ref. = <Expense Ref.>
  - Total Expense Amount = 5000
  - Remarks/Note = AUTOMATION_TEST expense Inventory
- Expected:
  1. System should list the row <Expense ID> with 'Status' = PENDING.
  2. System should open the popup with every field read-only (typing is not possible).
  3. System should show 'Expense Ref.' = <Expense Ref.>, 'Total Expense Amount' = 5000, 'Remarks/Note' = "AUTOMATION_TEST expense Inventory" and the 'Date of Entry'.
  4. System should show 'Debit A/C' = "Other Maintenance Expenses[5108010101-07]" and 'Credit A/C' = "Other Inventory [1107010401-02]".
  5. System should show the asset serial in the asset grid.
  6. System should show the buttons 'Approve', 'Reject', 'Sendback' and 'Close'.
- Basis: VERIFIED (test_16 full flows; test_17 only reads the lists)
- Check also: Click 'Close'. System should close the popup and leave the row PENDING.

**EXP-P10 — Verify Approve makes the expense APPROVED in both lists**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A PENDING Inventory expense exists for the asset 'Cabinet Table' (Asset Serial <Asset Serial>), Expense Amount 5000. Its Expense ID is known (<Expense ID>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense Approval'.
  2. In 'Status' choose 'PENDING', then click the button 'Search'.
  3. In the grid click the link in the column 'Expense ID' of the row with <Expense ID>. A popup opens.
  4. Click the button 'Approve'.
  5. Wait for the toast message to appear and read it (both lines).
  6. In the Approval list, in 'Status' choose 'APPROVED', then click the button 'Search'.
  7. Find the row <Expense ID> and read the columns 'Status', 'Approved By' and 'Approve Date'.
  8. Click the link 'Asset Expense' in the menu 'Asset Expenditure' to open the Asset Expense list.
  9. In 'Status' choose 'APPROVED', then click the button 'Search'.
  10. Find the row <Expense ID> and read the columns 'Status', 'Approved By' and 'Approve Date'.
- Test data:
  - <ERP Username> / <ERP Password>
  - Expense ID = <Expense ID>
  - Status filter = PENDING, then APPROVED
- Expected:
  1. System should show a toast starting "Asset Expense approved successfully." and, for an Inventory expense, a second line "Journal voucher submitted successfully."
  2. System should close the popup.
  3. System should show the row <Expense ID> with 'Status' = APPROVED in the Approval list, with 'Approved By' and 'Approve Date' filled.
  4. System should show the row <Expense ID> with 'Status' = APPROVED in the Asset Expense list, with 'Approved By' and 'Approve Date' filled.
- Basis: VERIFIED (test_16 full flows)
- Check also: Open the asset 'Cabinet Table' (Asset Serial <Asset Serial>) in the asset list and read its status, assignment and value. System should show them unchanged (an expense does not change the asset).

**EXP-P11 — Verify the voucher row in Voucher Search for an approved Inventory expense**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same login can open the Accounting module.
  2. An APPROVED Inventory expense of 5000 exists. Its Expense ID (<Expense ID>, for example BBDEXP00000001) and its 'Date of Entry' (<Date of Entry>) are known.
- Steps:
  1. Click the tab 'Accounting' in the top bar. The Accounting module opens in the same browser tab.
  2. Click the menu 'Voucher', then click the link 'Voucher Search'.
  3. Wait for the page to settle. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>.
  4. Wait for the calendar to close. Click the calendar icon beside 'Date To' and click the day number of <Date of Entry>.
  5. In the field 'Transaction Number' type <Expense ID> in full.
  6. Click the button 'Search'.
  7. Wait for the grid 'Voucher Search List' to fill.
  8. Read the columns 'Date', 'Voucher No.', 'Transaction No', 'Amount', 'Particular' and 'Status' of the row.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = <Date of Entry>
  - Date To = <Date of Entry>
  - Transaction Number = <Expense ID>
- Expected:
  1. System should list exactly one row.
  2. System should show 'Transaction No' = <Expense ID>.
  3. System should show 'Amount' = 5,000.
  4. System should show 'Particular' = "Asset Expense Voucher, Reference no: <Expense ID>".
  5. System should show 'Status' = "Approved".
  6. System should show a 'Preview' link in the row and a 'Voucher No.' value.
- Basis: VERIFIED (test_17)
- Check also: Write down the 'Voucher No.' as <Voucher No.>. Open the Preview of the row and check that the VIN equals <Voucher No.> (see the next voucher check).

**EXP-P12 — Verify the voucher preview (Inventory): lines, totals and references**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. An APPROVED Inventory expense of 5000 exists with Expense ID <Expense ID> and Date of Entry <Date of Entry>. The user who created it is known.
- Steps:
  1. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  2. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>.
  3. Click the calendar icon beside 'Date To' and click the day number of <Date of Entry>.
  4. In the field 'Transaction Number' type <Expense ID> in full.
  5. Click the button 'Search' and wait for the row. Read 'Voucher No.' as <Voucher No.>.
  6. Click the link 'Preview' in the row. A PDF opens in a new browser tab.
  7. Read the header: title, branch, project, VIN, Creation Date and Posted Date.
  8. Read the table lines: Accounts Code, Heads of Accounts, Debit, Credit and Particulars.
  9. Read the totals line and 'Amount (In Word)'.
  10. Read the footer: 'Prepared By' and 'Approved By'.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = Date To = <Date of Entry>
  - Transaction Number = <Expense ID>
  - Amount = 5000
- Expected:
  1. System should show the title "JOURNAL VOUCHER".
  2. System should show a branch containing "Head Office" and a project containing "Microfinance (Dabi)".
  3. System should show VIN = <Voucher No.> (the same as in the search row).
  4. System should show 'Creation Date' and 'Posted Date' equal to <Date of Entry>.
  5. System should show the debit line: account code 5108010101-07, head "Other Maintenance Expenses", Debit 5,000.00, Credit 0.00.
  6. System should show the credit line: account code 1107010401-02, head "Other Inventory", Credit 5,000.00, Debit 0.00.
  7. System should show the reference "Asset Expense Voucher, Reference no: <Expense ID>" (the Expense ID) on every line.
  8. System should show Total Debit = Total Credit = 5,000.00.
  9. System should show 'Amount (In Word)' containing "Five Thousand".
  10. System should show 'Approved By' = "Auto Voucher".
- Basis: VERIFIED (test_16 full flow reads the preview PDF; the CHANGELOG notes voucher checks may fail at times, so re-confirm on the current environment)
- Check also: Read 'Prepared By' in the footer. System should show the user who created the expense.

**EXP-P13 — Verify the voucher preview (Accounts): credit goes to Supplier Payable-Opex**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. An APPROVED Accounts expense of 5000 exists with Expense ID <Expense ID> and Date of Entry <Date of Entry>.
- Steps:
  1. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  2. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>.
  3. Click the calendar icon beside 'Date To' and click the day number of <Date of Entry>.
  4. In the field 'Transaction Number' type <Expense ID> in full.
  5. Click the button 'Search' and wait for the row. Read 'Voucher No.' as <Voucher No.>.
  6. Click the link 'Preview' in the row. A PDF opens in a new browser tab.
  7. Read the header: title, branch, project, VIN, Creation Date and Posted Date.
  8. Read the table lines: Accounts Code, Heads of Accounts, Debit, Credit and Particulars.
  9. Read the totals line and 'Amount (In Word)'.
  10. Read 'Approved By' in the footer.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = Date To = <Date of Entry>
  - Transaction Number = <Expense ID>
  - Amount = 5000
- Expected:
  1. System should show the title "JOURNAL VOUCHER", a branch containing "Head Office", a project containing "Microfinance (Dabi)", VIN = <Voucher No.> and Creation Date and Posted Date = <Date of Entry>.
  2. System should show the debit line: account code 5108010101-07, head "Other Maintenance Expenses", Debit 5,000.00.
  3. System should show the credit line: account code 2101010301-05, head "Supplier Payable-Opex", Credit 5,000.00.
  4. System should show the reference "Asset Expense Voucher, Reference no: <Expense ID>" on every line.
  5. System should show Total Debit = Total Credit = 5,000.00 and 'Amount (In Word)' containing "Five Thousand".
  6. System should show 'Approved By' = "Auto Voucher".
- Basis: VERIFIED (test_16 full flow reads the preview PDF)
- Check also: In the search row read 'Particular'. System should show "Asset Expense Voucher, Reference no: <Expense ID>".

**EXP-P14 — Verify the Asset Expense list filters and columns**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. At least one expense exists.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the drop-down 'Status' and read all options.
  3. Read the filter labels 'Entry From Date' and 'Entry To Date' and the buttons beside them.
  4. Read the column headings of the grid 'List of Asset Expense'.
- Test data:
  - <ERP Username> / <ERP Password>
- Expected:
  1. System should list the 'Status' options in this order: "-Select Status-", PENDING, APPROVED, REJECTED, DRAFT, SENDBACK.
  2. System should show the grid columns: SL, Expense ID, Entry Date, Expense Amount, Expense Ref., Status, Created By, Approved By, Approve Date, Note/Remarks.
  3. System should show the filters 'Entry From Date' and 'Entry To Date' and the buttons 'Search' and 'Reset'.
- Basis: VERIFIED (test_16)
- Check also: Click 'Create'. System should open the popup 'Create Asset Expense'; click 'Close' to leave it.

**EXP-P15 — Verify the Asset Expense Approval list filters and columns**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. At least one non-draft expense exists.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense Approval'.
  2. Click the drop-down 'Status' and read all options.
  3. Read the column headings of the grid 'List of Asset Expense Approval'.
  4. Read the filter labels 'Entry From Date' and 'Entry To Date', the buttons 'Search' and 'Reset' and the button 'Approve' under the grid.
- Test data:
  - <ERP Username> / <ERP Password>
- Expected:
  1. System should list the 'Status' options in this order: "-Select Status-", PENDING, APPROVED, REJECTED, SENDBACK (no DRAFT).
  2. System should show the grid columns: SL, Expense ID, Entry Date, Supplier, Expense Amount, Status, Created By, Approved By, Approve Date, plus a checkbox column.
- Basis: VERIFIED (test_17)
- Check also: Check that the buttons 'Search', 'Reset' and 'Approve' are visible on the page.

#### Negative

**EXP-N01 — Verify Draft without a vendor is rejected (Inventory)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid.
  6. In 'Expense Source' choose 'Inventory'.
  7. In 'Select Category' choose 'Furniture'.
  8. In 'Select Sub Category' choose 'Wooden Furniture'.
  9. In 'Item Name' choose 'Cabinet Table'.
  10. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  11. In the field 'Expense Ref.' type <Expense Ref.>.
  12. Do not choose anything in 'Vendor/Supplier/Lessor Name' (it keeps '-Select Party-').
  13. Click the button 'Draft'.
  14. Wait for the toast message to appear and read it.
  15. Check that the popup is still open.
  16. Click the button 'Close'.
  17. In the Asset Expense list, in 'Status' choose 'DRAFT', then click the button 'Search' and look for the row with 'Expense Ref.' <Expense Ref.>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Inventory
  - Select Category = Furniture
  - Select Sub Category = Wooden Furniture
  - Item Name = Cabinet Table
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Expense Ref. = <Expense Ref.> (EXP followed by 6 digits)
  - Vendor/Supplier/Lessor Name = (left empty)
- Expected:
  1. System should show the error "Vendor/Supplier/Lessor Name is required."
  2. System should keep the popup open.
  3. System should save nothing: no row with <Expense Ref.> appears in the list.
- Basis: VERIFIED (test_16)

**EXP-N02 — Verify Draft without a vendor is rejected (Accounts)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid.
  6. In 'Expense Source' choose 'Accounts'.
  7. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  8. In the field 'Expense Ref.' type <Expense Ref.>.
  9. Do not choose anything in 'Vendor/Supplier/Lessor Name' (it keeps '-Select Party-').
  10. Click the button 'Draft'.
  11. Wait for the toast message to appear and read it.
  12. Check that the popup is still open.
  13. Click the button 'Close'.
  14. In the Asset Expense list, in 'Status' choose 'DRAFT', then click the button 'Search' and look for the row with 'Expense Ref.' <Expense Ref.>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Accounts
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Expense Ref. = <Expense Ref.> (EXP followed by 6 digits)
  - Vendor/Supplier/Lessor Name = (left empty)
- Expected:
  1. System should show the error "Vendor/Supplier/Lessor Name is required."
  2. System should keep the popup open and save nothing (no row with <Expense Ref.> in the list).
- Basis: VERIFIED (test_16)

**EXP-N03 — Verify direct Submit without a vendor is rejected**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'. Check that the asset is in the grid.
  6. In 'Expense Source' choose 'Inventory'.
  7. In 'Select Category' choose 'Furniture'.
  8. In 'Select Sub Category' choose 'Wooden Furniture'.
  9. In 'Item Name' choose 'Cabinet Table'.
  10. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  11. In the field 'Expense Ref.' type <Expense Ref.>.
  12. Do not choose anything in 'Vendor/Supplier/Lessor Name'.
  13. Click the button 'Submit' (not 'Draft').
  14. Wait for the toast message to appear and read it.
  15. Click the button 'Close'.
  16. In the Asset Expense list, in 'Status' choose 'PENDING', then click the button 'Search' and look for the row with 'Expense Ref.' <Expense Ref.>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Inventory
  - Select Category = Furniture
  - Select Sub Category = Wooden Furniture
  - Item Name = Cabinet Table
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Expense Ref. = <Expense Ref.>
  - Vendor/Supplier/Lessor Name = (left empty)
- Expected:
  1. System should show "Vendor/Supplier/Lessor Name is required."
  2. System should save nothing: no row with <Expense Ref.> in the list.
- Basis: DERIVED (not yet run). The message is recorded for both Draft and Submit in the notes.

**EXP-N04 — Verify Credit A/C stays empty if Expense Source is chosen before the asset is added**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears. Do not click 'Add' yet.
  4. In 'Expense Source' choose 'Inventory'.
  5. Read the field 'Credit A/C'.
  6. In the field 'Expense Amount' type 5000.
  7. Click the button 'Add'.
  8. Read the field 'Credit A/C' again.
  9. In 'Expense Source' choose 'Accounts', then choose 'Inventory' again.
  10. Read the field 'Credit A/C' again.
  11. Click the button 'Close' (nothing is saved).
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Source = Inventory (chosen before Add)
  - Expense Amount = 5000
- Expected:
  1. System should leave 'Credit A/C' empty after step 4 (the asset is not yet added).
  2. System should still show 'Credit A/C' empty after Add in step 7.
  3. System should fill 'Credit A/C' with "Other Inventory [1107010401-02]" after the source is chosen again once the asset is in the grid.
- Basis: VERIFIED (rule from the checklist)
- Check also: With 'Credit A/C' empty (after step 8), fill the other fields and click 'Draft'. Read what the form does. Whether the form blocks saving when Credit A/C is empty is not recorded.

**EXP-N05 — Verify Submit with no Expense Ref. is rejected**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
  4. The vendor 'ACE IT[P008937]' is available.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'.
  6. In 'Expense Source' choose 'Accounts'.
  7. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  8. Click the link '-Select Party-' under 'Vendor/Supplier/Lessor Name', type ACE IT and click the option 'ACE IT[P008937]'.
  9. Leave the field 'Expense Ref.' empty.
  10. In the field 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  11. Click the button 'Submit'.
  12. Wait for the message to appear and read it.
  13. Click the button 'Close'.
  14. In the Asset Expense list, in 'Status' choose 'PENDING', click 'Search' and check that no new row appears for this asset.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Accounts
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Expense Ref. = (left empty)
  - Remarks/Note = AUTOMATION_TEST expense Accounts
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should not save the expense: no new PENDING row appears.
- Basis: DERIVED (not yet run)

**EXP-N06 — Verify Submit with no Debit A/C is rejected**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
  4. The vendor 'ACE IT[P008937]' is available.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'.
  6. In 'Expense Source' choose 'Accounts'.
  7. Leave 'Debit A/C' unselected.
  8. Click the link '-Select Party-' under 'Vendor/Supplier/Lessor Name', type ACE IT and click the option 'ACE IT[P008937]'.
  9. In the field 'Expense Ref.' type <Expense Ref.>.
  10. In the field 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  11. Click the button 'Submit'.
  12. Wait for the message to appear and read it.
  13. Click the button 'Close'.
  14. In the Asset Expense list, in 'Status' choose 'PENDING', click 'Search' and look for the row with 'Expense Ref.' <Expense Ref.>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Accounts
  - Debit A/C = (left unselected)
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Expense Ref. = <Expense Ref.> (EXP followed by 6 digits)
  - Remarks/Note = AUTOMATION_TEST expense Accounts
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should not save the expense: no row with <Expense Ref.> in the list.
- Basis: DERIVED (not yet run)

**EXP-N07 — Verify Submit without adding any asset is rejected**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. The vendor 'ACE IT[P008937]' is available.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. Do not type an 'Asset Serial' and do not click 'Add' (the asset grid stays empty).
  4. In 'Expense Source' choose 'Accounts'.
  5. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  6. Click the link '-Select Party-' under 'Vendor/Supplier/Lessor Name', type ACE IT and click the option 'ACE IT[P008937]'.
  7. In the field 'Expense Ref.' type <Expense Ref.>.
  8. Click the button 'Submit'.
  9. Wait for the message to appear and read it.
  10. Click the button 'Close'.
  11. In the Asset Expense list, in 'Status' choose 'PENDING', click 'Search' and look for the row with 'Expense Ref.' <Expense Ref.>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = (not entered)
  - Expense Source = Accounts
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Expense Ref. = <Expense Ref.>
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should not save the expense: no row with <Expense Ref.> in the list.
- Basis: DERIVED (not yet run)

**EXP-N08 — Verify an Inventory expense with the Category chain left empty is rejected**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
  4. The vendor 'ACE IT[P008937]' is available.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'.
  6. In 'Expense Source' choose 'Inventory'.
  7. Leave 'Select Category', 'Select Sub Category' and 'Item Name' unselected.
  8. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  9. Click the link '-Select Party-' under 'Vendor/Supplier/Lessor Name', type ACE IT and click the option 'ACE IT[P008937]'.
  10. In the field 'Expense Ref.' type <Expense Ref.>.
  11. In the field 'Remarks/Note' type AUTOMATION_TEST expense Inventory.
  12. Click the button 'Submit'.
  13. Wait for the message to appear and read it.
  14. Click the button 'Close'.
  15. In the Asset Expense list, in 'Status' choose 'PENDING', click 'Search' and look for the row with 'Expense Ref.' <Expense Ref.>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Inventory
  - Select Category / Select Sub Category / Item Name = (left unselected)
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Expense Ref. = <Expense Ref.>
  - Remarks/Note = AUTOMATION_TEST expense Inventory
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should not save the expense: no row with <Expense Ref.> in the list.
- Basis: DERIVED (not yet run)

**EXP-N09 — Verify partial Transaction Number finds no voucher**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same login can open the Accounting module.
  2. An APPROVED expense exists with Expense ID <Expense ID> (for example BBDEXP00000001) and Date of Entry <Date of Entry>.
- Steps:
  1. Click the tab 'Accounting' in the top bar. The Accounting module opens.
  2. Click the menu 'Voucher', then click the link 'Voucher Search'.
  3. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>.
  4. Click the calendar icon beside 'Date To' and click the day number of <Date of Entry>.
  5. In the field 'Transaction Number' type BBDEXP.
  6. Click the button 'Search'.
  7. Wait for the grid 'Voucher Search List' to finish loading and read it.
  8. Clear 'Transaction Number', type the full <Expense ID> and click 'Search' again.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = Date To = <Date of Entry>
  - Transaction Number = BBDEXP (first search), then <Expense ID>
- Expected:
  1. System should show "No data available in table" for the partial text BBDEXP (exact match only).
  2. System should list one voucher row for the full <Expense ID>.
- Basis: VERIFIED (rule noted from voucher search work)

**EXP-N10 — Verify a Draft expense is not in the Approval list**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A DRAFT expense exists with Expense ID <Expense ID>, not yet submitted.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense Approval'.
  2. Click the drop-down 'Status' and read the options.
  3. In 'Status' choose 'PENDING', click 'Search' and look for <Expense ID>.
  4. In 'Status' choose 'APPROVED', click 'Search' and look for <Expense ID>.
  5. In 'Status' choose 'REJECTED', click 'Search' and look for <Expense ID>.
  6. In 'Status' choose 'SENDBACK', click 'Search' and look for <Expense ID>.
  7. In 'Status' choose '-Select Status-', click 'Search' and look for <Expense ID>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Expense ID = <Expense ID> (a Draft)
  - Status filter = PENDING, APPROVED, REJECTED, SENDBACK, -Select Status-
- Expected:
  1. System should not list <Expense ID> for any of the status searches.
  2. System should show the 'Status' options "-Select Status-", PENDING, APPROVED, REJECTED, SENDBACK (no DRAFT option).
- Basis: DERIVED (not yet run)

#### Edge Case

**EXP-E01 — Verify Source can be switched Inventory to Accounts and back**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 5000.
  5. Click the button 'Add'.
  6. In 'Expense Source' choose 'Inventory'. Read 'Credit A/C' and check whether 'Select Category', 'Select Sub Category' and 'Item Name' are enabled.
  7. In 'Expense Source' choose 'Accounts'. Read 'Credit A/C' and check the three drop-downs again.
  8. In 'Expense Source' choose 'Inventory' again. Read 'Credit A/C' and check the three drop-downs again.
  9. Click the button 'Close' (nothing is saved).
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Inventory, then Accounts, then Inventory
- Expected:
  1. System should (Inventory, first time) enable the Category chain and show 'Credit A/C' = "Other Inventory [1107010401-02]".
  2. System should (Accounts) disable the Category chain and show 'Credit A/C' = "Supplier Payable-Opex[2101010301-05]".
  3. System should (Inventory again) enable the Category chain and show 'Credit A/C' = "Other Inventory [1107010401-02]".
- Basis: VERIFIED (test_16, source switch)
- Check also: Before step 7 choose Furniture / Wooden Furniture / Cabinet Table, then switch to Accounts and back to Inventory. Read whether the chain values are cleared or kept (not recorded).

**EXP-E02 — Verify a date range that excludes the entry date finds no voucher**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same login can open the Accounting module.
  2. An APPROVED expense exists with Expense ID <Expense ID> and Date of Entry <Date of Entry>.
- Steps:
  1. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  2. Click the calendar icon beside 'Date From' and click the day number of the day after <Date of Entry>.
  3. Wait for the calendar to close, then click the calendar icon beside 'Date To' and click the same day number.
  4. In the field 'Transaction Number' type <Expense ID>.
  5. Click the button 'Search'.
  6. Wait for the grid to finish loading and read it.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = Date To = the day after <Date of Entry>
  - Transaction Number = <Expense ID>
- Expected:
  1. System should show "No data available in table".
- Basis: DERIVED (not yet run)
- Check also: Search registration vouchers with the Date From and Date To left empty and the full Registration Number in 'Transaction Number'. Registration vouchers were missed when a date range was set, so System should list the voucher with no dates.

**EXP-E03 — Verify Expense ID is unique across several expenses**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two APPROVED Furniture assets 'Cabinet Table' exist with no Draft or Pending expense. Their Asset Serials are known (<Asset Serial 1> and <Asset Serial 2>).
  4. The vendor 'ACE IT[P008937]' is available.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. In 'Asset Serial' type <Asset Serial 1> and click the suggestion.
  3. In the field 'Expense Amount' type 5000 and click the button 'Add'.
  4. In 'Expense Source' choose 'Accounts'.
  5. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  6. Click the link '-Select Party-', type ACE IT and click the option 'ACE IT[P008937]'.
  7. In 'Expense Ref.' type <Expense Ref. 1>, and in 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  8. Click the button 'Submit' and wait for the toast.
  9. Click the link 'Create' again. In 'Asset Serial' type <Asset Serial 2> and click the suggestion.
  10. In the field 'Expense Amount' type 5000 and click the button 'Add'.
  11. In 'Expense Source' choose 'Accounts'.
  12. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  13. Click the link '-Select Party-', type ACE IT and click the option 'ACE IT[P008937]'.
  14. In 'Expense Ref.' type <Expense Ref. 2>, and in 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  15. Click the button 'Submit' and wait for the toast.
  16. In the Asset Expense list, in 'Status' choose 'PENDING', click 'Search'.
  17. Read the column 'Expense ID' of the rows with 'Expense Ref.' <Expense Ref. 1> and <Expense Ref. 2>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial 1> / <Asset Serial 2>
  - Expense Amount = 5000 (both)
  - Expense Source = Accounts
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Expense Ref. = <Expense Ref. 1> / <Expense Ref. 2> (EXP followed by 6 digits each)
  - Remarks/Note = AUTOMATION_TEST expense Accounts
- Expected:
  1. System should give each expense a different 'Expense ID' of the form BBDEXPnnnnnnnn.
  2. System should number them in increasing order (for example BBDEXP00000001, BBDEXP00000002).
- Basis: DERIVED (not yet run)

**EXP-E04 — Verify an asset with a Draft or Pending expense cannot be found in the serial search**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An asset 'Cabinet Table' (Asset Serial <Asset Serial>) has a DRAFT or PENDING expense.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial>.
  4. Wait a few seconds and look for the suggestion list.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System seems to offer no suggestion for this serial (the asset is locked). Confirm with the BA.
- Basis: OBSERVED (catalog; stated as "seems to")
- Check also: Approve that expense in 'Asset Expense Approval', then type the same serial again in 'Create'. System should offer the suggestion again.

**EXP-E05 — Verify the Expense ID is generated for Draft and for direct Submit alike**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two APPROVED Furniture assets 'Cabinet Table' exist with no Draft or Pending expense (<Asset Serial 1> and <Asset Serial 2>).
  4. The vendor 'ACE IT[P008937]' is available.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. In 'Asset Serial' type <Asset Serial 1> and click the suggestion.
  3. In 'Expense Amount' type 5000 and click the button 'Add'.
  4. In 'Expense Source' choose 'Accounts'.
  5. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  6. Click the link '-Select Party-', type ACE IT and click the option 'ACE IT[P008937]'.
  7. In 'Expense Ref.' type <Expense Ref. 1> and in 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  8. Click the button 'Draft' and wait for the toast.
  9. Click the link 'Create'. In 'Asset Serial' type <Asset Serial 2> and click the suggestion.
  10. In 'Expense Amount' type 5000 and click the button 'Add'.
  11. In 'Expense Source' choose 'Accounts'.
  12. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  13. Click the link '-Select Party-', type ACE IT and click the option 'ACE IT[P008937]'.
  14. In 'Expense Ref.' type <Expense Ref. 2> and in 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  15. Click the button 'Submit' and wait for the toast.
  16. In the Asset Expense list leave 'Status' on '-Select Status-' and click 'Search'.
  17. Compare the rows with 'Expense Ref.' <Expense Ref. 1> and <Expense Ref. 2>: read 'Expense ID' and 'Status'.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial 1> / <Asset Serial 2>
  - Expense Amount = 5000 (both)
  - Expense Source = Accounts
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Expense Ref. = <Expense Ref. 1> / <Expense Ref. 2>
  - Remarks/Note = AUTOMATION_TEST expense Accounts
- Expected:
  1. System should show the toast "Asset expense successfully drafted." for the first and "Asset expense successfully submitted." for the second.
  2. System should show an Expense ID on both rows: the first with 'Status' DRAFT, the second with 'Status' PENDING.
- Basis: VERIFIED (test_16)

**EXP-E06 — Verify Total Expense Amount boundary values**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' exists with no Draft or Pending expense. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In the field 'Expense Amount' type 0 and click the button 'Add'. Read any message and the asset grid.
  5. Clear the field 'Expense Amount', type 0.01 and click the button 'Add'. Read any message, the asset grid and 'Total Expense Amount'.
  6. If the asset was added, remove its row with the button in the column 'Action' (or click 'Reset' in the asset block), then select the asset again.
  7. Clear the field 'Expense Amount', type 99999999 and click the button 'Add'. Read any message, the asset grid and 'Total Expense Amount'.
  8. Remove the row again (or click 'Reset' in the asset block) and select the asset again.
  9. Clear the field 'Expense Amount', type -100 and click the button 'Add'. Read any message, the asset grid and 'Total Expense Amount'.
  10. Click the button 'Close' (nothing is saved).
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 0, then 0.01, then 99999999, then -100
- Expected:
  1. System should show a validation message for invalid values (exact text to be confirmed) and not add the asset for 0 and for -100.
  2. System should accept the valid values (0.01 and 99999999 are assumed valid; the limits are to be confirmed with the BA) and show the same value in 'Total Expense Amount'.
- Basis: DERIVED (not yet run)

#### Business

**EXP-B01 — Verify no voucher exists for a Draft expense**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same login can open the Accounting module.
  2. A DRAFT expense exists (saved with 'Draft', not submitted). Its Expense ID is known (<Expense ID>).
- Steps:
  1. Click the tab 'Accounting' in the top bar. The Accounting module opens.
  2. Click the menu 'Voucher', then click the link 'Voucher Search'.
  3. Leave 'Date From' and 'Date To' empty.
  4. In the field 'Transaction Number' type <Expense ID> in full.
  5. Click the button 'Search'.
  6. Wait for the grid 'Voucher Search List' to finish loading and read it.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = Date To = (empty)
  - Transaction Number = <Expense ID> (a Draft expense)
- Expected:
  1. System should show "No data available in table".
- Basis: DERIVED (not yet run). The same check is verified for registrations (a registration without approval has no voucher), but not for expenses.
- Check also: Repeat the search after setting 'Date From' and 'Date To' to the expense 'Date of Entry'. System should again show "No data available in table".

**EXP-B02 — Verify no voucher exists for a Pending expense**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same login can open the Accounting module and the Fixed Asset module.
  2. A PENDING expense exists (submitted, not yet approved). Its Expense ID is known (<Expense ID>) and its Date of Entry (<Date of Entry>).
- Steps:
  1. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  2. Leave 'Date From' and 'Date To' empty.
  3. In the field 'Transaction Number' type <Expense ID> in full.
  4. Click the button 'Search'.
  5. Wait for the grid to finish loading and read it.
  6. Go back to the Fixed Asset module, click the tab 'Asset Expenditure', then the link 'Asset Expense Approval'.
  7. In 'Status' choose 'PENDING', click 'Search', click the link in the column 'Expense ID' of the row <Expense ID> and click the button 'Approve'. Wait for the toast.
  8. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then the link 'Voucher Search'.
  9. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>; click the calendar icon beside 'Date To' and click the same day number.
  10. In the field 'Transaction Number' type <Expense ID>, click 'Search' and read the grid.
- Test data:
  - <ERP Username> / <ERP Password>
  - Transaction Number = <Expense ID>
  - Date From = Date To = (empty) in the first search, <Date of Entry> in the second
  - Status filter = PENDING
- Expected:
  1. System should show "No data available in table" for the first search (before approval).
  2. System should show a toast starting "Asset Expense approved successfully." after Approve.
  3. System should list one voucher row for <Expense ID> in the second search (after approval) with 'Status' = "Approved".
- Basis: DERIVED (not yet run)
- Check also: This pair of searches on one expense (before and after Approve) proves that approval is the trigger for the voucher.

**EXP-B03 — Verify the voucher is created by "Auto Voucher" with status Approved**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same login can open the Accounting module.
  2. An APPROVED expense exists with Expense ID <Expense ID> and Date of Entry <Date of Entry>.
- Steps:
  1. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  2. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>.
  3. Click the calendar icon beside 'Date To' and click the day number of <Date of Entry>.
  4. In the field 'Transaction Number' type <Expense ID> in full.
  5. Click the button 'Search' and wait for the row.
  6. Read the cell under the column 'Status' of the row.
  7. Click the link 'Preview' in the row. A PDF opens in a new browser tab.
  8. Read 'Approved By' in the footer of the PDF.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = Date To = <Date of Entry>
  - Transaction Number = <Expense ID>
- Expected:
  1. System should show 'Status' = "Approved" in the search row.
  2. System should show 'Approved By' = "Auto Voucher" on the voucher (no human approval of the voucher is needed).
- Basis: VERIFIED (test_16 full flows)

**EXP-B04 — Verify the Credit account differs between Inventory and Accounts sources**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The same login can open the Accounting module.
  2. One APPROVED Inventory expense of 5000 (Expense ID <Expense ID Inventory>) and one APPROVED Accounts expense of 5000 (Expense ID <Expense ID Accounts>) exist. Both have Date of Entry <Date of Entry>.
- Steps:
  1. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  2. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>; click the calendar icon beside 'Date To' and click the same day number.
  3. In the field 'Transaction Number' type <Expense ID Inventory> and click the button 'Search'.
  4. Click the link 'Preview' in the row. A PDF opens in a new tab. Read the Debit line and the Credit line. Close the tab.
  5. In the field 'Transaction Number' replace the text with <Expense ID Accounts> and click the button 'Search'.
  6. Click the link 'Preview' in the row. A PDF opens in a new tab. Read the Debit line and the Credit line.
  7. Compare the two vouchers.
- Test data:
  - <ERP Username> / <ERP Password>
  - Date From = Date To = <Date of Entry>
  - Transaction Number = <Expense ID Inventory>, then <Expense ID Accounts>
  - Amount = 5000 each
- Expected:
  1. System should show the same debit line in both vouchers: 5108010101-07 Other Maintenance Expenses 5,000.00.
  2. System should show the credit line "1107010401-02 Other Inventory" 5,000.00 on the Inventory voucher.
  3. System should show the credit line "2101010301-05 Supplier Payable-Opex" 5,000.00 on the Accounts voucher.
  4. System should show Total Debit = Total Credit = 5,000.00 on both.
- Basis: VERIFIED (test_16 full flows)

**EXP-B05 — Verify the expense does not change the asset**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED Furniture asset 'Cabinet Table' (Asset Serial <Asset Serial>) exists with no Draft or Pending expense. Its status, assignment and value are written down before the test (<Status before>, <Assignment before>, <Value before>).
  4. The vendor 'ACE IT[P008937]' is available.
- Steps:
  1. Open the asset lists of the Fixed Asset module (screen and column names to be confirmed), find <Asset Serial> and note its status, assignment and value.
  2. Click the tab 'Asset Expenditure', then the link 'Asset Expense', then the link 'Create'.
  3. In the field 'Asset Serial' type <Asset Serial> and click the suggestion that appears.
  4. In 'Expense Amount' type 5000 and click the button 'Add'.
  5. In 'Expense Source' choose 'Accounts'.
  6. In 'Debit A/C' choose 'Other Maintenance Expenses[5108010101-07]'.
  7. Click the link '-Select Party-', type ACE IT and click the option 'ACE IT[P008937]'.
  8. In 'Expense Ref.' type <Expense Ref.> and in 'Remarks/Note' type AUTOMATION_TEST expense Accounts.
  9. Click the button 'Submit' and wait for the toast.
  10. Click the link 'Asset Expense Approval' in the menu 'Asset Expenditure'.
  11. In 'Status' choose 'PENDING', click 'Search', click the link in the column 'Expense ID' of the new row and click the button 'Approve'. Wait for the toast.
  12. Open the asset list again, find <Asset Serial> and read its status, assignment and value.
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Expense Amount = 5000
  - Expense Source = Accounts
  - Debit A/C = Other Maintenance Expenses[5108010101-07]
  - Vendor/Supplier/Lessor Name = ACE IT[P008937]
  - Expense Ref. = <Expense Ref.>
  - Remarks/Note = AUTOMATION_TEST expense Accounts
- Expected:
  1. System should show the toasts "Asset expense successfully submitted." and then one starting "Asset Expense approved successfully."
  2. System should leave the asset unchanged: status, assignment and value equal <Status before>, <Assignment before> and <Value before>.
- Basis: VERIFIED (test_16 states this; value check is DERIVED)

**EXP-B06 — Verify the Accounts source needs a later manual payment journal**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. The Accounting module can be opened.
  2. An APPROVED Accounts expense of 5000 exists with Expense ID <Expense ID>.
- Steps:
  1. Click the tab 'Accounting' in the top bar.
  2. Open the manual journal screen (menu and link to be confirmed with the BA).
  3. Create a journal with Debit "Supplier Payable-Opex" 5000 and Credit "Cash-Bank" 5000 (field labels to be confirmed).
  4. Save and post the journal (button labels to be confirmed).
  5. Read the message and the journal result.
- Test data:
  - <ERP Username> / <ERP Password>
  - Debit account = Supplier Payable-Opex
  - Credit account = Cash-Bank
  - Amount = 5000
- Expected:
  1. System should accept the payment journal and clear the payable. Not yet exercised; confirm the exact screen and steps with the BA.
- Basis: DERIVED (not yet run)

**EXP-B07 — Verify the Approval list bulk Approve (checkbox)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two PENDING expenses exist for two different 'Cabinet Table' assets, each 5000. Their Expense IDs are known (<Expense ID 1>, <Expense ID 2>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense Approval'.
  2. In 'Status' choose 'PENDING', then click the button 'Search'.
  3. In the grid tick the checkbox at the start of the row <Expense ID 1>.
  4. Tick the checkbox at the start of the row <Expense ID 2>.
  5. Click the button 'Approve' under the grid.
  6. Wait for the toast message to appear and read it.
  7. In 'Status' choose 'APPROVED', click 'Search' and read the 'Status' of both rows.
  8. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then the link 'Voucher Search'.
  9. Click the calendar icon beside 'Date From' and click the day number of <Date of Entry>; click the calendar icon beside 'Date To' and click the same day number.
  10. In 'Transaction Number' type <Expense ID 1>, click 'Search' and read the grid.
  11. In 'Transaction Number' type <Expense ID 2>, click 'Search' and read the grid.
- Test data:
  - <ERP Username> / <ERP Password>
  - Status filter = PENDING, then APPROVED
  - Transaction Number = <Expense ID 1>, then <Expense ID 2>
- Expected:
  1. System should approve both expenses and show them with 'Status' = APPROVED (exact message to be confirmed).
  2. System should create one voucher for each expense: one row per Expense ID in Voucher Search.
- Basis: DERIVED (not yet run). The checkbox column and bulk Approve button exist but were never clicked.

**EXP-B08 — Verify Distribute splits one total across several assets**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two APPROVED Furniture assets 'Cabinet Table' exist with no Draft or Pending expense (<Asset Serial 1>, <Asset Serial 2>).
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense'.
  2. Click the link 'Create'. The popup 'Create Asset Expense' opens.
  3. In the field 'Asset Serial' type <Asset Serial 1>, click the suggestion, then click the button 'Add' (leave 'Expense Amount' empty if the screen allows it; otherwise type 1).
  4. In the field 'Asset Serial' type <Asset Serial 2>, click the suggestion, then click the button 'Add' (same rule).
  5. In the field 'Total Expense Amount' type 5000 (if the field is read-only after Add, this step cannot be done and must be confirmed with the BA).
  6. Click the button 'Distribute'.
  7. In the asset grid read the 'Expense Amount' of each row.
  8. Click the button 'Close' (nothing is saved).
- Test data:
  - <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial 1> and <Asset Serial 2>
  - Total Expense Amount = 5000
- Expected:
  1. System should split the total evenly: 2,500 for each of the two assets.
  2. Odd totals (for example 5000 over 3 assets) are untested.
- Basis: DERIVED (not yet run)

**EXP-B09 — Verify Reject and Sendback outcomes (open question)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two PENDING expenses exist (<Expense ID 1> for the Reject check and <Expense ID 2> for the Sendback check), each 5000.
- Steps:
  1. Click the tab 'Asset Expenditure' in the Fixed Asset module, then click the link 'Asset Expense Approval'.
  2. In 'Status' choose 'PENDING', then click the button 'Search'.
  3. Click the link in the column 'Expense ID' of the row <Expense ID 1>. The popup opens.
  4. Click the button 'Reject'. Read any message.
  5. In 'Status' choose 'REJECTED', click 'Search' and read the 'Status' of <Expense ID 1>. Open the Asset Expense list and read the 'Status' of <Expense ID 1> there.
  6. In the Approval list, in 'Status' choose 'PENDING', click 'Search', click the link in the column 'Expense ID' of the row <Expense ID 2>.
  7. Click the button 'Sendback'. Read any message.
  8. In 'Status' choose 'SENDBACK', click 'Search' and read the 'Status' of <Expense ID 2>. Open the Asset Expense list and read the 'Status' of <Expense ID 2> there.
  9. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then the link 'Voucher Search'.
  10. Leave the dates empty. In 'Transaction Number' type <Expense ID 1>, click 'Search' and read the grid. Repeat with <Expense ID 2>.
- Test data:
  - <ERP Username> / <ERP Password>
  - Status filter = PENDING, REJECTED, SENDBACK
  - Transaction Number = <Expense ID 1>, <Expense ID 2>
- Expected:
  1. Unknown. Expected statuses REJECTED / SENDBACK are listed in the Status filter, and no voucher should exist ("No data available in table"). Do not write expected messages until the BA confirms.
- Basis: DERIVED (not yet run)

**5. When a CR changes something here — what to re-check**
- A field is added or changed in the Create popup (Expense Source, Debit/Credit A/C, vendor, Expense Ref., Remarks): re-run EXP-P01 to P08, EXP-N01 to N08, EXP-E01, E06.
- Credit or Debit account mapping changes: EXP-P03, P04, P12, P13, B04.
- Vendor rule changes (for example optional for one source): EXP-N01 to N03.
- Status or approval rule changes (new status, second approver, bulk approve): EXP-P09, P10, P15, N10, B01, B02, B07, B09.
- Voucher layout, branch/project or "Auto Voucher" changes: EXP-P11, P12, P13, B03 and the generic voucher checklist.
- Toast text changes ("drafted", "submitted", "approved successfully", vendor message): EXP-P05, P06, P07, P10, N01 to N03.
- List filters or columns change: EXP-P14, P15.
- Expense ID format change: EXP-P05, P11, E03, N09.

**6. Questions to ask the BA**
- What happens on Reject and on Sendback (statuses, messages, can the creator edit and resubmit)?
- Does a Draft or Pending expense create any voucher? (assumed no)
- Is the Distribute button behaviour even splitting with rounding on odd totals?
- What are the required-field messages for serial, source, Debit A/C, Expense Ref. and amount?
- Should the creator and the approver be different users? (tests used the same user)
- Does bulk checkbox Approve create one voucher per expense?
- For the Accounts source, who posts the manual payment journal and where is it checked?
- Is the lock of an asset with a Draft/Pending expense intended, and what message does the user see?
- What are the limits on Expense Amount (zero, negative, decimals, maximum)?

---

### Asset Transfer (Shipment) and Single Challan

**1. What this area is, in plain words**

This area moves approved fixed assets out of one project and into another project of the organisation. There are two ways to do it.
- Asset Transfer (Shipment): the head office creates a Shipment (courier and driver details). Under it, one or more Transfer Challans are created, each listing the items. Serial numbers of real assets are attached. Each challan is approved, then the whole shipment is approved. After that the receiving side acknowledges the challan, and a Gate Pass can be printed.
- Single Challan: one challan on its own, with no shipment around it. Create (Draft or Submit), add the serial, approve, acknowledge, print Gate Pass.
- Business outcome: the asset is documented as leaving the sending project and arriving in the receiving project, with a gate pass for the physical movement.
- Before this: the asset must be registered and approved. After this: the acknowledged asset is in its new project and can be assigned, expensed or disposed. Accounting vouchers for Out Challan and In Challan are expected by the business but are NOT verified (see section 6).

**2. Before you test: getting the right starting state**

| State needed | Why | How to get it in short human steps |
|---|---|---|
| An APPROVED, UNASSIGNED furniture asset in the sending project | The Add Serial box lists only approved, unassigned assets that fit the chosen item | Register furniture (Registration > Asset Registration by AAQ), Submit, approve it in Asset Registration Approval List, note the Asset Serial. Use a fresh asset for each chain, because once its serial is in a challan it cannot be used again |
| A new PENDING shipment with no challan | To test "no challan" refusal | Fixed Asset > Asset Transfer > Asset Shipment > Create, fill courier fields, Save. Note the Shipment No |
| A shipment with one DRAFT challan (All Serial Added = No) | To test serial add, delete, draft-challan refusal | Open the shipment (click Shipment No), Transfer Challans tab > Create, fill the form (see test data), Add, Draft. Note the Out Challan No |
| A challan DRAFT with serial added (All Serial Added = Yes) | Required before Submit in the shipment chain | Open challan details, click Add Serial, choose the serial, Add, Save |
| A challan PENDING | To approve it | Transfer Challans > Edit on the draft challan > Submit |
| A challan APPROVED and a shipment still PENDING | To test shipment approval and "In-Challan appears only after shipment approval" | Approve the challan in Asset Shipment Challan Approval List |
| A challan ACKNOWLEDGED | For Gate Pass | Approve the shipment, then acknowledge in Asset Shipment In-Challan |
| Single challan PENDING or DRAFT | For single challan approval and Draft paths | Fixed Asset > Single Challan > Asset Single Out Challan > Create, fill form, Submit (or Draft) |
| Login | Every step in the verified runs was done by one user | Log in with `<ERP Username> / <ERP Password>`. Acknowledging by a user of the receiving branch is not verified (see section 6) |

Standard challan test data: From Project "[015] Microfinance (Dabi)"; Receiving Branch "Head Office" (type "Head", pick "[HO - BDHO] Head Office"); To Project "[060] Progoti" (type "Progoti"); Asset Item "Cabinet Table" (type "Cabinet"); Quantity 1; Note "AUTOMATION_TEST challan note".

**3. Rules and what to test for each**

| Rule (plain words) | Where it applies | Pass example | Fail / boundary examples to test |
|---|---|---|---|
| A new shipment shows Shipment No AUTO, From Branch Head Office (BDHO), Shipment Date today | Create Shipment popup | Open Create: AUTO, BDHO, today's date | Shipment Date or From Branch should not be editable |
| A saved shipment starts PENDING with no Preview link | Asset Shipment list | After Save, newest row PENDING | There is no Draft state for a shipment |
| A shipment cannot be approved with no challan | Shipment Details > Details tab | Toast "Please add at least one challan" | Approve on a shipment with a challan: see next rule |
| A shipment cannot be approved while its challans are only DRAFT | Shipment Details | Toast "Approve at least one challan" | PENDING (submitted but unapproved) challan: message to be confirmed |
| From Project is required to add a line | Create Challan popup | Toast "Please select from project" | Fill To Project only |
| To Project is required to add a line | Create Challan popup | Toast "Please select to project" | Fill From Project only |
| A Draft challan needs at least one line | Create Challan popup | Toast "No Items in Challan to perform operation" | Add then Remove the only line, then Draft |
| To Project must be mapped to an area code | Draft challan | "[060] Progoti" works | "[C04] Administratiion" gives "Area code not found" |
| A DRAFT challan is deletable; Update popup locks branch/project/date | Update Challan popup | Delete gives "Challan deleted successfuly" | Delete a PENDING challan: Delete availability to be confirmed |
| Serial is added on the challan details, then All Serial Added turns Yes | Challan Details | After Save, "Asset serial added Successfuly" | Save with no serial row (derived) |
| Shipment challan needs approval before shipment approval | Challan Approval List | Challan APPROVED, then shipment approved | Approve shipment with PENDING challan |
| Shipment approval also generates the gate pass | Shipment Details | Two-line toast | See scenarios TRF-P20, TRF-B03 |
| In-Challan lists the challan only after the SHIPMENT is approved | Shipment In-Challan | Not listed before, listed after | Challan approved but shipment not approved: must not appear |
| Acknowledge turns APPROVED to ACKNOWLEDGED, adds Preview | In-Challan screens | Status ACKNOWLEDGED | Acknowledge twice (derived) |
| Gate Pass lists ACKNOWLEDGED challans | Gate Pass Generation | Row ACKNOWLEDGED | Challan not acknowledged: should not be listed (derived) |
| Single challan Submit needs no serial first; serial is added after PENDING | Asset Single Out Challan | Submit then add serial | Approve without a serial (derived) |
| Single challan Draft/Submit give no toast; popup closes | Single Out popup | Status changes in the list | Do not expect a toast |
| Single challan approval generates a gate pass | Single Out Challan Approval List | Two-line toast | Preview present on row |
| Month-end rule: no shipment in last 3 days of month | Create Shipment | Not verified | See SCH/TRF derived scenario TRF-B05 |
| Same Receiving and Sending Branch needs different From and To Projects | Create Challan | Not verified | See TRF-B06 |

**4. Scenario catalogue**

#### Positive

**TRF-P01 — Verify the Asset Shipment list shows the expected columns and status filter**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. Wait for the page to load completely.
  3. In the grid, read the column headings from left to right (ignore the blank hidden column).
  4. Click the drop-down 'Shipment Status' in the filter area and read all its options.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Menu = Asset Transfer > Asset Shipment
- Expected:
  1. System should show the column headings SL, Shipment No, Edit, Shipment Date, Created By, Creation Date, Approved By, Approval Date, From Branch, Status, Preview.
  2. System should offer exactly these options in 'Shipment Status': -Select Shipment Status-, PENDING, APPROVED, REJECTED.
- Basis: VERIFIED (test_19)
- Check also: Read the 'Shipment Status' options again and confirm there is no option DRAFT and no option SENDBACK. Open the drop-down 'Records per page' (below the grid) and confirm it offers 10, 20, 30, 50, 100.

**TRF-P02 — Verify the Create Shipment popup opens with the right defaults**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. Wait for the page to load completely.
  3. Click the button 'Create'.
  4. Wait for the popup 'Create Shipment' to appear.
  5. Read the value of the field 'Shipment No'.
  6. Read the value of the field 'From Branch'.
  7. Read the value of the field 'Shipment Date' and compare it with today's date (format dd/mm/yyyy).
- Test data:
  - Login = <ERP Username> / <ERP Password>
- Expected:
  1. System should show the popup 'Create Shipment'.
  2. System should show 'Shipment No' = "AUTO".
  3. System should show 'From Branch' = "Head Office [ BDHO ]" (it contains BDHO).
  4. System should show 'Shipment Date' = today's date.
- Basis: VERIFIED (test_19)
- Check also: Try to type in 'Shipment No' and in 'Shipment Date'; System should not accept typing (both are read-only). Confirm 'From Branch' offers only "Head Office [ BDHO ]".

**TRF-P03 — Verify Reset clears typed courier details and Close shuts the popup**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. Wait for the page to load completely.
  3. Click the button 'Create' and wait for the popup 'Create Shipment'.
  4. In the field 'Courier Service Name / Transfer By' type "AUTOMATION_TEST courier".
  5. In the field 'Courier Number' type "AWB-AUTOTEST-1".
  6. In the field 'Driver Name' type "AUTOMATION_TEST driver".
  7. Click the button 'Reset'.
  8. Read the value of the field 'Courier Service Name / Transfer By'.
  9. Click the button 'Close'.
  10. Look at the page.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Courier Service Name / Transfer By = AUTOMATION_TEST courier
  - Courier Number = AWB-AUTOTEST-1
  - Driver Name = AUTOMATION_TEST driver
- Expected:
  1. After Reset, System should show the field 'Courier Service Name / Transfer By' empty.
  2. After Close, System should close the popup 'Create Shipment' and show the Asset Shipment list.
- Basis: VERIFIED (test_19)
- Check also: After Reset, read 'Courier Number' and 'Driver Name'; they should also be empty (the run only checked the courier name). Confirm 'Shipment No' still shows "AUTO" after Reset.

**TRF-P04 — Verify a shipment can be created with all courier fields filled**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. Wait for the page to load completely.
  3. Click the button 'Create' and wait for the popup 'Create Shipment'.
  4. In the field 'Courier Service Name / Transfer By' type "AUTOMATION_TEST courier <unique suffix>".
  5. In the field 'Courier Number' type "AWB-AUTOTEST-1".
  6. In the field 'Driver Name' type "AUTOMATION_TEST driver".
  7. In the field 'Transport No.' type "TR-AUTOTEST-1".
  8. In the field 'Courier Details' type "AUTOMATION_TEST courier details".
  9. In the field 'Note/Remarks' type "AUTOMATION_TEST shipment note".
  10. Click the button 'Save'.
  11. Wait for the toast message to appear and read it.
  12. Click the button 'Search' in the filter area of the list.
  13. In the grid, read the cells 'Shipment No', 'Status' and 'Preview' of the top row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Courier Service Name / Transfer By = AUTOMATION_TEST courier <unique suffix>
  - Courier Number = AWB-AUTOTEST-1
  - Driver Name = AUTOMATION_TEST driver
  - Transport No. = TR-AUTOTEST-1
  - Courier Details = AUTOMATION_TEST courier details
  - Note/Remarks = AUTOMATION_TEST shipment note
  - Read during the run: <Shipment No>
- Expected:
  1. System should show the toast message "Asset Shipment Initiated Successfuly" (spelled so).
  2. System should close the popup 'Create Shipment'.
  3. System should show a new top row with a new 'Shipment No' (written below as <Shipment No>).
  4. System should show 'Status' = "PENDING" in that row.
  5. System should show no link in the column 'Preview' of that row.
- Basis: VERIFIED (test_19)
- Check also: Note the <Shipment No>. Click 'Edit' on the row and confirm the popup 'Update Shipment' shows the six typed values, then click 'Close'.

**TRF-P05 — Verify Edit and Details show the saved shipment values**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and these saved values: Courier Service Name / Transfer By "AUTOMATION_TEST courier <unique suffix>", Courier Number "AWB-AUTOTEST-1", Driver Name "AUTOMATION_TEST driver", Transport No. "TR-AUTOTEST-1", Courier Details "AUTOMATION_TEST courier details", Note/Remarks "AUTOMATION_TEST shipment note".
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>.
  3. Click the button 'Search'.
  4. In the grid, click the link 'Edit' in the row of <Shipment No>.
  5. Wait for the popup 'Update Shipment' and read all its fields.
  6. Click the button 'Close'.
  7. In the grid, click the link <Shipment No> in the column 'Shipment No'.
  8. Wait for the popup 'Shipment Details' and read the tab names, the 'Status' and the courier fields.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Saved values as listed in the precondition
- Expected:
  1. System should show the popup 'Update Shipment' with the six saved values in their fields.
  2. System should show 'Shipment No' = <Shipment No> as read-only in that popup.
  3. System should show the popup 'Shipment Details' with the tabs 'Details', 'Transfer Challans', 'Add Serial'.
  4. System should show Status "PENDING" in 'Shipment Details'.
  5. System should show the six saved values in 'Shipment Details'.
- Basis: VERIFIED (test_19)
- Check also: In 'Update Shipment' confirm the buttons 'Update', 'Delete' and 'Close' are shown. In 'Shipment Details' confirm the buttons 'Approve' and 'Reject' are shown on the 'Details' tab.

**TRF-P06 — Verify the Create Challan popup defaults**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No> in the column 'Shipment No'.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. Click the button 'Create'.
  6. Wait for the popup 'Create Challan'.
  7. Read the value of the field 'Out Challan No'.
  8. Read the value of the field 'Sending Branch'.
  9. Read the value of the field 'Out Challan Date'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
- Expected:
  1. System should show the popup 'Create Challan'.
  2. System should show 'Out Challan No' = "AUTO".
  3. System should show 'Sending Branch' containing "BDHO" (Head Office [BDHO]).
- Basis: VERIFIED (test_19)
- Check also: Confirm 'Out Challan Date' is already filled and read-only (it shows the business date, which may differ from today). Confirm the field 'From Department' is disabled until a 'From Project' is chosen.

**TRF-P07 — Verify choosing an asset item fills its classification**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and its popup 'Create Challan' (Shipment Details > tab 'Transfer Challans' > button 'Create') can be opened.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'Asset Item Name'.
  6. In its search field type "Cabinet".
  7. Click the result "Cabinet Table".
  8. Read the fields 'Asset Category', 'Asset Sub Category' (shown as 'Sub Category'), 'Group' and 'Measurement Unit'.
  9. Try to type in 'Asset Category'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Asset Item Name = Cabinet Table (search text "Cabinet")
- Expected:
  1. System should show 'Asset Category' = "Furniture".
  2. System should show 'Sub Category' = "Wooden Furniture".
  3. System should show 'Measurement Unit' = "Pcs".
  4. System should show 'Group' filled in (value to be confirmed).
  5. System should not accept typing in these four fields (read-only).
- Basis: VERIFIED (test_19)
- Check also: Click the button 'Reset' and confirm the four classification fields and 'Asset Item Name' are cleared.

**TRF-P08 — Verify a line can be added and removed in the challan item grid**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Progoti", click the result "[060] Progoti".
  8. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  9. In the field 'Quantity' type 1.
  10. Click the button 'Add'.
  11. Read the item grid (columns Asset Item Name, Quantity).
  12. In the item grid click the link 'Remove' on the line.
  13. Read the item grid and the fields 'Asset Item Name' and 'Quantity'.
  14. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  15. In the field 'Quantity' type 1.
  16. Click the button 'Add'.
  17. Read the item grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office (search "Head")
  - To Project = [060] Progoti (search "Progoti")
  - Asset Item Name = Cabinet Table (search "Cabinet")
  - Quantity = 1
- Expected:
  1. After the first Add, System should show one line in the item grid: Asset Item Name "Cabinet Table", Quantity 1.
  2. After Remove, System should show an empty item grid.
  3. After Remove, System should clear 'Asset Item Name' and 'Quantity'.
  4. After the second Add, System should show one line again: "Cabinet Table", Quantity 1.
- Basis: VERIFIED (test_19)
- Check also: Read the other item grid columns of the line (Asset Sub Category "Wooden Furniture", Asset Category "Furniture", Measurement Unit "Pcs") and confirm they are filled.

**TRF-P09 — Verify a challan can be saved as Draft**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and no challan.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Progoti", click the result "[060] Progoti".
  8. In the field 'Note' type "AUTOMATION_TEST challan note".
  9. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  10. In the field 'Quantity' type 1.
  11. Click the button 'Add'.
  12. Click the button 'Draft'.
  13. Wait for the toast message to appear and read it.
  14. In the list on the tab 'Transfer Challans', read the cells 'Out Challan No.', 'Status' and 'All Serial Added' of the newest row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [060] Progoti
  - Note = AUTOMATION_TEST challan note
  - Asset Item Name = Cabinet Table
  - Quantity = 1
  - Read during the run: <Out Challan No>
- Expected:
  1. System should show the toast message "Challan drafted successfully".
  2. System should close the popup 'Create Challan'.
  3. System should show a new challan row with a generated 'Out Challan No.' (written below as <Out Challan No>).
  4. System should show 'Status' = "DRAFT" in that row.
  5. System should show 'All Serial Added' = "No" in that row.
- Basis: VERIFIED (test_19)
- Check also: In that row confirm the 'Edit' link is present and the column 'Preview' is empty.

**TRF-P10 — Verify the Challan Details popup shows projects and DRAFT status**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with one challan <Out Challan No> with Status DRAFT, From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. In the list click the link <Out Challan No> in the column 'Out Challan No.'.
  6. Wait for the popup 'Challan Details'.
  7. Read the fields 'From Project', 'To Project' and 'Status'.
  8. Read the names of the tabs of the popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
- Expected:
  1. System should show 'From Project' = "[015] Microfinance (Dabi)".
  2. System should show 'To Project' = "[060] Progoti".
  3. System should show 'Status' = "DRAFT".
  4. System should show the tabs "Details", "Asset Serials", "Posted Accounts".
- Basis: VERIFIED (test_19)
- Check also: Click the tab 'Posted Accounts' and confirm it is empty for a DRAFT challan. Click the tab 'Asset Serials' and confirm no serial is listed.

**TRF-P11 — Verify a serial can be added to a draft challan**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists in project "[015] Microfinance (Dabi)" and its Asset Serial is known (written below as <Asset Serial>).
  4. A shipment <Shipment No> exists with one challan <Out Challan No> with Status DRAFT and All Serial Added = No.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. In the list click the link <Out Challan No>.
  6. In the popup 'Challan Details' stay on the tab 'Details' and click the link 'Add Serial' in the item row.
  7. Wait for the popup 'Add Asset Serial'.
  8. Click the box 'Serial No', type <Asset Serial>, click the result that contains <Asset Serial>.
  9. Read the fields 'Item Name', 'Category', 'Sub-Category' and 'Quantity' of the popup.
  10. Click the button 'Add'.
  11. Read the grid inside the popup.
  12. Click the button 'Save'.
  13. Wait for the toast message to appear and read it.
  14. In 'Challan Details' click the tab 'Asset Serials' and read the serials listed.
  15. Click the button 'Close' of 'Challan Details'.
  16. In 'Shipment Details' click the tab 'Add Serial' and read the serials listed.
  17. Click the tab 'Transfer Challans' and read the cell 'All Serial Added' of the row <Out Challan No>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
  - Serial No = <Asset Serial>
- Expected:
  1. After choosing the serial, System should show 'Item Name' = "Cabinet Table" and 'Category' = "Furniture", and fill 'Sub-Category' and 'Quantity'.
  2. After Add, System should show one serial row in the popup grid and no toast message.
  3. After Save, System should show the toast message "Asset serial added Successfuly" (spelled so).
  4. System should list <Asset Serial> on the tab 'Asset Serials' of 'Challan Details'.
  5. System should list <Asset Serial> on the tab 'Add Serial' of 'Shipment Details'.
  6. System should show 'All Serial Added' = "Yes" in the challan row.
- Basis: VERIFIED (test_19)
- Check also: In the popup 'Add Asset Serial' confirm the checkboxes 'Disposal' and 'Tranfer to maintenance' (spelled so) are shown and unchecked; do not tick them. Confirm the challan 'Status' is still "DRAFT".

**TRF-P12 — Verify the Update Challan popup locks branch, project and date**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with one challan <Out Challan No> with Status DRAFT.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. In the row <Out Challan No> click the link 'Edit'.
  6. Wait for the popup 'Update Challan'.
  7. Try to change the fields 'Sending Branch', 'Receiving Branch', 'From Project', 'To Project' and 'Out Challan Date' one by one.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
- Expected:
  1. System should show 'Sending Branch' as read-only.
  2. System should show 'Receiving Branch' as read-only.
  3. System should show 'From Project' as read-only.
  4. System should show 'To Project' as read-only.
  5. System should show 'Out Challan Date' as read-only.
- Basis: VERIFIED (test_19)
- Check also: Confirm the popup shows the buttons 'Add', 'Update', 'Submit', 'Delete' and 'Close'. Click 'Close' and confirm the challan is still DRAFT.

**TRF-P13 — Verify a DRAFT challan can be deleted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No 1> with Status DRAFT (this one stays).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Progoti", click the result "[060] Progoti".
  8. In the field 'Note' type "AUTOMATION_TEST challan note".
  9. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  10. In the field 'Quantity' type 1.
  11. Click the button 'Add', then click the button 'Draft'.
  12. In the list read the new second row and note its 'Out Challan No.' (written below as <Out Challan No 2>).
  13. In the row <Out Challan No 2> click the link 'Edit'.
  14. Wait for the popup 'Update Challan'.
  15. Click the button 'Delete'.
  16. Wait for the toast message to appear and read it; look for any confirmation box.
  17. Read the list on the tab 'Transfer Challans'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [060] Progoti
  - Note = AUTOMATION_TEST challan note
  - Asset Item Name = Cabinet Table
  - Quantity = 1
  - Read during the run: <Out Challan No 2>
- Expected:
  1. System should show the toast message "Challan deleted successfuly" (spelled so).
  2. System should show no confirmation box before deleting.
  3. System should not list <Out Challan No 2> any more.
  4. System should still list <Out Challan No 1> with Status "DRAFT".
- Basis: VERIFIED (test_19)

**TRF-P14 — Verify a draft challan with serial can be submitted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No> with Status DRAFT, All Serial Added = Yes (serial <Asset Serial> of an approved Furniture asset 'Cabinet Table' is saved on it).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. In the row <Out Challan No> click the link 'Edit'.
  6. Wait for the popup 'Update Challan'.
  7. Click the button 'Submit'.
  8. Wait for the toast message to appear and read it.
  9. In the list read the cell 'Status' of the row <Out Challan No>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should show the toast message "Challan submitted successfully".
  2. System should close the popup 'Update Challan'.
  3. System should show 'Status' = "PENDING" in the row of <Out Challan No>.
- Basis: VERIFIED (test_19)
- Check also: In the same row confirm the link 'Edit' is no longer offered for a PENDING challan (to be confirmed on screen).

**TRF-P15 — Verify a PENDING challan appears in the Challan Approval List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No> with Status PENDING, To Project "[060] Progoti".
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment Challan Approval List'.
  2. Wait for the page to load completely.
  3. In the filter field 'Out Challan No' type <Out Challan No>.
  4. Click the button 'Search'.
  5. In the grid, read the cells 'Challan Status', 'Shipment Number' and 'To Project' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan No (filter) = <Out Challan No>
  - Shipment No = <Shipment No>
- Expected:
  1. System should list one row for <Out Challan No>.
  2. System should show 'Challan Status' = "PENDING".
  3. System should show 'Shipment Number' = <Shipment No>.
  4. System should show 'To Project' = "[060] Progoti".
- Basis: VERIFIED (test_20)
- Check also: Confirm the cell 'Preview' of the row is empty (no link while PENDING). Open the filter 'Approval Status' and confirm it offers PENDING, APPROVED, REJECTED, ACKNOWLEDGED, SENDBACK.

**TRF-P16 — Verify a challan can be approved with a comment**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No> with Status PENDING, with serial <Asset Serial> saved on it.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment Challan Approval List'.
  2. In the filter field 'Out Challan No' type <Out Challan No>, then click the button 'Search'.
  3. In the grid, click the link <Out Challan No> in the column 'Out Challan No.'.
  4. Wait for the challan popup and read which action buttons are shown.
  5. In the item row of the popup click the link 'Show Serial'.
  6. Wait for the loading overlay to go away; read the list in the popup 'Show Asset Serial'.
  7. Click the button 'Close' of the popup 'Show Asset Serial'.
  8. Click the comment box (placeholder 'Leave comment here...') and type "AUTOMATION_TEST approve challan".
  9. Click the button 'Approve'.
  10. Wait for the toast message to appear and read it.
  11. In the filter field 'Out Challan No' type <Out Challan No> again, then click the button 'Search'.
  12. In the grid, read the cells 'Challan Status' and 'Preview' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan No (filter) = <Out Challan No>
  - Comment = AUTOMATION_TEST approve challan
  - Asset Serial = <Asset Serial>
- Expected:
  1. System should offer the buttons 'Approve', 'Reject', 'Sendback' (and 'Close').
  2. System should list <Asset Serial> in the popup 'Show Asset Serial'.
  3. System should show the toast message "Challan approved successfully."
  4. System should close the challan popup.
  5. System should show 'Challan Status' = "APPROVED" in the row.
  6. System should show a link in the column 'Preview' of the row.
- Basis: VERIFIED (test_20)
- Check also: Read the cells 'Approval By' and 'Approval Date' of the row; both should be filled.

**TRF-P17 — Verify shipment approval gives a two-line toast and gate pass**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No> with Status APPROVED (serial <Asset Serial> saved).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' stay on the tab 'Details'.
  5. Click the button 'Approve'.
  6. Wait for the toast message to appear and read all its lines.
  7. In the filter field 'Shipment No' type <Shipment No> again, then click the button 'Search'.
  8. In the grid, read the cells 'Status', 'Approved By', 'Approval Date' and 'Preview' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
- Expected:
  1. System should show one toast message with two lines: "Shipment approved successfully" and "Gate pass generated successfully".
  2. System should show 'Status' = "APPROVED" in the shipment row.
  3. System should fill 'Approved By' and 'Approval Date' in the row.
  4. System should show a link in the column 'Preview' of the row.
- Basis: VERIFIED (test_20)
- Check also: Open Shipment Details again and confirm 'Status' = "APPROVED"; the tab 'Transfer Challans' should list <Out Challan No> with an 'In Challan No' filled.

**TRF-P18 — Verify the challan shows in Shipment In-Challan after shipment approval**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> has Status APPROVED and contains one challan <Out Challan No> (Status APPROVED, not yet acknowledged).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment In-Challan'.
  2. Wait for the page to load completely.
  3. In the filter field 'Out Challan No' type <Out Challan No>.
  4. Click the button 'Search'.
  5. In the grid, read the cells 'Challan Status', 'In Challan No' and 'Preview' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan No (filter) = <Out Challan No>
- Expected:
  1. System should list one row for <Out Challan No>.
  2. System should show 'Challan Status' = "APPROVED".
  3. System should show 'In Challan No' filled (format like IC-...).
  4. System should show no link in the column 'Preview'.
- Basis: VERIFIED (test_21)
- Check also: Confirm the cells 'In Challan Date' and 'Acknowledged By' are empty.

**TRF-P19 — Verify Acknowledge changes the challan to ACKNOWLEDGED**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A challan <Out Challan No> is listed in Asset Shipment In-Challan with 'Challan Status' APPROVED (its shipment is APPROVED).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment In-Challan'.
  2. In the filter field 'Out Challan No' type <Out Challan No>, then click the button 'Search'.
  3. In the grid, click the link <Out Challan No> in the column 'Out Challan No.'.
  4. Wait for the challan popup and read which action buttons are shown.
  5. Click the button 'Acknowledge'.
  6. Wait for the loading overlay to go away; if the popup is still open click the button 'Close'.
  7. In the filter field 'Out Challan No' type <Out Challan No> again, then click the button 'Search'.
  8. In the grid, read the cells 'Challan Status', 'In Challan Date', 'Acknowledged By' and 'Preview' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan No (filter) = <Out Challan No>
- Expected:
  1. System should offer only the action 'Acknowledge' (and 'Close') in the popup.
  2. System should show 'Challan Status' = "ACKNOWLEDGED" in the row.
  3. System should fill 'In Challan Date' and 'Acknowledged By' in the row.
  4. System should show a link in the column 'Preview' of the row.
  5. The success toast was not captured in the run, so do not expect a fixed text; if a toast appears, record its exact text (to be confirmed).
- Basis: VERIFIED (test_21)

**TRF-P20 — Verify an acknowledged challan appears in Gate Pass Generation and Preview opens a PDF**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A challan <Out Challan No> from project "[015] Microfinance (Dabi)" to project "[060] Progoti" has 'Challan Status' ACKNOWLEDGED.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Gate Pass Generation'.
  2. Wait for the page to load completely.
  3. In the filter field 'Out Challan No' type <Out Challan No>.
  4. Click the button 'Search'.
  5. In the grid, read the cells 'Out Challan Number', 'In Challan Number' and 'Status' of the row.
  6. In the row click the link in the column 'Preview'.
  7. Wait for a new browser tab to open and look at it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan No (filter) = <Out Challan No>
- Expected:
  1. System should list one row for <Out Challan No> with 'Status' = "ACKNOWLEDGED" and 'In Challan Number' filled.
  2. System should open a new browser tab showing a PDF report that loads without error.
  3. The PDF contents were not read in the run (to be confirmed).
- Basis: VERIFIED (test_22) for the row; the Preview check exists but is switched off in the suite, so treat as OBSERVED (catalog).
- Check also: Read the gate pass PDF and compare items (Cabinet Table, Quantity 1), From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti" and the shipment with the challan.

**SCH-P01 — Verify a single challan can be created and submitted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset exists in project "[015] Microfinance (Dabi)" (so that a serial can be added later). It is not used in any other challan.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. Click the button 'Create'. Wait for the Create Challan popup to open.
  3. In the popup read the field 'Challan Number' and the field 'Sending Branch'.
  4. In 'From Project' choose '[015] Microfinance (Dabi)'.
  5. In 'Receiving Branch' type 'Head' and choose 'Head Office'.
  6. In 'To Project' type 'Progoti' and choose '[060] Progoti'.
  7. In 'Asset Item Name' type 'Cabinet' and choose 'Cabinet Table'.
  8. In the field 'Quantity' type 1.
  9. In the field 'Challan Note' type 'AUTOMATION_TEST challan note'.
  10. Click the button 'Add'. In the item grid read the new line.
  11. Click the button 'Submit'. Watch whether any toast message appears, and wait for the popup to close.
  12. Click the button 'Search'.
  13. In the grid read the cell under the column 'Out Challan Number' of the top row and note it as <Out Challan No.>.
  14. In the same top row read the cell under the column 'Status' and check whether the column 'Edit' has an 'Edit' link.
  15. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  16. Click the link <Out Challan No.> in the column 'Out Challan Number' to open the challan popup.
  17. In the popup read the fields 'From Project', 'To Project' and 'Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = Head Office (typed search text: Head)
  - To Project = [060] Progoti (typed search text: Progoti)
  - Asset Item Name = Cabinet Table (typed search text: Cabinet)
  - Quantity = 1
  - Challan Note = AUTOMATION_TEST challan note
  - Out Challan Number (read in step 13) = <Out Challan No.>
- Expected:
  1. System should show 'Challan Number' as "AUTO" in step 3.
  2. System should pre-fill 'Sending Branch' with "Head Office [ BDHO ]" in step 3.
  3. System should show one line in the item grid in step 10: Cabinet Table, Quantity 1.
  4. After Submit, System should close the popup and show no toast message.
  5. The top row in the grid should have a new Out Challan Number, 'Status' "PENDING", and no 'Edit' link.
  6. The challan popup should show 'From Project' "[015] Microfinance (Dabi)", 'To Project' "[060] Progoti", 'Status' "PENDING".
- Basis: VERIFIED (test_23)
- Check also: In the popup read the field 'Out Challan No' and check it equals <Out Challan No.>. Click the tab 'Asset Serials' and check the serial grid is empty, because no serial has been added yet.

**SCH-P02 — Verify a single challan Draft path: Draft, Edit, Submit**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset exists in project "[015] Microfinance (Dabi)". It is not used in any other challan.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. Click the button 'Create'. Wait for the Create Challan popup to open.
  3. In 'From Project' choose '[015] Microfinance (Dabi)'.
  4. In 'Receiving Branch' type 'Head' and choose 'Head Office'.
  5. In 'To Project' type 'Progoti' and choose '[060] Progoti'.
  6. In 'Asset Item Name' type 'Cabinet' and choose 'Cabinet Table'.
  7. In the field 'Quantity' type 1.
  8. In the field 'Challan Note' type 'AUTOMATION_TEST challan note'.
  9. Click the button 'Add'. In the item grid read the new line.
  10. Click the button 'Draft'. Watch whether any toast message appears, and wait for the popup to close.
  11. Click the button 'Search'.
  12. In the grid read the cell under the column 'Out Challan Number' of the top row and note it as <Out Challan No.>.
  13. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  14. In the row read the cell under the column 'Status' and check whether the column 'Edit' has an 'Edit' link.
  15. Click the link 'Edit' in that row. Wait for the Edit Challan popup to open and read its buttons.
  16. Click the button 'Submit'. Watch whether any toast message appears, and wait for the popup to close.
  17. Click the button 'Search' again (the filter still holds <Out Challan No.>).
  18. In the row read the cell under the column 'Status' and check whether the column 'Edit' has an 'Edit' link.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = Head Office (typed search text: Head)
  - To Project = [060] Progoti (typed search text: Progoti)
  - Asset Item Name = Cabinet Table (typed search text: Cabinet)
  - Quantity = 1
  - Challan Note = AUTOMATION_TEST challan note
  - Out Challan Number (read in step 12) = <Out Challan No.>
- Expected:
  1. After Draft, System should close the popup and show no toast message.
  2. After Draft, the row should show 'Status' "DRAFT" and an 'Edit' link.
  3. The Edit Challan popup should offer the buttons 'Update', 'Submit' and 'Delete'.
  4. After Submit, System should close the popup and show no toast message.
  5. After Submit, the row should show 'Status' "PENDING" and no 'Edit' link.
- Basis: VERIFIED (test_23)
- Check also: Open the challan by clicking <Out Challan No.> after Submit and read the field 'Status' in the popup; it should be "PENDING". Click the tab 'Asset Serials' and check the serial grid is empty.

**SCH-P03 — Verify a serial can be added to a PENDING single challan**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' PENDING exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1) and has no serial yet. Its number is known (written below as <Out Challan No.>). It was created either with Submit directly, or with Draft followed by Edit and Submit; the result is the same.
  4. An APPROVED, UNASSIGNED Furniture asset exists whose Asset Serial is known (written below as <Asset Serial>). It fits the item Cabinet Table and is not used in any other challan.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. Click the link <Out Challan No.> in the column 'Out Challan Number'. Wait for the challan popup to open.
  4. On the tab 'Details' click the link 'Add Serial' on the item row. Wait for the Add Asset Serial popup to open.
  5. In the box 'Serial No' type <Asset Serial> and choose it from the list.
  6. Click the button 'Add'. Read the serial grid of the popup.
  7. Click the button 'Save'. Wait for the toast message to appear and read it.
  8. Check whether the Add Asset Serial popup is still open.
  9. Click the button 'Close' of the challan popup.
  10. In the grid click the link <Out Challan No.> again to reopen the challan.
  11. Click the tab 'Asset Serials'. Read the column 'Asset Serial' of the serial grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
  - Serial No = <Asset Serial> (read from the asset before the test)
- Expected:
  1. After Add, System should show one serial row in the Add Asset Serial popup.
  2. After Save, System should show the toast "Asset serial added successfully" (note the lowercase "successfully", unlike the shipment message "Asset serial added Successfuly").
  3. System should close the Add Asset Serial popup.
  4. The tab 'Asset Serials' of the challan should list exactly one row with 'Asset Serial' equal to <Asset Serial>.
- Basis: VERIFIED (test_23)
- Check also: Repeat the same steps on a second PENDING challan of the other creation path (Submit directly versus Draft then Submit) with its own fresh asset; the result should be the same. After adding, click the tab 'Details' and check the 'Status' is still "PENDING".

**SCH-P04 — Verify a single challan is approved with a two-line toast and gate pass**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' PENDING exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1) and its serial has already been added. Its number is known (written below as <Out Challan No.>).
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan Approval List'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. In the grid read the cell under the column 'Status' of the row.
  4. Click the link <Out Challan No.> in the column 'Out Challan Number'. Wait for the challan popup to open.
  5. Read the names of the action buttons at the bottom of the popup.
  6. In the comment box of the popup type 'Approved by automation'.
  7. Click the button 'Approve'. Wait for the toast message to appear and read it.
  8. Click the button 'Search' again (the filter still holds <Out Challan No.>).
  9. In the grid read the cell under the column 'Status' of the row, and check whether the column 'Preview' has a 'Preview' link.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
  - Comment = Approved by automation
- Expected:
  1. Before approval, the row should show 'Status' "PENDING".
  2. The popup should offer the buttons 'Approve', 'Reject' and 'Sendback'.
  3. System should show one toast with two lines: "Challan approved successfully." and "Gate pass generated successfully".
  4. After approval, the row should show 'Status' "APPROVED" and a 'Preview' link.
  5. The row should show an In Challan Number in the column 'In Challan Number' and the column 'Approved By' should be filled.
- Basis: VERIFIED (test_24)
- Check also: Open the challan again from this list and check that the buttons 'Approve', 'Reject' and 'Sendback' are no longer all offered for an APPROVED challan (exact behaviour to be confirmed).

**SCH-P05 — Verify a single challan is acknowledged**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' APPROVED exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1, serial added). Its number is known (written below as <Out Challan No.>). It has not been acknowledged.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single In-Challan'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. In the grid read the cells under the columns 'Status' and 'In Challan Number', and check whether the column 'Preview' has a 'Preview' link.
  4. Click the link <Out Challan No.> in the column 'Out Challan Number'. Wait for the challan popup to open.
  5. Read the names of the action buttons at the bottom of the popup.
  6. Click the button 'Acknowledge'.
  7. Wait for the loading overlay to disappear. If the popup is still open, click the button 'Close'.
  8. In the filter 'Out Challan Number' type <Out Challan No.> again and click the button 'Search'.
  9. In the grid read the cell under the column 'Status', and check whether the column 'Preview' has a 'Preview' link.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
- Expected:
  1. Before Acknowledge, the row should show 'Status' "APPROVED", the column 'In Challan Number' filled, and no 'Preview' link.
  2. The popup should offer only the button 'Acknowledge'.
  3. After Acknowledge, the row should show 'Status' "ACKNOWLEDGED" and a 'Preview' link. The column 'Acknowledged By' should be filled.
  4. The success toast was not captured in the verified run, so check the status in the list (toast text to be confirmed).
- Basis: VERIFIED (test_25)
- Check also: Repeat with a second APPROVED challan that was created through Draft then Edit then Submit; the result should be the same.

**SCH-P06 — Verify the acknowledged single challan appears in Gate Pass Generation**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' ACKNOWLEDGED exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1). Its number is known (written below as <Out Challan No.>). A second ACKNOWLEDGED challan of the other creation path (Draft then Edit then Submit versus Submit directly) may be used for the second check.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Gate Pass Generation'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. In the grid read the cell under the column 'Status' of the row.
  4. Click the 'Preview' link in the last column of the row. Wait for a new browser tab to open.
  5. Look at the new tab and check what it shows.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
- Expected:
  1. The row should show 'Status' "ACKNOWLEDGED" (for both creation paths).
  2. The Preview should open a new tab that loads the gate pass as a PDF without error. The PDF contents were read once for one challan only.
- Basis: VERIFIED (test_26) for the row; Preview check switched off in the suite.
- Check also: Open the PDF and compare the challan number, the projects "[015] Microfinance (Dabi)" and "[060] Progoti", and the item Cabinet Table with the challan data. Check whether the list also shows challans in 'Status' APPROVED (the catalog says the list shows APPROVED and ACKNOWLEDGED rows).

#### Negative

**TRF-N01 — Verify shipment approval is refused when the shipment has no challan**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and no challan on its tab 'Transfer Challans'.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' stay on the tab 'Details'.
  5. Click the button 'Approve'.
  6. Wait for the toast message to appear and read it.
  7. Read the field 'Status' of the popup and the cell 'Status' of the shipment row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
- Expected:
  1. System should show the toast message "Please add at least one challan".
  2. System should keep the shipment 'Status' = "PENDING".
- Basis: VERIFIED (test_19)

**TRF-N02 — Verify shipment approval is refused while its challan is only DRAFT**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No> with Status DRAFT and All Serial Added = Yes (serial <Asset Serial> saved).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' stay on the tab 'Details'.
  5. Click the button 'Approve'.
  6. Wait for the toast message to appear and read it.
  7. Read the field 'Status' of the popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
- Expected:
  1. System should show the toast message "Approve at least one challan".
  2. System should keep the shipment 'Status' = "PENDING".
- Basis: VERIFIED (test_19)

**TRF-N03 — Verify adding a challan line without From Project is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Leave 'From Project', 'Receiving Branch' and 'To Project' empty.
  6. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  7. In the field 'Quantity' type 1.
  8. Click the button 'Add'.
  9. Wait for the toast message to appear and read it.
  10. Read the item grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = (empty)
  - Asset Item Name = Cabinet Table
  - Quantity = 1
- Expected:
  1. System should show the toast message "Please select from project".
  2. System should add no line to the item grid.
- Basis: VERIFIED (test_19)

**TRF-N04 — Verify adding a challan line without To Project is refused**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Leave 'To Project' empty.
  8. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  9. In the field 'Quantity' type 1.
  10. Click the button 'Add'.
  11. Wait for the toast message to appear and read it.
  12. Read the item grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = (empty)
  - Asset Item Name = Cabinet Table
  - Quantity = 1
- Expected:
  1. System should show the toast message "Please select to project".
  2. System should add no line to the item grid.
- Basis: VERIFIED (test_19)

**TRF-N05 — Verify Draft is refused when the challan has no item line**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and no challan.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Progoti", click the result "[060] Progoti".
  8. Do not choose an item and do not click 'Add'.
  9. Click the button 'Draft'.
  10. Wait for the toast message to appear and read it.
  11. Close the popup with the button 'Close' and read the list on the tab 'Transfer Challans'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [060] Progoti
  - Item line = none
- Expected:
  1. System should show the toast message "No Items in Challan to perform operation".
  2. System should create no challan (the list stays empty).
- Basis: VERIFIED (test_19)

**TRF-N06 — Verify Draft fails for an unmapped To Project**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and no challan.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Administratiion", click the result "[C04] Administratiion" (spelled so on screen).
  8. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  9. In the field 'Quantity' type 1.
  10. Click the button 'Add'.
  11. Click the button 'Draft'.
  12. Wait for the toast message to appear and read it.
  13. Close the popup with the button 'Close' and read the list on the tab 'Transfer Challans'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [C04] Administratiion
  - Asset Item Name = Cabinet Table
  - Quantity = 1
- Expected:
  1. System should show the toast message "Area code not found".
  2. System should create no DRAFT challan (the list stays empty).
- Basis: OBSERVED (catalog)
- Check also: In a new 'Create Challan' popup choose 'From Project' "[015] Microfinance (Dabi)", 'Receiving Branch' "[HO - BDHO] Head Office", 'To Project' "[060] Progoti", 'Asset Item Name' "Cabinet Table", 'Quantity' 1, click 'Add' and 'Draft', and confirm the toast "Challan drafted successfully" appears and a DRAFT challan is listed.

**TRF-N07 — Verify Draft with only the Reset button after Add leaves the popup empty (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and no challan.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Progoti", click the result "[060] Progoti".
  8. In the field 'Note' type "AUTOMATION_TEST challan note".
  9. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  10. In the field 'Quantity' type 1.
  11. Click the button 'Add' and confirm one line is in the item grid.
  12. Click the button 'Reset' and read the form fields and the item grid.
  13. Click the button 'Draft'.
  14. Wait for the toast message to appear and read it.
  15. Close the popup with the button 'Close' and read the list on the tab 'Transfer Challans'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [060] Progoti
  - Note = AUTOMATION_TEST challan note
  - Asset Item Name = Cabinet Table
  - Quantity = 1
- Expected:
  1. After Reset, System should clear the form (message to be confirmed whether the item grid is also cleared).
  2. After Draft, System should refuse and create no challan; the toast message text is to be confirmed.
- Basis: DERIVED (not yet run)

**TRF-N08 — Verify a shipment cannot be approved while its challan is PENDING (submitted, not approved)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No> with Status PENDING (serial <Asset Serial> saved, challan submitted, not yet approved).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' stay on the tab 'Details'.
  5. Click the button 'Approve'.
  6. Wait for the toast message to appear and read it.
  7. Read the field 'Status' of the popup.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
- Expected:
  1. System should refuse the approval.
  2. System should show a validation message (exact text to be confirmed).
  3. System should keep the shipment 'Status' = "PENDING".
- Basis: DERIVED (not yet run)

**TRF-N09 — Verify Add Serial cannot be saved with no serial row (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with one challan <Out Challan No> with Status DRAFT and All Serial Added = No.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. In the list click the link <Out Challan No>.
  6. In 'Challan Details' on the tab 'Details' click the link 'Add Serial' in the item row.
  7. Wait for the popup 'Add Asset Serial'.
  8. Do not choose a 'Serial No' and do not click 'Add'.
  9. Click the button 'Save'.
  10. Wait for the toast message to appear and read it.
  11. Close the popups and read the cell 'All Serial Added' of the row <Out Challan No>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
  - Serial row = none
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should keep 'All Serial Added' = "No" in the row.
- Basis: DERIVED (not yet run)

**TRF-N10 — Verify a challan with All Serial Added = No cannot be submitted (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with one challan <Out Challan No> with Status DRAFT and All Serial Added = No (no serial saved).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. In the row <Out Challan No> click the link 'Edit'.
  6. Wait for the popup 'Update Challan'.
  7. Click the button 'Submit'.
  8. Wait for the toast message to appear and read it.
  9. Read the cell 'Status' of the row <Out Challan No>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No = <Out Challan No>
- Expected:
  1. System should refuse or warn (exact text to be confirmed). The run only verified Submit after the serial was added.
  2. System should keep 'Status' = "DRAFT" if the submit is refused.
- Basis: DERIVED (not yet run)

**TRF-N11 — Verify the same asset serial cannot go into a second challan**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with two challans: <Out Challan No 1> with serial <Asset Serial> already saved on it (a Furniture asset 'Cabinet Table'), and <Out Challan No 2> with Status DRAFT and no serial.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  5. In the list click the link <Out Challan No 2>.
  6. In 'Challan Details' on the tab 'Details' click the link 'Add Serial' in the item row.
  7. Wait for the popup 'Add Asset Serial'.
  8. Click the box 'Serial No' and type <Asset Serial>.
  9. Read the results offered by the box.
  10. If a result for <Asset Serial> is offered, click it, click the button 'Add', and click the button 'Save'; read the toast message.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Out Challan No 2 = <Out Challan No 2>
  - Serial No = <Asset Serial> (already used on the first challan)
- Expected:
  1. System should not offer <Asset Serial> in 'Serial No' (the box lists only approved, unassigned assets), or should show a validation message (exact text to be confirmed).
  2. System should not list <Asset Serial> on the second challan.
- Basis: DERIVED (not yet run)

**SCH-N01 — Verify single challan Add is refused without From Project or To Project (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. No special data is needed; the Asset Single Out Challan screen is used.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. Click the button 'Create'. Wait for the Create Challan popup to open.
  3. Leave 'From Project' empty.
  4. In 'Receiving Branch' type 'Head' and choose 'Head Office'.
  5. In 'To Project' type 'Progoti' and choose '[060] Progoti'.
  6. In 'Asset Item Name' type 'Cabinet' and choose 'Cabinet Table'.
  7. In the field 'Quantity' type 1.
  8. In the field 'Challan Note' type 'AUTOMATION_TEST challan note'.
  9. Click the button 'Add'. Wait for the toast message and read it. Check the item grid.
  10. Click the button 'Reset' to clear the form (or close and reopen the popup).
  11. In 'From Project' choose '[015] Microfinance (Dabi)'.
  12. In 'Receiving Branch' type 'Head' and choose 'Head Office'.
  13. Leave 'To Project' empty.
  14. In 'Asset Item Name' type 'Cabinet' and choose 'Cabinet Table'.
  15. In the field 'Quantity' type 1.
  16. In the field 'Challan Note' type 'AUTOMATION_TEST challan note'.
  17. Click the button 'Add'. Wait for the toast message and read it. Check the item grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Part A: From Project = (empty); Receiving Branch = Head Office; To Project = [060] Progoti; Asset Item Name = Cabinet Table; Quantity = 1; Challan Note = AUTOMATION_TEST challan note
  - Part B: From Project = [015] Microfinance (Dabi); Receiving Branch = Head Office; To Project = (empty); Asset Item Name = Cabinet Table; Quantity = 1; Challan Note = AUTOMATION_TEST challan note
- Expected:
  1. In part A, System should show a validation message (exact text to be confirmed on this screen; the shipment screen uses "Please select from project"). No line should be added to the item grid.
  2. In part B, System should show a validation message (exact text to be confirmed on this screen; the shipment screen uses "Please select to project"). No line should be added to the item grid.
- Basis: DERIVED (not yet run)
- Check also: In the Create Challan popup, fill all fields correctly and click 'Add'; the line should be added, which confirms the refusals above come from the empty project field only.

**SCH-N02 — Verify single challan Draft or Submit with no item line is refused (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. No special data is needed; the Asset Single Out Challan screen is used.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. Click the button 'Create'. Wait for the Create Challan popup to open.
  3. In 'From Project' choose '[015] Microfinance (Dabi)'.
  4. In 'Receiving Branch' type 'Head' and choose 'Head Office'.
  5. In 'To Project' type 'Progoti' and choose '[060] Progoti'.
  6. Do not choose an item and do not click 'Add'; the item grid stays empty.
  7. Click the button 'Draft'. Wait for the toast message and read it. Check whether the popup closes.
  8. Click the button 'Submit'. Wait for the toast message and read it. Check whether the popup closes.
  9. Close the popup with the button 'Close'. Click the button 'Search' and read the top row of the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = Head Office (typed search text: Head)
  - To Project = [060] Progoti (typed search text: Progoti)
  - Item line = none
- Expected:
  1. After Draft, System should show a validation message (exact text to be confirmed; the shipment screen uses "No Items in Challan to perform operation") and the popup should stay open.
  2. After Submit, System should show a validation message (exact text to be confirmed) and the popup should stay open.
  3. No new challan should appear at the top of the grid.
- Basis: DERIVED (not yet run)
- Check also: Note the top row of the grid before step 2 and compare it after step 9; it should be unchanged.

**SCH-N03 — Verify single challan Draft fails for an unmapped To Project (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. The project "[C04] Administratiion" (spelled so on screen) exists in the 'To Project' list and has no area code mapped (this is the case on the Asset Shipment screen).
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. Click the button 'Create'. Wait for the Create Challan popup to open.
  3. In 'From Project' choose '[015] Microfinance (Dabi)'.
  4. In 'Receiving Branch' type 'Head' and choose 'Head Office'.
  5. In 'To Project' type 'C04' and choose '[C04] Administratiion'.
  6. In 'Asset Item Name' type 'Cabinet' and choose 'Cabinet Table'.
  7. In the field 'Quantity' type 1.
  8. In the field 'Challan Note' type 'AUTOMATION_TEST challan note'.
  9. Click the button 'Add'. In the item grid read the new line.
  10. Click the button 'Draft'. Wait for the toast message and read it. Check whether the popup closes.
  11. Close the popup if it is still open, click the button 'Search' and read the top row of the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = Head Office (typed search text: Head)
  - To Project = [C04] Administratiion (typed search text: C04)
  - Asset Item Name = Cabinet Table (typed search text: Cabinet)
  - Quantity = 1
  - Challan Note = AUTOMATION_TEST challan note
- Expected:
  1. System may show the toast "Area code not found" as on the shipment screen; this is not verified on the single challan screen (exact text to be confirmed).
  2. No DRAFT challan should be created for "[C04] Administratiion" (the top row of the grid should not be a new challan with this To Project).
- Basis: DERIVED (not yet run)
- Check also: Repeat with To Project '[060] Progoti'; Draft should work and the row should show 'Status' "DRAFT".

**SCH-N04 — Verify a PENDING single challan cannot be edited**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' PENDING exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1). Its number is known (written below as <Out Challan No.>).
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. In the grid read the cell under the column 'Status' of the row.
  4. Look at the column 'Edit' of the row and check whether an 'Edit' link is there.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
- Expected:
  1. The row should show 'Status' "PENDING".
  2. The row should have no 'Edit' link.
- Basis: VERIFIED (test_23)
- Check also: Create a new challan with the button 'Draft' and check that its row shows an 'Edit' link; then compare with the PENDING row above.

**SCH-N05 — Verify single challan Acknowledge by a user who is not allowed**
- Precondition:
  1. A single challan with 'Status' APPROVED exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1, serial added). Its number is known (written below as <Out Challan No.>). It has not been acknowledged.
  2. A second ERP user exists who is different from the user who created and approved the challan, with the login <Other ERP Username> / <Other ERP Password>. Two such manual users were tried before.
  3. The browser is logged out of the ERP.
- Steps:
  1. Log into the ERP with <Other ERP Username> / <Other ERP Password>.
  2. Open the Fixed Asset module.
  3. Click the menu 'Single Challan', then click the link 'Asset Single In-Challan'. Wait for the list to load.
  4. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  5. Click the link <Out Challan No.> in the column 'Out Challan Number'. Wait for the challan popup to open.
  6. Click the button 'Acknowledge'. Wait for the toast message to appear and read it.
  7. Close the popup if it is still open, click the button 'Search' again and read the cell under the column 'Status' of the row.
- Test data:
  - Login = <Other ERP Username> / <Other ERP Password>
  - Out Challan Number = <Out Challan No.>
- Expected:
  1. In the earlier manual tries, two other users got the error toast "Api error - User not found" in step 6, while the original user could acknowledge.
  2. The 'Status' should stay "APPROVED" (not confirmed by a run).
  3. This is an open question for the BA (should only a user of the receiving branch acknowledge?); the exact rule is to be confirmed.
- Basis: OBSERVED (catalog)
- Check also: Log out, log in with <ERP Username> / <ERP Password> (the original user) and Acknowledge the same challan; the 'Status' should become "ACKNOWLEDGED" with a 'Preview' link.

#### Edge Case

**TRF-E01 — Verify a shipment can be saved with all courier fields empty (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. Click the button 'Create' and wait for the popup 'Create Shipment'.
  3. Leave the fields 'Courier Service Name / Transfer By', 'Courier Number', 'Driver Name', 'Transport No.', 'Courier Details' and 'Note/Remarks' empty.
  4. Click the button 'Save'.
  5. Wait for the toast message to appear and read it.
  6. Click the button 'Search' and read the top row of the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - All six courier fields = (empty)
- Expected:
  1. Only 'Shipment No', 'From Branch' and 'Shipment Date' are marked required and all three are filled automatically, so Save may succeed with the toast "Asset Shipment Initiated Successfuly" and a new PENDING row. This is to be confirmed with the BA (are the courier fields mandatory?).
- Basis: DERIVED (not yet run)

**TRF-E02 — Verify very long text in Courier Details and Note/Remarks (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. Click the button 'Create' and wait for the popup 'Create Shipment'.
  3. In the field 'Courier Service Name / Transfer By' type "AUTOMATION_TEST courier <unique suffix>".
  4. In the field 'Courier Details' type a text of 1000 characters (the letter A repeated 1000 times).
  5. In the field 'Note/Remarks' type a text of 1000 characters (the letter A repeated 1000 times).
  6. Click the button 'Save'.
  7. Wait for the toast message to appear and read it.
  8. If saved, click the button 'Search', click 'Edit' on the top row, and read the length of the saved texts.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Courier Service Name / Transfer By = AUTOMATION_TEST courier <unique suffix>
  - Courier Details = 1000 characters
  - Note/Remarks = 1000 characters
- Expected:
  1. System should either save the shipment (toast "Asset Shipment Initiated Successfuly") with the full text, or show a length validation message (exact text to be confirmed).
- Basis: DERIVED (not yet run)

**TRF-E03 — Verify Quantity larger than the available quantity (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists (only this one is available) and its Asset Serial is known (<Asset Serial>).
  4. A shipment <Shipment No> exists with Status PENDING and no challan.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Progoti", click the result "[060] Progoti".
  8. In the field 'Note' type "AUTOMATION_TEST challan note".
  9. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  10. In the field 'Quantity' type 2.
  11. Click the button 'Add' and read any toast message.
  12. Click the button 'Draft' and read the toast message.
  13. In the list click the new <Out Challan No>, then in 'Challan Details' click the link 'Add Serial'.
  14. Click the box 'Serial No', type <Asset Serial>, click the result, click the button 'Add', then click the button 'Save'.
  15. Read the toast message and the cell 'All Serial Added' of the challan row.
  16. Click the tab 'Transfer Challans' and click the button 'Create' again. Choose 'From Project' "[015] Microfinance (Dabi)", 'Receiving Branch' "[HO - BDHO] Head Office", 'To Project' "[060] Progoti"; in 'Note' type "AUTOMATION_TEST challan note"; choose 'Asset Item Name' "Cabinet Table"; in 'Quantity' type 0; click the button 'Add' and read any toast message and the item grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [060] Progoti
  - Note = AUTOMATION_TEST challan note
  - Asset Item Name = Cabinet Table
  - Quantity = 2, then 0
  - Serial No = <Asset Serial>
- Expected:
  1. System should validate the quantity. A message named "Quantity exceeded!" appears in the catalog, but its trigger was not explored; exact text and trigger are to be confirmed.
  2. System should refuse Quantity 0 (message to be confirmed).
- Basis: DERIVED (not yet run)

**TRF-E04 — Verify two challans under one shipment (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two APPROVED, UNASSIGNED Furniture assets 'Cabinet Table' exist, with Asset Serials <Asset Serial 1> and <Asset Serial 2>.
  4. A shipment <Shipment No> exists with Status PENDING and no challan.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office".
  7. Click the box 'To Project', type "Progoti", click the result "[060] Progoti".
  8. In the field 'Note' type "AUTOMATION_TEST challan note".
  9. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  10. In the field 'Quantity' type 1.
  11. Click the button 'Add', then click the button 'Draft'. Note the new challan number as <Out Challan No 1>.
  12. Click the button 'Create' again. Choose 'From Project' "[015] Microfinance (Dabi)", 'Receiving Branch' "[HO - BDHO] Head Office", 'To Project' "[060] Progoti"; in 'Note' type "AUTOMATION_TEST challan note"; choose 'Asset Item Name' "Cabinet Table"; in 'Quantity' type 1; click the button 'Add', then click the button 'Draft'. Note the new challan number as <Out Challan No 2>.
  13. Click the link <Out Challan No 1>, click the link 'Add Serial', choose <Asset Serial 1> in 'Serial No', click 'Add', click 'Save', then close 'Challan Details'.
  14. Click the link <Out Challan No 2>, click the link 'Add Serial', choose <Asset Serial 2> in 'Serial No', click 'Add', click 'Save', then close 'Challan Details'.
  15. In the row <Out Challan No 1> click the link 'Edit' and click the button 'Submit'.
  16. In the row <Out Challan No 2> click the link 'Edit' and click the button 'Submit'.
  17. Click the menu 'Asset Transfer', then the link 'Asset Shipment Challan Approval List'; filter 'Out Challan No' by <Out Challan No 1>, click 'Search', open the link <Out Challan No 1>, type the comment "AUTOMATION_TEST approve challan" and click the button 'Approve'. (Do not approve <Out Challan No 2>.)
  18. Click the menu 'Asset Transfer', then the link 'Asset Shipment'; filter by <Shipment No>, open <Shipment No>, stay on the tab 'Details'.
  19. Click the button 'Approve'.
  20. Wait for the toast message to appear and read it.
  21. Read the Status of the shipment and of both challans.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [060] Progoti
  - Note = AUTOMATION_TEST challan note
  - Asset Item Name = Cabinet Table
  - Quantity = 1
  - Serial No = <Asset Serial 1> (first challan), <Asset Serial 2> (second challan)
  - Comment = AUTOMATION_TEST approve challan
- Expected:
  1. The refusal text "Approve at least one challan" suggests shipment approval needs one approved challan. System behaviour with one APPROVED and one PENDING challan is to be confirmed (approve with both toasts, or refuse with a message).
  2. The Status of the second challan after shipment approval is to be confirmed.
- Basis: DERIVED (not yet run)

**TRF-E05 — Verify Out Challan Date can differ from Shipment Date**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> was created today and has one challan <Out Challan No> created today.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, read the cell 'Shipment Date' of the row.
  4. Click the link <Shipment No>.
  5. In the popup 'Shipment Details' click the tab 'Transfer Challans'.
  6. In the list read the cell 'Out Challan Date' of the row <Out Challan No>.
  7. Compare the two dates with today's real date.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
- Expected:
  1. System should show 'Shipment Date' = today's real date.
  2. System should show 'Out Challan Date' = the business date, which may be different from 'Shipment Date' (observed 20/09/2026 against a real today of 04/10/2026).
- Basis: OBSERVED (catalog)

**SCH-E01 — Verify single challan Submit works without a serial and the serial is added afterwards**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset exists in project "[015] Microfinance (Dabi)" and its Asset Serial is known (written below as <Asset Serial>). It is not used in any other challan.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. Click the button 'Create'. Wait for the Create Challan popup to open.
  3. In 'From Project' choose '[015] Microfinance (Dabi)'.
  4. In 'Receiving Branch' type 'Head' and choose 'Head Office'.
  5. In 'To Project' type 'Progoti' and choose '[060] Progoti'.
  6. In 'Asset Item Name' type 'Cabinet' and choose 'Cabinet Table'.
  7. In the field 'Quantity' type 1.
  8. In the field 'Challan Note' type 'AUTOMATION_TEST challan note'.
  9. Click the button 'Add'. In the item grid read the new line.
  10. Do not add any serial. Click the button 'Submit'. Wait for the popup to close.
  11. Click the button 'Search'.
  12. In the grid read the cell under the column 'Out Challan Number' of the top row and note it as <Out Challan No.>. Read the cell under the column 'Status' of that row.
  13. Click the link <Out Challan No.> to open the challan popup.
  14. On the tab 'Details' click the link 'Add Serial' on the item row. Wait for the Add Asset Serial popup to open.
  15. In the box 'Serial No' type <Asset Serial> and choose it from the list.
  16. Click the button 'Add'. Read the serial grid of the popup.
  17. Click the button 'Save'. Wait for the toast message to appear and read it.
  18. Click the button 'Close' of the challan popup, reopen the challan by clicking <Out Challan No.>, and click the tab 'Asset Serials'. Read the column 'Asset Serial' of the serial grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = Head Office (typed search text: Head)
  - To Project = [060] Progoti (typed search text: Progoti)
  - Asset Item Name = Cabinet Table (typed search text: Cabinet)
  - Quantity = 1
  - Challan Note = AUTOMATION_TEST challan note
  - Serial No = <Asset Serial>
  - Out Challan Number (read in step 12) = <Out Challan No.>
- Expected:
  1. System should accept Submit without any serial: the popup closes and the top row shows 'Status' "PENDING".
  2. After Add, the Add Asset Serial popup should show one serial row.
  3. After Save, System should show the toast "Asset serial added successfully".
  4. The tab 'Asset Serials' should list <Asset Serial>.
- Basis: VERIFIED (test_23)
- Check also: Open the challan before step 14 and click the tab 'Asset Serials'; the grid should be empty. After step 18 the 'Status' in the popup should still be "PENDING".

**SCH-E02 — Verify approval of a single challan with no serial (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' PENDING exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1) with no serial added. Its number is known (written below as <Out Challan No.>). It was created with Submit and no serial was added afterwards.
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan Approval List'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. In the grid read the cell under the column 'Status' of the row.
  4. Click the link <Out Challan No.> in the column 'Out Challan Number'. Wait for the challan popup to open.
  5. In the comment box of the popup type 'AUTOMATION_TEST approve without serial'.
  6. Click the button 'Approve'. Wait for the toast message to appear and read it.
  7. Click the button 'Search' again and read the cell under the column 'Status' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
  - Comment = AUTOMATION_TEST approve without serial
- Expected:
  1. The row in step 3 should show 'Status' "PENDING".
  2. The challan is listed as PENDING in the approval list even without a serial.
  3. The automation only approved challans that had a serial. System should refuse or approve (to be confirmed): record the exact toast text and the 'Status' after step 7.
- Basis: DERIVED (not yet run)
- Check also: If the approval is accepted, open Gate Pass Generation under the menu 'Single Challan' and check whether the challan is listed with a 'Preview' link; if it is refused, check the 'Status' is still "PENDING".

**SCH-E03 — Verify Reject and Sendback on a single challan (derived)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two single challans with 'Status' PENDING exist (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1, serial added, each with its own asset). The first is written below as <Out Challan No. 1> (used for Reject) and the second as <Out Challan No. 2> (used for Sendback).
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan Approval List'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No. 1> and click the button 'Search'.
  3. Click the link <Out Challan No. 1> in the column 'Out Challan Number'. Wait for the challan popup to open.
  4. In the comment box of the popup type 'AUTOMATION_TEST reject comment'.
  5. Click the button 'Reject'. Wait for the toast message to appear and read it.
  6. Click the button 'Search' again and read the cell under the column 'Status' of the row.
  7. In the filter 'Out Challan Number' replace the text with <Out Challan No. 2> and click the button 'Search'.
  8. Click the link <Out Challan No. 2> in the column 'Out Challan Number'. Wait for the challan popup to open.
  9. In the comment box of the popup type 'AUTOMATION_TEST sendback comment'.
  10. Click the button 'Sendback'. Wait for the toast message to appear and read it.
  11. Click the button 'Search' again and read the cell under the column 'Status' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number (first challan) = <Out Challan No. 1>
  - Out Challan Number (second challan) = <Out Challan No. 2>
  - Comment (Reject) = AUTOMATION_TEST reject comment
  - Comment (Sendback) = AUTOMATION_TEST sendback comment
- Expected:
  1. After Reject, the 'Status' of <Out Challan No. 1> should become "REJECTED" (the status filter of the list offers REJECTED).
  2. After Sendback, the 'Status' of <Out Challan No. 2> should become "SENDBACK" (the status filter of the list offers SENDBACK).
  3. The toast texts and the effects (does the asset serial become free again? can the sender edit the challan?) are to be confirmed.
- Basis: DERIVED (not yet run)
- Check also: After each action, open the Asset Single Out Challan list, filter by the challan number and check the 'Status' and whether an 'Edit' link is present. Then open the serial box of a new challan and type the serial of the rejected challan to see whether it is offered again.

#### Business

**TRF-B01 — Verify the challan appears in Shipment In-Challan only after the SHIPMENT is approved**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and one challan <Out Challan No> with Status APPROVED (serial saved).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment In-Challan'.
  2. In the filter field 'Out Challan No' type <Out Challan No>, then click the button 'Search'.
  3. Read the grid.
  4. Click the menu 'Asset Transfer', then click the link 'Asset Shipment'.
  5. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  6. Click the link <Shipment No>; in the popup 'Shipment Details' stay on the tab 'Details' and click the button 'Approve'. Wait for the toast.
  7. Click the menu 'Asset Transfer', then click the link 'Asset Shipment In-Challan'.
  8. In the filter field 'Out Challan No' type <Out Challan No>, then click the button 'Search'.
  9. In the grid, read the cells 'Challan Status' and 'In Challan No' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan No (filter) = <Out Challan No>
  - Shipment No (filter) = <Shipment No>
- Expected:
  1. Before shipment approval, System should not list <Out Challan No> in Asset Shipment In-Challan (no row).
  2. After shipment approval, System should list <Out Challan No> with 'Challan Status' = "APPROVED".
  3. After shipment approval, System should show 'In Challan No' filled.
- Basis: VERIFIED (test_21 and flow doc for "appears only after")

**TRF-B02 — Verify the Shipment In-Challan status filter offers only APPROVED and ACKNOWLEDGED**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment In-Challan'.
  2. Wait for the page to load completely.
  3. Click the drop-down 'Challan Status' in the filter area and read all its options.
- Test data:
  - Login = <ERP Username> / <ERP Password>
- Expected:
  1. System should offer only the options APPROVED and ACKNOWLEDGED (besides any empty select option).
- Basis: OBSERVED (catalog)
- Check also: Open the drop-down 'Approval Status' on 'Asset Shipment Challan Approval List' and confirm it offers PENDING, APPROVED, REJECTED, ACKNOWLEDGED, SENDBACK (more options than In-Challan).

**TRF-B03 — Verify the shipment row gets a Preview link (consolidated gate pass) after approval**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status APPROVED. Another shipment <Shipment No 2> exists with Status PENDING.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No 2>, then click the button 'Search'.
  3. In the grid, read the cell 'Preview' of the row.
  4. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  5. In the grid, read the cell 'Preview' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No 2>, then <Shipment No>
- Expected:
  1. For the PENDING shipment, System should show no link in the column 'Preview'.
  2. For the APPROVED shipment, System should show a link in the column 'Preview'.
  3. Opening the link was not tested; its content is to be confirmed.
- Basis: VERIFIED (test_20) for the link; content NOT checked.

**TRF-B04 — Verify the full shipment chain end to end**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A fresh APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' exists in project "[015] Microfinance (Dabi)" and its Asset Serial is known (<Asset Serial>).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module.
  2. Click the link 'Asset Shipment'.
  3. Click the button 'Create'.
  4. In the field 'Courier Service Name / Transfer By' type "AUTOMATION_TEST courier <unique suffix>".
  5. In the field 'Courier Number' type "AWB-AUTOTEST-1".
  6. In the field 'Driver Name' type "AUTOMATION_TEST driver".
  7. In the field 'Transport No.' type "TR-AUTOTEST-1".
  8. In the field 'Courier Details' type "AUTOMATION_TEST courier details".
  9. In the field 'Note/Remarks' type "AUTOMATION_TEST shipment note".
  10. Click the button 'Save' and wait for the toast message.
  11. Click the button 'Search'. In the top row note 'Shipment No' as <Shipment No> and read the cell under 'Status'.
  12. Click the link <Shipment No>. The popup 'Shipment Details' opens.
  13. In the popup click the tab 'Transfer Challans'.
  14. Click the button 'Create'. The popup 'Create Challan' opens.
  15. In the box 'From Project' type "Microfinance" and choose "[015] Microfinance (Dabi)".
  16. In the box 'Receiving Branch' type "Head" and choose "[HO - BDHO] Head Office".
  17. In the box 'To Project' type "Progoti" and choose "[060] Progoti".
  18. In the field 'Note' type "AUTOMATION_TEST challan note".
  19. In the box 'Asset Item Name' type "Cabinet" and choose "Cabinet Table".
  20. In the field 'Quantity' type 1.
  21. Click the button 'Add'. One line appears in the item grid.
  22. Click the button 'Draft' and wait for the toast message.
  23. In the 'Transfer Challans' list note the new 'Out Challan No.' as <Out Challan No> and read the cells under 'Status' and 'All Serial Added'.
  24. Click the link <Out Challan No>. The popup 'Challan Details' opens on the tab 'Details'.
  25. Click the link 'Add Serial' on the item row. The popup 'Add Asset Serial' opens.
  26. In the box 'Serial No' type <Asset Serial> and choose it.
  27. Click the button 'Add'. The serial appears in the popup grid.
  28. Click the button 'Save' and wait for the toast message.
  29. Close the popup 'Challan Details'.
  30. In the 'Transfer Challans' list read the cell under 'All Serial Added' of the row <Out Challan No>.
  31. In the same row click the link 'Edit'. The popup 'Update Challan' opens.
  32. Click the button 'Submit'. Read the cell under 'Status' of the row.
  33. Click the menu 'Asset Transfer', then click the link 'Asset Shipment Challan Approval List'.
  34. In the filter 'Out Challan No' type <Out Challan No> and click the button 'Search'.
  35. Click the link <Out Challan No>. The challan popup opens.
  36. In the comment box type "AUTOMATION_TEST approve challan".
  37. Click the button 'Approve' and wait for the toast message. Then search again and read the cell under 'Challan Status'.
  38. Click the menu 'Asset Transfer', then click the link 'Asset Shipment'.
  39. In the filter 'Shipment No' type <Shipment No> and click the button 'Search'.
  40. Click the link <Shipment No>. On the tab 'Details' click the button 'Approve' and read the toast message.
  41. Search again and read the cell under 'Status' of the shipment.
  42. Click the menu 'Asset Transfer', then click the link 'Asset Shipment In-Challan'.
  43. In the filter 'Out Challan No' type <Out Challan No> and click the button 'Search'.
  44. Click the link <Out Challan No>, then click the button 'Acknowledge'.
  45. Wait until the loading overlay disappears. Close the popup if it is still open.
  46. Click the button 'Search' again and read the cell under 'Challan Status'.
  47. Click the menu 'Asset Transfer', then click the link 'Gate Pass Generation'.
  48. In the filter 'Out Challan No' type <Out Challan No> and click the button 'Search'.
  49. Read the cell under 'Status' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Courier Service Name / Transfer By = AUTOMATION_TEST courier <unique suffix>
  - Courier Number = AWB-AUTOTEST-1
  - Driver Name = AUTOMATION_TEST driver
  - Transport No. = TR-AUTOTEST-1
  - Courier Details = AUTOMATION_TEST courier details
  - Note/Remarks = AUTOMATION_TEST shipment note
  - From Project = [015] Microfinance (Dabi)
  - Receiving Branch = [HO - BDHO] Head Office
  - To Project = [060] Progoti
  - Note = AUTOMATION_TEST challan note
  - Asset Item Name = Cabinet Table
  - Quantity = 1
  - Serial No = <Asset Serial>
  - Comment = AUTOMATION_TEST approve challan
  - Read during the run: <Shipment No>, <Out Challan No>
- Expected:
  1. After step 11, System should show the shipment 'Status' = "PENDING".
  2. After step 23, System should show the challan 'Status' = "DRAFT" and 'All Serial Added' = "No".
  3. After step 30, System should show 'All Serial Added' = "Yes".
  4. After step 32, System should show the challan 'Status' = "PENDING".
  5. After step 37, System should show 'Challan Status' = "APPROVED".
  6. After step 40, System should show the toast lines "Shipment approved successfully" and "Gate pass generated successfully"; after step 41 the shipment 'Status' = "APPROVED".
  7. After step 46, System should show 'Challan Status' = "ACKNOWLEDGED".
  8. After step 49, System should list <Out Challan No> with 'Status' = "ACKNOWLEDGED".
- Basis: VERIFIED (test_19, 20, 21, 22)

**TRF-B05 — Verify a shipment cannot be created in the last 3 days of the month (DERIVED, open question)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. The system business date is within the last 3 days of a month (how to set this date is to be confirmed with the BA).
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. Click the button 'Create' and wait for the popup 'Create Shipment'.
  3. In the field 'Courier Service Name / Transfer By' type "AUTOMATION_TEST courier <unique suffix>".
  4. In the field 'Courier Number' type "AWB-AUTOTEST-1".
  5. In the field 'Driver Name' type "AUTOMATION_TEST driver".
  6. In the field 'Transport No.' type "TR-AUTOTEST-1".
  7. In the field 'Courier Details' type "AUTOMATION_TEST courier details".
  8. In the field 'Note/Remarks' type "AUTOMATION_TEST shipment note".
  9. Click the button 'Save'.
  10. Wait for the toast message to appear and read it.
  11. As a control, on a business date just before the last 3 days of a month, open 'Create Shipment' again, type the same six values listed in the test data, click the button 'Save' and read the toast message.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Courier Service Name / Transfer By = AUTOMATION_TEST courier <unique suffix>
  - Courier Number = AWB-AUTOTEST-1
  - Driver Name = AUTOMATION_TEST driver
  - Transport No. = TR-AUTOTEST-1
  - Courier Details = AUTOMATION_TEST courier details
  - Note/Remarks = AUTOMATION_TEST shipment note
  - Business date = a date in the last 3 days of a month; control date = a date before that
- Expected:
  1. The rule exists only in the flow document; no test or screen was seen enforcing it. System should refuse the save in the last 3 days (exact text and exact dates to be confirmed).
  2. On the control date System should save with the toast "Asset Shipment Initiated Successfuly".
- Basis: DERIVED (not yet run)

**TRF-B06 — Verify the same-branch rule for projects (DERIVED, open question)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> exists with Status PENDING and no challan.
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. In the grid, click the link <Shipment No>.
  4. In the popup 'Shipment Details' click the tab 'Transfer Challans', then click the button 'Create'.
  5. Read 'Sending Branch' ("Head Office [BDHO]").
  6. Click the box 'Receiving Branch', type "Head", click the result "[HO - BDHO] Head Office" (same branch as the sending branch).
  7. Click the box 'From Project', type "[015] Microfinance (Dabi)", click the result "[015] Microfinance (Dabi)".
  8. Click the box 'To Project', type "Microfinance", click the result "[015] Microfinance (Dabi)" (same project).
  9. Click the box 'Asset Item Name', type "Cabinet", click the result "Cabinet Table".
  10. In the field 'Quantity' type 1.
  11. Click the button 'Add', then click the button 'Draft'.
  12. Wait for the toast message to appear and read it.
  13. Click the button 'Reset' (or reopen the popup) and fill it again with 'Receiving Branch' "[HO - BDHO] Head Office", 'From Project' "[015] Microfinance (Dabi)", 'To Project' "[060] Progoti", 'Asset Item Name' "Cabinet Table", 'Quantity' 1; click the button 'Add', then click the button 'Draft'.
  14. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Receiving Branch = [HO - BDHO] Head Office (same as the sending branch)
  - First attempt: From Project = [015] Microfinance (Dabi), To Project = [015] Microfinance (Dabi)
  - Second attempt: From Project = [015] Microfinance (Dabi), To Project = [060] Progoti
  - Asset Item Name = Cabinet Table
  - Quantity = 1
- Expected:
  1. Rule in the flow document: same branch needs different projects. For the same project, System should refuse (exact text to be confirmed) and create no challan.
  2. For different projects, System should work and show the toast "Challan drafted successfully".
  3. Only Head Office is offered as Receiving Branch in the seen data, so a different-branch case could not be tried.
- Basis: DERIVED (not yet run)

**TRF-B07 — Verify the Out Challan and In Challan vouchers (DERIVED, open question)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A shipment <Shipment No> has Status APPROVED and contains one challan <Out Challan No> with 'Challan Status' ACKNOWLEDGED and an In Challan No <In Challan No>, from project "[015] Microfinance (Dabi)" to project "[060] Progoti".
- Steps:
  1. Click the menu 'Asset Transfer' in the Fixed Asset module, then click the link 'Asset Shipment'.
  2. In the filter field 'Shipment No' type <Shipment No>, then click the button 'Search'.
  3. Click the link <Shipment No>, then in 'Shipment Details' click the tab 'Transfer Challans'.
  4. Click the link <Out Challan No>, then in 'Challan Details' click the tab 'Posted Accounts' and read it.
  5. Click the tab 'Accounting' in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  6. In 'Module:' choose "Fixed Asset".
  7. In 'Transaction Number' type <Out Challan No>, then click the button 'Search' and read the grid 'Voucher Search List'.
  8. In 'Transaction Number' type <In Challan No>, then click the button 'Search' and read the grid.
  9. In 'Transaction Number' type <Shipment No>, then click the button 'Search' and read the grid.
  10. Open the voucher with the link 'Preview' if a row is found and read the debit and credit lines.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Shipment No (filter) = <Shipment No>
  - Module = Fixed Asset
  - Transaction Number = <Out Challan No>, then <In Challan No>, then <Shipment No>
- Expected (unverified rule):
  1. Out Challan voucher: Debit = Account Head of the project the asset goes to, Credit = Equipment.
  2. In Challan voucher: Debit = Equipment, Credit = that Account Head.
  3. No voucher should exist before acknowledgement.
  4. Observed so far: 'Posted Accounts' was empty and Voucher Search found nothing, so the real behaviour is to be confirmed.
- Basis: DERIVED (not yet run)

**SCH-B01 — Verify approving a single challan creates the gate pass, and acknowledging changes the status**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' PENDING exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1) and its serial has already been added. Its number is known (written below as <Out Challan No.>).
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan Approval List'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. Click the link <Out Challan No.> in the column 'Out Challan Number'. Wait for the challan popup to open.
  4. In the comment box of the popup type 'Approved by automation'.
  5. Click the button 'Approve'. Wait for the toast message to appear and read it.
  6. Click the button 'Search' again and read the cell under the column 'Status' of the row. Check whether the column 'Preview' has a 'Preview' link.
  7. Click the menu 'Single Challan', then the link 'Asset Single In-Challan'.
  8. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  9. Click the link <Out Challan No.> in the column 'Out Challan Number'. Wait for the challan popup to open.
  10. Click the button 'Acknowledge'.
  11. Wait for the loading overlay to disappear. If the popup is still open, click the button 'Close'.
  12. Click the menu 'Single Challan', then the link 'Gate Pass Generation'.
  13. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  14. In the grid read the cell under the column 'Status' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
  - Comment = Approved by automation
- Expected:
  1. System should show one toast with two lines: "Challan approved successfully." and "Gate pass generated successfully".
  2. After approval, the row should show 'Status' "APPROVED" and a 'Preview' link.
  3. After Acknowledge, the Gate Pass Generation row should show 'Status' "ACKNOWLEDGED".
- Basis: VERIFIED (test_24, 25, 26)
- Check also: On Asset Single In-Challan, before step 10, read the row: 'Status' "APPROVED" with the column 'In Challan Number' filled and no 'Preview' link. After step 11 the row should show 'Status' "ACKNOWLEDGED" and a 'Preview' link.

**SCH-B02 — Verify single challan vouchers and receivable/returnable behaviour (DERIVED, open question)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A single challan with 'Status' ACKNOWLEDGED exists (From Project "[015] Microfinance (Dabi)", To Project "[060] Progoti", item Cabinet Table, Quantity 1). Its Out Challan Number and In Challan Number are known (written below as <Out Challan No.> and <In Challan No.>).
- Steps:
  1. In the Fixed Asset module click the menu 'Single Challan', then click the link 'Asset Single Out Challan'. Wait for the list to load.
  2. In the filter 'Out Challan Number' type <Out Challan No.> and click the button 'Search'.
  3. Click the link <Out Challan No.> to open the challan popup. Read the names of the tabs (the verified popup has the tabs 'Details' and 'Asset Serials'; a tab for posted accounts was not seen on this screen).
  4. Close the popup. Click the Accounting tab in the top bar, click the menu 'Voucher', then click the link 'Voucher Search'.
  5. Search for vouchers by <Out Challan No.> (filter label to be confirmed) and read the result grid. Repeat with <In Challan No.>.
  6. Go back to the Fixed Asset module, click the menu 'Single Challan' and open the link 'Asset Receivable List'. Read the grid.
  7. Click the link 'Asset Returnable List'. Read the grid.
  8. Open 'Asset Single Out Challan', click the button 'Create' and look for the options 'Receivable' and 'Returnable' (labels to be confirmed). If 'Returnable' is chosen, a return date field appears (label to be confirmed). Write down what each option shows.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Out Challan Number = <Out Challan No.>
  - In Challan Number = <In Challan No.>
  - Receivable / Returnable values = (value to be confirmed)
- Expected:
  1. Not verified. The vouchers for Out Challan and In Challan were not found in the shipment checks (Posted Accounts was empty and Voucher Search found nothing); the single challan behaviour is to be confirmed.
  2. Asset Receivable List, Asset Returnable List and the Receivable / Returnable options were not explored. System behaviour is to be confirmed.
- Basis: DERIVED (not yet run)
- Check also: Record, for each screen visited, the grid column headings and whether the acknowledged challan appears, so the BA can decide the expected result.

**5. When a CR changes something here — what to re-check**

- If a courier field becomes mandatory or a new field is added on Create/Update Shipment: TRF-P02, P03, P04, P05, E01, E02.
- If the shipment status list or approval rules change (Draft, Reject): TRF-P01, P17, N01, N02, N08, E04, B03.
- If a challan field or project/branch rule changes: TRF-P06 to P09, N03, N04, N06, B05, B06, SCH-P01, N01, N03.
- If serial rules change (disposal / transfer to maintenance, quantity): TRF-P11, N09, N10, N11, E03, SCH-P03.
- If a message text changes: re-check the scenario that quotes it. Note the spelling difference "Successfuly" (shipment) and "successfully" (single).
- If In-Challan visibility or acknowledgement rules change (user/branch): TRF-B01, P18, P19, SCH-P05, N05.
- If gate pass generation changes (when it is made, what it shows): TRF-P17, P20, B03, SCH-P04, P06, B01.
- If vouchers for Out Challan / In Challan are implemented: TRF-B07, SCH-B02, plus Voucher Search.
- If challan approval flow adds Reject or Sendback handling: SCH-E03 and TRF equivalents.

**6. Questions to ask the BA**

- Are the courier fields (name, number, driver, transport) mandatory on Create Shipment?
- What do Update, Delete and Reject do on a shipment?
- What happens on Reject and Sendback for a transfer challan and a single challan (status, comment, is the serial released)?
- What is the exact message and trigger for "Quantity exceeded!"?
- What do the "Disposal" and "Tranfer to maintenance" (spelled so on screen) checkboxes do in Add Asset Serial? What does the Remove link on a wrong serial do?
- Is the "no shipment in the last 3 days of the month" rule real? Exact dates and message?
- Same Receiving and Sending Branch needs different projects: what message? How does a different branch (not Head Office) work, and which user acknowledges for it?
- Which To Projects are mapped to an area code besides "[060] Progoti"? Should the "Area code not found" message be friendlier?
- Are vouchers raised for Out Challan and In Challan, when, and with what accounts (Debit / Credit)? Why is Posted Accounts empty?
- Must the approver and acknowledger be different from the creator? Why did two other users get "Api error - User not found" on Acknowledge?
- Is there a success toast for Acknowledge on either In-Challan screen?
- What does the Gate Pass PDF (transfer and single) contain? What does the consolidated gate pass on the shipment row contain?
- What are the Asset Receivable List and Asset Returnable List, and how do Receivable and Returnable single challans work?
- Must the asset be in the sending project, and is it checked?

---

### Asset Disposal — Write-off and Sale

**1. What this area is, in plain words**
- Disposal is the end of an asset's life in the books. There are two ways out: Write-off (the asset is damaged or no longer usable) and Sale (the asset is sold for a Sale Value).
- A user picks the project and one asset, adds it to a grid with a Note, and then saves it as Draft (can be edited later) or Submit (goes for approval, status PENDING).
- An approver (a user with the disposal approval permission) approves the PENDING record in an Approval List. The creator may approve their own record.
- On approval the system posts accounting vouchers (the success message mentions them). A sold or written-off asset cannot be used again.
- A Sale shows Profit/Loss: Sale Value minus Written Down Value (WDV). Higher than WDV is a profit, lower is a loss.
- Before: the asset was registered, approved and is UNASSIGNED (it may have been assigned, moved or expensed earlier, but must be unassigned again). After: the asset is gone from all pick lists.
- Write-off only accepts an asset whose Utilization Status is NOT IN_USE, so the tester first sets the asset to DAMAGE. Sale accepts IN_USE assets.

**2. Before you test: getting the right starting state**

| State needed | Why | How to get it in short human steps |
|---|---|---|
| An APPROVED, UNASSIGNED asset with Utilization Status DAMAGE | Write-off search lists only assets that are not IN_USE | Register an asset (Registration > Asset Registration by AAQ), Submit, approve it in Asset Registration Approval List. If it was assigned earlier, make sure it is unassigned again. Open the Asset Serial Global List, search the Asset Serial, open its details, click Change next to Asset Utilization Status, choose DAMAGE, type a note, click Update. Look for the toast "Asset profile status updated successfully." |
| An APPROVED, UNASSIGNED asset that is IN_USE and in no pending process | Sale search lists only these | Register, Submit and approve an asset as above. Do not put it in a pending Split, write-off or sale. Note the Asset Serial. No status change is needed. |
| A DRAFT write-off or sale | To test Edit and later Submit | Create the record and click Draft. Note the new ID from the list (filter Status = DRAFT, newest row first). |
| A PENDING write-off or sale | To test approval | Create the record and click Submit, or Edit a Draft and Submit. |
| A user with the disposal approval permission | Approve works only for such a user | Use the normal test user. A user without the permission gets an error (see rules). |
| Written Down Value of the asset | Needed to compute Sale Value for profit and loss | Pick the asset on the Asset Sale screen and read the Written Down Value field (for the test assets this is 25000). |

**3. Rules and what to test for each**

| Rule (plain words) | Where it applies | Pass example | Fail / boundary examples to test |
|---|---|---|---|
| Write-off needs a non-IN_USE asset (set to DAMAGE first) | Asset Write-off, Asset Serial search | DAMAGE asset appears after typing 3+ characters of serial | IN_USE asset gives "No matches found" |
| Sale needs an IN_USE, UNASSIGNED asset not in a pending process | Asset Sale, Asset Serial search | Free IN_USE asset appears | Assigned asset, or one in pending Split, Draft/Pending write-off or sale, gives "No matches found" |
| Asset Serial search needs at least 3 characters | Both create screens | 3 or more characters shows results | 1 or 2 characters shows "Please enter 3 or more characters" |
| Project must be chosen first; search lists only that project's assets | Both create screens | Asset of the chosen project is listed | Asset of another project is not listed |
| Asset details fill automatically after picking the asset | Both create screens | Asset name, Utilization Status, Written Down Value fill in | Fields stay empty if no asset picked |
| Utilization Status is read-only: DAMAGE (write-off) or the asset's own status, IN_USE (sale) | Both create screens | Shows DAMAGE / IN_USE | Field cannot be edited |
| Sale Value is required (sale only) | Asset Sale | Number typed | Empty Sale Value on Add to Grid: message text to be confirmed |
| Profit/Loss = Sale Value minus WDV, 2 decimals | Asset Sale grid | WDV + 5000 shows 5000.00; WDV - 5000 shows -5000.00 | Sale Value equal to WDV should show 0.00 (derived) |
| Note maximum 200 characters | Both create screens | 200 characters accepted (derived boundary) | 201 characters: behaviour to be confirmed |
| Add to Grid shows no toast; Draft/Submit clear the grid | Both create screens | Grid row appears; after save "No data available in table" | - |
| Draft keeps an Edit link in the list; Submit gives PENDING with no Edit | Write-off List, Sale List | DRAFT row has Edit | PENDING / APPROVED rows have no Edit |
| Only PENDING rows have a checkbox in the Approval Lists | Both Approval Lists | PENDING row has a checkbox | DRAFT / APPROVED rows have no checkbox |
| Approve moves PENDING to APPROVED and fills Approved By and Approval Date | Both Approval Lists | Row shows APPROVED | User without permission gets "Api error - User not found"; record stays PENDING |
| Select all approves every PENDING row shown, including other users' rows | Both Approval Lists | All shown PENDING rows become APPROVED | Warning: other users' records on shared systems are approved too |
| An approved (or pending) asset cannot be written off or sold again | Both Asset Serial searches | - | Asset no longer appears ("No matches found") |
| Receive Type is not on the Sale form; list shows BANK for every sale | Asset Sale, Sale List | - | Source document describes a Cash/Bank choice (see BA questions) |

**4. Scenario catalogue**

#### Positive

**WOF-P01 — Verify an asset can be set to DAMAGE as preparation for write-off**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of the project '[015] Microfinance (Dabi)' exists. Its Utilization Status is IN_USE and it is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'. Wait for the page to load.
  2. In the filter 'Asset Serial:' type <Asset Serial>.
  3. Click the button 'Search'. Wait for the grid 'List of Global Asset Serial' to show the row.
  4. In the grid, read the cell under the column 'Utilization Status' of the row. It shows IN_USE.
  5. In the column 'Asset Serial' click the blue link <Asset Serial>. Wait for the popup 'Asset Profile Details' to open on the tab 'Details'.
  6. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update' to open.
  7. In the status drop-down of the small popup (label to be confirmed; it shows the current value IN_USE) choose 'DAMAGE'.
  8. In the mandatory text area 'Note' of the small popup (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  9. Click the button 'Update' in the small popup.
  10. Wait for the toast message to appear and read it.
  11. Close the small popup if it is still open, then click the button 'Close' of the popup 'Asset Profile Details'.
  12. In the filter 'Asset Serial:' type <Asset Serial> again and click the button 'Search'.
  13. In the grid, read the cell under the column 'Utilization Status' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial> (read from the system; Cabinet Table of '[015] Microfinance (Dabi)')
  - Status chosen = DAMAGE
  - Note = AUTOMATION_TEST damaged for write off
- Expected:
  1. System should show the toast "Asset profile status updated successfully."
  2. System should show the column 'Utilization Status' of the row as DAMAGE after the new search (it showed IN_USE before).
  3. The asset should now be eligible for write-off.
- Basis: VERIFIED (test_27)
- Check also: In the grid read the cell under the column 'Assign Status' of the same row. System should still show UNASSIGNED.

**WOF-P02 — Verify a DAMAGE asset is found and its details fill in on the Asset Write-off screen**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of the project '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'. Wait for the page to load.
  2. In the filter 'Asset Serial:' type <Asset Serial>.
  3. Click the button 'Search'. Wait for the row to appear.
  4. In the column 'Asset Serial' click the blue link <Asset Serial>. Wait for the popup 'Asset Profile Details'.
  5. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  6. In the status drop-down of the small popup (label to be confirmed) choose 'DAMAGE'.
  7. In the text area 'Note' of the small popup (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  8. Click the button 'Update'. Wait for the toast message and read it.
  9. Close the small popup if it is still open, then click the button 'Close' of 'Asset Profile Details'.
  10. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'. Wait for the form to load.
  11. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  12. Click the search drop-down 'Asset Serial'.
  13. In its search box type <Asset Serial>.
  14. Wait for the result list and click the result that starts with <Asset Serial>.
  15. Read the fields 'Asset Item Name', 'Utilization Status' and 'Written Down Value'.
  16. Try to change the drop-down 'Utilization Status' by clicking on it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
- Expected:
  1. System should show the toast "Asset profile status updated successfully." in step 8.
  2. System should list the asset in the Asset Serial result list (result text: <Asset Serial>-> Cabinet Table-> Sub Category-> Category-> Group).
  3. System should fill 'Asset Item Name' with the asset name (Cabinet Table).
  4. System should show 'Utilization Status' as DAMAGE.
  5. System should fill 'Written Down Value' (25000 for the test assets).
  6. The field 'Utilization Status' should be read-only (it cannot be changed).
- Basis: VERIFIED (test_27)
- Check also: Read the field 'Branch' and the field 'Department'. System should show 'Branch' pre-filled with the user's branch and 'Department' disabled.

**WOF-P03 — Verify Add to Grid on Asset Write-off adds a row without a toast**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and then disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'.
  14. Watch the screen for a toast message for about 3 seconds.
  15. In the grid below the form read the new row and the column headings.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
- Expected:
  1. System should add exactly one row to the grid.
  2. The row should show the Asset Serial <Asset Serial>, Asset Item Name Cabinet Table, Utilization Status DAMAGE and Note/Remarks "write off".
  3. No toast message should appear after clicking 'Add to Grid'.
- Basis: VERIFIED (test_27)
- Check also: Read the grid column headings. System should show: SL, Profile ID, Asset Serial, Asset Item Name, Asset Project Id, Project Name, Unit Price(TK.), Addition, Accumulated Depreciation, Written Down Value, Utilization Status, Note/Remarks, Action.

**WOF-P04 — Verify a write-off can be saved as Draft**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'. Check that one row appears in the grid.
  14. Click the button 'Draft'.
  15. Wait for the toast message to appear and read it.
  16. Read the grid and the drop-down 'Project' after the save.
  17. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  18. In the filter 'Status' choose 'DRAFT'.
  19. Click the button 'Search'.
  20. In the grid read the top row (newest first): the cells under 'Write Off ID' and 'Status', and the 'Edit' column. Write the Write Off ID down as <Write Off ID>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
  - List filter Status = DRAFT
- Expected:
  1. System should show the toast "Asset write-off drafted successfully".
  2. The grid should show "No data available in table" and the drop-down 'Project' should be cleared (-Select Project-).
  3. The Write-off List should show the new <Write Off ID> in the top row with 'Status' = DRAFT.
  4. That row should have an 'Edit' link.
- Basis: VERIFIED (test_27)
- Check also: Go back to 'Asset Write-off', choose Project '[015] Microfinance (Dabi)', click 'Asset Serial', type <Asset Serial>. System should show "No matches found" because the asset is now in a pending process.

**WOF-P05 — Verify a write-off can be Submitted directly from the form**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'. Check that one row appears.
  14. Click the button 'Submit'.
  15. Wait for the toast message to appear and read it.
  16. Read the grid below the form.
  17. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  18. In the filter 'Status' choose 'PENDING', then click the button 'Search'.
  19. In the grid read the top row: the cells under 'Write Off ID' and 'Status', and the 'Edit' column. Write the Write Off ID down as <Write Off ID>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
  - List filter Status = PENDING
- Expected:
  1. System should show the toast "Asset write-off submitted successfully".
  2. The grid should show "No data available in table".
  3. The Write-off List should show <Write Off ID> with 'Status' = PENDING.
  4. That row should have no 'Edit' link.
- Basis: VERIFIED (test_27)
- Check also: Go to 'Asset Write-off', choose Project '[015] Microfinance (Dabi)', click 'Asset Serial', type <Asset Serial>. System should show "No matches found" (the asset cannot be written off again).

**WOF-P06 — Verify a Draft write-off can be edited from the list and Submitted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'. Check that one row appears.
  14. Click the button 'Draft' and wait for the toast "Asset write-off drafted successfully" to appear and disappear.
  15. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  16. In the filter 'Status' choose 'DRAFT', then click the button 'Search'.
  17. In the grid find the top row and write its 'Write Off ID' down as <Write Off ID>.
  18. In that row click the link 'Edit'. Wait for the Asset Write-off form to open.
  19. Read the grid below the form (Asset Serial, Asset Item Name, Utilization Status, Note/Remarks).
  20. Click the button 'Submit'.
  21. Wait for the toast message to appear and read it.
  22. Read the grid below the form.
  23. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  24. In the filter 'Status' choose 'PENDING', then click the button 'Search'.
  25. In the grid find the row with <Write Off ID> and read its 'Status' cell and its 'Edit' column.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
  - List filters Status = DRAFT, then PENDING
- Expected:
  1. System should open the write-off form with the asset already in the grid: Asset Serial <Asset Serial>, Asset Item Name Cabinet Table, Utilization Status DAMAGE, Note/Remarks "write off".
  2. After Submit the system should show the toast "Asset write-off submitted successfully".
  3. The grid should show "No data available in table".
  4. The Write-off List should show <Write Off ID> with 'Status' = PENDING.
- Basis: VERIFIED (test_28)
- Check also: In the PENDING row of <Write Off ID> look at the 'Edit' column. System should show no 'Edit' link.

**WOF-P07 — Verify a PENDING write-off can be approved**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. This user has the disposal approval permission (the creator may approve their own write-off).
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'. Check that one row appears.
  14. Click the button 'Submit' and wait for the toast "Asset write-off submitted successfully" to appear and disappear.
  15. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  16. In the filter 'Status' choose 'PENDING', click the button 'Search', and write the 'Write Off ID' of the top row down as <Write Off ID>.
  17. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off Approval List'.
  18. In the filter 'Status' choose 'PENDING', then click the button 'Search'.
  19. In the grid find the row with <Write Off ID> and tick the checkbox at the start of that row.
  20. Click the button 'Approve' at the bottom of the page.
  21. Wait for the toast message to appear and read both lines.
  22. In the filter 'Status' choose 'APPROVED', then click the button 'Search'.
  23. In the grid find the row with <Write Off ID> and read the cells under 'Status', 'Approved By' and 'Approval Date'.
- Test data:
  - Login = <ERP Username> / <ERP Password> (user with the disposal approval permission)
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
  - Filters Status = PENDING, then APPROVED
- Expected:
  1. System should show a two-line toast: "Asset write-off approved successfully." and "Journal voucher submitted successfully!".
  2. The row of <Write Off ID> should show 'Status' = APPROVED.
  3. The cells 'Approved By' and 'Approval Date' of that row should be filled.
- Basis: VERIFIED (test_29)
- Check also: Open 'Asset Write-off List', filter 'Status' = APPROVED, click 'Search'. System should show <Write Off ID> as APPROVED there too.

**SAL-P01 — Verify an IN_USE asset is found on the Asset Sale screen with its Written Down Value**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED asset of type Building exists in the project '[015] Microfinance (Dabi)'. Its Utilization Status is IN_USE (never changed to anything else).
  4. The asset is in no pending process (no pending Asset Split, no Draft or Pending write-off, no Draft or Pending sale).
  5. The Asset Serial of the asset is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'. Leave 'Branch' as pre-filled and leave 'Department' (it is disabled).
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial> (the exact serial).
  6. Wait for the result row to appear in the list, then click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Utilization Status'.
  9. Read the field 'Written Down Value'.
  10. Look through the form for a 'Receive Type' or Cash/Bank choice.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
- Expected:
  1. System should list the asset <Asset Serial> in the 'Asset Serial' search results.
  2. System should fill the read-only fields (Asset Item Name, Sub Category, Category, Group, Unit Price, Addition, Accumulated Depreciation) after the asset is picked.
  3. System should show 'Utilization Status' = IN_USE.
  4. System should show a value in 'Written Down Value' (25000 for the test assets).
  5. System should show no Cash/Bank (Receive Type) choice on the form.
- Basis: VERIFIED (test_30)
- Check also: Click the field 'Utilization Status' and try to change it; System should not allow the change because the field is read-only.

**SAL-P02 — Verify a sale at a profit shows a positive Profit/Loss in the grid**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset of type Building exists in the project '[015] Microfinance (Dabi)' and is in no pending process.
  4. The Asset Serial of the asset is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (for a Written Down Value of 25000, type 30000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid'.
  12. Wait for the row to appear in the grid below the form.
  13. In the grid, read the cell under the column 'Sale Value' and the cell under the column 'Profit/Loss' of the new row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>, 25000 for the test assets
  - Sale Value = <Written Down Value> + 5000 (30000 for a Written Down Value of 25000)
  - Note = sale
- Expected:
  1. System should add one row to the grid for <Asset Serial>.
  2. System should show 'Sale Value' = 30000 in the grid row (Written Down Value + 5000).
  3. System should show 'Profit/Loss' = 5000.00 in the grid row.
  4. System should show no toast message after 'Add to Grid'.
- Basis: VERIFIED (test_30)
- Check also: Read the grid headings; System should show the two sale-only columns 'Sale Value' and 'Profit/Loss' in addition to the write-off style columns (SL, Profile ID, Asset Serial, Asset Item Name, Asset Project Id, Asset Project Name, Unit Price, Addition, Accumulated Depreciation, Written Down Value, Note/Remarks, Action).

**SAL-P03 — Verify a sale at a loss shows a negative Profit/Loss in the grid**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset of type Laptop exists in the project '[015] Microfinance (Dabi)' and is in no pending process.
  4. The Asset Serial of the asset is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> - 5000 (for a Written Down Value of 25000, type 20000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid'.
  12. Wait for the row to appear in the grid.
  13. In the grid, read the cell under the column 'Profit/Loss' of the new row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>, 25000 for the test assets
  - Sale Value = <Written Down Value> - 5000 (20000 for a Written Down Value of 25000)
  - Note = sale
- Expected:
  1. System should add one row to the grid for <Asset Serial>.
  2. System should show 'Sale Value' = 20000 in the grid row.
  3. System should show 'Profit/Loss' = -5000.00 in the grid row.
- Basis: VERIFIED (test_30)
- Check also: Take a second asset whose Written Down Value is different (read it first) and type Written Down Value - 5000 as Sale Value; System should show 'Profit/Loss' = -5000.00 again, which proves the figure is calculated from the Written Down Value and not fixed.

**SAL-P04 — Verify a sale can be saved as Draft (profit and loss)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset of type Building exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
  4. The profit run below is done with this Building asset; the loss run (see Check also) is done with a second asset of type Laptop in the same state.
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (30000 for a Written Down Value of 25000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid' and wait for the grid row to appear.
  12. Click the button 'Draft'.
  13. Wait for the toast message to appear and read it.
  14. Read the grid below the form.
  15. Click the menu 'Asset Disposal', then click the link 'Asset Sale List'.
  16. In the drop-down 'Status' choose 'DRAFT'.
  17. Click the button 'Search' and wait for the grid to reload.
  18. In the top row of the grid, read the cell under the column 'Disposal Sale ID' (written below as <Disposal Sale ID>) and the cell under the column 'Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>
  - Sale Value = <Written Down Value> + 5000 (30000)
  - Note = sale
  - Status filter = DRAFT
  - Disposal Sale ID (read) = <Disposal Sale ID>
- Expected:
  1. System should show the toast "Asset sale drafted successfully".
  2. System should show "No data available in table" in the grid below the form after the save.
  3. System should show the newest row of the Asset Sale List with 'Disposal Sale ID' = <Disposal Sale ID> and 'Status' = DRAFT.
  4. System should show an 'Edit' link on that DRAFT row.
- Basis: VERIFIED (test_30)
- Check also: Repeat all steps with a Laptop asset and Sale Value = <Written Down Value> - 5000 (20000 for 25000); System should show the same toast and a new top row with Status DRAFT.

**SAL-P05 — Verify a sale can be Submitted directly (profit and loss)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset of type Building exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
  4. The loss run (see Check also) uses a second asset of type Laptop in the same state.
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (30000 for a Written Down Value of 25000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid' and wait for the grid row to appear.
  12. Click the button 'Submit'.
  13. Wait for the toast message to appear and read it.
  14. Read the grid below the form.
  15. Click the menu 'Asset Disposal', then click the link 'Asset Sale List'.
  16. In the drop-down 'Status' choose 'PENDING'.
  17. Click the button 'Search' and wait for the grid to reload.
  18. In the top row of the grid, read the cell under the column 'Disposal Sale ID' (written below as <Disposal Sale ID>) and the cell under the column 'Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>
  - Sale Value = <Written Down Value> + 5000 (30000)
  - Note = sale
  - Status filter = PENDING
  - Disposal Sale ID (read) = <Disposal Sale ID>
- Expected:
  1. System should show the toast "Asset sale submitted successfully".
  2. System should show "No data available in table" in the grid below the form.
  3. System should show the newest row of the Asset Sale List with 'Disposal Sale ID' = <Disposal Sale ID> and 'Status' = PENDING.
  4. System should show no 'Edit' link on that PENDING row.
- Basis: VERIFIED (test_30)
- Check also: Repeat all steps with a Laptop asset and Sale Value = <Written Down Value> - 5000 (20000 for 25000); System should show the same toast and a new top row with Status PENDING.

**SAL-P06 — Verify a Draft sale can be edited from the Sale List and Submitted**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A sale saved with 'Draft' exists with Status DRAFT: Asset Serial <Asset Serial>, Sale Value = Written Down Value + 5000 (30000), Note 'sale'. Its 'Disposal Sale ID' is known (written below as <Disposal Sale ID>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale List'.
  2. In the drop-down 'Status' choose 'DRAFT'.
  3. Click the button 'Search' and wait for the grid to reload.
  4. In the grid, find the row with 'Disposal Sale ID' = <Disposal Sale ID>.
  5. In that row, click the link 'Edit' (under the column 'Edit').
  6. Wait for the Asset Sale form to open.
  7. Read the grid below the form (the Sale Value and Profit/Loss columns).
  8. Click the button 'Submit'.
  9. Wait for the toast message to appear and read it.
  10. Read the grid below the form.
  11. Click the menu 'Asset Disposal', then click the link 'Asset Sale List'.
  12. In the drop-down 'Status' choose 'PENDING'.
  13. Click the button 'Search' and wait for the grid to reload.
  14. In the grid, read the cell under the column 'Status' of the row with 'Disposal Sale ID' = <Disposal Sale ID>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Disposal Sale ID (known from the Draft) = <Disposal Sale ID>
  - Status filter (first) = DRAFT
  - Status filter (second) = PENDING
- Expected:
  1. System should open the Asset Sale form with the asset <Asset Serial> already in the grid, showing 'Sale Value' = 30000 and 'Profit/Loss' = 5000.00.
  2. System should show the toast "Asset sale submitted successfully".
  3. System should show "No data available in table" in the grid after Submit.
  4. System should show the row <Disposal Sale ID> with 'Status' = PENDING in the Asset Sale List.
- Basis: VERIFIED (test_31)
- Check also: Open the Asset Sale List with Status 'PENDING' and look at the row; System should show no 'Edit' link on it.

**SAL-P07 — Verify PENDING sales can be approved with the select-all checkbox**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>, and this user has the disposal approval permission (the approver).
  2. The Fixed Asset module is open.
  3. Four sales exist with Status PENDING: two sold at a profit (Sale Value = Written Down Value + 5000) and two sold at a loss (Sale Value = Written Down Value - 5000). Their 'Disposal Sale ID' values are known (written below as <Sale ID 1> to <Sale ID 4>).
  4. The sale value, the Note ('sale') and the project ('[015] Microfinance (Dabi)') were as entered on the Asset Sale form.
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale Approval List'.
  2. In the drop-down 'Status' choose 'PENDING'.
  3. Click the button 'Search' and wait for the grid to reload.
  4. Check that the four sales <Sale ID 1> to <Sale ID 4> are listed with 'Status' = PENDING.
  5. Tick the select-all checkbox in the grid heading.
  6. Click the button 'Approve'.
  7. Wait for the toast message to appear and read both lines.
  8. In the drop-down 'Status' choose 'APPROVED'.
  9. Click the button 'Search' and wait for the grid to reload.
  10. In the grid, read the cells under the columns 'Status', 'Approved By' and 'Approval Date' of the rows <Sale ID 1> to <Sale ID 4>.
- Test data:
  - Login = <ERP Username> / <ERP Password> (approver)
  - Sale IDs = <Sale ID 1>, <Sale ID 2>, <Sale ID 3>, <Sale ID 4>
  - Status filter (first) = PENDING
  - Status filter (second) = APPROVED
- Expected:
  1. System should list the four sales with 'Status' = PENDING, each row with a checkbox.
  2. System should show a two-line toast. Line 1: "Asset disposal sale approved successfully." Line 2: "Journal and Credit voucher submitted successfully!"
  3. System should show all four sales with 'Status' = APPROVED.
  4. System should fill 'Approved By' and 'Approval Date' on all four rows.
- Basis: VERIFIED (test_31)
- Check also: Open the Asset Sale List with Status 'APPROVED' and look at the four rows; System should show 'APPROVED' there as well. Warning: select-all also approves PENDING sales of other users on a shared system.

**SAL-P08 — Verify a single PENDING sale can be approved with its own row checkbox**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>, and this user has the disposal approval permission (the approver).
  2. The Fixed Asset module is open.
  3. At least two sales exist with Status PENDING. The sale to approve has 'Disposal Sale ID' <Sale ID> (Asset Serial <Asset Serial>, Sale Value = Written Down Value + 5000). At least one other PENDING sale (<Other Sale ID>) must stay unticked.
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale Approval List'.
  2. In the drop-down 'Status' choose 'PENDING'.
  3. Click the button 'Search' and wait for the grid to reload.
  4. In the grid, find the row with 'Disposal Sale ID' = <Sale ID>.
  5. Tick the checkbox at the start of that row only. Do not tick any other row and not the select-all checkbox.
  6. Click the button 'Approve'.
  7. Wait for the toast message to appear and read both lines.
  8. In the drop-down 'Status' choose 'APPROVED'.
  9. Click the button 'Search' and wait for the grid to reload.
  10. In the grid, read the cell under the column 'Status' of the row <Sale ID>.
  11. In the drop-down 'Status' choose 'PENDING', click the button 'Search' and wait for the grid to reload.
  12. In the grid, read the cell under the column 'Status' of the row <Other Sale ID>.
- Test data:
  - Login = <ERP Username> / <ERP Password> (approver)
  - Sale ID to approve = <Sale ID>
  - Sale ID not ticked = <Other Sale ID>
  - Status filters = PENDING, APPROVED, PENDING
- Expected:
  1. System should show a two-line toast. Line 1: "Asset disposal sale approved successfully." Line 2: "Journal and Credit voucher submitted successfully!"
  2. System should show the row <Sale ID> with 'Status' = APPROVED.
  3. System should keep the row <Other Sale ID> with 'Status' = PENDING.
- Basis: DERIVED (not yet run)
- Check also: Open the Asset Write-off Approval List, filter Status 'PENDING', tick the checkbox of one write-off row and click 'Approve'; System should show the toast "Asset write-off approved successfully." and "Journal voucher submitted successfully!" and approve only that row.

#### Negative

**WOF-N01 — Verify an IN_USE asset is not offered on the Asset Write-off screen**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE (not changed to DAMAGE). Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'. Wait for the form to load.
  2. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  3. Click the search drop-down 'Asset Serial'.
  4. In its search box type <Asset Serial>.
  5. Wait for the result list and read the message shown.
  6. Press the Escape key to close the drop-down.
  7. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  8. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  9. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  10. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  11. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  12. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  13. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  14. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  15. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  16. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  17. Click the search drop-down 'Asset Serial', type <Asset Serial> and read the result list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Project = [015] Microfinance (Dabi)
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
- Expected:
  1. In step 5 system should show "No matches found" and no result for the IN_USE asset.
  2. After the asset is set to DAMAGE, system should list the asset in step 17 (result text starts with <Asset Serial>).
- Basis: VERIFIED (test_27; catalog note that IN_USE assets are not listed)
- Check also: Click the result in step 17. System should fill 'Utilization Status' with DAMAGE.

**WOF-N02 — Verify fewer than 3 characters in Asset Serial gives a hint**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'. Wait for the form to load.
  2. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  3. Click the search drop-down 'Asset Serial'.
  4. In its search box type the 2 characters "BB".
  5. Read the message shown under the search box.
  6. In the same search box type one more character so the text is "BBD".
  7. Read the message or result list shown.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Search text = BB, then BBD
- Expected:
  1. After step 4 system should show "Please enter 3 or more characters".
  2. After step 6 the hint should no longer show; system should search (it shows either matching assets or "No matches found").
- Basis: OBSERVED (catalog)
- Check also: Open the screen 'Asset Sale' (Fixed Asset menu bar, tab 'Asset Disposal'), choose the same project, click 'Asset Serial' and type "BB". System should show "Please enter 3 or more characters" there too.

**WOF-N03 — Verify an asset in a Draft or Pending write-off cannot be written off again**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'. Check that one row appears.
  14. Click the button 'Draft' and wait for the toast "Asset write-off drafted successfully" to appear and disappear.
  15. In the drop-down 'Project' choose '[015] Microfinance (Dabi)' again.
  16. Click the search drop-down 'Asset Serial'.
  17. In its search box type <Asset Serial>.
  18. Wait for the result list and read the message shown.
  19. Press the Escape key to close the drop-down.
  20. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  21. In the filter 'Status' choose 'DRAFT', click 'Search', and in the top row click the link 'Edit'.
  22. Click the button 'Submit' and wait for the toast "Asset write-off submitted successfully" to appear and disappear.
  23. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  24. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  25. Click the search drop-down 'Asset Serial', type <Asset Serial> and read the message shown.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
- Expected:
  1. While the write-off is DRAFT (step 18) system should show "No matches found".
  2. While the write-off is PENDING (step 25) system should show "No matches found".
- Basis: DERIVED (not yet run)
- Check also: In the Fixed Asset menu bar click the tab 'Asset Profile', then the link 'Asset In Pending Process List'. Look for <Asset Serial> in the column 'Asset Serial'. System should list it, with the column 'Pending in Feature' showing the write-off feature (exact text to be confirmed).

**WOF-N04 — Verify an approved written-off asset cannot be written off again**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. This user has the disposal approval permission.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'. Check that one row appears.
  14. Click the button 'Submit' and wait for the toast "Asset write-off submitted successfully" to appear and disappear.
  15. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  16. In the filter 'Status' choose 'PENDING', click 'Search', and write the 'Write Off ID' of the top row down as <Write Off ID>.
  17. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off Approval List'.
  18. In the filter 'Status' choose 'PENDING', then click the button 'Search'.
  19. Tick the checkbox of the row with <Write Off ID> and click the button 'Approve'.
  20. Wait for the toast "Asset write-off approved successfully." / "Journal voucher submitted successfully!" and confirm the row now shows 'Status' = APPROVED after filtering 'Status' = APPROVED and clicking 'Search'.
  21. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  22. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  23. Click the search drop-down 'Asset Serial'.
  24. In its search box type <Asset Serial> and read the message shown.
- Test data:
  - Login = <ERP Username> / <ERP Password> (user with the disposal approval permission)
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
- Expected:
  1. In step 20 the write-off <Write Off ID> should show 'Status' = APPROVED.
  2. In step 24 system should show "No matches found" (the written-off asset is not offered again).
- Basis: DERIVED (not yet run) (rule that a written-off asset cannot be reused is CONFIRMED in the project notes)
- Check also: Open 'Asset Sale' (Fixed Asset menu bar, tab 'Asset Disposal'), choose the same project, click 'Asset Serial', type <Asset Serial>. System should show "No matches found" there too.

**WOF-N05 — Verify an assigned DAMAGE asset is not offered for write-off (precondition may be unreachable: the Global List allows a status change only for an UNASSIGNED asset)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status DAMAGE and Assign Status ASSIGNED (it is currently assigned to an employee). Its Asset Serial is known (<Asset Serial>). It is in no pending process.
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. In the grid read the cells under the columns 'Assign Status' and 'Utilization Status' of the row.
  4. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'. Wait for the form to load.
  5. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  6. Click the search drop-down 'Asset Serial'.
  7. In its search box type <Asset Serial>.
  8. Wait for the result list and read the message shown.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial> (assigned DAMAGE asset)
  - Project = [015] Microfinance (Dabi)
- Expected:
  1. In step 3 the grid should show 'Assign Status' = ASSIGNED and 'Utilization Status' = DAMAGE.
  2. In step 8 system should show "No matches found" (the asset must be UNASSIGNED). Exact behaviour to confirm.
- Basis: DERIVED (not yet run)
- Check also: In the Fixed Asset menu bar click the tab 'Asset Transaction', then the link 'Asset Un Assign', and unassign the asset. Then repeat steps 4 to 8. System should now list the asset in the result list.

**WOF-N06 — Verify Add to Grid without choosing an asset is rejected**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'. Wait for the form to load. Do not choose a Project and do not pick an Asset Serial.
  2. Click the button 'Add to Grid'.
  3. Wait for a message to appear and read it.
  4. Read the grid below the form.
  5. Click the button 'Draft' with the grid still empty.
  6. Wait for a message to appear and read it.
  7. Click the button 'Submit' with the grid still empty.
  8. Wait for a message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = (not chosen)
  - Asset Serial = (not chosen)
  - Note = (empty)
- Expected:
  1. After step 2 system should show a validation message (exact text to be confirmed) and add no row to the grid (the grid should still show "No data available in table").
  2. After steps 5 and 7 system should show a message (exact text to be confirmed) and save nothing.
- Basis: DERIVED (not yet run)
- Check also: Choose Project '[015] Microfinance (Dabi)' only, leave 'Asset Serial' empty and click 'Add to Grid'. System should show a message (text to be confirmed) and add no row.

**WOF-N07 — Verify a user without the approval permission cannot approve a write-off**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. This user does NOT have the disposal approval permission.
  2. The Fixed Asset module is open.
  3. A write-off with status PENDING exists for a Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)'. Its Write Off ID is known (<Write Off ID>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off Approval List'. Wait for the page to load.
  2. In the filter 'Status' choose 'PENDING'.
  3. Click the button 'Search'.
  4. In the grid find the row with <Write Off ID> and tick the checkbox at the start of the row.
  5. Click the button 'Approve' at the bottom of the page.
  6. Wait for the toast message to appear and read it.
  7. In the filter 'Status' choose 'PENDING' again and click 'Search'.
  8. In the grid find the row with <Write Off ID> and read the cell under 'Status'.
- Test data:
  - Login = <ERP Username> / <ERP Password> (user without the approval permission)
  - Write Off ID = <Write Off ID> (read from the system)
  - Filter Status = PENDING
- Expected:
  1. System should show the error toast "Api error - User not found".
  2. The row of <Write Off ID> should still show 'Status' = PENDING; 'Approved By' and 'Approval Date' stay empty.
- Basis: OBSERVED (earlier exploration; not part of the automated runs)
- Check also: Open 'Asset Sale Approval List' (derived), choose 'Status' = PENDING, click 'Search', tick a row and click 'Approve'. System should show an error toast (text to be confirmed) and the sale should stay PENDING.

**SAL-N01 — Verify an asset in a pending Asset Serial Split, Draft/Pending write-off or Draft/Pending sale is not offered for sale**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset exists in the project '[015] Microfinance (Dabi)'. Its Asset Serial is known (written below as <Asset Serial>).
  4. That asset is in a pending process, for example a sale saved with 'Draft' (Status DRAFT) for this asset.
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the search result to refresh and read the text shown in the list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial> (asset in a Draft sale)
- Expected:
  1. System should show "No matches found" in the Asset Serial list.
  2. System should not fill any asset field.
- Basis: VERIFIED (catalog rule in asset sale)
- Check also: Repeat the same steps with an asset in a pending Asset Serial Split, then with an asset in a Draft or Pending write-off, then with an asset in a Pending sale; System should show "No matches found" each time.

**SAL-N02 — Verify fewer than 3 characters in Asset Serial gives a hint on Asset Sale**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. The Asset Sale screen is open (menu 'Asset Disposal', link 'Asset Sale') and the project '[015] Microfinance (Dabi)' is chosen in the drop-down 'Project'.
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type 'BB' (2 characters).
  6. Read the text shown in the list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = BB
- Expected:
  1. System should show "Please enter 3 or more characters" in the Asset Serial list.
  2. System should list no asset.
- Basis: OBSERVED (catalog)
- Check also: In the same search field type a 3rd character, 'BBD'; System should replace the hint with the matching assets or "No matches found".

**SAL-N03 — Verify an assigned asset is not offered for sale**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED asset in the project '[015] Microfinance (Dabi)' has Utilization Status IN_USE and is currently ASSIGNED to an employee (Assign Status ASSIGNED, not unassigned). Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Read the text shown in the list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial> (assigned asset)
- Expected:
  1. System should show "No matches found" in the Asset Serial list.
- Basis: DERIVED (not yet run) (rule "asset must be UNASSIGNED" is CONFIRMED)
- Check also: Unassign the asset (menu 'Asset Transaction', link 'Asset Un Assign', submit and approve), then repeat steps 1 to 6; System should list the asset.

**SAL-N04 — Verify an already sold asset cannot be sold again**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A sale of the asset exists with Status APPROVED (the asset was IN_USE and UNASSIGNED before the sale, in the project '[015] Microfinance (Dabi)'). Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Read the text shown in the list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial> (sold asset)
- Expected:
  1. System should show "No matches found" in the Asset Serial list.
- Basis: DERIVED (not yet run) (rule CONFIRMED in the project notes)
- Check also: Click the menu 'Asset Disposal', then the link 'Asset Write-off', choose the same project and type <Asset Serial> in 'Asset Serial'; System should show "No matches found" there as well.

**SAL-N05 — Verify Add to Grid without a Sale Value is rejected**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Leave the field 'Sale Value' empty.
  9. In the field 'Note' type 'sale'.
  10. Click the button 'Add to Grid'.
  11. Wait for any message and read it.
  12. Read the grid below the form.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Sale Value = (empty)
  - Note = sale
- Expected:
  1. System should show a validation message (exact text to be confirmed).
  2. System should add no row to the grid (the grid still shows "No data available in table").
- Basis: DERIVED (not yet run)
- Check also: In the field 'Sale Value' type 'abc', then -100, and click 'Add to Grid' each time; System should reject or accept each value with a message (expected result to be confirmed).

**SAL-N06 — Verify the Edit link is missing for PENDING and APPROVED records**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. At least one write-off with Status PENDING and one with Status APPROVED exist.
  4. At least one sale with Status PENDING, one with Status APPROVED and one with Status DRAFT exist.
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Write-off List'.
  2. In the drop-down 'Status' choose 'PENDING'.
  3. Click the button 'Search' and wait for the grid to reload.
  4. In the grid, look at the column 'Edit' of the rows.
  5. In the drop-down 'Status' choose 'APPROVED'.
  6. Click the button 'Search' and wait for the grid to reload.
  7. In the grid, look at the column 'Edit' of the rows.
  8. Click the menu 'Asset Disposal', then click the link 'Asset Sale List'.
  9. In the drop-down 'Status' choose 'PENDING'.
  10. Click the button 'Search' and wait for the grid to reload.
  11. In the grid, look at the column 'Edit' of the rows.
  12. In the drop-down 'Status' choose 'APPROVED'.
  13. Click the button 'Search' and wait for the grid to reload.
  14. In the grid, look at the column 'Edit' of the rows.
  15. In the drop-down 'Status' choose 'DRAFT'.
  16. Click the button 'Search' and wait for the grid to reload.
  17. In the grid, look at the column 'Edit' of the rows.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status filters = PENDING, APPROVED (Write-off List); PENDING, APPROVED, DRAFT (Sale List)
- Expected:
  1. System should show no 'Edit' link on any PENDING row of the Asset Write-off List.
  2. System should show no 'Edit' link on any APPROVED row of the Asset Write-off List.
  3. System should show no 'Edit' link on any PENDING row of the Asset Sale List.
  4. System should show no 'Edit' link on any APPROVED row of the Asset Sale List.
  5. System should show an 'Edit' link on the DRAFT rows of the Asset Sale List (Edit appears only on DRAFT rows).
- Basis: VERIFIED (test_27, test_28, catalogs)
- Check also: Open the Asset Write-off Approval List and the Asset Sale Approval List (menu 'Asset Disposal'), choose Status 'PENDING', click 'Search'; System should show no 'Edit' column at all and a checkbox column instead.

**SAL-N07 — Verify a user without the approval permission cannot approve a sale**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>, and this user does NOT have the disposal approval permission.
  2. The Fixed Asset module is open.
  3. A sale with Status PENDING exists (Asset Serial <Asset Serial>, 'Disposal Sale ID' <Sale ID>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale Approval List'.
  2. In the drop-down 'Status' choose 'PENDING'.
  3. Click the button 'Search' and wait for the grid to reload.
  4. In the grid, find the row with 'Disposal Sale ID' = <Sale ID> and tick the checkbox at the start of that row.
  5. Click the button 'Approve'.
  6. Wait for the toast message to appear and read it.
  7. In the drop-down 'Status' choose 'PENDING', click the button 'Search' and wait for the grid to reload.
  8. In the grid, read the cell under the column 'Status' of the row <Sale ID>.
- Test data:
  - Login = <ERP Username> / <ERP Password> (user without the permission)
  - Sale ID = <Sale ID>
  - Status filter = PENDING
- Expected:
  1. System should show an error toast (for write-off the text was "Api error - User not found"; text for sale to be confirmed).
  2. System should keep the sale <Sale ID> with 'Status' = PENDING.
  3. System should show no success toast.
- Basis: DERIVED (not yet run)
- Check also: Read 'Approved By' and 'Approval Date' of the row <Sale ID>; System should show both empty.

#### Edge Case

**WOF-E01 — Verify a Note of exactly 200 characters is accepted on Asset Write-off**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type the letter A exactly 200 times.
  13. Click the button 'Add to Grid'. Check that one row appears and read its cell under 'Note/Remarks'.
  14. Click the button 'Draft'.
  15. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = the letter A typed 200 times (200 characters)
- Expected:
  1. System should accept the Note and add the row; the cell under 'Note/Remarks' should show all 200 characters.
  2. System should save the Draft with the toast "Asset write-off drafted successfully".
- Basis: DERIVED (not yet run) (limit of 200 characters is CONFIRMED)
- Check also: On a new form, type 205 characters into the 'Note' field and read the box. The box may stop at 200 characters; expected result to be confirmed.

**WOF-E02 — Verify a Note of 201 characters is not accepted on Asset Write-off**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type or paste the letter A exactly 201 times.
  13. Read the characters kept in the 'Note' field.
  14. Click the button 'Add to Grid'.
  15. Wait for a message to appear and read it, then read the grid.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = the letter A typed 201 times (201 characters)
- Expected:
  1. System should either stop the extra character (the box keeps 200) or show a validation message (exact text to be confirmed).
  2. The 201st character should not be saved in the grid row.
- Basis: DERIVED (not yet run)
- Check also: Open 'Asset Sale' (Fixed Asset menu bar, tab 'Asset Disposal') and type 201 characters in its 'Note' field. System should behave in the same way (text to be confirmed).

**WOF-E03 — Verify the project filter limits the Asset Serial search**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. Two APPROVED, UNASSIGNED assets with Utilization Status DAMAGE exist in two different projects: asset A in project A (<Project A>) and asset B in project B = '[015] Microfinance (Dabi)'. The Asset Serial of asset B is known (<Asset Serial B>). Project A is any project other than project B (value to be confirmed).
  4. If asset B is still IN_USE, set it to DAMAGE first (steps 1 to 8 below).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial B> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial B> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose <Project A>.
  11. Click the search drop-down 'Asset Serial'.
  12. In its search box type <Asset Serial B>.
  13. Wait for the result list and read the message shown.
  14. Press the Escape key to close the drop-down.
  15. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  16. Click the search drop-down 'Asset Serial', type <Asset Serial B> and read the result list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project A = <Project A> (value to be confirmed)
  - Project B = [015] Microfinance (Dabi)
  - Asset Serial B = <Asset Serial B>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
- Expected:
  1. With project A chosen (step 13) system should show "No matches found".
  2. With project B chosen (step 16) system should list the asset (result text starts with <Asset Serial B>).
- Basis: DERIVED (not yet run)
- Check also: Click the result in step 16. System should fill 'Utilization Status' with DAMAGE and 'Asset Item Name' with the asset name.

**SAL-E01 — Verify a Note of exactly 200 characters is accepted on Asset Sale**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (30000 for a Written Down Value of 25000).
  10. In the field 'Note' type a text of exactly 200 characters (the letter 'A' repeated 200 times).
  11. Click the button 'Add to Grid' and wait for the grid row to appear.
  12. Click the button 'Draft'.
  13. Wait for the toast message to appear and read it.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>
  - Sale Value = <Written Down Value> + 5000 (30000)
  - Note = 200 characters ('A' repeated 200 times)
- Expected:
  1. System should accept all 200 characters in 'Note' and add the row to the grid.
  2. System should show the toast "Asset sale drafted successfully".
- Basis: DERIVED (not yet run)
- Check also: Before step 11, click in the 'Note' field and try to type one more character; System should not accept it (the box may stop at 200).

**SAL-E02 — Verify a Note of 201 characters is not accepted on Asset Sale**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (30000 for a Written Down Value of 25000).
  10. In the field 'Note' type or paste a text of exactly 201 characters (the letter 'A' repeated 201 times).
  11. Read how many characters the 'Note' field now holds.
  12. Click the button 'Add to Grid'.
  13. Wait for any message and read it. Read the 'Note/Remarks' cell of the grid row if a row was added.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>
  - Sale Value = <Written Down Value> + 5000 (30000)
  - Note = 201 characters ('A' repeated 201 times)
- Expected:
  1. System should stop the extra character (the 'Note' field holds 200 characters) or show a validation message (exact text to be confirmed).
  2. System should not save a 201st character in the grid cell 'Note/Remarks'.
- Basis: DERIVED (not yet run)
- Check also: Delete one character so the Note has 200 characters and click 'Add to Grid' again; System should add the row without a message.

**SAL-E03 — Verify a Sale Value equal to the Written Down Value gives zero Profit/Loss**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type the same number as <Written Down Value> (25000 for a Written Down Value of 25000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid'.
  12. Wait for the row to appear in the grid.
  13. In the grid, read the cell under the column 'Profit/Loss' of the new row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>, 25000 for the test assets
  - Sale Value = <Written Down Value> (25000)
  - Note = sale
- Expected:
  1. System should add the row to the grid with 'Sale Value' = 25000.
  2. System should show 'Profit/Loss' = 0.00.
- Basis: DERIVED (not yet run)
- Check also: Click the grid action to remove the row (label to be confirmed), then type 'Sale Value' = 1 and click 'Add to Grid'; System should show 'Profit/Loss' = -24999.00 with 2 decimals (for a Written Down Value of 25000).

**SAL-E04 — Verify a Sale Value with decimals is handled**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 0.50 (25000.50 for a Written Down Value of 25000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid'.
  12. Wait for the row or a message to appear.
  13. In the grid, read the cells under the columns 'Sale Value' and 'Profit/Loss' of the new row, if a row was added.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>
  - Sale Value = 25000.50 (Written Down Value + 0.50)
  - Note = sale
- Expected:
  1. System should add the row and show 'Profit/Loss' = 0.50 with 2 decimals, or reject the decimals with a message (to be confirmed).
- Basis: DERIVED (not yet run) (the automated test types only the integer part)
- Check also: Type 'Sale Value' = 25000.555 and click 'Add to Grid'; the rounding or message is to be confirmed.

#### Business

**WOF-B01 — Verify the full write-off life: Draft, Edit, Submit, Approve**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. This user has the disposal approval permission (the creator may approve their own write-off).
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  2. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  3. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  4. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  5. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  6. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  7. Click the button 'Update'. Wait for the toast "Asset profile status updated successfully." to appear and disappear.
  8. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  9. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  10. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  11. Click the search drop-down 'Asset Serial', type <Asset Serial> and click the matching result.
  12. In the field 'Note' type "write off".
  13. Click the button 'Add to Grid'. Check that one row appears.
  14. Click the button 'Draft'. Wait for the toast message and read it.
  15. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  16. In the filter 'Status' choose 'DRAFT', click 'Search', read the top row and write its 'Write Off ID' down as <Write Off ID>. Read its 'Status' cell.
  17. In that row click the link 'Edit'. Wait for the Asset Write-off form to open with the asset in the grid.
  18. Click the button 'Submit'. Wait for the toast message and read it.
  19. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off List'.
  20. In the filter 'Status' choose 'PENDING', click 'Search', and read the 'Status' cell of the row with <Write Off ID>.
  21. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off Approval List'.
  22. In the filter 'Status' choose 'PENDING', then click 'Search'.
  23. Tick the checkbox of the row with <Write Off ID> and click the button 'Approve'. Wait for the toast message and read both lines.
  24. In the filter 'Status' choose 'APPROVED', click 'Search', and read the cells 'Status', 'Approved By' and 'Approval Date' of the row with <Write Off ID>.
  25. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  26. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  27. Click the search drop-down 'Asset Serial', type <Asset Serial> and read the message shown.
- Test data:
  - Login = <ERP Username> / <ERP Password> (user with the disposal approval permission)
  - Asset Serial = <Asset Serial>
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
  - Project = [015] Microfinance (Dabi)
  - Note = write off
  - List filters Status = DRAFT, PENDING, APPROVED
- Expected:
  1. After step 14 system should show the toast "Asset write-off drafted successfully"; in step 16 the 'Status' is DRAFT.
  2. After step 18 system should show the toast "Asset write-off submitted successfully"; in step 20 the 'Status' is PENDING.
  3. After step 23 system should show the two-line toast "Asset write-off approved successfully." and "Journal voucher submitted successfully!".
  4. In step 24 the row should show 'Status' = APPROVED.
  5. After approval (step 27) the asset should not be offered again: system should show "No matches found".
- Basis: VERIFIED (test_27, test_28, test_29)
- Check also: In step 24 the cells 'Approved By' and 'Approval Date' must be filled.

**WOF-B02 — Verify why DAMAGE must be set first**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)' exists with Utilization Status IN_USE, in no pending process. Its Asset Serial is known (<Asset Serial>).
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'. Wait for the form to load.
  2. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  3. Click the search drop-down 'Asset Serial'.
  4. In its search box type <Asset Serial>.
  5. Wait for the result list and read the message shown.
  6. Press the Escape key to close the drop-down.
  7. In the Fixed Asset menu bar click the tab 'Asset Profile', then click the link 'Asset Serial Global List'.
  8. In the filter 'Asset Serial:' type <Asset Serial> and click the button 'Search'. Wait for the row.
  9. Click the blue link <Asset Serial> in the column 'Asset Serial'. Wait for 'Asset Profile Details'.
  10. Click the button 'Change' next to 'Asset Utilization Status'. Wait for the small popup 'Update'.
  11. In the status drop-down (label to be confirmed) choose 'DAMAGE'.
  12. In the text area 'Note' (label to be confirmed) type "AUTOMATION_TEST damaged for write off".
  13. Click the button 'Update'. Wait for the toast message and read it.
  14. Close the small popup if it is still open, then click 'Close' of 'Asset Profile Details'.
  15. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off'.
  16. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  17. Click the search drop-down 'Asset Serial', type <Asset Serial> and read the result list.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Asset Serial = <Asset Serial> (the same asset for both searches)
  - Project = [015] Microfinance (Dabi)
  - Status chosen = DAMAGE
  - Status Note = AUTOMATION_TEST damaged for write off
- Expected:
  1. In step 5 system should show "No matches found" (the asset is IN_USE).
  2. In step 13 system should show the toast "Asset profile status updated successfully."
  3. In step 17 system should list the asset (result text starts with <Asset Serial>). Write-off lists only assets that are not IN_USE.
- Basis: VERIFIED (test_27)
- Check also: Open the filter 'Asset Utilization Status:' on the Asset Serial Global List and read its options (SPLIT, IN_USE, DAMAGE, STOLEN, BURNED, DONATED, OFFLINE_TRANSFER, UNDER_REPAIR). Whether other non-IN_USE statuses also make the asset eligible for write-off is to be confirmed.

**WOF-B03 — Verify select-all on the Write-off Approval List approves other users' PENDING rows (warning)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. This user has the disposal approval permission.
  2. The Fixed Asset module is open.
  3. At least two write-offs with status PENDING exist, and at least one of them was created by a different user (a shared system). Their Write Off IDs are known (<Write Off ID 1> by this user, <Write Off ID 2> by another user).
  4. The team knows that this test approves every PENDING row shown.
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off Approval List'. Wait for the page to load.
  2. In the filter 'Status' choose 'PENDING'.
  3. Click the button 'Search'.
  4. In the grid read the cells under 'Write Off ID', 'Created By' and 'Status' of every row and write down the PENDING rows.
  5. Tick the select-all checkbox in the grid heading.
  6. Click the button 'Approve' at the bottom of the page.
  7. Wait for the toast message to appear and read it.
  8. In the filter 'Status' choose 'APPROVED' and click 'Search'.
  9. In the grid read the 'Status' and 'Approved By' cells of <Write Off ID 1> and <Write Off ID 2>.
- Test data:
  - Login = <ERP Username> / <ERP Password> (user with the disposal approval permission)
  - Write Off ID 1 = <Write Off ID 1> (created by this user)
  - Write Off ID 2 = <Write Off ID 2> (created by another user)
  - Filters Status = PENDING, then APPROVED
- Expected:
  1. System should approve every PENDING row shown, including rows created by other users: both <Write Off ID 1> and <Write Off ID 2> show 'Status' = APPROVED.
  2. System should show the toast "Asset write-off approved successfully." and "Journal voucher submitted successfully!" (the same two-line toast as a single approval; to be confirmed for a bulk approval).
  3. Warn the team before running this on a shared system. Tick individual rows when only your own records should be approved.
- Basis: DERIVED (not yet run for write-off; the same select-all was verified on the Sale Approval List, test_31)
- Check also: Before step 5 look at the rows with status APPROVED or DRAFT in the grid (filter 'Status' without a value). System should show a checkbox only on PENDING rows.

**WOF-B04 — Verify Reject and Send Back on the Write-off Details popup (open question)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>. This user has the disposal approval permission.
  2. The Fixed Asset module is open.
  3. A write-off with status PENDING exists for a Furniture asset 'Cabinet Table' of '[015] Microfinance (Dabi)'. Its Write Off ID is known (<Write Off ID>) and its Asset Serial is <Asset Serial>.
- Steps:
  1. In the Fixed Asset menu bar click the tab 'Asset Disposal', then click the link 'Asset Write-off Approval List'. Wait for the page to load.
  2. In the filter 'Status' choose 'PENDING', then click 'Search'.
  3. In the grid, in the row of <Write Off ID>, click the link in the column 'Details' (link text to be confirmed). Wait for the popup 'Asset Write Off Details'.
  4. Read the asset grid of the popup (Asset Serial, Item Name, Purchase Price, Written Down Value, Accumulated Depreciation, Addition, Status, Asset Assign Status, Disposal Type).
  5. Look at the buttons at the bottom of the popup.
  6. In the comment box of the popup (label to be confirmed) type "AUTOMATION_TEST comment".
  7. Click the button 'Reject'.
  8. Wait for the toast message to appear and read it.
  9. In the filter 'Status' choose 'REJECTED' and click 'Search'. Read the 'Status' cell of <Write Off ID>.
  10. Open the Asset Write-off screen (Fixed Asset menu bar, tab 'Asset Disposal', link 'Asset Write-off'), choose Project '[015] Microfinance (Dabi)', click 'Asset Serial', type <Asset Serial> and read the message or result.
  (For the Send Back path, repeat steps 1 to 6 on another PENDING write-off, click the button 'Send Back' instead of 'Reject' in step 7, and filter 'Status' = 'SENDBACK' in step 9.)
- Test data:
  - Login = <ERP Username> / <ERP Password> (user with the disposal approval permission)
  - Write Off ID = <Write Off ID>
  - Asset Serial = <Asset Serial>
  - Comment = AUTOMATION_TEST comment
  - Project = [015] Microfinance (Dabi)
- Expected:
  1. Behaviour not yet known. The popup has a comment box, a date, and the buttons Approve, Reject, Send Back and Close.
  2. Expected status after Reject (REJECTED) / Send Back (SENDBACK) and whether the asset is offered again on the Asset Write-off screen are to be confirmed.
- Basis: OBSERVED (catalog; Approve via popup never completed)
- Check also: Open the filter 'Status' of the Approval List and read its options. System should offer PENDING, APPROVED, REJECTED, DRAFT and SENDBACK.

**SAL-B01 — Verify the full sale life on the Draft path**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>, and this user has the disposal approval permission (the same user creates, submits and approves).
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset of type Building exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (30000 for a Written Down Value of 25000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid' and wait for the grid row to appear.
  12. Click the button 'Draft'. Wait for the toast message and read it.
  13. Click the menu 'Asset Disposal', then click the link 'Asset Sale List'.
  14. In the drop-down 'Status' choose 'DRAFT', click the button 'Search' and wait for the grid to reload.
  15. In the top row, read the cells under the columns 'Disposal Sale ID' (written below as <Disposal Sale ID>) and 'Status'.
  16. In that row click the link 'Edit' and wait for the Asset Sale form to open.
  17. Click the button 'Submit'. Wait for the toast message and read it.
  18. Click the menu 'Asset Disposal', then click the link 'Asset Sale List'.
  19. In the drop-down 'Status' choose 'PENDING', click the button 'Search' and wait for the grid to reload.
  20. Read the cell under the column 'Status' of the row <Disposal Sale ID>.
  21. Click the menu 'Asset Disposal', then click the link 'Asset Sale Approval List'.
  22. In the drop-down 'Status' choose 'PENDING', click the button 'Search' and wait for the grid to reload.
  23. Tick the checkbox at the start of the row <Disposal Sale ID>.
  24. Click the button 'Approve'. Wait for the toast message and read both lines.
  25. In the drop-down 'Status' choose 'APPROVED', click the button 'Search' and wait for the grid to reload.
  26. Read the cells under the columns 'Status', 'Approved By' and 'Approval Date' of the row <Disposal Sale ID>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>
  - Sale Value = <Written Down Value> + 5000 (30000)
  - Note = sale
  - Disposal Sale ID (read) = <Disposal Sale ID>
- Expected:
  1. System should show the toast "Asset sale drafted successfully", and the list row <Disposal Sale ID> should show 'Status' = DRAFT.
  2. System should show the toast "Asset sale submitted successfully" after Submit, and the list row should show 'Status' = PENDING.
  3. System should show the two-line toast on Approve. Line 1: "Asset disposal sale approved successfully." Line 2: "Journal and Credit voucher submitted successfully!"
  4. System should show 'Status' = APPROVED with 'Approved By' and 'Approval Date' filled.
- Basis: VERIFIED (test_30, test_31)
- Check also: Repeat the whole flow with a Laptop asset and 'Sale Value' = <Written Down Value> - 5000 (20000 for 25000); System should show the same messages and statuses.

**SAL-B02 — Verify the full sale life on the Submit path**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>, and this user has the disposal approval permission.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset of type Building exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (30000 for a Written Down Value of 25000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid' and wait for the grid row to appear.
  12. Click the button 'Submit'. Wait for the toast message and read it.
  13. Click the menu 'Asset Disposal', then click the link 'Asset Sale List'.
  14. In the drop-down 'Status' choose 'PENDING', click the button 'Search' and wait for the grid to reload.
  15. In the top row, read the cells under the columns 'Disposal Sale ID' (written below as <Disposal Sale ID>), 'Edit' and 'Status'.
  16. Click the menu 'Asset Disposal', then click the link 'Asset Sale Approval List'.
  17. In the drop-down 'Status' choose 'PENDING', click the button 'Search' and wait for the grid to reload.
  18. Tick the checkbox at the start of the row <Disposal Sale ID>.
  19. Click the button 'Approve'. Wait for the toast message and read both lines.
  20. In the drop-down 'Status' choose 'APPROVED', click the button 'Search' and wait for the grid to reload.
  21. Read the cell under the column 'Status' of the row <Disposal Sale ID>.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>
  - Sale Value = <Written Down Value> + 5000 (30000)
  - Note = sale
  - Disposal Sale ID (read) = <Disposal Sale ID>
- Expected:
  1. System should show the toast "Asset sale submitted successfully".
  2. System should show the list row <Disposal Sale ID> with 'Status' = PENDING and no 'Edit' link.
  3. System should show the two-line toast on Approve. Line 1: "Asset disposal sale approved successfully." Line 2: "Journal and Credit voucher submitted successfully!"
  4. System should show 'Status' = APPROVED for the row <Disposal Sale ID>.
- Basis: VERIFIED (test_30, test_31)
- Check also: Repeat with a Laptop asset and 'Sale Value' = <Written Down Value> - 5000; System should show the same results. At no point should an 'Edit' link appear on the row.

**SAL-B03 — Verify Profit/Loss in the grid matches Sale Value minus Written Down Value**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. An APPROVED, UNASSIGNED, IN_USE asset of type Building exists in the project '[015] Microfinance (Dabi)' and is in no pending process. Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. Wait for the Asset Sale form to load.
  3. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  4. Click the search box 'Asset Serial'.
  5. In the search field that opens, type <Asset Serial>.
  6. Wait for the result row and click the result row that shows <Asset Serial>.
  7. Wait for the read-only fields to fill in.
  8. Read the field 'Written Down Value' (written below as <Written Down Value>, 25000 for the test assets).
  9. In the field 'Sale Value' type <Written Down Value> + 5000 (30000 for a Written Down Value of 25000).
  10. In the field 'Note' type 'sale'.
  11. Click the button 'Add to Grid' and wait for the grid row to appear.
  12. In the grid, read the cell under the column 'Profit/Loss' of the row.
  13. In the column 'Action' of that row, click the option that removes the row (label to be confirmed).
  14. Check that the grid is empty and that the asset is still picked on the form (if the form was cleared, pick the asset again as in steps 4 to 7).
  15. In the field 'Sale Value' type <Written Down Value> - 5000 (20000 for a Written Down Value of 25000).
  16. Click the button 'Add to Grid' and wait for the grid row to appear.
  17. In the grid, read the cell under the column 'Profit/Loss' of the row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial>
  - Written Down Value (read) = <Written Down Value>, 25000 for the test assets
  - Sale Value (first) = <Written Down Value> + 5000 (30000)
  - Sale Value (second) = <Written Down Value> - 5000 (20000)
  - Note = sale
- Expected:
  1. System should show 'Profit/Loss' = 5000.00 for 'Sale Value' above the Written Down Value.
  2. System should show 'Profit/Loss' = -5000.00 for 'Sale Value' below the Written Down Value.
- Basis: VERIFIED (test_30)
- Check also: Run the same two sale values on an asset of type Laptop; System should show 5000.00 and -5000.00 again, so the sign rule applies to every asset type tested (Building and Laptop).

**SAL-B04 — Verify an approved sold asset cannot be used again anywhere**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. A sale of the asset exists with Status APPROVED (the asset was IN_USE and UNASSIGNED before the sale, in the project '[015] Microfinance (Dabi)'). Its Asset Serial is known (written below as <Asset Serial>).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale'.
  2. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  3. Click the search box 'Asset Serial', type <Asset Serial> and read the text shown in the list.
  4. Click the menu 'Asset Disposal', then click the link 'Asset Write-off'.
  5. In the drop-down 'Project' choose '[015] Microfinance (Dabi)'.
  6. Click the search box 'Asset Serial', type <Asset Serial> and read the text shown in the list.
  7. Click the menu 'Asset Transaction', then click the link 'Asset Assign'.
  8. Try to find <Asset Serial> in the asset search of the Asset Assign screen (label of the search field to be confirmed) and read the result.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Project = [015] Microfinance (Dabi)
  - Asset Serial (typed) = <Asset Serial> (sold asset)
- Expected:
  1. System should show "No matches found" on the Asset Sale screen.
  2. System should show "No matches found" on the Asset Write-off screen.
  3. System should not offer the asset on the Asset Assign screen (for example "No matches found"; exact text to be confirmed).
- Basis: DERIVED (not yet run)
- Check also: Open the menu 'Asset Profile', link 'Asset Serial Global List', search <Asset Serial> and read the asset status; the value after a sale is not asserted so far (to be confirmed).

**SAL-B05 — Verify vouchers after approval (contents unverified)**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>, and this user has the disposal approval permission.
  2. The Fixed Asset module is open.
  3. A sale with Status PENDING exists ('Disposal Sale ID' <Sale ID>, Asset Serial <Asset Serial>, Sale Value = Written Down Value + 5000).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale Approval List'.
  2. In the drop-down 'Status' choose 'PENDING', click the button 'Search' and wait for the grid to reload.
  3. Tick the checkbox at the start of the row <Sale ID>.
  4. Click the button 'Approve'.
  5. Wait for the toast message to appear and read both lines.
  6. Open the voucher screens of the project '[015] Microfinance (Dabi)' (menu path and screen name to be confirmed) and look for the new Journal voucher and Credit voucher of this sale.
  7. Click the menu 'Asset Disposal', then click the link 'Asset Write-off List' and read the column 'Dr/Cr Note' of a write-off row.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Sale ID = <Sale ID>
  - Project = [015] Microfinance (Dabi)
- Expected:
  1. System should show the two-line toast. Line 1: "Asset disposal sale approved successfully." Line 2: "Journal and Credit voucher submitted successfully!" (for a write-off the second line is "Journal voucher submitted successfully!").
  2. System should create vouchers; what the vouchers contain (accounts, amounts) is not yet verified (see BA questions).
- Basis: DERIVED (not yet run)
- Check also: Read the column 'Dr/Cr Note' in the Asset Write-off List for an approved write-off; what it shows is to be confirmed.

**SAL-B06 — Verify the Receive Type shown in the Sale List**
- Precondition:
  1. The user is logged into the ERP with <ERP Username> / <ERP Password>.
  2. The Fixed Asset module is open.
  3. At least one sale exists (any status).
- Steps:
  1. Click the menu 'Asset Disposal' in the Fixed Asset module, then click the link 'Asset Sale List'.
  2. Click the button 'Search' (leave the drop-down 'Status' as it is) and wait for the grid to reload.
  3. In the grid, read the cell under the column 'Receive Type' of every row shown.
  4. In the drop-down 'Status' choose 'DRAFT', click the button 'Search' and wait for the grid to reload.
  5. In the grid, read the cell under the column 'Receive Type' of the rows.
- Test data:
  - Login = <ERP Username> / <ERP Password>
  - Status filter = (default), then DRAFT
- Expected:
  1. System should show 'Receive Type' = BANK on every sale row, because the Sale form has no Cash/Bank choice.
- Basis: OBSERVED (catalog)
- Check also: Read the columns 'Bank Name', 'Bank Branch Name', 'Bank Account No' and 'Cheque No' of a row; what they show for a sale is to be confirmed.

**5. When a CR changes something here — what to re-check**
- A field is added or changed on the Write-off or Sale form (for example a required field, Receive Type) → WOF-P02, WOF-P03, WOF-N06, SAL-P01, SAL-P02, SAL-N05, SAL-B06 and the grid columns.
- Note length changes → WOF-E01, WOF-E02, SAL-E01, SAL-E02.
- Asset eligibility changes (status, assigned, pending process) → WOF-N01, WOF-N03, WOF-N05, WOF-B02, SAL-N01, SAL-N03.
- Status or approval flow changes (new status, Reject, Send Back, multi-level approval) → WOF-P04 to WOF-P07, WOF-B01, WOF-B03, WOF-B04, SAL-P04 to SAL-P08, SAL-B01, SAL-B02, SAL-N06.
- Profit/Loss formula or Sale Value rules change → SAL-P02, SAL-P03, SAL-E03, SAL-E04, SAL-B03.
- Message text changes → every scenario quoting a toast (WOF-P04 to WOF-P07, SAL-P04 to SAL-P07, WOF-N07).
- Voucher or accounting changes → SAL-B05 and a voucher check in both approvals.
- Permission rules change → WOF-N07, SAL-N07.

**6. Questions to ask the BA**
- What exactly do Reject and Send Back do for write-off and sale? What status does the record get, can it be edited again, and is the asset freed?
- Which vouchers are posted on approval (accounts, debit/credit, amounts, date)? What does the Dr/Cr Note column show?
- What is the asset's status after write-off or sale approval in the Asset Serial Global List?
- What are the exact validation messages for: no asset picked, empty Sale Value, Note longer than 200 characters, empty grid on Draft/Submit?
- Should the Sale form offer Cash/Bank (Receive Type)? The source document describes it but the screen has no such field and the list shows BANK for all sales.
- Can the creator approve their own record, or should the system require a different user?
- Should select-all approval be limited to the user's own records?
- Which other statuses (besides DAMAGE) make an asset eligible for write-off?
- What is the Disposal Date: the ERP business date or the date of action?
- Is the Sale Value allowed to have decimals or be zero or negative?

---
