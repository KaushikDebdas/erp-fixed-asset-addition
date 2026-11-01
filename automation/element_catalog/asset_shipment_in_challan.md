# Asset Shipment In-Challan/Memo List — element catalog

| Field | Value |
|---|---|
| Page class | not yet built |
| Module / menu path | Fixed Asset >> Asset Transfer >> Asset Shipment In-Challan |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransfer/showInChallan` (reach it by clicking the menu) |
| Role needed | employee `00015370` (same branch as the sender, so one login did the whole transfer) |
| Last explored | 2026-10-04 (live; one challan was acknowledged) |
| Screenshot | none taken; values read from the live page |

## Filters and grid
- Filters: Out Challan No `#outChallanNo`, In Challan No `#inChallanNo`, Sending Branch `#fromOffice`, To Project `#toProject`, Created By `#createdBy`, Acknowledged By `#acknowledgedBy`, From/To Date `#fromDate`, `#toDate`, Challan Status `#challanStatus` (offers only **APPROVED** and **ACKNOWLEDGED**), To Department `#toDepartment`, Approved By `#approvedBy`; Search, Reset `#resetUpdate`.
- Grid `#challanListTable`: SL, ID, Out Challan No., In Challan No, In Challan Date, Sending Branch, Receiving Branch, From Project, From Department, To Project, To Department, Created By, Approval Date, Approved By, Acknowledged By, Challan Status, ShipmentId, Preview.
- Right after the shipment was approved the challan was listed with an **In Challan No already filled** (`IC-BBDSHP00000009-BBDICH00000102`), Status **APPROVED**, In Challan Date empty, Acknowledged By empty and **nothing in the Preview cell** (no action yet).

## Challan popup and Acknowledge
- The Out Challan No link opens `#inChallanDetailsModal` with the same read-only fields as the approval popup (In Challan No filled). Its only actions are **Acknowledge** `#acknowledge` and Close. (The popup has a Details tab only.)
- After clicking Acknowledge the row shows Status **ACKNOWLEDGED**, In Challan Date (`20/09/2026`), Acknowledged By (the user) and a **Preview** link (`printChallan(594,827)`). **The success toast was not captured** (nothing appeared in `.toast-message` for 7 seconds) and the popup stayed open. NEEDS CHECK on the next challan: the exact acknowledgement message.

Not explored: acknowledgement by a user of a different receiving branch, the Preview report, filters and paging.

## Receiving-branch user (explored 2026-10-14, user 126060 at `[BO - 0233] Chagalnaiya`)
Screenshot: `evidence/shipment_in_challan_receiving_user.png`.
- The user has the menus Asset Shipment, Asset Shipment Challan Approval List, **Asset Shipment In-Challan**, Gate Pass Generation, the Single Challan screens, Asset Receivable List and Asset Returnable List.
- The In-Challan list is limited to the user's own office: it showed one row, `OC-BBDSHP00000034-644` / `IC-BBDSHP00000034-BBDICH00000123`, Sending Branch `[HO - BDHO] Head Office`, Receiving Branch `[BO - 0233] Chagalnaiya`, From Project and To Project both `[015] Microfinance (Dabi)`, created and approved by employee 15370, Challan Status **APPROVED** (not yet acknowledged). So a cross-branch challan with the same project reaches the receiving branch's list once the shipment is approved.
- The Sending Branch filter `#fromOffice` is a text box, not a dropdown.
- Accounting day for this user's office: `Accounting Date : 20-09-2026 [DAY CLOSED]`. Acknowledging while the day is closed was NOT tried (the row was left untouched).
- Not yet seen: the acknowledgement by this user, and whether the sending branch's user can acknowledge a cross-branch challan.

## Acknowledge by the receiving branch's user (2026-10-15)
- Tests: `test_20_asset_shipment_in_challan.py`, `test_different_branch_{same,different}_project_receiving_user_acknowledges_the_challan`; the receiving user is `ACK_SHIPMENT_ERP_*` in `.env` (user 126060 at `[BO - 0233] Chagalnaiya`).
- Result: the click on **Acknowledge** was refused with the toast **`Business day not open for Fixed Asset.`**; the row stayed APPROVED (challans `OC-BBDSHP00000047-660`, `OC-BBDSHP00000048-661`). The Accounting Date of that office showed `[DAY CLOSED]`.
- The Accounting Date box is `#sessionBusinessDateReload` (see `dashboard_page.md`).
- NOT YET SEEN: the acknowledgement of a branch-to-branch challan on an open day (message, ACKNOWLEDGED, Preview link, vouchers).
