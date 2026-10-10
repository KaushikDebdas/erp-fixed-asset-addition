# BRAC IT Change Request Document

| | |
|---|---|
| **Title** | Asset Addition with Reference Number with existing asset |
| **CR ID** | FAHOV2-643 |
| **JIRA ID** | FAHOV2-643 |
| **Created by** | Abu Saleh Md. Nafis, Business Analyst, BRAC IT Services Limited |
| **Reviewed by** | Rafijur Rahman, Sr. Business Analyst, BRAC IT Services Limited |

**Confidential Level – External (Protected)**

*This document contains proprietary and confidential information of BRAC IT. The information enclosed in this Software Requirement Specification (SRS) is intended solely for the use of BRAC IT and the designated client, its nominated individuals, and/or partners. Unauthorized access, use, distribution, or disclosure of any information contained herein is strictly prohibited. The contents of this document must not be disclosed to any third party without prior written consent from BRAC IT. All rights to this document and the information contained within are reserved by BRAC IT.*

---

## Revision History

| Date | Version | Created by | Description of change | Impacted Pages |
|---|---|---|---|---|
| 7-Dec-25 | 1.0 | Abu Saleh Md. Nafis | Initial Draft | |
| 14-Dec-25 | 1.1 | Abu Saleh Md. Nafis | Changes incorporated: Asset Expenditure Feature Incorporated; Asset Expenditure Approval Feature Incorporated; Impacted Reports Feature Incorporated | 33, 34, 48 |
| 21-Dec-25 | 1.2 | Abu Saleh Md. Nafis | Changes incorporated: Asset Addition List Report Incorporated | 48 |
| 15-Jan-26 | 1.3 | Abu Saleh Md. Nafis | Changes incorporated: Asset Addition sequence format is changed; Child asset naming is replaced with Asset extension; Extension Asset can be sold separately; Extension Asset can be written off separately; Validation to restrict asset split for assets having asset extension; Additional field required in the asset split user story is removed from the document; Additional column added in the asset addition list report | 8, All, 41, 36, 44, 46, 45 |
| 05-Apr-26 | 1.4 | Abu Saleh Md. Nafis | Changes incorporated: New Validation added for asset transactions having extended assets during asset addition; Validation added for asset sale and write-off during bulk upload via excel; Automatic asset assignments with asset transaction will take place if any asset has already been assigned to any employee and new extended asset is added; Asset Sale value will be assigned to parent asset and then gradually to extended assets | 8, 37/41, 12, 41 |
| 16-Apr-26 | 1.5 | Abu Saleh Md. Nafis | Changes incorporated: All the impairment related business has been removed from entire document | All |
| 29-Apr-26 | 1.6 | Abu Saleh Md. Nafis | Changes incorporated: Parent asset will be restricted from Transfer, Shipment, Write-off, and Sale when a new child asset addition is acknowledged but pending approval. Child asset addition will be restricted in HOFIN if the parent asset is already involved in a Transfer, Shipment, Write-off, or Sale transaction. Parent asset will be restricted from Transfer, Shipment, Write-off, and Sale while the new child asset addition is pending acknowledgement. Individual disposal is allowed only for child assets. Selecting a parent asset for disposal will dispose of the parent and all associated child assets together. A parent without child assets can be disposed of independently. To dispose of an individual child asset, both the parent and child assets must first be unassigned. After disposal, the remaining assets can be reassigned as required. Child Disposal in Progress: During child asset addition, if any associated child asset is under a disposal process, the parent asset will be restricted from all applicable transactions. | All |

---

## Purpose

The current fixed asset management system handles asset additions by simply aggregating the cost of additions with the existing parent asset's price and recalculating the unit price. The proposed change introduces the concept of creating a separate asset entity under the parent asset for each addition, ensuring better control, traceability, and compliance with accounting standards. The change will also enforce a minimum asset price threshold, ensure proper depreciation calculation, and introduce parent & added asset relationships in the system.

**The Change and scope of this CR is applicable across the whole fixed asset system (FOFA & HOFA).**

## Users

The users of this document are Business Analysts, Software Engineers, Quality Assurance, Product Owner, Project Manager and Stakeholders from BRAC Bangladesh Fixed Asset users.

## Scope of this CR

| Scope Identification | Description |
|---|---|
| **In Scope** | The scope of this document includes:<br>– New process for asset addition in the system by generating a new asset entity instead of merging costs with the parent asset.<br>– Strengthen asset tracking and reporting through parent & extended/subsidiary asset relationships.<br>– Introduce new fields for parent asset details in the asset profile.<br>– New tab for addition history on asset profile details.<br>– New validation on extended/subsidiary assets.<br>– New list view for extended/subsidiary assets.<br>– Asset split conditions and extended validation with additional fields.<br>– The Change and scope of this CR is applicable across the whole fixed asset system (FOFA & HOFA). |
| **Out of Scope** | • Extended asset addition from branch offices is out of scope; extended assets can only be added through the Head Office Finance (HOFIN) module.<br>• Anything not mentioned in the SRS is out of scope. |

## Workflow

N/A

---

## Table of Contents

1. Asset Serial Global List | F01
2. Asset Assign | F02
3. Asset Unassign | F03
4. Internal Movement | F04
5. Transaction List | F05
6. Transaction Approval List | F06
7. Asset Assign Acknowledgement | F07
8. Asset Shipment | F08
9. Asset Shipment Challan Approval List | F09
10. Asset Shipment In-Challan | F10
11. Asset Single Out Challan | F11
12. Asset Single Out Challan Approval List | F12
13. Asset Single In-Challan | F13
14. Asset Receivable List | F14
15. Asset Returnable List | F15
16. Asset Expenditure | F16
17. Asset Expenditure Approval | F17
18. Asset Write Off | F18
19. Asset Write Off List | F19
20. Asset Write Off Approval List | F20
21. Asset Sale | F21
22. Asset Sale List | F22
23. Asset Sale Approval List | F23
24. Asset Split | F24
25. New and Existing Impacted Reports | F25

---

## List of Features & Stories

| Feature ID | Feature Title | Story ID | Story Title |
|---|---|---|---|
| F01 | Asset Serial Global List | F01S01 | A new asset will be added to the Global Asset Serial List upon asset addition |
| | | F01S02 | Parent asset information in the Asset Profile Details pop-up window |
| F02 | Asset Assign | F02S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F03 | Asset Unassign | F03S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F04 | Internal Movement | F04S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F05 | Transaction List | F05S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F06 | Transaction Approval List | F06S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F07 | Asset Assign Acknowledgement | F07S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F08 | Asset Shipment | F08S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F09 | Asset Shipment Challan Approval List | F09S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F10 | Asset Shipment In-Challan | F10S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F11 | Asset Single Out Challan | F11S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F12 | Asset Single Out Challan Approval List | F12S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F13 | Asset Single In-Challan | F13S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F14 | Asset Receivable List | F14S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F15 | Asset Returnable List | F15S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F16 | Asset Expenditure | F16S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F17 | Asset Expenditure Approval List | F17S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F18 | Asset Write-Off | F18S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F19 | Asset Write-Off List | F19S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F20 | Asset Write-Off Approval List | F20S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F21 | Asset Sale | F21S01 | New validation will be added on not letting the user select any extended/subsidiary asset |
| F22 | Asset Sale List | F22S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F23 | Asset Sale Approval List | F23S01 | Extended/Subsidiary asset will show with right indentation below parent asset on the list view |
| F24 | Asset Split | F24S01 | Validation to Restrict Asset Split for Assets Having Assets Extension |
| F25 | New and Existing Impacted Reports | F25S01 | Asset Addition List Report |
| | | F25S02 | Asset List Report |
| | | F25S03 | Asset Register Report |
| | | F25S04 | Asset Schedule Report |
| | | F25S05 | Asset Disposal Sale Report |
| | | F25S06 | Asset Write-off & Offline Transfer Report |
| | | F25S07 | Asset Valuation Report |
| | | F25S08 | Asset Transaction History Report |
| | | F25S09 | Asset Receivable Report |
| | | F25S10 | Asset Returnable Report |
| | | F25S11 | Asset Tracking Report |
| | | F25S12 | Asset Registration Report |
| | | F25S13 | Asset Depreciation Statement (Serial Wise) Report |
| | | F25S14 | Asset Depreciation Statement (Group Wise) Report |
| | | F25S15 | Asset Depreciation History (Serial Wise) Report |
| | | F25S16 | Asset Depreciation History (Group Wise) Report |

---

## Features

## 1. Asset Serial Global List | F01

### 1.1. A new asset will be added to the Global Asset Serial List upon asset addition from HOFIN | F01S01

**1.1.1. User Story:** As an authorized user, I want the system to create a new asset record in the Global Asset Serial List for every asset addition so that I can access, identify, and track the added asset separately as an individual asset entity.

**1.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Profile from the top menu bar.
- Select and click on the Asset Serial Global List feature.

**1.1.3. Actors:**
- Authorized user.

**1.1.4. Scope:**
- **Current Scope:** Currently the fixed asset management system handles asset additions by simply aggregating the cost of additions with the existing parent asset's price and recalculating the unit price.
- **New Scope:**
  i. The proposed change introduces the concept of creating a separate asset entity under the parent asset for each addition, ensuring better control, traceability, and compliance with accounting standards.

**1.1.5. Pre-condition:**
- Parent asset must already exist and be active.
- Asset addition amount must meet the minimum asset capitalization threshold defined in the system.
- Asset registration must be done with the asset addition condition.

**1.1.6. Impacted Areas:**
- Asset Serial Global List
- Reports:
  i. Asset List
  ii. Asset Register
  iii. Fixed Asset Tracking Report
  iv. Asset Transaction History

**1.1.7. Mock-up/ Prototypes:** N/A

**1.1.8. Requirements:**
- When an asset addition is approved and executed in the fixed asset system, via HOFIN, the system will register the additional asset as a separate standalone asset in the Asset Serial Global List.
  i. A new standalone asset will be listed in the Asset Serial Global List with same serial number of parent asset with hyphen (e.g. BBDASRXXXXXX-1, BBDASRXXXXXX-2).
  ii. Asset will be listed directly in the asset serial global list and can be found individually from the list upon search.
  iii. System must generate a unique Asset Serial Number for each asset addition.
  iv. Parent Asset information for the asset addition will be presented in the added asset's Asset Profile Details pop-up window. [F01S02]
- No impact will be made on the Parent Asset (the asset with which new asset is being added) on the Asset Serial Global List. Purchase value, Written Down Value, Remaining Lifetime, and all the other information will remain unchanged.
- No new asset can be added under an extended asset. Asset addition will only be allowed at the parent asset level.
- When initiating asset addition from the Head Office Finance module, the Asset dropdown must display only Parent Asset serials. Extended assets must not appear in the selection list.
- During asset addition, if the asset (with or without extended asset) is involved in any pending asset transaction, such as Asset Assign, Unassign, Internal Movement, Transaction List, Transaction Approval List, or Asset Assign Acknowledgement, the system will restrict the addition process and will not allow the operation to proceed until the pending transaction is completed. The system will show the following validation messages for these two scenarios:
  - For parent asset in another pending transaction: "Asset addition is not allowed. Parent asset % is pending in another transaction flow."
  - For attempting addition under an extended asset: "Asset addition is not allowed under an extended asset. Reference Asset ID: %."
- During a new extended asset addition, if the parent asset (with/without extended asset) is already within a transaction like Transfer/Shipment/Write-off/Sale then the extended asset addition needs to be restricted in HOFIN module during submission of the request.

