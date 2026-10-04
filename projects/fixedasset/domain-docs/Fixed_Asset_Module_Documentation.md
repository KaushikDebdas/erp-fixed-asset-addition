# Fixed Asset Module — Full Documentation

This document consolidates the screen-by-screen breakdown of the Fixed Asset module, organized by section. Each screen includes its purpose, generated output/IDs, related journal voucher (accounting) entries, and additional notes.

---

## 1. Setup

### Manage Building
- **Purpose:** Used to configure and maintain building information (setting up the buildings that exist).

### Manage Floor
- **Purpose:** Used to manage the floors associated with each building.

### Manage Room
- **Purpose:** Used to manage the rooms available on each floor.

---

## 2. Asset Registration
> *Asset Registration means creating the official identity of a newly purchased asset in the ERP system.*

### Asset Registration by AAQ
- **Purpose:** Used to register a new asset.
- **Output:** Registration No.

### Asset Registration by List
- **Purpose:** Displays assets saved in **Draft** status, allowing them to be reviewed, edited, and submitted.

### Asset Approval by List
- **Purpose:** Used to approve newly created asset registrations.
- **Output:**
  1. Asset ID / Serial generated
  2. Journal Voucher created
- **Accounting Entry (on approval):**
  - Fixed Asset (Group-wise) — **Dr.**
  - Supplier Payable – Capex — **Cr.**

---

## 3. Asset Profile

### Asset Serial Global List
- **Purpose:** After an asset is approved, a serial number is generated. This screen displays the complete details of an asset, including:
  - Asset Details
  - Depreciation History
  - Revaluation History
  - Transaction History
  - Expenditure
  - Disposal Information
  - Attachments

### Generate Barcode
- **Purpose:** Used to generate and print an asset's barcode.
- **Output:** Barcode

### Asset in Pending Process List
- **Purpose:** If a specific asset is currently in any pending process (e.g., submitted for relocation but not yet approved, submitted for transfer to another branch but not yet approved, etc.), the asset appears in this list.

### Asset Serial Split
- **Purpose:** Used to split an asset into multiple parts/units.
- **Prerequisite:** The asset's measurement must be defined. If missing, the asset must first be edited to add the measurement before it can be split.
- **Logic:** The "Split Into" field determines how many parts the value is divided into. Example: if an asset's written-down value is 100 taka and it's split into 2 equal parts, the result is 50 + 50 = 100.

### Asset Serial Split Approval List
- **Purpose:** Used to approve asset split requests.
- **Output:** New Asset ID / Serial generated (for the split asset).

---

## 4. Asset Transaction

### Asset Assign
- **Purpose:** Used to assign unassigned assets to employees.
- **Workflow:**
  1. Enter the Asset Serial Number.
  2. Remaining fields auto-populate after selection.
  3. Save to the data grid.
  4. In "Assign To," search the employee by PIN Number or Name, then save.
- **Result:** Saved transactions go to the **Transaction Approval List**; drafts appear in the **Transaction List**.
- **After approval:** the assigned employee must confirm receipt of the asset in **Asset Assign Acknowledgement** (see below).

### Asset Un-Assign
- **Purpose:** Used to unassign previously assigned assets.
- **Search options:**
  - **Serial Number** — search directly by asset serial number.
  - **Employee PIN** — view all assets assigned to a specific employee.
- **Workflow:** Add to grid → use "Hand Over To" section to unassign. Multiple assets can be unassigned together via "Add to Grid."

### Asset Internal Movement
- **Prerequisite:** The asset must be assigned. Unassigned assets cannot use this screen.
- **Purpose:** Used to move assets from one location to another.
- **Search options:** Serial Number, Employee PIN (same as Un-Assign).

### Transaction List
- **Purpose:** Displays transactions from Asset Assign, Asset Un-Assign, and Asset Internal Movement that were saved as Draft or Submitted.
  - Draft transactions can be edited and updated here.
  - Transactions that are **Sent Back** during approval also appear here for editing/resubmission.

