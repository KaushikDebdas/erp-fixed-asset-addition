# Asset Shipment Challan/Memo Approval List — element catalog

| Field | Value |
|---|---|
| Page class | not yet built |
| Module / menu path | Fixed Asset >> Asset Transfer >> Asset Shipment Challan Approval List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransfer/showShipmentChallanApprovalList` (reach it by clicking the menu) |
| Role needed | employee `00015370` (also approved his own challan: no separate approver was needed) |
| Last explored | 2026-10-04 (live; one challan was approved) |
| Screenshot | none taken; values read from the live page |

## Filters and grid
| # | Element | Locator | Status |
|---|---|---|---|
| 1 | Out Challan No / Shipment No | `#outChallanNo`, `#shipmentNo` | VERIFIED |
| 2 | From Project / From Department | `#fromProject`, `#fromDept` | VERIFIED |
| 3 | Approval Status: PENDING, APPROVED, REJECTED, ACKNOWLEDGED, SENDBACK | `#challanStatus` | VERIFIED |
| 4 | Created By / Approved By (employee search, Created By starts empty) | `#createdBy`, `#approvedBy` | VERIFIED |
| 5 | Receiving Branch / To Project / To Department | `#toOffice`, `#toProject`, `#toDepartment` | VERIFIED |
| 6 | Approval From / To Date (read-only, calendar) | `#fromDate`, `#toDate` | VERIFIED |
| 7 | Search / Reset | `get_by_role("button", name=" Search")`, `#resetUpdate` | VERIFIED |
| 8 | Grid `#challanListTable`: SL, (id), Out Challan No., Shipment Number, From Project, From Department, Sending Branch, Receiving Branch, To Project, To Department, Created By, Approval By, Approval Date, Challan Status, ShipmentId, Preview. The list held 102 challans (other people's too). | `#challanListTable` | VERIFIED |
| 9 | Out Challan No link: opens the popup (`showAssetChallanDetailsPopup`) | `get_by_role("link", name=<number>, exact=True)` | VERIFIED |
| 10 | **Preview** link: appears on an APPROVED row (`printChallan(594,827)`) | link in the last cell | VERIFIED that it appears; what it opens is NOT yet checked |

## Challan popup (`#inChallanDetailsModal`)
- Read-only fields: `#inChallanNoDetails`, `#inChallanDateDetails`, `#outChallanNoDetails`, `#outChallanDateDetails`, `#fromProjectDetails`, `#toProjectDetails`, `#challanStatusDetails`, `#fromBranchDetails`, `#toBranchDetails`, `#challanCreatedByDetails`, `#challanApprovalDateDetails`, `#challanApprovedByDetails`, and the item grid `#assetItemsInChallanTableDetails`.
- Comment box `#challanCommentNew` ("Leave comment here...") and `#challanCommentDate`.
- Actions: **Approve** `#approveChallan`, **Reject** `#rejectChallan`, **Sendback** `#sendBackChallan`, Close. (Unlike the Asset Registration Approval List, all three actions exist here.)
- **Show Serial** link in the item row opens a second popup `#addAssetSerialShipmentChallanModal` ("Show Asset Serial") with the table `#assetSerialAdditionShipmentChallanTable` (Asset Serial, Item Name, Sub Category, Category, Disposal, Maintenance). A loading overlay (`.modalLoader`) covers the screen for a moment after the click; wait for it to disappear before clicking Close.
- **Approve** (with a comment typed): toast **`Challan approved successfully.`**; the popup closes; the row shows APPROVED, Approval By (the approver) and Approval Date (`20/09/2026`, the business date).

Not explored: Reject and Sendback outcomes, the Preview report, filters and paging.