**1.1.9. Assumptions:**
- Minimum asset capitalization threshold is defined for the asset groups in the system.

**1.1.10. Non-functional Requirements:** N/A

**1.1.11. Acceptance Criteria:**
- When a user submits an asset addition, the system must generate a new unique Asset Serial Number.
- The newly created asset must appear in the Global Asset Serial List as a separate and standalone asset.

**1.1.12. Exceptions:** N/A

### 1.2. Parent asset information in the Asset Profile Details pop-up window | F01S02

**1.2.1. User Story:** As an authorized user, I want the system to present the parent asset information and the asset addition history in the Asset Profile Details pop-up window so that I can view and track the parent–extended asset relationship of assets and understand the addition history of any asset.

**1.2.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Profile from the top menu bar.
- Select and click on the Asset Serial Global List feature.
- Click on the asset serial number.

**1.2.3. Actors:**
- Authorized user.

**1.2.4. Scope:**
- **Current Scope:** Currently there is no field for parent asset information and no tab particularly for the asset addition history in the Asset Profile Details pop-up window.
- **New Scope:**
  i. A new field will be added to the asset profile details pop-up window named "Parent Asset".
  ii. Asset serial number of parent assets will be shown in the newly added Parent Asset field in the Asset Profile Details of the assets added as an addition to existing assets.
  iii. A new tab will be added to the Asset Profile Details pop-up window named Asset Addition containing the list of added Extended/subsidiary asset added under that particular asset with other relevant information.

**1.2.5. Pre-condition:**
- Asset addition must be acknowledged and approved in the HOFA and HOFIN system respectively.

**1.2.6. Impacted Areas:**
- Asset Global Serial List feature – Asset Profile Details pop-up window.

**1.2.7. Mock-up/ Prototypes:** Figure: Newly added "Parent Asset" field – only for extended assets. Figure: Newly added "Asset Addition History" tab – only for Parent assets.

**1.2.8. Requirements:**
- A new field will be added to the Asset Profile Details pop-up window named "Parent Asset" that will contain the asset serial number of the parent asset.
- The "Parent Asset" field will be visible for only the Extended Assets in the Asset Serial Global List. Only the extended/subsidiary asset will have the parent asset field and information in the Asset Profile Details.
- An additional tab will be added to the Asset Profile Details pop-up window named Addition History. The tab will be available only for the parent asset. No extended/subsidiary asset's Asset Profile Details pop-up window will contain the Asset Addition History tab. The Addition History tab will contain following requirements:
  i. Records per page: User can select the number of entries to view in a single list page from the record per page drop down. The drop-down values will be 10, 20, 50, and 100 with 10 being the default value.
  ii. Asset addition history data grid: Asset addition history data grid will contain the list of asset added to the particular parent assets over the time with:
    a) SL: Serial number for the number of entries in a page.
    b) Asset Serial: Asset serial numbers of the added extended/subsidiary assets under the parent asset. Asset serial number will be hyperlinked to the Asset Profile Details window for the particular extended/subsidiary asset. A pop-up over pop-up layout will be implemented when user clicks on the hyperlinked active extended/subsidiary asset serial number. Closing the latest pop-up will lead the user to exactly previous pop-up or page.
    c) Addition Amount: Price of the added asset.
    d) Addition Date: Date of asset addition registration.
    e) Reference Number: Asset addition registration posted voucher number from HOFIN.
    f) Item Name: Item name of the additional asset.
    g) Acc. Depreciation: Accumulated depreciation of the additional extended/subsidiary assets.
    h) WDV: Written Down Value of the Extended/Subsidiary assets.
  iii. Entries per page: The page will show the range of entries in a given list page out of all the entries in the whole list.
- The Addition History tab will not be populated with data in the data grid if there is no asset added or registered as an asset addition for the particular asset, but the Addition History tab will be visible for all the parent assets in the asset global serial list.
- The Utilization Status of an extended asset can be updated independently without affecting the Utilization Status of its corresponding parent asset.
- However, whenever the Assign/Unassign Status or Utilization Status of the parent asset is updated, the system will automatically synchronize the same status to all associated extended assets, overriding their existing status.

**1.2.9. Assumptions:** N/A

**1.2.10. Non-functional Requirements:** N/A

**1.2.11. Acceptance Criteria:**
- Parent Asset field appears under Details tab for only the extended/subsidiary assets' Asset Profile Details tab.
- Addition History tab is added to the Asset Profile Details pop-up window, and it is visible only for all the parent assets in the asset serial global list.
- All extended/subsidiary assets are accurately listed with details on Asset Serial, Addition Amount, Addition Date, Reference Number, Item Name, Acc. Depreciation, WDV as appropriate.

**1.2.12. Exceptions:** N/A

---

## 2. Asset Assign | F02

### 2.1. New validation will be added on not letting the user select any extended/subsidiary asset | F02S01

**2.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Assign and ensure that when I perform Asset Assign on a parent asset, all associated extended/subsidiary assets automatically be assigned with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**2.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transaction from the top menu bar.
- Select and click on the Asset Assign feature.

**2.1.3. Actors:**
- Authorized user.

**2.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no such validation on extended/subsidiary asset not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will not be able to select the extended/subsidiary assets.
  ii. Only parent assets will be available for selection.
  iii. When a transaction/operation is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.

**2.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**2.1.6. Impacted Areas:**
- Asset Assign
- Transaction List
- Transaction Approval List
- Asset Assign Acknowledgement

**2.1.7. Mock-up/ Prototypes:** Figure omitted.

**2.1.8. Requirements:**
- Extended/subsidiary assets must not appear as selectable individually without the parent asset for asset assign feature when searched via Asset Serial field.
- If the user enters the asset serial number for a extended/subsidiary asset, system will show a validation message stating the selected asset not found.
- When a parent asset is selected, the system must automatically:
  i. Fetch all associated active extended/subsidiary assets and include them in the Asset List of Asset Assign feature.
  ii. For every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button for the extended/subsidiary assets.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  iv. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included list.
  v. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- Upon submission, the system will behave as per current flow and list the transaction as per approval workflow.
- If a parent asset has one or more extended assets already assigned to an employee, any newly registered extended asset under the same parent will be automatically assigned to that same employee through the asset assignment and asset transaction functionality.
- During the asset assignment and transaction process, the system will automatically populate and record the Employee Name, PIN, Building, Floor, and Room details based on the existing assignment information.
- If an asset is already assigned to an employee, any newly added extended asset under that parent will be automatically assigned to the same employee through the asset transaction process, ensuring consistency in asset assignment. Here system will trigger both asset assignment and asset transaction approval automatically in the system.

**2.1.9. Assumptions:** N/A

**2.1.10. Non-functional Requirements:** N/A

**2.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must not appear as selectable individually without the parent asset in the Asset Assign feature when searched via Asset Serial field.
- When a user manually enters an extended/subsidiary asset serial number, the system displays a validation message indicating that extended/subsidiary assets cannot be selected for Asset Assign.
- When a parent asset is selected, the system must automatically fetch and include all associated active extended/subsidiary assets to the Asset List.
- Auto-included extended/subsidiary assets must appear immediately under the parent asset in the Asset List with proper right indentation for visual distinction with no action buttons for the extended/subsidiary assets.
- Users must not be able to deselect or remove any extended/subsidiary asset that is auto included under a parent asset.
- Removing a parent asset from the assignment grid must automatically remove all associated extended/subsidiary assets from the grid.
- Inactive extended/subsidiary assets must not appear in the asset list.
- The system must apply the Asset Assign activity equally to the parent asset and all extended/subsidiary assets in the list.
- The parent asset and its extended/subsidiary assets must appear together in the Transaction List, Transaction Approval List, and Asset Assign Acknowledgement as part of the same transaction.

**2.1.12. Exceptions:**
- Upon Asset Assign, only the currently active and not merged extended/subsidiary assets will be considered for the above-mentioned requirements.

---

## 3. Asset Unassign | F03

### 3.1. New validation will be added on not letting the user select any extended/subsidiary asset | F03S01

**3.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Unassign and ensure that when I perform Asset Unassign on a parent asset, all associated extended/subsidiary assets automatically be unassigned with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**3.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transaction from the top menu bar.
- Select and click on the Asset Unassign feature.

**3.1.3. Actors:**
- Authorized user.

**3.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no such validation on extended/subsidiary asset not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will not be able to select the Extended/subsidiary assets individually.
  ii. Only parent assets will be available for selection.
  iii. When a transaction/operation is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.

**3.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**3.1.6. Impacted Areas:**
- Asset Unassign
- Transaction List
- Transaction Approval List
- Asset Assign Acknowledgement

**3.1.7. Mock-up/ Prototypes:** Figures omitted (Asset List for Asset Unassign via asset serial and via employee PIN).

**3.1.8. Requirements:**
- Extended/subsidiary assets must not appear as selectable individually without the parent asset for asset unassign feature when searched via Asset Serial field.
- If the user enters the asset serial number for a extended/subsidiary asset, system will show a validation message stating the selected asset not found.
- When a parent asset is selected, the system must automatically:
  i. Fetch all associated extended/subsidiary assets and include them in the Asset List of Asset Unassign feature.
  ii. For every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button for the extended/subsidiary assets.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  iv. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included asset list.
  v. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- Asset List will be impacted in a similar way as mentioned above for the Search By employee PIN option as well.
- Upon submission, the system will behave as per current flow and list the transaction as per approval workflow.

**3.1.9. Assumptions:** N/A

**3.1.10. Non-functional Requirements:** N/A

**3.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must not appear as selectable individually without the parent asset in the Asset Unassign feature when searched via Asset Serial field.
- When a user manually enters a extended/subsidiary asset serial number, the system is displaying a validation message indicating that extended/subsidiary assets cannot be selected for Asset Unassign.
- When a parent asset is selected, the system must automatically fetch and include all associated active extended/subsidiary assets to the Asset List.
- Auto-included extended/subsidiary assets must appear immediately under the parent asset in the Asset List with proper right indentation for visual distinction with no action buttons for the extended/subsidiary assets.
- Users must not be able to deselect or remove any extended/subsidiary asset that is auto-included under a parent asset.
- Removing a parent asset from the assignment grid must automatically remove all associated extended/subsidiary assets from the grid.
- Inactive extended/subsidiary assets must not appear in the asset list.
- The system must apply the Asset Unassign activity equally to the parent asset and all extended/subsidiary assets in the list.
- The parent asset and its extended/subsidiary assets must appear together in the Transaction List, Transaction Approval List, and Asset Assign Acknowledgement as part of the same transaction.

**3.1.12. Exceptions:**
- Upon Asset Unassign, only the currently active and not merged extended/subsidiary assets will be considered for the above-mentioned requirements.

---

## 4. Internal Movement | F04

### 4.1. New validation will be added on not letting the user select any extended/subsidiary asset | F04S01

**4.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Internal Movement and ensure that when I perform Asset Internal Movement on a parent asset, all associated extended/subsidiary assets automatically move with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**4.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transaction from the top menu bar.
- Select and click on the Asset Internal Movement feature.

**4.1.3. Actors:**
- Authorized user.

**4.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no such validation on extended/subsidiary asset not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will not be able to select the Extended/subsidiary assets individually.
  ii. Only parent assets will be available for selection.
  iii. When a transaction/operation is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.

**4.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**4.1.6. Impacted Areas:**
- Asset Internal Movement
- Transaction List
- Transaction Approval List

