# Asset Shipment (list and Create Shipment popup) — element catalog

| Field | Value |
|---|---|
| Page class | not yet built |
| Module / menu path | Fixed Asset >> Asset Transfer >> Asset Shipment |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetTransfer/showShipment` (reach it by clicking the menu, like the other Fixed Asset pages) |
| Role needed | Employee `00015370` (Sachindra Nath Ghosh), the second user in `.env`, Head Office [ BDHO ]. The main user (`abushoaib.asik`, INVENTORY_SA, Head Office [ BDHO ]) sees the same four Asset Transfer pages. Both users are in the SAME branch. |
| Last explored | 2026-10-04 (read only: the list, and the Create Shipment popup opened and closed; nothing saved) |
| Screenshot | none taken; values below were read from the live page |

## Menu
Asset Transfer menu: **Asset Shipment**, **Asset Shipment Challan Approval List**, **Asset Shipment In-Challan**, **Gate Pass Generation**. The separate Single Challan menu has six pages (Asset Single Out Challan, Asset Single Out Challan Approval List, Asset Single In-Challan, Gate Pass Generation, Asset Receivable List, Asset Returnable List). The menu text is a plain label; click it, then click the link.

## Shipment List — filters and grid
| # | Element | What it is for | Locator | Status |
|---|---|---|---|---|
| 1 | Shipment No | free text filter | `#searchShipmentNo` | VERIFIED |
| 2 | Shipment Date From / To | read-only date filters (calendar pop-up, dd/mm/yyyy) | `#fromDate`, `#toDate` | VERIFIED |
| 3 | Created By | employee search box (min 3 characters), starts with the logged-in user: `00015370-SACHINDRA NATH G...` | `#createdBy` | VERIFIED |
| 4 | Approved By | employee search box | `#approvedBy` | VERIFIED |
| 5 | Shipment Status | PENDING, APPROVED, REJECTED (no DRAFT, no SENDBACK) | `#searchAssetShipmentStatus` | VERIFIED |
| 6 | Search | runs the filter | `get_by_role("button", name=" Search")` (onclick `searchAssetShipment()`) | VERIFIED |
| 7 | Reset | empties the filters | `#resetUpdate` | VERIFIED |
| 8 | **Create** | opens the Create Shipment popup. It is a **link styled as a button, not a `<button>`**: `get_by_role("button", name="Create")` finds nothing | `locator(".btn:visible", has_text="Create")` | VERIFIED (a more specific locator is still needed; LOCATOR_REQUIRES_REVIEW for a role-based one) |
| 9 | Records per page | 10, 20, 30, 50, 100 | `select[name=shipmentListTable_length]` | VERIFIED |
| 10 | Grid | columns: SL, (tick box), Shipment No, Edit, Shipment Date, Created By, Creation Date, Approved By, Approval Date, From Branch, Status, Preview | `#shipmentListTable` | VERIFIED |

The list was empty for employee 00015370 ("Showing 0 to 0 of 0 entries", "No data available in table").

## Create Shipment popup (title " Create Shipment")
| # | Element | Notes | Locator | Status |
|---|---|---|---|---|
| 1 | Shipment No | read-only, shows `AUTO`; the number is generated on Save | `#shipmentNo` | VERIFIED |
| 2 | From Branch * | dropdown, only `Head Office [ BDHO ]`, already chosen | `#office` (name `fromOffice`) | VERIFIED |
| 3 | Shipment Date * | read-only, pre-filled with `04/10/2026` (today) | `#faShipmentDate` | VERIFIED |
| 4 | Courier Service Name / Transfer By | free text | `#courierName` | VERIFIED |
| 5 | Courier Number | free text | `#awbNo` | VERIFIED |
| 6 | Driver Name | free text | `#driverName` | VERIFIED |
| 7 | Transport No. | free text | `#transportNo` | VERIFIED |
| 8 | Courier Details | text area | `#courierDetails` | VERIFIED |
| 9 | Note/Remarks | text area | `#remarks` | VERIFIED |
| 10 | Save | saves the shipment (onclick `saveShipment()`) | `#createShipment` | VERIFIED (click not yet tried) |
| 11 | Reset | clears the popup | `#cancel` | VERIFIED |
| 12 | Close | closes the popup; after Close the popup is gone | `locator(".modal:visible .btn:visible", has_text="Close")` | VERIFIED |