### Transaction Approval List
- **Purpose:** Used to approve, reject, or send back requests from Asset Assign, Asset Un-Assign, and Asset Internal Movement.

### Asset Assign Acknowledgement
*(Added after checking the screen on the staging environment; the original sources did not describe it.)*
- **Purpose:** Used to verify that the employee an asset was assigned to has actually received it. It is used by the **assigned employee**, not by the person who created the assignment.
- **Prerequisite:** The Asset Assign transaction must already be approved in the **Transaction Approval List**.
- **Screen layout:** The screen has two sections:
  - **Pending Asset Acknowledgement** — one row for each approved assignment waiting for the logged-in employee, with Transaction Type, Project, Branch, Assigned Employee, Assigned By, Approval Date and a Details link. Each row has a checkbox (and a select-all checkbox) and an **Acknowledge** button for the ticked rows.
  - **My Assigned Asset** — the assets the logged-in employee has already acknowledged, with Asset Serial, Asset Item Name, Branch, Project, Building, Floor, Room, Assigned Employee, Assigned By and Utilization Status.
- **Workflow:**
  1. The assigned employee logs in and opens **Asset Transaction > Asset Assign Acknowledgement**.
  2. Click **Details** on the assignment to open the transaction details and its list of assets.
  3. Check that the **Asset Serial Number** shown is the asset that was assigned to you.
  4. Click **Acknowledge** (in the details window, or tick the row and use the Acknowledge button on the screen).
- **Result:** The message **"Acknowledged successfully"** is shown, the assignment leaves the Pending list, and the asset appears in **My Assigned Asset**. The transaction itself still shows the status APPROVED in the Transaction List and the Transaction Approval List.

---

## 5. Asset Transfer
> *Asset Transfer means moving a fixed asset from one location to another while the organization remains the owner — the asset is not sold, only relocated.*

### Asset Shipment
- **Purpose:** Used when assets need to be transferred from one branch to multiple branches. A Shipment must be created first.
- **Rule:** Cannot create a shipment during the **last 3 days of the month**.
- **Output:** Shipment number generated.
- **Note:** After creating the shipment, a **Chalan** (official supporting document) must also be generated.

### Asset Shipment → Shipment List → Shipment No. → Transfer Challan → Create Challan
- **Purpose:** A Challan is an official document containing: Challan No., asset details, asset quantity, sending/receiving branch, department, and project.
- **Output:** OutChallan Number generated.
- **Note:** After saving the Challan, asset serial numbers must be added separately (via Asset Shipment → Add Details).
- **Rule:** If the sending and receiving branch are not in the same month, the Challan cannot be submitted.

### Asset Shipment → Shipment List → Shipment No. → Add Serial
- **Purpose:** After creating the Challan, add the asset serial numbers to specify exactly which assets are being shipped.
- **Note:** If the Initiator skips this during Challan creation, it can be done later via "Add Serial."
- **Options:**
  - **Disposal** — mark an asset no longer in use for disposal.
  - **Transfer to Maintenance** — mark an asset that needs maintenance.

### Asset Shipment Challan Approval List
- **Purpose:** Used to approve, reject, or send back the shipment Challan.

### Asset Shipment Approval
- **Purpose:** After the Challan is added (via Shipment No.), the shipment itself is approved or rejected here.
- **Note:** Serial numbers can still be added here if missed earlier.

### Gate Pass Generation
- **Purpose:** Generates a gate pass for transferring an asset between branches. Auto-generated; searchable by criteria; downloadable as PDF.
- **Output:** Gate Pass PDF.

### Asset Shipment In-Challan
- **Purpose:** When a branch sends assets via a shipment Challan, the receiving branch creates an "In-Challan" which must be **acknowledged**. Serial numbers can also be added here.
- **Note:** No voucher is created until acknowledged.
- **Output:** InChallan Voucher / Journal Voucher.
- **Accounting Entry (on acknowledgment):**
  - Equipment — **Dr.**
  - Current A/C with HO — **Cr.**
  - *(Sending Branch – Cr., Receiving Branch – Dr., impacts Trial Balance)*