**4.1.7. Mock-up/ Prototypes:** Figures omitted (Asset List for Asset Internal Movement via asset serial and via employee PIN).

**4.1.8. Requirements:**
- Extended/subsidiary assets must not appear as selectable individually without the parent asset for asset internal movement feature when searched via Asset Serial field.
- If the user enters the asset serial number for a extended/subsidiary asset, system will show a validation message stating the selected asset not found.
- When a parent asset is selected, the system must automatically:
  i. Fetch all associated active extended/subsidiary assets and include them in the Asset List of Asset Internal Movement feature.
  ii. For every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button for the extended/subsidiary assets.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  iv. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included asset list.
  v. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- Asset List will be impacted in a similar way as mentioned above for the Search By employee PIN option as well.
- Upon submission, the system will behave as per current flow and list the transaction as per approval workflow.

**4.1.9. Assumptions:** N/A

**4.1.10. Non-functional Requirements:** N/A

**4.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must not appear as selectable individually without the parent asset in the Asset Internal Movement feature when searched via Asset Serial field.
- When a user manually enters a extended/subsidiary asset serial number, the system is displaying a validation message indicating that extended/subsidiary assets cannot be selected for Asset Internal Movement.
- When a parent asset is selected, the system must automatically fetch and include all associated active extended/subsidiary assets to the Asset List.
- Auto-included extended/subsidiary assets must appear immediately under the parent asset in the Asset List with right indentation for visual distinction with no action buttons for the extended/subsidiary assets.
- Users must not be able to deselect or remove any extended/subsidiary asset that is auto-included under a parent asset.
- Removing a parent asset from the assignment grid must automatically remove all associated extended/subsidiary assets from the grid.
- Inactive extended/subsidiary assets must not appear in the asset list.
- The system must apply the Asset Internal Movement activity equally to the parent asset and all extended/subsidiary assets in the list.
- The parent asset and its extended/subsidiary assets must appear together in the Transaction List and Transaction Approval List, as part of the same transaction.

**4.1.12. Exceptions:**
- Upon Asset Internal Movement, only the currently active and not merged extended/subsidiary assets will be considered for the above mentioned requirements.

---

## 5. Transaction List | F05

### 5.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F05S01

**5.1.1. User Story:** As an authorized user, I want the system to show the extended/subsidiary assets immediately below their respective parent asset with right indentation in asset serial number and no list serial number for list pages so that I can visually distinguish the extended/subsidiary assets from the parent assets in a list.

**5.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transaction from the top menu bar.
- Select and click on the Transaction List feature.
- Click on the Details button from the Transaction List of Asset Assign/Un Assign/Internal Movement data grid.

**5.1.3. Actors:**
- Authorized user.

**5.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no distinctions between them.
- **New Scope:**
  i. In a given list page, where there might be parent asset as well as extended/subsidiary assets, the system will present the extended/subsidiary assets with no list Sl. Number and with the asset serial number being indented towards right side for visual distinction.

**5.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**5.1.6. Impacted Areas:**
- Asset Transaction Details (Assign/UnAssign/Internal Movement) pop-up window.

**5.1.7. Mock-up/ Prototypes:** Figure omitted.

**5.1.8. Requirements:**
- When both parent and extended/assets in the list page, the list will show following behavior:
  i. For every parent asset in the list with extended/subsidiary asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/Subsidiary asset will not contain any list SL No.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**

**5.1.9. Assumptions:** N/A

**5.1.10. Non-functional Requirements:** N/A

**5.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must appear immediately below their respective parent asset in the Transaction List.
- Extended/subsidiary assets must not display any List Serial Number (SL No.) in the list view.
- The asset serial number of every extended/subsidiary asset must be visually indented to the right to distinguish it from parent assets.
- Only active extended/subsidiary assets must appear under the parent asset.

**5.1.12. Exceptions:**
- Only the currently active and not merged extended/subsidiary assets will be listed in list pages.

---

## 6. Transaction Approval List | F06

### 6.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F06S01

**6.1.1. User Story:** As an authorized user, I want the system to show the extended/subsidiary assets immediately below their respective parent asset with right indentation in asset serial number and no list serial number for list pages so that I can visually distinguish the extended/subsidiary assets from the parent assets in a list.

**6.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transaction from the top menu bar.
- Select and click on the Transaction Approval List feature.
- Click on the Details button from the Approval List of Transaction (Assign/UnAssign/Internal Movement) data grid.

**6.1.3. Actors:**
- Authorized user.

**6.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no distinctions between them.
- **New Scope:**
  i. In a given list page, where there might be parent asset as well as extended/subsidiary assets, the system will present the extended/subsidiary assets with no list Sl. Number and with the asset serial number being indented towards right side for visual distinction.

**6.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**6.1.6. Impacted Areas:**
- Asset Transaction Details (Assign/UnAssign/Internal Movement) pop-up window.

**6.1.7. Mock-up/ Prototypes:** Figure omitted.

**6.1.8. Requirements:**
- When both parent and extended/assets in the list page, the list will show following behavior:
  i. For every parent asset in the list with extended/subsidiary asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/Subsidiary asset will not contain any list SL No.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**

**6.1.9. Assumptions:** N/A

**6.1.10. Non-functional Requirements:** N/A

**6.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must appear immediately below their respective parent asset in the Transaction Approval List.
- Extended/subsidiary assets must not display any List Serial Number (SL No.) in the list view.
- The asset serial number of every extended/subsidiary asset must be visually indented to the right to distinguish it from parent assets.
- Only active extended/subsidiary assets must appear under the parent asset.

**6.1.12. Exceptions:**
- Only the currently active and not merged extended/subsidiary assets will be listed in list pages.

---

## 7. Asset Assign Acknowledgement | F07

### 7.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F07S01

**7.1.1. User Story:** As an authorized user, I want the system to show the extended/subsidiary assets immediately below their respective parent asset with right indentation in asset serial number and no list serial number for list pages so that I can visually distinguish the extended/subsidiary assets from the parent assets in a list.

**7.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transaction from the top menu bar.
- Select and click on the Asset Assign acknowledgement feature.
- Click on the Details button from the Details column of the Pending Asset Acknowledgement data grid.

**7.1.3. Actors:**
- Authorized user.

**7.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no distinctions between them.
- **New Scope:**
  i. In a given list page, where there might be parent assets as well as extended/subsidiary assets, the system will present the extended/subsidiary assets with no list serial number (SL.) and with the asset serial number being indented towards right side for visual distinction.

**7.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**7.1.6. Impacted Areas:**
- Asset Transaction Details (Assign/UnAssign/Internal Movement) pop-up window.

**7.1.7. Mock-up/ Prototypes:** Figure omitted.

**7.1.8. Requirements:**
- When both parent and extended/assets in the list page, the list will show following behavior:
  i. For every parent asset in the list with extended/subsidiary asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/Subsidiary asset will not contain any list serial number (SL.).
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**

**7.1.9. Assumptions:** N/A

**7.1.10. Non-functional Requirements:** N/A

**7.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must appear immediately below their respective parent asset in the Asset Transaction Details (Assign/UnAssign/Internal Movement) pop-up window of Asset Assign Acknowledgement feature.
- Extended/subsidiary assets must not display any List Serial Number (SL No.) in the list view.
- The asset serial number of every extended/subsidiary asset must be visually indented to the right to distinguish it from parent assets.
- Only active extended/subsidiary assets appear under the parent asset.

**7.1.12. Exceptions:**
- Only the currently active and not merged extended/subsidiary assets will be listed in list pages.

---

## 8. Asset Shipment | F08

### 8.1. New validation will be added on not letting the user select any extended/subsidiary asset | F08S01

**8.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Shipment Challan and ensure that when I perform Asset Transfer via Shipment on a parent asset, all associated extended/subsidiary assets automatically be transferred to the destination project/branch with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**8.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transfer from the top menu bar.
- Select and click on the Asset Shipment feature.
- Click on the shipment number hyperlinked.
- Select the Add Serial Tab for directly adding the asset serial or select the Transfer Challan tab to access a particular challan and then click on the Add Serial button to open Add Asset Serial pop-up window.

**8.1.3. Actors:**
- Authorized user.

**8.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no such validation on extended/subsidiary asset not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will not be able to select the Extended/subsidiary assets.
  ii. Only parent assets will be available for selection.
  iii. When a transfer is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.
  iv. During any shipment transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**8.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**8.1.6. Impacted Areas:**
- Asset Shipment
- Asset Shipment Challan Approval List
- Asset Shipment In Challan

**8.1.7. Mock-up/ Prototypes:** Figures omitted (Add Serial tab under Shipment Details; Add Serial tab and Add Asset Serial pop-up under Challan Details).

**8.1.8. Requirements:**
- For the **Add Serial tab** in the Shipment Details of the Asset Shipment feature:
  i. Asset Serial No. drop-down field will only list the Parent Assets.
  ii. No extended/subsidiary asset should be shown in the drop-down values of the Asset Serial No. field.
  iii. When a user selects a parent asset with extended/subsidiary assets via Add button, the system will record and show the quantity for the parent asset only and will fetch all associated extended/subsidiary assets and include them in the asset serial list data grid below the Asset Serial Details section.
  iv. In the Asset Serial List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  v. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  vi. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  vii. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included list.
  viii. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- For the **Add Serial tab** (Asset Shipment feature > Shipment No. (hyperlinked) > Transfer Challans tab > Out Challan No. > Add Serial):
  i. In the Asset Serial data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- For the **Add Asset Serial pop-up window** (Asset Shipment feature > Shipment No. (hyperlinked) > Transfer Challans tab > Out Challan No. > Add Serial button from Item Details Data grid):
  i. Serial No. drop-down field will only list the Parent Assets.
  ii. No extended/subsidiary asset should be shown in the drop-down values of the Serial No. field.
  iii. When a user selects a parent asset with extended/subsidiary assets via Add button, the system will fetch all associated extended/subsidiary assets and include them in the asset serial list data grid below the Asset Serial Details section.
  iv. In the Asset Serial List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  v. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  vi. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  vii. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included list.
  viii. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- Fixed asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- During a new extended asset addition, if the parent asset (with/without extended asset) is already within a transaction like Transfer/Shipment/Write-off/Sale then the extended asset addition needs to be restricted in HOFIN module during submission of the request.
- During a new extended asset addition, when it is already acknowledged in HOFA but pending approval in HOFIN the parent asset (with/without extended asset) will be restricted from transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During a new extended asset addition, when acknowledgement is pending in HOFA then the parent asset (with/without extended asset) will be restricted for transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.

**8.1.9. Assumptions:** N/A

**8.1.10. Non-functional Requirements:** N/A

**8.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must not appear as selectable in the Asset Serial No. or Serial No. dropdown fields in both the Add Serial tab and Add Asset Serial pop-up window.
- When a user manually enters or attempts to select a extended/subsidiary asset, the system must prevent the selection and allow only valid parent assets to be added.
- When a parent asset is added through the Add button, the system must automatically fetch all associated extended/subsidiary assets and include them in the Asset Serial List data grid.
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.
- No action button (remove/delete) must be available for the auto-included extended/subsidiary assets in any grid or pop-up window.
- Users must not be able to deselect or remove extended/subsidiary assets at any stage of the shipment process.
- Removing or deleting a parent asset from the list/grid must automatically remove the associated extended/subsidiary assets as well.
- The system must correctly transfer both the parent asset and all auto-included active extended/subsidiary assets to the destination project/branch as part of the same shipment/shipment challan transaction.
- The system must maintain the parent–extended grouping structure throughout the shipment workflow, including the Shipment Details pop-up windows and Shipment Challans.

