# FAHOV2-643 Business Understanding: Asset Addition with Reference Number with existing asset (CR V1.6)

Primary source (source of truth): `projects/fixedasset/cr/FAHOV2-643_Asset_Addition_with_Reference_Number_V1.6.md` (read in full, 2,361 lines).
Secondary sources (lower precedence; conflicts with the CR are tagged NEEDS_CLARIFICATION):
- S1 = draft flow `projects/fixedasset/e2e-flows/asset-registration-addition-hofin-hofa-hofin.md`
- S2 = HOFIN user manual "Asset Registration from HO FIN" (registration only; the manual does not cover additions)
- S3 = QA "Scope of Work" list for FAHOV2-643 (verification checklist)
Also read: `projects/fixedasset/project_config.yaml`. Domain file `knowledge/erp-fixedasset.md` used for background only (read-only, being edited by another agent).

Tag legend: `CONFIRMED` (stated in the CR, or in a secondary source where marked), `INFERRED` (reasonable reading, not stated), `UNKNOWN` (silent), `NEEDS_CLARIFICATION` (contradiction/ambiguity, human decision needed).
Ids use the CR numbering, e.g. `F08S01 8.1.8`. "Extended asset" = the CR's extended/subsidiary/child asset ("child" is the word S3 uses).

Status: DRAFT for human review. Test cases must not be generated until the NEEDS_CLARIFICATION items in section 12 are resolved or explicitly accepted.

---

## 1. Summary and scope

1.1 [CONFIRMED] (Purpose) Today an asset addition only adds its cost to the parent asset's price and recalculates the unit price. The CR changes this: each addition creates a separate asset entity (extended asset) under the parent asset, with a parent-extended relationship, a minimum capitalization threshold and correct depreciation. (Purpose; F01S01 1.1.4)
1.2 [CONFIRMED] Applies across the whole Fixed Asset system, HOFA and FOFA. (Purpose; Scope table)
1.3 [CONFIRMED] In scope: new addition process creating a new asset entity; parent/extended tracking and reporting; new "Parent Asset" field; new addition-history tab on Asset Profile Details; new validations on extended assets; new list view for extended assets; asset split conditions. (Scope table)
1.4 [CONFIRMED] Out of scope: extended-asset addition from branch offices (only through the Head Office Finance HOFIN module); anything not in the SRS. S3 states the same ("addition cannot be performed from FOFIN (Field/Branch Office)"); "FOFIN" is not a term in the CR.
1.5 [CONFIRMED] Impairment business was removed from the whole document in v1.5. (Revision History)
1.6 [CONFIRMED] 25 features (F01-F25), 40 stories (F25 has 16 report stories). Features by kind:
- New data/UI: F01 (Global List, Asset Profile), F25S01 (new report).
- Selection screens (hide extended, auto-include): F02, F03, F04, F08, F10, F11, F18, F21 (F18/F21 differ, see Q1).
- Indented list views: F05-F07, F09, F12-F17, F19, F20, F22, F23.
- Restriction: F24 (split).
- Existing reports changed: F25S02-F25S16.
1.7 [CONFIRMED] The Workflow section of the CR says "N/A". The addition workflow is derived from rules scattered in F01, F08, F10, F11, F13, F18, F21 (section 5), and from S1/S2 for the screens.
1.8 [CONFIRMED] Revision history: v1.3 renamed child to "extension asset", new serial format, extended assets can be sold or written off separately, split restriction; v1.4 bulk upload validation, auto-assignment, sale value allocation; v1.5 impairment removed; v1.6 pending-state restrictions and child-disposal rules. (Revision History)
1.9 [UNKNOWN] The CR gives no performance, security, audit-log or data-migration requirement (all "Non-functional Requirements: N/A"). Treatment of existing assets that already carry merged additions is not mentioned.
1.10 [INFERRED] "with Reference Number" in the title most likely points to the Reference Number (HOFIN posted voucher number) column of the Addition History tab (F01S02 1.2.8 ii e). The CR does not explain the title (Q11).
1.11 [CONFIRMED by S3] QA scope is organised in 27 groups: core addition flow, profile/history tab, 18 screen groups mirroring F02-F23, Asset Split, Split Approval List, Depreciation. S3 adds checks that are not in the CR (marked "secondary-only" where they appear below).

---

## 2. Glossary

| Term | Meaning | Tag | Ref |
|---|---|---|---|
| Parent asset | The existing active asset under which an addition is registered. Only parents are offered for addition and for selection in most transaction screens. | CONFIRMED | F01S01 1.1.5, 1.1.8 |
| Extended / subsidiary / child asset | A standalone asset created by an approved addition. Same serial as the parent plus a hyphen and a number. Names used interchangeably (S3 says "child"). | CONFIRMED | F01S01 1.1.8 i; Revision v1.3 |
| Asset Addition | Registering an additional purchase against an existing asset. New behaviour: creates a new extended asset instead of merging cost into the parent. | CONFIRMED | Purpose; F01S01 |
| Addition amount | Price of the added asset (Addition History column "Addition Amount"). | CONFIRMED | F01S02 1.2.8 ii c |
| Minimum capitalization threshold | Minimum price an addition must meet; defined per asset group. Value and failure message not given. S3 adds "addition is blocked if below the threshold for that asset group". | CONFIRMED (existence, block per S3), UNKNOWN (value, message) | F01S01 1.1.5, 1.1.9; S3 1.1 |
| HOFIN | Head Office Finance module where the addition request is created, submitted, and finally approved; posts the voucher. | CONFIRMED | Scope table; F01S01; S2 |
| HOFA | Head Office Fixed Asset module where the request is acknowledged. S2: the request appears in Registration > Asset Registration Pending/Review List of the HOFA environment connected to the HOFIN environment. | CONFIRMED | F01S02 1.2.5; F08 8.1.8; S2 |
| FOFA / FOFIN | Field (branch) office Fixed Asset system / Field office finance. Expansion of the acronyms is not in the CR. | CONFIRMED (FOFA impacted), INFERRED (expansion) | Purpose; S3 |
| Transaction No. | Auto-generated number of the HOFIN vendor bill payable (generated when Bill Allocation Details is added; the Fixed Asset Details button then appears). Used to find the request in the HOFIN Approval screen. Not in the CR. | CONFIRMED (S1, S2) | S1; S2 Step 5, 11 |
| Asset Serial Global List | Fixed Asset > Asset Profile > Asset Serial Global List. Extended assets appear here as separate rows. | CONFIRMED | F01S01 1.1.2, 1.1.8 ii |
| Asset Profile Details | Pop-up opened by clicking an asset serial. Gets a "Parent Asset" field (extended assets only) and an addition-history tab (parent assets only). | CONFIRMED | F01S02 |
| Parent Asset field | Shows the parent's serial. Only on extended assets. | CONFIRMED | F01S02 1.2.8 |
| Addition History tab | New tab on parent assets only. Name conflicts across the CR (Q4). | CONFIRMED (existence), NEEDS_CLARIFICATION (name) | F01S02 |
| Parent Asset Serial JSON reference | Value used to send combined (accumulated) parent plus extended data to the finance module for shipment, challan, expense, write-off, sale. Structure not described. | CONFIRMED (name, use), UNKNOWN (structure) | F08 8.1.4 iv; F10; F11; F13; F17; F18; F20; F21; F23 |
| Utilization Status | Asset state such as IN_USE; extended assets can change independently; parent changes overwrite children. (Existing values per domain file: SPLIT, IN_USE, DAMAGE, STOLEN, BURNED, DONATED, OFFLINE_TRANSFER, UNDER_REPAIR. S3 uses Damaged/Stolen/Burned/Donated.) | CONFIRMED (rule), INFERRED (value list) | F01S02 1.2.8 |
| Assign Status | ASSIGNED / UNASSIGNED. | CONFIRMED | F18 18.1.8 |
| Active and not merged extended asset | Only these are auto-included and shown in lists. "Merged" is not defined. | CONFIRMED (filter), NEEDS_CLARIFICATION (meaning) | F02 2.1.12; F05 5.1.12; others |
| Auto-included | Extended assets fetched and listed under the selected parent automatically, with no remove button. | CONFIRMED | F02-F04, F08, F10, F11, F18, F21 |
| Indentation | Extended serial shown with 4 space indentation, no SL number, no action button. (S3: "parent serial left-aligned, child serial right-aligned/indented".) | CONFIRMED | e.g. F02 2.1.8 iii |
| Asset Addition List (report) | New report listing parent assets that have extended assets. | CONFIRMED | F25S01 |
| Total Addition | In reports: combined purchase value of all extended assets under a parent. | CONFIRMED | F25S03 |
| Total unit price | Purchase Price + Total Addition. | CONFIRMED | F25S03 |
| WDV | Written Down Value = Total unit price - Accumulated Depreciation. | CONFIRMED | F25S01 XIX |
| Disposal | Write-off or Sale (existing types per domain file: WRITE_OFF, SALE, AUCTION, SPLIT). | CONFIRMED (write-off, sale) | F18, F21 |
| Backend Support Sale/Write-Off | Disposal via backend support; counted in disposal depreciation in schedule and statement reports. Not defined further. | CONFIRMED (mention), UNKNOWN (process) | F25S04, F25S13, F25S14 |
| Journal Voucher (JV) | Finance voucher generated for the new asset and for shipment/challan; S3 checks its generation and that the parent's JV is unaffected. CR does not describe JV content. | CONFIRMED (S3), UNKNOWN (content) | S3 1.1, 1.9, 1.11 |

---

## 3. Actors and roles

The CR names only "Authorized user" (every story) and "Authorized HO User" (F25S01 25.1.3). It does not name roles or permissions. Role detail comes from S1/S2.