---

## 6. Single Challan
> *Used for transferring assets between branches, or between different projects within the same branch. **Cannot** be used for transfers across multiple projects within the same branch — use multiple Challans in that case.*

### Asset Single Out Challan
- **Purpose:** Used to send an asset from one branch to another, or between projects in the same branch.
- **Fields:** Courier details, Sending Branch, From Project, Receiving Branch, To Project, etc.
- **Options:**
  - **Returnable** — mark if the asset must be returned (e.g., loaned).
  - **Receivable** — mark when returnable assets are sent back.
- **Output:** OutChallan number generated.
- **Accounting Entry (on acknowledgment, sending branch):**
  - Current A/C with HO — **Dr.**
  - Equipment — **Cr.**
  - *(Impacts Trial Balance)*

### Asset Single Out Approval
- **Purpose:** Used to approve the Single Out Challan.
- **Output:** OutChallan Voucher / Journal Voucher (an OutChallan Voucher and an InChallan Voucher are created upon acknowledgment).

### Asset Single-In Challan
- **Purpose:** Used by the receiving branch/project to receive and acknowledge a transferred asset.
- **Output:**
  1. InChallan number generated
  2. InChallan voucher created
  3. OutChallan voucher created
- **Accounting Entries (on acknowledgment):**
  - OutChallan/Journal Voucher: Current A/C with HO — **Dr.**, Equipment — **Cr.**
  - InChallan/Journal Voucher: Equipment — **Dr.**, Current A/C with HO — **Cr.**
  - *(Impacts Trial Balance)*

### Asset Receivable List
- **Purpose:** Shows assets sent as "Returnable" (via Single Challan) from the receiving branch's point of view — i.e., which assets it currently holds that must eventually be returned.

### Asset Returnable List
- **Purpose:** Shows assets that have been returned by the receiving branch (marked Receivable) and acknowledged by the sending branch — lets the sending branch track/confirm returns.

---

## 7. Asset Expenditure

### Asset Expense
- **Purpose:** Used to record expenses that do **not** increase an asset's useful life.
- **Fields:**
  - **Expense Amount** (optional) — used when different assets have different expense amounts.
  - **Total Expense Amount Distribute** — used when same-type assets share the same expense; enter total and click Distribute to split evenly.
  - **Expense Source (Inventory)** — select when repairing using parts already in inventory. Credit A/C = Other Inventory (item taken from inventory).
    - *Example: 5 AC units in inventory; 1 filter used to repair an AC.*
  - **Expense Source (Accounts)** — select when the item/service is purchased externally. Credit A/C = Supplier Payable–Opex (creates a liability).
    - *Example: Paying a technician to repair an AC.*
- **Output:** Expense ID generated.
- **Draft:** The expense can also be saved as a **Draft** (the Expense ID is generated at that moment). Open the Expense ID from the Asset Expense list to review or edit it, then **Submit**; a Draft is not sent for approval until it is submitted. Submitting directly without a Draft is also possible, and it generates the Expense ID too.
- **Rules learned from checking the screen on the staging environment:**
  1. Add the asset to the grid first: enter the Expense Amount and click Add, and only then choose the Expense Source. Otherwise the Credit A/C list stays empty.
  2. Vendor/Supplier/Lessor Name is required for both sources. Without it the message is: Vendor/Supplier/Lessor Name is required.
  3. Inventory: Category, Sub Category and Item Name are required and match the asset (for a Cabinet Table: Furniture, Wooden Furniture, Cabinet Table). Credit A/C fills in as Other Inventory [1107010401-02].
  4. Accounts: Category, Sub Category and Item Name are disabled. Credit A/C fills in as Supplier Payable-Opex[2101010301-05].
  5. Debit A/C: Other Maintenance Expenses[5108010101-07], chosen by hand for both sources.
  6. Expense Ref. is required (any text; the tests use EXP plus six random digits). The Expense ID is generated as soon as the expense is saved, whether you click Draft or Submit (BBDEXP00000001, ...); store it, it is the key to find the expense again.