**8.1.12. Exceptions:**
- On Asset Shipment, only the currently active and not merged extended/subsidiary assets will be considered for the above-mentioned requirements.

---

## 9. Asset Shipment Challan Approval List | F09

### 9.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F09S01

**9.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset transfers via shipment.

**9.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transfer from the top menu bar.
- Select and click on the Asset Shipment Approval List feature.
- Click on the shipment number hyperlinked.
- Click on the Show Serial button to open Show Asset Serial pop-up window.

**9.1.3. Actors:**
- Authorized user.

**9.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.

**9.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**9.1.6. Impacted Areas:** N/A

**9.1.7. Mock-up/ Prototypes:** Figure omitted.

**9.1.8. Requirements:**
- For the Show Asset Serial pop-up window under Shipment Challan Details pop-up window:
  i. In the Asset Serial Details data grid, for every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- Fixed asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**9.1.9. Assumptions:** N/A

**9.1.10. Non-functional Requirements:** N/A

**9.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**9.1.12. Exceptions:**
- Upon Asset Shipment, only the currently active and not merged extended/subsidiary assets will be considered for the above-mentioned requirements.

---

## 10. Asset Shipment In-Challan | F10

### 10.1. New validation will be added on not letting the user select any extended/subsidiary asset | F10S01

**10.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Shipment In-Challan and ensure that when I receive a parent asset via Asset Shipment Transfer, all associated extended/subsidiary assets automatically be received to the destination project/branch with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**10.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Transfer from the top menu bar.
- Select and click on the Asset Shipment In-Challan feature.
- Click on the shipment number hyperlinked.
- Click on the Show Serial button to open Add Asset Serial pop-up window.

**10.1.3. Actors:**
- Authorized user.

**10.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no such validation on extended/subsidiary asset not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will not be able to select the Extended/subsidiary assets.
  ii. Only parent assets will be available for selection.
  iii. When a transfer receive is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.
  iv. During any shipment, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**10.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**10.1.6. Impacted Areas:**
- Asset Serial Global List

**10.1.7. Mock-up/ Prototypes:** Figure omitted.

**10.1.8. Requirements:**
- For the Add Asset Serial pop-up window under the In Challan Details pop-up window:
  i. Serial No. drop-down field will only list the Parent Assets.
  ii. No extended/subsidiary asset should be shown in the drop-down values of the Serial No. field.
  iii. When a user selects a parent asset with extended/subsidiary assets via Add button, the system will fetch all associated extended/subsidiary assets and include them in the asset serial list data grid below the Asset Serial Details section.
  iv. In the Asset Serial List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  v. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  vi. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  vii. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included list.
  viii. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- Upon successful acknowledgement of the shipment in-challan that contains parent and extended/subsidiary assets in it, the extended/subsidiary asset(s) will also be listed in the asset serial global list of the destined project/branch and will contain all the behavior and validations related to the extended/subsidiary assets while being tagged with the parent asset in the destined project/branch.
- Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- During a new extended asset addition, if the parent asset (with/without extended asset) is already within a transaction like Transfer/Shipment/Write-off/Sale then the extended asset addition needs to be restricted in HOFIN module during submission of the request.
- During a new extended asset addition, when it is already acknowledged in HOFA but pending approval in HOFIN the parent asset (with/without extended asset) will be restricted from transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During a new extended asset addition, when acknowledgement is pending in HOFA then the parent asset (with/without extended asset) will be restricted for transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.

**10.1.9. Assumptions:** N/A

**10.1.10. Non-functional Requirements:** N/A

**10.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must not appear as selectable in the Serial No. dropdown field in the Add Asset Serial pop-up window.
- When a user manually enters or attempts to select a extended/subsidiary asset, the system must prevent the selection and allow only valid parent assets to be added.
- When a parent asset is added through the Add button, the system must automatically fetch all associated extended/subsidiary assets and include them in the Asset Serial List data grid.
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.
- No action button (remove/delete) must be available for the auto-included extended/subsidiary assets in any grid or pop-up window.
- Users must not be able to deselect or remove extended/subsidiary assets at any stage of the shipment process.
- Removing or deleting a parent asset from the list/grid must automatically remove its associated extended/subsidiary assets as well.
- The system must correctly transfer both the parent asset and all auto-included active extended/subsidiary assets to the destination project/branch as part of the same shipment/shipment challan transaction.
- The system must maintain the parent–extended grouping structure throughout the shipment workflow, including the Shipment Details pop-up windows and Shipment Challans.

**10.1.12. Exceptions:** N/A

---

## 11. Asset Single Out Challan | F11

### 11.1. New validation will be added on not letting the user select any extended/subsidiary asset | F11S01

**11.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Single Out Challan and ensure that when I perform Asset Transfer via Single Out Challan on a parent asset, all associated extended/subsidiary assets automatically be transferred to the destination project/branch with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**11.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Single Challan from the top menu bar.
- Select and click on the Asset Single Out Challan feature.
- Click on the out-challan number hyperlinked.
- Click on the Add Serial/Show Serial button to open Add Asset Serial pop-up window.

**11.1.3. Actors:**
- Authorized user.

**11.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary relationship that exists in the system hence there is no such validation on extended/subsidiary assets not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will not be able to select the Extended/subsidiary assets.
  ii. Only parent assets will be available for selection.
  iii. When a transfer is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.
  iv. Extended/Subsidiary assets will be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  v. During any challan, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**11.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**11.1.6. Impacted Areas:**
- Asset Single Out Challan
- Asset Single Out Challan Approval List
- Asset Single In Challan
- Asset Receivables List
- Asset Returnable List

**11.1.7. Mock-up/ Prototypes:** Figures omitted.

**11.1.8. Requirements:**
- For the **Add Asset Serial pop-up window** under Single Challan/Memo Detail pop-up window via Add Serial button:
  i. Asset Serial No. drop-down field will only list the Parent Assets.
  ii. No extended/subsidiary asset should be shown in the drop-down values of the Asset Serial No. field.
  iii. When a user selects a parent asset with extended/subsidiary assets via Add button, the system will fetch all associated extended/subsidiary assets and include them in the asset serial list data grid in the Asset Serial Details section.
  iv. In the Asset Serial List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  v. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  vi. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  vii. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included list.
  viii. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- For the **Add Asset Serial pop-up window** under Single Challan/Memo Detail pop-up window via Show Serial button:
  i. In the Asset Serial data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- For the **Add Serial tab** under Single Challan/Memo Detail pop-up window:
  i. In the Asset Serial data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- During a new extended asset addition, if the parent asset (with/without extended asset) is already within a transaction like Transfer/Shipment/Write-off/Sale then the extended asset addition needs to be restricted in HOFIN module during submission of the request.
- During a new extended asset addition, when it is already acknowledged in HOFA but pending approval in HOFIN the parent asset (with/without extended asset) will be restricted from transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During a new extended asset addition, when acknowledgement is pending in HOFA then the parent asset (with/without extended asset) will be restricted for transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.

**11.1.9. Assumptions:** N/A

**11.1.10. Non-functional Requirements:** N/A

**11.1.11. Acceptance Criteria:**
- Extended/subsidiary assets must not appear as selectable in the Asset Single Out Challan feature.
- When a user manually enters or attempts to select a extended/subsidiary asset, the system must prevent the selection and allow only valid parent assets to be added.
- When a parent asset is added through the Add button, the system must automatically fetch all associated extended/subsidiary assets and include them in the Asset Serial List data grid.
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.
- No action button (remove/delete) must be available for the auto-included extended/subsidiary assets in any grid or pop-up window.
- Users must not be able to deselect or remove extended/subsidiary assets at any stage of the shipment process.
- Removing or deleting a parent asset from the list/grid must automatically remove its associated extended/subsidiary assets as well.
- The system must correctly transfer both the parent asset and all auto-included active extended/subsidiary assets to the destination project/branch as part of the same challan.

**11.1.12. Exceptions:** N/A

---

## 12. Asset Single Out Challan Approval List | F12

### 12.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F12S01

**12.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset transfers via shipment.

**12.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Single Challan from the top menu bar.
- Select and click on the Asset Single Out Challan Approval List feature.
- Click on the Single Out Challan number hyperlinked.
- Click on the Show Serial button to open Add Asset Serial pop-up window.

**12.1.3. Actors:**
- Authorized user.

**12.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.

**12.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**12.1.6. Impacted Areas:** N/A

**12.1.7. Mock-up/ Prototypes:** Figure omitted.

**12.1.8. Requirements:**
- For the Add Asset Serial pop-up window under Shipment Challan Details pop-up window:
  i. In the Asset Serial Details data grid, for every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**12.1.9. Assumptions:** N/A

**12.1.10. Non-functional Requirements:** N/A

**12.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**12.1.12. Exceptions:** N/A

---

## 13. Asset Single In-Challan | F13

### 13.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F13S01

**13.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset transfers via shipment.

**13.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Single Challan from the top menu bar.
- Select and click on the Asset Single In-Challan feature.
- Click on the Single Out Challan number hyperlinked.
- Click on the Show Serial button to open Add Asset Serial pop-up window.

**13.1.3. Actors:**
- Authorized user.

**13.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.
  ii. During any challan transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**13.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**13.1.6. Impacted Areas:** N/A

**13.1.7. Mock-up/ Prototypes:** Figure omitted.

**13.1.8. Requirements:**
- For the Add Asset Serial pop-up window under Shipment Challan Details pop-up window:
  i. In the Asset Serial Details data grid, for every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- During challan transaction, Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- During a new extended asset addition, if the parent asset (with/without extended asset) is already within a transaction like Transfer/Shipment/Write-off/Sale then the extended asset addition needs to be restricted in HOFIN module during submission of the request.
- During a new extended asset addition, when it is already acknowledged in HOFA but pending approval in HOFIN the parent asset (with/without extended asset) will be restricted from transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During a new extended asset addition, when acknowledgement is pending in HOFA then the parent asset (with/without extended asset) will be restricted for transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.

**13.1.9. Assumptions:** N/A

**13.1.10. Non-functional Requirements:** N/A

**13.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**13.1.12. Exceptions:** N/A

---

## 14. Asset Receivable List | F14

### 14.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F14S01

**14.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset transfers via shipment.

**14.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Single Challan from the top menu bar.
- Select and click on the Asset Receivables List feature.

**14.1.3. Actors:**
- Authorized user.

**14.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.

**14.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**14.1.6. Impacted Areas:** N/A

**14.1.7. Mock-up/ Prototypes:** Figure omitted.

**14.1.8. Requirements:**
- For the Add Asset Receivables List data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**

**14.1.9. Assumptions:** N/A

**14.1.10. Non-functional Requirements:** N/A

**14.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**14.1.12. Exceptions:** N/A

---

## 15. Asset Returnable List | F15

### 15.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F15S01

**15.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset transfers via shipment.

**15.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Single Challan from the top menu bar.
- Select and click on the Asset Returnable List feature.

**15.1.3. Actors:**
- Authorized user.

**15.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.

**15.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**15.1.6. Impacted Areas:** N/A

**15.1.7. Mock-up/ Prototypes:** Figure omitted.

**15.1.8. Requirements:**
- For the Add Asset Returnable List data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**

**15.1.9. Assumptions:** N/A

**15.1.10. Non-functional Requirements:** N/A