| Actor | Responsibility | Tag | Source |
|---|---|---|---|
| Authorized user | Performs every user story in the CR. | CONFIRMED | all stories |
| Authorized HO user | Runs the new Asset Addition List report; can choose Head Office or Branch Office in "Report For". | CONFIRMED | F25S01 25.1.3, 25.1.8 i |
| HOFIN creator | Creates the vendor bill payable and Fixed Asset Details (Bill, Fixed Asset Addition checkbox, parent serial) and submits. S2 example user: dijendra.nm@brac.net (registration). | CONFIRMED (S1, S2), INFERRED (CR says only "via HOFIN") | S1; S2 Step 1; F01S01 1.1.8 |
| HOFA acknowledger | Acknowledges in HOFA (Registration > Asset Registration Pending/Review List). | CONFIRMED (CR: "acknowledged in HOFA"; screen from S1, S2) | F08 8.1.8; S1; S2 Step 10 |
| HOFIN approver | Approves in HOFIN (Approval > Approval; search by Transaction No.; Action; Approve). Example account kazi.mm@brac.net in both S1 and S2. | CONFIRMED (stage in CR; account in S1/S2) | F08 8.1.8; S1; S2 Step 11 |
| Branch office user | Cannot add extended assets. Receives extended assets via In-Challan. S3: after HO addition the asset can be Assigned, Unassigned and Transferred at the Field Office. | CONFIRMED | Scope table; F10 10.1.8; S3 1.3-1.5 |
| System (auto-assignment) | Triggers assignment and asset-transaction approval automatically for a new extended asset when the parent is assigned. | CONFIRMED | F02 2.1.8 |
| Finance module (system) | Receives combined data (section 10). | CONFIRMED | F08 etc. |

3.1 [UNKNOWN] Whether creator and approver must be different users, who may acknowledge in HOFA, and role names.
3.2 [INFERRED] Three-login model (creator, acknowledger, approver) matches the CR's three states.

---

## 4. User-stated workflow versus the CR and secondary sources

The user's message said: asset registration/addition starts in HOFIN -> HOFA -> HOFIN, described as "approval in HOFA, acknowledgment in HOFIN".

4.1 [CONFIRMED by CR] Sequence: HOFIN submit -> HOFA ACKNOWLEDGE -> HOFIN APPROVE. Evidence: "already acknowledged in HOFA but pending approval in HOFIN" (F08 8.1.8, F10 10.1.8, F11 11.1.8, F13 13.1.8, F18 18.1.8, F21 21.1.8); "acknowledgement is pending in HOFA" (same); "Asset addition must be acknowledged and approved in the HOFA and HOFIN system respectively" (F01S02 1.2.5).
4.2 [CONFIRMED by S1] Step 1 HOFIN creator submits, Step 2 HOFA "Acknowledged", Step 3 HOFIN approver "Approve".
4.3 [CONFIRMED by S2] The HOFIN manual (registration flow) gives the same order: Phase 1 create and submit in HOFIN, Phase 2 "Review / Acknowledge" in HOFA ("Need to acknowledge this from here"), Phase 3 approve in HOFIN with the approval user (kazi.mm@brac.net). Final result: "the asset will be successfully registered". S2 describes registration; for additions it is INFERRED to apply (same skeleton as S1).
4.4 [CONFIRMED, user 2026-10-10] The order is HOFIN submit -> HOFA acknowledge -> HOFIN approve, for asset registration and asset addition. The user's earlier wording ("approval in HOFA, acknowledgment in HOFIN") is withdrawn. Other functionalities will adopt this flow later (Q12 resolved).
4.5 [CONFIRMED by S2] Prerequisites for the flow: (1) know which HOFA environment is connected to the HOFIN environment in use; (2) HOFIN and HOFA must be on the same business date; (3) otherwise the submitted request may not appear in the HOFA Pending/Review List. S2 gives an SQL check on the `configuration` table. The CR is silent on this. [Treat as test-environment pre-condition.]
4.6 [CONFIRMED by S2] Screen texts: confirm dialog "Do you want to continue?You are confirming item information for the bill." (Yes / No; Yes closes the pop-up and keeps the data; No keeps the pop-up open); success message after Submit "Transaction Submitted Successfully". Transaction No. is generated on clicking Add in Bill Allocation Details, and the Fixed Asset Details button becomes visible only after that.
4.7 [CONFIRMED, user 2026-10-10] Target environment (QA): HOFIN `https://hofin42.erp.bracits.net/`, HOFA `https://env42.erp.bracits.net/` (Q27 resolved on the URLs). Still to verify before a run: that the pair is connected and on the same business date (4.5). Earlier note, superseded: environment URLs differed: S2 uses `hofinstaging.brac.net` (HOFIN) and `erpstaging.brac.net` (HOFA), project_config.yaml uses `erpstaging.brac.net`, S1 uses `hofin42.erp.bracits.net` and `env42.erp.bracits.net`. Which pair is the target for this CR's test run, and are they connected to each other (4.5)? (Q27)
4.8 [CONFIRMED] Result when approved: a new standalone asset is created in the Global List with parent serial plus hyphen number. (F01S01 1.1.8)
4.9 [CONFIRMED] Registration of a brand-new asset (S1 Section A, S2) is not the subject of the CR. The CR says only the parent "must already exist and be active" and "Asset registration must be done with the asset addition condition" (F01S01 1.1.5); the latter is INFERRED to mean the "Fixed Asset Addition" checkbox of S1 (not named in the CR; S2 does not mention it).
4.10 [INFERRED] End-to-end chain: register parent (S1 Section A) -> read serial from Global List -> create addition against it (S1 Section B) -> after HOFIN approval check `<parent>-<n>` in the Global List, Parent Asset field, Addition History tab.
4.11 [UNKNOWN] Reject, send-back, cancel or withdraw paths for an addition.

---

## 5. Workflow states for an addition and what each locks

| State | Meaning | Parent locks in Fixed Asset | Tag | Ref |
|---|---|---|---|---|
| S0 Before submission | HOFIN user builds the request. Submission is blocked if the parent is in Transfer, Shipment, Write-off or Sale. Addition is blocked while the parent (or its extended asset) is pending in Assign, Unassign, Internal Movement, Transaction List, Transaction Approval List or Assign Acknowledgement. Also blocked if amount is below the capitalization threshold (S3) and if the target is an extended asset. | not applicable | CONFIRMED (CR); threshold block CONFIRMED by S3 | F01S01 1.1.8; F08 8.1.8; S3 1.1 |
| S1 Submitted, pending HOFA acknowledgement | Request sent from HOFIN ("Transaction Submitted Successfully"). | Parent (with or without extended assets) restricted from Transfer, Shipment, Write-off, Sale. | CONFIRMED | F08 8.1.8; F10, F11, F13, F18, F21 |
| S2 Acknowledged in HOFA, pending HOFIN approval | HOFA acknowledged. | Same restriction. | CONFIRMED | F08 8.1.8 |
| S3 Approved in HOFIN | New extended asset created and listed in the Global List; parent unchanged; JV generated (S3); auto-assignment if the parent is assigned; depreciation calculated separately for parent and child (S3). | Locks released (INFERRED). | CONFIRMED (creation), CONFIRMED by S3 (JV, separate depreciation), INFERRED (release) | F01S01 1.1.8; F02 2.1.8; S3 1.1, 1.27 |
| S4 Rejected / sent back / cancelled | Not described. | UNKNOWN | UNKNOWN | none |

5.1 [CONFIRMED] Parent data is unchanged by an addition: purchase value, WDV, remaining lifetime, other info. (F01S01 1.1.8; also S3 1.1: Purchase Price, WDV, Remaining Life Time each verified.)
5.2 [CONFIRMED] No new asset can be added under an extended asset; additions only at the parent level. (F01S01 1.1.8)
5.3 [CONFIRMED by S3, secondary-only] Multiple additions (multiple children) are allowed under the same parent. The CR does not say this explicitly but does not forbid it. Whether two may be pending at the same moment remains open (Q9).
5.4 [CONFIRMED by S3, secondary-only] A child asset cannot be reassigned to a different parent; "if this were to happen, the only resolution is disposal (Sale/Write-Off)". The CR has no re-parenting feature; the sentence is odd. (Q30)
5.5 [INFERRED] "Transfer" in the lock rule covers Shipment and Single Out Challan; "Disposal" covers Write-off and Sale. F18/F21 use "Shipment/Challan/Disposal" for the child-disposal rule (Q13).
5.6 [UNKNOWN] Whether Assign, Unassign, Internal Movement, Expenditure are blocked while an addition is pending (CR lists only Transfer/Shipment/Write-off/Sale).
5.7 [UNKNOWN] Whether a second addition on the same parent can be submitted while the first is in S1 or S2 (Q9).
5.8 [CONFIRMED by S3] Depreciation is calculated separately for the parent and separately for each child. CR hints at this only via "ensure proper depreciation calculation" and combined figures in reports. Rate, method and start date remain UNKNOWN. S3 also lists an open check: "whether a new serial ID is generated when an Asset Split is approved" (Q28).

---

## 6. Business rules

### 6A. Selection screens: hide extended assets and auto-include them

Applies to F02 Assign, F03 Unassign, F04 Internal Movement, F08 Shipment (Add Serial tab and Add Asset Serial pop-up), F10 Shipment In-Challan, F11 Single Out Challan. (F18/F21 in 6C.)