### Asset Expense Approval
- **Purpose:** Used to approve, reject, or send back an asset expense.
- **How:** Open the Expense ID to see the expense, then click **Approve**, **Reject** or **Sendback**. After approval the expense shows the status APPROVED in both the Asset Expense Approval list and the Asset Expense list.
- **Checking the journal after approval:** In the **Accounting** module open **Voucher > Voucher Search**, enter the expense date in both Date From and Date To, type the **Expense ID** in Transaction Number and click Search; the voucher is listed with Particular "Asset Expense Voucher, Reference no: <Expense ID>". Click **Preview**: the voucher opens in a new tab as a PDF. Check the Journal Voucher header (branch, project, dates), the Reference no, the accounts and the amounts: Inventory = Other Maintenance Expenses Dr. 5,000.00 / Other Inventory Cr. 5,000.00; Accounts = Other Maintenance Expenses Dr. 5,000.00 / Supplier Payable-Opex Cr. 5,000.00 (for an expense amount of 5,000), and both totals equal.
- **Accounting Entries:**
  - If **Expense Source = Inventory** (auto journal):
    - Other Maintenance Expenses — **Dr.**
    - Other Inventory — **Cr.**
  - If **Expense Source = Accounts** (auto journal):
    - Other Maintenance Expenses — **Dr.**
    - Supplier Payable–Opex — **Cr.**
    - *(A second, manual journal is then required from the Accounting Module to record payment: Supplier Payable–Opex — Dr., Cash/Bank — Cr.)*

### Asset Addition from Inventory
- **Purpose:** Used for expenses that **do** increase an asset's useful life, where the added component comes from existing inventory.
  - *Example: Adding RAM (already in inventory) to an existing laptop.*
- **Note:** Can be saved as Draft and later edited/submitted from the same screen.

### Asset Addition from Inventory Approval
- **Purpose:** Approve, reject, or send back requests from "Asset Addition from Inventory."
- **Accounting Entry (on approval, auto journal):**
  - Asset (Building/Furniture/Equipment, etc.) — **Dr.**
  - Work in Progress – Capital Inventory — **Cr.**

### Asset Addition from Vendor
- **Purpose:** Similar to above, but the added component/part is purchased directly from a vendor rather than taken from inventory.
  - *Example: Buying RAM from a vendor and adding it to an existing laptop.*
- **Note:** Can be saved as Draft and later edited/submitted from the same screen.

### Asset Addition from Vendor Approval
- **Purpose:** Approve, reject, or send back requests from "Asset Addition from Vendor."
- **Accounting Entry (on approval, auto journal):**
  - Asset (Building/Furniture/Equipment, etc.) — **Dr.**
  - Work in Progress – Capital Inventory — **Cr.**
- **Note:** Vendor payment itself must still be journalized manually from the Accounting Module.

---

## 8. Asset Depreciation

### Asset Depreciation Schedule List
- **Purpose:** Generates the depreciation schedule during month-end processing (after the Fixed Asset module is initiated).
- **Branch attribution rules:**
  - If depreciation is generated **after** acknowledgment → attributed to **Receiving Branch**.
  - If depreciation is generated **before** acknowledgment → attributed to **Sending Branch**.
- **Calculation:** Depends on the asset's purchase date.
  - `Last Depreciation Amount = round((Total Unit Price − Accumulated Depreciation − Salvage Value) / Remaining Asset Life)`
- **Output:**
  1. Depreciation Schedule
  2. Journal Voucher
- **Accounting Entry (auto, at month-end):**
  - Depreciation Expense — **Dr.**
  - Accumulated Depreciation — **Cr.**

---

## 9. Asset Disposal

### Asset Write Off
- **Prerequisites:**
  1. Asset must be **unassigned**.
  2. Asset Utilization Status must be set to Burn, Stolen, Damaged, or Donated (via Asset Global List).
- **Rule:** No depreciation is calculated for the month in which the asset is written off.

### Asset Write Off Schedule List
- **Purpose:** Used to draft/edit a write-off before submission.

