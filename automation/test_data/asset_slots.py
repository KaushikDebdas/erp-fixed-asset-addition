"""
asset_slots.py: the table of assets the whole test suite uses, and which test
flow gets which asset.

Why one file: an asset is registered and approved once, then handed from flow to
flow while its state allows it (an asset that was assigned, moved and unassigned
can still be written off, but a sold or split asset cannot be used again). This
table is the ONE place that says who gets which asset, so a new team member can
read it instead of searching every test file. The pool that hands the assets out
is `utils/asset_pool.py`.

How to use it (in a test):
    asset = assets.get("sale_profit_a")      # {"serial": ..., "registration_number": ..., "data": ...}
    serial = asset["serial"]

Each slot has:
    item, sub_type  what is registered (see test_data/asset_registration_data.py)
    plan            how the registration tests create it:
                        submit             created and submitted (ends PENDING, then approved)
                        draft_then_submit  saved as a Draft, then submitted from the list
                        draft              saved as a Draft and left as a Draft
    ends            the state the registration tests leave it in: APPROVED, DRAFT or PENDING
    reuse_from      (optional) this slot takes the asset of another slot when that asset is
                    free (UNASSIGNED and in no pending process); otherwise it gets its own new asset
    used_by         the flows that use it, in order (documentation only)
"""
import pytest

ASSET_SLOTS = {
    # --- the assets that Assign, Acknowledge, Movement, Unassign and Expense share, then Write-off ---
    "usage_a": {
        "item": "furniture", "sub_type": "spot", "plan": "submit", "ends": "APPROVED",
        "used_by": "Assign (Draft + Submit), Acknowledge, Internal Movement, Unassign, Expense, then Write-off",
    },
    "usage_b": {
        "item": "furniture", "sub_type": "gift", "plan": "submit", "ends": "APPROVED",
        "used_by": "Assign (Submit only), Internal Movement, Unassign, Expense, then Write-off",
    },
    "write_off_a": {
        "item": "furniture", "sub_type": "spot", "reuse_from": "usage_a",
        "used_by": "Write-off Draft, Edit from the list, Submit, Approve",
    },
    "write_off_b": {
        "item": "furniture", "sub_type": "gift", "reuse_from": "usage_b",
        "used_by": "Write-off Submit only",
    },
    # --- assets that are used up by one flow ---
    "split_land": {
        "item": "land", "sub_type": "spot", "plan": "submit", "ends": "APPROVED",
        "used_by": "Asset Serial Split (Land needs a Measurement)",
    },
    "transfer_a": {
        "item": "furniture", "sub_type": "spot", "plan": "submit", "ends": "APPROVED",
        "used_by": "Asset Shipment, Draft challan path (a Submit-only challan path is not built yet, so there is no transfer_b slot)",
    },
    "challan_a": {
        "item": "furniture", "sub_type": "spot", "plan": "submit", "ends": "APPROVED",
        "used_by": "Asset Single Challan, Draft path",
    },
    "challan_b": {
        "item": "furniture", "sub_type": "gift", "plan": "submit", "ends": "APPROVED",
        "used_by": "Asset Single Challan, Submit-only path",
    },
    "sale_profit_a": {
        "item": "building", "sub_type": "spot", "plan": "draft_then_submit", "ends": "APPROVED",
        "used_by": "Asset Sale above the Written Down Value, Draft path",
    },
    "sale_profit_b": {
        "item": "building", "sub_type": "gift", "plan": "draft_then_submit", "ends": "APPROVED",
        "used_by": "Asset Sale above the Written Down Value, Submit only",
    },
    "sale_loss_a": {
        "item": "laptop", "sub_type": "spot", "plan": "draft_then_submit", "ends": "APPROVED",
        "used_by": "Asset Sale below the Written Down Value, Draft path",
    },
    "sale_loss_b": {
        "item": "laptop", "sub_type": "gift", "plan": "draft_then_submit", "ends": "APPROVED",
        "used_by": "Asset Sale below the Written Down Value, Submit only",
    },
    # --- registrations that are never approved (the registration tests check what is not there) ---
    "reg_draft": {
        "item": "desktop", "sub_type": "spot", "plan": "draft", "ends": "DRAFT",
        "used_by": "Registration List and Approval List checks on a Draft",
    },
    "reg_pending": {
        "item": "furniture", "sub_type": "spot", "plan": "submit", "ends": "PENDING",
        "used_by": "No voucher before approval",
    },
}

# The slots the registration tests (test_01 to test_03) create themselves; the others
# (the ones with "reuse_from") are only registered when their test runs alone
REGISTERED_SLOTS = [name for name, slot in ASSET_SLOTS.items() if "plan" in slot]

# The slots that end approved, with their item and sub type
APPROVED_SLOTS = [name for name in REGISTERED_SLOTS if ASSET_SLOTS[name]["ends"] == "APPROVED"]

# (slot, item, sub type, plan) of every registered slot, and of the ones submitted from a Draft
SLOT_ROWS = [(name, ASSET_SLOTS[name]["item"], ASSET_SLOTS[name]["sub_type"], ASSET_SLOTS[name]["plan"]) for name in REGISTERED_SLOTS]
DRAFT_THEN_SUBMIT_SLOT_ROWS = [row for row in SLOT_ROWS if row[3] == "draft_then_submit"]

# Put above a test to run it once for each registered slot / each slot submitted from a Draft
ALL_SLOTS = pytest.mark.parametrize("slot, item, sub_type, plan", SLOT_ROWS, ids=[row[0] for row in SLOT_ROWS])
SLOTS_SUBMITTED_FROM_LIST = pytest.mark.parametrize(
    "slot, item, sub_type, plan", DRAFT_THEN_SUBMIT_SLOT_ROWS, ids=[row[0] for row in DRAFT_THEN_SUBMIT_SLOT_ROWS]
)
