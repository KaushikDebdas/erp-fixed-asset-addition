# Flow: Asset Shipment (Asset Transfer) — Create Shipment to Journal Vouchers

**Business scenario:** A user creates a Shipment, adds a Transfer Challan to it with an asset item, adds the asset's serial number, submits and approves the Challan, approves the Shipment (which generates a Gate Pass), acknowledges the Challan on Asset Shipment-In Challan, previews the Gate Pass, and checks the two journal vouchers. Three combinations are covered (see "Three scenarios" below): the same branch with a different project (one login is enough), and another branch with the same or with a different project (the receiving branch's user acknowledges, so two logins are needed).

**Login:** the sender is the main user (`ERP_USERNAME` / `ERP_PASSWORD` / `DEFAULT_BRANCH` in `.env`). For a transfer to **another branch** a second, different user acknowledges: a user of the receiving branch (`ACK_SHIPMENT_ERP_USERNAME` / `ACK_SHIPMENT_ERP_PASSWORD` / `ACK_SHIPMENT_ERP_DEFAULT_BRANCH`, whose default branch is the receiving branch; fixture `ack_shipment_logged_in_page`). The ERP allows only one login per user, so the two must be different people. A user who works in more than one office picks the office at Office Selection after signing in. (NOTE 2026-10-15: the earlier text here, which named `00015370` and said a second branch's user was not available, is replaced.)

**Update 2026-10-08:** the automation now runs as one user (the logged-in `ERP_USERNAME`) in a single tab; the login note above describes how the flow was explored.

**Automated in:** `automation/tests/test_18_asset_shipment.py` to `test_21_asset_gate_pass_generation_transfer.py` (37 tests in 4 files: 19 = steps up to the submitted challan, 20 = challan and shipment approval, 21 = In-Challan, 22 = gate pass; steps 1 to 26, one login: employee `00015370`; the transferred asset is a fresh approved Cabinet Table created by the main user). The shipment moves through seven stages kept by `utils/transfer_helper.py` (shipment, draft challan, serial added, challan submitted, challan approved, shipment approved, acknowledged); every test also runs alone. Pages: `asset_shipment_page.py`, `shipment_challan_page.py`, `shipment_challan_approval_page.py`, `shipment_in_challan_page.py`, `gate_pass_page.py`. Steps 27 and 28 (vouchers) are not automated. Last full run (2026-10-05): 37 passed. Cross-branch tests added 2026-10-15 (4 in test 21, see "Three scenarios").

**Status (2026-10-04):** steps 1 to 26 were run live on staging as employee `00015370` for one real shipment (`BBDSHP00000009`, challan `OC-BBDSHP00000009-594`, asset `BBDASR00227812`, From Project `[015] Microfinance (Dabi)`, To Project `[060] Progoti`). Catalogs: `asset_shipment.md`, `asset_shipment_challan_approval_list.md`, `asset_shipment_in_challan.md`, `asset_gate_pass_generation.md` (all in `automation/element_catalog/`). **Steps 27 and 28 (the vouchers) are NOT confirmed**: no voucher could be found. Several messages on screen differ from the original description; use the messages in this table.

**Use `[060] Progoti` as the To Project** (user's instruction). `[C04] Administratiion` is refused with `Area code not found` at Draft.
Domain background: `knowledge/erp-fixedasset.md` §5, §11, §12.

## Rules to test (from the user's description and the domain documents)
- A shipment cannot be created in the last 3 days of the month (§5).
- Receiving Branch = Sending Branch: From Project and To Project must be different. Receiving Branch not equal to Sending Branch: the projects may be the same or different.
- Shipment Approve is refused while the Challan is still a Draft or no Challan exists.
- No voucher is created until the Challan is acknowledged.
- Voucher check, same branch and different project. Out Challan voucher: Debit = Account Head of the project the asset goes to, Credit = Equipment. In Challan voucher: Debit = Equipment, Credit = Account Head of the project the asset goes to.

| Step | Role/Login | Action | Reference | Data carried forward |
|---|---|---|---|---|
| 1 | employee 00015370 | Open Asset Transfer > **Asset Shipment**. Search by Shipment No or the other filters | automation-only: open the list | — |
| 2 | same session | Click **Create**; the Create Shipment popup opens. Fill the required fields, click **Save**; expect a success message and the popup closing | automation-only: create shipment | — |
| 3 | same session | Read the generated **Shipment No.**; click **Edit** to check it can be edited | automation-only: edit shipment | produces `shipment_no` |
| 4 | same session | Click the Shipment No to open **Shipment Details** | automation-only: open details | consumes `shipment_no` |
| 2a | same session | (live) Save toast is `Asset Shipment Initiated Successfuly`; the popup closes; the new row shows Status PENDING | automation-only: save message | — |
| 5 | same session | Click **Approve** on the **Details** tab; expect `Please add at least one challan` (live message) | automation-only: approve without a challan | — |
| 6 | same session | Open the **Transfer Challans** tab, click **Create**; the Create Challan popup opens | automation-only: open challan popup | — |
| 7 | same session | Select Receiving Branch, From Project, To Project; the Note box is optional. Item Name of the asset; Asset Sub Category, Category, Group and Measurement Unit fill in by themselves; choose Quantity; click **Add** | automation-only: add asset line | produces `item_name` |
| 8 | same session | Check the line is in the grid; delete it; check another can be added again | automation-only: remove and re-add | — |
| 9 | same session | Check the buttons Draft, Submit, Reset and Close are available | automation-only: challan buttons | — |
| 10 | same session | Branch and project rules: same branch needs different projects; a different branch may use the same or different projects | automation-only: branch/project rules | — |
| 11 | same session | Choose the three dropdowns (From Project, Receiving Branch, To Project, and the asset item) by clicking the visible box and typing; setting the hidden `<select>` is not enough. Click **Draft**; expect `Challan drafted successfully` (live). With no To Project Add says `Please select to project`; Draft with no line says `No Items in Challan to perform operation`; To Project `[C04] Administratiion` says `Area code not found` | automation-only: draft | — |
| 12 | same session | After the popup closes read the **Out Challan No.** from the Transfer Challans list (it already exists at Draft, e.g. `OC-BBDSHP00000009-594`). Submit is done later from the Update Challan popup (step 18) | automation-only: read challan number | produces `out_challan_no` |
| 13 | same session | Click the Out Challan No to open **Challan Details**, click **Add Serial**; the Add Serial popup opens | automation-only: open add serial | consumes `out_challan_no` |
| 14 | same session | In the Challan Details item grid click the **Add Serial** link on the item row. Type the Asset Serial No, pick it from the dropdown; Item Name, Quantity, Sub-Category and Category fill in. Disposal and Transfer to Maintenance (misspelled "Tranfer") are NOT yet explored. Click **Add** (no toast; the row appears in the popup grid) | automation-only: add serial | produces `asset_serial` |
| 15 | same session | A wrong serial can be removed with its **Remove** link (not yet tried); click **Save**; live message `Asset serial added Successfuly` | automation-only: save serial | consumes `asset_serial` |
| 16 | same session | Open the **Asset Serial** tab in Challan Details, check the serial; close the popup; reopen Shipment Details and check the same serial in the Add Serial section | automation-only: check serial shown | consumes `asset_serial` |
| 17 | same session | In Shipment Details (Details tab) click **Approve**; live message `Approve at least one challan` (the challan is still a Draft) | automation-only: approve with a draft challan | — |
| 18 | same session | Back on Transfer Challans click **Edit** for the challan (opens "Update Challan"), click **Submit**; live message `Challan submitted successfully`; the challan status is **PENDING**. A second Draft challan can be removed with **Delete** (`Challan deleted successfuly`) | automation-only: submit the challan | consumes `out_challan_no` |
| 19 | same session | Open **Asset Shipment Challan Approval List**, search by Out Challan No, open it | automation-only: open challan for approval | consumes `out_challan_no` |
| 20 | same session | Click **Show Serial**, check the serial; check the actions Approve, Reject and Send Back exist; add a comment if needed | automation-only: review challan | consumes `asset_serial` |
| 21 | same session | Click **Approve**; expect `Challan approved successfully.`; click **Preview** and check the challan report opens | automation-only: approve challan | — |
| 22 | same session | Back on **Asset Shipment**, search by Shipment No, open Shipment Details, click **Approve** | automation-only: approve shipment | consumes `shipment_no` |
| 23 | same session | Live message `Shipment approved successfully` and `Gate pass generated successfully` (one toast, two lines); the status goes from PENDING to APPROVED; a Preview link appears. No voucher was visible | automation-only: shipment approved | — |
| 24 | same session | Open **Asset Shipment In-Challan**, search by Out Challan No. The challan is listed with an In Challan No (`IC-...`), Status APPROVED and nothing in the Preview cell | automation-only: find the in-challan | consumes `out_challan_no`; produces `in_challan_no` |
| 25 | same session | Click the Out Challan No to see Challan Details, click **Acknowledge**. The row then shows ACKNOWLEDGED, an In Challan Date, Acknowledged By and a Preview link. **The success message was not captured** (still to be confirmed) | automation-only: acknowledge | consumes `out_challan_no` |
| 26 | same session | Open **Gate Pass Generation**, search by Out Challan No, click **Preview**: a new tab opens with a PDF from `faAssetReport/generateAssetGatePassReport`. The PDF content was not read yet | automation-only: gate pass preview | consumes `out_challan_no` |
| 27 | same session | In Accounting, check the Out Challan voucher: Debit the account head of the project the asset goes to, Credit Equipment. **NOT CONFIRMED: no voucher found** (Voucher Search by Out Challan No, In Challan No and Shipment No; module Fixed Asset on `20/09/2026`; as both users). The challan's **Posted Accounts** tab was empty | automation-only: out challan voucher | consumes `out_challan_no` |
| 28 | same session | Check the In Challan voucher: Debit Equipment, Credit the account head of the project the asset goes to. **NOT CONFIRMED**, same reason | automation-only: in challan voucher | consumes `out_challan_no` |

## Three scenarios (checked on staging, 2026-10-14 and 2026-10-15)

Where to go, in order: Fixed Asset >> Asset Transfer >> **Asset Shipment** (steps 1 to 18) > **Asset Shipment Challan Approval List** (steps 19 to 21) > **Asset Shipment** (steps 22 and 23) > **Asset Shipment In-Challan** (steps 24 and 25) > **Gate Pass Generation** (step 26).

| # | Scenario | Sending Branch / Receiving Branch | From Project / To Project | Who acknowledges (step 24 and 25) | Test (file `test_20_asset_shipment_in_challan.py` unless noted) |
|---|---|---|---|---|---|
| 1 | Same branch, different project | the same (Receiving Branch left empty = Sending Branch) | `[015] Microfinance (Dabi)` to `[060] Progoti` | the sender, same tab | tests 18 to 21 (`test_in_challan_acknowledge` acknowledges it) |
| 2 | Another branch, same project | Head Office `[HO - BDHO]` to the branch of `ACK_SHIPMENT_ERP_DEFAULT_BRANCH` (`[BO - 0233] Chagalnaiya`) | `[015]` to `[015]` | a user of the receiving branch, own tab | `test_different_branch_same_project_receiving_user_sees_the_challan`, `..._acknowledges_the_challan` |
| 3 | Another branch, different project | as scenario 2 | `[015]` to `[060] Progoti` | as scenario 2 | `test_different_branch_different_project_receiving_user_sees_the_challan`, `..._acknowledges_the_challan` |
| - | Same branch, same project | the same | the same | not allowed | not built (the message was not seen) |

Steps 24 and 25 for scenarios 2 and 3: sign in as the receiving branch's user, pick the Receiving Branch at Office Selection, open **Fixed Asset >> Asset Transfer >> Asset Shipment In-Challan**, search the Out Challan No (the list shows only the challans addressed to that office; status APPROVED, an In Challan No), open the challan and click **Acknowledge**. The scenario data is in `test_data/asset_shipment_data.py` (`SAME_BRANCH_DIFFERENT_PROJECT`, `OTHER_BRANCH_SAME_PROJECT`, `OTHER_BRANCH_DIFFERENT_PROJECT`); the stages are in `utils/transfer_helper.py` (`TransferHelper(scenario=..., receiving_in_challan_page=...)`).

**Result on 2026-10-15:** scenarios 2 and 3 run correctly up to the approved shipment and the receiving user sees the challan with the right branches and projects. **Acknowledge was refused** with `Business day not open for Fixed Asset.` because the Accounting Date of the receiving office showed `[DAY CLOSED]`; the status stayed APPROVED, so the two `..._acknowledges_the_challan` tests fail with that message. A successful branch-to-branch acknowledgement (message, ACKNOWLEDGED, vouchers) is not seen yet. Top right corner of every Fixed Asset page: `Accounting Date : dd-mm-yyyy [DAY OPEN]` or `[DAY CLOSED]`.

**Data needed before step 1:** an approved asset in the sending project (its Asset Serial is added in step 14). The Asset Registration tests can create one (`registrations.get_approved("furniture")`).

**Automation Suitable: Yes**, as one chained test with a helper per stage. Reason: every step is a fixed sequence on one login, and the shipment, challan and serial numbers are carried from step to step. The voucher steps depend on the Accounting module check that `test_17_asset_expense_approval.py` already does for Asset Expense.
