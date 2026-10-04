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