**15.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**15.1.12. Exceptions:** N/A

---

## 16. Asset Expenditure | F16

### 16.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F16S01

**16.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborate view of the asset expenditure.

**16.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Expenditure from the top menu bar.
- Select and click on the Asset Expenditure feature.

**16.1.3. Actors:**
- Authorized user.

**16.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.

**16.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**16.1.6. Impacted Areas:**
- Asset Expenditure

**16.1.7. Mock-up/ Prototypes:** Figure omitted (List of Asset data grid in Asset Expenditure Details pop-up window).

**16.1.8. Requirements:**
- For List of Asset data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  iv. In asset serial field, there will be no extended asset serial can be fetched if searched. Users can input expense for both asset and extended assets.
  v. Assets having only 'IN USE' status will be shown in the list.

**16.1.9. Assumptions:** N/A

**16.1.10. Non-functional Requirements:** N/A

**16.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**16.1.12. Exceptions:** N/A

---

## 17. Asset Expenditure Approval | F17

### 17.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F17S01

**17.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset expenditure approval.

**17.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Expenditure from the top menu bar.
- Select and click on the Asset Expenditure Approval List feature.

**17.1.3. Actors:**
- Authorized user.

**17.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.
  ii. During asset expense transactions, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**17.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**17.1.6. Impacted Areas:**
- Asset Sale Approval List

**17.1.7. Mock-up/ Prototypes:** Figure omitted.

**17.1.8. Requirements:**
- For List of Asset data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- During asset expenditure transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**17.1.9. Assumptions:** N/A

**17.1.10. Non-functional Requirements:** N/A

**17.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**17.1.12. Exceptions:** N/A

---

## 18. Asset Write Off | F18

### 18.1. New validation will be added on not letting the user select any extended/subsidiary asset | F18S01

**18.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Disposal Write off and ensure that when I perform Asset Disposal via Write off on a parent asset, all associated extended/subsidiary assets automatically be disposed with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**18.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Disposal from the top menu bar.
- Select and click on the Asset Write-Off feature.

**18.1.3. Actors:**
- Authorized user.

**18.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no such validation on extended/subsidiary asset not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will not be able to select the Extended/subsidiary assets.
  ii. Only parent assets will be available for selection.
  iii. When a transfer is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.
  iv. Extended/Subsidiary assets will be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  v. During any write-off, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**18.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**18.1.6. Impacted Areas:**
- Asset Write-Off
- Asset Write-Off List
- Asset Write-Off Approval List

**18.1.7. Mock-up/ Prototypes:** Figures omitted.

**18.1.8. Requirements:**
- For asset disposal via Write-Off purpose:
  i. **One By One:** The Asset Serial dropdown will display both parent assets and extended (child) assets. During single (one-by-one) processing, the system will validate whether the selected asset is a parent or an extended asset and will not allow the selection of both types within the same request. Users may select extended assets independently and execute the operation accordingly. However, if a parent asset is selected, the system will automatically include all associated extended (child) assets in the operation.
  ii. **Bulk Operation:** During bulk upload via the Excel template, the system will validate whether the uploaded data contains extended (subsidiary) assets, either individually or along with their corresponding parent assets. If a parent asset is included in the file, the system will verify that all associated extended (subsidiary) assets under that parent are also included in the upload. If any required extended assets are missing, the system will restrict the upload and display a validation message such as:
  > "Invalid asset serial(s). Please correct the following data and upload again: [Parent Asset Serial] has missing extended/subsidiary asset(s)."
- When a user selects a parent asset with extended/subsidiary assets via Add button for One-by-One upload or via excel upload, the system will fetch all associated extended/subsidiary assets and include them in the Asset List data grid.
- For Asset List data grid:
  i. In the Asset List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  iv. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove an extended asset from the auto-included list.
  v. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- During any write-off transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- For assets, the write-off of an extended asset can be performed independently, without requiring the parent asset to be written off. To do so, the system will consider Utilization Status other than "IN_USE" and Assigned status to be "Unassigned".
- During a new extended asset addition, if the parent asset (with/without extended asset) is already within a transaction like Transfer/Shipment/Write-off/Sale then the extended asset addition needs to be restricted in HOFIN module during submission of the request.
- During a new extended asset addition, when it is already acknowledged in HOFA but pending approval in HOFIN the parent asset (with/without extended asset) will be restricted from transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During a new extended asset addition, when acknowledgement is pending in HOFA then the parent asset (with/without extended asset) will be restricted for transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During the asset addition, if extended asset is in progress for disposal (utilization status changed or submitted for disposal) Parent asset (with/without extended asset) will be restricted for any transaction like Shipment/Challan/Disposal.

**18.1.9. Assumptions:** N/A

**18.1.10. Non-functional Requirements:** N/A

**18.1.11. Acceptance Criteria:**
- The Asset Serial dropdown field in the One-by-One write-off process must only display parent assets, and no extended or subsidiary asset may appear in the dropdown list.
- When uploading asset serials through the Excel bulk upload template, the system is validating the file and preventing completion of the upload if any extended or subsidiary assets are included, displaying a validation message with the invalid extended/subsidiary serial numbers from the file.
- When a parent asset is selected for write-off (in both One-by-One and bulk upload processes), the system must automatically fetch all associated active extended/subsidiary assets and include them in the Asset List data grid.
- In the Asset List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
- Removing a parent asset from the Asset List grid must automatically remove all associated extended/subsidiary assets from the list.
- The system must dispose of the parent asset and all auto-included extended/subsidiary assets together as part of the same write-off transaction.
- After submission, the write-off transaction must follow the existing approval workflow, and parent and extended/subsidiary assets must appear together in all downstream transactions and approval records.

**18.1.12. Exceptions:** N/A

---

## 19. Asset Write Off List | F19

### 19.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F19S01

**19.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset transfers via shipment.

**19.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Disposal from the top menu bar.
- Select and click on the Asset Write-Off List feature.

**19.1.3. Actors:**
- Authorized user.

**19.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.

**19.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**19.1.6. Impacted Areas:**
- Asset Write-Off List

**19.1.7. Mock-up/ Prototypes:** Figure omitted (List of Asset data grid in Asset Write Off Details pop-up window).

**19.1.8. Requirements:**
- For List of Asset data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- For assets, the write-off of an extended asset can be performed independently, without requiring the parent asset to be written off. To do so, the system will consider Utilization Status other than "IN_USE" and Assigned status to be "Unassigned".

**19.1.9. Assumptions:** N/A

**19.1.10. Non-functional Requirements:** N/A

**19.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**19.1.12. Exceptions:** N/A

---

## 20. Asset Write Off Approval List | F20

### 20.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F20S01

**20.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset transfers via shipment.

**20.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Disposal from the top menu bar.
- Select and click on the Asset Write-Off Approval List feature.

**20.1.3. Actors:**
- Authorized user.

**20.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.
  ii. During any write-off transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**20.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**20.1.6. Impacted Areas:**
- Asset Write-Off Approval List

**20.1.7. Mock-up/ Prototypes:** Figure omitted.

**20.1.8. Requirements:**
- For List of Asset data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- During any write-off transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- For assets, the write-off of an extended asset can be performed independently, without requiring the parent asset to be written off. To do so, the system will consider Utilization Status other than "IN_USE" and Assigned status to be "Unassigned".

**20.1.9. Assumptions:** N/A

**20.1.10. Non-functional Requirements:** N/A

**20.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**20.1.12. Exceptions:** N/A

---

## 21. Asset Sale | F21

### 21.1. New validation will be added on not letting the user select any extended/subsidiary asset | F21S01

**21.1.1. User Story:** As an authorized user, I want the system to prevent extended/subsidiary assets from being selected for Asset Disposal Sale and ensure that when I perform Asset Disposal via Sale on a parent asset, all associated extended/subsidiary assets automatically be disposed with the parent asset, so that the asset hierarchy remains consistent, and parent-extended/subsidiary asset relationship is maintained appropriately across the system.

**21.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Disposal from the top menu bar.
- Select and click on the Asset Sale feature.

**21.1.3. Actors:**
- Authorized user.

**21.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system hence there is no such validation on extended/subsidiary asset not being selected and any activity on parent asset to impact extended/subsidiary asset as well.
- **New Scope:**
  i. The user will be able to select the Extended/subsidiary assets.
  ii. Parent assets will be available for selection as well.
  iii. When a transfer is completed with parent asset, the transaction/operation will also impact the extended/subsidiary asset to that particular parent asset similarly.
  iv. Extended/Subsidiary assets will be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  v. During asset sale transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**21.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**21.1.6. Impacted Areas:**
- Asset Sale
- Asset Sale List
- Asset Sale Approval List

**21.1.7. Mock-up/ Prototypes:** Figures omitted.

**21.1.8. Requirements:**
- For asset disposal via Sale purpose:
  i. **One By One:** The Asset Serial dropdown will display both parent assets and extended assets. During single (one-by-one) processing, the system will validate whether the selected asset is a parent or an extended asset and will not allow the selection of both types within the same request. Users may select extended assets independently and execute the operation accordingly. However, if a parent asset is selected, the system will automatically include all associated extended (child) assets in the operation.
  ii. **Bulk Operation:** During bulk upload via the Excel template, the system will validate whether the uploaded data contains extended (subsidiary) assets, either individually or along with their corresponding parent assets. If a parent asset is included in the file, the system will verify that all associated extended (subsidiary) assets under that parent are also included in the upload. If any required extended assets are missing, the system will restrict the upload and display a validation message such as:
  > "Invalid asset serial(s). Please correct the following data and upload again: [Parent Asset Serial] has missing extended/subsidiary asset(s)."
- When a user selects a parent asset with extended/subsidiary assets via Add button for One-by-One upload or via excel upload, the system will fetch all associated extended/subsidiary assets and include them in the Asset List data grid.
- For Asset List data grid:
  i. In the Asset List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
  iv. No action button will be available for the extended/subsidiary assets. Users cannot deselect or remove a extended asset from the auto-included list.
  v. Any activity on the parent asset, such as removing the parent asset from the grid, will have a similar impact on the extended/subsidiary asset as well.
- During asset sale transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- For assets, the sale of an extended asset can be performed independently, without requiring the parent asset to be sale.
- The Gain/Loss will be calculated based on the total sale price of the asset. The system will first allocate the full sale price to the parent asset and calculate its Gain/Loss. Any remaining sale value will then be gradually distributed among the extended (child) assets, and Gain/Loss will be calculated sequentially for each child asset based on the allocated amount. An example scenario is provided below for better understanding.

  **Total Sale amount assigned to Parent asset then gradually extended assets**

  | Asset | Purchase Price | WDV | Sale Price | Gain/Loss |
  |---|---|---|---|---|
  | Parent Asset | 33000 | 33000 | 180000 | 147000 |
  | Extended Asset 1 | 25000 | 1000 | 0 | -1000 |
  | Extended Asset 2 | 20000 | 2000 | 0 | -2000 |

- During a new extended asset addition, if the parent asset (with/without extended asset) is already within a transaction like Transfer/Shipment/Write-off/Sale then the extended asset addition needs to be restricted in HOFIN module during submission of the request.
- During a new extended asset addition, when it is already acknowledged in HOFA but pending approval in HOFIN the parent asset (with/without extended asset) will be restricted from transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During a new extended asset addition, when acknowledgement is pending in HOFA then the parent asset (with/without extended asset) will be restricted for transactions like Transfer/Shipment/Write-off/Sale in fixed asset module.
- During the asset addition, if extended asset is in progress for disposal (utilization status changed or submitted for disposal) Parent asset (with/without extended asset) will be restricted for any transaction like Shipment/Challan/Disposal.