Required fields marked `*`: Shipment No, From Branch, Shipment Date (the first and last are filled automatically). The page also holds hidden dialogs ("Runtime Exception occurred:", "Support Contact Information", "Session Timeout Notification"); ignore them.

## Verified 2026-10-04 (live, employee 00015370; data was created on staging, see the CHANGELOG)
**Save a shipment**: toast `Asset Shipment Initiated Successfuly` (spelled that way); the popup closes; the new row is in the list with Status PENDING and Shipment No like `BBDSHP00000009`. The list row has the Shipment No link (`showAssetShipmentDetailsPopup`) and an **Edit** link (`editShipment()`; it carries `disabled="disabled"` but opens the popup).

**Update Shipment popup** (Edit): same fields filled in, Shipment No read-only; buttons Update `#updateShipment`, Delete `#deleteShipment`, Close.

**Shipment Details popup** (`#commonModal`, title "Shipment Details"): tabs **Details**, **Transfer Challans**, **Add Serial**. Read-only fields `#shipmentNoDetails`, `#fromBranchDetails`, `#driverNameDetails`, `#transportNoDetails`, `#courierNameDetails`, `#courierDetailsDetails`, `#remarksDetails`, `#shipmentDateDetails`, `#statusDetails`, `#dateCreatedDetails`, `#createdByDetails`, `#approvalDateDetails`, `#approvedByDetails`. Buttons **Approve** `#approveShipment`, **Reject** `#rejectShipment`, Close.
- Approve with no challan: toast **`Please add at least one challan`** (lowercase "add", no full stop; the description said `Please Add at least one challan.`).

**Transfer Challans tab**: Create `#addChallanBtn`; challan list `#challanListTable` columns SL, (id), Out Challan No., Edit, All Serial Added, Out Challan Date, Sending Branch, From Project, From Department, Receiving Branch, To Project, To Department, Created By, Approved By, Approved Date, Status, In Challan No, Preview. The Out Challan No (`OC-BBDSHP00000009-594`) link opens Challan Details.

**Create Challan popup** (title " Create Challan", `#challanResponsive`): Out Challan No `#outChallanNo` (`AUTO`), Sending Branch `#fromBranchId` (read-only, Head Office [BDHO]), From Project `#fromProject` (dropdown box `#s2id_fromProject`), From Department `#fromDept` (disabled until a project is chosen), Note `#challanRemarks`, Out Challan Date `#faOutChallanDate` (read-only, pre-filled `20/09/2026`, the business date, while the shipment date is today `04/10/2026`), Receiving Branch `#toOffice` (box `#s2id_toOffice`; the only choice is `[HO - BDHO] Head Office`), To Project `#toProject` (box `#s2id_toProject`), To Department `#toDepartment`, Asset Item Name `#asset` (box `#s2id_asset`, search "Cabinet"), and read-only Asset Category `#assetCategory`, Sub Category `#assetSubCategory`, Group `#assetGroup`, Measurement Unit `#uom`, Quantity `#quantity`. Buttons Add `#addToAssetItemGrid`, Draft `#createChallan`, Submit `#submitChallan`, Reset `#resetChalan`, Close. Added lines show in `#assetItemsTable` (SL, Asset Item Name, Asset Sub Category, Asset Category, Quantity, Measurement Unit, Challan Item ID, Action = **Remove**).
- The three dropdowns (From Project, To Project and the asset item and Receiving Branch) must be chosen by clicking the visible box, typing, and clicking the result. Setting the hidden native `<select>` directly is NOT enough: Add then says `Please select to project`.
- Add with no To Project: toast `Please select to project`. Draft with no line: toast `No Items in Challan to perform operation`.
- Draft with From Project `[015] Microfinance (Dabi)` and To Project `[C04] Administratiion`: toast **`Area code not found`** (the project is not mapped, like the earlier Approve blocker). With To Project **`[060] Progoti`** the Draft works: toast **`Challan drafted successfully`**, the popup closes, and the Out Challan No is already generated (Status DRAFT, All Serial Added `No`).
- Removing a line (Remove link) empties the grid and clears the item fields.

