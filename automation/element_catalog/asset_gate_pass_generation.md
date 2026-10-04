# Gate Pass Generation List — element catalog

| Field | Value |
|---|---|
| Page class | not yet built |
| Module / menu path | Fixed Asset >> Asset Transfer >> Gate Pass Generation (the Single Challan menu has a page with the same name) |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetGatePassGeneration/show` (reach it by clicking the menu) |
| Role needed | employee `00015370` |
| Last explored | 2026-10-04 (live, read only plus one Preview click) |
| Screenshot | none taken; values read from the live page |

## Filters and grid
- Filters: Out Challan No `#outChallanNo`, From Project `#fromProject`, From Department `#fromDept`, From/To Date `#fromDate`, `#toDate`, Receiving Branch `#toOffice`, To Project `#toProject`, To Department `#toDepartment`, Status `#challanStatus`, Created By `#createdBy`, Approved By `#approvedBy`; Search, Reset `#resetUpdate`.
- Grid `#challanListTable` columns: ID, SL, Out Challan Number, In Challan Number, In Challan Date, (hidden branch and id columns), From Project, From Department, Receiving Branch, To Project, To Department, Created By, Approved By, Approval Date, Status, ShipmentId, Preview.
- Searching by the Out Challan No shows the challan with its In Challan Number, Status ACKNOWLEDGED, and a **Preview** link.

## Preview
- The Preview link (`printSingleChallanGatePass(594)`) opens a **new browser tab** with a PDF report: `https://erpstaging.brac.net/nodef/faAssetReport/generateAssetGatePassReport?format=PDF&radPdf=1&organizationBranchId=2&office=2&challan=594&...`. The tab has no page text (it is a PDF), so check it like the voucher preview: take the tab's address, then fetch it with the logged-in session and read the PDF (see `VoucherSearchPage.read_voucher_preview`). The PDF content itself was not read yet.
- The Asset Shipment list also has a Preview on an APPROVED shipment (`shipmentConsolidatedGatePass(827)`, a consolidated gate pass). Not opened yet.
