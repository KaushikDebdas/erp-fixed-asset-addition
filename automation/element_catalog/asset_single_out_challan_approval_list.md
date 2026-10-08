# Asset Single Out Challan Approval List — element catalog

| Field | Value |
|---|---|
| Page class | `pages/single_out_challan_approval_list_page.py` → `SingleOutChallanApprovalListPage` (inherits `SingleChallanListPage`); tests in `tests/test_24_asset_single_out_challan_approval_list.py` |
| Module / menu path | Fixed Asset >> Single Challan >> Asset Single Out Challan Approval List |
| Entry URL | `https://erpstaging.brac.net/nodef/fixedasset#!faAssetSingleChallan/showApproverList` |
| Last explored | 2026-10-08 |
| Screenshot | `evidence/asset_single_out_challan_approval_list.png` |

## Elements
The filters, grid and challan popup are the ones in `asset_single_out_challan.md` (no Create button, no Edit column use).

| # | Element | Locator | Status |
|---|---|---|---|
| 1 | Comment box (popup) | `#singleChallanhallanComment` (and `#challanCommentDate`) | VERIFIED |
| 2 | Approve / Reject / Sendback | `#approveChallan`, `#rejectChallan`, `#sendBackChallan` | Approve VERIFIED; Reject and Sendback seen only |
| 3 | Show Serial link (item row) | `popup.get_by_role("link", name="Show Serial")` | seen only |

## Notes
- **Approve verified** (challan OC-79823 with a comment): toast, two lines, `Challan approved successfully.` / `Gate pass generated successfully`; the row then shows APPROVED, an In Challan Number (`IC-BBDISCH00000355`), Approved By, Approval Date and a **Preview** link.
- The popup shows Approve, Reject and Sendback for a PENDING challan.
- A challan submitted without a serial can also be listed as PENDING; the tests approve only challans that have the serial.