**Challan Details popup** (`#challanDetailsModal`): tabs **Details**, **Asset Serials**, **Posted Accounts** (expected to show the journal vouchers). Read-only fields `#outChallanNoDetails`, `#outChallanDateDetails`, `#fromProjectDetails`, `#toProjectDetails`, `#status`, `#fromBranchDetails`, `#toBranchDetails`, and so on. Item grid `#assetItemsTableDetails` has a per-line link **Add Serial** (`showAddAssetSerialPopup(...)`), not a button.

**Add Asset Serial popup** (`#addAssetSerialModal`, title "Add Asset Serial"): Serial No dropdown (native `#assetSerialSelect`, box inside the popup; typing the serial finds `BBDASR00227812 Cabinet Table`), read-only Item Name `#addItemName`, Quantity `#addItemQuantity`, Sub-Category `#addSubCategory`, Category `#addCategory`, checkboxes Disposal `#isDisposal2` and "Tranfer to maintenance" `#isMaintenance2` (label misspelled), Add `#addChallanSerial`, Save (`saveAssetSerial()`, it reuses the id `createChallan`, the same id as the Draft button, so scope it to the popup), Close. Grid `#assetSerialItemAdditionTable`; each row has a **Remove** link. Choosing a serial fills the four read-only boxes. Add puts the row in the grid with no toast. **Save: toast `Asset serial added Successfuly`** (the description said `Asset Serial(s) save successfully`). The Asset Serials tab of Challan Details then lists the serial in `#assetSerialTableShipmentChallan`.

**Shipment tabs**: the **Approve** and **Reject** buttons are only visible on the **Details** tab; on the Add Serial tab `#approveShipment` is hidden. The shipment's **Add Serial** tab lists the challan's serials in `#assetSerialAdditionTable` (SL, Asset Profile ID, shipment id, Asset Serial, Item Name, Sub Category, Category, Disposal, Maintenance).

**Messages seen (live)**
| Action | Message |
|---|---|
| Save shipment | `Asset Shipment Initiated Successfuly` |
| Approve shipment with no challan | `Please add at least one challan` |
| Approve shipment while the challan is a Draft | `Approve at least one challan` |
| Draft a challan | `Challan drafted successfully` |
| Delete a Draft challan (Update Challan popup, Delete `#deleteChallan`; no confirmation box) | `Challan deleted successfuly` |
| Submit the challan (Update Challan popup, Submit `#submitChallan`) | `Challan submitted successfully` (status becomes PENDING; the popup closes) |
| Save a serial | `Asset serial added Successfuly` |
| Approve the challan (approval list) | `Challan approved successfully.` |
| Approve the shipment | `Shipment approved successfully` and `Gate pass generated successfully` (shown together in one toast) |

**Update Challan popup** (a Draft's Edit link, heading " Update Challan"): the Sending and Receiving Branch, From and To Project, and the date are read-only; buttons Add, **Update** `#updateChallan`, **Submit** `#submitChallan`, **Delete** `#deleteChallan`, Close.

**Challan list on the Transfer Challans tab**: after the serial was added, the challan row showed All Serial Added **Yes** (it showed No before). After approval of the shipment the challan row shows the In Challan No and Status ACKNOWLEDGED once acknowledged.

**Approve the shipment** (Details tab, `#approveShipment`, with the challan APPROVED): the popup closes; the list row shows Status **APPROVED**, Approved By, Approval Date (`20/09/2026`) and a **Preview** link (`shipmentConsolidatedGatePass(827)`).

## Not yet explored
The Preview reports (challan, shipment gate pass, in-challan), Reject and Sendback outcomes, Reject on the shipment, editing and deleting a shipment, the filters and paging of the four lists, the branch and project rules (same branch needs different projects), the `Area code not found` projects, the month rule for Submit, the Disposal and Transfer to Maintenance options when adding a serial, "Quantity exceeded!", acknowledgement by a user of a different branch, the exact acknowledgement message, and **the journal vouchers**: the challan's Posted Accounts tab stayed empty after the acknowledgement, and Voucher Search (module Fixed Asset, accounting date `20/09/2026`, and the Out Challan, In Challan and Shipment numbers) found nothing as either user. The flow is in `projects/fixedasset/e2e-flows/asset-transfer-shipment.md`.