### Write off Schedule Approval List
- **Purpose:** Used to approve or reject created write-offs.
- **Accounting Entry (on approval, auto journal):**
  - Loss Recognized — **Dr.**
  - Asset Decrease — **Cr.**

### Asset Sale
- **Prerequisites:**
  1. Asset must be **unassigned**.
  2. Asset Utilization Status must be changed via Asset Global List.
  3. Assets marked Stolen or with Offline Transfer status **cannot** be sold.
- **Receive Types:** Cash or Bank.

### Asset Sale Schedule List
- **Purpose:** Used to draft/edit an asset sale before submission.

### Asset Sale Schedule Approval List
- **Purpose:** Used to approve or reject created asset sales.
- **Accounting Entries (on approval — two vouchers created):**
  - **Credit Voucher:**
    - Cash/Bank — **Dr.**
    - Suspense A/C — **Cr.**
  - **Journal Voucher:**
    - Gain/Loss on Property, Plant and Equipment — **Dr.**
    - Suspense Account — **Dr.**
    - Computer and IT Equipment — **Cr.**

---

## 10. Reports

| Report | Description |
|---|---|
| **Asset List** | Download a list of all available assets. |
| **Asset Register Report** | Report of all registered assets. |
| **Asset Valuation Report** | Determines the current/fair value of an asset; keeps records financially accurate. |
| **Asset Transfer & Receive Report** | History of asset transfers/receipts — Out Challan No., In Challan No., Sending/Receiving Branch & Department, Shipment No. |
| **Asset Transaction History Report** | History of Asset Assign, Un-Assign, and Internal Movement transactions. |
| **Asset Receivable Report** | Tracks Receivable/Returnable values from Single Challans — when an asset was due back, when it was returned, and between which projects it moved. |
| **Asset Returnable Report** | List of all assets currently marked as returnable. |
| **Asset Disposal Sale Report** | Details of sold assets: total price, written-down value, sale price, profit/loss. |
| **Asset Depreciation Statement (Serial-Wise)** | Cost/depreciation details (Opening, Receive, Addition, Disposal, etc.) for a specific serial number over a date range. |
| **Asset Depreciation Statement (Group-Wise)** | Cost/depreciation details (Opening, Receive, Addition, Disposal, etc.) grouped by asset group over a date range. |
| **Asset Depreciation History (Serial-Wise)** | Month-by-month depreciation history for a specific asset serial. |
| **Asset Depreciation History (Group-Wise)** | Month-by-month depreciation history for an asset group, as of a given date. |

---

## Summary: Journal Voucher Triggers by Screen

| Trigger Screen | Debit | Credit |
|---|---|---|
| Asset Approval by List | Fixed Asset (Group-wise) | Supplier Payable – Capex |
| Asset Shipment In-Challan (acknowledged) | Equipment | Current A/C with HO |
| Asset Single Out Challan (acknowledged) | Current A/C with HO | Equipment |
| Asset Single-In Challan (acknowledged) — OutChallan | Current A/C with HO | Equipment |
| Asset Single-In Challan (acknowledged) — InChallan | Equipment | Current A/C with HO |
| Asset Expense Approval (Inventory source) | Other Maintenance Expenses | Other Inventory |
| Asset Expense Approval (Accounts source) | Other Maintenance Expenses | Supplier Payable–Opex |
| Asset Addition from Inventory Approval | Asset (Building/Furniture/Equipment) | Work in Progress – Capital Inventory |
| Asset Addition from Vendor Approval | Asset (Building/Furniture/Equipment) | Work in Progress – Capital Inventory |
| Asset Depreciation Schedule (month-end) | Depreciation Expense | Accumulated Depreciation |
| Write Off Schedule Approval | Loss Recognized | Asset Decrease |
| Asset Sale Schedule Approval — Credit Voucher | Cash/Bank | Suspense A/C |
| Asset Sale Schedule Approval — Journal Voucher | Gain/Loss on PP&E, Suspense Account | Computer and IT Equipment |