| ID | Rule | Tag | Ref |
|---|---|---|---|
| A1 | Extended assets are not selectable on their own; only parents are offered. | CONFIRMED (also S3 1.3-1.5, 1.9, 1.11, 1.12, 1.14) | F02 2.1.4; F03 3.1.4; F04 4.1.4; F08; F10; F11 |
| A2 | Assign/Unassign/Internal Movement: extended assets do not appear when searching the Asset Serial field. S3: "can never be searched/selected individually". | CONFIRMED | 2.1.8; 3.1.8; 4.1.8 |
| A3 | Assign/Unassign/Internal Movement: typing an extended serial shows a validation message. Requirements: "the selected asset not found"; Acceptance: it indicates extended assets "cannot be selected". Exact text missing; S3 gives no text either (it says the child "can never be searched/selected"). | NEEDS_CLARIFICATION | 2.1.8 vs 2.1.11; F03; F04 (Q3) |
| A4 | Shipment/In-Challan/Single Out Challan: Asset Serial No. / Serial No. drop-downs list parent assets only; extended must be prevented. No message text. | CONFIRMED (rule), UNKNOWN (message) | 8.1.8; 10.1.8; 11.1.8; AC 8.1.11 |
| A5 | Selecting a parent (S3: "search by parent's ID and click Add to Grid") fetches all associated active, not-merged extended assets into the list, directly under the parent. | CONFIRMED | 2.1.8; 3.1.8; 4.1.8; 8.1.8; 10.1.8; 11.1.8 |
| A6 | Indentation: extended serial indented, "4 space indentation". | CONFIRMED | all |
| A7 | Extended rows have no action button (remove/delete); cannot be deselected. S3: Delete/Action button only on the parent row. | CONFIRMED | all |
| A8 | Removing the parent from the grid removes its extended assets. | CONFIRMED | all |
| A9 | Inactive extended assets must not appear in the list. | CONFIRMED | 2.1.11; 3.1.11; 4.1.11 |
| A10 | Operation applies equally to the parent and all listed extended assets; the group stays in one transaction. | CONFIRMED | 2.1.11 and others |
| A11 | Parent and extended appear together in Transaction List, Transaction Approval List and (Assign/Unassign) Asset Assign Acknowledgement as one transaction. | CONFIRMED | 2.1.11; 3.1.11; 4.1.11 (Internal Movement lists only the first two) |
| A12 | Unassign and Internal Movement: same behaviour for Search By employee PIN. Assign has no PIN search in the CR. | CONFIRMED | 3.1.8; 4.1.8 |
| A13 | After submission the normal approval workflow is followed. | CONFIRMED | 2.1.8; 3.1.8; 4.1.8 |
| A14 | Shipment Add Serial tab: quantity recorded for the parent counts the parent only; extended assets are fetched into the grid below Asset Serial Details. | CONFIRMED | 8.1.8 i-iii |
| A15 | Shipment, Transfer Challans > Out Challan > Add Serial tab: only the grid indentation rule is given. | CONFIRMED | 8.1.8 second bullet |
| A16 | Shipment, Transfer Challans > Add Serial button > "Add Asset Serial" pop-up: Serial No. drop-down lists parents only; Add fetches extended assets. | CONFIRMED | 8.1.8 third bullet |
| A17 | In-Challan: Add Asset Serial pop-up follows the same rule. On successful acknowledgement, extended assets are also listed in the destination project/branch Global List, keep extended-asset behaviour and stay tagged to the parent. | CONFIRMED | 10.1.8 |
| A18 | Single Out Challan: rules apply for Add Asset Serial pop-up via Add Serial button, via Show Serial button, and the Add Serial tab. | CONFIRMED | 11.1.8 |
| A19 | The parent and active extended assets go to the destination in the same shipment/challan. S3: completing Shipment/Transfer/Single Out Challan for the parent also applies to all its children. | CONFIRMED | 8.1.11; 10.1.11; 11.1.11 |
| A20 | Hierarchy kept across Shipment Details pop-ups and Shipment Challans. | CONFIRMED | 8.1.11 |
| A21 | S3-only check: a child with Utilization Status Damaged/Stolen/Burned/Donated is blocked from Shipment and Challan transactions (that child only) until it is sold or written off; unaffected children and the parent stay eligible. Conflicts with the CR child-disposal rule (C13) that restricts the parent. | NEEDS_CLARIFICATION | S3 1.9, 1.11, 1.12, 1.14 vs 18.1.8, 21.1.8 (Q13, Q29) |
| A22 | S3-only check: if the parent is already disposed, a leftover bad-status child "disappears from normal transactions and can only be disposed through Sale/Write-Off". The CR says a parent disposal takes all active children with it, so how a child is left over is not explained. | NEEDS_CLARIFICATION | S3 1.9; Revision v1.6 (Q29) |
| A23 | S3 1.3-1.5: after HO addition the asset can be Assigned, Unassigned and Transferred at the Field Office. | CONFIRMED by S3 (secondary-only) | S3 |

### 6B. Indented list views (read-only displays)

Pattern for each row below: extended assets appear immediately below their parent; asset serial indented 4 spaces (S3: right-aligned/indented, parent left-aligned); no SL number on extended rows; no action button on extended rows where an action column exists; only active and not-merged extended assets shown. [CONFIRMED] (also confirmed per screen by S3 1.6-1.8, 1.10, 1.13, 1.15-1.18, 1.20, 1.21, 1.23, 1.24).

| Feature | Screen and place | Ref |
|---|---|---|
| F05 | Transaction List > Details (Assign/Unassign/Internal Movement), Asset Transaction Details pop-up | 5.1.2, 5.1.6, 5.1.8 |
| F06 | Transaction Approval List > Details | 6.1.2, 6.1.8 |
| F07 | Asset Assign Acknowledgement > Details column of Pending Asset Acknowledgement grid | 7.1.2, 7.1.6 |
| F09 | Asset Shipment Challan Approval List > shipment no. > Show Serial > Show Asset Serial pop-up (journey names the menu "Asset Shipment Approval List") | 9.1.2, 9.1.8 |
| F12 | Asset Single Out Challan Approval List > challan no. > Show Serial (text says "under Shipment Challan Details", probable copy-paste) | 12.1.2, 12.1.8 |
| F13 | Asset Single In-Challan > challan no. > Show Serial | 13.1.2, 13.1.8 |
| F14 | Asset Receivables List data grid | 14.1.8 |
| F15 | Asset Returnable List data grid | 15.1.8 |
| F16 | Asset Expenditure, List of Asset grid in Asset Expenditure Details pop-up | 16.1.7, 16.1.8 |
| F17 | Asset Expenditure Approval List, List of Asset grid | 17.1.8 |
| F19 | Asset Write-Off List, List of Asset grid | 19.1.7, 19.1.8 |
| F20 | Asset Write-Off Approval List, List of Asset grid | 20.1.8 |
| F22 | Asset Sale List, List of Asset grid | 22.1.7, 22.1.8 |
| F23 | Asset Sale Approval List, List of Asset grid | 23.1.7, 23.1.8 |

6B.1 [CONFIRMED] F05, F06, F07 acceptance adds "Only active extended assets must appear under the parent". F09, F12-F17, F19, F20, F22, F23 acceptance lists only indentation and no SL number.
6B.2 [CONFIRMED] F16: only assets with 'IN USE' status are shown (16.1.8 v; S3 1.17 repeats).
6B.3 [NEEDS_CLARIFICATION] F16: "no extended asset serial can be fetched if searched. Users can input expense for both asset and extended assets." S3 1.17 only verifies that the Asset Serial field never returns an extended asset, plus indentation and no SL; it does not cover expense entry for children (Q5).
6B.4 [INFERRED] The 4 space indentation is a rendering rule; in HTML leading spaces may need non-breaking spaces or CSS padding, so a test must check the rendered offset (section 13).
6B.5 [CONFIRMED] F16/F17 also carry the JSON reference data rule (F17 17.1.4 ii); see section 10.

### 6C. Disposal (Write-off F18/F19/F20, Sale F21/F22/F23)

