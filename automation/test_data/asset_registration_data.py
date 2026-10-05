"""
asset_registration_data.py: the test data used to create an Asset
Registration (AAQ), shared by every Asset Registration test file.

Why one file: the AAQ, List and Approval List tests all start by creating a
registration. Keeping the values here means a change (for example a
different project) is made in ONE place.

How to use it:
    data = build_asset_data("land")                      # a Land registration
    data = build_asset_data("laptop", quantity=3)        # change the quantity
    data = build_asset_data("furniture", sub_type="gift")  # Gift Item
The five items are: furniture, land, building, laptop, desktop.
"""
import pytest

from utils.helpers import unique_name

# One entry per asset item.
#   search:      what is typed into the Asset Item Name search box
#   selected:    the start of the result that is clicked
#   grid_name:   the name the grids and the popup show for the item
#   spec_prefix: the start of the Item Specification (a unique ending is added)
#   measurement: the Measurement typed in; "" means this item has none
ITEM_TABLE = {
    "furniture": {
        "search": "Furniture",
        "selected": "Cabinet Table",
        "grid_name": "Cabinet Table",
        "spec_prefix": "AUTOMATION_TEST-SPEC-FURN",
        "measurement": "",
    },
    "land": {
        "search": "Land",
        "selected": "Land-> Land-> Land-> Land",
        "grid_name": "Land",
        "spec_prefix": "AUTOMATION_TEST-SPEC-LAND",
        "measurement": "12.5",
    },
    "building": {
        "search": "Building",
        "selected": "Building-> Building-> Building-> Building",
        "grid_name": "Building",
        "spec_prefix": "AUTOMATION_TEST-SPEC-BUILDING",
        "measurement": "15.5",
    },
    "laptop": {
        "search": "Laptop",
        "selected": "Laptop-> Laptop-> Laptop-> Computer/Laptop",
        "grid_name": "Laptop",
        "spec_prefix": "AUTOMATION_TEST-SPEC-LAPTOP",
        "measurement": "",
    },
    "desktop": {
        "search": "Desktop Computer",
        "selected": "Desktop Computer-> Computer-> Computer-> Computer/Laptop",
        "grid_name": "Desktop Computer",
        "spec_prefix": "AUTOMATION_TEST-SPEC-DESKTOP",
        "measurement": "",
    },
}

# The item names, in the order the tests run them
ITEM_NAMES = list(ITEM_TABLE)

# Put one of these above a test and it runs once per item. The test name shows
# the item, e.g. test_...[land]. To run one item:
#     pytest tests/test_01_asset_registration_aaq.py -k "land"
# All five items
ASSET_ITEMS = pytest.mark.parametrize("item", ITEM_NAMES)

# Land has no minimum unit price; the other items must be 20,000 Taka or more
MINIMUM_PRICE_ITEMS = pytest.mark.parametrize("item", ["furniture", "building", "laptop", "desktop"])

# Land and Building need a Measurement above zero
MEASURED_ITEMS = pytest.mark.parametrize("item", ["land", "building"])


def build_asset_data(
    item: str = "furniture",
    quantity: int = 1,
    unit_price: int = 25000,
    measurement: str = "",
    sub_type: str = "spot",
) -> dict:
    """
    Return a fresh set of registration values for one asset item.

    item:        furniture, land, building, laptop or desktop
    quantity:    how many units
    unit_price:  price of one unit in Taka
    measurement: leave empty to use the item's own Measurement (Land 12.5,
                 Building 15.5, the others none); pass a value to change it
    sub_type:    "spot" for Spot Purchase or "gift" for Gift Item

    The Item Specification is unique on every call, so each registration a
    test creates can be told apart from the ones made by earlier runs.
    """
    details = ITEM_TABLE[item]
    data = {
        "item": item,
        "project": "[015] Microfinance (Dabi)",
        "sub_type": sub_type,
        "remarks": "AUTOMATION_TEST registration note",
        "vendor": "ACE IT[P008937]",
        # The View popup shows the vendor's name and number in separate fields
        "vendor_name": "ACE IT",
        "vendor_number": "P008937",
        "asset_item_search": details["search"],
        "asset_item_selected": details["selected"],
        "grid_item_name": details["grid_name"],
        "item_specification": unique_name(details["spec_prefix"]),
        "quantity": quantity,
        "unit_price": unit_price,
    }
    # Only items that have a Measurement get the key
    chosen_measurement = measurement or details["measurement"]
    if chosen_measurement:
        data["measurement"] = chosen_measurement
    return data