**21.1.9. Assumptions:** N/A

**21.1.10. Non-functional Requirements:** N/A

**21.1.11. Acceptance Criteria:**
- The Asset Serial dropdown field in the One-by-One Sale Disposal process must only display parent assets, and no extended or subsidiary asset may appear in the dropdown list.
- When uploading asset serials through the Excel bulk upload template, the system is validating the file and preventing completion of the upload if any extended or subsidiary assets are included, displaying a validation message with the invalid extended/subsidiary serial numbers from the file.
- When a parent asset is selected for Sale Disposal (in both One-by-One and bulk upload processes), the system must automatically fetch all associated active extended/subsidiary assets and include them in the Asset List data grid.
- In the Asset List data grid, for every parent asset selected, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
- Removing a parent asset from the Asset List grid must automatically remove all associated extended/subsidiary assets from the list.
- The system must dispose of the parent asset and all auto-included extended/subsidiary assets together as part of the same Disposal Sale transaction.
- After submission, the Disposal Sale transaction must follow the existing approval workflow, and parent and extended/subsidiary assets must appear together in all downstream transactions and approval records.

**21.1.12. Exceptions:** N/A

---

## 22. Asset Sale List | F22

### 22.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F22S01

**22.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset sale.

**22.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Disposal from the top menu bar.
- Select and click on the Asset Sale List feature.

**22.1.3. Actors:**
- Authorized user.

**22.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.

**22.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**22.1.6. Impacted Areas:**
- Asset Sale List

**22.1.7. Mock-up/ Prototypes:** Figure omitted (List of Asset data grid in Asset Sale Details pop-up window).

**22.1.8. Requirements:**
- For List of Asset data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- For assets, the sale of an extended asset can be performed independently, without requiring the parent asset to be sale. To do so, the system will consider Utilization Status other than "IN_USE" and Assigned status to be "Unassigned".
- The Gain/Loss will be calculated based on the total sale price of the asset. The system will first allocate the full sale price to the parent asset and calculate its Gain/Loss. Any remaining sale value will then be gradually distributed among the extended (child) assets, and Gain/Loss will be calculated sequentially for each child asset based on the allocated amount. An example scenario is provided below for better understanding.

  **Total Sale amount assigned to Parent asset then gradually extended assets**

  | Asset | Purchase Price | WDV | Sale Price | Gain/Loss |
  |---|---|---|---|---|
  | Parent Asset | 33000 | 33000 | 180000 | 147000 |
  | Extended Asset 1 | 25000 | 1000 | 0 | -1000 |
  | Extended Asset 2 | 20000 | 2000 | 0 | -2000 |

**22.1.9. Assumptions:** N/A

**22.1.10. Non-functional Requirements:** N/A

**22.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**22.1.12. Exceptions:** N/A

---

## 23. Asset Sale Approval List | F23

### 23.1. Extended/Subsidiary asset will show with right indentation below parent asset on the list view | F23S01

**23.1.1. User Story:** As an authorized user, I want the system to show and list the extended/subsidiary assets under the parent assets in the list pages so that I can have an accurate and elaborated view of the asset sale approval list.

**23.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Disposal from the top menu bar.
- Select and click on the Asset Sale Approval List feature.

**23.1.3. Actors:**
- Authorized user.

**23.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Extended/subsidiary assets will be shown and listed below their designated parent asset.
  ii. During asset sale transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.

**23.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**23.1.6. Impacted Areas:**
- Asset Sale Approval List

**23.1.7. Mock-up/ Prototypes:** Figure omitted (List of Asset data grid in Asset Sale Details pop-up window).

**23.1.8. Requirements:**
- For List of Asset data grid:
  i. For every parent asset, the related extended/subsidiary asset(s) (if any) will also be listed below the parent asset with right indentation on the asset serial and no action button (remove/delete) for the extended/subsidiary assets.
  ii. Extended/subsidiary assets under a parent asset will not contain the list serial no (SL) in the list.
  iii. The asset serial numbers of the extended asset in the Asset Serial column will be indented to the right for visual distinction. **4 space indentation will be applied.**
- During asset sale transaction, the Fixed Asset module will transmit the combined accumulated data of both parent and extended assets to the respective finance module using the Parent Asset Serial JSON reference value.
- For assets, the sale of an extended asset can be performed independently, without requiring the parent asset to be sale. To do so, the system will consider Utilization Status other than "IN_USE" and Assigned status to be "Unassigned".
- The Gain/Loss will be calculated based on the total sale price of the asset. The system will first allocate the full sale price to the parent asset and calculate its Gain/Loss. Any remaining sale value will then be gradually distributed among the extended (child) assets, and Gain/Loss will be calculated sequentially for each child asset based on the allocated amount. An example scenario is provided below for better understanding.

  **Total Sale amount assigned to Parent asset then gradually extended assets**

  | Asset | Purchase Price | WDV | Sale Price | Gain/Loss |
  |---|---|---|---|---|
  | Parent Asset | 33000 | 33000 | 180000 | 147000 |
  | Extended Asset 1 | 25000 | 1000 | 0 | -1000 |
  | Extended Asset 2 | 20000 | 2000 | 0 | -2000 |

**23.1.9. Assumptions:** N/A

**23.1.10. Non-functional Requirements:** N/A

**23.1.11. Acceptance Criteria:**
- Extended/subsidiary assets included under a parent asset must appear immediately below the parent asset with right indentation of the asset serial number for clear visual distinction.
- Extended/subsidiary assets must not display any list serial number (SL) in the grid.

**23.1.12. Exceptions:** N/A

---

## 24. Asset Split | F24

### 24.1. Validation to Restrict Asset Split for Assets Having Assets Extension | F24S01

**24.1.1. User Story:** As an authorized user, I want the system to restrict asset split for any asset that has associated extended/subsidiary assets, so that assets with parent–extended/subsidiary relationships cannot be split, and data integrity is maintained.

**24.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Asset Profile from the top menu bar.
- Select and click on the Asset Split feature.

**24.1.3. Actors:**
- Authorized user.

**24.1.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. The system will not show any extended/subsidiary asset(s) in the List of Global Asset Serial data grid under the Asset Split feature.
  ii. Validation to restrict asset split for assets having extended/subsidiary assets.

**24.1.5. Pre-condition:**
- Parent–extended/subsidiary asset relationship must exist and be approved through asset addition.

**24.1.6. Impacted Areas:**
- Asset Split

**24.1.7. Mock-up/ Prototypes:** Figure omitted (validation message for extended/subsidiary asset).

**24.1.8. Requirements:**
- In the List of Global Asset Serial data grid, no extended/subsidiary asset will be shown for the user to select.
- When a parent asset is selected for asset split, the system must check whether any active extended/subsidiary asset is associated with it.
- If one or more active extended/subsidiary assets exist under the selected parent asset, the system must prevent the asset split operation.
- When users click on split button, the system must display a validation message stating: **"Cannot Split. Asset has associated asset extension."**
- Other than this, Asset Split will follow the current process of Asset Split.

**24.1.9. Assumptions:** N/A

**24.1.10. Non-functional Requirements:** N/A

**24.1.11. Acceptance Criteria:**
- The Asset Split feature must display only parent assets in the List of Global Asset Serial data grid.
- If a selected parent asset has one or more active extended/subsidiary assets, the system must block the asset split operation.
- The system must display a clear validation message when the split operation is restricted.

**24.1.12. Exceptions:** N/A

---

## 25. New and Existing Impacted Reports | F25

### 25.1. Asset Addition List Report | F25S01

**25.1.1. User Story:** As an authorized user, I want to view a new Asset Addition List Report so that I can view the Parent and extended asset List report as per selected criteria.

**25.1.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Addition List.

**25.1.3. Actors:**
- Authorized HO User

**25.1.4. Scope:**
- **Current Scope:** Currently there is no asset addition list report in the system.
- **New Scope:**
  i. This report will display both parent assets and their associated extended assets as maintained in the Fixed Asset module.

**25.1.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.1.6. Impacted Areas:**
- Asset Addition List Report

**25.1.7. Mock-up/ Prototypes:** Figures omitted (Filtering Criteria – Head Office; Filtering Criteria – Branch Office; Asset Addition List Report).

**25.1.8. Requirements:**
- This report will only show parent assets having one or multiple extended assets in the fixed asset module.
- User will be able to select from the following filtering criteria:
  i. **Report For:** Drop-down field with Head Office and Branch Office. If Head Office is selected, the system will show the following fields for report filtering criteria. If Branch Office is selected, the system will show additional fields: Division, Region, Area and Branch (as per existing business for report calling feature for Branch Office from Head Office).
  ii. Project (Drop-down, Optional)
  iii. Department (Drop-down, Optional): This field will be applicable to the selected project where required.
  iv. Source of Fund (Drop-down, Optional)
  v. Employee Name & PIN (Drop-down, Optional)
  vi. Asset Group (Drop-down, Optional)
  vii. Asset Category (Drop-down, Optional)
  viii. Asset Sub Category (Drop-down, Optional)
  ix. Asset Item Name (Drop-down, Optional)
  x. Asset Utilization Status (Drop-down, Optional)
  xi. Asset Assign Status (Drop-down, Optional)
- User have to select PDF or Excel from the radio button (if selected branch office only, otherwise for the head office there will be no PDF/Excel button as the report will be in CSV format.)
- User will click on Submit button to generate the report.
- User will be able to click on Reset button to reset the filtering criteria.
- If the user selects the PDF radio button, then system will generate PDF version of the report and show it in another tab in the browser (Only for the branch offices).
- **Report Header:** The downloaded report will have the following report header:
  a) BRAC (Only for Branch Office)
  b) Location: Name of the branch office user selected in filtering criteria (Only for Branch Office)
  c) List of Asset Addition (Only for Branch Office)
  d) Project: Show the names of selected Project during report filtering criteria. If no project is selected, mention "All"
  e) Department: Show the names of selected asset department during report filtering criteria. If no department is selected, mention "All". (Only for Head Office)
  f) Source of Fund: Show the names of selected asset source of fund during report filtering criteria. If no source of fund is selected, mention "All"
  g) As on Date: System will show as on date business date based on the report download date
- **Report Format and Columns:**
  I. **SL:** Auto-generated serial number for each asset in the report. This will be incremental in the downloaded report and will show total rows for the report.
  II. **Asset Serial:** This column will show the parent asset serial number.
  III. **RFID:** This column will show the parent asset RFID.
  IV. **Asset IMEI/SL No.:** This column will show the parent asset IMEI/SL No.
  V. **Asset Name:** This column will show the parent asset name.
  VI. **Sub Category:** This column will show the parent asset subcategory.
  VII. **Category:** This column will show the parent asset category.
  VIII. **Group:** This column will show the parent asset group.
  IX. **Asset Purchase/ Addition Date:** This column will show the purchase/addition date of parent/extended asset.
  X. **Asset Registration Date:** This column will show the parent asset registration business date.
  XI. **Project:** This column will show the project code and name associated with the parent asset.
  XII. **Department:** This column will show the department code and name associated with the parent asset.
  XIII. **Current Location:** This column will show the location associated with the parent asset.
  XIV. **Assign Status:** This column will show the assign status of asset based on the filtering criteria.
  XV. **Employee Name & PIN:** This column will display the name and PIN of the employee to whom the parent asset is assigned.
  XVI. **Utilization Status:** This column will show the utilization status of assets based on the filtering criteria.
  XVII. **Purchase/ Addition Price:** The column will show the purchase price of the parent Asset or extended assets.
  XVIII. **Accumulated Depreciation:** Total accumulated depreciation that has been charged against that specific parent/extended Asset.
  XIX. **Written Down Value:** This column will show the Written Down Value of the parent/extended Asset against each Asset. Calculation: Total Unit Price – Accumulated Depreciation.