| ID | Rule | Tag | Ref |
|---|---|---|---|
| C1 | One-by-one, Requirements text: the Asset Serial drop-down shows both parent and extended assets. The system checks whether the selected asset is parent or extended and does not allow both types in one request. Extended assets may be selected independently; a parent selection auto-includes all its extended assets. S3 1.19 and 1.22 agree on "either only the parent or only the child" and on auto-include for a parent. | CONFIRMED (Requirements and S3) | 18.1.8 i; 21.1.8 i; S3 |
| C2 | One-by-one, Acceptance text: the drop-down shows only parent assets and no extended asset. Conflicts with C1. | NEEDS_CLARIFICATION | 18.1.11; 21.1.11 (Q1) |
| C3 | Scope text differs: Write-off "user will not be able to select the extended assets"; Sale "user will be able to select the extended assets". S3 1.22 states that a child can be sold independently; S3 1.19 does not state the same for write-off. | NEEDS_CLARIFICATION | 18.1.4; 21.1.4 (Q1) |
| C4 | Bulk Excel, Requirements text: if the file has a parent, all its active extended assets must also be in the file; otherwise upload is blocked: "Invalid asset serial(s). Please correct the following data and upload again: [Parent Asset Serial] has missing extended/subsidiary asset(s)." Extended assets may also be uploaded individually. | CONFIRMED (Requirements) | 18.1.8 ii; 21.1.8 ii |
| C5 | Bulk Excel, Acceptance text: upload prevented if any extended asset is included; message lists the invalid extended serials. S3 1.19/1.22 agree with this version: "If a child/subsidiary asset is included in the upload file, the system shall reject it", message "Invalid asset serials. Please correct the following data and upload again: BBDSAR304823048 is a child/subsidiary asset." It conflicts with C4 (and the message wording differs). | NEEDS_CLARIFICATION | 18.1.11; 21.1.11; S3 (Q2) |
| C5a | Internal CR inconsistency: 18.1.8 and 21.1.8 also say that when a parent is selected "via Add button for One-by-One upload or via excel upload", the system fetches all associated extended assets into the Asset List. That implies a parent alone in the file is accepted and expanded, not rejected for missing children. | NEEDS_CLARIFICATION | 18.1.8 second bullet vs 18.1.8 ii (Q2) |
| C6 | Parent selected (one-by-one or Excel): all active extended assets fetched into the Asset List grid, indented, no SL number, no action button; removing the parent removes children. | CONFIRMED | 18.1.8; 21.1.8; 18.1.11; 21.1.11 |
| C7 | Parent and extended disposed together in the same transaction; they appear together downstream. | CONFIRMED | 18.1.11; 21.1.11 |
| C8 | A parent without extended assets can be disposed on its own. | CONFIRMED | Revision v1.6 |
| C9 | Individual disposal is allowed only for extended assets. Selecting a parent disposes the parent and all its extended assets together. | CONFIRMED | Revision v1.6 |
| C10 | To dispose an extended asset on its own, both the parent and the child must first be unassigned; afterwards the remaining assets may be reassigned. | CONFIRMED | Revision v1.6 |
| C11 | Independent extended-asset write-off/sale: the system considers Utilization Status other than "IN_USE" and Assigned status "Unassigned" (whose status is not said). Wider rule in C10 (parent and child unassigned). | NEEDS_CLARIFICATION | 18.1.8; 19.1.8; 20.1.8; 22.1.8; 23.1.8; Revision v1.6 (Q7) |
| C12 | Sale: an extended asset can be sold independently without selling the parent (S3 1.22 agrees). Write-off: the same (18.1.8). | CONFIRMED | 18.1.8; 21.1.8; S3 |
| C13 | Parent is restricted from Shipment/Challan/Disposal while an extended asset is in progress for disposal (utilization status changed or submitted for disposal). Revision text says "during child asset addition ... all applicable transactions". S3 narrows it to the affected child only (A21). | CONFIRMED (CR rule), NEEDS_CLARIFICATION (scope and S3 conflict) | 18.1.8 last bullet; 21.1.8 last bullet; Revision v1.6; S3 (Q13) |
| C14 | Sale gain/loss: full sale price allocated to the parent first and its gain/loss calculated; any remaining sale value distributed gradually to extended assets, gain/loss per child sequentially. | CONFIRMED | 21.1.8; 22.1.8; 23.1.8 |
| C15 | Worked example (same table in F21, F22, F23): Parent purchase 33000, WDV 33000, sale price 180000, gain/loss 147000; Extended 1 purchase 25000, WDV 1000, sale 0, gain/loss -1000; Extended 2 purchase 20000, WDV 2000, sale 0, gain/loss -2000. Gain/Loss = Sale price - WDV (F25S05). The example gives all 180000 to the parent, so no "remaining" value reaches children; the cap is unclear. | CONFIRMED (figures), NEEDS_CLARIFICATION (cap, Q14) | |
| C16 | Gain/loss for an independently sold child uses its own sale price and WDV. | INFERRED | F25S05 25.5.8 |
| C17 | Combined parent plus extended data is sent to the finance module through the Parent Asset Serial JSON reference at every write-off and sale. | CONFIRMED | 18.1.8; 20.1.8; 21.1.8; 23.1.4 |
| C18 | A disposed extended asset is no longer "active"; effect on the parent's reported Total Addition not stated. | UNKNOWN | none |

### 6D. The 16 reports in F25

Common rule for F25S02-F25S16 [CONFIRMED]: filters, UI and generation unchanged (Acceptance); the Parent Asset Serial is the primary identifier; extended values aggregated under the parent or group. Exceptions: F25S05, F25S06 show the child's serial when a child is disposed alone. S3 contains no report checks, so the report rules rest on the CR alone.

| # | Story, report | What changes | Columns / values (CR) | Output | Tag | Ref |
|---|---|---|---|---|---|---|
| 1 | F25S01 Asset Addition List (NEW) | New report; only parent assets that have one or more extended assets. | Filters: Report For (Head Office / Branch Office; Branch adds Division, Region, Area, Branch), Project, Department, Source of Fund, Employee Name & PIN, Asset Group, Category, Sub Category, Item Name, Utilization Status, Assign Status (all optional drop-downs). Submit, Reset. Columns: SL, Asset Serial (parent), RFID, Asset IMEI/SL No., Asset Name, Sub Category, Category, Group, Asset Purchase/Addition Date (parent/extended), Asset Registration Date, Project (code and name), Department (code and name), Current Location, Assign Status, Employee Name & PIN, Utilization Status, Purchase/Addition Price (parent or extended), Accumulated Depreciation, Written Down Value. Header: BRAC, Location, List of Asset Addition (Branch only); Project; Department (Head Office only); Source of Fund; As on Date. | Head Office: CSV (no PDF/Excel option). Branch Office: PDF (opens in another tab) or Excel via radio button. | CONFIRMED (structure); NEEDS_CLARIFICATION (extended rows, Q15) | 25.1.8 |
| 2 | F25S02 Asset List | Asset Serial always parent; extended serials not shown. | no new columns | unchanged | CONFIRMED | 25.2.8 |
| 3 | F25S03 Asset Register | Asset Serial parent; Total Addition, Total unit price, Accumulated Depreciation, WDV updated. | Total Addition = combined purchase of extended assets; Total unit price = Purchase Price + Total Addition; Acc. Dep. and WDV aggregated | unchanged | CONFIRMED | 25.3.8 |
| 4 | F25S04 Asset Schedule | Cost Value and Depreciation sections change. | Cost: Additions During the Period, Received from Branch/Project, Transfer to Branch/Project, Disposals During the Period, Closing Balance = Opening + Additions + Received - Transfer - Disposal. Depreciation: Charged During the Period, Received, Transfer, Disposals (Sale, Write Off, Backend Support), Closing = Opening + Charged + Received - Transfer - Disposal. Per asset group. | unchanged | CONFIRMED | 25.4.8 |
| 5 | F25S05 Asset Disposal Sale | Parent sale: parent serial and aggregated values; child alone: child serial and own values. | Asset Serial, Total unit price, WDV, Sale Price, Gain/Loss = Sale Price - WDV | unchanged | CONFIRMED | 25.5.8 |
| 6 | F25S06 Asset Write-off & Offline Transfer | Same logic for write-off. | Asset Serial, Total unit price, WDV, Sale Price (odd for write-off), Accumulated Depreciation | unchanged | CONFIRMED | 25.6.8 |
| 7 | F25S07 Asset Valuation | Per asset group. | Purchase Price (all parents in group), Total Addition, Total unit price, Accumulated Depreciation, WDV | unchanged | CONFIRMED | 25.7.8 |
| 8 | F25S08 Asset Transaction History | Asset Serial always parent. | none else | unchanged | CONFIRMED | 25.8.8 |
| 9 | F25S09 Asset Receivable | Asset Serial always parent. | none else | unchanged | CONFIRMED | 25.9.8 |
| 10 | F25S10 Asset Returnable | Asset Serial always parent. | none else | unchanged | CONFIRMED | 25.10.8 |
| 11 | F25S11 Asset Tracking | Asset Serial parent in UI and report; values aggregated; each addition shown as an event. | Total unit price, Acc. Dep., WDV aggregated; event format undefined | unchanged | CONFIRMED (rule), UNKNOWN (event format) | 25.11.8 |
| 12 | F25S12 Asset Registration | Same value updates as Asset Register. | Asset Serial parent, Total Addition, Total unit price, Acc. Dep., WDV | unchanged | CONFIRMED | 25.12.8 |
| 13 | F25S13 Asset Depreciation Statement (Serial wise) | Asset Serial parent. | Cost: Addition, Received, Disposals, Total = Opening + Additions + Received - Disposal. Depreciation: Charge, Receive, Disposal, Total, Written Down Value | unchanged | CONFIRMED | 25.13.8 |
| 14 | F25S14 Asset Depreciation Statement (Group wise) | Same, per asset group. | Same elements (numbering v-x is cosmetic) | unchanged | CONFIRMED | 25.14.8 |
| 15 | F25S15 Asset Depreciation History (Serial wise) | Parent plus extended aggregated. | Addition (Up-to Last Period; extended only, excludes parent cost), Addition (During the Period), Total Unit Price, WDV (Up-to last period), Acc. Dep. (Up-to Last period), Dep. (During the period), Acc. Depreciation, New WDV | unchanged | CONFIRMED | 25.15.8 |
| 16 | F25S16 Asset Depreciation History (Group wise) | Same, per asset group. | Same columns | unchanged | CONFIRMED | 25.16.8 |

6D.1 [UNKNOWN] Sample values, expected row counts, file names/layouts for the 16 reports (mock-ups omitted).
6D.2 [INFERRED] F01S01 1.1.6 lists four impacted reports; F25 lists 16. F25 is the wider list.
6D.3 [CONFIRMED] Menu path: Fixed Asset Module > Report > Asset Addition List (journey text also says "Select ... Asset List").

### 6E. F01 Global List and Asset Profile