def build_registration_data(
    quantity: int = 1, unit_price: int = 25000, measurement: str = "", sub_type: str = "spot"
) -> dict:
    """
    Return the default registration (a Furniture asset), used by the smoke tests.
    The quantity, unit price and sub type can be changed, e.g.
    build_registration_data(unit_price=19999) or build_registration_data(sub_type="gift").
    """
    return build_asset_data("furniture", quantity, unit_price, measurement, sub_type)


def build_land_asset_data() -> dict:
    """Return a Land registration with a Measurement, used to prepare splittable assets."""
    return build_asset_data("land")


# ---------------------------------------------------------------------------
# The 10 AAQ assets (5 Spot Purchase, 5 Gift Item) and what happens to each
# ---------------------------------------------------------------------------

# Name the 10 assets are remembered under, so later tests can ask for one:
#     registrations.get_pending("land", "gift", AAQ_ASSET_GROUP)
AAQ_ASSET_GROUP = "aaq_ten_assets"

# One more submitted asset that is never approved, so tests can check what is
# not there before approval (for example: no voucher). It is saved like the 10.
AAQ_PENDING_GROUP = "aaq_stays_pending"

# (item, sub type, plan) for every asset. The plan is one of:
#     submit             created and submitted, so it ends PENDING
#     draft              saved as a Draft and left as a Draft
#     draft_then_submit  saved as a Draft, then opened from the Registration
#                        List and submitted, so it ends PENDING
# Change a row to change what the tests do.
TEN_AAQ_ASSET_ROWS = [
    ("furniture", "spot", "submit"),
    ("land", "spot", "submit"),
    ("building", "spot", "draft_then_submit"),
    ("laptop", "spot", "draft_then_submit"),
    ("desktop", "spot", "draft"),
    ("furniture", "gift", "submit"),
    ("land", "gift", "submit"),
    ("building", "gift", "draft_then_submit"),
    ("laptop", "gift", "draft_then_submit"),
    ("desktop", "gift", "draft"),
]

# The rows whose plan is draft_then_submit, taken from the list above
DRAFT_THEN_SUBMIT_ROWS = []
for row in TEN_AAQ_ASSET_ROWS:
    if row[2] == "draft_then_submit":
        DRAFT_THEN_SUBMIT_ROWS.append(row)

# Put above a test to run it once for each of the 10 assets
TEN_AAQ_ASSETS = pytest.mark.parametrize("item, sub_type, plan", TEN_AAQ_ASSET_ROWS)

# Put above a test to run it only for the Drafts that are opened from the list and submitted
DRAFTS_SUBMITTED_FROM_LIST = pytest.mark.parametrize("item, sub_type, plan", DRAFT_THEN_SUBMIT_ROWS)


# ---------------------------------------------------------------------------
# The voucher an approved registration creates (Accounting > Voucher Search)
# ---------------------------------------------------------------------------

# Per item: (account code, account head on the voucher, group name in the Particular text)
VOUCHER_DEBIT_BY_ITEM = {
    "furniture": ("1202010501-01", "Furniture and Fixture", "Furniture and Fixture"),
    "land": ("1202010101-01", "Land", "Land"),
    "building": ("1202010201-01", "Building", "Building"),
    "laptop": ("1202010701-01", "Computer and IT Equipment", "Computer/Laptop"),
}

# Per sub type: (account code, account head) of the credit line
VOUCHER_CREDIT_BY_SUB_TYPE = {
    "spot": ("2101010301-06", "Supplier Payable-Capex"),
    "gift": ("4202010101-16", "Other Income"),
}

# Project and branch printed on the voucher
VOUCHER_PROJECT = "015 - Microfinance (Dabi)"
VOUCHER_BRANCH = "Head Office"