**25.1.9. Assumptions:** N/A

**25.1.10. Non-functional Requirements:** N/A

**25.1.11. Acceptance Criteria:**
- The system is generating report as per selected filtering criteria.
- The system is generating the report as per selected (for branch Offices) / CSV (for Head Offices) format.

**25.1.12. Exceptions:** N/A

### 25.2. Asset List Report | F25S02

**25.2.1. User Story:** As an authorized user, I want to view the Asset List Report so that I can view the Asset List report as per selected criteria.

**25.2.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset List.

**25.2.3. Actors:**
- Authorized user.

**25.2.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.2.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.2.6. Impacted Areas:**
- Asset List Report

**25.2.7. Mock-up/ Prototypes:** Figure omitted.

**25.2.8. Requirements:**
- Asset Serial column will always show parent asset serial number.
- Extended Asset serial will not be shown in this report.

**25.2.9. Assumptions:** N/A

**25.2.10. Non-functional Requirements:** N/A

**25.2.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.2.12. Exceptions:** N/A

### 25.3. Asset Register Report | F25S03

**25.3.1. User Story:** As an authorized user, I want to view the Asset Register Report so that I can view the Asset Register report as per selected criteria.

**25.3.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Register Report.

**25.3.3. Actors:**
- Authorized user.

**25.3.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.3.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.3.6. Impacted Areas:**
- Asset Register Report

**25.3.7. Mock-up/ Prototypes:** Figure omitted.

**25.3.8. Requirements:**
The following column values in the Asset Register Report will be updated as part of the new parent–extended asset handling logic:
- **Asset Serial:** The Asset Serial column will always display the Parent Asset Serial.
- **Total Addition:** The Total Addition column will represent the combined purchase value of all extended assets under the parent asset.
- **Total unit price:** System will show the total unit price of the Fixed Asset. Formula: Purchase Price + Total Addition.
- **Accumulated Depreciation:** The Accumulated Depreciation column will show the aggregated accumulated depreciation of both the parent asset and all associated extended assets.
- **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values.

**25.3.9. Assumptions:** N/A

**25.3.10. Non-functional Requirements:** N/A

**25.3.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.3.12. Exceptions:** N/A

### 25.4. Asset Schedule Report | F25S04

**25.4.1. User Story:** As an authorized user, I want to view the Asset Schedule Report so that I can view the Asset Schedule report as per selected criteria.

**25.4.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Schedule Report.

**25.4.3. Actors:**
- Authorized user.

**25.4.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.4.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.4.6. Impacted Areas:**
- Asset List Report

**25.4.7. Mock-up/ Prototypes:** Figure omitted.

**25.4.8. Requirements:**
The following column values in the report will be updated as part of the new parent–extended asset handling logic:
- **Cost Value:** Under cost value heading following individuals will change:
  i. **Additions During the Period:** The system will show the combined purchase value of all extended assets under the respective parent asset group.
  ii. **Received from Branch/Project:** The system will display the total value of parent and extended assets received from other branches or projects.
  iii. **Transfer to Branch/Project:** The system will display the total value of parent and extended assets transferred out to other branches or projects.
  iv. **Disposals During the Period:** This value represents the combined disposal value of the parent and all extended assets under each asset group.
  v. **Closing Balance:** System will show the closing balance of the selected period in this column against each Fixed Asset group. Calculation: Opening Balance + Additions During the Period + Received from Branch/Project – Transfer to Branch/Project – Disposal During the Period.
- **Depreciation:** Under depreciation value heading following individuals will change:
  i. **Charged During the Period:** The system will show the total depreciation charged during the selected period for the parent asset and all extended assets under the asset group.
  ii. **Received from Branch/Project:** The system will show the combined accumulated depreciation (parent + extended) for assets received from other branches.
  iii. **Transfer to Branch/Project:** The system will show the combined accumulated depreciation (parent + extended) for assets transferred out.
  iv. **Disposals During the Period:** System will show the sum of Accumulated Depreciation of the Fixed Asset in each Asset Group that has been Disposed using Disposal Sale, Fixed Asset Write Off, and Backend Support Sale/ Write-Off.
  v. **Closing Balance:** System will show the closing balance of the selected period in this column against each Fixed Asset group. Calculation: Opening Balance + Charged during the Period + Received from Branch/Project – Transfer to Branch/Project – Disposal During the Period.

**25.4.9. Assumptions:** N/A

**25.4.10. Non-functional Requirements:** N/A

**25.4.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.4.12. Exceptions:** N/A

### 25.5. Asset Disposal Sale Report | F25S05

**25.5.1. User Story:** As an authorized user, I want to view the Asset Disposal Sale Report so that I can view the Asset Disposal Sale report as per selected criteria.

**25.5.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Disposal Sale Report.

**25.5.3. Actors:**
- Authorized user.

**25.5.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group during parent asset sale. For child asset respective value will be shown.

**25.5.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.5.6. Impacted Areas:**
- Asset Disposal Sale Report

**25.5.7. Mock-up/ Prototypes:** Figure omitted.

**25.5.8. Requirements:**
The following column values in the Asset Disposal Sale Report will be updated as part of the new parent–extended asset handling logic:
- **Asset Serial:** The Asset Serial column will always display the Parent Asset Serial while aggregated asset will be sold. When individual child asset will be sold then it will show child asset's serial number.
- **Total unit price:** System will show the total unit price of the Fixed Asset. Formula for parent asset: Purchase Price + Total Addition (combined purchase value of all extended assets). For child asset only its own purchase price will be shown.
- **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values while asset will be sold on aggregated. But for child asset it will be shown only child asset written down value.
- **Sale Price:** The amount at which the Fixed Asset has been sold.
- **Gain/Loss:** System will show the amount of gain/loss that has occurred due to disposal processes. Gain/Loss = Sale Price – Written Down Value.

**25.5.9. Assumptions:** N/A

**25.5.10. Non-functional Requirements:** N/A

**25.5.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.5.12. Exceptions:** N/A

### 25.6. Asset Write-off & Offline Transfer Report | F25S06

**25.6.1. User Story:** As an authorized user, I want to view the Asset Write-off & Offline Transfer Report so that I can view the Asset Write-off & Offline transfer report as per selected criteria.

**25.6.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Write-off & Offline Transfer Report.

**25.6.3. Actors:**
- Authorized user.

**25.6.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group during parent asset write-off. For child asset respective value will be shown.

**25.6.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.6.6. Impacted Areas:**
- Asset Write-off & Offline Transfer Report

**25.6.7. Mock-up/ Prototypes:** Figure omitted.

**25.6.8. Requirements:**
The following column values in the Asset Write-off & Offline transfer Report will be updated as part of the new parent–extended asset handling logic:
- **Asset Serial:** The Asset Serial column will always display the Parent Asset Serial while aggregated asset will be write-off. When individual child asset will be write-off then it will show child asset's serial number.
- **Total unit price:** System will show the total unit price of the Fixed Asset. Formula: Purchase Price + Total Addition (combined purchase value of all extended assets). For child asset only its own purchase price will be shown.
- **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values while asset will be written off as aggregated. But for child asset it will be shown only child asset written down value.
- **Sale Price:** The amount at which the Fixed Asset has been sold.
- **Accumulated Depreciation:** The Accumulated Depreciation column will show the aggregated accumulated depreciation of both the parent asset and all associated extended assets. But for child asset it will be shown only child asset Accumulated depreciation value.

**25.6.9. Assumptions:** N/A

**25.6.10. Non-functional Requirements:** N/A

**25.6.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.6.12. Exceptions:** N/A

### 25.7. Asset Valuation Report | F25S07

**25.7.1. User Story:** As an authorized user, I want to view the Asset Valuation Report so that I can view the Asset Valuation report as per selected criteria.

**25.7.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Valuation Report.

**25.7.3. Actors:**
- Authorized user.

**25.7.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.7.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.7.6. Impacted Areas:**
- Asset Valuation Report

**25.7.7. Mock-up/ Prototypes:** Figure omitted.

**25.7.8. Requirements:**
The following column values in the Asset Valuation Report will be updated as part of the new parent–extended asset handling logic:
- **Purchase Price:** System will show the total purchase price of all parent asset under the asset group.
- **Total Addition:** The Total Addition column will represent the combined purchase value of all extended assets under the parent asset of asset group.
- **Total unit price:** System will show the total unit price of the Fixed Asset for asset groups. Formula: Purchase Price + Total Addition.
- **Accumulated Depreciation:** The Accumulated Depreciation column will show the aggregated accumulated depreciation of both the parent asset and all associated extended assets for specific asset groups.
- **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values for asset groups.

**25.7.9. Assumptions:** N/A

**25.7.10. Non-functional Requirements:** N/A

**25.7.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.7.12. Exceptions:** N/A

### 25.8. Asset Transaction History Report | F25S08

**25.8.1. User Story:** As an authorized user, I want to view the Asset Transaction History Report so that I can view the Asset Transaction History report as per selected criteria.

**25.8.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Transaction History Report.

**25.8.3. Actors:**
- Authorized user.

**25.8.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.8.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.8.6. Impacted Areas:**
- Asset Transaction History Report

**25.8.7. Mock-up/ Prototypes:** Figure omitted.

**25.8.8. Requirements:**
- Asset Serial column will always show parent asset serial number.

**25.8.9. Assumptions:** N/A

**25.8.10. Non-functional Requirements:** N/A

**25.8.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.8.12. Exceptions:** N/A

### 25.9. Asset Receivable Report | F25S09

**25.9.1. User Story:** As an authorized user, I want to view the Asset Receivable Report so that I can view the Asset Receivable report as per selected criteria.

**25.9.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Receivable Report.

**25.9.3. Actors:**
- Authorized user.

**25.9.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.9.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.9.6. Impacted Areas:**
- Asset Receivable Report

**25.9.7. Mock-up/ Prototypes:** Figure omitted.

**25.9.8. Requirements:**
- Asset Serial column will always show parent asset serial number.

**25.9.9. Assumptions:** N/A

**25.9.10. Non-functional Requirements:** N/A

**25.9.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.9.12. Exceptions:** N/A

### 25.10. Asset Returnable Report | F25S10

**25.10.1. User Story:** As an authorized user, I want to view the Asset Returnable Report so that I can view the Asset Returnable Report as per selected criteria.

**25.10.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Returnable Report.

**25.10.3. Actors:**
- Authorized user.

**25.10.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.10.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.10.6. Impacted Areas:**
- Asset Returnable Report

**25.10.7. Mock-up/ Prototypes:** Figure omitted.

**25.10.8. Requirements:**
- Asset Serial column will always show parent asset serial number.

**25.10.9. Assumptions:** N/A

**25.10.10. Non-functional Requirements:** N/A

**25.10.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.10.12. Exceptions:** N/A

### 25.11. Asset Tracking Report | F25S11

**25.11.1. User Story:** As an authorized user, I want to view the Asset Tracking Report so that I can view the Asset Tracking Report as per selected criteria.