| ID | Rule | Tag | Ref |
|---|---|---|---|
| E1 | On approval and execution in HOFIN, a new standalone asset is registered in the Global List (S3 1.1 checks this). | CONFIRMED | 1.1.8 |
| E2 | Serial format: parent serial plus hyphen plus number, e.g. BBDASRXXXXXX-1, BBDASRXXXXXX-2 (S3: ParentSerial-1, ParentSerial-2). | CONFIRMED | 1.1.8 i |
| E3 | Appears directly in the Global List and is searchable on its own. | CONFIRMED | 1.1.8 ii |
| E4 | Each addition generates a unique Asset Serial Number. | CONFIRMED | 1.1.8 iii; 1.1.11 |
| E5 | The extended asset's Asset Profile Details shows the parent's information. | CONFIRMED | 1.1.8 iv |
| E6 | New "Parent Asset" field holds the parent's serial; visible only on extended assets; not on the parent's own profile (S3 1.2 agrees). | CONFIRMED | 1.2.8 |
| E7 | New tab (named "Addition History" in requirements) is available only for parent assets. S3 1.2 says "Addition History tab is visible on asset's profile details" without restricting to parents. | CONFIRMED (CR); S3 wording ambiguous | 1.2.8 |
| E8 | Tab is visible for all parents even with no additions; the grid is then empty. | CONFIRMED | 1.2.8 |
| E9 | Records per page drop-down: 10, 20, 50, 100; default 10. | CONFIRMED | 1.2.8 i |
| E10 | Grid columns: SL; Asset Serial (hyperlink to the extended asset's Asset Profile Details; pop-up over pop-up; closing returns to the previous pop-up or page); Addition Amount; Addition Date (date of addition registration); Reference Number (posted voucher number from HOFIN); Item Name; Acc. Depreciation; WDV. S3 names the column "Reference No." | CONFIRMED | 1.2.8 ii a-h; S3 1.2 |
| E11 | Visual rule from S3 only: active children in the grid are blue and clickable; inactive children are black (clickability "to be confirmed"). The CR says only that the link works for "active" extended serials. | CONFIRMED by S3 (colours, secondary-only); UNKNOWN (inactive link behaviour) | 1.2.8 ii b; S3 1.2 |
| E12 | Entries-per-page text: range of entries in the page out of the total. Wording not given. | CONFIRMED (concept), UNKNOWN (wording) | 1.2.8 iii |
| E13 | Extended asset's Utilization Status can be updated independently without affecting the parent. | CONFIRMED (S3 1.2 agrees) | 1.2.8 |
| E14 | When the parent's Assign/Unassign Status or Utilization Status changes, the system synchronizes the same status to all associated extended assets, overriding their existing status (S3 1.2 agrees). | CONFIRMED | 1.2.8 |
| E15 | Parent unchanged by an addition (purchase value, WDV, remaining life time). | CONFIRMED | 1.1.8 |
| E16 | Pre-conditions: parent exists and is active; amount meets the capitalization threshold; registration done with the asset addition condition. | CONFIRMED | 1.1.5 |
| E17 | Profile pre-condition: addition acknowledged in HOFA and approved in HOFIN. | CONFIRMED | 1.2.5 |
| E18 | In HOFIN, the "Asset" drop-down of the initiation pop-up shows only parent serials. (S1: the "Fixed Asset Serial No" list shows parents only.) | CONFIRMED | 1.1.8; S1 |
| E19 | Tab name conflict: "Asset Addition" vs "Asset Addition History" vs "Addition History". | NEEDS_CLARIFICATION | 1.2.4 iii; 1.2.7; 1.2.8; 1.2.11 (Q4) |
| E20 | Numeric part of the hyphen suffix (sequence per parent, after a transfer) not described. | UNKNOWN | none |
| E21 | S3 check: Addition Amount, Addition Date and Asset Serial in the grid match what was entered/generated at creation. | CONFIRMED by S3 (secondary-only) | S3 1.2 |

### 6F. Asset Split restriction (F24)

| ID | Rule | Tag | Ref |
|---|---|---|---|
| F1 | The List of Global Asset Serial grid under Asset Split shows no extended assets. | CONFIRMED | 24.1.8 |
| F2 | On selecting a parent for split, the system checks for active extended assets. | CONFIRMED | 24.1.8 |
| F3 | With one or more active extended assets, the split is blocked; the message appears when the user clicks Split: "Cannot Split. Asset has associated asset extension." (S3 1.25 repeats the text.) | CONFIRMED | 24.1.8; 24.1.11; S3 |
| F4 | Otherwise the split follows the current process. A parent with only inactive extended assets can be split (INFERRED from "active"). | CONFIRMED / INFERRED | 24.1.8 |
| F5 | S3-only: on the Asset Split screen the Asset Purchase Price field shows the parent's purchase price; a "Child Asset" field shows all child assets separated by commas; "Total Addition Amount" = sum of addition amounts of all children. The CR does not list these fields (Revision v1.3 says the "additional field required in the asset split user story is removed"). Also, with a block in place it is unclear when these fields are shown. | NEEDS_CLARIFICATION | S3 1.25; Revision v1.3 (Q26) |

---

## 7. Validation messages

Exact texts given by the CR (and S2 for registration):

| # | Exact text | Where | Tag | Ref |
|---|---|---|---|---|
| M1 | "Asset addition is not allowed. Parent asset % is pending in another transaction flow." S3 example: "... Parent asset BBDASR000123 is pending ..." so % = parent serial. | HOFIN addition when parent (with or without extended assets) is pending in Assign, Unassign, Internal Movement, Transaction List, Transaction Approval List, Assign/Unassign Acknowledgement. | CONFIRMED (CR), CONFIRMED by S3 (placeholder) | 1.1.8; S3 1.1 |
| M2 | "Asset addition is not allowed under an extended asset. Reference Asset ID: %." S3 example: "... Reference Asset ID: BBDASR000123-1." so % = the extended serial the user chose. | HOFIN addition attempted under an extended asset. | CONFIRMED (CR), CONFIRMED by S3 (placeholder) | 1.1.8; S3 1.1 |
| M3 | "Invalid asset serial(s). Please correct the following data and upload again: [Parent Asset Serial] has missing extended/subsidiary asset(s)." Introduced as "a validation message such as" (indicative). | Write-off and Sale bulk Excel upload when a parent's children are missing. | CONFIRMED (CR Requirements), NEEDS_CLARIFICATION (conflict with M5, Q2) | 18.1.8; 21.1.8 |
| M4 | "Cannot Split. Asset has associated asset extension." | Asset Split on clicking Split with a parent that has active extended assets. | CONFIRMED (CR and S3) | 24.1.8; S3 1.25 |
| M5 | "Invalid asset serials. Please correct the following data and upload again: BBDSAR304823048 is a child/subsidiary asset." (the serial in the sample is S3's, and its prefix differs from BBDASR). | Write-off and Sale bulk Excel upload when a child serial is in the file. Matches CR Acceptance (message lists the invalid extended serials) but conflicts with M3 wording. | NEEDS_CLARIFICATION | S3 1.19, 1.22; 18.1.11; 21.1.11 (Q2) |
| M6 | "Transaction Submitted Successfully" | HOFIN success after Submit (registration; assumed identical for addition). | CONFIRMED (S2), INFERRED (addition) | S2 Step 9 |
| M7 | "Do you want to continue?You are confirming item information for the bill." (Yes / No) | HOFIN, after clicking Confirm in the Fixed Asset Details pop-up. | CONFIRMED (S1, S2) | S2 Step 8 |

Messages described but not worded:

| # | Situation | Tag | Ref |
|---|---|---|---|
| N1 | Extended serial typed in Assign/Unassign/Internal Movement: "selected asset not found" vs "cannot be selected for Asset <feature>". | NEEDS_CLARIFICATION | 2.1.8/2.1.11; 3.1.8/3.1.11; 4.1.8/4.1.11 |
| N2 | Extended serial typed/selected in Shipment, In-Challan, Single Out Challan. | UNKNOWN | 8.1.11; 10.1.11; 11.1.11 |
| N3 | HOFIN submission blocked because the parent is already in Transfer, Shipment, Write-off or Sale. | UNKNOWN | 1.1.8; 8.1.8 |
| N4 | Parent blocked from Transfer/Shipment/Write-off/Sale while an addition is pending HOFA acknowledgement or HOFIN approval. | UNKNOWN | 8.1.8 |
| N5 | Parent (or child) blocked from Shipment/Challan/Disposal because a child disposal is in progress or a child has Damaged/Stolen/Burned/Donated status. | UNKNOWN | 18.1.8; 21.1.8; S3 |
| N6 | Addition amount below the minimum capitalization threshold. | UNKNOWN | 1.1.5; S3 1.1 |
| N7 | Disposal of a child while parent or child is assigned or IN_USE. | UNKNOWN | 18.1.8; Revision v1.6 |
| N8 | One-by-one disposal where parent and extended assets are selected in the same request. | UNKNOWN | 18.1.8 i; 21.1.8 i; S3 |
| N9 | Reject/send-back messages for additions. | UNKNOWN | none |

---

## 8. Restriction matrix

### 8.1 Pending state or transaction on the parent -> blocks a new addition?

| Parent pending in | Blocks new addition (HOFIN)? | Tag | Ref |
|---|---|---|---|
| Asset Assign | Yes; M1 | CONFIRMED (also S3) | 1.1.8 |
| Asset Unassign | Yes; M1 | CONFIRMED (also S3) | 1.1.8 |
| Internal Movement | Yes; M1 | CONFIRMED (also S3) | 1.1.8 |
| Transaction List (pending Assign/Unassign/Movement) | Yes; M1 | CONFIRMED (also S3) | 1.1.8 |
| Transaction Approval List | Yes; M1 | CONFIRMED (also S3) | 1.1.8 |
| Asset Assign Acknowledgement | Yes; M1 (S3: "Asset Assign and Unassign Acknowledgement") | CONFIRMED | 1.1.8 |
| Transfer (Shipment) | Yes, at HOFIN submission; message missing | CONFIRMED (rule), UNKNOWN (message) | 1.1.8; 8.1.8 |
| Single Out Challan transfer | Same as Transfer | INFERRED | 11.1.8 |
| Write-off | Yes, at submission | CONFIRMED | 18.1.8 |
| Sale | Yes, at submission | CONFIRMED | 21.1.8 |
| Asset Expenditure / Expense | not mentioned | UNKNOWN | none |
| Asset Split in progress | not mentioned | UNKNOWN | none |
| Another pending addition on the same parent | not mentioned in CR; S3 says multiple additions are allowed under the same parent | UNKNOWN (pending at the same time), CONFIRMED by S3 (sequential) | Q9 |
| Extended asset itself (any state) | Addition under an extended asset blocked; M2 | CONFIRMED | 1.1.8 |
| Amount below capitalization threshold | Blocked (S3); CR lists it as a pre-condition | CONFIRMED | 1.1.5; S3 1.1 |
| Request from FOFIN / branch | Not possible (out of scope; S3: "cannot be performed from FOFIN") | CONFIRMED | Scope table; S3 |

### 8.2 Addition state -> blocks parent transactions

| Addition state | Transfer | Shipment | Write-off | Sale | Challan | Assign / Unassign / Movement | Tag | Ref |
|---|---|---|---|---|---|---|---|---|
| Pending HOFA acknowledgement | Blocked | Blocked | Blocked | Blocked | INFERRED blocked | UNKNOWN | CONFIRMED / INFERRED / UNKNOWN | 8.1.8; 10.1.8; 11.1.8; 13.1.8; 18.1.8; 21.1.8 |
| Acknowledged, pending HOFIN approval | Blocked | Blocked | Blocked | Blocked | INFERRED blocked | UNKNOWN | same | same |
| Approved | Not blocked by the addition (INFERRED) | | | | | | INFERRED | none |

### 8.3 Extended asset in disposal or bad status -> blocks parent or child

| Condition | Blocked | Tag | Ref |
|---|---|---|---|
| Extended asset in progress for disposal (utilization status changed, or submitted for disposal) | CR: the parent from Shipment, Challan, Disposal ("all applicable transactions" in the revision text) | CONFIRMED (rule), NEEDS_CLARIFICATION (list of blocked transactions) | 18.1.8; 21.1.8; Revision v1.6 |
| Child with Utilization Status Damaged/Stolen/Burned/Donated | S3: only that child is blocked from Shipment and Challan (until sold or written off); other children and the parent stay eligible | NEEDS_CLARIFICATION (conflicts with the row above) | S3 1.9, 1.11, 1.12, 1.14 (Q13, Q29) |
| Parent already disposed, bad-status child left | S3: child disappears from normal transactions; only Sale/Write-Off possible | NEEDS_CLARIFICATION | S3 1.9 (Q29) |
| Existing rule: Stolen or Offline-Transferred assets cannot be sold (domain file §7) | Interplay with a Stolen child's sale is not covered | UNKNOWN | domain file (read-only) |

### 8.4 Other blocks

| Rule | Tag | Ref |
|---|---|---|
| Parent with active extended assets cannot be split (M4). | CONFIRMED | 24.1.8 |
| No addition under an extended asset (M2). | CONFIRMED | 1.1.8 |
| Parent disposal with extended assets disposes all together. | CONFIRMED | Revision v1.6 |
| Extended asset disposal alone needs parent and child unassigned. | CONFIRMED | Revision v1.6 |
| Child cannot be moved to another parent (only disposal). | CONFIRMED by S3 only | S3 1.1 |

---

## 9. Auto-assignment rule

9.1 [CONFIRMED] If a parent asset has extended assets already assigned to an employee, a newly registered extended asset under the same parent is automatically assigned to that same employee through the asset assignment and asset transaction functionality. (F02 2.1.8)
9.2 [CONFIRMED] The system populates and records Employee Name, PIN, Building, Floor and Room from the existing assignment. (F02 2.1.8)
9.3 [CONFIRMED] If an asset is already assigned to an employee, any newly added extended asset is automatically assigned to the same employee via the asset transaction process; the system triggers both asset assignment and asset transaction approval automatically. (F02 2.1.8; Revision v1.4)
9.4 [NEEDS_CLARIFICATION] 9.1 requires "extended assets already assigned", 9.3 says "an asset already assigned". Behaviour when the parent is assigned but has no extended asset yet, or the parent is unassigned, is not stated (INFERRED: stays unassigned if parent is unassigned) (Q16).
9.5 [UNKNOWN] When the automatic assignment fires (HOFIN approval is INFERRED), whether employee acknowledgement is skipped, which user is the approver, what happens mid-acknowledgement (M1 would block the addition then). S3 has no check for auto-assignment.
9.6 [CONFIRMED] Parent and extended appear together in Transaction List, Transaction Approval List and Assign Acknowledgement (F02 2.1.11). Whether the automatic transaction appears there is not stated (INFERRED yes).
9.7 [CONFIRMED] Later parent Assign/Unassign status changes override children (E14).

---

## 10. Integrations and dependencies

| ID | Item | Tag | Ref |
|---|---|---|---|
| I1 | HOFIN origination: vendor bill payable with Fixed Asset Details. Branch offices cannot originate. | CONFIRMED | Scope table; F01S01; S1; S2 |
| I2 | HOFA acknowledgement and HOFIN approval pass the Transaction No. between modules. | CONFIRMED (S1, S2) | S1; S2 |
| I3 | HOFIN and HOFA environments must be connected and on the same business date, else the request is not visible in the HOFA Pending/Review List. | CONFIRMED (S2) | S2 Section 2 |
| I4 | HOFIN posted voucher number is shown in Addition History as "Reference Number"; delivery mechanism to Fixed Asset not described. | CONFIRMED (field), UNKNOWN (mechanism) | 1.2.8 ii e (Q11) |
| I5 | Fixed Asset sends combined accumulated parent plus extended data to finance via the Parent Asset Serial JSON reference for: Shipment (F08, F09, F10), Single Out Challan (F11, F12), Single In-Challan (F13), Asset Expenditure approval (F17), Write-off (F18, F20), Sale (F21, F23). F16, F19, F22 do not repeat it. | CONFIRMED | listed refs |
| I6 | JSON structure, finance endpoint and failure/retry behaviour not described. | UNKNOWN | none |
| I7 | JV expectations from S3: JV generated for the new asset after addition; parent's JV unaffected; JV generated after Shipment/Transfer/Single Out Challan with children. Content (accounts, amounts) not described. | CONFIRMED by S3 (check exists), UNKNOWN (content) | S3 1.1, 1.9, 1.11 |
| I8 | In-Challan receive: extended assets are added to the destination Global List, tagged to the parent. | CONFIRMED | 10.1.8 |
| I9 | Minimum capitalization threshold defined per asset group (value not in CR). | CONFIRMED (existence) | 1.1.9 |
| I10 | Dependency on the parent registration flow: parent must exist, be active, and carry the addition condition. | CONFIRMED | 1.1.5 |
| I11 | Report generation depends on branch hierarchy (Division, Region, Area, Branch) as in the existing Branch Office report call. | CONFIRMED | 25.1.8 i |
| I12 | Depreciation: calculated separately for parent and child (S3 1.27); rate/method/start date not described. | CONFIRMED by S3 (separate), UNKNOWN (details) | S3 |
| I13 | Legacy "Asset Addition from Inventory / from Vendor" sub-screens (domain file) are not mentioned in the CR or S3. | NEEDS_CLARIFICATION | domain file; CR silent (Q19) |

---

## 11. Dependencies on existing screens and automation

Mapping by file name only (files not opened or modified). "gap" = no matching file found.

| CR feature | Screen | Page class (`automation/pages`) | Element catalog (`automation/element_catalog`) | Tag |
|---|---|---|---|---|
| Addition flow (HOFIN + HOFA + approval) | HOFIN Vendor Bill Payable, HOFA Asset Registration Pending/Review, HOFIN Approval | asset_registration_aaq_page, asset_registration_list_page, asset_registration_approval_list_page, asset_in_pending_process_list_page, login_page, voucher_search_page | asset_registration_aaq, asset_registration_list, asset_registration_approval_list, asset_in_pending_process_list, voucher_search | INFERRED |
| F01 | Asset Serial Global List, Asset Profile Details | asset_serial_global_list_page | asset_serial_global_list, asset_profile_reference_values | CONFIRMED (file exists) |
| F02 | Asset Assign | asset_assign_page (plus asset_transaction_form_page, transaction_grid_page) | asset_assign | INFERRED |
| F03 | Asset Unassign | asset_unassign_page | asset_unassign | INFERRED |
| F04 | Internal Movement | asset_internal_movement_page | asset_internal_movement | INFERRED |
| F05 | Transaction List | transaction_list_page | transaction_list | INFERRED |
| F06 | Transaction Approval List | transaction_approval_list_page | transaction_approval_list | INFERRED |
| F07 | Asset Assign Acknowledgement | asset_assign_acknowledgement_page | asset_assign_acknowledgement | INFERRED |
| F08 | Asset Shipment | asset_shipment_page, shipment_challan_page, gate_pass_page | asset_shipment, asset_gate_pass_generation | INFERRED |
| F09 | Shipment Challan Approval List | shipment_challan_approval_page | asset_shipment_challan_approval_list | INFERRED |
| F10 | Shipment In-Challan | shipment_in_challan_page | asset_shipment_in_challan | INFERRED |
| F11 | Single Out Challan | single_out_challan_page, single_gate_pass_page | asset_single_out_challan, asset_single_challan_gate_pass | INFERRED |
| F12 | Single Out Challan Approval List | single_out_challan_approval_list_page | asset_single_out_challan_approval_list | INFERRED |
| F13 | Single In-Challan | single_in_challan_page | asset_single_in_challan | INFERRED |
| F14, F15 | Receivables / Returnable List | single_challan_list_page (probable) | none dedicated | gap, INFERRED |
| F16 | Asset Expenditure | asset_expense_page | asset_expense | INFERRED |
| F17 | Asset Expenditure Approval | asset_expense_approval_page | asset_expense_approval | INFERRED |
| F18 | Asset Write-Off | asset_write_off_page | asset_write_off | INFERRED |
| F19 | Write-Off List | asset_write_off_list_page | asset_write_off_list | INFERRED |
| F20 | Write-Off Approval List | asset_write_off_approval_list_page | asset_write_off_approval_list | INFERRED |
| F21 | Asset Sale | asset_sale_page | asset_sale | INFERRED |
| F22 | Asset Sale List | asset_sale_list_page | asset_sale_list | INFERRED |
| F23 | Asset Sale Approval List | asset_sale_approval_list_page | asset_sale_approval_list | INFERRED |
| F24 | Asset Split (S3 also: Asset Serial Split Approval List) | asset_serial_split_page, asset_split_view_popup, asset_serial_split_list_page, asset_serial_split_approval_list_page | asset_serial_split, asset_serial_split_list, asset_serial_split_approval_list | INFERRED |
| F25 (16 reports) | Fixed Asset > Report | none | none | gap |
| Bulk Excel upload (Write-off, Sale) | upload on write-off/sale pages | check asset_write_off_page / asset_sale_page | asset_write_off, asset_sale | UNKNOWN |

11.1 [INFERRED] Existing automation covers parent flows; new checks mostly extend existing page classes. Report screens and the HOFIN addition pop-up (Bill, checkbox, parent serial) need exploration. Note for the later automation track only.
11.2 [CONFIRMED] S1 relies on a chained register -> read serial -> add flow; `asset_serial_number` is read at run time from the Global List.

---

## 12. Open questions and conflicts for human review

| # | Question | Ids | Suggested default |
|---|---|---|---|
| Q1 | Write-off/Sale one-by-one drop-down: Requirements say parent AND extended listed (extended alone allowed, never mixed with a parent); Acceptance says parent only. Scope: Write-off "will not select extended", Sale "will select extended". S3 supports "either parent only or child only in one request". | 18.1.4, 18.1.8 i, 18.1.11; 21.1.4, 21.1.8 i, 21.1.11; S3 1.19, 1.22 | Requirements and S3: drop-down shows both; extended alone allowed (C10/C11 conditions); parent auto-includes children; mixed request rejected. |
| Q2 | Bulk Excel: CR Requirements say a parent must come with all children else reject (message M3); CR Acceptance and S3 say reject if any child is in the file (message M5: "... X is a child/subsidiary asset."). CR also says a parent selected "via excel upload" gets its children fetched (C5a). Which rule, which exact message, and is a child-only file ever accepted? | 18.1.8 ii, 18.1.11, 21.1.8 ii, 21.1.11; S3 1.19, 1.22 | Treat the CR text as primary: M3 for parent with missing children; child-only upload accepted only if independent-disposal conditions hold. But two of three sources prefer "reject children", so the owner must choose. |
| Q3 | Typing an extended serial in Assign/Unassign/Internal Movement: "selected asset not found" (Requirements) vs "cannot be selected" (Acceptance); exact text missing. No text for Shipment, In-Challan, Single Out Challan. S3 gives none. | 2.1.8/2.1.11; 3.1.8/3.1.11; 4.1.8/4.1.11; 8.1.11; 10.1.11; 11.1.11 | Requirements: extended not returned by search, "selected asset not found"; ask for exact wording. |
| Q4 | Tab name: "Asset Addition" (scope), "Asset Addition History" (mock-up), "Addition History" (requirements, acceptance, S3 title mixes). | 1.2.4, 1.2.7, 1.2.8, 1.2.11 | "Addition History". |
| Q5 | Expenditure: "no extended asset serial can be fetched if searched" yet "users can input expense for both asset and extended assets". Is expense entered per child row? S3 does not cover it. | 16.1.8 iv | Search returns parents only; expense entered on parent and child rows. |
| Q6 | F17 Impacted Areas says "Asset Sale Approval List". | 17.1.6 | Typo; scope is Asset Expenditure Approval List. |
| Q7 | v1.6 child-disposal rule: parent AND child unassigned first, vs F18/F19/F20/F22/F23 "Utilization Status other than IN_USE and Unassigned" (no mention of the parent). Whose status, and what message when it fails? | Revision v1.6; 18.1.8; 19.1.8; 20.1.8; 22.1.8; 23.1.8 | Both parent and child unassigned (v1.6); child not IN_USE; no message defined. |
| Q8 | Does the HOFIN pop-up Asset drop-down hide assets in pending states, or does M1 appear on selection/submit? When is M2 reachable if extended assets are hidden? | 1.1.8 | Drop-down shows all active parents; blocks fire on selection or submission; M2 only on a manually entered extended serial. |
| Q9 | Several additions for the same parent: S3 says multiple children are allowed, but may a second addition be submitted while the first is pending in HOFA/HOFIN? Serial numbering order? | 1.1.8; 8.1.8; S3 1.1 | One pending addition per parent at a time; numbering in approval order. |
| Q10 | Meaning of "merged" in "active and not merged extended assets"; what makes an extended asset inactive? | 2.1.12; 3.1.12; 4.1.12; 5.1.12; 6.1.12; 7.1.12; 8.1.12; 9.1.12 | Active = not disposed; do not test "merged" until defined. |
| Q11 | How the Addition History "Reference Number" (HOFIN posted voucher) reaches Fixed Asset, when it is populated, and what the title "with Reference Number" refers to. S3 calls the column "Reference No." | 1.2.8 ii e; Title; S3 1.2 | Voucher number posted at HOFIN approval, shown after approval. |
| Q12 RESOLVED 2026-10-10 (user: HOFIN -> HOFA acknowledge -> HOFIN approve, for registration and addition) | Workflow direction: user said "approval in HOFA, acknowledgment in HOFIN"; the CR, S1 and S2 say HOFA acknowledges and HOFIN approves. | 1.2.5; 8.1.8; 10.1.8; 11.1.8; 13.1.8; 18.1.8; 21.1.8; S1; S2 | CR/S1/S2 version. Confirm with the user. |
| Q13 | Child-disposal lock scope: CR blocks the PARENT from Shipment/Challan/Disposal (revision: "all applicable transactions") while a child is in disposal; S3 blocks only the AFFECTED CHILD (Damaged/Stolen/Burned/Donated) from Shipment/Challan while parent and other children stay eligible. Does the lock also block a new addition? Are Transfer, Assign/Unassign, Movement, Expense included? What counts as "in progress"? | 18.1.8; 21.1.8; Revision v1.6; S3 1.9, 1.11, 1.12, 1.14 | CR version (parent blocked from Shipment, Single Out Challan, Write-off, Sale, and new additions); get the owner's ruling because the two sources differ. |
| Q14 | Sale allocation: example gives the full 180000 to the parent (gain 147000) and 0 to children. Is the parent allocation capped (WDV or purchase price) with the rest going to child 1 then 2? What if the sale price is below the parent's WDV? | 21.1.8; 22.1.8; 23.1.8 | The example is the only data: all to parent, 0 to children, gain/loss = sale price - WDV. |
| Q15 | Asset Addition List report: "only parent assets" but some columns are "parent/extended". Are extended assets separate rows? Actor "Authorized HO User" vs Branch Office option; journey text vs menu name. | 25.1.3; 25.1.8 | One row per extended asset under its parent; ask for the mock-up. |
| Q16 | Auto-assignment trigger: "extended assets already assigned" vs "an asset already assigned"; parent assigned with no earlier child; timing; acknowledgement skipped; approver recorded. | 2.1.8 | Triggered at addition approval when the parent is assigned; Employee, PIN, Building, Floor, Room copied. |
| Q17 | Minimum capitalization threshold: value per asset group, where checked (HOFIN on submit), failure message. | 1.1.5; 1.1.9; S3 1.1 | On-screen error at submission; message unknown. |
| Q18 | Which pending transactions block a new addition: 1.1.8 lists Assign, Unassign, Movement, Transaction List, Approval List, Acknowledgement (M1) while F08/F10/F11/F13/F18/F21 list Transfer, Shipment, Write-off, Sale (no message). Is M1 reused? Are Expenditure, Split, Single Out Challan included? | 1.1.8; 8.1.8 etc. | Treat both lists as blocking; reuse M1. |
| Q19 | Legacy "Asset Addition from Inventory/Vendor" screens and existing assets with merged additions: changed or unchanged? | Scope; domain file | Unchanged, out of scope. |
| Q20 | Rejected/sent back/cancelled addition: which locks apply? | none | Locks released. |
| Q21 | Reports: after a child is disposed alone, does the parent's Total Addition drop it? Format of the "event" for each addition in the Tracking Report? Is the "Sale Price" column in the Write-off & Offline Transfer report intended? | 25.3.8; 25.6.8; 25.11.8 | Exclude disposed children from active totals; tracking event format needs the owner. |
| Q22 | Parent-to-extended status override: do all children (including disposed or independently DAMAGED ones) change when the parent changes? Does a parent change to non-IN_USE start the child-disposal lock? | 1.2.8; 18.1.8 | Override only active children. |
| Q23 | Roles and permissions for create/acknowledge/approve; can creator and approver be the same user? | none | Three distinct users as in S1. |
| Q24 | Addition History: inactive extended asset row (S3: black, clickability "to be confirmed"; CR: link only for active) and entries-per-page wording. | 1.2.8; S3 1.2 | Blue and clickable for active, black and not clickable for inactive. |
| Q25 | At which step does the extended asset first appear in the Global List (HOFA acknowledgement or HOFIN approval)? | 1.1.8; 1.2.5 | After HOFIN approval. |
| Q26 | Asset Split screen: S3 expects fields Asset Purchase Price (parent), Child Asset (comma list) and Total Addition Amount; CR does not list them (and v1.3 removed an "additional field"). Which is correct, and how is it visible when split is blocked? | 24.1.8; Revision v1.3; S3 1.25 | CR text only (message M4 on click Split); treat S3 fields as unconfirmed. |
| Q27 URLs RESOLVED 2026-10-10 (hofin42 / env42; connection + business date still to verify) | Test environment: S2 uses hofinstaging.brac.net and erpstaging.brac.net; project_config uses erpstaging.brac.net; S1 uses hofin42/env42.erp.bracits.net. Which HOFIN-HOFA pair is connected and on the same business date for FAHOV2-643? | S1; S2; project_config.yaml | Use the pair that S2's SQL check shows as connected; confirm. |
| Q28 | S3 asks "whether a new serial ID is generated when an Asset Split is approved" (twice, under Split Approval List and Depreciation) and wants separate depreciation per parent and per child. Answers and depreciation parameters are not in the CR. | S3 1.26, 1.27 | UNKNOWN; owner to answer. |
| Q29 | Leftover child after the parent is disposed (S3): the CR disposes all active children with the parent, so which children can be left (inactive? bad status excluded from the auto-include)? | S3 1.9; Revision v1.6 | Ask the owner; no default. |
| Q30 | S3: "a child asset cannot be reassigned to a different parent; if this were to happen, the only resolution is disposal". Is there any re-parenting action, or is this only a negative check? | S3 1.1 | Negative check only: no UI to re-parent. |
| Q31 | JV expectations (account lines, amounts) for addition, shipment/challan with children, and for parent JV "no unintended impact". | S3 1.1, 1.9, 1.11 | UNKNOWN; owner to supply JV samples. |

---

## 13. Testability notes

UI-verifiable (HOFIN and HOFA screens):
- 13.1 Global List: new serial `<parent>-<n>` after HOFIN approval; Parent Asset field only on extended assets; Addition History tab only on parents; records per page 10/20/50/100 (default 10); grid columns; active link blue and clickable, inactive black; pop-up over pop-up and return to the previous pop-up; empty tab for parents with no additions; grid values match the addition data. [UI]
- 13.2 Synchronization: change the parent's Utilization Status and Assign status and see children follow; change a child's Utilization Status and see the parent unaffected. [UI]
- 13.3 Selection screens: extended serial absent from search and drop-down; search by serial and by PIN; auto-included rows indented, no SL, no action button; removing the parent removes children; Delete/Action button only on the parent row; exact message wording needed first (Q3). [UI]
- 13.4 Indented list views (14 features): children directly under the parent, no SL, no action button, 4 space offset (check leading whitespace or CSS padding; a visual check alone is weak). [UI]
- 13.5 Pending-state restrictions: UI shows whether the parent is rejected in Transfer/Shipment/Write-off/Sale while an addition is pending; exact messages unknown (N3-N5). Needs controlled states: addition pending HOFA acknowledgement; addition acknowledged and pending HOFIN approval. [UI, messages UNKNOWN]
- 13.6 HOFIN submit-time blocks: M1, M2, threshold, parent already in Transfer/Shipment/Write-off/Sale, and confirmation that FOFIN cannot add. [UI in HOFIN]
- 13.7 Split block and M4. [UI]
- 13.8 Auto-assignment after HOFIN approval: Employee, PIN, Building, Floor, Room in Global List and Transaction List. [UI]
- 13.9 Disposal: parent with children, child alone, parent without children, mixed selection rejected, bulk Excel (prepared files; M3 vs M5 conflict, Q2), gain/loss example (33000/25000/20000 with 180000). [UI plus file preparation]
- 13.10 Shipment/In-Challan: destination Global List shows children after In-Challan acknowledgement (needs a second branch/project login); Assign/Unassign/Transfer at Field Office after HO addition (S3 1.3-1.5). [UI, multi-login]
- 13.11 Bad-status child checks (S3): need child with Damaged/Stolen/Burned/Donated while the parent and siblings stay IN_USE; expected result depends on Q13. [UI, blocked until Q13]

Environment pre-conditions (new from S2):
- 13.12 Before any HOFIN -> HOFA test: confirm the connected HOFA environment and the same business date on both (S2 SQL check on `configuration`). Wrong pairing makes the request invisible in the Pending/Review List and produces false failures. Target URLs undecided (Q27). [Setup]
- 13.13 Transaction No. is only generated after Add in Bill Allocation Details; Fixed Asset Details button appears after that; success text "Transaction Submitted Successfully". [UI]

Not (or hardly) UI-verifiable:
- 13.14 Finance module receiving combined data through the Parent Asset Serial JSON reference (I5/I6) and Journal Voucher generation (I7): visible only through finance posting, vouchers or API/DB; structure and expected lines undefined. [Integration only]
- 13.15 The 16 reports: download and read the file (CSV for Head Office, PDF/Excel for Branch) and compare with Global List numbers; no catalog or page class yet; S3 contains no report checks. [File content]
- 13.16 Reference Number mechanism, separate depreciation values, JV content: not defined (Q11, Q28, Q31). [UNKNOWN]
- 13.17 Reject, send-back, threshold value, concurrent additions, re-parenting: not testable until Q9, Q17, Q20, Q30 are answered.
- 13.18 Mapping gap: S1 and S2 cover the registration/addition flow; the controls "Bill Allocation drop-down" and "Fixed Asset Addition" checkbox appear only in S1, not in the CR or S2. [INFERRED mapping]
- 13.19 Test data need: a parent with at least 2 extended assets (one with a changed Utilization Status), an assigned parent, a branch with In-Challan receipt, a parent with a pending Assign (for M1), an extended asset serial (for M2), and Excel templates for bulk disposal.

Note: no test case, code or CHANGELOG change was made. Next step: human review of section 12.


## Live findings 2026-10-10 (HOFIN -> HOFA -> HOFIN run on hofin42/env42, automation test_32)
- [CONFIRMED LIVE] Q4: the parent popup tab is named "Addition History" (not "Asset Addition"). The extended asset popup has a Parent Asset field (`parentAssetSerial`) and no Addition History tab (F01S02).
- [CONFIRMED LIVE] F01S01: after HOFIN approval a separate asset `<parent>-1` is listed in the Asset Serial Global List, UNASSIGNED / IN_USE; the parent row is unchanged. The HOFIN "Fixed Asset Serial No" search lists the parent serial only.
- [CONFIRMED LIVE] Addition History columns: SL, Asset Serial (link), Addition Amount, Addition Date, Reference Number (journal voucher number, JV...), Item Name, Acc. Depreciation, WDV, plus Impairment Status and Impairment ID (impairment was removed in CR v1.5 but the columns are still shown: report to the BA).
- [CONFIRMED LIVE] Workflow: HOFIN submit -> HOFA acknowledge (PENDING -> ACKNOWLEDGED) -> HOFIN approve (APPROVED in both applications). A fixed asset A/C code needs an amount of 20000 or more (may be the capitalization threshold of Q17: to confirm; no failure text seen).
- [OBSERVED] HOFIN approval screen shows no toast after Approve; the APPROVED row appears after the list is opened again.

## Live findings 2026-10-10 — Asset Assign (F02) and its follow-up screens (automation test_33, 8 passed)
- [CONFIRMED LIVE] Q3 (Assign): an extended serial typed in Asset Assign gives the toast "No asset found" and no suggestion (Requirement text "selected asset not found"; the Acceptance wording "cannot be selected" is not what the screen shows). Shipment, challan, Unassign and Internal Movement not yet checked.
- [CONFIRMED LIVE] F02: the parent search offers the parent only; Add to Grid lists the extended asset directly below it (4 leading spaces, no SL number, no action button); deleting the parent removes both; Submit and Approve assign both (ASSIGNED in the Global List).
- [CONFIRMED LIVE] F06 and F07: the Details popups of the Transaction Approval List and of the Asset Assign Acknowledgement list the extended asset below the parent with the same indentation and no SL number.
- [OBSERVED] The extended asset's row in the Assign list shows the HOFIN bill text in Note/Remarks.
- [OBSERVED] HOFA answers "You have to select a Asset first" when Acknowledge of a registration request is clicked before its details have loaded.

## Live findings 2026-10-10 — Asset Assign (F02) completed (automation test_33: 16 tests)
- [CONFIRMED LIVE] Inactive extended asset (CR F02 exception): an extended asset that is written off becomes inactive: it disappears from the Asset Serial Global List, cannot be found in Asset Assign ("No asset found") and is not brought in by its parent (Asset List, Draft Details popup).
- [CONFIRMED LIVE] Q1 (Write-off dropdown): the Asset Serial box of Asset Write-off lists an extended asset on its own when its Utilization Status is not IN_USE; its parent (IN_USE) is not offered. An extended asset is written off independently of its parent (CR F18 requirement version).
- [CONFIRMED LIVE] F02 auto-assign: an extended asset added to an assigned parent is assigned automatically to the same employee with the parent's Building, Floor and Room (checked on the asset popup). Not checked: whether a separate approved transaction record is created.
- [CONFIRMED LIVE] Several extended assets: all active ones are listed below the parent in order. The Draft path (Draft, Transaction List Details, Submit from the list, Approve) and Acknowledge cover the parent and its active extended assets.
- [OBSERVED] Internal Movement and Un Assign do not offer an asset whose assignment still waits for acknowledgement.
- [OBSERVED] The ERP allows one session per user: a second login of the same account ends the first. The Assign user, TEST user and HOFA acknowledger are the same account, so flows and tests log out when they finish.
