# Flow: Asset Single Challan (Single Challan) — Create to Acknowledge

**Business scenario:** A user creates an Asset Single Out Challan (one challan on its own, no shipment around it), adds the asset's serial number, a second step approves it, and the receiving side acknowledges it on Asset Single In-Challan. The Gate Pass is then previewed. Three combinations of branch and project are covered: the same branch with a different project (one login is enough), and another branch with the same or with a different project (the receiving branch's user acknowledges, so two logins are needed).

**Login:** the sender is the main user (`ERP_USERNAME` / `ERP_PASSWORD` / `DEFAULT_BRANCH`). For another branch the challan is acknowledged by a different user of the receiving branch (`ACK_SHIPMENT_ERP_USERNAME` / `ACK_SHIPMENT_ERP_PASSWORD` / `ACK_SHIPMENT_ERP_DEFAULT_BRANCH`, fixture `ack_shipment_logged_in_page`). The ERP allows one login per user, so the two users must be different.

**Automated in:** `automation/tests/test_22_asset_single_out_challan.py` to `test_25_asset_gate_pass_generation_challan.py`; stages in `utils/single_challan_flow.py` (`SingleChallanFlow`, stages drafted, submitted, serial_added, approved, acknowledged; two paths "draft" and "submit", each with its own approved asset from the slots `challan_a` and `challan_b`). Pages: `single_out_challan_page.py`, `single_out_challan_approval_list_page.py`, `single_in_challan_page.py`, `single_gate_pass_page.py`. Catalogs: `asset_single_out_challan.md`, `asset_single_out_challan_approval_list.md`, `asset_single_in_challan.md`, `asset_single_challan_gate_pass.md`.

## Rules to test
- A Single Challan carries one project pair. For several project pairs create several Single Challans.
- Same branch with the same project is not allowed (the message was not seen, so it is not built).
- Draft and Submit show no message; the Status in the list is the check (Submit gives PENDING, Draft gives DRAFT with an Edit link).
- The serial is added after Submit: click the Out Challan Number, then Add Serial (message `Asset serial added successfully`).
- Another branch: the challan reaches the receiving branch's Single In-Challan list only for users of that office; Acknowledge is refused on a closed day with `Business day not open for Fixed Asset.`

## Three scenarios (checked on staging, 2026-10-15)
| # | Scenario | Sending / Receiving Branch | From Project / To Project | Who acknowledges | Test (file `test_24_asset_single_in_challan.py`) |
|---|---|---|---|---|---|
| 1 | Same branch, different project | the same (Receiving Branch empty = Sending Branch) | `[015]` to `[060] Progoti` | the sender, same tab | `test_in_challan_acknowledge[submit]` and `[draft]` |
| 2 | Another branch, same project | Head Office `[HO - BDHO]` to `[BO - 0233] Chagalnaiya` | `[015]` to `[015]` | a user of the receiving branch, own tab | `test_single_out_challan_different_branch_same_project_receiving_user_sees_the_challan`, `..._acknowledges_the_challan` |
| 3 | Another branch, different project | as scenario 2 | `[015]` to `[060] Progoti` | as scenario 2 | `test_single_out_challan_different_branch_different_project_receiving_user_sees_the_challan`, `..._acknowledges_the_challan` |

| Step | Role/Login | Action | Reference | Data carried forward |
|---|---|---|---|---|
| 1 | sender | Open **Fixed Asset >> Single Challan >> Asset Single Out Challan**, click **Create**; the Sending Branch is already the sender's branch | automation-only: open the create popup | — |
| 2 | sender | Choose From Project, Receiving Branch, To Project, the asset item (Cabinet Table) and Quantity 1; click **Add**, then **Submit** (or **Draft**, then **Edit**, then **Submit**) | automation-only: create the challan | produces `out_challan_no` |
| 3 | sender | Click the Out Challan Number, **Add Serial**, choose the asset's serial, **Add**, **Save** | automation-only: add serial | consumes `out_challan_no`; produces `asset_serial` |
| 4 | sender (or an approver) | Open **Fixed Asset >> Single Challan >> Asset Single Out Challan Approval List**, search the Out Challan No, open it, add a comment, **Approve** | automation-only: approve | consumes `out_challan_no` |
| 5 | receiving branch's user | Open **Fixed Asset >> Single Challan >> Asset Single In-Challan**, search the Out Challan No; the row shows APPROVED and an In Challan Number | automation-only: find the in-challan | consumes `out_challan_no` |
| 6 | receiving branch's user | Open the challan and click **Acknowledge**; the row shows ACKNOWLEDGED and a Preview link (inside one branch). Another branch on a closed day: refused with `Business day not open for Fixed Asset.` | automation-only: acknowledge | consumes `out_challan_no` |
| 7 | sender | Open **Fixed Asset >> Single Challan >> Gate Pass Generation** and preview the Gate Pass of the acknowledged challan | automation-only: gate pass | consumes `out_challan_no` |

**Result on 2026-10-15:** scenarios 2 and 3 pass steps 1 to 5 (the receiving user sees the challan with the right branches and projects). Step 6 for another branch was refused on a closed day, so the `..._acknowledges_the_challan` tests fail with the ERP message; a successful branch-to-branch acknowledge is not seen yet.

**Automation Suitable: Yes**, as one chained flow per scenario. Reason: every step is a fixed sequence and the Out Challan Number is carried from step to step.
