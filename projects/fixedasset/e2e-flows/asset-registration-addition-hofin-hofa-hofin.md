# Flow: Asset Registration & Asset Addition (HOFIN → HOFA → HOFIN)

**Business scenario:** ERP Fixed Asset has two related but distinct
HOFIN-originated journeys that both cross into HOFA for acknowledgment and
back into HOFIN for final approval: **Asset Registration** (a brand-new
asset entered via a Vendor Bill Payable) and **Asset Addition** (an
addition against an existing/allocated Bill, flagged via the "Fixed Asset
Addition" checkbox). Both share the identical HOFIN → HOFA → HOFIN
skeleton and the same Transaction No. handoff; they differ only inside the
"Fixed Asset Details" pop-up step. **The two sections are chained, not
independent**: Section A's final step produces an Asset Serial Number
that Section B's Asset Addition process must consume — see Section A
Step 4 and the Notes below.

---
## Section A — Asset Registration

**Automation Suitable:** Yes — deterministic 3-role journey (HOFIN
Creator → HOFA Acknowledger → HOFIN Approver), no visual judgment required
at any step; needs credentials for the HOFIN creator, the HOFA
acknowledger, and the specific HOFIN approval user (`kazi.mm@brac.net`)
configured in `.env`. Also produces `asset_serial_number` (Step 4, below)
that Section B's Asset Addition process consumes — Section A must run to
completion before Section B starts.

| Step | Role/Login | Action | Reference | Data carried forward |
|---|---|---|---|---|
| 1 | HOFIN User (Creator) — https://hofin42.erp.bracits.net/ | 1. Log in. 2. Navigate Vendor → Payable Journal. 3. Click Create. 4. Fill all required fields in "Create Vendor Bill Payable". 5. Skip "Advance Adjustment Details". 6. Fill "Bill Allocation Details" (Project-015, A/C code: Furniture and Fixer). 7. Click Add. 8. Record the auto-generated Transaction No. 9. Click "Fixed Asset Details" and fill all mandatory fields. 10. Click Add in the Fixed Asset Details pop-up. 11. Click Confirm. 12. Click "Yes" on the "Do you want to continue? You are confirming item information for the bill." dialog. 13. Copy the Transaction No. from the Transaction No. field. 14. Click Submit. 15. Verify the success message. | automation-only: no confirmed standalone manual case yet — cross-check row Names in `Test_Case_HOFIN-ASSET-REG.xlsx` before automating; keep as automation-only if no match | `transaction_no` — produced here |
| 2 | HOFA Acknowledger — https://env42.erp.bracits.net/ | 1. Log in. 2. Navigate to Fixed Asset. 3. Click Registration menu. 4. Click "Asset Registration Pending/Review" list. 5. Enter `transaction_no` in the Payable Number field. 6. Click Search. 7. Click Action → View. 8. Click Acknowledged. | automation-only: no standalone manual case for this lookup+acknowledge step | `transaction_no` — consumed here |
| 3 | HOFIN Approver (`kazi.mm@brac.net`) — https://hofin42.erp.bracits.net/ | 1. Log in as the approval user. 2. Navigate Approval → Approval. 3. Enter `transaction_no` in the Transaction No. field. 4. Click Search. 5. Click Action for the matching transaction. 6. Click Approve. | automation-only: no standalone manual case for this approval step | `transaction_no` — consumed here |
| 4 | HOFA Acknowledger — https://env42.erp.bracits.net/ | 1. Log in to HOFA again. 2. Navigate to Asset Profile → Asset Serial Global List. 3. Identify the latest Asset Serial Number from the list (e.g. `BBDASR00227617`). 4. Copy the latest Asset Serial Number. | automation-only: no standalone manual case for this lookup step | `asset_serial_number` — produced here, consumed in Section B |

---
## Section B — Asset Addition

**Automation Suitable:** Yes — identical shape to Section A, same 3-role
journey and credential needs; only the "Fixed Asset Details" pop-up
interaction differs (adds a Bill-selection step and the "Fixed Asset
Addition" checkbox).

| Step | Role/Login | Action | Reference | Data carried forward |
|---|---|---|---|---|
| 1 | HOFIN User (Creator) — https://hofin42.erp.bracits.net/ | 1. Log in. 2. Navigate Vendor → Payable Journal. 3. Click Create. 4. Fill all required fields in "Create Vendor Bill Payable". 5. Skip "Advance Adjustment Details". 6. Fill "Bill Allocation Details" (Project-015, A/C code: Furniture and Fixer). 7. Click Add. 8. Record the auto-generated Transaction No. 9. Click "Fixed Asset Details". 10. **Select the Bill from the "Bill Allocation" dropdown in the pop-up** (a normal dropdown, not a button — confirmed in UI exploration on 2026-09-27; it must be picked first because it filters the Serial No list by project and A/C code). 11. **Select the "Fixed Asset Addition" checkbox.** 12. **In the "Fixed Asset Serial No" field, enter `asset_serial_number`, search, and select the matching (parent) asset.** 13. Fill all other mandatory fields. 14. Click Add in the Fixed Asset Details pop-up. 15. Click Confirm. 16. Click "Yes" on the "Do you want to continue? You are confirming item information for the bill." dialog. 17. Copy the Transaction No. from the Transaction No. field. 18. Click Submit. 19. Verify the success message. | automation-only: no confirmed standalone manual case yet — cross-check row Names in `Test_Case_HOFIN-ASSET-REG.xlsx` before automating; keep as automation-only if no match | `transaction_no` — produced here; `asset_serial_number` — consumed here (produced in Section A Step 4) |
| 2 | HOFA Acknowledger — https://env42.erp.bracits.net/ | 1. Log in. 2. Navigate to Fixed Asset. 3. Click Registration menu. 4. Click "Asset Registration Pending/Review" list. 5. Enter `transaction_no` in the Payable Number field. 6. Click Search. 7. Click Action → View. 8. Click Acknowledged. | automation-only: no standalone manual case for this lookup+acknowledge step | `transaction_no` — consumed here |
| 3 | HOFIN Approver (`kazi.mm@brac.net`) — https://hofin42.erp.bracits.net/ | 1. Log in as the approval user. 2. Navigate Approval → Approval. 3. Enter `transaction_no` in the Transaction No. field. 4. Click Search. 5. Click Action for the matching transaction. 6. Click Approve. | automation-only: no standalone manual case for this approval step | `transaction_no` — consumed here |

> **CONFIRMED (user, 2026-09-27)**: the "Fixed Asset Serial No"
> search/select happens inside the Fixed Asset Details pop-up **after**
> "Select Bill from the Bill Allocation button" and ticking "Fixed Asset
> Addition", and before the remaining mandatory fields (Step 1 sub-step
> 12 above). Per the CR, this list shows parent asset serials only.
>
> **CONFIRMED (user spec, 2026-09-27; supersedes an earlier "standalone"
> decision)**: Section B follows exactly the same workflow, roles,
> validations, data and Creator → Acknowledger → Approver approval flow
> as Section A. The only difference is the asset selection step, where
> `asset_serial_number` is used to search for and select the parent
> asset. That value is always taken at run time from Section A Step 4 in
> the same run, and is never hardcoded or supplied externally.

---
## Notes for the Automation Engineer
- Three browser contexts per flow, not two: HOFIN Creator, HOFA
  Acknowledger, and HOFIN Approver are three distinct logins — the
  approver (`kazi.mm@brac.net`) is a different account from the creator
  even though both hit the same HOFIN base URL. Never reuse a session
  across any of the three.
- `transaction_no` is captured once per flow (Step 1's "Record the
  auto-generated Transaction No." sub-step) and threaded as a variable
  through the rest of that flow's steps — the later "copy Transaction No."
  sub-step (after Confirm) re-confirms the same value, it does not produce
  a new one.
- Section A (Registration) and Section B (Addition) are now **one
  chained flow**, not independent scenarios: Section A must run to
  completion (through its Step 4 HOFA lookup) before Section B starts.
  `asset_serial_number`, captured in Section A Step 4, is threaded into
  Section B the same way `transaction_no` is threaded within each
  section already — never re-derived or hardcoded. It plugs into Section
  B Step 1 sub-step 12 (see the CONFIRMED notes under Section B's table). They remain in one
  file because they share the same HOFIN → HOFA → HOFIN skeleton and
  nearly all of their steps, in addition to now sharing this data
  dependency.
- The only functional difference between the two flows is inside the
  "Fixed Asset Details" pop-up: Addition additionally selects a Bill via
  "Select Bill from the Bill Allocation button" and checks "Fixed Asset
  Addition" before filling mandatory fields; Registration skips both.
  Build this as a shared helper/page-object method with a parameter (e.g.
  `is_addition: bool`) rather than duplicating the whole pop-up
  interaction in two places.
- Steps execute strictly in the order listed within each section —
  acknowledgment cannot happen before creation, approval cannot happen
  before acknowledgment.
- No step in either flow currently has a confirmed standalone manual
  Test_Cases row — verify against `test-cases/Test_Case_HOFIN-ASSET-REG.xlsx`
  (by row Name) before writing automation; where no match exists, the
  `automation-only` marking stands and this flow file remains the sole
  spec for that step, so document that in the test's inline comments.
- Two applications are involved (HOFIN at https://hofin42.erp.bracits.net/,
  HOFA at https://env42.erp.bracits.net/) — `project_config.yaml`'s single
  `application_url` field is still an unfilled placeholder and only has
  room for one URL. Resolve this (e.g. two named env vars,
  `HOFIN_URL`/`HOFA_URL`) before writing `.env`/`automation/config/settings.py`.

---
## Automation status (2026-10-10)
- Automated in `automation/tests/test_32_asset_registration_addition_hofin.py` (2 tests, run in order) with `utils/hofin_flow.py`; both passed against hofin42 / env42 on 2026-10-10.
- Section A Step 4 now reads the newest parent asset (item "Sofa Set") from the Asset Serial Global List. Section B then checks the new `<parent>-1` row, its Parent Asset field and the parent's Addition History tab.
- URLs and logins: `HOFA_URL`, `HOFIN_URL` and the three logins are read from `.env` (see `.env.example`). The note above about a single `application_url` is closed: `project_config.yaml` has `hofa_url` and `hofin_url`; HOFA is the Fixed Asset application used by every Fixed Asset test.
- The approver (kazi.mm@brac.net in the manual) is a different login from the creator; one browser window per role.
- Locators: `automation/element_catalog/vendor_bill_payable.md`, `asset_registration_pending_review_list.md`, `hofin_approval_list.md`.