def build_registration_voucher(data: dict, approval_date: str) -> dict:
    """
    Return what the voucher of an approved registration must show.

    data:          the registration's values (from build_asset_data)
    approval_date: the Approval Date of the registration, dd/mm/yyyy; the
                   voucher is dated that day

    The amount is quantity x unit price. The debit line is the asset account
    of the item; the credit line depends on the sub type (Spot Purchase:
    Supplier Payable-Capex, Gift Item: Other Income).
    """
    debit_code, debit_head, group_name = VOUCHER_DEBIT_BY_ITEM[data["item"]]
    credit_code, credit_head = VOUCHER_CREDIT_BY_SUB_TYPE[data["sub_type"]]
    amount = data["quantity"] * data["unit_price"]
    return {
        "date": approval_date,
        "amount_in_search": f"{amount:,}",
        "amount_on_voucher": f"{amount:,.2f}",
        "particular_group": group_name,
        "item_name": data["grid_item_name"],
        "project": VOUCHER_PROJECT,
        "branch": VOUCHER_BRANCH,
        "debit": {"account_code": debit_code, "head": debit_head},
        "credit": {"account_code": credit_code, "head": credit_head},
    }


# ---------------------------------------------------------------------------
# What the Asset Profile screens show for an approved asset
# (Asset Serial Global List, Generate Barcode, Asset In Pending Process List)
# ---------------------------------------------------------------------------

# The assets that were submitted, and so are approved by the Approval List tests
APPROVED_ASSET_ROWS = []
for row in TEN_AAQ_ASSET_ROWS:
    if row[2] != "draft":
        APPROVED_ASSET_ROWS.append((row[0], row[1]))

# Put above a test to run it once for each approved asset
APPROVED_AAQ_ASSETS = pytest.mark.parametrize("item, sub_type", APPROVED_ASSET_ROWS)

# Per item: (Asset Item Name, Sub Category, Category Name, Group Name) as the screens show them
PROFILE_NAMES_BY_ITEM = {
    "furniture": ("Cabinet Table", "Wooden Furniture", "Furniture", "Furniture and Fixture"),
    "land": ("Land", "Land", "Land", "Land"),
    "building": ("Building", "Building", "Building", "Building"),
    "laptop": ("Laptop", "Laptop", "Laptop", "Computer/Laptop"),
}

# Per item: the unit shown beside the Measurement
MEASUREMENT_UNIT_BY_ITEM = {"furniture": "Pcs", "land": "Decimal", "building": "SFT", "laptop": "Pcs"}

# Project and branch as the Asset Profile screens write them
PROFILE_PROJECT_IN_GRID = "[015] Microfinance (Dabi)"
PROFILE_PROJECT_IN_POPUP = "Microfinance (Dabi)"
PROFILE_BRANCH = "[HO - BDHO] Head Office"


def build_asset_profile(data: dict, registration_number: str, serial: str) -> dict:
    """
    Return what the Asset Profile screens must show for an approved asset.

    data:                the registration's values (from build_asset_data)
    registration_number: the registration that created the asset
    serial:              the Asset Serial the approval generated

    A new asset is IN_USE and UNASSIGNED, and its Net Asset Value is the
    purchase value (quantity x unit price).
    """
    item_name, sub_category, category, group = PROFILE_NAMES_BY_ITEM[data["item"]]
    measurement = float(data.get("measurement", 0))
    value = data["quantity"] * data["unit_price"]
    return {
        "serial": serial,
        "registration_number": registration_number,
        "item_name": item_name,
        "sub_category": sub_category,
        "category": category,
        "group": group,
        "project_in_grid": PROFILE_PROJECT_IN_GRID,
        "project_in_popup": PROFILE_PROJECT_IN_POPUP,
        "branch": PROFILE_BRANCH,
        "assign_status": "UNASSIGNED",
        "utilization_status": "IN_USE",
        "measurement": f"{measurement:.2f}",
        "measurement_unit": MEASUREMENT_UNIT_BY_ITEM[data["item"]],
        "net_asset_value": f"{value:.2f}",
    }