**25.11.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Tracking Report.

**25.11.3. Actors:**
- Authorized user.

**25.11.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.11.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.11.6. Impacted Areas:**
- Asset List Report

**25.11.7. Mock-up/ Prototypes:** Figures omitted (Asset Tracking Report UI; Asset Tracking Report).

**25.11.8. Requirements:**
1. The following column values in the Asset Tracking Report will be updated as part of the new parent–extended asset handling logic:
   - **Asset Serial:** The Asset Serial column will always display the Parent Asset Serial in both UI and report details.
   - **Total unit price:** System will show the total unit price of the Fixed Asset. Formula: Purchase Price + Total Addition.
   - **Accumulated Depreciation:** The Accumulated Depreciation column will show the aggregated accumulated depreciation of both the parent asset and all associated extended assets.
   - **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values.
2. Addition impact will be shown in the tracking report under event section for each addition.

**25.11.9. Assumptions:** N/A

**25.11.10. Non-functional Requirements:** N/A

**25.11.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.11.12. Exceptions:** N/A

### 25.12. Asset Registration Report | F25S12

**25.12.1. User Story:** As an authorized user, I want to view the Asset Registration Report so that I can view the Asset Registration Report as per selected criteria.

**25.12.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Registration Report.

**25.12.3. Actors:**
- Authorized user.

**25.12.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.12.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.12.6. Impacted Areas:**
- Asset Register Report

**25.12.7. Mock-up/ Prototypes:** Figure omitted.

**25.12.8. Requirements:**
The following column values in the Asset Registration Report will be updated as part of the new parent–extended asset handling logic:
- **Asset Serial:** The Asset Serial column will always display the Parent Asset Serial.
- **Total Addition:** The Total Addition column will represent the combined purchase value of all extended assets under the parent asset.
- **Total unit price:** System will show the total unit price of the Fixed Asset. Formula: Purchase Price + Total Addition.
- **Accumulated Depreciation:** The Accumulated Depreciation column will show the aggregated accumulated depreciation of both the parent asset and all associated extended assets.
- **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values.

**25.12.9. Assumptions:** N/A

**25.12.10. Non-functional Requirements:** N/A

**25.12.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.12.12. Exceptions:** N/A

### 25.13. Asset Depreciation Statement (Serial wise) | F25S13

**25.13.1. User Story:** As an authorized user, I want to view the Asset Depreciation Statement Serial Wise Report so that I can view the Asset Depreciation Statement Serial Wise as per selected criteria.

**25.13.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Depreciation Statement Serial Wise.

**25.13.3. Actors:**
- Authorized user.

**25.13.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.13.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.13.6. Impacted Areas:**
- Asset Depreciation Statement Serial Wise

**25.13.7. Mock-up/ Prototypes:** Figure omitted.

**25.13.8. Requirements:**
The following column values in the report will be updated as part of the new parent–extended asset handling logic:
- **Asset Serial:** The Asset Serial column will always display the Parent Asset Serial.
- **Cost Value:** Under cost value heading following individuals will change:
  i. **Addition:** The system will show the combined purchase value of all extended assets under the respective parent asset.
  ii. **Received:** The system will display the total value of parent and extended assets received from other branches or projects.
  iii. **Disposals:** This value represents the combined disposal value of the parent and all extended assets under each asset.
  iv. **Total:** System will show the closing balance of the selected period in this column against each Fixed Asset. Calculation: Opening Balance + Additions During the Period + Received from Branch/Project – Disposal During the Period.
- **Depreciation:** Under depreciation value heading following individuals will change:
  i. **Charge:** The system will show the total depreciation charged during the selected period for the parent asset and all extended assets under the parent asset.
  ii. **Receive:** The system will show the combined accumulated depreciation (parent + extended) for assets received from other branches.
  iii. **Disposal:** System will show the sum of Accumulated Depreciation of the Fixed Asset that has been Disposed using Disposal Sale, Fixed Asset Write Off, and Backend Support Sale/ Write-Off.
  iv. **Total:** System will show the closing balance of the selected period in this column against each Fixed Asset. Calculation: Opening Balance + Charged during the Period + Received from Branch/Project – Disposal During the Period.
  v. **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values.

**25.13.9. Assumptions:** N/A

**25.13.10. Non-functional Requirements:** N/A

**25.13.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.13.12. Exceptions:** N/A

### 25.14. Asset Depreciation Statement (Group wise) | F25S14

**25.14.1. User Story:** As an authorized user, I want to view the Asset Depreciation Statement Group Wise Report so that I can view the Asset Depreciation Statement Group Wise as per selected criteria.

**25.14.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Depreciation Statement Group Wise.

**25.14.3. Actors:**
- Authorized user.

**25.14.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.14.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.14.6. Impacted Areas:**
- Asset Depreciation Statement Group Wise

**25.14.7. Mock-up/ Prototypes:** Figure omitted.

**25.14.8. Requirements:**
The following column values in the report will be updated as part of the new parent–extended asset handling logic:
- **Cost Value:** Under cost value heading following individuals will change:
  v. **Addition:** The system will show the combined purchase value of all extended assets under the respective parent asset group.
  vi. **Received:** The system will display the total value of parent and extended assets received from other branches or projects.
  vii. **Disposals:** This value represents the combined disposal value of the parent and all extended assets under each asset group.
  viii. **Total:** System will show the closing balance of the selected period in this column against each Fixed Asset group. Calculation: Opening Balance + Additions During the Period + Received from Branch/Project – Disposal During the Period.
- **Depreciation:** Under depreciation value heading following individuals will change:
  vi. **Charge:** The system will show the total depreciation charged during the selected period for the parent asset and all extended assets under the asset group.
  vii. **Receive:** The system will show the combined accumulated depreciation (parent + extended) for assets received from other branches.
  viii. **Disposal:** System will show the sum of Accumulated Depreciation of the Fixed Asset in each Asset Group that has been Disposed using Disposal Sale, Fixed Asset Write Off, and Backend Support Sale/ Write-Off.
  ix. **Total:** System will show the closing balance of the selected period in this column against each Fixed Asset group. Calculation: Opening Balance + Charged during the Period + Received from Branch/Project – Disposal During the Period.
  x. **Written Down Value:** The Written Down Value column will present the total written-down value, combining parent and extended asset values for the asset group.

**25.14.9. Assumptions:** N/A

**25.14.10. Non-functional Requirements:** N/A

**25.14.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.14.12. Exceptions:** N/A

### 25.15. Asset Depreciation History (Serial wise) | F25S15

**25.15.1. User Story:** As an authorized user, I want to view the Asset Depreciation History Serial Wise Report so that I can view the Asset Depreciation History Serial Wise as per selected criteria.

**25.15.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Depreciation History Serial Wise.

**25.15.3. Actors:**
- Authorized user.

**25.15.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.15.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.15.6. Impacted Areas:**
- Asset Depreciation History Serial Wise

**25.15.7. Mock-up/ Prototypes:** Figures omitted.

**25.15.8. Requirements:**
The following column values in the report will be updated as part of the new parent–extended asset handling logic:
- **Addition (Up-to Last Period):** This column will display the total purchase value of all extended assets that were added prior to the selected reporting period. The system will not consider the parent asset's own purchase cost in this value; only the cumulative cost of extended assets created before the last period will be included.
- **Addition (During the Period):** This field will show the purchase value of extended assets added within the selected reporting period. Any new extended asset creation or extended-level addition captured during the selected date range will be reflected here.
- **Total Unit Price:** The system will present the combined purchase cost of the parent asset plus all associated extended assets. This represents the full capitalized value displayed under the parent asset serial in the UI.
- **WDV (Up-to last period):** This column will display the written-down value up to the previous period by deducting the combined accumulated depreciation (parent + extended) from the total purchase cost of the parent and extended assets recorded up to that point.
- **Acc. Dep. (Up-to Last period):** The accumulated depreciation up to the previous period will show the total depreciation charged on the parent asset and all extended assets until the last closing month.
- **Dep. (During the period):** This field will show the depreciation charged during the selected period for both the parent and extended assets.
- **Acc. Depreciation:** The accumulated depreciation column will display the updated total by adding the period's depreciation to the accumulated depreciation of the previous period for the entire parent–extended hierarchy.
- **New WDV:** The New Written-Down Value will represent the closing value of the asset group by subtracting the updated accumulated depreciation from the total unit price of the parent asset and all extended assets.

**25.15.9. Assumptions:** N/A

**25.15.10. Non-functional Requirements:** N/A

**25.15.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.15.12. Exceptions:** N/A

### 25.16. Asset Depreciation History (Group wise) | F25S16

**25.16.1. User Story:** As an authorized user, I want to view the Asset Depreciation History Group Wise Report so that I can view the Asset Depreciation History Group Wise Report as per selected criteria.

**25.16.2. User Journey:**
- Log into the system.
- Go to Fixed Asset Module.
- Select Report from the top menu bar.
- Select and click on the Asset List.
- Fixed Asset Module > Report > Asset Depreciation History Group Wise Report.

**25.16.3. Actors:**
- Authorized user.

**25.16.4. Scope:**
- **Current Scope:** Currently there is no parent-extended/subsidiary asset relationship that exists in the system.
- **New Scope:**
  i. Report will display the Parent Asset Serial as the primary identifier, regardless of whether the asset has one or multiple extended assets.
  ii. Transactional values associated with extended assets will be aggregated and presented under the corresponding Parent Asset Serial/Asset Group.

**25.16.5. Pre-condition:**
- Users must be authorized and logged into the system.
- User will click on the submit button to generate the report.

**25.16.6. Impacted Areas:**
- Asset Depreciation History Group Wise Report

**25.16.7. Mock-up/ Prototypes:** Figure omitted.

**25.16.8. Requirements:**
The following column values in the report will be updated as part of the new parent–extended asset handling logic:
- **Addition (Up-to Last Period):** This column will display the total purchase value of all extended assets that were added prior to the selected reporting period. The system will not consider the parent asset's own purchase cost in this value; only the cumulative cost of extended assets created before the last period will be included.
- **Addition (During the Period):** This field will show the purchase value of extended assets added within the selected reporting period. Any new extended asset creation or extended-level addition captured during the selected date range will be reflected here.
- **Total Unit Price:** The system will present the combined purchase cost of the parent asset plus all associated extended assets. This represents the full capitalized value displayed under the parent asset serial in the UI.
- **WDV (Up-to last period):** This column will display the written-down value up to the previous period by deducting the combined accumulated depreciation (parent + extended) from the total purchase cost of the parent and extended assets recorded up to that point.
- **Acc. Dep. (Up-to Last period):** The accumulated depreciation up to the previous period will show the total depreciation charged on the parent asset and all extended assets until the last closing month.
- **Dep. (During the period):** This field will show the depreciation charged during the selected period for both the parent and extended assets.
- **Acc. Depreciation:** The accumulated depreciation column will display the updated total by adding the period's depreciation to the accumulated depreciation of the previous period for the entire parent–extended hierarchy.
- **New WDV:** The New Written-Down Value will represent the closing value of the asset group by subtracting the updated accumulated depreciation from the total unit price of the parent asset and all extended assets.

**25.16.9. Assumptions:** N/A

**25.16.10. Non-functional Requirements:** N/A

**25.16.11. Acceptance Criteria:**
- All filtering criteria, user interface elements, and report generation procedures will remain unchanged and will follow the existing behavior of the Fixed Asset module.

**25.16.12. Exceptions:** N/A
